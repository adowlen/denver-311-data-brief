"""Resumable 2023 download via ObjectId-range paging (robust)."""
import csv, sys, time, urllib.request, urllib.parse, json

FS = "https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services/311_Service_Requests_2023/FeatureServer/0"
OUT = "/home/hatch/workspace/goals/daily-civic-data-brief/hidden_files/311-brief-2026-10-12/data/311_2023.csv"
PAGE = 1000

def fetch(where):
    q = {"where": where, "outFields": "*", "returnGeometry": "false",
         "resultRecordCount": PAGE, "f": "json", "orderByFields": "ObjectId"}
    url = FS + "/query?" + urllib.parse.urlencode(q)
    last = None
    for attempt in range(8):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                d = json.load(r)
            if "error" in d:
                raise RuntimeError(d["error"])
            return d.get("features", [])
        except Exception as e:
            last = e
            print(f"  retry {attempt} ({type(e).__name__})", file=sys.stderr, flush=True)
            time.sleep(4 + attempt * 4)
    raise RuntimeError(f"failed: {where}: {last}")

with open(OUT, encoding="latin-1") as fh:
    rd = csv.DictReader(fh)
    fields = rd.fieldnames
    last_id = 0
    n = 0
    for row in rd:
        n += 1
        try:
            oid = int(row.get("ObjectId") or 0)
        except ValueError:
            oid = 0
        if oid > last_id:
            last_id = oid
print(f"existing rows={n} max ObjectId={last_id}", flush=True)

total = n
with open(OUT, "a", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    empty_streak = 0
    while last_id < 474695:
        feats = fetch(f"ObjectId > {last_id}")
        if not feats:
            empty_streak += 1
            print(f"empty page (streak {empty_streak}), waiting...", flush=True)
            time.sleep(10 + empty_streak * 5)
            if empty_streak >= 6:
                print("too many empty pages, stopping", flush=True)
                break
            continue
        empty_streak = 0
        for ft in feats:
            a = ft["attributes"]
            w.writerow([a.get(c) for c in fields])
            oid = a.get("ObjectId") or 0
            if oid > last_id:
                last_id = oid
        total += len(feats)
        print(f"...{total} (maxId {last_id})", flush=True)
        if len(feats) < PAGE:
            break
print(f"DONE total={total}")
