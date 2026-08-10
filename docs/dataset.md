# Dataset and provenance

## Sources

The project downloads two public sources for the coordinates of Delhi, Mumbai, and Hyderabad:

1. **Open-Meteo Air Quality API** — PM2.5, PM10, nitrogen dioxide, and ozone. For India, the historical global air-quality series is based on Copernicus Atmosphere Monitoring Service model output.
2. **Open-Meteo Historical Weather API** — daily mean temperature, mean relative humidity, precipitation, mean wind speed, and maximum wind gust.

Source documentation:

- https://open-meteo.com/en/docs/air-quality-api
- https://open-meteo.com/en/docs/historical-weather-api
- https://open-meteo.com/en/license
- https://cpcb.nic.in/displaypdf.php?id=bmF0aW9uYWwtYWlyLXF1YWxpdHktaW5kZXgvQWJvdXRfQVFJLnBkZg==

Open-Meteo API data are offered under CC BY 4.0. The raw files are downloaded locally and excluded from version control; `data/raw/source_manifest.json` records filenames and SHA-256 hashes after acquisition.

## Coverage

| Attribute | Value |
|---|---|
| Cities | Delhi, Mumbai, Hyderabad |
| Coordinates | One representative coordinate per city |
| Start | 2022-08-01 |
| End | 2025-12-31 |
| Processed grain | One city-day |
| Processed rows | 3,747 before feature-window exclusions |
| Timezone | Asia/Kolkata |

The start date follows the availability window documented for the CAMS global atmospheric-composition series.

## Variables

Hourly pollutant fields are aggregated to daily mean and daily maximum:

- PM2.5;
- PM10;
- nitrogen dioxide;
- ozone.

Daily weather fields are retained at source grain:

- mean temperature at 2 m;
- mean relative humidity at 2 m;
- precipitation sum;
- mean wind speed at 10 m;
- maximum wind gust at 10 m.

## Important limitation

These values are spatially complete model outputs for a city coordinate. They are not observations from every monitoring station in a city and should not be described as audited CPCB measurements. This design makes the project reproducible, but it also means local roadside conditions and within-city variation are not represented.

The binary alert threshold is derived from the CPCB 24-hour PM2.5 concentration bands. The project does not calculate the complete Indian AQI, whose final value depends on the worst sub-index across multiple pollutants and specific averaging rules.
