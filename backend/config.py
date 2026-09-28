"""
Application configuration loaded from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Server ──
APP_TITLE = "AgriRisk AI - Agricultural Insurance Risk Assessment"
APP_DESCRIPTION = (
    "AI-driven risk assessment engine for agricultural insurance policies. "
    "Uses Cox Proportional Hazards survival analysis with El Nino integration "
    "to predict claim probability, survival curves, and explainable risk factors."
)
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
MODEL_VERSION = os.getenv("MODEL_VERSION", "cox-ph-v1")

# ── Database ──
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./predictions.db")

# ── CORS ──
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
).split(",")

# ── Logging ──
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ── ML Paths (relative to project root) ──
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPELINE_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "ml_pipeline_output")
MODEL_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "model_output")
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "raw_unclean_dataset.csv")

# ── Risk Assessment ──
RISK_THRESHOLDS = {
    "HIGH": float(os.getenv("RISK_THRESHOLD_HIGH", "1.5")),
    "MEDIUM": float(os.getenv("RISK_THRESHOLD_MEDIUM", "1.0")),
}
DEFAULT_PREMIUM_RATE = float(os.getenv("DEFAULT_PREMIUM_RATE", "2.0"))
