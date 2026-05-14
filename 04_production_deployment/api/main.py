"""
AdventureWorks Analytics API - main application.

Production-grade FastAPI service exposing the Phase 3 ML models:
- POST /predict/segment    - real-time customer segmentation
- POST /predict/forecast   - revenue forecasts by product line x country
- GET  /health             - service health check
- GET  /metrics            - Prometheus metrics (no auth required)
- GET  /docs               - interactive OpenAPI documentation

The application loads all model artifacts once at startup and serves
predictions from in-memory state. Latency is dominated by model
inference and dataframe lookup, not I/O.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .config import settings
from .dependencies import store
from .routes import forecast, segment
from .schemas import HealthResponse


# ----------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Lifecycle - load models at startup
# ----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models and data at startup; clean up at shutdown."""
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("Loading model artifacts...")
    store.load()
    if not store.models_loaded:
        logger.warning("API started without K-Means model - /predict/segment will fail")
    if not store.data_loaded:
        logger.warning("API started without forecast data - /predict/forecast will fail")
    logger.info("Startup complete")

    yield

    logger.info("Shutting down")


# ----------------------------------------------------------------------------
# Application
# ----------------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    description=(
        "Production deployment of the AdventureWorks Cycles ML models. "
        "Provides customer segmentation and revenue forecasting endpoints. "
        "All prediction endpoints require an `X-API-Key` header."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Permissive CORS for the portfolio demo; tighten for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics - exposed at /metrics (no auth)
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


# ----------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------
app.include_router(segment.router)
app.include_router(forecast.router)


@app.get("/", tags=["meta"])
async def root() -> dict:
    """Root endpoint - service metadata."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "endpoints": {
            "POST /predict/segment": "Live customer segmentation (requires API key)",
            "POST /predict/forecast": "Revenue forecast (requires API key)",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health() -> HealthResponse:
    """Health check - no auth required, used by Docker healthcheck."""
    overall = "healthy"
    if not store.models_loaded:
        overall = "degraded"
    if not store.data_loaded:
        overall = "unhealthy"

    return HealthResponse(
        status=overall,
        version=settings.app_version,
        models_loaded=store.models_loaded,
        data_loaded=store.data_loaded,
    )
