from __future__ import annotations

import numpy as np
import pandas as pd

NUMERIC_FEATURES = [
    "pm2_5_lag_1",
    "pm2_5_lag_2",
    "pm2_5_lag_3",
    "pm2_5_roll_3",
    "pm2_5_roll_7",
    "pm2_5_roll_7_std",
    "pm10_mean",
    "pm10_max",
    "nitrogen_dioxide_mean",
    "nitrogen_dioxide_max",
    "ozone_mean",
    "ozone_max",
    "temperature_2m_mean",
    "relative_humidity_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_mean",
    "wind_gusts_10m_max",
    "month_sin",
    "month_cos",
    "day_of_year_sin",
    "day_of_year_cos",
]
CATEGORICAL_FEATURES = ["city"]
TARGET = "target_pm2_5_next_day"


def pm25_category(value: float) -> str:
    if value <= 30:
        return "Good"
    if value <= 60:
        return "Satisfactory"
    if value <= 90:
        return "Moderately polluted"
    if value <= 120:
        return "Poor"
    if value <= 250:
        return "Very poor"
    return "Severe"


def build_features(daily: pd.DataFrame) -> pd.DataFrame:
    frame = daily.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.sort_values(["city", "date"]).reset_index(drop=True)
    grouped = frame.groupby("city", group_keys=False)
    frame["pm2_5_lag_1"] = frame["pm2_5_mean"]
    frame["pm2_5_lag_2"] = grouped["pm2_5_mean"].shift(1)
    frame["pm2_5_lag_3"] = grouped["pm2_5_mean"].shift(2)
    frame["pm2_5_roll_3"] = grouped["pm2_5_mean"].transform(
        lambda values: values.rolling(3, min_periods=3).mean()
    )
    frame["pm2_5_roll_7"] = grouped["pm2_5_mean"].transform(
        lambda values: values.rolling(7, min_periods=7).mean()
    )
    frame["pm2_5_roll_7_std"] = grouped["pm2_5_mean"].transform(
        lambda values: values.rolling(7, min_periods=7).std()
    )
    frame[TARGET] = grouped["pm2_5_mean"].shift(-1)
    frame["target_date"] = frame["date"] + pd.Timedelta(days=1)
    frame["month_sin"] = np.sin(2 * np.pi * frame["date"].dt.month / 12)
    frame["month_cos"] = np.cos(2 * np.pi * frame["date"].dt.month / 12)
    day_of_year = frame["date"].dt.dayofyear
    frame["day_of_year_sin"] = np.sin(2 * np.pi * day_of_year / 365.25)
    frame["day_of_year_cos"] = np.cos(2 * np.pi * day_of_year / 365.25)
    required = NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET, "target_date"]
    return frame.dropna(subset=required).reset_index(drop=True)
