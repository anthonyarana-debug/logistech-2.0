"""Comprobaciones F4 reproducibles, sin credenciales ni cambios de infraestructura."""

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

root = Path(__file__).resolve().parents[1]
backend = ["docker", "compose", "exec", "-T", "backend"]
frontend = ["docker", "compose", "exec", "-T", "frontend"]
commands = [
    ["docker", "info", "--format", "{{.OSType}} {{.ServerVersion}}"],
    ["docker", "compose", "config", "--quiet"],
    ["docker", "compose", "ps"],
    backend + ["python", "-m", "pip", "--no-cache-dir", "check"],
    backend + ["python", "manage.py", "check"],
    backend + ["python", "manage.py", "makemigrations", "--check", "--dry-run"],
    backend + ["python", "manage.py", "migrate", "--check"],
    backend + ["python", "manage.py", "showmigrations"],
    backend + ["python", "-m", "tools.verificar_base"],
    backend
    + [
        "python",
        "-m",
        "pytest",
        "--ds=config.settings.testing",
        "-q",
        "-o",
        "cache_dir=/tmp/pytest-f4-final",
    ],
    backend + ["ruff", "check", "--no-cache", "."],
    frontend + ["npm", "run", "lint"],
    frontend + ["npm", "run", "build"],
    frontend + ["npm", "audit"],
    [shutil.which("node") or "node", "--test", "frontend/unit/session.test.js"],
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
]:
    url = f"http://127.0.0.1:5173/api/v1/{path}"
    try:
        response = urlopen(url, timeout=8)
    except HTTPError as exc:
        response = exc
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
output = root / "docs/evidencias/fase4-verificacion.json"
output.write_text(
    json.dumps(
        {
            "fecha_utc": datetime.now(timezone.utc).isoformat(),
            "entorno": "Docker Linux local; PostgreSQL real; Node del host para unitarias JS",
            "resultados": results,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
raise SystemExit(any(item["codigo_salida"] for item in results))
