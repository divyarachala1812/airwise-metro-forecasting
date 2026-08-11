from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "India_Metro_Air_Quality_Forecasting_Report.pdf"
FIGURES = ROOT / "reports" / "figures"
METRICS_PATH = ROOT / "reports" / "model_metrics.json"

NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2E6F95")
TEAL = colors.HexColor("#2A9D8F")
SAFFRON = colors.HexColor("#F4A261")
LIGHT = colors.HexColor("#EEF4F6")
INK = colors.HexColor("#24323D")
MUTED = colors.HexColor("#60717C")

BASE = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "CoverTitle",
    parent=BASE["Title"],
    fontName="Helvetica-Bold",
    fontSize=28,
    leading=34,
    textColor=colors.white,
    alignment=TA_CENTER,
    spaceAfter=18,
)
SUBTITLE = ParagraphStyle(
    "CoverSubtitle",
    parent=BASE["BodyText"],
    fontName="Helvetica",
    fontSize=13,
    leading=19,
    textColor=colors.HexColor("#D6E6EC"),
    alignment=TA_CENTER,
)
H1 = ParagraphStyle(
    "PageTitle",
    parent=BASE["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=24,
    textColor=NAVY,
    spaceAfter=12,
)
H2 = ParagraphStyle(
    "SectionTitle",
    parent=BASE["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=16,
    textColor=BLUE,
    spaceBefore=6,
    spaceAfter=6,
)
BODY = ParagraphStyle(
    "Body",
    parent=BASE["BodyText"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=13.5,
    textColor=INK,
    spaceAfter=8,
)
SMALL = ParagraphStyle(
    "Small",
    parent=BODY,
    fontSize=8.2,
    leading=10.5,
    textColor=MUTED,
)


def report_table(rows: list[list[str]], widths: list[float]) -> Table:
    prepared = [[Paragraph(str(cell), SMALL) for cell in row] for row in rows]
    table = Table(prepared, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), LIGHT),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8C8CE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def bullets(items: list[str]) -> list[Paragraph]:
    return [Paragraph(f"<font color='#2A9D8F'>●</font> {item}", BODY) for item in items]


def scaled_image(path: Path, width: float, height: float) -> Image:
    image = Image(str(path))
    image._restrictSize(width, height)
    return image


def decorate_page(pdf_canvas, doc) -> None:
    page = doc.page
    width, height = A4
    pdf_canvas.saveState()
    if page == 1:
        pdf_canvas.setFillColor(NAVY)
        pdf_canvas.rect(0, 0, width, height, fill=1, stroke=0)
        pdf_canvas.setFillColor(SAFFRON)
        pdf_canvas.rect(28 * mm, height - 45 * mm, 45 * mm, 2.5 * mm, fill=1, stroke=0)
    else:
        pdf_canvas.setFillColor(NAVY)
        pdf_canvas.rect(0, height - 16 * mm, width, 16 * mm, fill=1, stroke=0)
        pdf_canvas.setFillColor(colors.white)
        pdf_canvas.setFont("Helvetica-Bold", 8.5)
        pdf_canvas.drawString(18 * mm, height - 10.5 * mm, "INDIA METRO AIR QUALITY FORECASTING")
        pdf_canvas.setFillColor(MUTED)
        pdf_canvas.setFont("Helvetica", 8)
        pdf_canvas.drawString(18 * mm, 11 * mm, "Divya Rachala | Data Science Portfolio")
        pdf_canvas.drawRightString(width - 18 * mm, 11 * mm, f"Page {page} of 10")
    pdf_canvas.restoreState()


def build_report() -> Path:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    test = metrics["test"]
    baseline = metrics["persistence_test"]
    city = metrics["test_by_city"]

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=23 * mm,
        bottomMargin=18 * mm,
        title="India Metro Air Quality Forecasting",
        author="Divya Rachala",
        subject="Machine learning portfolio project report",
    )
    story = []

    story.extend(
        [
            Spacer(1, 62 * mm),
            Paragraph("India Metro<br/>Air Quality Forecasting", TITLE),
            Paragraph(
                "Next-day PM2.5 modelling for Delhi, Mumbai, and Hyderabad",
                SUBTITLE,
            ),
            Spacer(1, 25 * mm),
            report_table(
                [
                    ["Portfolio summary", "Verified result"],
                    ["Data", "3,747 city-day records from August 2022 to December 2025"],
                    ["Model", "Ridge regression with alpha 10 and chronological validation"],
                    ["Final test", "MAE 8.50 ug/m3, R2 0.851, alert recall 0.871"],
                    ["Author", "Divya Rachala | August 2026"],
                ],
                [48 * mm, 100 * mm],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Executive brief", H1),
            Paragraph(
                "This project estimates the next day's city-level mean PM2.5 using current and historical pollution, weather, city, and seasonal signals. It is a compact, interview-ready machine learning case study rather than a production alerting system.",
                BODY,
            ),
            report_table(
                [
                    ["Decision", "Evidence"],
                    ["Selected model", "Ridge alpha 10, chosen on late-2024 validation MAE"],
                    ["Final test", "1,095 unseen city-day rows from calendar year 2025"],
                    ["Accuracy", f"MAE {test['mae']:.2f} ug/m3 and R2 {test['r2']:.3f}"],
                    ["Baseline", f"Persistence MAE {baseline['mae']:.2f} ug/m3"],
                    ["Alert view", f"Recall {test['alert_recall']:.3f} at 60 ug/m3"],
                ],
                [45 * mm, 103 * mm],
            ),
            Spacer(1, 5 * mm),
            Paragraph("Portfolio value", H2),
            *bullets(
                [
                    "Prevents future information from leaking into training.",
                    "Compares a learned model with a strong persistence baseline.",
                    "Reports city-level error instead of hiding it behind one aggregate score.",
                    "Connects model evidence to a responsible-use boundary.",
                ]
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Problem framing and stakeholders", H1),
            Paragraph(
                "The analytical question is deliberately narrow: how accurately can a compact model estimate tomorrow's mean PM2.5 for three Indian metros when today's pollution and weather are known? A continuous target preserves more information than a category label.",
                BODY,
            ),
            report_table(
                [
                    ["Reviewer", "Question answered"],
                    ["Data scientist", "Was leakage prevented and was the baseline credible?"],
                    ["Environmental analyst", "Which cities and conditions drive the error?"],
                    [
                        "Hiring manager",
                        "Can the model choice and limitations be explained clearly?",
                    ],
                    ["Engineer", "Can the data, features, model, and evidence be reproduced?"],
                ],
                [43 * mm, 105 * mm],
            ),
            Spacer(1, 5 * mm),
            Paragraph("Out of scope", H2),
            *bullets(
                [
                    "Neighbourhood exposure estimates or CPCB regulatory reporting.",
                    "Health advice, emergency alerts, or pollution-causality claims.",
                    "A claim that atmospheric model fields equal audited station observations.",
                ]
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Data, provenance, and analytical grain", H1),
            Paragraph(
                "Open-Meteo air-quality and historical-weather APIs provide the reproducible source. Pollutants originate from Copernicus Atmosphere Monitoring Service model output. Raw JSON stays local; checksums and a versioned city-day panel provide traceability.",
                BODY,
            ),
            report_table(
                [
                    ["Attribute", "Value"],
                    ["Cities", "Delhi, Mumbai, Hyderabad"],
                    ["Coverage", "2022-08-01 through 2025-12-31"],
                    ["Processed grain", "One city and date"],
                    ["Rows", "3,747 before feature-window exclusions"],
                    ["Pollutants", "PM2.5, PM10, nitrogen dioxide, ozone"],
                    ["Weather", "Temperature, humidity, rain, wind speed, wind gust"],
                    ["Timezone", "Asia/Kolkata"],
                ],
                [43 * mm, 105 * mm],
            ),
            Spacer(1, 5 * mm),
            Paragraph(
                "One representative coordinate per city makes the project reproducible but cannot represent roadside, industrial, residential, and suburban variation. The report carries this limitation into every interpretation.",
                BODY,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Feature engineering and leakage control", H1),
            report_table(
                [
                    ["Feature family", "Examples", "Control"],
                    [
                        "Pollution history",
                        "Current, lags, 3-day and 7-day rolls",
                        "Grouped within city",
                    ],
                    ["Related pollutants", "PM10, NO2, ozone", "Current day or earlier"],
                    ["Weather", "Temperature, humidity, rain, wind", "Joined by city and date"],
                    ["Seasonality", "Month and day-of-year cycles", "Cyclical encoding"],
                    ["Geography", "City indicator", "One-hot encoding"],
                ],
                [39 * mm, 65 * mm, 44 * mm],
            ),
            Spacer(1, 6 * mm),
            Paragraph("Pipeline sequence", H2),
            *bullets(
                [
                    "Aggregate hourly pollution to a daily city panel.",
                    "Join weather at the same city-date grain.",
                    "Create lags and rolling windows independently within each city.",
                    "Shift the target one day forward within city.",
                    "Split chronologically before model selection or evaluation.",
                ]
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Validation and model selection", H1),
            Paragraph(
                "Training ends on 30 June 2024, validation covers July through December 2024, and the final test is calendar year 2025. Candidate choice uses validation MAE only. The selected model is refit on training plus validation data.",
                BODY,
            ),
            scaled_image(FIGURES / "02_model_comparison.png", 148 * mm, 105 * mm),
            Spacer(1, 4 * mm),
            Paragraph(
                "Ridge alpha 10 wins by a narrow validation margin. The simpler model improves interpretability without claiming a dramatic advantage over persistence.",
                BODY,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Final test performance", H1),
            report_table(
                [
                    ["Metric", "Ridge", "Persistence"],
                    ["MAE", f"{test['mae']:.2f}", f"{baseline['mae']:.2f}"],
                    ["RMSE", f"{test['rmse']:.2f}", f"{baseline['rmse']:.2f}"],
                    ["R2", f"{test['r2']:.3f}", f"{baseline['r2']:.3f}"],
                    [
                        "Alert recall",
                        f"{test['alert_recall']:.3f}",
                        f"{baseline['alert_recall']:.3f}",
                    ],
                    ["Alert F1", f"{test['alert_f1']:.3f}", f"{baseline['alert_f1']:.3f}"],
                ],
                [58 * mm, 45 * mm, 45 * mm],
            ),
            Spacer(1, 5 * mm),
            scaled_image(FIGURES / "01_test_predictions.png", 148 * mm, 100 * mm),
            Spacer(1, 3 * mm),
            Paragraph(
                "The learned model improves MAE by about 4.7 percent. Persistence remains strong, which is credible for a next-day target dominated by recent conditions.",
                BODY,
            ),
            PageBreak(),
        ]
    )

    importance = scaled_image(FIGURES / "03_feature_importance.png", 70 * mm, 74 * mm)
    residuals = scaled_image(FIGURES / "04_residuals.png", 70 * mm, 74 * mm)
    story.extend(
        [
            Paragraph("Explainability and city-level error", H1),
            report_table(
                [
                    ["City", "MAE", "R2", "Alert F1"],
                    [
                        "Delhi",
                        f"{city['Delhi']['mae']:.2f}",
                        f"{city['Delhi']['r2']:.3f}",
                        f"{city['Delhi']['alert_f1']:.3f}",
                    ],
                    [
                        "Mumbai",
                        f"{city['Mumbai']['mae']:.2f}",
                        f"{city['Mumbai']['r2']:.3f}",
                        f"{city['Mumbai']['alert_f1']:.3f}",
                    ],
                    [
                        "Hyderabad",
                        f"{city['Hyderabad']['mae']:.2f}",
                        f"{city['Hyderabad']['r2']:.3f}",
                        f"{city['Hyderabad']['alert_f1']:.3f}",
                    ],
                ],
                [58 * mm, 30 * mm, 30 * mm, 30 * mm],
            ),
            Spacer(1, 5 * mm),
            Table([[importance, residuals]], colWidths=[74 * mm, 74 * mm]),
            Spacer(1, 5 * mm),
            Paragraph(
                "Delhi drives most of the remaining absolute error. Hyderabad rarely crosses the threshold in 2025, so its zero alert F1 is exposed rather than hidden behind aggregate performance.",
                BODY,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Limitations and responsible interpretation", H1),
            report_table(
                [
                    ["Limitation", "Why it matters", "Improvement"],
                    [
                        "Modelled source",
                        "Not audited station observations",
                        "Add CPCB station data",
                    ],
                    ["One point per city", "No within-city variation", "Build a spatial panel"],
                    ["Realised weather", "Cleaner than forecast inputs", "Use issued forecasts"],
                    ["No intervals", "Point estimates hide risk", "Calibrate uncertainty"],
                    ["Sparse alerts", "City F1 can be unstable", "Use longer backtests"],
                ],
                [39 * mm, 55 * mm, 54 * mm],
            ),
            Spacer(1, 6 * mm),
            Paragraph("Responsible-use boundary", H2),
            *bullets(
                [
                    "Do not use this model for health decisions or emergency warnings.",
                    "Do not present 60 ug/m3 as the complete Indian AQI.",
                    "Do not generalise one-coordinate results to every neighbourhood.",
                    "Treat the output as a reproducible modelling study and baseline comparison.",
                ]
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Paragraph("Reproducibility, evidence, and interview value", H1),
            report_table(
                [
                    ["Step", "Command or artifact"],
                    ["Environment", "uv sync"],
                    ["Acquire", "uv run python scripts/download_data.py"],
                    ["Train", "uv run python scripts/train_model.py"],
                    ["Verify", "uv run pytest -q and uv run ruff check ."],
                    ["Evidence", "reports/model_metrics.json and reports/figures/"],
                    ["Documentation", "docs/dataset.md, model-card.md, and project-report.md"],
                ],
                [42 * mm, 106 * mm],
            ),
            Spacer(1, 5 * mm),
            Paragraph("Skills demonstrated", H2),
            *bullets(
                [
                    "API acquisition, checksum provenance, pandas features, and time-aware splits.",
                    "Scikit-learn pipelines, model selection, baseline comparison, and importance.",
                    "Regression and threshold metrics, error analysis, tests, and documentation.",
                ]
            ),
            Paragraph("Primary sources", H2),
            *bullets(
                [
                    "Open-Meteo Air Quality and Historical Weather APIs.",
                    "Copernicus Atmosphere Monitoring Service attribution through Open-Meteo.",
                    "Central Pollution Control Board national AQI documentation.",
                ]
            ),
        ]
    )

    doc.build(story, onFirstPage=decorate_page, onLaterPages=decorate_page)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return OUTPUT


if __name__ == "__main__":
    build_report()
