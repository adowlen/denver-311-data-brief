"""Charts for Denver 311 brief - Machine Readable brand palette."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Brand palette
CHARCOAL = "#23221F"
PAPER = "#F1E7DA"
AMBER = "#E8A33D"
TEAL = "#2AA198"
AMBER_DIM = "#8A6420"
TEAL_DIM = "#1E6E68"
GRID = "#4A453C"
TEXT = "#F1E7DA"
TEXT_DIM = "#B8AE9C"

OUT = "/home/hatch/workspace/goals/daily-civic-data-brief/hidden_files/311-brief-2026-10-12/charts"
import os
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": CHARCOAL,
    "axes.facecolor": CHARCOAL,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": TEXT_DIM,
    "ytick.color": TEXT_DIM,
    "grid.color": GRID,
    "grid.alpha": 0.5,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlecolor": TEXT,
})

s = json.load(open("/home/hatch/workspace/goals/daily-civic-data-brief/hidden_files/311-brief-2026-10-12/stats.json"))
years = [y for y in ["2023", "2024", "2025"] if y in s]

def save(fig, name):
    fig.tight_layout()
    fig.savefig(f"{OUT}/{name}", dpi=150, facecolor=CHARCOAL)
    plt.close(fig)
    print("saved", name)

# 1. Top 12 case summaries, 2025 (horizontal bars, amber)
r = s["2025"]
topics = [(t, c) for t, c in r["topics"] if t][:12]
topics = topics[::-1]
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh([t[:42] for t, c in topics], [c for t, c in topics], color=AMBER, edgecolor="none")
ax.set_title("What Denver calls 311 about most, 2025")
ax.set_xlabel("cases")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
for i, (t, c) in enumerate(topics):
    ax.text(c * 1.01, i, f"{c:,}", va="center", fontsize=9, color=TEXT)
save(fig, "top_topics_2025.png")

# 2. Median resolution days by council district, 2023 (full coverage year)
if "2023" in s:
    d = s["2023"]["districts"]
    items = sorted(d.items(), key=lambda kv: kv[1]["median"])
    labels = [f"D{k}" for k, v in items]
    meds = [v["median"] for k, v in items]
    colors = [TEAL if m <= sorted(meds)[len(meds)//2] else AMBER for m in meds]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(labels, meds, color=colors, edgecolor="none")
    ax.set_title("Median 311 resolution time by council district, 2023\n(full district coverage; teal = faster half)")
    ax.set_ylabel("median days to close")
    ax.set_ylim(0, max(meds) * 1.25)
    for i, m in enumerate(meds):
        ax.text(i, m + max(meds)*0.03, f"{m:.1f}d", ha="center", fontsize=9, color=TEXT)
    save(fig, "district_medians_2023.png")

# 3. Trend: volume + same-day close rate 2023-2025 (twin axis)
vols = [s[y]["rows"] for y in years]
sdr = [s[y]["same_day_rate"] * 100 for y in years]
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.bar(years, vols, color=TEAL, alpha=0.85, edgecolor="none", label="cases")
ax1.set_ylabel("total 311 cases", color=TEAL)
ax1.tick_params(axis="y", labelcolor=TEAL)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x/1000)}k"))
for i, v in enumerate(vols):
    ax1.text(i, v * 1.01, f"{v:,}", ha="center", fontsize=10, color=TEXT)
ax2 = ax1.twinx()
ax2.plot(years, sdr, color=AMBER, marker="o", lw=2.5, markersize=8)
ax2.set_ylabel("closed same-day (%)", color=AMBER)
ax2.tick_params(axis="y", labelcolor=AMBER)
ax2.set_ylim(min(sdr) - 3, 100)
for i, v in enumerate(sdr):
    ax2.text(i, v + 0.4, f"{v:.1f}%", ha="center", fontsize=10, color=AMBER, fontweight="bold")
ax1.set_title("311 volume vs. same-day resolution, 2023-2025")
save(fig, "volume_trend.png")

# 4. Encampment reporting: the re-categorization (monthly bars 2025)
# computed separately; placeholder values filled from analysis
enc = {
    "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
    "reporting": [529,466,767,762,727,809,888,911,473,257,205,171],
    "engagement": [0,0,0,0,0,0,0,0,421,605,533,421],
}
fig, ax = plt.subplots(figsize=(11, 5))
x = range(12)
ax.bar(x, enc["reporting"], color=AMBER, label="Encampment Reporting", edgecolor="none")
ax.bar(x, enc["engagement"], bottom=enc["reporting"], color=TEAL, label="Encampment / Street Engagement", edgecolor="none")
ax.set_xticks(list(x)); ax.set_xticklabels(enc["months"])
ax.set_title('Encampment reports didn\'t fall in late 2025 — they were re-categorized')
ax.set_ylabel("cases per month")
ax.legend(frameon=False, fontsize=10)
ax.text(9.5, 1050, "new category\nstarts Sep 2025", color=TEAL, fontsize=9, ha="center")
save(fig, "encampment_recategorization.png")

# 5. Resolution distribution: p50/p90 by district 2025 (shows tail inequality)
if "2025" in s:
    d = s["2025"]["districts"]
    items = sorted(d.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 99)
    labels = [f"D{k}" for k, v in items]
    p90s = [v["p90"] for k, v in items]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(labels, p90s, color=AMBER, edgecolor="none")
    ax.set_title("Slowest 10% of 311 cases by council district, 2025\n(90th percentile days to close — partial district coverage)")
    ax.set_ylabel("days (90th percentile)")
    for i, v in enumerate(p90s):
        ax.text(i, v + max(p90s)*0.02, f"{v:.0f}d", ha="center", fontsize=9, color=TEXT)
    save(fig, "district_p90_2025.png")

print("done")
