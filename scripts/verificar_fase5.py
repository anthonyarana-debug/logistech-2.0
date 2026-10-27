"""Auditoría final F5 local. No sobrescribe evidencias F1–F4 ni ejecuta carga/cloud."""

import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

root = Path(__file__).resolve().parents[1]
compose = [
    "docker",
    "compose",
    "-p",
    "logistech-f5",
    "-f",
    "docker-compose.yml",
    "-f",
    "compose.validation.yml",
]
backend = compose + ["exec", "-T", "backend"]
production = compose + ["-f", "compose.production-check.yml"]
commands = [
    [
        "docker",
        "info",
        "--format",
        "{{.OSType}} {{.ServerVersion}} CPU={{.NCPU}} RAM={{.MemTotal}}",
    ],
    compose + ["config", "--quiet"],
    compose + ["ps"],
    backend + ["python", "-m", "pip", "--no-cache-dir", "check"],
    backend + ["python", "manage.py", "check"],
    backend + ["python", "manage.py", "makemigrations", "--check", "--dry-run"],
    backend + ["python", "manage.py", "migrate", "--check"],
    backend + ["python", "-m", "tools.verificar_base"],
    backend + ["python", "-m", "tools.verificar_entrega"],
    backend
    + [
        "python",
        "-m",
        "pytest",
        "--ds=config.settings.testing",
        "-q",
        "-o",
        "cache_dir=/tmp/pytest-f5-final",
    ],
    backend + ["ruff", "check", "--no-cache", "."],
    compose + ["exec", "-T", "frontend", "npm", "run", "lint"],
    compose + ["exec", "-T", "frontend", "npm", "run", "build"],
    compose + ["exec", "-T", "frontend", "npm", "audit"],
    [shutil.which("node") or "node", "--test", "frontend/unit/session.test.js"],
    production + ["build", "backend"],
    production
    + ["run", "--rm", "--no-deps", "backend", "python", "-m", "pip", "--no-cache-dir", "check"],
    production
    + [
        "run",
        "--rm",
        "--no-deps",
        "backend",
        "gunicorn",
        "config.wsgi:application",
        "--check-config",
    ],
    production
    + [
        "run",
        "--rm",
        "--no-deps",
        "backend",
        "python",
        "manage.py",
        "check",
        "--deploy",
        "--settings=config.settings.production",
    ],
    production + ["run", "--rm", "--no-deps", "backend", "python", "-m", "tools.verificar_wsgi"],
]
results = []
for command in commands:
    run = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    results.append(
        {
            "comando": command,
            "codigo_salida": run.returncode,
            "stdout": run.stdout,
            "stderr": run.stderr,
        }
    )
    print(f"[{run.returncode}] {' '.join(command)}", flush=True)
for path, expected in [
    ("health/", 200),
    ("categories/", 401),
    ("boxes/", 401),
    ("references/", 401),
    ("no-existe/", 404),
]:
    url = f"http://127.0.0.1:5174/api/v1/{path}"
    try:
        response = urlopen(url, timeout=8)
    except HTTPError as error:
        response = error
    with response:
        code, body = response.code, response.read().decode()
    results.append(
        {
            "url": url,
            "http": code,
            "esperado": expected,
            "codigo_salida": int(code != expected),
            "cuerpo": body,
        }
    )
schema_run = next(r for r in results if "tools.verificar_entrega" in r.get("comando", []))
if schema_run["codigo_salida"] == 0:
    schema = json.loads(schema_run["stdout"])
    diagram = (root / "docs/MODELO_DATOS.mmd").read_text(encoding="utf-8")
    differences = {}
    for name, block in re.findall(r"    ([A-Z]+) \{(.*?)\n    \}", diagram, re.S):
        declared = {line.split()[1] for line in block.splitlines() if len(line.split()) >= 2}
        actual = set(schema["esquema"][name]["columnas"])
        if declared != actual:
            differences[name] = {
                "solo_diagrama": sorted(declared - actual),
                "solo_modelo": sorted(actual - declared),
            }
    results.append(
        {
            "comprobacion": "ER editable vs columnas de modelos/DB",
            "diferencias": differences,
            "codigo_salida": int(bool(differences)),
        }
    )
for filename in ("fase5-e2e-inicial.json", "fase5-e2e-final.json"):
    raw = root / "docs/evidencias/local" / filename
    if not raw.exists():
        print(
            f"Sin reporte crudo {filename}; se conserva la evidencia histórica existente.",
            flush=True,
        )
        continue
    data = json.loads(raw.read_text(encoding="utf-8-sig"))
    cases = []

    def visit(suite):
        for spec in suite.get("specs", []):
            for test in spec["tests"]:
                outcome = test["results"][-1]
                cases.append(
                    {
                        "nombre": spec["title"],
                        "estado": outcome["status"],
                        "duracion_ms": outcome["duration"],
                    }
                )
        for child in suite.get("suites", []):
            visit(child)

    for suite in data["suites"]:
        visit(suite)
    public = {
        "fecha_inicio": data["stats"]["startTime"],
        "estadisticas": data["stats"],
        "casos": cases,
        "origen": "inicial 5173" if "inicial" in filename else "aislado 5174",
    }
    (root / "docs/evidencias" / filename).write_text(
        json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
report = {
    "fecha_utc": datetime.now(timezone.utc).isoformat(),
    "entorno": "Validación F5 con base/caché separadas; sin infraestructura externa",
    "resultados": results,
}
(root / "docs/evidencias/fase5-verificacion.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
raise SystemExit(any(r["codigo_salida"] for r in results))
