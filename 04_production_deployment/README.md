# Phase 4 — Production Deployment

> FastAPI service serving the trained models, packaged with Docker, monitored with Prometheus and Grafana, tracked with MLflow.

## What's In This Folder

```
04_production_deployment/
├── README.md                     ← This file
├── api/                          FastAPI application
│   ├── main.py                   Application entry point
│   ├── schemas.py                Pydantic request/response models
│   ├── dependencies.py           Model loading, DB connection
│   └── routes/
│       ├── segment.py            /predict/segment endpoint
│       └── forecast.py           /predict/forecast endpoint
├── docker/
│   ├── Dockerfile.api            Multi-stage build for the API
│   └── docker-compose.yml        Full stack: Postgres + API + monitoring
├── monitoring/
│   ├── prometheus.yml            Prometheus scrape config
│   └── grafana/dashboards/       Pre-built Grafana dashboard JSONs
├── tests/
│   └── test_api.py               API integration tests
└── docs/
    ├── API_REFERENCE.md          Endpoint specifications
    ├── DEPLOYMENT.md             How to run locally
    └── MONITORING.md             Prometheus metrics + Grafana dashboards
```

## What This Phase Delivers

### FastAPI Service

Two prediction endpoints:

| Endpoint | Purpose |
|---|---|
| `POST /predict/segment` | Given a customer_key, return assigned segment + confidence |
| `POST /predict/forecast` | Given product_line + country + horizon, return forecasted units/revenue |

Plus operational endpoints:
- `GET /health` — health check
- `GET /metrics` — Prometheus metrics
- `GET /docs` — interactive Swagger UI

### Docker Stack

`docker-compose up` brings up:

| Service | Purpose | Port |
|---|---|---|
| `postgres` | The data warehouse | 5432 |
| `api` | FastAPI prediction service | 8000 |
| `prometheus` | Metrics collection | 9090 |
| `grafana` | Metrics visualization | 3000 |
| `mlflow` | Experiment tracking + model registry | 5000 |

### Monitoring

Prometheus collects:
- HTTP request count, latency, error rate per endpoint
- Model inference latency
- Data drift indicators (feature distribution checks against training data)

Grafana dashboards visualize the above with alert thresholds.

### CI/CD

GitHub Actions workflow ([`.github/workflows/ci_python.yml`](../.github/workflows/ci_python.yml)):
- Lint with ruff
- Format check with black
- Run pytest with coverage
- Build Docker image on push to main

## Quick Start

```bash
cd 04_production_deployment
docker compose -f docker/docker-compose.yml up --build
```

Then:
- API docs: http://localhost:8000/docs
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- MLflow: http://localhost:5000

### Example API Calls

```bash
# Segment a customer
curl -X POST http://localhost:8000/predict/segment \
  -H "Content-Type: application/json" \
  -d '{"customer_key": 12345}'

# Forecast revenue
curl -X POST http://localhost:8000/predict/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "product_line": "Road",
    "country": "United States",
    "horizon_months": 6
  }'
```

See [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) for full request/response schemas.

## Tech Stack

FastAPI · Pydantic · uvicorn · Docker · docker-compose · Prometheus · Grafana · MLflow

## Key Design Decisions

### Why FastAPI (Not Flask or Django)
FastAPI provides:
- Automatic OpenAPI/Swagger documentation
- Pydantic-based request validation
- Async support out of the box
- Better performance than Flask for the same code complexity

### Why Multi-Stage Docker Build
A multi-stage Dockerfile separates build dependencies (compilers, dev libs) from runtime, reducing final image size. The runtime image only contains Python + the wheel install + the trained model artifacts.

### Why Prometheus + Grafana (Not Just Logs)
- Prometheus pull-based scraping scales better than push-based logging.
- Grafana dashboards provide visual SLO tracking.
- Together they enable alerting (latency > threshold → notification).

### Why MLflow
Demonstrates the full ML lifecycle: experiment tracking during development, model registry for versioning, and serving the registered model from the API.

## What's Next

This is the final phase. The four phases together form a complete analytics platform: data engineering → BI → ML → production deployment.

See [`../README.md`](../README.md) for the overall project context.
