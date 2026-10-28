"""Record local adaptation checks without replacing F0-F5 evidence or running deployment."""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = [
    "docker",
    "compose",
    "-p",
    "logistech-language",
    "-f",
    "docker-compose.yml",
    "-f",
    "compose.validation.yml",
]
BACKEND = COMPOSE + ["exec", "-T", "backend"]
COMMANDS = [
    ["docker", "info", "--format", "{{.OSType}} {{.ServerVersion}}"],
    COMPOSE + ["config", "--quiet"],
    BACKEND + ["python", "manage.py", "check"],
    BACKEND + ["python", "manage.py", "migrate", "--check"],
    BACKEND + ["python", "manage.py", "makemigrations", "--check", "--dry-run"],
    BACKEND + ["python", "-m", "tools.verificar_base"],
    BACKEND
    + [
        "python",
        "-m",
        "pytest",
        "--ds=config.settings.testing",
        "-q",
        "-o",
        "cache_dir=/tmp/pytest-language-final",
    ],
    BACKEND + ["ruff", "check", "--no-cache", "."],
    BACKEND + ["python", "-m", "pip", "check"],
    COMPOSE + ["exec", "-T", "frontend", "npm", "run", "lint"],
    COMPOSE + ["exec", "-T", "frontend", "npm", "run", "build"],
    COMPOSE + ["exec", "-T", "frontend", "npm", "run", "test:unit"],
]


def main():
    results = []
    for command in COMMANDS:
        run = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240,
            check=False,
        )
        results.append(
            {
                "command": command,
                "exit_code": run.returncode,
                "stdout": run.stdout,
                "stderr": run.stderr,
            }
        )
        print(f"{run.returncode}: {' '.join(command)}", flush=True)
    target = ROOT / "docs/evidencias/adaptacion-verificacion.json"
    target.write_text(
        json.dumps(
            {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "scope": "Local isolated PostgreSQL; E2E recorded separately; no cloud deployment",
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return int(any(item["exit_code"] for item in results))


if __name__ == "__main__":
    raise SystemExit(main())
