from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

RAW_DATASET_PATH = RAW_DATA_DIR / "Toddler Autism dataset July 2018.csv"

PROCESSED_TRAIN_PATH = PROCESSED_DATA_DIR / "train_ready.csv"