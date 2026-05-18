# RCM Claims Denial Intelligence Dashboard

A healthcare analytics portfolio project tracking insurance claim denial trends, payer performance,
and revenue recovery insights using SQL, Python, and Excel.

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Data Generation | Python + Faker |
| Database | SQLite |
| Analysis | SQL |
| Excel Dashboard | Python + OpenPyXL |
| Web Dashboard | Streamlit + Plotly |

---

## Project Structure

```
├── data/
│   ├── generate_data.py        # Synthetic data generation
│   └── claims_data.csv         # Generated output (gitignored)
├── sql/
│   ├── schema.sql              # Table definitions
│   ├── 01_denial_trends.sql    # Denial rate trends over time
│   ├── 02_payer_performance.sql# Denials by payer
│   ├── 03_denial_reasons.sql   # Top denial codes & reason frequency
│   ├── 04_revenue_recovery.sql # Appeals success & recovered amounts
│   ├── 05_provider_drilldown.sql# Denials by provider/department
│   └── 06_aging_ar.sql        # Aging buckets & days in A/R
├── excel/
│   └── build_dashboard.py      # Generates formatted .xlsx workbook
├── dashboard/
│   ├── app.py                  # Streamlit entry point
│   └── pages/
│       ├── overview.py
│       ├── payer_analysis.py
│       ├── denial_reasons.py
│       ├── revenue_recovery.py
│       └── provider_aging.py
├── requirements.txt
└── README.md
```

---

## Phase 1 — Data Generation & Database Setup

**Goal:** Generate realistic synthetic healthcare claims data and set up an SQLite database.

**Tasks:**
1. Create `data/generate_data.py` using Faker to produce ~10,000–50,000 claims
2. Fields: Claim ID, Patient ID, Provider, Department, Payer, Service/Billing/Denial/Recovery Dates,
   Billed/Allowed/Denied/Recovered Amounts, Denial Reason Code + Description,
   Claim Status, Appeal Flag, Appeal Days, Aging Days
3. Realistic distributions (e.g., Medicare denies more, CO-97 most common, etc.)
4. Create `sql/schema.sql` with normalized tables: `claims`, `payers`, `denial_reasons`, `providers`
5. Export generated data as `data/claims_data.csv`

**Deliverables:** `generate_data.py`, `schema.sql`, `claims_data.csv`

**Status:** Complete

**Sample Output (20,000 claims):**
| Metric | Value |
|--------|-------|
| Total claims | 20,000 |
| Denial rate | ~14.7% |
| Recovery rate | ~19% of denied |
| Total denied | ~$23.5M |
| Total recovered | ~$3.2M |

### How to Run

```bash
# Create virtual environment
uv venv
uv pip install -r requirements.txt

# Generate data
.venv\Scripts\python data\generate_data.py
```

---

## Phase 2 — SQL Analysis Queries

**Goal:** Write SQL queries addressing all 6 analysis dimensions.

**Tasks:**
1. `01_denial_trends.sql` — Monthly/quarterly denial counts, denial rate %, denied $ trends
2. `02_payer_performance.sql` — Denial rate, avg $ denied, and recovery rate by payer
3. `03_denial_reasons.sql` — Frequency and total $ amount by denial code, Pareto ranking
4. `04_revenue_recovery.sql` — Appeal success rate, recovered $ vs written-off $, avg days to recover
5. `05_provider_drilldown.sql` — Denial count & $ by provider and department
6. `06_aging_ar.sql` — Claims in aging buckets (0-30, 31-60, 61-90, 90+ days), avg days in A/R

**Deliverables:** 6 `.sql` files in `sql/`

---

## Phase 3 — Excel Dashboard

**Goal:** Generate a polished, formatted Excel workbook with charts and pivot tables.

**Tasks:**
1. Create `excel/build_dashboard.py` using OpenPyXL
2. Summary sheet — KPI cards, sparkline trends
3. Payer Performance sheet — bar chart, denial rate vs $ denied
4. Denial Reasons sheet — Pareto chart (bar + cumulative line)
5. Revenue Recovery sheet — waterfall chart (billed → denied → recovered → written off)
6. Provider Drill-down sheet — conditional-formatted table
7. Aging AR sheet — stacked bar or histogram for aging buckets

**Deliverables:** `build_dashboard.py` + generated `.xlsx` workbook

---

## Phase 4 — Streamlit Web Dashboard

**Goal:** Build an interactive multi-page web dashboard.

**Tasks:**
1. Create `dashboard/app.py` with Streamlit config, sidebar navigation
2. `pages/overview.py` — KPI cards (total claims, denial rate, $ denied, recovery %), date range filter
3. `pages/payer_analysis.py` — Payer dropdown, bar charts, payer comparison table
4. `pages/denial_reasons.py` — Top denial codes, treemap, reason details
5. `pages/revenue_recovery.py` — Appeal funnel, recovery timeline, $ waterfall
6. `pages/provider_aging.py` — Provider filter, aging distribution, department heatmap

**Deliverables:** Streamlit app files, `requirements.txt`

---

## Phase 5 — Polish & Documentation

**Goal:** Finalize README, add screenshots, ensure reproducibility.

**Tasks:**
1. Document how to run each component
2. Add sample screenshots of Excel dashboard and Streamlit app
3. Verify `requirements.txt` pins all dependencies
4. Clean up any unused code

**Deliverables:** Updated README, final commit
