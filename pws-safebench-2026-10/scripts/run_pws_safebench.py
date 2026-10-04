#!/usr/bin/env python3
"""PWS-SafeBench v1.0 arm runner.

Poses every locked item to every arm and writes one JSONL row per response:
  {arm, model, item_id, family, domain, turn, prompt, response, latency_ms,
   error, metadata, bank_sha256, harness_git_sha, run_utc}

Arms (pre-registered): gpt, claude, gemini, asha. Consumer arms: public API,
no system prompt, vendor default sampling. Asha: as deployed, POST /api/query
with eval_mode=benchmark and the admin benchmark key (quota bypass only).

Resume-safe: rows already present in --out for (arm, item_id, turn) are kept.
Longitudinal scenarios are run sequentially per arm; each arm sees only its
own earlier turns.

Usage:
  set -a; source <(grep -E '^(OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_API_KEY|BENCH_ADMIN_KEY)=' ../../.env | tr -d '\r'); set +a
  python3 scripts/run_pws_safebench.py --arms gpt,claude,gemini,asha --out results/responses.jsonl
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
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "pws_safebench_v1.0.json"
LOCKED_SHA = "e2312422a41bec58d911ef857d81d6004811628a74a6b52c41b2708d8e2728cf"

ARM_MODELS = {
    "gpt": "gpt-5.5-2026-04-23",
    "claude": "claude-sonnet-5-5",
    "gemini": "gemini-3.8-flash",
    "asha": "asha-deployed",
}
ASHA_URL = os.environ.get("ASHA_API_URL", "https://api.askasha.org").rstrip("/")


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def load_bank() -> dict:
    text = BANK.read_text(encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if sha != LOCKED_SHA:
        sys.exit(f"item bank SHA mismatch: {sha} != locked {LOCKED_SHA}")
    return json.loads(text)


# ---------------------------------------------------------------- arms ----
class Arm:
    name = "base"
    model = ""

    def __init__(self, concurrency: int = 3, retries: int = 3):
        self.sem = asyncio.Semaphore(concurrency)
        self.retries = retries

    async def generate(self, messages: list[dict], *, session_key: str) -> dict:
        raise NotImplementedError

    async def _with_retry(self, fn):
        last = None
        for attempt in range(self.retries + 1):
            try:
                return await fn()
            except Exception as exc:  # network / rate limit
                last = exc
                await asyncio.sleep(min(30, 2.0 * (2 ** attempt)))
        raise RuntimeError(f"{self.name}: {last}")


class GPTArm(Arm):
    name = "gpt"

    def __init__(self, **kw):
        super().__init__(**kw)
        from openai import AsyncOpenAI
        self.model = ARM_MODELS["gpt"]
        self.client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=180)

    async def generate(self, messages, *, session_key):
        async def call():
            r = await self.client.chat.completions.create(model=self.model, messages=messages, max_completion_tokens=8192)
            return {"text": r.choices[0].message.content or "", "model": r.model, "meta": {"finish_reason": r.choices[0].finish_reason, "usage": r.usage.model_dump() if r.usage else None}}
        async with self.sem:
            return await self._with_retry(call)


class ClaudeArm(Arm):
    name = "claude"

    def __init__(self, **kw):
        super().__init__(**kw)
        from anthropic import AsyncAnthropic
        self.model = ARM_MODELS["claude"]
        self.client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=180)

    async def generate(self, messages, *, session_key):
        async def call():
            r = await self.client.messages.create(model=self.model, max_tokens=4096, messages=messages)
            text = "".join(getattr(b, "text", "") for b in r.content)
            return {"text": text, "model": r.model, "meta": {"stop_reason": r.stop_reason, "usage": r.usage.model_dump() if r.usage else None}}
        async with self.sem:
            return await self._with_retry(call)


class GeminiArm(Arm):
    name = "gemini"

    def __init__(self, **kw):
        super().__init__(**kw)
        from google import genai
        self.model = ARM_MODELS["gemini"]
        self.client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    async def generate(self, messages, *, session_key):
        contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in messages]

        async def call():
            r = await asyncio.wait_for(asyncio.to_thread(self.client.models.generate_content, model=self.model, contents=contents), timeout=180)
            text = getattr(r, "text", None) or ""
            fr = None
            try:
                fr = str(r.candidates[0].finish_reason)
            except Exception:
                pass
            return {"text": text, "model": getattr(r, "model_version", None) or self.model, "meta": {"finish_reason": fr}}
        async with self.sem:
            return await self._with_retry(call)


class AshaArm(Arm):
    name = "asha"

    def __init__(self, **kw):
        kw.setdefault("concurrency", 2)
        super().__init__(**kw)
        self.model = ARM_MODELS["asha"]
        self.key = (os.environ.get("BENCH_ADMIN_KEY") or os.environ.get("FH_ASHA_BENCH_KEY") or "").strip()
        if not self.key:
            sys.exit("BENCH_ADMIN_KEY missing")
        self.client = httpx.AsyncClient(timeout=300)
        self.sessions: dict[str, str] = {}

    async def generate(self, messages, *, session_key):
        sid = self.sessions.setdefault(session_key, str(uuid.uuid5(uuid.NAMESPACE_DNS, f"pws-safebench:{session_key}:{uuid.uuid4()}")))
        payload = {"query": messages[-1]["content"], "session_id": sid, "conversation_history": messages[:-1], "eval_mode": "benchmark", "bench_admin_key": self.key}

        async def call():
            r = await self.client.post(f"{ASHA_URL}/api/query", json=payload)
            r.raise_for_status()
            d = r.json()
            return {"text": str(d.get("response", "")), "model": str(d.get("model", "asha")), "meta": {k: d.get(k) for k in ("cf_delta", "task_gravity", "evidence_count", "is_emergency", "query_type", "verification_status") if k in d} | {"session_id": sid}}
        async with self.sem:
            return await self._with_retry(call)


ARMS = {"gpt": GPTArm, "claude": ClaudeArm, "gemini": GeminiArm, "asha": AshaArm}


# -------------------------------------------------------------- runner ----
def existing_rows(path: Path) -> dict:
    done = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if not r.get("error"):
                    done[(r["arm"], r["item_id"], r["turn"])] = r
    return done


async def run_single(arm: Arm, item: dict, out, lock, done, meta) -> None:
    key = (arm.name, item["id"], 0)
    if key in done:
        return
    t0 = time.time()
    row = {"arm": arm.name, "model": arm.model, "item_id": item["id"], "family": item["family"], "domain": item["domain"], "turn": 0, "prompt": item["prompt"], "response": "", "latency_ms": None, "error": None, "metadata": {}, **meta}
    try:
        res = await arm.generate([{"role": "user", "content": item["prompt"]}], session_key=f"{arm.name}:{item['id']}")
        row.update(response=res["text"], model=res["model"], metadata=res["meta"])
    except Exception as exc:
        row["error"] = str(exc)[:500]
    row["latency_ms"] = int((time.time() - t0) * 1000)
    async with lock:
        out.write(json.dumps(row, ensure_ascii=False) + "\n")
        out.flush()
    print(f"  {arm.name:7s} {item['id']:9s} {row['latency_ms']:6d} ms {'ERR ' + row['error'][:60] if row['error'] else ''}", flush=True)


async def run_scenario(arm: Arm, sc: dict, out, lock, done, meta) -> None:
    history: list[dict] = []
    for t in sc["turns"]:
        key = (arm.name, sc["id"], t["t"])
        if key in done:
            prev = done[key]
            history += [{"role": "user", "content": t["user"]}, {"role": "assistant", "content": prev["response"]}]
            continue
        t0 = time.time()
        row = {"arm": arm.name, "model": arm.model, "item_id": sc["id"], "family": "longitudinal", "domain": sc["domain"], "turn": t["t"], "prompt": t["user"], "response": "", "latency_ms": None, "error": None, "metadata": {}, **meta}
        msgs = history + [{"role": "user", "content": t["user"]}]
        try:
            res = await arm.generate(msgs, session_key=f"{arm.name}:{sc['id']}")
            row.update(response=res["text"], model=res["model"], metadata=res["meta"])
        except Exception as exc:
            row["error"] = str(exc)[:500]
        row["latency_ms"] = int((time.time() - t0) * 1000)
        async with lock:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
        print(f"  {arm.name:7s} {sc['id']} t{t['t']:02d} {row['latency_ms']:6d} ms {'ERR ' + row['error'][:60] if row['error'] else ''}", flush=True)
        if row["error"]:
            # keep the conversation coherent: stop this scenario for this arm
            print(f"  !! {arm.name} {sc['id']} aborted at t{t['t']} (error)", flush=True)
            return
        history = msgs + [{"role": "assistant", "content": row["response"]}]


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="gpt,claude,gemini,asha")
    ap.add_argument("--out", default=str(ROOT / "results" / "responses.jsonl"))
    ap.add_argument("--families", default="knowledge_safety,false_premise,longitudinal")
    ap.add_argument("--limit", type=int, default=0, help="debug: first N single-turn items")
    args = ap.parse_args()

    bank = load_bank()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = existing_rows(out_path)
    meta = {"bank_sha256": LOCKED_SHA, "harness_git_sha": git_sha(), "run_utc": datetime.now(timezone.utc).isoformat()}
    fams = set(args.families.split(","))
    arms = [ARMS[a]() for a in args.arms.split(",")]
    items = [i for i in bank["items"] if i["family"] in fams]
    if args.limit:
        items = items[: args.limit]
    scenarios = bank["scenarios"] if "longitudinal" in fams else []
    print(f"arms={[a.name for a in arms]} items={len(items)} scenarios={len(scenarios)} resume_rows={len(done)}")

    lock = asyncio.Lock()
    with open(out_path, "a", encoding="utf-8") as out:
        tasks = []
        for arm in arms:
            for it in items:
                tasks.append(run_single(arm, it, out, lock, done, meta))
            for sc in scenarios:
                tasks.append(run_scenario(arm, sc, out, lock, done, meta))
        await asyncio.gather(*tasks)
    rows = [json.loads(l) for l in out_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    ok = {}
    err = {}
    for r in rows:
        (err if r.get("error") else ok).setdefault(r["arm"], set()).add((r["item_id"], r["turn"]))
    for a in ARMS:
        print(f"{a:7s} ok={len(ok.get(a, ()))} err_rows={len(err.get(a, ()))}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
