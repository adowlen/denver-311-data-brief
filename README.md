# The 311 Report Card

A data brief on Denver's 311 system: 1,381,852 cases from 2023-2025, what residents actually call about, how fast the city answers by council district, and the data trap hiding in the encampment numbers.

**Headline:** 84% of 311 cases close the same day — the system is mostly the city's front desk, not its dispatch radio. But among field-work cases, the median wait in District 6 (1.76 days) is more than triple District 11 (0.49 days). And "encampment reports" didn't collapse in late 2025 — the city renamed the category and the cases migrated with it.

Read the full brief: [brief/denver-311-brief.md](brief/denver-311-brief.md)

## Contents

- `brief/` - the narrative brief with findings, charts, methods, and caveats
- `charts/` - 5 charts (PNG) + hero graphic (WebP)
- `data/` - aggregated statistics (`stats.json`): yearly totals, top case summaries, resolution-time distributions, district medians
- `code/` - download scripts and analysis (`download_2023.py`, `resume2_2023.py`, `analyze.py`, `charts.py`)

## Data sources

All public, City and County of Denver via ArcGIS Hub (opendata-geospatialdenver.hub.arcgis.com):

- 311 Service Requests 2023 — feature service, 474,695 records
- 311 Service Requests 2024 — CSV, 455,214 rows
- 311 Service Requests 2025 — CSV, 451,943 rows
- Denver Auditor, "Denver 311 and Select Agency Case Management," August 2025

## Reproduce

1. Download the three yearly files from Denver's ArcGIS Hub (see Data sources)
2. Run `python code/download_2023.py` for the 2023 feature service (paged; `resume2_2023.py` resumes interrupted runs), or place the CSVs in `data/`
3. Run `python code/analyze.py [years]` — writes `stats.json`
4. Run `python code/charts.py` — charts land in `charts/`

Requires Python 3 with matplotlib.

## Caveats (short version)

The published Topic/Type/Neighborhood fields are blank in all three files — topics come from free-text Case Summary. Council-district coding is complete in 2023 but sparse in 2024/2025, so cross-year district comparisons are unreliable. "911 NECT KEEP" appears from ~April 2024; "Encampment / Street Engagement" splits off "Encampment Reporting" in September 2025. Full caveats in the brief.

## Methods and data

The analysis uses the public datasets listed under Data sources. The scripts in [code/](code/) download and analyze the yearly files, write the aggregate statistics in [data/stats.json](data/stats.json), and generate the charts. Coding limits and the full caveat set are documented in the [full brief](brief/denver-311-brief.md) and in Caveats (short version) above.

## Part of Machine Readable

This brief is part of [Machine Readable](https://adowlen.github.io/machine-readable/), the catalog of all Machine Readable briefs.


## Reuse and citation

This brief is free to cite, quote, and reuse under the CC BY 4.0 license (see LICENSE). If you use it, please credit Machine Readable and link back to this repository.

Attribution line: Machine Readable (Alex Dowlen), https://github.com/adowlen/denver-311-data-brief
