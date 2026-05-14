# Phase 4 — Production Deployment

> Wraps the Phase 3 machine learning models in a production-grade FastAPI service, with API key authentication, Prometheus metrics, and an integration test suite. This is the layer that turns notebooks into software other applications can call.

## What's In This Folder

```
04_production_deployment/
├── README.md                       ← This file
├── requirements-api.txt            Pinned dependencies for the service
├── .env.example                    Environment configuration template
├── api/
│   ├── __init__.py
│   ├── config.py                   Pydantic settings (env-driven)
│   ├── schemas.py                  Request/response models
│   ├── auth.py                     API key authentication
│   ├── dependencies.py             Model loading + inference logic
│   ├── main.py                     FastAPI app, routes, lifecycle
│   └── routes/
│       ├── __init__.py
│       ├── segment.py              POST /predict/segment
│       └── forecast.py             POST /predict/forecast
├── tests/
│   ├── __init__.py
│   └── test_api.py                 16 integration tests
├── models/                         Trained artifacts (copied from Phase 3)
│   └── kmeans_segmentation.joblib
└── data/
    ├── processed/fact_sales.csv     For live RFM computation
    └── predictions/
        ├── forecasts.csv            Prophet forecasts
        └── segments.csv             Cached RFM segments
```

## The Service

A FastAPI application exposing the Phase 3 models as HTTP endpoints.

### Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/` | No | Service metadata |
| `GET` | `/health` | No | Health check (used by Docker healthcheck) |
| `GET` | `/metrics` | No | Prometheus metrics |
| `GET` | `/docs` | No | Interactive OpenAPI documentation |
| `POST` | `/predict/segment` | **Yes** | Live customer segmentation |
| `POST` | `/predict/forecast` | **Yes** | Revenue forecast by product line × country |

### `POST /predict/segment`

Computes a customer's segment. The K-Means cluster is computed **live** from `fact_sales` — recency, frequency, and monetary are recalculated, then the trained K-Means model is applied. The rules-based Power BI RFM segment is looked up from cache when available.

**Request:**
```json
{ "customer_key": 2 }
```

**Response:**
```json
{
  "customer_key": 2,
  "rfm_segment": "Whales",
  "kmeans_cluster": 1,
  "kmeans_name": "K-Whales (active, high-value)",
  "recency_days": 49.0,
  "frequency": 11,
  "monetary_usd": 6384.0,
  "source": "cached"
}
```

### `POST /predict/forecast`

Returns the Prophet forecast for a product line × country combination. Forecasts were precomputed in Phase 3 notebook 03 for the 12 combinations with sufficient training history.

**Request:**
```json
{ "product_line": "Road", "country": "Australia", "horizon_months": 6 }
```

**Response:**
```json
{
  "product_line": "Road",
  "country": "Australia",
  "horizon_months": 6,
  "model": "Prophet",
  "forecasts": [
    { "month": "2014-01-01", "forecast": 124380.3, "lower": 77842.1, "upper": 169335.1 }
  ]
}
```

Combinations without a trained model (e.g. `Touring × France`, which had < 18 months of history) return `404` with an explanatory message.

## Running Locally

### 1. Install dependencies

```bash
cd 04_production_deployment
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements-api.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — at minimum, change API_KEY for any non-local use
```

### 3. Start the server

```bash
uvicorn api.main:app --reload
```

The service starts on `http://127.0.0.1:8000`. Visit `http://127.0.0.1:8000/docs` for the interactive API documentation.

### 4. Make a request

```bash
curl -X POST http://127.0.0.1:8000/predict/segment \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-in-production" \
  -d '{"customer_key": 2}'
```

## Running the Tests

```bash
pytest tests/ -v
```

16 integration tests cover: metadata endpoints, authentication (missing key, wrong key), live segmentation (valid customer, nonexistent customer, validation errors), and forecasting (valid combination, horizon limits, unmodellable combinations, input validation).

The tests use FastAPI's `TestClient` as a context manager, which triggers the application lifespan — so models are loaded exactly as they would be in production.

## Design Decisions

### Live segmentation, not cached lookup
The `/predict/segment` endpoint recomputes RFM features from `fact_sales` rather than serving a precomputed lookup. This demonstrates the full inference pipeline — feature engineering, scaling, model application — and means the endpoint works for any customer in the warehouse, not just those present at training time.

### API key authentication
Prediction endpoints require an `X-API-Key` header. Health and metrics endpoints deliberately skip auth — health is needed by orchestration tooling (Docker, Kubernetes) before any key would be provisioned, and metrics are scraped by Prometheus.

### Models loaded once at startup
The FastAPI lifespan context loads all artifacts (K-Means model, scaler, forecast table, segment cache, `fact_sales`) into memory once. Per-request latency is dominated by dataframe filtering and model inference, not disk I/O.

### Pydantic validation everywhere
Request bodies are validated against typed schemas. `product_line` and `country` use `Literal` types, so invalid values are rejected with a `422` before any handler code runs. This shifts error handling to the framework boundary.

### Configuration via environment
All settings (`API_KEY`, `LOG_LEVEL`, paths, reference date) come from environment variables via `pydantic-settings`, with sensible local-development defaults. Nothing environment-specific is hard-coded.

## Tech Stack

FastAPI · Uvicorn · Pydantic v2 · scikit-learn · pandas · Prometheus · pytest

## Status

- ✅ **4.1 — FastAPI service** (this document) — endpoints, auth, tests
- ⬜ **4.2 — Docker** — multi-stage Dockerfile, docker-compose stack
- ⬜ **4.3 — Monitoring + CI/CD** — Prometheus config, Grafana dashboards, GitHub Actions

## What's Next

Phase 4.2 containerizes this service with a multi-stage Dockerfile and a `docker-compose.yml` that brings up the API alongside PostgreSQL, Prometheus, and Grafana. Phase 4.3 adds the monitoring dashboards and a GitHub Actions CI/CD pipeline.

See the [top-level README](../README.md) for overall project context.
