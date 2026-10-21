"""
Fertilizer classifier inference interface.

This module provides the `predict_fertilizer_category` function, which:
  1. Validates inputs and assembles the feature DataFrame.
  2. Runs the trained pipeline to predict a fertilizer category label.
  3. Returns an MLClassifierOutput schema instance.

IMPORTANT DISTINCTION
---------------------
The classifier predicts a fertilizer *category* (e.g. "Urea", "DAP").
This is a data-driven statistical suggestion, NOT:
  - A validated nutrient quantity.
  - An agronomically calibrated application rate.
  - A replacement for soil testing or certified agronomist advice.

The optimization engine (optimization/fertilizer_optimizer.py) determines
actual application quantities based on crop nutrient requirements and prices.
"""
import logging
from typing import Optional

import numpy as np

from app.ml.feature_engineering import build_feature_dataframe
from app.ml.model_loader import get_model, is_model_available
from app.models.soil_reading import SoilReading
from app.schemas.recommendation import MLClassifierOutput, RecommendationRequest
from app.schemas.weather import WeatherResponse

logger = logging.getLogger("neerniti.ml.nutrient_estimator")

_CLASSIFIER_DISCLAIMER = (
    "The ML classifier suggests a fertilizer category based on statistical "
    "patterns in the training dataset (fertilizer_recommendation.csv). "
    "It does NOT determine scientifically validated nutrient quantities, "
    "application rates, or field-specific requirements. "
    "This suggestion should be treated as one input among several, "
    "not as an agronomic prescription."
)


def predict_fertilizer_category(
    request: RecommendationRequest,
    crop_name: str,
    growth_stage: str,
    readings: list[SoilReading],
    weather: Optional[WeatherResponse],
) -> tuple[Optional[MLClassifierOutput], list[str]]:
    """
    Run the fertilizer category classifier.

    Returns:
        (MLClassifierOutput | None, list_of_warning_strings)

    Returns (None, warnings) if the model is unavailable or inference fails.
    Never raises — exceptions are caught and returned as warnings.
    """
    warnings: list[str] = []

    if not is_model_available():
        warnings.append(
            "ML model artifacts not found. Run ml/src/models/train_classifier.py "
            "to generate them. ML category suggestion is unavailable."
        )
        return None, warnings

    pipeline, label_encoder, metadata = get_model()

    try:
        feature_df, missing_features = build_feature_dataframe(
            request=request,
            crop_name=crop_name,
            growth_stage=growth_stage,
            readings=readings,
            weather=weather,
        )

        if missing_features:
            warnings.append(
                f"ML features missing (will use NaN/defaults): {missing_features}. "
                "Classifier confidence may be lower."
            )

        # Run inference
        y_pred = pipeline.predict(feature_df)
        y_proba = pipeline.predict_proba(feature_df)

        predicted_label: str = label_encoder.inverse_transform(y_pred)[0]
        probabilities: list[float] = y_proba[0].tolist()
        classes: list[str] = list(label_encoder.classes_)

        confidence: float = float(max(probabilities))

        # Top-3 classes by probability
        sorted_indices = np.argsort(probabilities)[::-1]
        top_classes = [
            {"class": classes[i], "probability": round(float(probabilities[i]), 4)}
            for i in sorted_indices[:3]
        ]

        model_version = (metadata or {}).get("model_version", "unknown")

        result = MLClassifierOutput(
            predicted_class=predicted_label,
            confidence=round(confidence, 4),
            top_classes=top_classes,
            input_features_used=[f for f in feature_df.columns if not feature_df[f].isna().all()],
            disclaimer=_CLASSIFIER_DISCLAIMER,
        )

        logger.info(
            "ML classifier predicted '%s' (confidence=%.3f) for crop='%s' stage='%s'",
            predicted_label, confidence, crop_name, growth_stage,
        )
        return result, warnings

    except Exception as exc:
        logger.warning("ML inference failed: %s", exc, exc_info=True)
        warnings.append(
            f"ML classifier inference failed: {exc}. "
            "The recommendation will proceed without an ML category suggestion."
        )
        return None, warnings
