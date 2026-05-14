"""
/predict/forecast endpoint.

Returns the precomputed Prophet forecast for the requested
product_line x country combination. Forecasts are stored in
forecasts.csv produced by notebook 03.
"""

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_503_SERVICE_UNAVAILABLE

from ..auth import require_api_key
from ..dependencies import store
from ..schemas import ForecastPoint, ForecastRequest, ForecastResponse

router = APIRouter(prefix="/predict", tags=["predictions"])


@router.post(
    "/forecast",
    response_model=ForecastResponse,
    summary="Retrieve the Prophet forecast for a product_line x country combination",
)
async def predict_forecast(
    request: ForecastRequest,
    _: str = Depends(require_api_key),
) -> ForecastResponse:
    """Return forecasted revenue for the next N months.

    Forecasts were precomputed by notebook 03 (Prophet) for combinations
    with at least 18 months of training history. Not every product_line x
    country combination has a forecast.
    """
    if not store.data_loaded or store.forecasts is None:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="Forecast data not loaded",
        )

    df = store.forecasts
    mask = (
        (df["product_line"] == request.product_line)
        & (df["country"] == request.country)
    )
    matching = df[mask].sort_values("month").head(request.horizon_months)

    if matching.empty:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=(
                f"No forecast available for {request.product_line} x {request.country}. "
                f"This combination either had insufficient training history "
                f"(< 18 months) or is not in the active dataset."
            ),
        )

    forecasts = [
        ForecastPoint(
            month=row["month"].date(),
            forecast=float(row["forecast"]),
            lower=float(row["yhat_lower"]),
            upper=float(row["yhat_upper"]),
        )
        for _, row in matching.iterrows()
    ]

    return ForecastResponse(
        product_line=request.product_line,
        country=request.country,
        horizon_months=len(forecasts),
        model="Prophet",
        forecasts=forecasts,
    )
