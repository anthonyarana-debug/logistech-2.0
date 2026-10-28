"""Read-only production rehearsal checks; no AWS, DNS writes or database resets.

Run after the isolated F7 stack is installed. The public-domain checks only
render configuration; they never contact that hostname or request certificates.
"""

import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = [
    "docker",
    "compose",
    "-p",
    os.environ.get("F7_PROJECT", "logistech-f7-rehearsal"),
    "--env-file",
    os.environ.get("F7_ENV_FILE", ".env.f7"),
    "-f",
    "compose.production.yml",
    "-f",
    "compose.production-rehearsal.yml",
]


def main():
    checks = []

    def run(label, command, **kwargs):
        result = subprocess.run(
            command,
            check=False,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            **kwargs,
        )
        checks.append(
            {
                "check": label,
                "exit_code": result.returncode,
                "output": (result.stdout + result.stderr).strip(),
            }
        )
        if result.returncode:
            raise RuntimeError(f"Check failed: {label}")
        return result

    run(
        "linux_engine", ["docker", "info", "--format", "{{.OSType}} {{.ServerVersion}}"]
    )
    run("compose", COMPOSE + ["config", "--quiet"])
    run(
        "django_deploy",
        COMPOSE + ["exec", "-T", "backend", "python", "manage.py", "check", "--deploy"],
    )
    run(
        "migrations_applied",
        COMPOSE
        + ["exec", "-T", "backend", "python", "manage.py", "migrate", "--check"],
    )
    run(
        "migration_drift",
        COMPOSE
        + [
            "exec",
            "-T",
            "backend",
            "python",
            "manage.py",
            "makemigrations",
            "--check",
            "--dry-run",
        ],
    )
    run(
        "caddy_configuration",
        COMPOSE
        + [
            "exec",
            "-T",
            "proxy",
            "caddy",
            "validate",
            "--config",
            "/etc/caddy/Caddyfile",
        ],
    )
    run(
        "database_privileges_integrity",
        COMPOSE
        + [
            "exec",
            "-T",
            "backend",
            "python",
            "manage.py",
            "shell",
            "-c",
            (ROOT / "scripts/production_database_check.py").read_text(encoding="utf-8"),
        ],
    )
    # Synthetic contact is a parser fixture, not the future operator's email.
    environment = {
        **os.environ,
        "PUBLIC_DOMAIN": "logistech.stackpe.online",
        "PUBLIC_ORIGIN": "https://logistech.stackpe.online",
        "ACME_EMAIL": "parser-fixture@stackpe.online",
        "SOURCE_REF": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
    }
    config = subprocess.check_output(
        [
            "docker",
            "compose",
            "--env-file",
            os.environ.get("F7_ENV_FILE", ".env.f7"),
            "-f",
            "compose.production.yml",
            "config",
            "--format",
            "json",
        ],
        cwd=ROOT,
        env=environment,
        text=True,
    )
    run(
        "public_domain_preflight_render_only",
        [sys.executable, "deploy/production/preflight.py", "false"],
        input=config,
    )
    bad = json.loads(config)
    bad["services"]["backend"]["environment"]["CSRF_TRUSTED_ORIGINS"] = (
        "https://other.stackpe.online"
    )
    rejected = subprocess.run(
        [sys.executable, "deploy/production/preflight.py", "false"],
        check=False,
        cwd=ROOT,
        input=json.dumps(bad),
        text=True,
        capture_output=True,
    )
    assert rejected.returncode != 0, "Mismatched public origin accepted"
    checks.append({"check": "mismatched_origin_rejected", "exit_code": 0})
    context = ssl.create_default_context(
        cafile=os.environ.get(
            "F7_CADDY_CA", str(ROOT / ".env.f7-secrets/caddy-local-ca.pem")
        )
    )
    routes = {}
    for path, expected in [
        ("/", 200),
        ("/app/receptions", 200),
        ("/api/v1/health/", 200),
        ("/api/v1/missing/", 404),
        ("/admin/", 404),
        ("/assets/missing.js", 404),
        ("/static/admin/css/base.css", 200),
    ]:
        try:
            response = urllib.request.urlopen(
                "https://localhost:8447" + path, context=context, timeout=10
            )
        except urllib.error.HTTPError as error:
            response = error
        assert response.status == expected, (path, response.status)
        routes[path] = {
            "status": response.status,
            "content_type": response.headers.get("Content-Type"),
        }
        if path.startswith("/api/"):
            assert "application/json" in response.headers.get("Content-Type", "")
        response.close()
    try:
        urllib.request.urlopen("https://localhost:8447/api/v1/health/", timeout=10)
    except urllib.error.URLError as error:
        assert isinstance(error.reason, ssl.SSLCertVerificationError)
    else:
        raise AssertionError("Local private CA was unexpectedly trusted globally")
    checks.append(
        {
            "check": "https_routes_with_verified_ca",
            "exit_code": 0,
            "routes": routes,
            "untrusted_private_ca_rejected": True,
        }
    )
    report = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "public_target": "https://logistech.stackpe.online",
        "public_deployment": False,
        "checks": checks,
    }
    destination = ROOT / os.environ.get(
        "F7_EVIDENCE_REPORT", "docs/evidencias/fase7/local-verification.json"
    )
    destination.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"{len(checks)} checks passed. Public-domain parser only; no external deployment."
    )


if __name__ == "__main__":
    main()
