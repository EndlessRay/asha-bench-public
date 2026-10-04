"""Study 1 extraction: real-world PWS sessions on Asha, 2026-02-01 to 2026-09-30.

Lyra (research) + Asha (medical fiduciary). Builds on tests/qa/asha_pws/
extract_pws_corpus.py (2026-05-02), whose deidentification, regex role
detection and theme tagging are imported unchanged so the two extractions
stay comparable.

What this version adds (pre-specified in the study protocol):
  * fixed observation window [2026-02-01, 2026-10-01)
  * widened PWS capture lexicon (Prader, PWS, hyperphagia, 15q11, DCCR,
    diazoxide choline, Vykat); LLM semantic confirmation happens downstream
    on the deidentified text (classify_sessions.py), never here
  * explicit, counted exclusion flags so the flow diagram is reproducible:
    non-Asha agent, internal/A2A traffic, staff and admin accounts,
    content-detected test or benchmark traffic
  * per-turn guardrail telemetry pulled from message columns and the JSONB
    payload (task_gravity, cf_delta, symbolic_entropy, is_emergency,
    emergency_type, evidence_count, evidence_coverage, evidence_ids,
    verification_status, hallucinated_pmids, citation_validation)
  * emergency_audit_log join (session-level event counts)

Outputs (OUT_DIR, default /tmp/pws_s1):
  turns_deid.csv      one row per turn in INCLUDED sessions, deidentified
  sessions.csv        one row per CANDIDATE session with inclusion flags
  mapping.csv         hash -> source ids. STAYS ON THE 5090. Never copied.
  summary.json        counts for the flow diagram

Run inside the citadel-api container (psycopg2 present, postgres reachable):
  docker exec citadel-api python /tmp/pws_s1/extract_pws_study1.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_pws_corpus import deidentify, detect_role, detect_themes  # noqa: E402

OUT_DIR = Path(os.environ.get("PWS_S1_OUT", "/tmp/pws_s1"))
OUT_DIR.mkdir(parents=True, exist_ok=True)

WINDOW_START = "2026-02-01"
WINDOW_END = "2026-10-01"  # exclusive

HASH_SALT = os.environ.get("PWS_S1_HASH_SALT", "lyra-pws-study1-2026-10-03-v1").encode("utf-8")

# Capture lexicon. Case-insensitive. Word-bounded PWS / DCCR so "pws" inside
# other tokens (gaming prompts, URLs) does not match.
PWS_SQL_REGEX = r"(prader|\mPWS\M|hyperphagi|15q11|diazoxide choline|\mDCCR\M|vykat)"
PWS_PY_REGEX = re.compile(r"(prader|\bPWS\b|hyperphagi|15q11|diazoxide choline|\bDCCR\b|vykat)", re.IGNORECASE)

STAFF_EMAIL_DOMAINS = {"dnai.systems", "endlessray.com"}
STAFF_EMAIL_FRAGMENTS = ("ashatest", "endlessray")
INTERNAL_ROLES = {"admin", "system"}


def short_hash(value: object, prefix: str) -> str:
    if value is None:
        return f"{prefix}-NULL"
    s = str(value)
    if not s:
        return f"{prefix}-EMPTY"
    return f"{prefix}-{hashlib.sha256(HASH_SALT + s.encode('utf-8')).hexdigest()[:12]}"


def pg_connect():
    url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if url:
        return psycopg2.connect(url)
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "postgres"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        user=os.environ.get("POSTGRES_USER", "asha"),
        password=os.environ.get("POSTGRES_PASSWORD", "fiduciary_sovereign_2025"),
        dbname=os.environ.get("POSTGRES_DB", "asha_ledger"),
    )


def payload_get(payload, key, default=None):
    if not isinstance(payload, dict):
        return default
    v = payload.get(key, default)
    return v


def jdump(v):
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        return json.dumps(v, separators=(",", ":"), ensure_ascii=False)
    return str(v)


def main() -> int:
    t0 = datetime.utcnow()
    print(f"[{t0.isoformat()}Z] connecting", flush=True)
    conn = pg_connect()
    conn.set_session(readonly=True)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # ---- Step 1: candidate sessions (user turn matches lexicon inside window)
    cur.execute(
        """
        SELECT m.session_id, min(m.timestamp) AS first_hit
        FROM messages m
        WHERE m.role = 'user'
          AND m.timestamp >= %s AND m.timestamp < %s
          AND m.session_id IS NOT NULL
          AND m.content ~* %s
        GROUP BY m.session_id
        """,
        (WINDOW_START, WINDOW_END, PWS_SQL_REGEX),
    )
    cand = {str(r["session_id"]): r["first_hit"] for r in cur.fetchall()}
    print(f"[step1] candidate sessions: {len(cand)}", flush=True)

    sids = list(cand.keys())

    # ---- Step 2: session + user metadata
    cur.execute(
        """
        SELECT s.session_id, s.user_id, s.agent_id, s.started_at, s.ended_at,
               s.message_count, s.metadata AS session_metadata,
               u.role AS user_role_db, u.subscription_tier, u.email AS user_email,
               u.created_at AS user_created_at
        FROM sessions s
        LEFT JOIN users u
          ON CASE WHEN s.user_id ~ '^[0-9a-f-]{36}$' THEN u.user_id::text = s.user_id
                  ELSE u.auth0_sub = s.user_id END
        WHERE s.session_id::text = ANY(%s)
        """,
        (sids,),
    )
    smeta = {str(r["session_id"]): r for r in cur.fetchall()}
    missing = [s for s in sids if s not in smeta]
    print(f"[step2] session meta: {len(smeta)} (no sessions row: {len(missing)})", flush=True)

    # ---- Step 3: emergency audit events per session
    cur.execute(
        """
        SELECT session_id, event_type, emergency_type, count(*) AS n
        FROM emergency_audit_log
        WHERE session_id = ANY(%s)
        GROUP BY 1,2,3
        """,
        (sids,),
    )
    emerg: dict[str, Counter] = {}
    for r in cur.fetchall():
        emerg.setdefault(str(r["session_id"]), Counter())[f"{r['event_type']}:{r['emergency_type']}"] += int(r["n"])

    # ---- Step 4: stream sessions
    turns_path = OUT_DIR / "turns_deid.csv"
    sess_path = OUT_DIR / "sessions.csv"
    map_path = OUT_DIR / "mapping.csv"

    flow = Counter()
    role_counts = Counter()
    theme_counts = Counter()
    month_counts = Counter()
    user_session_counts: Counter = Counter()

    mcur = conn.cursor(cursor_factory=RealDictCursor)
    n_turns_written = 0

    with open(turns_path, "w", newline="", encoding="utf-8") as f_t, \
         open(sess_path, "w", newline="", encoding="utf-8") as f_s, \
         open(map_path, "w", newline="", encoding="utf-8") as f_m:
        tw = csv.writer(f_t, quoting=csv.QUOTE_ALL)
        tw.writerow([
            "session_hash", "message_hash", "user_hash", "turn_index", "role",
            "timestamp_utc", "is_pws_match", "themes_regex",
            "tokens_used", "latency_ms", "cf_delta", "task_gravity", "symbolic_entropy",
            "is_emergency", "ambiguity_detected", "n_evidence_ids",
            "p_evidence_count", "p_evidence_coverage", "p_verification_status",
            "p_verification_passed", "p_unverified_reason", "p_hallucinated_pmids",
            "p_citation_validation", "p_emergency_type", "p_query_type", "p_user_role",
            "p_detected_language", "p_was_translated", "p_cf_delta_v2",
            "content_chars", "content_redacted",
        ])
        sw = csv.writer(f_s, quoting=csv.QUOTE_ALL)
        sw.writerow([
            "session_hash", "user_hash", "agent_id", "started_utc", "ended_utc", "month",
            "turn_count", "user_turns", "assistant_turns", "pws_match_turns",
            "user_id_class", "user_role_db", "subscription_tier",
            "excl_agent", "excl_internal_userid", "excl_staff", "excl_content_test",
            "included",
            "role_regex", "role_regex_evidence", "themes_regex",
            "any_emergency", "max_task_gravity", "min_cf_delta",
            "emergency_audit_events", "first_user_query_redacted",
        ])
        mw = csv.writer(f_m, quoting=csv.QUOTE_ALL)
        mw.writerow(["session_hash", "session_id", "user_hash", "user_id", "message_hash", "message_id"])

        for i, sid in enumerate(sorted(sids, key=lambda s: cand[s])):
            sm = smeta.get(sid)
            agent_id = (sm["agent_id"] if sm else None) or "asha"
            user_id = (sm["user_id"] if sm else None) or ""
            mcur.execute(
                """
                SELECT message_id, session_id, user_id, role, content, timestamp,
                       tokens_used, latency_ms, cf_delta, task_gravity, symbolic_entropy,
                       is_emergency, ambiguity_detected, evidence_ids, payload
                FROM messages
                WHERE session_id::text = %s
                ORDER BY timestamp, message_id
                """,
                (sid,),
            )
            msgs = mcur.fetchall()
            if not msgs:
                continue
            if not user_id:
                user_id = next((m["user_id"] for m in msgs if m["user_id"]), "") or ""

            user_texts = [m["content"] for m in msgs if m["role"] == "user" and m["content"]]
            role_regex, evidence = detect_role(user_texts, user_id, (sm or {}).get("session_metadata") or {}, agent_id)

            uid_l = (user_id or "").lower()
            if uid_l == "anonymous":
                uid_class = "anonymous"
            elif uid_l == "":
                uid_class = "blank"
            elif uid_l.startswith("a2a_"):
                uid_class = "a2a_internal"
            elif re.match(r"^[0-9a-f-]{36}$", uid_l):
                uid_class = "registered_uuid"
            elif "|" in uid_l:
                uid_class = "registered_oauth"
            else:
                uid_class = "other"

            email = ((sm or {}).get("user_email") or "").lower()
            domain = email.split("@")[-1] if "@" in email else ""
            role_db = ((sm or {}).get("user_role_db") or "").lower()

            excl_agent = agent_id != "asha"
            excl_internal = uid_class == "a2a_internal" or any(k in uid_l for k in ("test", "benchmark", "qa_", "eval_")) or uid_l == "system"
            excl_staff = role_db in INTERNAL_ROLES or domain in STAFF_EMAIL_DOMAINS or any(f in email for f in STAFF_EMAIL_FRAGMENTS)
            excl_content = role_regex in ("test", "benchmark")
            included = not (excl_agent or excl_internal or excl_staff or excl_content)

            flow["candidates"] += 1
            if excl_agent:
                flow["excl_agent"] += 1
            if excl_internal:
                flow["excl_internal_userid"] += 1
            if excl_staff:
                flow["excl_staff"] += 1
            if excl_content:
                flow["excl_content_test"] += 1
            if included:
                flow["included"] += 1

            session_hash = short_hash(sid, "SESS")
            user_hash = short_hash(user_id, "USR")
            started = (sm["started_at"] if sm and sm["started_at"] else msgs[0]["timestamp"])
            ended = msgs[-1]["timestamp"]
            month = started.strftime("%Y-%m") if started else ""

            full_text = " ".join((m["content"] or "") for m in msgs)
            themes = detect_themes(full_text)

            n_user = sum(1 for m in msgs if m["role"] == "user")
            n_asst = sum(1 for m in msgs if m["role"] == "assistant")
            n_pws = sum(1 for m in msgs if m["role"] == "user" and PWS_PY_REGEX.search(m["content"] or ""))
            any_em = any(bool(m["is_emergency"]) for m in msgs)
            max_tg = max((m["task_gravity"] or 0.0) for m in msgs)
            cfds = [m["cf_delta"] for m in msgs if m["cf_delta"] is not None]
            min_cfd = min(cfds) if cfds else None
            first_q = next((deidentify(m["content"])[:400] for m in msgs if m["role"] == "user" and (m["content"] or "").strip()), "")

            sw.writerow([
                session_hash, user_hash, agent_id,
                started.isoformat() if started else "", ended.isoformat() if ended else "", month,
                len(msgs), n_user, n_asst, n_pws,
                uid_class, role_db, (sm or {}).get("subscription_tier") or "",
                int(excl_agent), int(excl_internal), int(excl_staff), int(excl_content),
                int(included),
                role_regex, json.dumps(evidence, separators=(",", ":")),
                "|".join(themes),
                int(any_em), f"{max_tg:.4f}", f"{min_cfd:.4f}" if min_cfd is not None else "",
                jdump(dict(emerg.get(sid, {}))), first_q,
            ])

            if not included:
                continue

            role_counts[role_regex] += 1
            month_counts[month] += 1
            user_session_counts[user_hash] += 1
            for t in themes:
                theme_counts[t] += 1

            for idx, m in enumerate(msgs):
                content = m["content"] or ""
                p = m["payload"] if isinstance(m["payload"], dict) else {}
                ev_ids = m["evidence_ids"] or []
                tw.writerow([
                    session_hash, short_hash(m["message_id"], "MSG"), user_hash, idx, m["role"],
                    m["timestamp"].isoformat() if m["timestamp"] else "",
                    int(bool(PWS_PY_REGEX.search(content))), "|".join(detect_themes(content)),
                    m["tokens_used"] or "", m["latency_ms"] or "",
                    f"{m['cf_delta']:.4f}" if m["cf_delta"] is not None else "",
                    f"{m['task_gravity']:.4f}" if m["task_gravity"] is not None else "",
                    f"{m['symbolic_entropy']:.4f}" if m["symbolic_entropy"] is not None else "",
                    int(bool(m["is_emergency"])), int(bool(m["ambiguity_detected"])), len(ev_ids),
                    jdump(payload_get(p, "evidence_count")), jdump(payload_get(p, "evidence_coverage")),
                    jdump(payload_get(p, "verification_status")), jdump(payload_get(p, "verification_passed")),
                    jdump(payload_get(p, "unverified_reason")), jdump(payload_get(p, "hallucinated_pmids")),
                    jdump(payload_get(p, "citation_validation")), jdump(payload_get(p, "emergency_type")),
                    jdump(payload_get(p, "query_type")), jdump(payload_get(p, "user_role")),
                    jdump(payload_get(p, "detected_language")), jdump(payload_get(p, "was_translated")),
                    jdump(payload_get(p, "cf_delta_v2")),
                    len(content), deidentify(content),
                ])
                mw.writerow([session_hash, sid, user_hash, user_id, short_hash(m["message_id"], "MSG"), str(m["message_id"])])
                n_turns_written += 1

            if (i + 1) % 100 == 0:
                print(f"  [progress] {i + 1}/{len(sids)} sessions, {n_turns_written} turns", flush=True)

    mcur.close()
    cur.close()
    conn.close()

    summary = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "window": [WINDOW_START, WINDOW_END],
        "lexicon_sql_regex": PWS_SQL_REGEX,
        "flow": dict(flow),
        "included_turns_written": n_turns_written,
        "included_distinct_user_hashes": len(user_session_counts),
        "included_users_with_2plus_sessions": sum(1 for c in user_session_counts.values() if c >= 2),
        "included_role_regex": dict(role_counts),
        "included_themes_regex": dict(theme_counts),
        "included_by_month": dict(sorted(month_counts.items())),
        "files": {k: str(OUT_DIR / k) for k in ("turns_deid.csv", "sessions.csv", "mapping.csv")},
        "note": "mapping.csv stays on the 5090 host; only deidentified files leave the box.",
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
