import pandas as pd
import numpy as np
from src.config import RAW_DATASET_PATH, PROCESSED_TRAIN_PATH, PROCESSED_DATA_DIR


def load_raw_dataset() -> pd.DataFrame:
    return pd.read_csv(RAW_DATASET_PATH)


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        c.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        for c in df.columns
    ]
    return df


def yes_no_map(x):
    if pd.isna(x):
        return np.nan
    x = str(x).strip().lower()
    if x in ["yes", "y", "true", "1"]:
        return 1
    if x in ["no", "n", "false", "0"]:
        return 0
    return np.nan


def preprocess_for_training(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # ---- Target ----
    if "class/asd_traits" in df.columns:
        df.rename(columns={"class/asd_traits": "target"}, inplace=True)
    else:
        raise ValueError("Target column not found after cleaning. Expected: class/asd_traits")

    df["target"] = df["target"].astype(str).str.strip().str.lower()
    df["target"] = df["target"].map({"yes": 1, "no": 0})
    df = df.dropna(subset=["target"])

    # ---- QCHAT columns ----
    q_cols = [f"a{i}" for i in range(1, 11)]
    for c in q_cols:
        if c not in df.columns:
            raise ValueError(f"Missing QCHAT column: {c}")
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # ---- Age ----
    if "age_mons" not in df.columns:
        raise ValueError("Missing column: age_mons")
    df["age_mons"] = pd.to_numeric(df["age_mons"], errors="coerce")

    # ---- Sex ----
    if "sex" not in df.columns:
        raise ValueError("Missing column: sex")

    df["sex"] = df["sex"].astype(str).str.strip().str.lower()
    df["sex"] = df["sex"].map({"m": 1, "male": 1, "f": 0, "female": 0})

    # ---- Jaundice ----
    if "jaundice" not in df.columns:
        raise ValueError("Missing column: jaundice")
    df["jaundice"] = df["jaundice"].apply(yes_no_map)

    # ---- Family history ----
    if "family_mem_with_asd" not in df.columns:
        raise ValueError("Missing column: family_mem_with_asd")
    df["family_mem_with_asd"] = df["family_mem_with_asd"].apply(yes_no_map)

    # ---- Drop unwanted columns ----
    drop_cols = []
    for col in ["case_no", "ethnicity", "who_completed_the_test", "qchat_10_score"]:
        if col in df.columns:
            drop_cols.append(col)

    df.drop(columns=drop_cols, inplace=True)

    # ---- Recompute QCHAT score ----
    df["qchat_score"] = df[q_cols].sum(axis=1)

    # ---- Drop rows with missing core fields ----
    df = df.dropna(subset=q_cols + ["age_mons", "sex", "jaundice", "family_mem_with_asd"])

    # Ensure correct data types
    df[q_cols] = df[q_cols].astype(int)
    df["sex"] = df["sex"].astype(int)
    df["jaundice"] = df["jaundice"].astype(int)
    df["family_mem_with_asd"] = df["family_mem_with_asd"].astype(int)
    df["qchat_score"] = df["qchat_score"].astype(int)
    df["target"] = df["target"].astype(int)

    return df


def save_processed_dataset(df: pd.DataFrame):
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_TRAIN_PATH, index=False)


def run_pipeline():
    df = load_raw_dataset()
    df = clean_column_names(df)
    df = preprocess_for_training(df)
    save_processed_dataset(df)

    print("✅ Processed dataset saved to:", PROCESSED_TRAIN_PATH)
    print("Shape:", df.shape)
    print("\nTarget distribution:\n", df["target"].value_counts())


if __name__ == "__main__":
    run_pipeline()
