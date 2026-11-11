"""Exercise dependency loss and rollback using a fresh local project."""

import json
import os
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "logistech-week13-fault-" + uuid.uuid4().hex[:12]
ENV = {
    **os.environ,
    "SOURCE_REF": "week13-local",
    "PUBLIC_DOMAIN": "localhost",
    "PUBLIC_ORIGIN": "https://localhost",
    "POSTGRES_DB": "logistech",
}
COMPOSE = [
    "docker",
    "compose",
    "-p",
    PROJECT,
    "--env-file",
    ".env.f7-candidate",
    "-f",
    "compose.production.yml",
    "-f",
    "compose.production-rehearsal.yml",
    "-f",
    "compose.week13-load.yml",
]
PROBE = """
import json, ssl, urllib.request, urllib.error
request = urllib.request.Request(
    "https://localhost/api/v1/health/",
    headers={"Origin": "https://untrusted.example.test"},
)
try:
    response = urllib.request.urlopen(request, context=ssl.create_default_context(cafile="/root.crt"), timeout=8)
except urllib.error.HTTPError as exc:
    response = exc
print(json.dumps({"status": response.status, "cors": response.headers.get("Access-Control-Allow-Origin")}))
"""


def run(*args, env=ENV):
    return subprocess.run(
        args,
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    ).stdout.strip()


def up(env, *services):
    run(
        *COMPOSE,
        "up",
        "--no-build",
        "--pull",
        "never",
        "-d",
        "--wait",
        *services,
        env=env,
    )


def probe(cert):
    return json.loads(
        run(
            "docker",
            "run",
            "--rm",
            "--network",
            f"container:{PROJECT}-proxy-1",
            "--memory",
            "128m",
            "--cpus",
            "0.5",
            "-v",
            f"{cert}:/root.crt:ro",
            "--entrypoint",
            "python",
            "logistech-backend:week13-local",
            "-c",
            PROBE,
        )
    )


def main():
    baseline = {**ENV, "SOURCE_REF": "f7-security-candidate"}
    evidence = {"project": PROJECT, "kind": "local fault simulation"}
    with tempfile.TemporaryDirectory() as folder:
        cert = Path(folder) / "root.crt"
        try:
            up(ENV, "db")
            run(*COMPOSE, "--profile", "tools", "run", "--rm", "--no-deps", "migration")
            up(ENV, "backend", "proxy")
            run(
                "docker",
                "cp",
                f"{PROJECT}-proxy-1:/data/caddy/pki/authorities/local/root.crt",
                str(cert),
            )
            evidence["healthy"] = probe(cert)
            assert evidence["healthy"] == {"status": 200, "cors": None}
            run(*COMPOSE, "stop", "db")
            evidence["database_down"] = probe(cert)
            assert evidence["database_down"]["status"] == 503
            started = time.monotonic()
            up(ENV, "db", "backend")
            evidence["database_recovered"] = probe(cert)
            evidence["database_recovery_seconds"] = round(time.monotonic() - started, 3)
            assert evidence["database_recovered"]["status"] == 200

            run(*COMPOSE, "stop", "backend")
            evidence["backend_down"] = probe(cert)
            assert evidence["backend_down"]["status"] == 502
            up(ENV, "backend")
            evidence["backend_recovered"] = probe(cert)
            assert evidence["backend_recovered"]["status"] == 200

            run(
                "docker",
                "exec",
                f"{PROJECT}-backend-1",
                "python",
                "manage.py",
                "create_demo",
                "--namespace",
                "rollback13",
                "--output",
                "/tmp/rollback13.json",
            )
            before = run(
                "docker",
                "exec",
                f"{PROJECT}-db-1",
                "psql",
                "-U",
                "logistech_owner",
                "-d",
                "logistech",
                "-Atc",
                "select count(*) from catalog_category",
            )
            up(baseline, "db", "backend", "proxy")
            evidence["rollback_f7"] = probe(cert)
            assert evidence["rollback_f7"]["status"] == 200
            up(ENV, "db", "backend", "proxy")
            evidence["forward_week13"] = probe(cert)
            assert evidence["forward_week13"]["status"] == 200
            after = run(
                "docker",
                "exec",
                f"{PROJECT}-db-1",
                "psql",
                "-U",
                "logistech_owner",
                "-d",
                "logistech",
                "-Atc",
                "select count(*) from catalog_category",
            )
            assert int(before) == int(after) > 0
            evidence["category_count_before_and_after"] = [int(before), int(after)]
        finally:
            run(*COMPOSE, "down")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
