import pandas as pd

from airwise.features import TARGET, build_features, pm25_category


def test_pm25_categories_follow_cpcb_breakpoints() -> None:
    assert pm25_category(30) == "Good"
    assert pm25_category(60) == "Satisfactory"
    assert pm25_category(61) == "Moderately polluted"
    assert pm25_category(121) == "Very poor"
    assert pm25_category(251) == "Severe"


def test_next_day_target_is_shifted_within_city() -> None:
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    frame = pd.DataFrame(
        {
            "date": dates,
            "city": "Delhi",
            "pm2_5_mean": range(10, 20),
            "pm2_5_max": range(20, 30),
            "pm10_mean": range(30, 40),
            "pm10_max": range(40, 50),
            "nitrogen_dioxide_mean": 20,
            "nitrogen_dioxide_max": 30,
            "ozone_mean": 40,
            "ozone_max": 50,
            "temperature_2m_mean": 25,
            "relative_humidity_2m_mean": 60,
            "precipitation_sum": 0,
            "wind_speed_10m_mean": 10,
            "wind_gusts_10m_max": 20,
        }
    )
    featured = build_features(frame)
    first = featured.iloc[0]
    assert first[TARGET] == 17
    assert first["pm2_5_lag_1"] == 16
    assert first["target_date"] == pd.Timestamp("2024-01-08")
