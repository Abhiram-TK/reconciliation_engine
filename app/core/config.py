import os

from dotenv import load_dotenv

load_dotenv()

class Settings:

    SALES_SERVICE_URL = os.getenv("SALES_SERVICE_URL", "http://localhost:8003")

    INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8002")

    INVENTORY_SERVICE_TOKEN = os.getenv("INVENTORY_SERVICE_TOKEN")

    REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")

    CHARTS_DIR = os.getenv("CHARTS_DIR", "reports/charts")

    DATASET_SIZE = int(os.getenv("DATASET_SIZE", 1000))

    MISMATCH_RATE = float(os.getenv("MISMATCH_RATE", 0.05))

settings = Settings()