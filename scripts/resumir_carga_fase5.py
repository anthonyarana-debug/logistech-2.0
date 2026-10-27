"""Consolida métricas reales; conserva CSV crudos y avisa de snapshots/cierre del generador."""

import csv
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
folder = root / "docs/evidencias/carga-fase5"
reports = []
for path in sorted(folder.glob("*_summary.json")):
    report = json.loads(path.read_text(encoding="utf-8"))
    prefix = path.name.removesuffix("_summary.json")
    report["prefijo"] = prefix
    console = (folder / f"{prefix}_console.txt").read_text(encoding="utf-8")
    report["error_cierre_csv_locust"] = "I/O operation on closed file" in console
    samples = json.loads((folder / f"{prefix}_resources.json").read_text(encoding="utf-8"))
    peaks = {}
    for sample in samples:
        for container in sample["contenedores"]:
            name = container["Name"]
            cpu = float(container["CPUPerc"].rstrip("%"))
            memory = re.match(r"([\d.]+)([A-Za-z]+)", container["MemUsage"])
            factor = {
                "B": 1,
                "kB": 1000,
                "MB": 1000**2,
                "GB": 1000**3,
                "KiB": 1024,
                "MiB": 1024**2,
                "GiB": 1024**3,
            }[memory[2]]
            entry = peaks.setdefault(name, {"cpu_porcentaje_pico": 0, "memoria_bytes_pico": 0})
            entry["cpu_porcentaje_pico"] = max(entry["cpu_porcentaje_pico"], cpu)
            entry["memoria_bytes_pico"] = max(
                entry["memoria_bytes_pico"], float(memory[1]) * factor
            )
    report["recursos_observados"] = peaks
    snapshot = folder / f"{prefix}_stats.csv"
    if snapshot.exists():
        with snapshot.open(newline="", encoding="utf-8") as stream:
            row = next(r for r in csv.DictReader(stream) if r["Name"] == "Aggregated")
        report["csv_ultimo_snapshot_solicitudes"] = int(row["Request Count"])
        report["diferencia_snapshot_vs_cierre"] = report["solicitudes"] - int(row["Request Count"])
    reports.append(report)
with (folder / "resumen-escenarios.csv").open("w", newline="", encoding="utf-8") as stream:
    fields = [
        "prefijo",
        "usuarios_configurados",
        "usuarios_autenticados_pico",
        "spawn_rate",
        "calentamiento_segundos",
        "medicion_segundos_reales",
        "solicitudes",
        "rps",
        "latencia_media_ms",
        "p95_ms",
        "fallos",
        "fallos_porcentaje",
        "error_cierre_csv_locust",
    ]
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(reports)
(root / "docs/evidencias/fase5-carga-resumen.json").write_text(
    json.dumps(
        {
            "fuente": "Eventos de cierre de Locust; snapshots originales conservados",
            "ejecuciones": reports,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
for report in reports:
    print(
        report["prefijo"],
        "users=",
        report["usuarios_autenticados_pico"],
        "RPS=",
        round(report["rps"], 2),
        "p95=",
        report["p95_ms"],
        "errors=",
        report["fallos"],
        "CSV_close_error=",
        report["error_cierre_csv_locust"],
    )
