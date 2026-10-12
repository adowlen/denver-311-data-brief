"""Download 2023 Denver 311 data from ArcGIS FeatureServer (paged)."""
import csv, sys, time, urllib.request, urllib.parse, json

FS = "https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services/311_Service_Requests_2023/FeatureServer/0"
OUT = "/home/hatch/workspace/goals/daily-civic-data-brief/hidden_files/311-brief-2026-10-12/data/311_2023.csv"
PAGE = 1000

def fetch(offset):
    q = {
        "where": "1=1", "outFields": "*", "returnGeometry": "false",
        "resultOffset": offset, "resultRecordCount": PAGE, "f": "json",
        "orderByFields": "ObjectId",
    }
    url = FS + "/query?" + urllib.parse.urlencode(q)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print(f"offset {offset} attempt {attempt}: {e}", file=sys.stderr, flush=True)
            time.sleep(2 + attempt * 2)
    raise RuntimeError(f"failed at offset {offset}")

first = fetch(0)
fields = [f["name"] for f in first["fields"]]
total = 0
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(fields)
    offset = 0
    while True:
        data = first if offset == 0 else fetch(offset)
        feats = data.get("features", [])
        if not feats:
            break
        for ft in feats:
            a = ft["attributes"]
            w.writerow([a.get(c) for c in fields])
        total += len(feats)
        offset += len(feats)
        if offset % 20000 == 0:
            print(f"...{offset}", flush=True)
        if len(feats) < PAGE:
            break
print(f"DONE total={total}")
