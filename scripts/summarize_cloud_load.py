"""Junta los resultados de load/nube.js en CSV, tabla Markdown y HTML con gráficas.

Uso: python scripts/summarize_cloud_load.py docs/evidencias/semana13-nube
Solo usa la biblioteca estándar; las gráficas son SVG en línea (se imprimen bien en B/N).
"""

import csv
import html
import json
import sys
from pathlib import Path

COLUMNS = [
    ("fecha", "Fecha UTC"), ("escenario", "Escenario"), ("objetivo", "Objetivo"),
    ("completadas", "Hechas"), ("vus", "VU"), ("tiempo_max", "T. máx"),
    ("duracion_s", "Duración s"), ("http", "HTTP"), ("req_s", "Req/s"),
    ("avg_ms", "Prom ms"), ("p95_ms", "p95 ms"), ("p99_ms", "p99 ms"),
    ("error_pct", "Error %"), ("usuarios_creados", "Creados BD"), ("cuota_429", "429"),
    ("servidor_5xx", "5xx"), ("red_timeout", "Timeout"), ("resultado", "Resultado"),
]


def fmt(value):
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def bars(rows, key, title, unit):
    width, bar_h, gap, label_w = 640, 22, 8, 170
    peak = max((float(r[key]) for r in rows), default=0) or 1
    height = 40 + len(rows) * (bar_h + gap)
    parts = [(f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" '
              f'aria-label="{html.escape(title)}"><text x="0" y="18" font-weight="bold">'
              f"{html.escape(title)}</text>")]
    for i, row in enumerate(rows):
        y = 32 + i * (bar_h + gap)
        value = float(row[key])
        w = (width - label_w - 90) * value / peak
        fill = "#888" if row["resultado"] == "APROBADO" else "url(#hatch)"
        parts.append(
            f'<text x="0" y="{y + 16}" font-size="12">{html.escape(row["tag"])}</text>'
            f'<rect x="{label_w}" y="{y}" width="{w:.1f}" height="{bar_h}" fill="{fill}" '
            f'stroke="#000"/><text x="{label_w + w + 6:.1f}" y="{y + 16}" font-size="12">'
            f"{value:.2f} {unit}</text>"
        )
    parts.append("</svg>")
    return "".join(parts)


def main(folder):
    folder = Path(folder)
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.row.json"))]
    if not rows:
        print("No hay resultados *.row.json en", folder)
        return
    rows.sort(key=lambda r: r["fecha"])
    with (folder / "resumen.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([label for _, label in COLUMNS])
        writer.writerows([[fmt(r.get(k, "")) for k, _ in COLUMNS] for r in rows])
    table = ["| " + " | ".join(label for _, label in COLUMNS) + " |",
             "|" + "---|" * len(COLUMNS)]
    table += ["| " + " | ".join(fmt(r.get(k, "")) for k, _ in COLUMNS) + " |" for r in rows]
    (folder / "resumen.md").write_text("\n".join(table) + "\n", encoding="utf-8")
    head = "".join(f"<th>{html.escape(label)}</th>" for _, label in COLUMNS)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(fmt(r.get(k, '')))}</td>" for k, _ in COLUMNS) + "</tr>"
        for r in rows
    )
    pattern = ('<svg width="0" height="0"><defs><pattern id="hatch" width="6" height="6" '
               'patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" '
               'height="6" fill="#fff"/><line x1="0" y1="0" x2="0" y2="6" stroke="#000" '
               'stroke-width="2"/></pattern></defs></svg>')
    page = f"""<!doctype html><html lang="es"><meta charset="utf-8">
<title>Pruebas de carga en la nube</title>
<style>body{{font-family:Arial,sans-serif;margin:24px;color:#000}}table{{border-collapse:collapse;
font-size:12px}}td,th{{border:1px solid #000;padding:4px 6px}}section{{margin:24px 0}}</style>
<h1>LogisTech: pruebas de carga en la nube</h1>
<p>Servidor: {html.escape(rows[-1]["servidor"])}. Barras grises: aprobado. Barras rayadas:
fallido, incompleto o lento.</p>{pattern}
<section>{bars(rows, "p95_ms", "Tiempo de respuesta p95 por prueba", "ms")}</section>
<section>{bars(rows, "req_s", "Solicitudes por segundo", "req/s")}</section>
<section>{bars(rows, "error_pct", "Porcentaje de error", "%")}</section>
<table><tr>{head}</tr>{body}</table></html>"""
    (folder / "resumen.html").write_text(page, encoding="utf-8")
    print("\n".join(table))
    print(f"\nGenerado: {folder / 'resumen.csv'}, resumen.md y resumen.html")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/evidencias/semana13-nube")
