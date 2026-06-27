import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SOURCE_FILE = BASE_DIR / os.getenv("SOURCE_FILE", "data/source.csv")

TARGET_FILE = BASE_DIR / os.getenv("TARGET_FILE", "data/target.csv")

REPORTS_DIR = BASE_DIR / os.getenv("REPORTS_DIR", "reports")

CHARTS_DIR = BASE_DIR / os.getenv("CHARTS_DIR", "reports/charts")

DATASET_SIZE = int(os.getenv("DATASET_SIZE", 1000))

MISMATCH_RATE = float(os.getenv("MISMATCH_RATE", 0.05))