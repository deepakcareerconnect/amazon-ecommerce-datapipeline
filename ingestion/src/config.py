
import os
from pathlib import Path
from dotenv import load_dotenv

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

load_dotenv(PROJECT_ROOT / ".env")

# DummyJSON configuration
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://dummyjson.com"
)

API_PAGE_SIZE = int(os.getenv("API_PAGE_SIZE", "30"))
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# AWS configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET = os.getenv("S3_BUCKET", "")

# Storage mode: local or s3
STORAGE_MODE = os.getenv("STORAGE_MODE", "local").lower()

# Categories to extract
CATEGORIES = [
    "smartphones",
    "laptops",
    "furniture",
    "groceries",
    "home-decoration"
]
