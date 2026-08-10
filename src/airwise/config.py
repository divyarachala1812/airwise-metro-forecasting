from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
MODELS_DIR = ROOT / "models"

START_DATE = "2022-08-01"
END_DATE = "2025-12-31"
TIMEZONE = "Asia/Kolkata"

CITIES = {
    "Delhi": {"latitude": 28.6139, "longitude": 77.2090},
    "Mumbai": {"latitude": 19.0760, "longitude": 72.8777},
    "Hyderabad": {"latitude": 17.3850, "longitude": 78.4867},
}

AIR_QUALITY_VARIABLES = ["pm2_5", "pm10", "nitrogen_dioxide", "ozone"]
WEATHER_VARIABLES = [
    "temperature_2m_mean",
    "relative_humidity_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_mean",
    "wind_gusts_10m_max",
]

TRAIN_END = "2024-06-30"
VALIDATION_END = "2024-12-31"
ALERT_THRESHOLD = 60.0
