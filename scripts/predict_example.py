import _project_path  # noqa: F401
import joblib
import pandas as pd

from airwise.config import MODELS_DIR, PROCESSED_DIR
from airwise.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES, build_features, pm25_category

if __name__ == "__main__":
    daily = pd.read_csv(PROCESSED_DIR / "india_metro_daily_air_quality.csv")
    features = build_features(daily)
    model = joblib.load(MODELS_DIR / "air_quality_model.joblib")
    latest = features.sort_values("date").groupby("city", as_index=False).tail(1).copy()
    latest["forecast_pm2_5"] = model.predict(latest[NUMERIC_FEATURES + CATEGORICAL_FEATURES])
    latest["forecast_category"] = latest["forecast_pm2_5"].map(pm25_category)
    print(
        latest[["city", "target_date", "forecast_pm2_5", "forecast_category"]].to_string(
            index=False
        )
    )
