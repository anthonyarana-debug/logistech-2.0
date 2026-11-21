"""Rehearse a dump transfer between two private, disposable PostgreSQL instances."""

import hashlib
import json
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "postgres:17-alpine"
APP_IMAGE = "logistech-week13-tests:local"
DB_SETTINGS = (
    "-e", "POSTGRES_DB=logistech", "-e", "POSTGRES_USER=logistech",
    "-e", "POSTGRES_PASSWORD=solo-pruebas-no-es-un-secreto-real",
)
MANIFEST = """
SELECT to_jsonb(result) FROM (
    SELECT (SELECT count(*) FROM organizations_company) AS companies,
           (SELECT count(*) FROM organizations_branch) AS branches,
           (SELECT count(*) FROM catalog_product) AS products,
           (SELECT count(*) FROM boxes_box) AS boxes,
           (SELECT count(*) FROM django_migrations) AS migrations,
           (SELECT count(*) FROM pg_trigger
            WHERE NOT tgisinternal
              AND tgname IN ('boxes_receipt_immutable', 'boxes_event_immutable')
           ) AS history_triggers,
           (SELECT md5(string_agg(to_jsonb(b)::text, ',' ORDER BY b.id))
            FROM boxes_box b) AS boxes_digest
) result;
"""


def docker(*args, capture=True, check=True, **streams):
    return subprocess.run(
        ["docker", *args], capture_output=capture, check=check, timeout=120, **streams,
    )


def wait_for_postgres(name):
    for _ in range(30):
        if not docker("exec", name, "pg_isready", "-h", "127.0.0.1", check=False).returncode:
            return
        time.sleep(1)
    raise RuntimeError("Isolated PostgreSQL did not start")


def manifest(name):
    return json.loads(
        docker("exec", name, "psql", "-U", "logistech", "-d", "logistech",
               "-XAt", "-v", "ON_ERROR_STOP=1", "-c", MANIFEST).stdout,
    )


def main():
    network = f"logistech-move-{uuid.uuid4().hex[:10]}"
    source, destination = f"{network}-source", f"{network}-destination"
    docker("network", "create", network)
    started_containers = []
    try:
        for name in (source, destination):
            docker("run", "-d", "--rm", "--network", network, "--name", name, *DB_SETTINGS, IMAGE)
            started_containers.append(name)
            wait_for_postgres(name)

        app = (
            "run", "--rm", "--network", network, "-v", f"{ROOT / 'backend'}:/app:ro",
            "-e", "PYTHONDONTWRITEBYTECODE=1", "-e", f"DB_HOST={source}",
            "-e", "DJANGO_SETTINGS_MODULE=config.settings.testing",
            APP_IMAGE, "python", "manage.py",
        )
        docker(*app, "migrate", "--noinput")
        docker(*app, "create_demo", "--namespace", "migration", "--scenario", "warehouse",
               "--output", "/tmp/credentials.json")
        before = manifest(source)
        assert before["boxes"] == 12 and before["history_triggers"] == 2

        with tempfile.TemporaryDirectory(prefix="logistech-migration-") as directory:
            dump = Path(directory) / "synthetic.dump"
            started = time.monotonic()
            with dump.open("wb") as stream:
                docker("exec", source, "pg_dump", "-U", "logistech", "-Fc", "logistech",
                       capture=False, stdout=stream)
            backup_seconds = time.monotonic() - started
            checksum = hashlib.sha256(dump.read_bytes()).hexdigest()
            restore_started = time.monotonic()
            with dump.open("rb") as stream:
                docker("exec", "-i", destination, "pg_restore", "-U", "logistech", "-d",
                       "logistech", "--single-transaction", "--exit-on-error",
                       capture=False, stdin=stream)
            restore_seconds = time.monotonic() - restore_started
            assert hashlib.sha256(dump.read_bytes()).hexdigest() == checksum
            after = manifest(destination)
            assert before == after == manifest(source)
            print(json.dumps({
                "environment": (
                    "local Docker, two independent PostgreSQL containers, synthetic data"
                ),
                "backup_sha256": checksum,
                "backup_bytes": dump.stat().st_size,
                "backup_seconds": round(backup_seconds, 3),
                "restore_seconds": round(restore_seconds, 3),
                "seconds_until_comparison": round(time.monotonic() - started, 3),
                "source_preserved": True,
                "manifest": after,
            }, indent=2))
    finally:
        for name in reversed(started_containers):
            docker("stop", name, check=False)
        docker("network", "rm", network, check=False)


if __name__ == "__main__":
    main()
