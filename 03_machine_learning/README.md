# Phase 3 — Machine Learning & Deep Learning

> Customer segmentation, sales forecasting, and prescriptive recommendations built on the gold-layer star schema.

## What's In This Folder

```
03_machine_learning/
├── README.md                          ← This file
├── pyproject.toml
├── requirements.txt
├── notebooks/                         Exploratory and modeling notebooks
│   ├── 01_eda.ipynb                   Exploratory data analysis
│   ├── 02_segmentation.ipynb          RFM validation + K-Means
│   ├── 03_forecasting_baseline.ipynb  Naive + Prophet
│   ├── 04_forecasting_lstm.ipynb      PyTorch LSTM
│   └── 05_prescriptive.ipynb          Combine segments + forecast → recommendations
├── src/                               Importable Python modules
│   ├── __init__.py
│   ├── config.py                      Paths, hyperparameters
│   ├── etl.py                         Gold-layer rebuild in pandas
│   ├── data_loader.py                 Load gold tables
│   ├── features.py                    Feature engineering
│   ├── segmentation.py                Segmentation model class
│   ├── forecasting.py                 Forecasting model classes
│   └── prescriptive.py                Recommendation logic
├── models/                            Trained model artifacts (gitignored)
├── tests/                             pytest unit tests
├── data/
│   ├── processed/                     Feature-engineered datasets (gitignored)
│   └── predictions/                   Model outputs (gitignored)
└── docs/
    ├── SEGMENTATION.md
    ├── FORECASTING.md
    └── PRESCRIPTIVE.md
```

## What This Phase Delivers

### 1. Customer Segmentation
- **Two parallel approaches:** RFM business-rules segmentation (built in Power BI) and unsupervised K-Means clustering (built here).
- **Validation:** Silhouette score on the RFM segments + agreement metrics between the two approaches.
- **Output:** `data/predictions/segments.csv` — one row per customer with both segment labels.

See [`docs/SEGMENTATION.md`](docs/SEGMENTATION.md).

### 2. Sales Forecasting
- **Aggregation level:** monthly by product line × country.
- **Baselines:** naive, seasonal naive, Prophet.
- **Deep learning:** PyTorch LSTM with 2 hidden layers.
- **Evaluation:** walk-forward backtesting on the last 6 months; MAPE and RMSE.
- **Output:** `data/predictions/forecasts.csv` — forecasted units and revenue per product-line × country × month.

See [`docs/FORECASTING.md`](docs/FORECASTING.md).

### 3. Prescriptive Recommendations
- **Logic:** combine segment value with forecasted demand to produce action lists.
- **Outputs:**
  - Inventory recommendations by region (`predictions/inventory_recommendations.csv`)
  - Marketing spend allocation by segment (`predictions/marketing_allocations.csv`)
  - Maintenance outreach ranked list (`predictions/maintenance_outreach.csv`)

See [`docs/PRESCRIPTIVE.md`](docs/PRESCRIPTIVE.md).

## Quick Start

```bash
cd 03_machine_learning

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run notebooks in order
jupyter notebook notebooks/01_eda.ipynb
```

The notebooks expect the gold-layer CSVs (`fact_sales.csv`, `dim_customers.csv`, `dim_products.csv`) in `data/processed/`. To generate them from the bronze sources:

```bash
python -m src.etl
```

## Tech Stack

Python 3.11 · pandas · numpy · scikit-learn · Prophet · PyTorch · MLflow · joblib · matplotlib · seaborn

## Key Design Decisions

### Why Both RFM and K-Means
RFM segmentation is a business-rules approach (every customer gets quintile scores on Recency, Frequency, Monetary, then is bucketed by combination). K-Means is data-driven (the algorithm finds natural clusters). Running both serves two purposes:
1. **Validation:** if K-Means independently rediscovers the same groups, the RFM rules are statistically defensible.
2. **Discovery:** if K-Means finds a segment the RFM rules missed (e.g., high-frequency low-monetary "subscription buyers"), that's a finding worth acting on.

### Why Prophet AND LSTM
Prophet is the right choice for this dataset (50 months of monthly history, clear yearly seasonality). LSTM is included to demonstrate the technique and to provide an honest comparison.

> **Note:** On this data volume, Prophet typically wins or ties LSTM. The portfolio story here is: *"I implemented LSTM, ran a fair backtest, and reported that Prophet is the production model."* That's stronger than "LSTM beat Prophet by 0.3%."

### Why Walk-Forward Backtesting
Standard train/test splits don't work for time series — they cause data leakage. Walk-forward backtesting trains on rolling windows ending before each test period, producing an honest estimate of out-of-sample performance.

## What's Next

The model outputs land back as CSV files in `data/predictions/`, ready to be consumed by:
- Power BI (refresh the report to see forecasts and segments alongside actuals).
- Phase 4 (FastAPI service serving real-time predictions).

See [`../README.md`](../README.md) for the overall project context.
