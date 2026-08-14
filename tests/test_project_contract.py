from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_project_assets_exist() -> None:
    required = [
        "README.md",
        "docs/dataset.md",
        "docs/model-card.md",
        "reports/model_metrics.json",
        "reports/AirWise_Metro_Forecasting_Report.pdf",
        "reports/test_predictions_2025.csv",
        "reports/figures/01_test_predictions.png",
        "scripts/build_report.py",
    ]
    assert all((ROOT / path).exists() for path in required)
