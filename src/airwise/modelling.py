from __future__ import annotations

import json
from dataclasses import dataclass

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from airwise.config import (
    ALERT_THRESHOLD,
    FIGURES_DIR,
    MODELS_DIR,
    REPORTS_DIR,
    TRAIN_END,
    VALIDATION_END,
)
from airwise.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET, pm25_category


@dataclass
class DatasetSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def temporal_split(features: pd.DataFrame) -> DatasetSplit:
    target_dates = pd.to_datetime(features["target_date"])
    train = features[target_dates <= TRAIN_END].copy()
    validation = features[(target_dates > TRAIN_END) & (target_dates <= VALIDATION_END)].copy()
    test = features[target_dates > VALIDATION_END].copy()
    if min(len(train), len(validation), len(test)) == 0:
        raise ValueError("Temporal split produced an empty partition")
    return DatasetSplit(train=train, validation=validation, test=test)


def _preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            (
                "city",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ],
        verbose_feature_names_out=False,
    )


def _pipeline(model) -> Pipeline:
    return Pipeline([("prepare", _preprocessor()), ("model", model)])


def regression_metrics(actual: pd.Series | np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    actual_array = np.asarray(actual)
    predicted_array = np.asarray(predicted)
    actual_alert = actual_array > ALERT_THRESHOLD
    predicted_alert = predicted_array > ALERT_THRESHOLD
    return {
        "mae": float(mean_absolute_error(actual_array, predicted_array)),
        "rmse": float(mean_squared_error(actual_array, predicted_array) ** 0.5),
        "r2": float(r2_score(actual_array, predicted_array)),
        "alert_accuracy": float(accuracy_score(actual_alert, predicted_alert)),
        "alert_precision": float(precision_score(actual_alert, predicted_alert, zero_division=0)),
        "alert_recall": float(recall_score(actual_alert, predicted_alert, zero_division=0)),
        "alert_f1": float(f1_score(actual_alert, predicted_alert, zero_division=0)),
    }


def _candidate_models() -> dict[str, Pipeline]:
    return {
        "ridge_alpha_1": _pipeline(Ridge(alpha=1.0)),
        "ridge_alpha_10": _pipeline(Ridge(alpha=10.0)),
        "hist_gradient_boosting": _pipeline(
            HistGradientBoostingRegressor(
                learning_rate=0.06,
                max_iter=300,
                max_leaf_nodes=20,
                min_samples_leaf=25,
                l2_regularization=1.0,
                random_state=42,
            )
        ),
    }


def _save_figures(
    results: pd.DataFrame,
    comparisons: dict[str, dict[str, float]],
    importance: pd.DataFrame,
) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    figure, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=False)
    for axis, (city, city_frame) in zip(axes, results.groupby("city"), strict=True):
        sample = city_frame.sort_values("target_date")
        axis.plot(sample["target_date"], sample["actual_pm2_5"], label="Actual", linewidth=1.4)
        axis.plot(
            sample["target_date"], sample["predicted_pm2_5"], label="Predicted", linewidth=1.2
        )
        axis.axhline(
            ALERT_THRESHOLD, color="#c94c4c", linestyle="--", linewidth=1, label="Alert threshold"
        )
        axis.set_title(city)
        axis.set_ylabel("PM2.5 µg/m³")
    axes[0].legend(ncol=3, loc="upper right")
    axes[-1].set_xlabel("Target date")
    figure.suptitle("2025 next-day PM2.5 predictions", fontsize=16, fontweight="bold")
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "01_test_predictions.png", dpi=180, bbox_inches="tight")
    plt.close(figure)

    labels = list(comparisons)
    mae_values = [comparisons[label]["mae"] for label in labels]
    figure, axis = plt.subplots(figsize=(9, 5))
    bars = axis.bar(
        labels, mae_values, color=["#8a9a9f", "#255f85", "#1f7a70", "#d79b2e"][: len(labels)]
    )
    axis.bar_label(bars, fmt="%.2f")
    axis.set_ylabel("Validation MAE (µg/m³; lower is better)")
    axis.set_title("Candidate model comparison")
    axis.tick_params(axis="x", rotation=15)
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "02_model_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(figure)

    top = importance.head(12).sort_values("importance_mean")
    figure, axis = plt.subplots(figsize=(9, 6))
    axis.barh(top["feature"], top["importance_mean"], color="#1f7a70")
    axis.set_xlabel("Increase in test MAE after permutation")
    axis.set_title("Permutation feature importance")
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "03_feature_importance.png", dpi=180, bbox_inches="tight")
    plt.close(figure)

    results = results.assign(residual=results["actual_pm2_5"] - results["predicted_pm2_5"])
    figure, axis = plt.subplots(figsize=(9, 5))
    for city, city_frame in results.groupby("city"):
        axis.scatter(
            city_frame["predicted_pm2_5"],
            city_frame["residual"],
            label=city,
            alpha=0.45,
            s=18,
        )
    axis.axhline(0, color="black", linewidth=1)
    axis.set_xlabel("Predicted PM2.5")
    axis.set_ylabel("Residual (actual - predicted)")
    axis.set_title("Test residuals by city")
    axis.legend()
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "04_residuals.png", dpi=180, bbox_inches="tight")
    plt.close(figure)

    city_error = (
        results.assign(absolute_error=lambda frame: frame["residual"].abs())
        .groupby("city", as_index=False)["absolute_error"]
        .mean()
        .sort_values("absolute_error", ascending=False)
    )
    figure, axis = plt.subplots(figsize=(9, 5))
    bars = axis.bar(city_error["city"], city_error["absolute_error"], color="#777777")
    axis.bar_label(bars, fmt="%.2f")
    axis.set_ylabel("Test MAE (µg/m³; lower is better)")
    axis.set_title("2025 error by city")
    axis.set_ylim(0, city_error["absolute_error"].max() * 1.18)
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "05_city_error.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def train_and_evaluate(features: pd.DataFrame) -> dict[str, object]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    split = temporal_split(features)
    feature_columns = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    candidates = _candidate_models()
    validation_results: dict[str, dict[str, float]] = {}

    persistence_predictions = split.validation["pm2_5_lag_1"].to_numpy()
    validation_results["persistence_baseline"] = regression_metrics(
        split.validation[TARGET], persistence_predictions
    )

    for name, pipeline in candidates.items():
        pipeline.fit(split.train[feature_columns], split.train[TARGET])
        validation_results[name] = regression_metrics(
            split.validation[TARGET], pipeline.predict(split.validation[feature_columns])
        )

    best_name = min(candidates, key=lambda name: validation_results[name]["mae"])
    development = pd.concat([split.train, split.validation], ignore_index=True)
    best_model = _candidate_models()[best_name]
    best_model.fit(development[feature_columns], development[TARGET])
    test_predictions = best_model.predict(split.test[feature_columns])
    test_metrics = regression_metrics(split.test[TARGET], test_predictions)
    baseline_test_metrics = regression_metrics(split.test[TARGET], split.test["pm2_5_lag_1"])

    scored = split.test[["target_date", "city", TARGET, "pm2_5_lag_1"]].copy()
    scored = scored.rename(
        columns={TARGET: "actual_pm2_5", "pm2_5_lag_1": "persistence_prediction"}
    )
    scored["predicted_pm2_5"] = test_predictions
    scored["actual_category"] = scored["actual_pm2_5"].map(pm25_category)
    scored["predicted_category"] = scored["predicted_pm2_5"].map(pm25_category)
    scored.to_csv(REPORTS_DIR / "test_predictions_2025.csv", index=False, date_format="%Y-%m-%d")

    permutation = permutation_importance(
        best_model,
        split.test[feature_columns],
        split.test[TARGET],
        scoring="neg_mean_absolute_error",
        n_repeats=8,
        random_state=42,
        n_jobs=-1,
    )
    importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance_mean": permutation.importances_mean,
            "importance_std": permutation.importances_std,
        }
    ).sort_values("importance_mean", ascending=False)
    importance.to_csv(REPORTS_DIR / "feature_importance.csv", index=False)

    city_metrics = {
        city: regression_metrics(group["actual_pm2_5"], group["predicted_pm2_5"])
        for city, group in scored.groupby("city")
    }
    payload: dict[str, object] = {
        "selected_model": best_name,
        "target": "next-day daily mean PM2.5 (µg/m³)",
        "alert_threshold": ALERT_THRESHOLD,
        "split_rows": {
            "train": len(split.train),
            "validation": len(split.validation),
            "test": len(split.test),
        },
        "validation": validation_results,
        "test": test_metrics,
        "persistence_test": baseline_test_metrics,
        "test_by_city": city_metrics,
    }
    (REPORTS_DIR / "model_metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    joblib.dump(best_model, MODELS_DIR / "air_quality_model.joblib")
    _save_figures(scored, validation_results, importance)
    return payload
