"""Verifica F2 en Compose y registra evidencia sin contraseñas, tokens ni cookies."""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if (root / "backend/apps/core/api.py").exists():
    raise SystemExit(
        "F2 es evidencia histórica. Usa scripts/verificar_fase3.py para el estado actual."
    )
prefix = ["docker", "compose", "exec", "-T", "backend"]
commands = [
    ["docker", "compose", "config", "--quiet"],
    ["docker", "compose", "ps"],
    prefix + ["python", "-m", "pip", "--no-cache-dir", "check"],
    prefix + ["python", "manage.py", "check"],
    prefix + ["python", "manage.py", "makemigrations", "--check", "--dry-run"],
    prefix + ["python", "manage.py", "migrate", "--check"],
    prefix + ["python", "manage.py", "showmigrations"],
    prefix + ["python", "-m", "tools.verificar_base"],
    prefix
    + [
        "python",
        "-m",
        "pytest",
        "--ds=config.settings.testing",
        "-q",
        "-o",
        "cache_dir=/tmp/pytest-f2",
    ],
    prefix + ["ruff", "check", "--no-cache", "."],
    ["docker", "compose", "exec", "-T", "frontend", "npm", "run", "lint"],
    ["docker", "compose", "exec", "-T", "frontend", "npm", "run", "build"],
    prefix + ["python", "manage.py", "check", "--deploy", "--settings=config.settings.production"],
    prefix + ["python", "-m", "tools.verificar_http_auth"],
]
results = []
for command in commands:
    response = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    results.append(
        {
            "comando": command,
            "codigo_salida": response.returncode,
            "stdout": response.stdout,
            "stderr": response.stderr,
        }
    )
    print(f"[{response.returncode}] {' '.join(command)}", flush=True)
    if response.returncode:
        print("Comprobación fallida; revisar la evidencia saneada.", flush=True)
        break
evidence = root / "docs/evidencias/fase2-verificacion.json"
evidence.write_text(
    json.dumps(
        {
            "fecha_utc": datetime.now(timezone.utc).isoformat(),
            "entorno": "Local Docker Linux",
            "resultados": results,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
raise SystemExit(any(item["codigo_salida"] for item in results))
