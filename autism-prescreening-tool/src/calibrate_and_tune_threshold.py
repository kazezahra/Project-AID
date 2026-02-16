import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_auc_score,
    precision_recall_curve
)
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

from src.config import PROCESSED_TRAIN_PATH, MODELS_DIR
from src.model_pipeline import get_feature_config, build_preprocessor


def find_best_threshold(y_true, y_prob, min_precision=0.90):
    """
    Finds the threshold that gives highest recall while maintaining
    precision >= min_precision.

    This is appropriate for screening:
    - prioritize recall (catch ASD)
    - but avoid too many false positives
    """
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_prob)

    best_threshold = 0.5
    best_recall = -1

    # thresholds array is length-1 compared to precision/recall
    for i, t in enumerate(thresholds):
        p = precisions[i]
        r = recalls[i]

        if p >= min_precision and r > best_recall:
            best_recall = r
            best_threshold = t

    return float(best_threshold), float(best_recall)


def main():
    df = pd.read_csv(PROCESSED_TRAIN_PATH)

    feature_config = get_feature_config()
    X = df[feature_config.numeric_cols]
    y = df["target"]

    # Split for calibration + evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    preprocessor = build_preprocessor(feature_config)

    base_model = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(
            max_iter=2000,
            class_weight="balanced"
        ))
    ])

    # Fit base model
    base_model.fit(X_train, y_train)

    # Calibrate probabilities (sigmoid = Platt scaling)
    calibrated_model = CalibratedClassifierCV(
        estimator=base_model,
        method="sigmoid",
        cv=5
    )
    calibrated_model.fit(X_train, y_train)

    # Predict probabilities
    y_prob = calibrated_model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)

    print("\n" + "=" * 70)
    print("CALIBRATED LOGISTIC REGRESSION RESULTS")
    print("=" * 70)
    print("ROC-AUC:", round(auc, 4))

    # Default threshold
    y_pred_default = (y_prob >= 0.5).astype(int)

    print("\n--- Threshold = 0.50 (default) ---")
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_default))
    print("\nClassification Report:\n", classification_report(y_test, y_pred_default))

    # Threshold tuning
    best_t, best_r = find_best_threshold(y_test, y_prob, min_precision=0.90)

    print("\n--- Threshold Tuning ---")
    print("Selected threshold:", round(best_t, 4))
    print("Recall at selected threshold:", round(best_r, 4))

    y_pred_tuned = (y_prob >= best_t).astype(int)

    print("\n--- Threshold = Tuned ---")
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_tuned))
    print("\nClassification Report:\n", classification_report(y_test, y_pred_tuned))

    # Save calibrated model + threshold
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(calibrated_model, MODELS_DIR / "calibrated_model.joblib")

    threshold_config = {
        "threshold": best_t,
        "min_precision_constraint": 0.90
    }

    joblib.dump(threshold_config, MODELS_DIR / "threshold_config.joblib")

    print("\n✅ Saved calibrated model to:")
    print(MODELS_DIR / "calibrated_model.joblib")

    print("\n✅ Saved threshold config to:")
    print(MODELS_DIR / "threshold_config.joblib")


if __name__ == "__main__":
    main()
