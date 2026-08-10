import json

import pandas as pd

from airwise.config import PROCESSED_DIR
from airwise.features import build_features
from airwise.modelling import train_and_evaluate

if __name__ == "__main__":
    daily = pd.read_csv(PROCESSED_DIR / "india_metro_daily_air_quality.csv")
    features = build_features(daily)
    metrics = train_and_evaluate(features)
    print(json.dumps(metrics, indent=2))
