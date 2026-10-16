"""Paired item-level bootstrap CIs for the HealthBench harm proxy (criterion level).

Inputs: public per-item grades in EndlessRay/asha-benchmarks@09df556 cloned to /tmp/asha-benchmarks,
and the official HealthBench Hard id list (hard_2025-05-08-21-00-10.jsonl) at /tmp/hb_hard.jsonl.
Output: research/harm_ci.csv. 4,000 percentile resamples, seed 20261015.
"""
import gzip, json, random
root="/tmp/asha-benchmarks/healthbench-5000-2026-09-20"
hard={json.loads(l)["prompt_id"] for l in open("/tmp/hb_hard.jsonl")}
def load(arm,g):
    out={}
    for l in gzip.open(f"{root}/{arm}/graded_{g}.jsonl.gz","rt"):
        r=json.loads(l); neg=[c for c in r.get("rubric_grades",[]) if c["points"]<0]
        out[r["prompt_id"]]=(sum(1 for c in neg if c["met"]),len(neg))
    return out
random.seed(20261015)
rows=[]
for g in ["gpt_4_1","gpt_5_4","claude_opus_4_8"]:
    A=load("asha-apex-j-frozen",g); B=load("bare-gpt-6-astra",g)
    for name,filt in [("Standard",lambda k:True),("Hard",lambda k:k in hard)]:
        ids=[k for k in A if k in B and filt(k) and A[k][1]==B[k][1] and A[k][1]>0]
        def d(sample):
            am=sum(A[k][0] for k in sample); bm=sum(B[k][0] for k in sample); n=sum(A[k][1] for k in sample)
            return 100*(am-bm)/n, 100*am/n, 100*bm/n
        pt=d(ids); bs=sorted(d([random.choice(ids) for _ in ids])[0] for _ in range(4000))
        rows.append((g,name,len(ids),pt[1],pt[2],pt[0],bs[100],bs[3899]))
        print(f"{g:16s} {name:8s} n={len(ids):5d} asha={pt[1]:.2f} bare={pt[2]:.2f} diff={pt[0]:+.2f} CI[{bs[100]:+.2f},{bs[3899]:+.2f}]")
import csv
with open("research/harm_ci.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.writer(fh); w.writerow(["grader","set","n_paired","asha_pct","bare_pct","diff_pp","ci95_low","ci95_high"])
    for r in rows: w.writerow([r[0],r[1],r[2]]+[f"{x:.2f}" for x in r[3:]])
