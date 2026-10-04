#!/usr/bin/env python3
"""Apex-PWS runner: one Apex-J configuration over one item bank.

  python3 run_apexpws.py --config C1 --bank ../data/pws_safebench_hard_v1.1.json --out results/dev_C1.jsonl

Knobs come from configs.json; "@fiduciary_directive" expands to the published
directive text. PRESS items fold prior turns into one query exactly as the
v1.1 apexj arm did. Resume-safe. Records the route pin on every row.
Env: EVAL_APEX_KEY (fetched from the 5090 at call time by the launcher).
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIGS = json.loads((HERE / "configs.json").read_text(encoding="utf-8"))
URL = os.environ.get("APEXJ_URL") or "https://api.askasha.org/api/eval/apex_j"


def fold(messages):
    last = messages[-1]["content"]
    prior = messages[:-1]
    if not prior:
        return last
    lines = "\n\n".join(f"{m['role']}: {m['content']}" for m in prior)
    return f"Conversation so far:\n{lines}\n\nLatest user message:\n{last}"


class ApexJ:
    def __init__(self, knobs: dict, concurrency: int = 3):
        self.key = (os.environ.get("EVAL_APEX_KEY") or "").strip() or sys.exit("EVAL_APEX_KEY missing")
        self.knobs = {k: (CONFIGS["fiduciary_directive"] if v == "@fiduciary_directive" else v) for k, v in knobs.items()}
        self.client = httpx.AsyncClient(timeout=600)
        self.sem = asyncio.Semaphore(concurrency)

    async def generate(self, messages):
        payload = {"query": fold(messages), "caller": "apex-pws", **self.knobs}
        last = None
        async with self.sem:
            t0 = time.time()
            for a in range(4):
                try:
                    r = await self.client.post(URL, json=payload, headers={"Content-Type": "application/json", "X-Eval-Key": self.key})
                    if r.status_code in (429, 503):
                        raise RuntimeError(f"http {r.status_code}")
                    r.raise_for_status()
                    d = r.json()
                    meta = d.get("meta") or {}
                    pin = d.get("pin") or {}
                    return {"text": str(d.get("answer", "") or ""), "latency_ms": int((time.time() - t0) * 1000),
                            "meta": {"elapsed_s": d.get("elapsed_s"), "draft_count": meta.get("draft_count"), "feng_flagged": meta.get("feng_flagged"), "pin_git_sha": pin.get("git_sha"), "compose_model": meta.get("compose_model") or pin.get("compose_model"), "compose_style": meta.get("compose_style"), "live_evidence": (meta.get("live_evidence") or {}).get("enabled") if isinstance(meta.get("live_evidence"), dict) else None, "knobs": {k: (v if k != "directive" else "@fiduciary_directive") for k, v in self.knobs.items()}}}
                except Exception as exc:
                    last = exc
                    await asyncio.sleep(min(60, 3.0 * (2 ** a)))
            raise RuntimeError(str(last))


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--bank", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--concurrency", type=int, default=3)
    args = ap.parse_args()
    bank_text = Path(args.bank).read_text(encoding="utf-8")
    bank = json.loads(bank_text)
    bank_sha = hashlib.sha256(bank_text.encode("utf-8")).hexdigest()
    cfg = CONFIGS["configs"][args.config]
    arm = ApexJ(cfg["knobs"], args.concurrency)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {}
    if out.exists():
        for l in out.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                if not r.get("error") and r.get("response"):
                    done[(r["item_id"], r["turn"])] = r
    meta = {"config": args.config, "config_label": cfg["label"], "bank_sha256": bank_sha, "bank_version": bank.get("version"), "run_utc": datetime.now(timezone.utc).isoformat(),
            "harness_git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()}
    lock = asyncio.Lock()
    f = open(out, "a", encoding="utf-8")

    async def write(row):
        async with lock:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
        print(f"  {args.config} {row['item_id']:12s} t{row['turn']} {row['latency_ms'] or 0:7d} ms {'ERR ' + row['error'][:60] if row['error'] else ''}", flush=True)

    async def single(it):
        if (it["id"], 0) in done:
            return
        row = {"arm": f"apexj_{args.config}", "item_id": it["id"], "family": it["family"], "archetype": it["archetype"], "domain": it["domain"], "turn": 0, "prompt": it["prompt"], "response": "", "latency_ms": None, "error": None, "metadata": {}, **meta}
        try:
            res = await arm.generate([{"role": "user", "content": it["prompt"]}])
            row.update(response=res["text"], latency_ms=res["latency_ms"], metadata=res["meta"])
        except Exception as exc:
            row["error"] = str(exc)[:400]
        await write(row)

    async def scenario(sc):
        hist = []
        for t in sc["turns"]:
            if (sc["id"], t["t"]) in done:
                hist += [{"role": "user", "content": t["user"]}, {"role": "assistant", "content": done[(sc["id"], t["t"])]["response"]}]
                continue
            msgs = hist + [{"role": "user", "content": t["user"]}]
            row = {"arm": f"apexj_{args.config}", "item_id": sc["id"], "family": "pressure", "archetype": "PRESS", "domain": sc["domain"], "turn": t["t"], "prompt": t["user"], "response": "", "latency_ms": None, "error": None, "metadata": {}, **meta}
            try:
                res = await arm.generate(msgs)
                row.update(response=res["text"], latency_ms=res["latency_ms"], metadata=res["meta"])
            except Exception as exc:
                row["error"] = str(exc)[:400]
            await write(row)
            if row["error"]:
                return
            hist = msgs + [{"role": "assistant", "content": row["response"]}]

    tasks = [single(i) for i in bank["items"]] + [scenario(s) for s in bank["scenarios"]]
    print(f"config={args.config} ({cfg['label']}) bank={bank.get('version')} items={len(bank['items'])} scenarios={len(bank['scenarios'])} resume={len(done)}")
    await asyncio.gather(*tasks)
    f.close()
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"done: ok={sum(1 for r in rows if not r['error'])} err={sum(1 for r in rows if r['error'])}")


if __name__ == "__main__":
    asyncio.run(main())
