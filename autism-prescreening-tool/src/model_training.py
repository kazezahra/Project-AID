import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score
)

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from sklearn.pipeline import Pipeline

from src.config import PROCESSED_TRAIN_PATH, MODELS_DIR
from src.model_pipeline import get_feature_config, build_preprocessor


def load_data():
    df = pd.read_csv(PROCESSED_TRAIN_PATH)
    return df


def evaluate_model(name, model, X_test, y_test):
    y_pred = model.predict(X_test)

    # Some models provide probability output
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_prob)
    else:
        auc = None

    print("\n" + "=" * 70)
    print(f"MODEL: {name}")
    print("=" * 70)

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    if auc is not None:
        print("ROC-AUC:", round(auc, 4))

    return auc


def main():
    df = load_data()

    feature_config = get_feature_config()
    X = df[feature_config.numeric_cols]
    y = df["target"]

    # Stratified split due to imbalance
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    preprocessor = build_preprocessor(feature_config)

    # -----------------------
    # Model 1: Logistic Regression (baseline)
    # -----------------------
    logreg = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(
            max_iter=2000,
            class_weight="balanced"
        ))
    ])

    # -----------------------
    # Model 2: Random Forest
    # -----------------------
    rf = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced"
        ))
    ])

    # -----------------------
    # Model 3: XGBoost (strong tabular model)
    # -----------------------
    # scale_pos_weight helps imbalance (minority class weight)
    # BUT: here ASD is majority, so we do not set scale_pos_weight.
    # We'll rely on tuning later if needed.

    xgb = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", XGBClassifier(
            n_estimators=400,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            eval_metric="logloss"
        ))
    ])

    models = {
        "Logistic Regression": logreg,
        "Random Forest": rf,
        "XGBoost": xgb
    }

    best_auc = -1
    best_name = None
    best_model = None

    for name, model in models.items():
        model.fit(X_train, y_train)
        auc = evaluate_model(name, model, X_test, y_test)

        if auc is not None and auc > best_auc:
            best_auc = auc
            best_name = name
            best_model = model

    # Save best model
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    save_path = MODELS_DIR / "best_model.joblib"

    joblib.dump(best_model, save_path)

    print("\n" + "=" * 70)
    print("BEST MODEL SAVED")
    print("Model:", best_name)
    print("ROC-AUC:", round(best_auc, 4))
    print("Saved to:", save_path)
    print("=" * 70)


if __name__ == "__main__":
    main()
