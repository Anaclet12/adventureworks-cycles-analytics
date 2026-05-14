"""
Integration tests for the AdventureWorks Analytics API.

Run with:  pytest tests/ -v

These tests use FastAPI's TestClient, which exercises the full
application stack (routing, validation, auth, model inference) without
needing a running server.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.config import settings


VALID_KEY = settings.api_key
HEADERS = {"X-API-Key": VALID_KEY}


@pytest.fixture(scope="module")
def client():
    """TestClient as a context manager so the lifespan startup hook runs.

    Without the `with` block, FastAPI does not execute the lifespan
    context, so models and data are never loaded and every prediction
    endpoint returns 503.
    """
    with TestClient(app) as test_client:
        yield test_client


# ----------------------------------------------------------------------------
# Meta endpoints (no auth)
# ----------------------------------------------------------------------------
def test_root_returns_metadata(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["service"] == settings.app_name
    assert "endpoints" in body


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in {"healthy", "degraded", "unhealthy"}
    assert "models_loaded" in body
    assert "data_loaded" in body


def test_metrics_endpoint_exposed(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    # Prometheus exposition format
    assert "python_gc_objects_collected_total" in resp.text


# ----------------------------------------------------------------------------
# Auth
# ----------------------------------------------------------------------------
def test_segment_without_key_rejected(client):
    resp = client.post("/predict/segment", json={"customer_key": 1})
    assert resp.status_code == 401


def test_segment_with_wrong_key_rejected(client):
    resp = client.post(
        "/predict/segment",
        json={"customer_key": 1},
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code == 401


def test_forecast_without_key_rejected(client):
    resp = client.post(
        "/predict/forecast",
        json={"product_line": "Road", "country": "Australia"},
    )
    assert resp.status_code == 401


# ----------------------------------------------------------------------------
# /predict/segment
# ----------------------------------------------------------------------------
def test_segment_valid_customer(client):
    resp = client.post("/predict/segment", json={"customer_key": 1}, headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["customer_key"] == 1
    assert body["kmeans_cluster"] in {0, 1, 2, 3}
    assert isinstance(body["kmeans_name"], str)
    assert body["monetary_usd"] > 0
    assert body["source"] in {"live", "cached"}


def test_segment_nonexistent_customer(client):
    resp = client.post(
        "/predict/segment", json={"customer_key": 999999}, headers=HEADERS
    )
    assert resp.status_code == 404


def test_segment_invalid_customer_key_zero(client):
    # customer_key must be > 0 per the schema
    resp = client.post("/predict/segment", json={"customer_key": 0}, headers=HEADERS)
    assert resp.status_code == 422


def test_segment_missing_customer_key(client):
    resp = client.post("/predict/segment", json={}, headers=HEADERS)
    assert resp.status_code == 422


# ----------------------------------------------------------------------------
# /predict/forecast
# ----------------------------------------------------------------------------
def test_forecast_valid_combination(client):
    resp = client.post(
        "/predict/forecast",
        json={"product_line": "Road", "country": "Australia", "horizon_months": 6},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["product_line"] == "Road"
    assert body["country"] == "Australia"
    assert body["model"] == "Prophet"
    assert len(body["forecasts"]) == 6
    # Each forecast point has the confidence interval ordered correctly
    for point in body["forecasts"]:
        assert point["lower"] <= point["forecast"] <= point["upper"]


def test_forecast_respects_horizon(client):
    resp = client.post(
        "/predict/forecast",
        json={"product_line": "Road", "country": "Australia", "horizon_months": 3},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert len(resp.json()["forecasts"]) == 3


def test_forecast_unmodellable_combination(client):
    # Touring x France had < 18 months of history — no forecast exists
    resp = client.post(
        "/predict/forecast",
        json={"product_line": "Touring", "country": "France", "horizon_months": 6},
        headers=HEADERS,
    )
    assert resp.status_code == 404


def test_forecast_invalid_product_line(client):
    resp = client.post(
        "/predict/forecast",
        json={"product_line": "Spaceship", "country": "France"},
        headers=HEADERS,
    )
    assert resp.status_code == 422


def test_forecast_invalid_country(client):
    resp = client.post(
        "/predict/forecast",
        json={"product_line": "Road", "country": "Atlantis"},
        headers=HEADERS,
    )
    assert resp.status_code == 422


def test_forecast_horizon_out_of_range(client):
    # horizon_months must be 1-6
    resp = client.post(
        "/predict/forecast",
        json={"product_line": "Road", "country": "Australia", "horizon_months": 99},
        headers=HEADERS,
    )
    assert resp.status_code == 422
