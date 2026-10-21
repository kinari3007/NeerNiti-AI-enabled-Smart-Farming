"""
ML model loader.

Loads the trained fertilizer classifier pipeline and label encoder once per
process.  Repeated calls to get_model() return the cached instance.

If the model artifacts are missing, get_model() returns None and the
recommendation service falls back gracefully (warning added to recommendation).
"""
import json
import logging
import pickle
from pathlib import Path
from typing import Optional

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from app.core.config import settings

logger = logging.getLogger("neerniti.ml.model_loader")

# Module-level cache — loaded once per worker process
_pipeline: Optional[Pipeline] = None
_label_encoder: Optional[LabelEncoder] = None
_model_metadata: Optional[dict] = None
_load_attempted: bool = False


def _resolve_path(config_path: str) -> Path:
    """Resolve a path relative to the repository root (two levels above backend/)."""
    p = Path(config_path)
    if p.is_absolute():
        return p
    # config_path is relative to repo root (e.g. "ml/artifacts/...")
    # backend/app/ml/model_loader.py → parents[0]=ml, [1]=app, [2]=backend, [3]=repo root
    repo_root = Path(__file__).resolve().parents[3]
    resolved = repo_root / p
    if not resolved.exists():
        # Fallback: maybe CWD is already repo root
        resolved_cwd = Path.cwd() / p
        if resolved_cwd.exists():
            return resolved_cwd
    return resolved


def load_model() -> tuple[Optional[Pipeline], Optional[LabelEncoder], Optional[dict]]:
    """
    Load model artifacts from disk.
    Returns (pipeline, label_encoder, metadata) or (None, None, None) if not found.
    """
    global _pipeline, _label_encoder, _model_metadata, _load_attempted
    _load_attempted = True

    model_path = _resolve_path(settings.ML_MODEL_PATH)
    le_path = _resolve_path(settings.ML_LABEL_ENCODER_PATH)

    if not model_path.exists():
        logger.warning(
            "ML model not found at %s. "
            "Run ml/src/models/train_classifier.py to generate artifacts. "
            "ML suggestions will be unavailable.",
            model_path,
        )
        return None, None, None

    if not le_path.exists():
        logger.warning("Label encoder not found at %s.", le_path)
        return None, None, None

    try:
        with open(model_path, "rb") as f:
            _pipeline = pickle.load(f)  # noqa: S301 — trusted internal artifact
        with open(le_path, "rb") as f:
            _label_encoder = pickle.load(f)  # noqa: S301

        # Load metadata if available
        meta_path = model_path.parent / "model_metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                _model_metadata = json.load(f)

        logger.info(
            "ML model loaded from %s (version: %s)",
            model_path,
            (_model_metadata or {}).get("model_version", "unknown"),
        )
        return _pipeline, _label_encoder, _model_metadata

    except Exception as exc:
        logger.error("Failed to load ML model: %s", exc)
        _pipeline = None
        _label_encoder = None
        _model_metadata = None
        return None, None, None


def get_model() -> tuple[Optional[Pipeline], Optional[LabelEncoder], Optional[dict]]:
    """Return the cached model, loading it on the first call."""
    global _load_attempted
    if not _load_attempted:
        load_model()
    return _pipeline, _label_encoder, _model_metadata


def is_model_available() -> bool:
    pipeline, le, _ = get_model()
    return pipeline is not None and le is not None
