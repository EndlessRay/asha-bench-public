#!/usr/bin/env python3
"""Mechanically verify every PMID in the item bank's SOURCES against NCBI
esummary before lock. Prints first author, year and title for each PMID and
flags mismatches (surname or year differs from the citation string).
Sacred refusal #2: no fabricated citations, including our own."""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_items import SOURCES  # noqa: E402

pmids = {k: v["pmid"] for k, v in SOURCES.items() if v.get("pmid")}
url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids.values()), "retmode": "json"})
for attempt in range(3):
    try:
        data = json.load(urllib.request.urlopen(url, timeout=30))
        break
    except Exception as exc:  # pragma: no cover
        print("retry", exc)
        time.sleep(2)
else:
    sys.exit("esummary failed")

res = data.get("result", {})
bad = 0
for key, pmid in pmids.items():
    r = res.get(pmid)
    cite = SOURCES[key]["cite"]
    want_surname = re.match(r"([A-Za-zÀ-ÿ' -]+?)\s", cite).group(1).split()[0].lower().replace("ö","o")
    want_year = re.search(r"\b(19|20)\d{2}\b", cite).group(0)
    if not r or "error" in r:
        print(f"MISSING  {key} PMID {pmid}")
        bad += 1
        continue
    first = (r.get("sortfirstauthor") or (r["authors"][0]["name"] if r.get("authors") else "")).lower()
    year = (r.get("pubdate") or "")[:4]
    title_ok = cite.lower()[:40].split(".")[-1].strip()[:20] in (r.get("title") or "").lower()
    ok = (want_surname in first or want_surname in ("aap", "american") or title_ok) and want_year == year
    print(f"{'OK      ' if ok else 'MISMATCH'} {key} PMID {pmid} | {first} {year} | {r.get('title','')[:110]}")
    if not ok:
        bad += 1
print(f"\n{len(pmids) - bad}/{len(pmids)} PMIDs verified")
sys.exit(1 if bad else 0)
