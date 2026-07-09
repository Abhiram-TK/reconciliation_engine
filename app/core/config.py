import os

from dataclasses import dataclass

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)

class Settings:

    base_dir: Path

    source_file: Path
    target_file: Path

    reports_dir: Path
    charts_dir: Path

    dataset_size: int
    mismatch_rate: float

BASE_DIR = Path(__file__).resolve().parent.parent

settings = Settings(base_dir=BASE_DIR,

    source_file=BASE_DIR / os.getenv("SOURCE_FILE", "data/source.csv"),

    target_file=BASE_DIR / os.getenv("TARGET_FILE", "data/target.csv"),

    reports_dir=BASE_DIR / os.getenv("REPORTS_DIR", "reports"),

    charts_dir=BASE_DIR / os.getenv("CHARTS_DIR", "reports/charts"),

    dataset_size=int(os.getenv("DATASET_SIZE", 1000)),

    mismatch_rate=float(os.getenv("MISMATCH_RATE", 0.05)))