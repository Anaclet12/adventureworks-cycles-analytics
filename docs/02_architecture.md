# Architecture

## High-Level Picture

```
                   Sources                Bronze              Silver              Gold
                  ─────────              ─────────           ─────────           ─────────
   CRM ─────►   raw CSV files  ──►   raw landing  ──►   cleansed     ──►   star schema
   ERP ─────►   raw CSV files  ──►   (as-is)            standardized      (dim + fact)
                                      full reload        deduplicated      materialized
                                                         type-fixed         + indexed
                                                                                  │
                                                                                  ▼
                                       ┌─────────────────────────────────────────┴────┐
                                       │                                              │
                              ┌────────▼──────────┐                          ┌────────▼──────────┐
                              │   Power BI        │                          │   Python ML/DL    │
                              │                   │                          │                   │
                              │ - Sales & Margin  │                          │ - Segmentation    │
                              │ - Customer Intel  │                          │ - Forecasting     │
                              │ - Operations      │                          │ - Prescriptive    │
                              └───────────────────┘                          └────────┬──────────┘
                                                                                      │
                                                                             ┌────────▼──────────┐
                                                                             │   FastAPI         │
                                                                             │   + Docker        │
                                                                             │   + Prometheus    │
                                                                             └───────────────────┘
```

## Phase 1 — Data Warehouse (PostgreSQL Medallion)

Three medallion layers plus two operational schemas, all in a single PostgreSQL database:

- **`bronze`** — raw ingestion, no transformations, preserves source artifacts.
- **`silver`** — cleansed, deduplicated, standardized, with referential integrity.
- **`gold`** — business-ready star schema (`dim_customers`, `dim_products`, `fact_sales`).
- **`meta`** — pipeline run history (`etl_log`), row-level audit trail (`audit_log`).
- **`quality`** — data quality rule violations (`violation_log`).

Three roles enforcing least-privilege access:
- `etl_user` — writes to bronze/silver/gold; the pipeline runs as this user.
- `analyst_user` — read-only on gold/quality/meta; Power BI connects as this user.
- `app_user` — read-only on gold; the FastAPI service uses this user.

See [`01_data_engineering/README.md`](../01_data_engineering/README.md) for the full walkthrough.

## Phase 2 — Business Intelligence (Power BI)

Three dashboards, each reading from the gold-layer star schema (consumed as CSV extracts for Tableau Public compatibility; live connection for Power BI Desktop):

| Dashboard | Primary stakeholder | What it answers |
|---|---|---|
| **Sales & Margin** | CFO, VP Merchandising | Margin by product line, region, time; pricing analysis |
| **Customer Intelligence** | CMO | Demographics, RFM segments, premium-bike buyer profile |
| **Operations & Fulfillment** | COO, Customer Service | Ship lag, seasonality, maintenance-eligible base |

The data model is a classic star schema:

```
                    [Date]
                       │
                       │ (Order Date — active)
                       │ (Ship Date — inactive)
                       │ (Due Date — inactive)
                       │
[dim_customers] ─── [fact_sales] ─── [dim_products]
   Customer Key       Product Key       Product Key
```

DAX measures live in a dedicated `_Measures` table. The full set of measures is documented in [`02_business_intelligence/docs/DAX_MEASURES.md`](../02_business_intelligence/docs/DAX_MEASURES.md).

## Phase 3 — Machine Learning (Python)

Three models built on the gold layer, designed to integrate with the BI work rather than replace it:

### Customer Segmentation
- **Input:** `dim_customers` + `fact_sales`
- **Features:** RFM (Recency, Frequency, Monetary)
- **Approaches:** Business-rule quintile scoring (also built in Power BI) + unsupervised K-Means
- **Output:** Segment label per customer, written to `data/predictions/segments.csv`
- **Why both approaches:** to validate that the rule-based BI segmentation is statistically coherent

### Sales Forecasting
- **Input:** `fact_sales` aggregated to monthly by product line × country
- **Baselines:** Naive forecast, seasonal naive, Prophet
- **Deep learning:** PyTorch LSTM
- **Evaluation:** Walk-forward backtesting on last 6 months; MAPE and RMSE
- **Output:** Forecasted units/revenue per product-line × country × month, written to `data/predictions/forecasts.csv`

### Prescriptive Recommendations
- **Input:** segments + forecasts
- **Logic:** Combine forecasted demand with segment value to produce three action lists
- **Outputs:**
  - Inventory recommendations by region (driven by forecast)
  - Marketing spend allocation by segment (segment value × forecast growth)
  - Maintenance outreach ranked list (segment × maintenance-eligible products)

See [`03_machine_learning/README.md`](../03_machine_learning/README.md) for methodology and evaluation.

## Phase 4 — Production Deployment

The ML models are wrapped in a FastAPI service with two endpoints:

| Endpoint | Purpose |
|---|---|
| `POST /predict/segment` | Given a customer_key, return the assigned segment |
| `POST /predict/forecast` | Given a product_line + country + horizon, return forecasted units/revenue |

The service is containerized via multi-stage Docker build. `docker-compose.yml` runs:
- PostgreSQL (the warehouse)
- The FastAPI service
- Prometheus (metrics collection)
- Grafana (metrics visualization)
- MLflow (experiment tracking + model registry)

CI/CD via GitHub Actions: lint, test, build image on push to main.

See [`04_production_deployment/README.md`](../04_production_deployment/README.md) for deployment details.
