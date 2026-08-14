from __future__ import annotations

import json
from pathlib import Path

from report_template import build_research_report

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "AirWise_Report.pdf"
FIGURES = ROOT / "reports" / "figures"


def build_report() -> Path:
    metrics = json.loads((ROOT / "reports/model_metrics.json").read_text())
    sections = [
        {
            "title": "Project overview and problem statement",
            "paragraphs": [
                "AirWise estimates next-day daily mean PM2.5 for Delhi, Mumbai, and Hyderabad. I framed the project around a practical modelling problem: a time-series result can look impressive when nearby dates leak across a random split, but such a score does not represent a true future forecast.",
                "The project therefore uses chronological partitions, a strong persistence baseline, interpretable candidates, and a final unseen 2025 test period. The output is a forecasting experiment and not a health warning or regulatory measurement.",
            ],
        },
        {
            "title": "Data source and preparation",
            "paragraphs": [
                "I collected air-quality and historical weather fields from Open-Meteo for one representative coordinate per city. The processed panel contains 3,747 city-day records from 1 August 2022 through 31 December 2025.",
                "Hourly pollutant values were aggregated into daily means and maxima. I joined daily weather, created city-separated lags and rolling statistics, added cyclical time features, and shifted the target one day forward within each city. Raw downloads are excluded from Git while checksums and the processed panel are versioned.",
            ],
            "table": [
                ["Split", "Rows", "Purpose"],
                ["Training", "2,070", "Model fitting through June 2024"],
                ["Validation", "552", "Candidate selection from July to December 2024"],
                ["Test", "1,095", "One final evaluation on 2025"],
            ],
        },
        {
            "title": "Methodology and evaluation design",
            "paragraphs": [
                "Persistence predicts tomorrow with today's PM2.5 and is the required baseline. Ridge regression with two regularisation settings and histogram gradient boosting are compared using validation MAE only. Ridge with alpha 10 is then refit on training plus validation data.",
                "I report MAE, RMSE and R-squared for concentration error. A secondary threshold at 60 micrograms per cubic metre reports accuracy, precision, recall and F1. Permutation importance and city-level residual analysis explain where the shared model succeeds and fails.",
            ],
        },
        {
            "title": "End-to-end forecasting architecture",
            "paragraphs": [
                "The architecture separates hourly source collection, city-day aggregation, past-only feature engineering, chronological model selection and final holdout evaluation. Each stage writes a reviewable artefact before the next stage begins.",
                "Open-Meteo provides air-quality and weather inputs. Python and pandas form the daily panel, while scikit-learn owns preprocessing, candidate comparison, Ridge fitting and permutation importance. The 2025 holdout is read only for the final reported result.",
            ],
            "figure": FIGURES / "06_architecture.png",
            "caption": "Architecture diagram. AirWise technology and responsibility across the forecasting flow.",
            "explanation": [
                ["Stage design", "Hourly data becomes a daily city panel before lags and rolling features are generated within each city."],
                ["Leakage control", "Candidate choice occurs on the chronological validation period, not on 2025 test rows."],
                ["Evidence", "Predictions, model metrics, feature importance and figures remain versioned for independent inspection."],
            ],
        },
        {
            "title": "Automated forecasting test execution",
            "paragraphs": [
                "I ran the repository test suite after the report changes. Three tests passed. The checks verify chronological feature construction, exclusion of future values and the presence of the final model and evaluation assets.",
                "These checks detect pipeline leakage and missing deliverables. Forecast quality is evaluated separately with the 1,095-row holdout, because a passing unit test cannot establish predictive usefulness.",
            ],
            "figure": FIGURES / "07_test_execution.png",
            "caption": "Test execution evidence. Actual AirWise pytest execution for feature and repository contracts.",
            "explanation": [
                ["Execution", "Three tests passed in 0.52 seconds and no test failed."],
                ["Critical rule", "Lag and rolling features must be derived from dates earlier than the target date."],
                ["Boundary", "The tests do not replace monitoring for API changes, sensor bias or future atmospheric regimes."],
            ],
        },
        {
            "title": "Experiment 1: forecast trace",
            "paragraphs": [
                "This experiment compares the model's daily 2025 predictions with observed values for each city. A time trace reveals timing errors and sharp pollution changes that a single aggregate metric cannot show."
            ],
            "figure": FIGURES / "01_test_predictions.png",
            "caption": "Figure 1. Observed and predicted next-day PM2.5 during the 2025 test period.",
            "explanation": [
                [
                    "What I tested",
                    "Whether the selected model follows the direction and scale of unseen daily PM2.5 changes across all three cities.",
                ],
                [
                    "What the graph shows",
                    "The model tracks the broad seasonal pattern but smooths some abrupt peaks, especially in Delhi.",
                ],
                [
                    "Conclusion",
                    "The model is useful for next-day estimation, but individual high-pollution spikes remain a major error source.",
                ],
            ],
        },
        {
            "title": "Experiment 2: model comparison",
            "paragraphs": [
                "This experiment determines whether the selected model improves on persistence and whether a nonlinear candidate is justified."
            ],
            "figure": FIGURES / "02_model_comparison.png",
            "caption": "Figure 2. Validation MAE for the persistence baseline and three learned candidates.",
            "explanation": [
                [
                    "What I tested",
                    "Four candidates were compared on the same chronological validation period using MAE.",
                ],
                [
                    "What the graph shows",
                    "Ridge alpha 10 achieved the lowest validation MAE at 8.03, narrowly ahead of Ridge alpha 1.",
                ],
                [
                    "Conclusion",
                    "The simple regularised linear model was selected because it performed best without adding unnecessary complexity.",
                ],
            ],
        },
        {
            "title": "Experiment 3: feature influence",
            "paragraphs": [
                "Permutation importance measures the increase in test MAE after each feature is shuffled. This gives an interpretable view of which inputs the trained pipeline uses most strongly."
            ],
            "figure": FIGURES / "03_feature_importance.png",
            "caption": "Figure 3. Permutation importance measured on the final test period.",
            "explanation": [
                ["What I tested", "How sensitive test performance is to each model input."],
                [
                    "What the graph shows",
                    "Recent PM2.5 and related pollutant history dominate, with weather and seasonal variables providing smaller adjustments.",
                ],
                [
                    "Conclusion",
                    "The finding is consistent with a one-day horizon: current atmospheric conditions contain most of the predictable signal.",
                ],
            ],
        },
        {
            "title": "Experiment 4: residual analysis",
            "paragraphs": [
                "Residuals are actual minus predicted PM2.5. Plotting them against predictions tests whether error grows with concentration and whether cities show different behaviour."
            ],
            "figure": FIGURES / "04_residuals.png",
            "caption": "Figure 4. Test residuals by city and predicted concentration.",
            "explanation": [
                [
                    "What I tested",
                    "Whether errors are centred near zero and whether high predictions create larger misses.",
                ],
                [
                    "What the graph shows",
                    "Most residuals are near zero, but the spread expands at higher concentrations and is widest for Delhi.",
                ],
                [
                    "Conclusion",
                    "A future version should add calibrated uncertainty intervals and consider city-specific modelling for Delhi.",
                ],
            ],
        },
        {
            "title": "Experiment 5: city-level error",
            "paragraphs": [
                "Aggregate performance can hide unequal error across cities. I therefore calculated test MAE separately for Delhi, Mumbai, and Hyderabad."
            ],
            "figure": FIGURES / "05_city_error.png",
            "caption": "Figure 5. Mean absolute error on unseen 2025 rows for each city.",
            "explanation": [
                [
                    "What I tested",
                    "Whether one shared model performs consistently across the three metro areas.",
                ],
                [
                    "What the graph shows",
                    "Delhi MAE is 14.47, while Mumbai and Hyderabad are approximately 5.63 and 5.39.",
                ],
                [
                    "Conclusion",
                    "The aggregate score should not be presented as uniform performance; Delhi is the clear improvement priority.",
                ],
            ],
        },
        {
            "title": "Alert scenario error analysis",
            "paragraphs": [
                "The 60 micrograms per cubic metre threshold converts the continuous forecast into an alert-style scenario. I calculated the complete confusion matrix so recall can be interpreted beside false positives, false negatives and the number of below-threshold days.",
                "A false negative is a day where observed PM2.5 reaches the threshold but the forecast remains below it. A false positive is the opposite. Both counts remain visible because an aggregate F1 score does not show which error type dominates.",
            ],
            "figure": FIGURES / "08_alert_confusion.png",
            "caption": "Scenario evaluation. Alert confusion matrix on all 1,095 unseen 2025 city-day rows.",
            "explanation": [
                ["Scenario", "Observed and predicted concentrations are compared at the declared 60 micrograms per cubic metre threshold."],
                ["Error interpretation", "False negatives affect alert recall, while false positives reduce precision."],
                ["Use boundary", "This experiment evaluates model behaviour only and is not an operational health alert system."],
            ],
        },
        {
            "title": "Results and interpretation",
            "paragraphs": [
                f"On 1,095 unseen 2025 rows, Ridge alpha 10 achieved MAE {metrics['test']['mae']:.2f}, RMSE {metrics['test']['rmse']:.2f}, and R-squared {metrics['test']['r2']:.3f}. Persistence MAE was {metrics['persistence_test']['mae']:.2f}. The learned model therefore improves average error by about 4.7 percent.",
                f"Alert recall was {metrics['test']['alert_recall']:.3f} and alert F1 was {metrics['test']['alert_f1']:.3f}. Hyderabad had too few positive alert days for a meaningful city-level alert F1, so the reported zero is retained rather than hidden.",
            ],
        },
        {
            "title": "Limitations, reproducibility and responsible use",
            "paragraphs": [
                "The source provides atmospheric model output at one coordinate per city rather than a quality-controlled network of ground stations. Historical realised weather is cleaner than forecast-time weather. The model does not represent neighbourhood exposure, emission sources, or the complete Indian AQI.",
                "The repository includes acquisition, feature engineering, training, metrics, predictions, model artefacts, tests, and this report. Rebuilding the project reproduces the chronological split and all five figures. Production use would require station observations, forecast meteorology, rolling backtests, uncertainty intervals, drift monitoring, and expert review.",
            ],
        },
        {
            "title": "Conclusion",
            "paragraphs": [
                "I found that a compact Ridge model improves modestly on a strong persistence baseline for next day metro PM2.5. The result is useful because it combines honest temporal validation, interpretable evidence, and city level error analysis. A credible forecasting result is not defined by the largest score; it is defined by a defensible split, a relevant baseline, reproducible tests, and clear limitations."
            ],
        },
    ]
    return build_research_report(
        OUTPUT,
        "AirWise Metro Forecasting",
        "Divya Rachala",
        [
            "This report presents an end-to-end next-day PM2.5 forecasting study for Delhi, Mumbai, and Hyderabad. I constructed a reproducible daily panel from public air-quality and weather data, created time-safe lag and rolling features, compared learned models with a persistence baseline, and evaluated the selected model on an unseen 2025 test period.",
            "The selected Ridge model achieved a test MAE of 8.50 micrograms per cubic metre and R-squared of 0.851. Five experiments examine forecast traces, model selection, feature influence, residual behaviour, and city-level error. The findings show a modest improvement over persistence, with Delhi remaining the most difficult city.",
        ],
        "PM2.5 forecasting; temporal validation; Ridge regression; baseline comparison; error analysis",
        sections,
    )


if __name__ == "__main__":
    print(build_report())
