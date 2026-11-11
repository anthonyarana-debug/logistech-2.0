"""Export measured k6 profiles and Docker snapshots without local credentials."""

import csv
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/qa/semana13/k6"
OUTPUT = ROOT / "docs/evidencias/semana13"
SCENARIOS = ("get", "crud", "register", "boxes", "history", "recovery")


def read_run(folder):
    raw = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    metrics = raw["metrics"]

    def value(metric, key):
        return metrics.get(metric, {}).get("values", {}).get(key, 0)

    snapshots = {}
    for phase in ("before", "after"):
        snapshots[phase] = [
            json.loads(line) for line in (folder / f"resources-{phase}.jsonl").read_text().splitlines()
        ]
    record = {
        "scenario": raw["scenario"], "run": folder.name, "vus": raw["vus"],
        "planned": raw["iterations"], "completed": value("iterations", "count"),
        "requests": value("http_reqs", "count"), "requests_per_second": round(value("http_reqs", "rate"), 2),
        "seconds": round(raw["state"]["testRunDurationMs"] / 1000, 3),
        "failed_percent": round(100 * value("http_req_failed", "rate"), 2),
        "registrations": value("registrations_created", "count"),
        "persisted_registrations": int((folder / "registration-count.txt").read_text().strip()),
        **{key: round(value("http_req_duration", metric), 2)
           for key, metric in (("mean_ms", "avg"), ("p90_ms", "p(90)"), ("p95_ms", "p(95)"), ("p99_ms", "p(99)"))},
        **{f"http_{status}": value(f"responses_{status}", "count")
           for status in ("2xx", "3xx", "4xx", "5xx", "connection")},
    }
    return record, {"summary": raw, "docker_snapshots": snapshots}


def main():
    rows, evidence = [], {}
    for scenario in SCENARIOS:
        folders = [
            path for path in SOURCE.glob(f"{scenario}-*")
            if re.fullmatch(r"[a-z]+-[0-9a-f]{12}", path.name)
            and (path / "summary.json").is_file()
        ]
        if folders:
            row, raw = read_run(max(folders, key=lambda path: (path / "summary.json").stat().st_mtime))
            rows.append(row)
            evidence[scenario] = raw
    if not rows:
        raise SystemExit("No isolated k6 reports found.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "k6.json").write_text(json.dumps({"runs": rows, "evidence": evidence}, indent=2), encoding="utf-8")
    with (OUTPUT / "k6.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    cells = ("scenario", "vus", "completed", "requests", "requests_per_second",
             "mean_ms", "p90_ms", "p95_ms", "p99_ms", "failed_percent")
    header = "".join(f"<th>{html.escape(key)}</th>" for key in cells)
    table = "".join("<tr>" + "".join(f"<td>{html.escape(str(row[key]))}</td>" for key in cells) + "</tr>" for row in rows)
    chart = "".join(
        f'<li>{html.escape(row["scenario"])} <meter min="0" max="{max(r["p95_ms"] for r in rows)}" '
        f'value="{row["p95_ms"]}"></meter> {row["p95_ms"]} ms</li>' for row in rows
    )
    (OUTPUT / "k6.html").write_text(
        '<!doctype html><html lang="es"><meta charset="utf-8"><title>LogisTech Semana 13</title>'
        '<style>body{font:16px system-ui;margin:2rem;color:#172b31}table{border-collapse:collapse}'
        'td,th{border:1px solid #bbc8ca;padding:.5rem;text-align:right}meter{width:240px}</style>'
        '<h1>Ensayos locales k6</h1><p>Las muestras tienen distintos tamaños y operaciones.</p>'
        f'<table><thead><tr>{header}</tr></thead><tbody>{table}</tbody></table><h2>Latencia p95</h2><ul>{chart}</ul></html>',
        encoding="utf-8",
    )
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
