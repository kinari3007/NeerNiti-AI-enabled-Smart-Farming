"""
Fertilizer Category Classifier — Training Script
=================================================

IMPORTANT DISCLAIMER
--------------------
This script trains a classifier on the fertilizer_recommendation.csv dataset.

The model predicts a fertilizer CATEGORY (e.g. Urea, DAP, MOP) based on
soil and weather features. It does NOT:
  - Determine scientifically validated nutrient quantities.
  - Establish crop-specific application rates.
  - Replace agronomic soil testing or certified agronomist advice.

The dataset contains fertilizer labels assigned under various combinations of
soil and crop conditions. The classifier learns statistical associations in
that dataset, not agronomic causality.

Usage
-----
Run from the repository root:
    python ml/src/models/train_classifier.py

Output artifacts (saved to ml/artifacts/):
    fertilizer_classifier.pkl   — trained scikit-learn pipeline
    label_encoder.pkl           — fitted LabelEncoder for target classes
    feature_scaler.pkl          — fitted StandardScaler (also inside pipeline)
    model_metadata.json         — training metrics and configuration

Requirements
------------
    pip install scikit-learn numpy pandas
"""

import json
import logging
import os
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_script_parents = Path(__file__).resolve().parents
# ml/src/models/train_classifier.py  →  parents[3] = repo root
REPO_ROOT = _script_parents[3]
# Fallback: if running from repo root as CWD
if not (REPO_ROOT / "data").exists():
    REPO_ROOT = Path.cwd()

DATA_PATH = REPO_ROOT / "data" / "raw" / "fertilizer_recommendation.csv"
ARTIFACTS_DIR = REPO_ROOT / "ml" / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Feature configuration
# ---------------------------------------------------------------------------
# Numeric features available in the dataset
NUMERIC_FEATURES = [
    "Soil_pH",
    "Soil_Moisture",
    "Organic_Carbon",
    "Electrical_Conductivity",
    "Nitrogen_Level",
    "Phosphorus_Level",
    "Potassium_Level",
    "Temperature",
    "Humidity",
    "Rainfall",
    "Yield_Last_Season",
]

# Categorical features
CATEGORICAL_FEATURES = [
    "Soil_Type",
    "Crop_Type",
    "Crop_Growth_Stage",
    "Season",
    "Irrigation_Type",
    "Previous_Crop",
    "Region",
]

# We intentionally exclude "Fertilizer_Used_Last_Season" because it would
# leak information about fertilizer choices, reducing the model's usefulness
# for novel situations where prior-season data may not be available.

TARGET_COLUMN = "Recommended_Fertilizer"

MODEL_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def load_and_validate_data(path: Path) -> pd.DataFrame:
    logger.info("Loading dataset from %s", path)
    df = pd.read_csv(path)
    logger.info("Dataset shape: %s", df.shape)
    logger.info("Columns: %s", df.columns.tolist())

    # Verify expected columns
    required = set(NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET_COLUMN])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing expected columns: {missing}")

    # Report class distribution
    class_counts = df[TARGET_COLUMN].value_counts()
    logger.info("Class distribution:\n%s", class_counts.to_string())

    # Report missing values
    nulls = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].isnull().sum()
    nulls = nulls[nulls > 0]
    if not nulls.empty:
        logger.warning("Columns with missing values:\n%s", nulls.to_string())
    else:
        logger.info("No missing values in feature columns.")

    return df


def build_pipeline(n_classes: int) -> Pipeline:
    """
    Build a scikit-learn Pipeline:
      ColumnTransformer (numeric → StandardScaler, categorical → OneHotEncoder)
      → RandomForestClassifier

    RandomForest was chosen because:
      - It handles mixed numeric/categorical data naturally.
      - It is robust to feature scale without requiring normalisation, but
        StandardScaler is included for consistency with the inference interface.
      - It provides feature importances for basic explainability.
      - It tends to generalise well on moderate-sized tabular datasets
        without extensive hyperparameter tuning.
    """
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )

    classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced",  # mitigates class imbalance
        random_state=42,
        n_jobs=-1,
    )

    return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", classifier)])


def train_and_evaluate(df: pd.DataFrame) -> dict:
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_raw = df[TARGET_COLUMN]

    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    classes = list(le.classes_)
    n_classes = len(classes)
    logger.info("Target classes (%d): %s", n_classes, classes)

    # Stratified 80/20 split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    logger.info("Train size: %d  Test size: %d", len(X_train), len(X_test))

    pipeline = build_pipeline(n_classes)

    logger.info("Training RandomForestClassifier (n_estimators=200)...")
    pipeline.fit(X_train, y_train)

    # --- Evaluation ---
    y_pred = pipeline.predict(X_test)
    y_pred_proba = pipeline.predict_proba(X_test)

    macro_f1 = f1_score(y_test, y_pred, average="macro")
    weighted_f1 = f1_score(y_test, y_pred, average="weighted")
    accuracy = float(np.mean(y_pred == y_test))

    logger.info("Test accuracy:         %.4f", accuracy)
    logger.info("Test macro F1:         %.4f", macro_f1)
    logger.info("Test weighted F1:      %.4f", weighted_f1)

    report = classification_report(
        y_test, y_pred,
        target_names=classes,
        output_dict=True,
    )
    logger.info("Per-class report:\n%s", classification_report(y_test, y_pred, target_names=classes))

    # 5-fold stratified cross-validation on the full dataset
    logger.info("Running 5-fold stratified CV on full dataset...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(
        pipeline, X, y, cv=cv, scoring="f1_macro", n_jobs=-1
    )
    logger.info(
        "CV macro F1: %.4f ± %.4f (per fold: %s)",
        cv_scores.mean(), cv_scores.std(),
        [f"{s:.4f}" for s in cv_scores],
    )

    # --- Save artifacts ---
    model_path = ARTIFACTS_DIR / "fertilizer_classifier.pkl"
    le_path = ARTIFACTS_DIR / "label_encoder.pkl"

    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)
    with open(le_path, "wb") as f:
        pickle.dump(le, f)

    logger.info("Model saved to %s", model_path)
    logger.info("LabelEncoder saved to %s", le_path)

    # --- Metadata ---
    metadata = {
        "model_version": MODEL_VERSION,
        "algorithm": "RandomForestClassifier",
        "n_estimators": 200,
        "features_numeric": NUMERIC_FEATURES,
        "features_categorical": CATEGORICAL_FEATURES,
        "target_column": TARGET_COLUMN,
        "target_classes": classes,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "test_accuracy": round(accuracy, 6),
        "test_macro_f1": round(macro_f1, 6),
        "test_weighted_f1": round(weighted_f1, 6),
        "cv_macro_f1_mean": round(float(cv_scores.mean()), 6),
        "cv_macro_f1_std": round(float(cv_scores.std()), 6),
        "cv_fold_scores": [round(float(s), 6) for s in cv_scores],
        "per_class_report": report,
        "disclaimer": (
            "This model predicts a fertilizer CATEGORY (classification). "
            "It does NOT determine scientifically validated nutrient quantities "
            "or application rates. Training data is from fertilizer_recommendation.csv "
            "which reflects statistical associations, not agronomic causality."
        ),
        "dataset_path": str(DATA_PATH),
        "artifact_paths": {
            "pipeline": str(model_path),
            "label_encoder": str(le_path),
        },
    }

    meta_path = ARTIFACTS_DIR / "model_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Metadata saved to %s", meta_path)

    return metadata


if __name__ == "__main__":
    if not DATA_PATH.exists():
        logger.error("Dataset not found at %s", DATA_PATH)
        sys.exit(1)

    df = load_and_validate_data(DATA_PATH)
    metadata = train_and_evaluate(df)

    print("\n" + "=" * 60)
    print(f"Training complete — model version {metadata['model_version']}")
    print(f"  Test accuracy:    {metadata['test_accuracy']:.4f}")
    print(f"  Test macro F1:    {metadata['test_macro_f1']:.4f}")
    print(f"  CV macro F1:      {metadata['cv_macro_f1_mean']:.4f} ± {metadata['cv_macro_f1_std']:.4f}")
    print(f"  Classes: {metadata['target_classes']}")
    print("=" * 60)
    print("\nIMPORTANT: This model predicts a fertilizer category, not nutrient quantities.")
