#!/usr/bin/env python3
"""Render BENCHMARKS.md from the public benchmark register JSON.

The register (benchmarks/register/benchmarks_live_<date>.json) is the same
document served at https://dnai.systems/benchmarks.json and by the Asha API at
/api/benchmarks. Nothing in this file is typed by hand: every number comes
from the register, so the markdown cannot drift from the page.

Usage: python3 tools/build_benchmarks_md.py [register.json] > BENCHMARKS.md
"""
from __future__ import annotations

import glob
import json
import sys


def fmt(x, unit=None):
    if x is None:
        return "n/a"
    if unit == "scale_1_5":
        return f"{x:.2f} / 5"
    return f"{x:.1f}" if isinstance(x, (int, float)) else str(x)


def ci(row):
    c = row.get("ci95")
    if not c or c[0] is None:
        return ""
    return f" [{fmt(c[0])}, {fmt(c[1])}]"


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("benchmarks/register/benchmarks_live_*.json"))[-1]
    reg = json.load(open(path, encoding="utf-8"))
    out = []
    out.append("# DNAi benchmarks (public register)\n")
    out.append(f"Rendered from `{path}` (register updated {reg.get('updated')}). "
               f"Canonical live page: {reg.get('canonical_page')}. Canonical JSON: {reg.get('canonical_json')}.\n")
    pol = reg.get("policy", {})
    out.append("## Publication policy\n")
    out.append(pol.get("summary", "") + "\n")
    tiers = pol.get("tiers", {})
    if tiers:
        out.append("| Tier | Meaning |\n|---|---|")
        for k, v in tiers.items():
            out.append(f"| {k} | {v} |")
        out.append("")
    bases = pol.get("comparator_bases", {})
    if bases:
        out.append("| Comparator basis | Meaning |\n|---|---|")
        for k, v in bases.items():
            out.append(f"| `{k}` | {v} |")
        out.append("")
    if pol.get("production_note"):
        out.append(pol["production_note"] + "\n")

    out.append("## Board\n")
    out.append("| Benchmark | Set | n | Configuration | Result | Grader | Best same-grader comparator | Tier |\n|---|---|---|---|---|---|---|---|")
    for r in reg["benchmarks"]:
        same = [c for c in r.get("comparators", []) if c.get("basis") == "same_grader_self_run"
                and not str(c.get("system", "")).startswith(("Asha", "Physician"))]
        best = max(same, key=lambda c: c.get("score") or -1) if same else None
        comp = f"{fmt(best.get('score'), best.get('unit') or r.get('unit'))} {best.get('system')}" if best else "none"
        out.append(f"| {r.get('benchmark')} | {r.get('set')} | {r.get('n')} | {r.get('configuration')} | "
                   f"**{fmt(r.get('score'), r.get('unit'))}**{ci(r)} | {r.get('grader')} | {comp} | {r.get('tier')} |")
    out.append("")

    out.append("## Rows\n")
    for r in reg["benchmarks"]:
        out.append(f"### {r.get('benchmark')}: {r.get('set')} (`{r['id']}`)\n")
        out.append(f"- Pipeline / configuration: {r.get('pipeline')}; {r.get('configuration')}")
        out.append(f"- Deployed tier: {r.get('deployed_tier')}")
        out.append(f"- Result: **{fmt(r.get('score'), r.get('unit'))}**{ci(r)} ({r.get('metric')}; CI method {r.get('ci_method')}); n = {r.get('n')}; run date {r.get('run_date')}")
        out.append(f"- Grader: {r.get('grader')}")
        if r.get("harm_gate"):
            hg = r["harm_gate"]
            out.append(f"- Pre-registered harm test: {hg.get('rule')}: {hg.get('delta_pts'):+.1f} points, bound {hg.get('bound_pts')}, {'passed' if hg.get('passed') else 'NOT met'}")
        comps = r.get("comparators", [])
        if comps:
            out.append("- Comparators:")
            for c in comps:
                out.append(f"  - {c.get('system')}: {fmt(c.get('score'), c.get('unit') or r.get('unit'))}"
                           + (f" (n={c['n']})" if c.get("n") else "") + f", basis `{c.get('basis')}`"
                           + (f": {c['source']}" if c.get("source") else ""))
        ps = r.get("paired_statistics", [])
        if ps:
            out.append("- Paired statistics:")
            for p in ps:
                out.append(f"  - {p.get('comparison')}: {p.get('delta_pp'):+} pp"
                           + (f", W/L/T {p['wins_losses_ties']}" if p.get("wins_losses_ties") else "")
                           + f", n={p.get('n')}, {p.get('test')}, p={p.get('p')}")
        sec = r.get("secondary_results", [])
        if sec:
            out.append("- Also measured:")
            for s in sec:
                out.append(f"  - {s.get('metric')}: {fmt(s.get('score'), s.get('unit'))}"
                           + (f" vs {fmt(s.get('comparator_score'))} bare" if s.get("comparator_score") is not None else "")
                           + (f" (n={s['n']})" if s.get("n") else "") + (f". {s['note']}" if s.get("note") else ""))
        if r.get("notes"):
            out.append(f"- Notes: {r['notes']}")
        if r.get("lay_summary"):
            out.append(f"- In plain terms: {r['lay_summary']}")
        arts = r.get("artifacts", [])
        if arts:
            out.append("- Artifacts: " + "; ".join(f"[{a.get('label')}]({a.get('url')})" for a in arts))
        out.append("")

    app = reg.get("appendix_small_n")
    if app:
        out.append("## Appendix: small-n scenarios\n")
        out.append(app.get("note", "") if isinstance(app, dict) else "")
        rows = app.get("rows", []) if isinstance(app, dict) else app
        if rows:
            out.append("Small samples (below the register's n threshold): reported with intervals where the metric is a proportion, never as headline claims.\n")
            out.append("| Benchmark | Set | n | Configuration | Result | Comparators | Grader |\n|---|---|---|---|---|---|---|")
            for s in rows:
                comps = "; ".join(f"{fmt(c.get('score'), c.get('unit') or s.get('unit'))} {c.get('system')}" for c in s.get("comparators", []))
                out.append(f"| {s.get('benchmark')} | {s.get('set')} | {s.get('n')} | {s.get('configuration')} | "
                           f"**{fmt(s.get('score'), s.get('unit'))}**{ci(s)} | {comps or 'none'} | {s.get('grader')} |")
            out.append("")
    ev = reg.get("external_validation")
    if ev:
        out.append("## External validation\n")
        out.append(f"- Validator: {ev.get('validator')}\n- Protocol: {ev.get('protocol')}\n- Status: {ev.get('status')}")
        for k in ("confirmed", "refuted", "corrections"):
            if ev.get(k):
                out.append(f"- {k.capitalize()}: " + "; ".join(str(x) for x in ev[k]))
        out.append("")
    rep = reg.get("reproduce")
    if rep:
        out.append("## Reproduce\n")
        for x in rep:
            out.append(f"- [{x.get('label')}]({x.get('url')})")
        out.append("")
    sys.stdout.write("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
