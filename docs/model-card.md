# Model card

## Model overview

| Item | Description |
|---|---|
| Model | Ridge regression with alpha 10 |
| Task | Predict next-day daily mean PM2.5 |
| Geography | Delhi, Mumbai, Hyderabad |
| Training window | 2022-08 through 2024-06 |
| Validation window | 2024-07 through 2024-12 |
| Test window | 2025-01 through 2025-12 |
| Training + validation rows | 2,622 |
| Test rows | 1,095 |

## Input features

The model uses:

- current-day, two-day, and three-day PM2.5 values;
- three-day and seven-day PM2.5 rolling statistics;
- PM10, nitrogen dioxide, and ozone daily summaries;
- temperature, relative humidity, precipitation, wind speed, and wind gust;
- cyclical month and day-of-year features;
- one-hot encoded city.

All model inputs describe the current day or earlier. The target is shifted one day forward within each city.

## Selection process

The candidates were:

1. persistence baseline — tomorrow equals today;
2. Ridge regression, alpha 1;
3. Ridge regression, alpha 10;
4. histogram gradient boosting.

The model with the lowest validation MAE was selected before the 2025 test set was evaluated. Ridge alpha 10 achieved 8.03 µg/m³ validation MAE, narrowly ahead of Ridge alpha 1 and histogram gradient boosting.

## Test performance

| Metric | Result |
|---|---:|
| MAE | 8.496 µg/m³ |
| RMSE | 13.453 µg/m³ |
| R² | 0.851 |
| Alert accuracy | 0.914 |
| Alert precision | 0.828 |
| Alert recall | 0.871 |
| Alert F1 | 0.849 |

The learned model reduces test MAE from 8.918 to 8.496 µg/m³ against persistence. The improvement is real but not large. Yesterday's concentration remains a strong predictor, and operational claims should reflect that.

## City-level behaviour

| City | MAE | R² | Alert F1 |
|---|---:|---:|---:|
| Delhi | 14.47 | 0.707 | 0.883 |
| Mumbai | 5.63 | 0.812 | 0.774 |
| Hyderabad | 5.39 | 0.795 | 0.000* |

\*Hyderabad contains too few positive alert days in the 2025 test period for a meaningful alert score. Returning zero exposes that evaluation limitation instead of hiding it behind aggregate accuracy.

## Intended use

- experimental next day forecasting;
- comparison of a learned model with a temporal baseline;
- investigation of feature influence and city-level error;
1. explanation of validation design and model limitations.

## Out-of-scope use

- health advice;
- regulatory or CPCB reporting;
- automated public warnings;
- neighbourhood-level exposure estimates;
- claims about pollution sources or causality.

## Risks and next steps

- Replace modelled fields with quality-controlled station observations for operational use.
- Use forecast-time weather inputs rather than historical realised weather when simulating a true morning-ahead forecast.
- Add calibrated prediction intervals so users see uncertainty, especially in Delhi.
- Monitor seasonal drift and retrain only through a documented schedule.
- Evaluate precision-recall curves by city before any alerting use.
