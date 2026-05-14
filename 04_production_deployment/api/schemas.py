"""
Pydantic schemas for request validation and response shaping.

Every endpoint's input and output is defined here. FastAPI uses these
to generate the OpenAPI documentation automatically.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# /predict/segment
# ============================================================


class SegmentRequest(BaseModel):
    """Request body for /predict/segment."""

    customer_key: int = Field(
        ...,
        gt=0,
        description="Surrogate key of the customer in dim_customers",
        examples=[12345],
    )


class SegmentResponse(BaseModel):
    """Response body for /predict/segment."""

    model_config = ConfigDict(json_schema_extra={
        "examples": [{
            "customer_key": 12345,
            "rfm_segment": "Whales",
            "kmeans_cluster": 1,
            "kmeans_name": "K-Whales (active, high-value)",
            "recency_days": 49,
            "frequency": 6,
            "monetary_usd": 6384.0,
            "source": "live",
        }]
    })

    customer_key: int
    rfm_segment: str | None = Field(
        None,
        description="Rules-based RFM segment (Whales / Everyday / At Risk / New Passions)",
    )
    kmeans_cluster: int = Field(
        ...,
        description="K-Means cluster ID (0-3)",
    )
    kmeans_name: str = Field(
        ...,
        description="Human-readable name for the K-Means cluster",
    )
    recency_days: float = Field(
        ...,
        description="Days since the customer's last purchase (relative to reference date)",
    )
    frequency: int = Field(..., description="Customer's order-line count")
    monetary_usd: float = Field(..., description="Customer's lifetime spend in USD")
    source: Literal["live", "cached"] = Field(
        ...,
        description="Whether the result was computed live or retrieved from cache",
    )


# ============================================================
# /predict/forecast
# ============================================================


class ForecastRequest(BaseModel):
    """Request body for /predict/forecast."""

    model_config = ConfigDict(json_schema_extra={
        "examples": [{
            "product_line": "Road",
            "country": "Australia",
            "horizon_months": 6,
        }]
    })

    product_line: Literal["Road", "Mountain", "Touring", "Other Sales"] = Field(
        ...,
        description="One of the four product lines",
    )
    country: Literal[
        "Australia", "Canada", "France", "Germany", "United Kingdom", "United States"
    ] = Field(
        ...,
        description="One of the six countries with sales history",
    )
    horizon_months: int = Field(
        6,
        ge=1,
        le=6,
        description="How many months ahead to return (max 6 — limited by trained model)",
    )


class ForecastPoint(BaseModel):
    """A single month in the forecast."""

    month: date
    forecast: float = Field(..., description="Point forecast (revenue USD)")
    lower: float = Field(..., description="80% confidence interval lower bound")
    upper: float = Field(..., description="80% confidence interval upper bound")


class ForecastResponse(BaseModel):
    """Response body for /predict/forecast."""

    product_line: str
    country: str
    horizon_months: int
    model: str = Field(..., description="Forecasting model used (Prophet)")
    forecasts: list[ForecastPoint]


# ============================================================
# /health
# ============================================================


class HealthResponse(BaseModel):
    """Response body for /health."""

    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    models_loaded: bool
    data_loaded: bool
