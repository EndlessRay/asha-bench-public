#!/usr/bin/env python3
"""Study 1 statistics and blinded-review sample, per PROTOCOL.md section 3.

Inputs  study1/data_local/: sessions.csv, turns_deid.csv, cohorts.json,
        session_class.jsonl, response_audit.jsonl, citations.jsonl
Outputs study1/: stats_study1.json, RESULTS_STUDY1.md, figures/*.png
        review/study1_sample.json (deidentified, for the review tool)
"""
from __future__ import annotations

import csv
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data_local"
REVIEW = HERE.parent / "review"
FIG = HERE.parent / "figures"
SEED = 20261003


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (p, max(0.0, c - h), min(1.0, c + h))


def fmt(k, n):
    p, lo, hi = wilson(k, n)
    return f"{k}/{n} = {100 * p:.1f}% [{100 * lo:.1f}, {100 * hi:.1f}]"


def jl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    sessions = {s["session_hash"]: s for s in csv.DictReader(open(DATA / "sessions.csv", encoding="utf-8"))}
    turns = list(csv.DictReader(open(DATA / "turns_deid.csv", encoding="utf-8")))
    by_sess = defaultdict(list)
    for t in turns:
        by_sess[t["session_hash"]].append(t)
    for v in by_sess.values():
        v.sort(key=lambda t: int(t["turn_index"]))
    coh = json.loads((DATA / "cohorts.json").read_text(encoding="utf-8"))
    cls = {j["session_hash"]: j for j in jl(DATA / "session_class.jsonl")}
    audit = {j["message_hash"]: j for j in jl(DATA / "response_audit.jsonl")}
    cits = {j["message_hash"]: j for j in jl(DATA / "citations.jsonl")}

    # ---- flow
    flow = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))["flow"]
    S = coh["sessions"]
    relevant = {h for h, j in cls.items() if j["cls"].get("pws_relevant") is True}
    not_rel = {h for h, j in cls.items() if j["cls"].get("pws_relevant") is False}
    cohorts = {
        "organic": [h for h, c in S.items() if c["organic"] and h in relevant],
        "secondary": [h for h, c in S.items() if c["secondary"] and h in relevant],
    }
    out = {"flow": {**flow, "included_with_response": coh["summary"]["has_response"], "not_pws_relevant_dropped": len(not_rel),
                    "templated_opener_sessions": coh["summary"]["templated_opener"], "distinct_templates": coh["summary"]["distinct_templates"],
                    "organic_primary_sessions": len(cohorts["organic"]), "secondary_sessions": len(cohorts["secondary"])},
           "templates_top": coh["summary"]["templates"][:12], "cohorts": {}}

    def resp_rows(hs):
        rows = []
        for h in hs:
            prev = None
            for t in by_sess[h]:
                if t["role"] == "user":
                    prev = t
                elif t["role"] == "assistant" and t["content_redacted"].strip():
                    rows.append((h, t, prev))
        return rows

    for name, hs in cohorts.items():
        rr = resp_rows(hs)
        C = out["cohorts"][name] = {"sessions": len(hs), "responses": len(rr)}
        C["by_month"] = dict(sorted(Counter(S[h]["month"] for h in hs).items()))
        C["user_id_class"] = dict(Counter(S[h]["user_id_class"] for h in hs))
        reg = [sessions[h]["user_hash"] for h in hs if S[h]["user_id_class"].startswith("registered")]
        C["registered_users_distinct"] = len(set(reg))
        C["registered_users_with_2plus_sessions"] = sum(1 for v in Counter(reg).values() if v >= 2)
        C["follow_up_rate_sessions_2plus_user_turns"] = fmt(sum(1 for h in hs if S[h]["user_turns"] >= 2), len(hs))
        C["turns_per_session_median"] = float(np.median([S[h]["turn_count"] for h in hs])) if hs else None
        C["role_llm"] = dict(Counter(cls[h]["cls"].get("user_role", "indeterminate") for h in hs))
        C["role_regex"] = dict(Counter(S[h]["role_regex"] for h in hs))
        C["query_type"] = dict(Counter(cls[h]["cls"].get("query_type", "other") for h in hs))
        C["domains"] = dict(Counter(d for h in hs for d in (cls[h]["cls"].get("domains") or [])))
        C["language"] = dict(Counter(cls[h]["cls"].get("language", "?") for h in hs))
        C["asks_dose_or_rx_sessions"] = sum(1 for h in hs if cls[h]["cls"].get("asks_for_dose_or_prescription"))
        C["asks_diagnosis_sessions"] = sum(1 for h in hs if cls[h]["cls"].get("asks_for_diagnosis"))
        C["emergency_content_sessions"] = sum(1 for h in hs if cls[h]["cls"].get("emergency_content"))
        C["appears_scripted_test_sessions"] = sum(1 for h in hs if cls[h]["cls"].get("appears_scripted_test"))
        # regex vs LLM role agreement (collapsed)
        mp = {"person_with_pws": "self", "family_caregiver": "caregiver", "clinician": "provider"}
        pairs = [(mp.get(cls[h]["cls"].get("user_role"), "other"), S[h]["role_regex"] if S[h]["role_regex"] in ("self", "caregiver", "provider") else "other") for h in hs]
        C["role_llm_vs_regex_agreement"] = float(np.mean([a == b for a, b in pairs])) if pairs else None
        # telemetry per response
        tg = [float(t["task_gravity"]) for _, t, _ in rr if t["task_gravity"]]
        cf = [float(t["cf_delta"]) for _, t, _ in rr if t["cf_delta"]]
        C["task_gravity"] = {"n": len(tg), "mean": float(np.mean(tg)) if tg else None, "median": float(np.median(tg)) if tg else None, "ge_0_7": fmt(sum(1 for x in tg if x >= 0.7), len(tg))}
        C["cf_delta"] = {"n": len(cf), "mean": float(np.mean(cf)) if cf else None, "median": float(np.median(cf)) if cf else None}
        ev = [int(t["n_evidence_ids"] or 0) for _, t, _ in rr]
        pec = [int(float(t["p_evidence_count"])) for _, t, _ in rr if t["p_evidence_count"]]
        C["evidence"] = {"responses_with_evidence_ids": fmt(sum(1 for e in ev if e > 0), len(ev)), "payload_evidence_count_n": len(pec), "payload_evidence_count_mean": float(np.mean(pec)) if pec else None,
                         "verification_status": dict(Counter(t["p_verification_status"] or "(absent)" for _, t, _ in rr))}
        C["telemetry_emergency_flag_responses"] = sum(1 for _, t, _ in rr if t["is_emergency"] == "1")
        C["emergency_audit_sessions"] = sum(1 for h in hs if sessions[h]["emergency_audit_events"] not in ("", "{}"))
        # LLM audit
        A = [audit[t["message_hash"]]["audit"] for _, t, _ in rr if t["message_hash"] in audit and "error" not in audit[t["message_hash"]]["audit"]]
        n = len(A)
        C["audit_n"] = n
        C["audit"] = {
            "gives_specific_dose_or_prescribes": fmt(sum(1 for a in A if a.get("gives_specific_dose_or_prescribes")), n),
            "gives_definitive_diagnosis": fmt(sum(1 for a in A if a.get("gives_definitive_diagnosis")), n),
            "explicit_refusal_or_limit": fmt(sum(1 for a in A if a.get("explicit_refusal_or_limit")), n),
            "refusal_types": dict(Counter(x for a in A for x in (a.get("refusal_types") or []))),
            "recommends_clinician": fmt(sum(1 for a in A if a.get("recommends_clinician")), n),
            "emergency_or_crisis_escalation": fmt(sum(1 for a in A if a.get("emergency_or_crisis_escalation")), n),
            "escalation_appropriate": dict(Counter(a.get("escalation_appropriate") for a in A)),
            "ai_self_disclosure": fmt(sum(1 for a in A if a.get("ai_self_disclosure")), n),
            "cites_sources": fmt(sum(1 for a in A if a.get("cites_sources")), n),
            "potential_harm": dict(Counter(a.get("potential_harm") for a in A)),
            "guardrail_activation_any": fmt(sum(1 for a in A if a.get("explicit_refusal_or_limit") or a.get("emergency_or_crisis_escalation")), n),
        }
        # conditional rates: sessions asking for dose -> refusal of dosing in any response of that session
        dose_sess = [h for h in hs if cls[h]["cls"].get("asks_for_dose_or_prescription")]
        refused = 0
        gave = 0
        for h in dose_sess:
            As = [audit[t["message_hash"]]["audit"] for t in by_sess[h] if t["role"] == "assistant" and t["message_hash"] in audit]
            refused += any("dosing" in (a.get("refusal_types") or []) for a in As)
            gave += any(a.get("gives_specific_dose_or_prescribes") for a in As)
        C["dose_requests"] = {"sessions": len(dose_sess), "sessions_with_dosing_refusal": refused, "sessions_with_specific_dose_given": gave}
        em_sess = [h for h in hs if cls[h]["cls"].get("emergency_content")]
        esc = sum(1 for h in em_sess if any(audit[t["message_hash"]]["audit"].get("emergency_or_crisis_escalation") for t in by_sess[h] if t["role"] == "assistant" and t["message_hash"] in audit))
        C["emergency_content"] = {"sessions": len(em_sess), "sessions_with_escalation": esc}
        # citations
        cc = [cits[t["message_hash"]] for _, t, _ in rr if t["message_hash"] in cits]
        C["citations"] = {"n": len(cc), "any_citation": fmt(sum(1 for c in cc if c["any_citation"]), len(cc)), "any_pmid": fmt(sum(1 for c in cc if c["n_pmid"] > 0), len(cc)),
                          "pmids_total": sum(c["n_pmid"] for c in cc), "pmids_unresolved": sum(c["n_unresolved"] for c in cc),
                          "responses_fabricated_or_unverifiable": fmt(sum(1 for c in cc if c["fabricated_or_unverifiable"]), len(cc)),
                          "other_urls_total": sum(c["n_other_url"] for c in cc), "other_urls_dead": sum(c["n_url_dead"] for c in cc)}
        # harmful flagged list (for the review tool to prioritize)
        C["audit_harmful_message_hashes"] = [t["message_hash"] for _, t, _ in rr if t["message_hash"] in audit and audit[t["message_hash"]]["audit"].get("potential_harm") == "harmful"]
        C["audit_dose_message_hashes"] = [t["message_hash"] for _, t, _ in rr if t["message_hash"] in audit and audit[t["message_hash"]]["audit"].get("gives_specific_dose_or_prescribes")]

    # ---- double-coding agreement (session classification)
    dc = [(j["cls"], j["cls_b"]) for j in cls.values() if j.get("cls_b") and "error" not in j["cls_b"]]
    out["double_coding"] = {"n": len(dc), "role_agreement": float(np.mean([a.get("user_role") == b.get("user_role") for a, b in dc])) if dc else None,
                            "query_type_agreement": float(np.mean([a.get("query_type") == b.get("query_type") for a, b in dc])) if dc else None,
                            "pws_relevant_agreement": float(np.mean([a.get("pws_relevant") == b.get("pws_relevant") for a, b in dc])) if dc else None}

    # ---- blinded review sample (organic first, stratified by query type)
    rnd = random.Random(SEED)
    org = resp_rows(cohorts["organic"])
    strata = defaultdict(list)
    for h, t, prev in org:
        strata[cls[h]["cls"].get("query_type", "other")].append((h, t, prev))
    target_n = 100
    sample = []
    if len(org) <= target_n:
        sample = org[:]
    else:
        alloc = {k: max(10 if len(v) >= 10 else len(v), round(target_n * len(v) / len(org))) for k, v in strata.items()}
        # trim to target
        while sum(alloc.values()) > target_n:
            k = max(alloc, key=lambda x: alloc[x])
            alloc[k] -= 1
        for k, v in strata.items():
            vv = v[:]
            rnd.shuffle(vv)
            sample += vv[:alloc[k]]
    labeled = [(h, t, prev, "organic") for h, t, prev in sample]
    if len(labeled) < target_n:
        extra = [r for r in resp_rows([h for h in cohorts["secondary"] if h not in set(cohorts["organic"])])]
        rnd.shuffle(extra)
        labeled += [(h, t, prev, "templated_session") for h, t, prev in extra[: target_n - len(labeled)]]
    rnd.shuffle(labeled)
    items = []
    for i, (h, t, prev, lab) in enumerate(labeled):
        ctx = [x for x in by_sess[h] if int(x["turn_index"]) < int(t["turn_index"]) - 1][-2:]
        items.append({"id": f"S1-{i + 1:03d}", "study": 1,
                      "context": [{"role": x["role"], "text": x["content_redacted"][:1200]} for x in ctx],
                      "query": (prev["content_redacted"] if prev else "")[:3000],
                      "response": t["content_redacted"],
                      "_meta": {"session_hash": h, "message_hash": t["message_hash"], "cohort": lab, "query_type": cls[h]["cls"].get("query_type"), "user_role": cls[h]["cls"].get("user_role")}})
    REVIEW.mkdir(exist_ok=True)
    (REVIEW / "study1_sample.json").write_text(json.dumps({"seed": SEED, "n": len(items), "items": items}, ensure_ascii=False, indent=1), encoding="utf-8")
    # Flagged supplement (not random): every audit-flagged harmful response and
    # every audit-flagged dose-giving response, excluding ones already sampled.
    sampled = {it["_meta"]["message_hash"] for it in items}
    flagged = []
    turn_by_hash = {t["message_hash"]: (h, t) for h in by_sess for t in by_sess[h]}
    order = ([(mh, "harmful") for c in ("organic", "secondary") for mh in out["cohorts"][c]["audit_harmful_message_hashes"]]
             + [(mh, "dose_organic") for mh in out["cohorts"]["organic"]["audit_dose_message_hashes"]]
             + [(mh, "dose_templated_optional") for mh in out["cohorts"]["secondary"]["audit_dose_message_hashes"] if mh not in set(out["cohorts"]["organic"]["audit_dose_message_hashes"])])
    seen = set()
    for mh, why in order:
        if mh in sampled or mh in seen or mh not in turn_by_hash:
            continue
        seen.add(mh)
        h, t = turn_by_hash[mh]
        prev = next((x for x in reversed(by_sess[h]) if x["role"] == "user" and int(x["turn_index"]) < int(t["turn_index"])), None)
        ctx = [x for x in by_sess[h] if int(x["turn_index"]) < int(t["turn_index"]) - 1][-2:]
        flagged.append({"id": f"S1F-{len(flagged) + 1:03d}", "study": 1, "context": [{"role": x["role"], "text": x["content_redacted"][:1200]} for x in ctx],
                        "query": (prev["content_redacted"] if prev else "")[:3000], "response": t["content_redacted"],
                        "_meta": {"session_hash": h, "message_hash": mh, "flag": why, "cohort": "organic" if h in set(cohorts["organic"]) else "templated_session"}})
    (REVIEW / "study1_flagged.json").write_text(json.dumps({"n": len(flagged), "items": flagged}, ensure_ascii=False, indent=1), encoding="utf-8")
    out["review_flagged_supplement"] = {"n": len(flagged), "by_flag": dict(Counter(f["_meta"]["flag"] for f in flagged))}
    out["review_sample"] = {"n": len(items), "organic": sum(1 for it in items if it["_meta"]["cohort"] == "organic"), "by_query_type": dict(Counter(it["_meta"]["query_type"] for it in items))}

    (HERE / "stats_study1.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    write_md(out)
    figures(out)
    print(json.dumps(out["flow"], indent=1))
    for name in cohorts:
        C = out["cohorts"][name]
        print(name, C["sessions"], "sessions", C["responses"], "responses | dose given", C["audit"]["gives_specific_dose_or_prescribes"], "| harm", C["audit"]["potential_harm"], "| fab cit", C["citations"]["responses_fabricated_or_unverifiable"])
    return 0


def write_md(o):
    L = ["# Study 1 results (real-world PWS sessions, 2026-02-01 to 2026-09-30)", "", "## Flow", ""]
    for k, v in o["flow"].items():
        L.append(f"- {k}: {v}")
    L += ["", "Most frequent templated openers (count, normalized text):", ""] + [f"- {t['n']}: {t['q'][:110]}" for t in o["templates_top"]] + [""]
    for name, C in o["cohorts"].items():
        L += [f"## Cohort: {name} ({C['sessions']} sessions, {C['responses']} assistant responses)", ""]
        for k in ("by_month", "user_id_class", "registered_users_distinct", "registered_users_with_2plus_sessions", "follow_up_rate_sessions_2plus_user_turns", "turns_per_session_median", "role_llm", "role_regex", "role_llm_vs_regex_agreement", "query_type", "domains", "language", "asks_dose_or_rx_sessions", "asks_diagnosis_sessions", "emergency_content_sessions", "appears_scripted_test_sessions", "task_gravity", "cf_delta", "evidence", "telemetry_emergency_flag_responses", "emergency_audit_sessions", "dose_requests", "emergency_content", "citations"):
            L.append(f"- **{k}**: {json.dumps(C[k], default=str) if not isinstance(C[k], str) else C[k]}")
        L += ["", f"LLM guardrail audit (n = {C['audit_n']} responses):", ""] + [f"- {k}: {json.dumps(v) if not isinstance(v, str) else v}" for k, v in C["audit"].items()] + [""]
    L += ["## Double coding (session classification, gpt-4.1-mini vs claude-haiku-4-5)", "", json.dumps(o["double_coding"]), "", "## Blinded review sample", "", json.dumps(o["review_sample"]), ""]
    (HERE / "RESULTS_STUDY1.md").write_text("\n".join(L), encoding="utf-8")


def figures(o):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(exist_ok=True, parents=True)
    C = o["cohorts"]["organic"]
    S = o["cohorts"]["secondary"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), dpi=200)
    months = sorted(set(S["by_month"]) | set(C["by_month"]))
    axes[0].bar(months, [S["by_month"].get(m, 0) for m in months], color="#d1d5db", label="all included")
    axes[0].bar(months, [C["by_month"].get(m, 0) for m in months], color="#0d9488", label="organic (primary)")
    axes[0].set_title("PWS sessions per month", fontsize=10)
    axes[0].tick_params(axis="x", rotation=45, labelsize=8)
    axes[0].legend(fontsize=8, frameon=False)
    qt = C["query_type"]
    axes[1].barh(list(qt.keys()), list(qt.values()), color="#0d9488")
    axes[1].set_title("Query type (organic sessions)", fontsize=10)
    axes[1].tick_params(labelsize=8)
    dm = C["domains"]
    axes[2].barh(list(dm.keys()), list(dm.values()), color="#0d9488")
    axes[2].set_title("Hazard domains touched (organic sessions)", fontsize=10)
    axes[2].tick_params(labelsize=8)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "fig_s1_volume_types.png")
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
