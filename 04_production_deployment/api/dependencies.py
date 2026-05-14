"""
Model and data loading.

Models and lookup tables are loaded once at application startup and held
in module-level singletons. This avoids re-loading on every request.

In a production system, a more sophisticated approach would use a model
registry (MLflow) and connect to a live database. For this portfolio
service, we load from local files.
"""

from __future__ import annotations

import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .config import settings

logger = logging.getLogger(__name__)


class ModelStore:
    """Holds loaded model artifacts. Initialized once at startup."""

    def __init__(self) -> None:
        self.kmeans = None
        self.scaler = None
        self.cluster_names: dict[int, str] = {}
        self.reference_date: pd.Timestamp = pd.Timestamp(settings.reference_date)

        # DataFrames loaded from disk
        self.fact_sales: pd.DataFrame | None = None
        self.segments_cache: pd.DataFrame | None = None
        self.forecasts: pd.DataFrame | None = None

    @property
    def models_loaded(self) -> bool:
        return self.kmeans is not None and self.scaler is not None

    @property
    def data_loaded(self) -> bool:
        return all(
            df is not None
            for df in [self.fact_sales, self.segments_cache, self.forecasts]
        )

    def load(self) -> None:
        """Load all artifacts from disk. Called once at startup."""
        self._load_kmeans_model()
        self._load_forecasts()
        self._load_segments_cache()
        self._load_fact_sales()

    def _load_kmeans_model(self) -> None:
        path = settings.models_dir / "kmeans_segmentation.joblib"
        if not path.exists():
            logger.warning("K-Means model not found at %s", path)
            return
        bundle = joblib.load(path)
        self.kmeans = bundle["kmeans"]
        self.scaler = bundle["scaler"]
        self.cluster_names = bundle["cluster_names"]
        # The training reference date may differ from settings; trust the bundle
        bundle_ref = bundle.get("reference_date")
        if bundle_ref is not None:
            self.reference_date = pd.Timestamp(bundle_ref)
        logger.info(
            "Loaded K-Means model: %d clusters, reference_date=%s",
            self.kmeans.n_clusters,
            self.reference_date.date(),
        )

    def _load_forecasts(self) -> None:
        path = settings.predictions_dir / "forecasts.csv"
        if not path.exists():
            logger.warning("forecasts.csv not found at %s", path)
            return
        self.forecasts = pd.read_csv(path, parse_dates=["month"])
        logger.info("Loaded forecasts: %d rows", len(self.forecasts))

    def _load_segments_cache(self) -> None:
        path = settings.predictions_dir / "segments.csv"
        if not path.exists():
            logger.warning("segments.csv not found at %s", path)
            return
        self.segments_cache = pd.read_csv(path)
        logger.info("Loaded segments cache: %d customers", len(self.segments_cache))

    def _load_fact_sales(self) -> None:
        """fact_sales is large; load it once for live segment computation."""
        path = settings.data_dir / "fact_sales.csv"
        if not path.exists():
            logger.warning("fact_sales.csv not found at %s", path)
            # For the API to function, we substitute with the segments cache
            # for any customer lookups (the cache has R, F, M precomputed).
            return
        self.fact_sales = pd.read_csv(path, parse_dates=["order_date"]).dropna(
            subset=["order_date"]
        )
        logger.info("Loaded fact_sales: %d rows", len(self.fact_sales))

    def compute_rfm_live(self, customer_key: int) -> dict | None:
        """Compute R, F, M for a customer from fact_sales.

        Returns dict with keys recency, frequency, monetary — or None
        if the customer has no transactions.
        """
        if self.fact_sales is None:
            # Fall back to cache if fact_sales isn't loaded
            return self._compute_rfm_from_cache(customer_key)

        cust_sales = self.fact_sales[self.fact_sales["customer_key"] == customer_key]
        if len(cust_sales) == 0:
            return None

        recency = (self.reference_date - cust_sales["order_date"].max()).days
        # Frequency = row count (matches Power BI definition)
        frequency = len(cust_sales)
        monetary = float(cust_sales["sales_amount"].sum())
        return {
            "recency": float(recency),
            "frequency": int(frequency),
            "monetary": monetary,
        }

    def _compute_rfm_from_cache(self, customer_key: int) -> dict | None:
        """Fallback: pull RFM from the cached segments table."""
        if self.segments_cache is None:
            return None
        row = self.segments_cache[self.segments_cache["customer_key"] == customer_key]
        if len(row) == 0:
            return None
        r = row.iloc[0]
        return {
            "recency": float(r["Recency"]),
            "frequency": int(r["Frequency"]),
            "monetary": float(r["Monetary"]),
        }

    def predict_cluster(self, recency: float, frequency: float, monetary: float) -> tuple[int, str]:
        """Apply the trained K-Means model to a single R, F, M tuple."""
        if not self.models_loaded:
            raise RuntimeError("K-Means model not loaded")

        # Same transform as training: log1p + StandardScaler.
        # Pass as a DataFrame with the original feature names so the
        # scaler does not emit a "missing feature names" warning.
        x_log = pd.DataFrame(
            [[np.log1p(recency), np.log1p(frequency), np.log1p(monetary)]],
            columns=["Recency", "Frequency", "Monetary"],
        )
        x_scaled = self.scaler.transform(x_log)
        cluster = int(self.kmeans.predict(x_scaled)[0])
        name = self.cluster_names.get(cluster, f"Cluster {cluster}")
        return cluster, name

    def get_cached_rfm_segment(self, customer_key: int) -> str | None:
        """Return the precomputed Power BI RFM segment if available."""
        if self.segments_cache is None:
            return None
        row = self.segments_cache[self.segments_cache["customer_key"] == customer_key]
        if len(row) == 0:
            return None
        seg = row.iloc[0]["RFM_Segment"]
        return None if pd.isna(seg) else str(seg)


# Module-level singleton populated by startup
store = ModelStore()
