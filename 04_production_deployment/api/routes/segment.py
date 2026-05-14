"""
/predict/segment endpoint.

Given a customer_key, compute R, F, M from fact_sales (live), apply the
trained K-Means model, and return both the rules-based RFM segment
(if cached) and the K-Means cluster assignment.
"""

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_503_SERVICE_UNAVAILABLE

from ..auth import require_api_key
from ..dependencies import store
from ..schemas import SegmentRequest, SegmentResponse

router = APIRouter(prefix="/predict", tags=["predictions"])


@router.post(
    "/segment",
    response_model=SegmentResponse,
    summary="Compute the customer's segment from live R/F/M features",
)
async def predict_segment(
    request: SegmentRequest,
    _: str = Depends(require_api_key),
) -> SegmentResponse:
    """Compute the customer's segment.

    The K-Means cluster is computed live from `fact_sales` (so it works
    for any customer in the warehouse). The Power BI RFM segment is
    looked up from cache if available.
    """
    if not store.models_loaded:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="K-Means model not loaded",
        )

    # Live RFM computation from fact_sales
    rfm = store.compute_rfm_live(request.customer_key)
    if rfm is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"customer_key {request.customer_key} not found",
        )

    # Apply K-Means
    cluster, name = store.predict_cluster(
        rfm["recency"], rfm["frequency"], rfm["monetary"]
    )

    # Look up the cached Power BI segment (None for customers not in training set)
    cached_segment = store.get_cached_rfm_segment(request.customer_key)
    # If the customer was in the cache, mark the source as cached for that
    # part of the response; otherwise the result is fully live.
    source = "cached" if cached_segment is not None else "live"

    return SegmentResponse(
        customer_key=request.customer_key,
        rfm_segment=cached_segment,
        kmeans_cluster=cluster,
        kmeans_name=name,
        recency_days=rfm["recency"],
        frequency=rfm["frequency"],
        monetary_usd=rfm["monetary"],
        source=source,
    )
