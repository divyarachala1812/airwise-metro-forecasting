from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import requests

from airwise.config import (
    AIR_QUALITY_VARIABLES,
    CITIES,
    END_DATE,
    PROCESSED_DIR,
    RAW_DIR,
    START_DATE,
    TIMEZONE,
    WEATHER_VARIABLES,
)

AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"


def _request_json(url: str, params: dict[str, object]) -> dict:
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(payload.get("reason", "Open-Meteo returned an error"))
    return payload


def _write_json(path: Path, payload: dict) -> str:
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _air_daily(payload: dict, city: str) -> pd.DataFrame:
    frame = pd.DataFrame(payload["hourly"])
    frame["time"] = pd.to_datetime(frame["time"])
    frame["date"] = frame["time"].dt.normalize()
    aggregations = {
        "pm2_5": ["mean", "max"],
        "pm10": ["mean", "max"],
        "nitrogen_dioxide": ["mean", "max"],
        "ozone": ["mean", "max"],
    }
    daily = frame.groupby("date", as_index=False).agg(aggregations)
    daily.columns = [
        "date" if column[0] == "date" else f"{column[0]}_{column[1]}" for column in daily.columns
    ]
    daily.insert(1, "city", city)
    return daily


def _weather_daily(payload: dict, city: str) -> pd.DataFrame:
    frame = pd.DataFrame(payload["daily"])
    frame["date"] = pd.to_datetime(frame["time"])
    frame = frame.drop(columns="time")
    frame.insert(1, "city", city)
    return frame


def download_and_prepare() -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    combined: list[pd.DataFrame] = []
    manifest: dict[str, object] = {
        "source": "Open-Meteo Air Quality API and Historical Weather API",
        "period": {"start": START_DATE, "end": END_DATE},
        "licence": "CC BY 4.0",
        "files": [],
    }

    for city, coordinates in CITIES.items():
        common = {
            **coordinates,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "timezone": TIMEZONE,
        }
        air_payload = _request_json(
            AIR_URL,
            {**common, "hourly": ",".join(AIR_QUALITY_VARIABLES)},
        )
        weather_payload = _request_json(
            WEATHER_URL,
            {**common, "daily": ",".join(WEATHER_VARIABLES)},
        )
        safe_city = city.lower()
        air_path = RAW_DIR / f"{safe_city}_air_quality.json"
        weather_path = RAW_DIR / f"{safe_city}_weather.json"
        for path, payload, kind in (
            (air_path, air_payload, "air_quality"),
            (weather_path, weather_payload, "weather"),
        ):
            digest = _write_json(path, payload)
            manifest["files"].append(
                {"city": city, "kind": kind, "path": path.name, "sha256": digest}
            )

        city_daily = _air_daily(air_payload, city).merge(
            _weather_daily(weather_payload, city), on=["date", "city"], how="inner"
        )
        combined.append(city_daily)

    daily = pd.concat(combined, ignore_index=True).sort_values(["city", "date"])
    output_path = PROCESSED_DIR / "india_metro_daily_air_quality.csv"
    daily.to_csv(output_path, index=False, date_format="%Y-%m-%d")
    manifest["rows"] = len(daily)
    manifest["cities"] = sorted(CITIES)
    manifest["processed_file"] = output_path.name
    (RAW_DIR / "source_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return daily
