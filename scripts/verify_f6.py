"""Verify only the isolated F6 stack; preserve historical evidence and production data."""

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = [
    "docker",
    "compose",
    "-p",
    "logistech-f6",
    "-f",
    "docker-compose.yml",
    "-f",
    "compose.validation.yml",
]
BACKEND = COMPOSE + ["exec", "-T", "backend"]
FRONTEND = COMPOSE + ["exec", "-T", "frontend", "npm", "run"]


def main():
    commands = [
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
            "cache_dir=/tmp/pytest-f6-final",
        ],
        BACKEND + ["ruff", "check", "--no-cache", "."],
        BACKEND + ["python", "-m", "pip", "check"],
        FRONTEND + ["test:unit"],
        FRONTEND + ["lint"],
        FRONTEND + ["build"],
    ]
    results = []
    for command in commands:
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
        entry = {
            "command": command,
            "exit_code": run.returncode,
            "stdout": run.stdout,
            "stderr": run.stderr,
        }
        # Discovery matters: exit 0 with no tests must never be called a successful suite.
        if "test:unit" in command:
            match = re.search(r"(?:#|ℹ) tests (\d+)", run.stdout)
            entry["discovered_tests"] = int(match[1]) if match else 0
            if not entry["discovered_tests"]:
                entry["exit_code"] = 1
        results.append(entry)
        print(f"{entry['exit_code']}: {' '.join(command[-8:])}", flush=True)
    target = ROOT / "docs/evidencias/fase6/checks.json"
    target.parent.mkdir(exist_ok=True, parents=True)
    target.write_text(
        json.dumps(
            {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "scope": (
                    "Isolated logistech-f6, real PostgreSQL, no deployment; E2E recorded separately"
                ),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return int(any(x["exit_code"] for x in results))


if __name__ == "__main__":
    raise SystemExit(main())
