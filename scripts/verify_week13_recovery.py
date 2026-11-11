"""Backup, restore and restart the synthetic Week 13 database."""

import json
import os
import re
import subprocess
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "logistech-week13"
BACKEND = f"{PROJECT}-backend-1"
DATABASE = f"{PROJECT}-db-1"
ENV = {
    **os.environ,
    "SOURCE_REF": "week13-local",
    "PUBLIC_DOMAIN": "localhost",
    "PUBLIC_ORIGIN": "https://localhost:8453",
    "POSTGRES_DB": "logistech",
    "F7_BACKUP_DIR": "./backups/week13",
}
COMPOSE = [
    "docker", "compose", "-p", PROJECT, "--env-file", ".env.f7-candidate",
    "-f", "compose.production.yml", "-f", "compose.production-rehearsal.yml",
    "-f", "compose.week13.yml", "--profile", "tools",
]


def run(args, *, env=ENV, check=True):
    return subprocess.run(
        args, cwd=ROOT, env=env, check=check, capture_output=True,
        encoding="utf-8", errors="replace", timeout=120,
    )


def manifest(database):
    program = (ROOT / "scripts/production_database_check.py").read_text(encoding="utf-8")
    result = run([
        "docker", "exec", "-e", f"POSTGRES_DB={database}", BACKEND,
        "python", "manage.py", "shell", "--no-imports", "-c", program,
    ])
    return json.loads(result.stdout)


def main():
    for container in (DATABASE, BACKEND):
        label = run([
            "docker", "inspect", "--format",
            '{{index .Config.Labels "com.docker.compose.project"}}', container,
        ]).stdout.strip()
        if label != PROJECT:
            raise RuntimeError("Only the synthetic Week 13 project is supported.")
    before = manifest("logistech")
    backup_start = time.monotonic()
    backup = run(COMPOSE + ["run", "--rm", "--no-deps", "backup"]).stdout
    backup_seconds = time.monotonic() - backup_start
    name = re.search(r"Backup complete: (logistech-[\w-]+\.dump)", backup).group(1)
    restored = "restore_week13_" + uuid.uuid4().hex[:10]
    restore_env = {**ENV, "STAGING_DB": restored, "RESTORE_FILE": name}
    restore_start = time.monotonic()
    run(COMPOSE + ["run", "--rm", "--no-deps", "restore"], env=restore_env)
    restore_seconds = time.monotonic() - restore_start
    copied = manifest(restored)
    assert before["business_manifest"] == copied["business_manifest"]
    repeated = run(COMPOSE + ["run", "--rm", "--no-deps", "restore"], env=restore_env, check=False)
    assert repeated.returncode and "Refusing to restore into any existing database" in repeated.stderr
    restart_start = time.monotonic()
    run(COMPOSE + ["restart", "db", "backend"])
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        try:
            after = manifest("logistech")
            break
        except subprocess.CalledProcessError:
            time.sleep(1)
    else:
        raise RuntimeError("PostgreSQL did not recover before the deadline.")
    assert before["business_manifest"] == after["business_manifest"]
    print(json.dumps({
        "project": PROJECT, "backup_bytes": (ROOT / "backups/week13" / name).stat().st_size,
        "backup_seconds": round(backup_seconds, 3), "restore_seconds": round(restore_seconds, 3),
        "restart_until_manifest_seconds": round(time.monotonic() - restart_start, 3),
        "checksum_verified_by_restore": True, "existing_database_refused": True,
        "manifest_matches": True, "persisted_after_restart": True,
        "model_counts": {key: value["count"] for key, value in before["business_manifest"].items()},
        "tls": after["tls_protocol"], "invalid_receipt_company": after["invalid_receipt_company"],
    }, indent=2))


if __name__ == "__main__":
    main()
