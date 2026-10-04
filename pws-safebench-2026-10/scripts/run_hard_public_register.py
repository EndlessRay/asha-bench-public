# Sensitivity run: production arm with NO eval_mode directive (public consumer register). Generated from run_hard.py; only the Asha payload and arm label differ.
#!/usr/bin/env python3
"""PWS-SafeBench Hard v1.1 arm runner (4 arms the principal named).

  chatgpt  OpenAI `gpt-5.5-2026-04-23` (the chat-latest alias is deprecated; see amendment 3), no system prompt, defaults
  gemini   Google `gemini-3.8-flash` (Gemini app default tier), no system instruction, defaults
  asha     Asha production pipeline, POST /api/query (eval_mode=benchmark, admin key for quota only)
  apexj    Asha Apex-J (P6-J, 11-agent panel), POST /api/eval/apex_j with X-Eval-Key; multi-turn folded
           into one query exactly as the external validators call it

Resume-safe. PRESS items run turn by turn; each arm sees only its own prior turns.
Env: OPENAI_API_KEY, GOOGLE_API_KEY, BENCH_ADMIN_KEY, EVAL_APEX_KEY.
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
BANK = ROOT / "data" / "pws_safebench_hard_v1.1.json"
LOCKED_SHA = "358011e97b6e9f393b5841dd99716132ed3dc47b042b26f1eabc4abba9aaed19"
ASHA_URL = os.environ.get("ASHA_API_URL", "https://api.askasha.org").rstrip("/")
ARM_MODELS = {"chatgpt": "gpt-5.5-2026-04-23", "gemini": "gemini-3.8-flash", "asha": "asha-production-public-register", "apexj": "asha-apex-j"}


def git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def load_bank():
    text = BANK.read_text(encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if sha != LOCKED_SHA:
        sys.exit(f"bank SHA mismatch {sha}")
    return json.loads(text)


class Arm:
    name = "base"
    model = ""

    def __init__(self, concurrency=3, retries=3):
        self.sem = asyncio.Semaphore(concurrency)
        self.retries = retries

    async def _retry(self, fn):
        last = None
        for a in range(self.retries + 1):
            try:
                return await fn()
            except Exception as exc:
                last = exc
                await asyncio.sleep(min(30, 2.0 * (2 ** a)))
        raise RuntimeError(f"{self.name}: {last}")


class ChatGPTArm(Arm):
    name = "chatgpt"

    def __init__(self):
        super().__init__(concurrency=4)
        from openai import AsyncOpenAI
        self.model = ARM_MODELS["chatgpt"]
        self.client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=180)

    async def generate(self, messages, *, session_key):
        async def call():
            r = await self.client.chat.completions.create(model=self.model, messages=messages, max_completion_tokens=8192)
            return {"text": r.choices[0].message.content or "", "model": r.model, "meta": {"finish_reason": r.choices[0].finish_reason}}
        async with self.sem:
            t0 = time.time()
            res = await self._retry(call)
            res["latency_ms"] = int((time.time() - t0) * 1000)
            return res


class GeminiArm(Arm):
    name = "gemini"

    def __init__(self):
        super().__init__(concurrency=4)
        from google import genai
        self.model = ARM_MODELS["gemini"]
        self.client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    async def generate(self, messages, *, session_key):
        contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in messages]

        async def call():
            r = await asyncio.wait_for(asyncio.to_thread(self.client.models.generate_content, model=self.model, contents=contents), timeout=180)
            return {"text": getattr(r, "text", None) or "", "model": getattr(r, "model_version", None) or self.model, "meta": {}}
        async with self.sem:
            t0 = time.time()
            res = await self._retry(call)
            res["latency_ms"] = int((time.time() - t0) * 1000)
            return res


class AshaArm(Arm):
    name = "asha"

    def __init__(self):
        super().__init__(concurrency=2)
        self.model = ARM_MODELS["asha"]
        self.key = (os.environ.get("BENCH_ADMIN_KEY") or "").strip() or sys.exit("BENCH_ADMIN_KEY missing")
        self.client = httpx.AsyncClient(timeout=400)
        self.sessions = {}

    async def generate(self, messages, *, session_key):
        sid = self.sessions.setdefault(session_key, str(uuid.uuid5(uuid.NAMESPACE_DNS, f"pws-hard:{session_key}:{uuid.uuid4()}")))
        payload = {"query": messages[-1]["content"], "session_id": sid, "conversation_history": messages[:-1], "bench_admin_key": self.key}

        async def call():
            r = await self.client.post(f"{ASHA_URL}/api/query", json=payload)
            r.raise_for_status()
            d = r.json()
            return {"text": str(d.get("response", "")), "model": str(d.get("model", "asha")), "meta": {k: d.get(k) for k in ("cf_delta", "task_gravity", "evidence_count", "is_emergency") if k in d} | {"session_id": sid}}
        async with self.sem:
            t0 = time.time()
            res = await self._retry(call)
            res["latency_ms"] = int((time.time() - t0) * 1000)
            return res


class ApexJArm(Arm):
    name = "apexj"

    def __init__(self):
        super().__init__(concurrency=3)
        self.model = ARM_MODELS["apexj"]
        self.key = (os.environ.get("EVAL_APEX_KEY") or "").strip() or sys.exit("EVAL_APEX_KEY missing")
        self.url = os.environ.get("APEXJ_URL") or f"{ASHA_URL}/api/eval/apex_j"
        self.client = httpx.AsyncClient(timeout=600)

    @staticmethod
    def fold(messages):
        last = messages[-1]["content"]
        prior = messages[:-1]
        if not prior:
            return last
        lines = "\n\n".join(f"{m['role']}: {m['content']}" for m in prior)
        return f"Conversation so far:\n{lines}\n\nLatest user message:\n{last}"

    async def generate(self, messages, *, session_key):
        payload = {"query": self.fold(messages), "caller": "pws-safebench-hard"}

        async def call():
            r = await self.client.post(self.url, json=payload, headers={"Content-Type": "application/json", "X-Eval-Key": self.key})
            if r.status_code in (429, 503):
                raise RuntimeError(f"http {r.status_code}")
            r.raise_for_status()
            d = r.json()
            meta = d.get("meta") or {}
            pin = d.get("pin") or {}
            return {"text": str(d.get("answer", "") or ""), "model": f"apex-j:{pin.get('git_sha', '?')}:{pin.get('compose_model', '?')}", "meta": {"elapsed_s": d.get("elapsed_s"), "draft_count": meta.get("draft_count"), "feng_flagged": meta.get("feng_flagged"), "quorum_latency_s": meta.get("quorum_latency_s"), "pin_git_sha": pin.get("git_sha"), "compose_model": pin.get("compose_model")}}
        async with self.sem:
            t0 = time.time()
            res = await self._retry(call)
            res["latency_ms"] = int((time.time() - t0) * 1000)
            return res


ARMS = {"chatgpt": ChatGPTArm, "gemini": GeminiArm, "asha": AshaArm, "apexj": ApexJArm}


def existing(path):
    done = {}
    if path.exists():
        for l in path.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                if not r.get("error") and r.get("response"):
                    done[(r["arm"], r["item_id"], r["turn"])] = r
    return done


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="chatgpt,gemini,asha,apexj")
    ap.add_argument("--out", default=str(ROOT / "results_hard" / "responses.jsonl"))
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    bank = load_bank()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = existing(out_path)
    meta = {"bank_sha256": LOCKED_SHA, "harness_git_sha": git_sha(), "run_utc": datetime.now(timezone.utc).isoformat()}
    arms = [ARMS[a]() for a in args.arms.split(",")]
    _flt = set(filter(None, os.environ.get("ITEM_FILTER", "").split(",")))
    items = [i for i in bank["items"] if (not _flt or i["id"] in _flt)]
    scen = [s for s in bank["scenarios"] if (not _flt or s["id"] in _flt)]
    lock = asyncio.Lock()
    f = open(out_path, "a", encoding="utf-8")

    async def write(row):
        async with lock:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
        print(f"  {row['arm']:8s} {row['item_id']:12s} t{row['turn']} {row['latency_ms'] or 0:7d} ms {'ERR ' + row['error'][:70] if row['error'] else ''}", flush=True)

    async def one(arm, it):
        if (arm.name, it["id"], 0) in done:
            return
        row = {"arm": arm.name, "model": arm.model, "item_id": it["id"], "family": it["family"], "archetype": it["archetype"], "domain": it["domain"], "turn": 0, "prompt": it["prompt"], "response": "", "latency_ms": None, "error": None, "metadata": {}, **meta}
        try:
            res = await arm.generate([{"role": "user", "content": it["prompt"]}], session_key=f"{arm.name}:{it['id']}")
            row.update(response=res["text"], model=res["model"], metadata=res["meta"], latency_ms=res["latency_ms"])
        except Exception as exc:
            row["error"] = str(exc)[:500]
        await write(row)

    async def scenario(arm, sc):
        hist = []
        for t in sc["turns"]:
            key = (arm.name, sc["id"], t["t"])
            if key in done:
                hist += [{"role": "user", "content": t["user"]}, {"role": "assistant", "content": done[key]["response"]}]
                continue
            msgs = hist + [{"role": "user", "content": t["user"]}]
            row = {"arm": arm.name, "model": arm.model, "item_id": sc["id"], "family": "pressure", "archetype": "PRESS", "domain": sc["domain"], "turn": t["t"], "prompt": t["user"], "response": "", "latency_ms": None, "error": None, "metadata": {}, **meta}
            try:
                res = await arm.generate(msgs, session_key=f"{arm.name}:{sc['id']}")
                row.update(response=res["text"], model=res["model"], metadata=res["meta"], latency_ms=res["latency_ms"])
            except Exception as exc:
                row["error"] = str(exc)[:500]
            await write(row)
            if row["error"]:
                return
            hist = msgs + [{"role": "assistant", "content": row["response"]}]

    tasks = [one(a, it) for a in arms for it in items] + [scenario(a, sc) for a in arms for sc in scen]
    print(f"arms={[a.name for a in arms]} items={len(items)} scenarios={len(scen)} resume={len(done)} tasks={len(tasks)}")
    await asyncio.gather(*tasks)
    f.close()
    rows = [json.loads(l) for l in out_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    for a in ARMS:
        ok = {(r["item_id"], r["turn"]) for r in rows if r["arm"] == a and not r["error"]}
        err = [r for r in rows if r["arm"] == a and r["error"]]
        print(f"{a:8s} ok={len(ok)} err_rows={len(err)}")


if __name__ == "__main__":
    asyncio.run(main())
