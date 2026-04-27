# Data Analysis Methodology

## Overview

All three projects in this portfolio follow the same structured analysis pipeline: **Data Acquisition → Cleaning → Exploration → Analysis → Visualisation → Reporting**. This document explains each phase, the tools used, and guidance on interpreting results.

---

## Analysis Pipeline

### 1. Data Acquisition

Synthetic datasets are generated with Python's `numpy.random` module using a fixed seed (`seed=42`) to ensure full reproducibility. Each CSV is written to `datasets/` and read by the corresponding analysis script via `os.path` relative to `__file__`, so scripts can be executed from any working directory.

### 2. Data Cleaning & Validation

- **Date parsing** — `pandas.read_csv(..., parse_dates=[...])` converts date columns to `datetime64` at load time.
- **Missing value handling** — derived metrics (e.g., conversion rate, cost-per-conversion) use `.replace(0, np.nan)` before division to avoid `ZeroDivisionError` and correctly produce `NaN` rather than `inf`.
- **Type coercion** — monetary and count columns are cast to `float64` / `int64` as appropriate.

### 3. Exploratory Data Analysis (EDA)

Each script prints descriptive statistics (`df.describe()` equivalent logic) as part of its summary output. Key distributions (revenue, duration, budget) are visually inspected via bar and scatter charts before deeper analysis.

### 4. Statistical Analysis Techniques

| Technique | Used in | Purpose |
|-----------|---------|---------|
| Group aggregation (`groupby` + `agg`) | All projects | Compute totals, means, counts by categorical dimension |
| Time-series resampling (`resample("ME")`) | Project 1 | Monthly revenue trend |
| Quantile binning (`pd.qcut`) | Project 1 | Customer value segmentation |
| RFM scoring | Project 1 | Multi-dimensional customer health metric |
| Normalisation (`MinMaxScaler`) | Project 1 | Scale RFM components to [0, 1] for compositing |
| Ratio metrics (ROI, CTR, ConvRate) | Project 2 | Derive efficiency KPIs from raw counts |
| Cross-tabulation (pivot via `unstack`) | Project 3 | Priority × Status matrix |

### 5. Visualisation

All charts are produced with **Matplotlib** (backend: `Agg`, suitable for headless/server environments) and **Seaborn** for statistical styling. Each figure is saved with `plt.savefig(path, dpi=150)` followed immediately by `plt.close()` to release memory and prevent figure bleed between plots.

**Colour palettes used:**
- `Blues_d` / `Greens_d` / `Oranges_d` — sequential, for ordered continuous data
- `viridis` / `coolwarm` — diverging / perceptually uniform, for comparative data
- `Set2` / `tab10` — qualitative, for categorical groupings

### 6. Reporting

Each project produces a `report.md` file with:
- Executive Summary (plain-language narrative)
- Key Findings (bullet points with illustrative numbers)
- Methodology (what was done and how)
- Business Recommendations (5 actionable items)
- Visualizations reference table

---

## How to Interpret Results

### Sales Analysis
- **Monthly trend** — look for seasonality (peaks, troughs) and year-over-year comparison opportunities.
- **Category performance** — pie chart share vs. bar chart absolute value together reveal both relative importance and absolute scale.
- **RFM segments** — Champion customers warrant retention investment; At Risk customers warrant win-back campaigns.

### Marketing Analysis
- **ROI** — a positive ROI means the channel returns more revenue than it costs; >100 % is excellent.
- **Conversion Rate** — measures funnel efficiency; a low conversion rate with high clicks indicates a landing-page or audience mismatch.
- **Budget vs. Revenue scatter** — points in the top-left quadrant (low budget, high revenue) are the most efficient campaigns to scale.

### Operations Analysis
- **Completion Rate** — below 70 % indicates capacity or process constraints worth investigating.
- **Average Duration** — high duration alone isn't negative; context matters (Production tasks are inherently longer). Compare against benchmarks.
- **Priority × Status** — if High-priority tasks have a higher delay rate than Low-priority, escalation protocols need review.

---

## Reproducibility

All datasets are generated with `numpy.random.seed(42)`. Re-running `datasets/generate_datasets.py` will always produce identical CSVs. Analysis scripts include a self-contained fallback generator so they can be run even without the pre-generated CSVs.

---

## Tools & Versions

| Tool | Version Requirement | Role |
|------|---------------------|------|
| Python | ≥ 3.9 | Runtime |
| pandas | ≥ 2.0 | Data wrangling |
| numpy | ≥ 1.24 | Numerical computation, RNG |
| matplotlib | ≥ 3.7 | Base charting |
| seaborn | ≥ 0.12 | Statistical visualisation |
| scikit-learn | ≥ 1.3 | Feature scaling (MinMaxScaler) |

---

*See `README.md` at the project root for quick-start instructions.*
