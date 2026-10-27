"""Extrae solo nombres/estados/tiempos: no copia contextos ni payloads de Playwright."""

import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
local = root / "docs/evidencias/local"
tests = []


def visit(suite):
    for spec in suite.get("specs", []):
        for test in spec["tests"]:
            result = test["results"][-1]
            tests.append(
                {
                    "nombre": spec["title"],
                    "archivo": spec["file"],
                    "estado": result["status"],
                    "duracion_ms": result["duration"],
                }
            )
    for child in suite.get("suites", []):
        visit(child)


for filename in (
    "fase4-flujos.json",
    "fase4-accesibilidad.json",
    "fase4-admin-final.json",
    "fase4-navegacion-final.json",
    "fase4-formato-final.json",
):
    if not (local / filename).exists():
        continue
    report = json.loads((local / filename).read_text(encoding="utf-8-sig"))
    for suite in report["suites"]:
        visit(suite)
tests = list({test["nombre"]: test for test in tests}.values())
output = {
    "fecha_utc": datetime.now(timezone.utc).isoformat(),
    "entorno": "Chromium 156 / Playwright 1.64.1; servicios Compose locales",
    "alcance": "8 flujos + 1 accesibilidad, ejecuciones separadas; sin retries",
    "pruebas": tests,
    "aprobadas": sum(t["estado"] == "passed" for t in tests),
    "total": len(tests),
    "trazas_secretos": "No conservados en evidencia pública",
}
(root / "docs/evidencias/fase4-e2e.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"{output['aprobadas']}/{len(tests)} pruebas E2E aprobadas")
raise SystemExit(any(t["estado"] != "passed" for t in tests))
