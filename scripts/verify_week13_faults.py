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
    "SOURCE_REF": os.environ.get("FAULT_TEST_SOURCE_REF", "week13-local"),
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
    "https://localhost/api/v1/health/?private=local-log-probe",
    headers={"Origin": "https://untrusted.example.test", "X-Probe": "local-log-probe"},
)
try:
    context = ssl.create_default_context(cafile="/root.crt")
    response = urllib.request.urlopen(request, context=context, timeout=8)
except urllib.error.HTTPError as exc:
    response = exc
print(json.dumps({
    "status": response.status,
    "cors": response.headers.get("Access-Control-Allow-Origin"),
    "request_id": response.headers.get("X-Request-ID"),
}))
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
            f"logistech-backend:{ENV['SOURCE_REF']}",
            "-c",
            PROBE,
        )
    )


def await_healthy(cert):
    deadline = time.monotonic() + 25
    last_error = ""
    while time.monotonic() < deadline:
        try:
            response = probe(cert)
            if response["status"] == 200:
                return response
            last_error = f"HTTP {response['status']}"
        except subprocess.CalledProcessError as error:
            last_error = error.stderr.strip()
        time.sleep(0.5)
    raise RuntimeError(f"HTTPS readiness deadline expired: {last_error}")


def failure_record(request_id):
    logs = run("docker", "logs", f"{PROJECT}-backend-1")
    for line in logs.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("request_id") == request_id and event.get("status") == 503:
            return event
    raise AssertionError("No JSON access log found for the database failure")


def verify_proxy_error_logs():
    result = subprocess.run(
        ["docker", "logs", f"{PROJECT}-proxy-1"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        check=True, timeout=15,
    )
    logs = result.stdout + result.stderr
    errors = []
    for line in logs.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("status") == 502:
            errors.append(event)
    assert errors and all("request" not in event for event in errors)
    assert "local-log-probe" not in logs
    return {"filtered_502_records": len(errors)}


def copy_local_ca(cert):
    source = f"{PROJECT}-proxy-1:/data/caddy/pki/authorities/local/root.crt"
    for _ in range(20):
        try:
            run("docker", "cp", source, str(cert))
            return
        except subprocess.CalledProcessError as error:
            if "could not find" not in error.stderr.lower():
                raise
            time.sleep(0.5)
    raise RuntimeError("Caddy did not create its local CA before the deadline")


def main():
    baseline = {**ENV, "SOURCE_REF": "f7-security-candidate"}
    evidence = {"project": PROJECT, "kind": "local fault simulation"}
    with tempfile.TemporaryDirectory() as folder:
        cert = Path(folder) / "root.crt"
        try:
            up(ENV, "db")
            run(*COMPOSE, "--profile", "tools", "run", "--rm", "--no-deps", "migration")
            up(ENV, "backend", "proxy")
            copy_local_ca(cert)
            evidence["healthy"] = await_healthy(cert)
            assert evidence["healthy"]["status"] == 200
            assert evidence["healthy"]["cors"] is None
            run(*COMPOSE, "stop", "db")
            evidence["database_down"] = probe(cert)
            assert evidence["database_down"]["status"] == 503
            if evidence["database_down"]["request_id"]:
                evidence["database_failure_access_log"] = failure_record(
                    evidence["database_down"]["request_id"]
                )
            started = time.monotonic()
            up(ENV, "db", "backend")
            evidence["database_recovered"] = await_healthy(cert)
            evidence["database_recovery_seconds"] = round(time.monotonic() - started, 3)
            assert evidence["database_recovered"]["status"] == 200

            run(*COMPOSE, "stop", "backend")
            evidence["backend_down"] = probe(cert)
            assert evidence["backend_down"]["status"] == 502
            if os.environ.get("FAULT_TEST_CHECK_PROXY_LOGS") == "true":
                evidence["proxy_logs"] = verify_proxy_error_logs()
            started = time.monotonic()
            up(ENV, "backend")
            evidence["backend_recovered"] = await_healthy(cert)
            evidence["backend_recovery_seconds"] = round(time.monotonic() - started, 3)
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
            evidence["rollback_f7"] = await_healthy(cert)
            assert evidence["rollback_f7"]["status"] == 200
            up(ENV, "db", "backend", "proxy")
            evidence["forward_week13"] = await_healthy(cert)
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
