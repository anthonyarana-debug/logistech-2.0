"""Build the Week 13 submission with its measured k6 figures."""

import csv
from pathlib import Path

from build_academic_submission import main
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidencias/semana13-cierre"


def chart():
    with (EVIDENCE / "capacity.csv").open(encoding="utf-8", newline="") as stream:
        rows = [
            row
            for row in csv.DictReader(stream)
            if row["scenario"] == "get" and row["completed"] == row["requested"]
        ]
    rows.sort(key=lambda row: (int(row["requested"]), int(row["vus"])))
    image = Image.new("RGB", (1200, 160 + 68 * len(rows)), "#f6f9fa")
    draw = ImageDraw.Draw(image)
    title = ImageFont.truetype("arial.ttf", 38)
    label = ImageFont.truetype("arial.ttf", 26)
    draw.text(
        (45, 27), "Latencia p95 de consultas GET paginadas", fill="#172b31", font=title
    )
    draw.text(
        (45, 80),
        "Ensayos locales · línea de aceptación: 500 ms",
        fill="#526d74",
        font=label,
    )
    maximum = max(500, *(float(row["p95_ms"]) for row in rows))
    for index, row in enumerate(rows):
        value = float(row["p95_ms"])
        y = 144 + index * 68
        width = int(670 * value / maximum)
        draw.text(
            (45, y), f"{row['requested']} / {row['vus']} VU", fill="#172b31", font=label
        )
        draw.rounded_rectangle(
            (265, y, 265 + width, y + 30),
            radius=7,
            fill="#167c7e" if value < 500 else "#b33f35",
        )
        draw.text((280 + width, y), f"{value:.2f} ms", fill="#172b31", font=label)
    threshold = 265 + int(670 * 500 / maximum)
    draw.line(
        (threshold, 130, threshold, 140 + len(rows) * 68), fill="#526d74", width=2
    )
    image.save(EVIDENCE / "capacity-p95.png")


if __name__ == "__main__":
    chart()
    main(
        source=ROOT / "docs/LOGISTECH_SEMANA_13_INFORME_FINAL.md",
        output=ROOT / "output/documents/LOGISTECH_SEMANA_13_INFORME_FINAL.docx",
        title="LogisTech 2.0 Semana 13",
        subtitle="Informe de avance de los entregables del 80 % y del 100 %",
        cover=True,
        cover_lines=(
            "[Sede y ciudad por confirmar]",
            "[Integrantes por confirmar]",
            "[Docente por confirmar]",
            "11 de noviembre de 2026",
        ),
    )
