"""Verificación local F3; sin carga, recursos externos ni secretos en las evidencias."""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

root = Path(__file__).resolve().parents[1]
prefix = ["docker", "compose", "exec", "-T", "backend"]
commands = [
    ["docker", "info", "--format", "{{.OSType}} {{.ServerVersion}}"],
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
        "cache_dir=/tmp/pytest-f3",
    ],
    prefix
    + [
        "python",
        "-c",
        "import tempfile; from pathlib import Path; "
        "print((Path(tempfile.gettempdir())/'logistech-f3-http.json')"
        ".read_text(encoding='utf-8'))",
    ],
    prefix + ["ruff", "check", "--no-cache", "."],
    ["docker", "compose", "exec", "-T", "frontend", "npm", "run", "lint"],
    ["docker", "compose", "exec", "-T", "frontend", "npm", "run", "build"],
    prefix + ["python", "manage.py", "check", "--deploy", "--settings=config.settings.production"],
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
        break
if all(item["codigo_salida"] == 0 for item in results):
    for route, expected in [
        ("http://127.0.0.1:8000/api/v1/health/", 200),
        ("http://127.0.0.1:5173/api/v1/health/", 200),
        ("http://127.0.0.1:8000/api/v1/categories/", 401),
        ("http://127.0.0.1:8000/api/v1/boxes/", 401),
    ]:
        try:
            response = urlopen(route, timeout=8)
        except HTTPError as error:
            response = error
        with response:
            code = response.code
            body = response.read().decode()
        results.append(
            {
                "url": route,
                "http": code,
                "esperado": expected,
                "codigo_salida": int(code != expected),
                "cuerpo": body,
            }
        )
        print(f"HTTP {code}: {route}", flush=True)
output = root / "docs/evidencias/fase3-verificacion.json"
output.write_text(
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
