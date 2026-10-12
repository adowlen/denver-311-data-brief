"""Denver 311 analysis 2023-2025: topics, resolution equity, trends."""
import csv, json, re
from collections import Counter, defaultdict
from datetime import datetime
import statistics

DATA = "/home/hatch/workspace/goals/daily-civic-data-brief/hidden_files/311-brief-2026-10-12/data"
OUT = "/home/hatch/workspace/goals/daily-civic-data-brief/hidden_files/311-brief-2026-10-12"

def parse_dt(s):
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d %H:%M:%S", "%m-%d-%Y %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def norm_summary(s):
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def analyze_year(yr):
    path = f"{DATA}/311_{yr}.csv"
    topics = Counter()
    districts = defaultdict(list)   # council district -> [resolution days]
    hoods = defaultdict(list)       # neighborhood -> [resolution days]
    agencies = Counter()
    statuses = Counter()
    sources = Counter()
    monthly = Counter()
    n = 0
    closed_valid = 0
    same_day = 0
    fcr_y = 0
    res_all = []
    try:
        fh = open(path, encoding="latin-1")
    except FileNotFoundError:
        return None
    with fh:
        r = csv.DictReader(fh)
        for row in r:
            n += 1
            topics[norm_summary(row.get("Case Summary"))] += 1
            agencies[row.get("Agency") or "(blank)"] += 1
            statuses[row.get("Case Status") or "(blank)"] += 1
            sources[row.get("Case Source") or "(blank)"] += 1
            if (row.get("First Call Resolution") or "").strip().upper() == "Y":
                fcr_y += 1
            c = parse_dt(row.get("Case Created dttm"))
            cl = parse_dt(row.get("Case Closed dttm"))
            if c:
                monthly[c.strftime("%Y-%m")] += 1
            if c and cl and cl >= c:
                d = (cl - c).total_seconds() / 86400
                closed_valid += 1
                res_all.append(d)
                if d < 1:
                    same_day += 1
                cd = (row.get("Council District") or "").strip()
                nh = (row.get("Neighborhood") or "").strip()
                if cd:
                    districts[cd].append(d)
                if nh:
                    hoods[nh].append(d)
    res_all.sort()
    def pct(arr, p):
        return arr[min(int(len(arr) * p), len(arr) - 1)] if arr else None
    return {
        "year": yr, "rows": n,
        "topics": topics.most_common(25),
        "agencies": agencies.most_common(15),
        "statuses": statuses.most_common(15),
        "sources": sources.most_common(10),
        "monthly": dict(sorted(monthly.items())),
        "closed_valid": closed_valid,
        "res_median": statistics.median(res_all) if res_all else None,
        "res_p90": pct(res_all, 0.9),
        "res_mean": sum(res_all) / len(res_all) if res_all else None,
        "same_day_rate": same_day / closed_valid if closed_valid else None,
        "fcr_y_rate": fcr_y / n if n else None,
        "districts": {k: {"n": len(v), "median": statistics.median(v),
                           "p90": pct(sorted(v), 0.9)}
                       for k, v in districts.items()},
        "hoods": {k: {"n": len(v), "median": statistics.median(v)}
                  for k, v in hoods.items() if len(v) >= 200},
        "hoods_p90": {k: {"n": len(v), "p90": pct(sorted(v), 0.9)}
                      for k, v in hoods.items() if len(v) >= 200},
    }

import sys
years = sys.argv[1:] or ["2023", "2024", "2025"]
results = {}
for yr in years:
    print(f"Analyzing {yr}...", flush=True)
    r = analyze_year(yr)
    if r:
        results[yr] = r
        print(f"  rows={r['rows']:,} closed_valid={r['closed_valid']:,} "
              f"median={r['res_median']:.2f}d p90={r['res_p90']:.1f}d "
              f"sameday={r['same_day_rate']:.1%}", flush=True)

# slim for JSON: drop full hoods dicts detail but keep
slim = {}
for yr, r in results.items():
    s = dict(r)
    s["topics"] = r["topics"]
    slim[yr] = s
with open(f"{OUT}/stats.json", "w") as fh:
    json.dump(slim, fh, indent=1, default=str)
print("wrote stats.json")
