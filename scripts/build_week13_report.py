"""Build the Week 13 submission with its measured k6 figures."""

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build_academic_submission import main

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidencias/semana13"


def chart():
    with (EVIDENCE / "k6.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    image = Image.new("RGB", (1200, 600), "#f6f9fa")
    draw = ImageDraw.Draw(image)
    title = ImageFont.truetype("arial.ttf", 38)
    label = ImageFont.truetype("arial.ttf", 26)
    draw.text((45, 27), "Latencia p95 de las solicitudes k6", fill="#172b31", font=title)
    draw.text((45, 80), "Ensayos locales · milisegundos · muestras de distinto tamaño", fill="#526d74", font=label)
    maximum = max(float(row["p95_ms"]) for row in rows)
    for index, row in enumerate(rows):
        value = float(row["p95_ms"])
        y = 144 + index * 68
        width = int(670 * value / maximum)
        draw.text((45, y), row["scenario"], fill="#172b31", font=label)
        draw.rounded_rectangle((235, y, 235 + width, y + 30), radius=7, fill="#167c7e")
        draw.text((250 + width, y), f"{value:.2f} ms", fill="#172b31", font=label)
    image.save(EVIDENCE / "k6-p95.png")


if __name__ == "__main__":
    chart()
    main(
        source=ROOT / "docs/LOGISTECH_SEMANA_13_INFORME_FINAL.md",
        output=ROOT / "output/documents/LOGISTECH_SEMANA_13_INFORME_FINAL.docx",
        title="LogisTech 2.0 Semana 13",
        subtitle="Informe de avance de los entregables del 80 % y del 100 %",
        cover=True,
    )
