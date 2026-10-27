"""Comprobaciones reproducibles de F1; requiere Compose iniciado y saludable."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

root = Path(__file__).resolve().parents[1]
results = []
commands = [
    ["docker", "info", "--format", "{{.OSType}} {{.ServerVersion}}"],
    ["docker", "compose", "config", "--quiet"],
    ["docker", "compose", "ps"],
    ["docker", "compose", "exec", "-T", "backend", "python", "-m", "pip", "check"],
    ["docker", "compose", "exec", "-T", "backend", "python", "manage.py", "check"],
    [
        "docker",
        "compose",
        "exec",
        "-T",
        "backend",
        "python",
        "manage.py",
        "makemigrations",
        "--check",
        "--dry-run",
    ],
    ["docker", "compose", "exec", "-T", "backend", "python", "manage.py", "migrate", "--noinput"],
    ["docker", "compose", "exec", "-T", "backend", "python", "manage.py", "showmigrations"],
    ["docker", "compose", "exec", "-T", "backend", "python", "-m", "tools.verificar_base"],
    [
        "docker",
        "compose",
        "exec",
        "-T",
        "backend",
        "python",
        "-m",
        "pytest",
        "--ds=config.settings.testing",
        "-q",
        "-o",
        "cache_dir=/tmp/logistech-pytest-cache",
    ],
    ["docker", "compose", "exec", "-T", "backend", "ruff", "check", "--no-cache", "."],
    ["docker", "compose", "exec", "-T", "frontend", "npm", "run", "lint"],
    ["docker", "compose", "exec", "-T", "frontend", "npm", "run", "build"],
    [
        "docker",
        "compose",
        "exec",
        "-T",
        "backend",
        "python",
        "manage.py",
        "check",
        "--deploy",
        "--settings=config.settings.production",
    ],
]
for command in commands:
    completed = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
    )
    results.append(
        {
            "comando": command,
            "codigo_salida": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    )
    print(f"[{completed.returncode}] {' '.join(command)}", flush=True)

for url, expected in [
    ("http://127.0.0.1:8000/api/v1/health/", 200),
    ("http://127.0.0.1:8000/api/v1/health/live/", 200),
    ("http://127.0.0.1:8000/api/v1/no-existe/", 404),
    ("http://127.0.0.1:5173/", 200),
    ("http://127.0.0.1:5173/api/v1/health/", 200),
]:
    try:
        response = urlopen(url, timeout=8)
    except HTTPError as error:
        response = error
    with response:
        code = response.code
        body = response.read().decode()
    results.append(
        {
            "url": url,
            "http": code,
            "esperado": expected,
            "codigo_salida": int(code != expected),
            "cuerpo": body if "/api/" in url else "HTML recibido; contenido omitido",
        }
    )
    print(f"HTTP {code}: {url}", flush=True)

# Inspeccionar sin persistir el JSON expandido: incluye secretos de .env.
expanded = subprocess.run(
    ["docker", "compose", "config", "--format", "json"],
    cwd=root,
    capture_output=True,
    text=True,
    check=True,
)
config = json.loads(expanded.stdout)
services = config["services"]
safe = not services["db"].get("ports")
safe = safe and config["networks"]["database"]["internal"]
safe = safe and all(
    p.get("host_ip") == "127.0.0.1"
    for service in ("backend", "frontend")
    for p in services[service]["ports"]
)
results.append(
    {"control": "PostgreSQL privado y puertos web en loopback", "codigo_salida": int(not safe)}
)

evidence = root / "docs" / "evidencias"
evidence.mkdir(exist_ok=True)
report = {
    "fecha_utc": datetime.now(timezone.utc).isoformat(),
    "entorno": "Local Docker Linux",
    "python_local": sys.version,
    "venv_aislado": sys.prefix != sys.base_prefix,
    "resultados": results,
}
(evidence / "fase1-verificacion.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
raise SystemExit(any(result["codigo_salida"] != 0 for result in results))
