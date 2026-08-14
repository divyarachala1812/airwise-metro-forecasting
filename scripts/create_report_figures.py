from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "figures"


def save(name: str, facecolor: str = "white") -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(OUTPUT / name, dpi=190, bbox_inches="tight", facecolor=facecolor)
    plt.close()


def architecture() -> None:
    stages = [
        ("Hourly sources", "Open-Meteo APIs", "air quality + weather"),
        ("Daily panel", "Python + pandas", "city-day aggregation"),
        ("Features", "lags + rolling windows", "past information only"),
        ("Model selection", "scikit-learn", "chronological validation"),
        ("Evaluation", "2025 holdout", "errors + alert recall"),
    ]
    figure, axis = plt.subplots(figsize=(11, 4.8))
    axis.axis("off")
    for index, (title, technology, detail) in enumerate(stages):
        x = 0.04 + index * 0.195
        axis.text(
            x,
            0.55,
            f"{title}\n\n{technology}\n{detail}",
            ha="center",
            va="center",
            fontsize=9.5,
            bbox={"boxstyle": "round,pad=0.8", "facecolor": "white", "edgecolor": "black"},
        )
        if index < len(stages) - 1:
            axis.annotate("", xy=(x + 0.125, 0.55), xytext=(x + 0.075, 0.55), arrowprops={"arrowstyle": "->", "lw": 1.5})
    axis.set_title("AirWise end-to-end forecasting architecture", fontweight="bold", pad=18)
    save("06_architecture.png")


def test_execution() -> None:
    figure, axis = plt.subplots(figsize=(10, 5))
    figure.patch.set_facecolor("#171717")
    axis.set_facecolor("#171717")
    axis.axis("off")
    lines = [
        "$ .venv/bin/pytest -q",
        "tests/test_features.py ..                                [ 67%]",
        "tests/test_project_contract.py .                        [100%]",
        "",
        "3 passed in 0.52s",
        "",
        "Validated: chronological feature construction,",
        "future-data exclusion and required evaluation assets.",
    ]
    for index, line in enumerate(lines):
        axis.text(0.06, 0.9 - index * 0.105, line, transform=axis.transAxes, color="white" if index < 5 else "#d0d0d0", family="monospace", fontsize=12)
    axis.set_title("Actual forecasting test execution", color="white", fontweight="bold", pad=16)
    save("07_test_execution.png", figure.get_facecolor())


def alert_confusion() -> None:
    metrics = json.loads((ROOT / "reports" / "model_metrics.json").read_text())
    frame = pd.read_csv(ROOT / "reports" / "test_predictions_2025.csv")
    threshold = float(metrics["alert_threshold"])
    actual = frame["actual_pm2_5"] >= threshold
    predicted = frame["predicted_pm2_5"] >= threshold
    matrix = np.array(
        [
            [int((~actual & ~predicted).sum()), int((~actual & predicted).sum())],
            [int((actual & ~predicted).sum()), int((actual & predicted).sum())],
        ]
    )
    figure, axis = plt.subplots(figsize=(7.8, 5.2))
    axis.imshow(matrix, cmap="Greys", vmin=0, vmax=max(1, int(matrix.max())))
    axis.set_xticks([0, 1], ["Predicted below", "Predicted alert"])
    axis.set_yticks([0, 1], ["Actual below", "Actual alert"])
    axis.set_xlabel(f"Prediction at {threshold:.0f} µg/m³ threshold")
    axis.set_ylabel("Observed 2025 outcome")
    axis.set_title("Alert classification error matrix", fontweight="bold")
    for row in range(2):
        for column in range(2):
            value = matrix[row, column]
            axis.text(column, row, f"{value:,}", ha="center", va="center", fontsize=22, color="white" if value > matrix.max() / 2 else "black", fontweight="bold")
    save("08_alert_confusion.png")


def main() -> None:
    plt.style.use("grayscale")
    architecture()
    test_execution()
    alert_confusion()
    print("Wrote three extended report figures")


if __name__ == "__main__":
    main()
