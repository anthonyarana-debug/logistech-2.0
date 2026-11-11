"""Summarize completed monitored runs without copying credentials or database data."""

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/qa/semana13/k6"
TARGET = ROOT / "docs/evidencias/semana13-cierre"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def json_lines(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def main():
    rows = []
    details = {}
    for path in sorted(SOURCE.glob("*/summary.json")):
        summary = read(path)
        if "duration" not in summary or not (path.parent / "storage.jsonl").is_file():
            continue
        folder = path.parent
        metrics = summary["metrics"]
        latency = metrics["http_req_duration"]["values"]
        storage = json_lines(folder / "storage.jsonl")
        persisted = folder / "registration-count.txt"
        row = {
            "run": folder.name,
            "scenario": summary["scenario"],
            "page": summary["page"],
            "requested": summary["iterations"],
            "completed": metrics["iterations"]["values"]["count"],
            "requests": metrics["http_reqs"]["values"]["count"],
            "vus": summary["vus"],
            "seconds": round(summary["state"]["testRunDurationMs"] / 1000, 3),
            "requests_per_second": round(metrics["http_reqs"]["values"]["rate"], 2),
            "failure_percent": round(
                metrics["http_req_failed"]["values"]["rate"] * 100, 2
            ),
            "mean_ms": round(latency["avg"], 2),
            **{
                f"p{percent}_ms": round(latency[f"p({percent})"], 2)
                for percent in (90, 95, 99)
            },
            "registered": int(persisted.read_text(encoding="utf-8-sig").strip())
            if persisted.exists()
            else None,
            "max_growth_kib": max(sample["usedKiB"] for sample in storage)
            - storage[0]["usedKiB"],
        }
        if row["completed"] != row["requested"]:
            row["decision"] = "incomplete"
        elif row["p95_ms"] >= 500 or row["failure_percent"] != 0:
            row["decision"] = "threshold_failed"
        else:
            row["decision"] = "passed"
        rows.append(row)
        details[folder.name] = {
            "summary": summary,
            "storage": storage,
            "plans": read(folder / "pagination-plans.json"),
            "docker": {
                phase: json_lines(folder / f"resources-{phase}.jsonl")
                for phase in ("before", "after")
                if (folder / f"resources-{phase}.jsonl").is_file()
            },
        }
    if not rows:
        raise SystemExit("No monitored runs available.")
    rows.sort(key=lambda row: (row["scenario"], row["requested"], row["run"]))
    TARGET.mkdir(parents=True, exist_ok=True)
    (TARGET / "capacity.json").write_text(
        json.dumps({"runs": rows, "details": details}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    with (TARGET / "capacity.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    fields = list(rows[0])
    headings = "".join(f"<th>{html.escape(key)}</th>" for key in fields)
    table = "".join(
        "<tr>"
        + "".join(f"<td>{html.escape(str(row[key]))}</td>" for key in fields)
        + "</tr>"
        for row in rows
    )
    bars = "".join(
        f'<li>{row["requested"]} GET · p95 <meter min="0" max="800" value="{row["p95_ms"]}"></meter>'
        f" {row['p95_ms']} ms</li>"
        for row in rows
        if row["scenario"] == "get"
    )
    (TARGET / "capacity.html").write_text(
        '<!doctype html><html lang="es"><meta charset="utf-8"><title>Capacidad local de LogisTech</title>'
        "<style>body{font:16px system-ui;margin:2rem}td,th{border:1px solid #ccc;padding:.45rem}"
        "table{border-collapse:collapse}meter{width:230px}</style>"
        "<h1>Capacidad local de LogisTech</h1><p>Una iteración GET equivale a una petición HTTP. "
        "Los registros hacen dos peticiones por iteración.</p>"
        f"<table><thead><tr>{headings}</tr></thead><tbody>{table}</tbody></table><ul>{bars}</ul></html>",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
