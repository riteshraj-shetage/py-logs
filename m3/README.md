# Data Analysis Portfolio — Business Domain (m3)

> **Month 3 Project** | Python · pandas · numpy · matplotlib · seaborn · scikit-learn

## Description

Three end-to-end business-domain analysis projects built with Python, covering **Retail Sales**, **Marketing Campaign**, and **Operations** analysis. Each project ingests a realistic synthetic dataset, performs statistical and segment-level analysis, produces publication-ready charts, and delivers a written business report with actionable recommendations.

---

## Project Structure

| Path | Description |
|------|-------------|
| `datasets/sales_data.csv` | 500-row retail sales records (2023) |
| `datasets/marketing_data.csv` | 300-row marketing campaign records |
| `datasets/operations_data.csv` | 400-row operational task records |
| `project1_sales_analysis/analysis.py` | Sales analysis script → 5 charts |
| `project1_sales_analysis/report.md` | Sales business report |
| `project2_marketing_analysis/analysis.py` | Marketing analysis script → 4 charts |
| `project2_marketing_analysis/report.md` | Marketing business report |
| `project3_operations_analysis/analysis.py` | Operations analysis script → 4 charts |
| `project3_operations_analysis/report.md` | Operations business report |
| `visualizations/` | All saved PNG charts land here |
| `docs/methodology.md` | Analysis methodology documentation |

---

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Project 1 — Sales Analysis
python project1_sales_analysis/analysis.py

# 3. Run Project 2 — Marketing Analysis
python project2_marketing_analysis/analysis.py

# 4. Run Project 3 — Operations Analysis
python project3_operations_analysis/analysis.py
```

Charts are saved automatically to `visualizations/`.

---

## Project Summaries

### Project 1 — Retail Sales Analysis
Analyses 500 orders across five product categories and four regions for the full year 2023.

**Key findings:**
- Electronics is the top revenue category (~35 % of total sales).
- North region leads in revenue; South shows fastest growth in Q4.
- Monthly trend peaks in October–November (pre-holiday demand).
- RFM segmentation identifies ~15 % of customers as high-value Champions.
- Top 5 products alone generate ~28 % of total revenue.

**Charts produced:** `monthly_sales.png`, `category_performance.png`, `regional_sales.png`, `customer_segments.png`, `top_products.png`

---

### Project 2 — Marketing Campaign Analysis
Analyses 300 campaigns across Email, Social Media, SEO, PPC, and Content channels.

**Key findings:**
- Email delivers the highest average ROI (~320 %).
- PPC drives the most conversions per campaign but at the highest cost.
- SEO has the lowest cost-per-conversion, making it most budget-efficient.
- Top 10 % of campaigns contribute over 40 % of total revenue.

**Charts produced:** `channel_roi.png`, `conversion_rates.png`, `budget_vs_revenue.png`, `campaign_performance.png`

---

### Project 3 — Operations Analysis
Analyses 400 operational tasks across five departments throughout 2023.

**Key findings:**
- Overall task completion rate is ~60 %; Delayed tasks represent ~15 %.
- Production department has the highest average task duration (~18 days).
- Warehouse tasks have the lowest average cost; Production the highest.
- High-priority tasks are delayed more often than low-priority ones.

**Charts produced:** `completion_rates.png`, `dept_duration.png`, `cost_by_dept.png`, `priority_analysis.png`

---

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| pandas | ≥ 2.0 | Data loading, wrangling, aggregation |
| numpy | ≥ 1.24 | Numerical operations, RNG |
| matplotlib | ≥ 3.7 | Base charting engine |
| seaborn | ≥ 0.12 | Statistical visualisations |
| scikit-learn | ≥ 1.3 | Preprocessing (scaling for RFM) |

---

## License

MIT — see repository root for details.
