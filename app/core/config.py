from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

class Settings:

    SALES_SERVICE_URL = os.getenv("SALES_SERVICE_URL", "http://localhost:8003")

    INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8002")

    INVENTORY_SERVICE_TOKEN = os.getenv("INVENTORY_SERVICE_TOKEN")

    source_file = (REPOSITORY_ROOT / "app" / "data" / "source.csv")

    target_file = (REPOSITORY_ROOT / "app" / "data" / "target.csv")

    reports_dir = (REPOSITORY_ROOT / "reports")

    charts_dir = (REPOSITORY_ROOT / "reports" / "charts")

    dataset_size = int(os.getenv("DATASET_SIZE", 1000))

    mismatch_rate = float(os.getenv("MISMATCH_RATE", 0.05))

settings = Settings()