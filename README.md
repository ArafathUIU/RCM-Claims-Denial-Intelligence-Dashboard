# RCM Claims Denial Intelligence Dashboard

A healthcare revenue cycle analytics portfolio project built with **Python, SQL, and Excel** that generates synthetic claims data, runs analytical queries, and visualizes denial trends in both a formatted Excel workbook and an interactive Streamlit dashboard.

---

## Quickstart

```bash
uv venv
uv pip install -r requirements.txt
python data/generate_data.py          # Generate 20,000 synthetic claims
python excel/build_dashboard.py       # Build formatted Excel workbook
streamlit run dashboard/app.py        # Launch interactive web dashboard
```

---

## Architecture

```
synthetic data ──► CSV ──► pandas ──► Excel workbook (6 sheets, charts)
 (Faker)           │         │
                   │         └───────► Streamlit app (5 pages, interactive)
                   │
                   └──────────► SQL queries (6 .sql files for SQLite)
```

**Output files (git-ignored):**
| File | Content |
|------|---------|
| `data/claims_data.csv` | 20,000 claims, 17 columns, ~7 MB |
| `excel/RCM_Denial_Dashboard.xlsx` | 6-sheet workbook with charts, ~30 KB |

---

## Data Model

### `claims` (fact table)
20,000 records spanning Jan 2024 – Dec 2025 with realistic distributions:
- 12 insurance payers (UnitedHealth, Aetna, BCBS, Cigna, Humana, Medicare, Medicaid, Tricare, Kaiser, Centene, Molina, Anthem)
- 50 providers across 12 clinical departments
- 14 denial reason codes (CO-16, CO-50, CO-97, CO-109, etc.)
- Realistic denial rates (~13-15%), appeal rates (~35%), and recovery rates (~17-20%)

### Claim Lifecycle
```
Billed → Allowed → [Paid]
                  → [Denied] → [Appealed] → [Recovered]
                                           → [Written Off]
```

### Key Metrics Tracked
| Metric | Description |
|--------|-------------|
| Denial Rate | `denied_claims / total_claims` |
| Recovery Rate | `recovered_amount / denied_amount` |
| Appeal Rate | `appealed_claims / denied_claims` |
| Appeal Success Rate | `recovered_claims / appealed_claims` |
| Aging Days | `days from billing_date to resolution` |

---

## Project Structure

```
├── data/
│   └── generate_data.py              # Synthetic RCM claims generator
├── sql/
│   ├── schema.sql                    # Tables, indexes, views (SQLite)
│   ├── 01_denial_trends.sql          # Monthly/quarterly/YoY denial trends
│   ├── 02_payer_performance.sql      # Payer denial rates, recovery, appeals
│   ├── 03_denial_reasons.sql         # Reason frequency, Pareto, categories
│   ├── 04_revenue_recovery.sql       # Appeal funnel, recovery time, monthly trends
│   ├── 05_provider_drilldown.sql     # Provider/department denials, top 10
│   └── 06_aging_ar.sql              # Aging buckets, AR by payer & department
├── excel/
│   └── build_dashboard.py            # OpenPyXL dashboard generator
├── dashboard/
│   ├── app.py                        # Streamlit entry point + sidebar
│   ├── data_loader.py                # Shared cached data loader
│   └── pages/
│       ├── overview.py               # KPI cards, filters, monthly trends
│       ├── payer_analysis.py          # Payer comparison, appeal metrics
│       ├── denial_reasons.py          # Treemap, Pareto, per-payer breakdown
│       ├── revenue_recovery.py        # Funnel, waterfall, recovery timeline
│       └── provider_aging.py          # Provider rates, aging buckets
├── .streamlit/
│   └── config.toml                   # Corporate blue theme
├── requirements.txt
└── README.md
```

---

## Analysis Dimensions

### 1. Denial Trends Over Time (`01_denial_trends.sql`)
Monthly denial counts, denial rate percentages, denied/recovered dollar amounts, quarterly rollups, and year-over-year month comparisons.

### 2. Payer Performance (`02_payer_performance.sql`)
Per-payer denial rates vs dollar amounts, recovery rates, appeal filing and success rates, and payer-type-level aggregation (Commercial/Government/Managed Care).

### 3. Denial Reasons (`03_denial_reasons.sql`)
Frequency and financial impact of 14 denial codes, Pareto analysis with cumulative percentages, category-level grouping (Coding, Authorization, Medical Necessity), and top denial reasons per payer.

### 4. Revenue Recovery (`04_revenue_recovery.sql`)
Appeal counts and success rates, recovered vs written-off dollars, average days to recover (by amount bucket), recovery rates by denial reason, and monthly recovery trends.

### 5. Provider Drill-down (`05_provider_drilldown.sql`)
Denial counts, rates, and dollar amounts by provider and department. Top 10 worst-performing providers and a provider-payer denial rate matrix.

### 6. Aging & AR (`06_aging_ar.sql`)
Aging bucket distribution (0-30, 31-60, 61-90, 90+ days) with dollar amounts, average aging days by payer and department, and monthly aging trends.

---

## Excel Dashboard (6 Sheets)

| Sheet | Content |
|-------|---------|
| **Summary** | 8 KPI cards, monthly trend table, denial rate line chart |
| **Payer Performance** | Denial rate % and denied $ bar charts by payer |
| **Denial Reasons** | Bar + cumulative line Pareto chart |
| **Revenue Recovery** | Revenue flow bar chart, appeal metrics table |
| **Provider Drill-down** | Provider table with conditional formatting (red/green for high/low denial), department bar chart |
| **Aging & AR** | Bucket distribution charts, outstanding AR, payer aging table |

Built entirely with **OpenPyXL** — no Excel required to generate.

---

## Streamlit Dashboard (5 Pages)

| Page | Interactive Features |
|------|---------------------|
| **Overview** | 8 KPI metric cards, date range filter, payer type multiselect, denial rate line chart, denied/recovered bar charts |
| **Payer Analysis** | Payer multiselect, denial rate & amount bars, recovery/appeal grouped bars, payer-type summary cards |
| **Denial Reasons** | Top-10 bar chart, treemap, Pareto (dual-axis bar+line), per-payer reason breakdown |
| **Revenue Recovery** | 4 KPI metrics, appeal funnel, revenue waterfall, recovery-by-reason bar, recovery timeline histogram, monthly recovery trend |
| **Provider & Aging** | Department dropdown filter, provider denial rate bars, department horizontal chart, heatmap. AR aging: bucket bars + pie, aging by payer & department |

All charts built with **Plotly** — hover, zoom, and download enabled.

---

## How to Run

### Prerequisites
- Python 3.10+
- `uv` package manager (recommended) or `pip`

### Step-by-step

```bash
# 1. Create environment and install dependencies
uv venv
uv pip install -r requirements.txt

# 2. Generate synthetic claims data (20,000 records)
.venv\Scripts\python data\generate_data.py

# 3. Build the Excel dashboard
.venv\Scripts\python excel\build_dashboard.py

# 4. Launch the Streamlit web dashboard
.venv\Scripts\streamlit run dashboard\app.py
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `faker` | >=22.0 | Synthetic data generation |
| `pandas` | >=2.0 | Data manipulation & analysis |
| `numpy` | >=1.26 | Numerical operations |
| `openpyxl` | >=3.1 | Excel workbook generation |
| `streamlit` | >=1.30 | Web dashboard framework |
| `plotly` | >=5.15 | Interactive charting |

---

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Data Generation & Database Setup | Complete |
| 2 | SQL Analysis Queries (6 dimensions) | Complete |
| 3 | Excel Dashboard (6 sheets) | Complete |
| 4 | Streamlit Web Dashboard (5 pages) | Complete |
| 5 | Documentation & Polish | Complete |
| 6 (bonus) | Streamlit Theme & Config | Complete |
