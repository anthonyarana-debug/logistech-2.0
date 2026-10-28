"""Prove incompatible clusters are rejected before starting PostgreSQL.

Only synthetic directories inside ephemeral containers are used. No real data
volume, secret file, application network or cloud service is mounted.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: check_postgres_platform.py REVIEWED_POSTGRES_IMAGE")
    checks = []
    for platform in ("", "postgres17-debian-glibc"):
        script = (
            'mkdir /tmp/fixture; printf "17\\n" > /tmp/fixture/PG_VERSION; '
            'if [ -n "$1" ]; then printf "%s\\n" "$1" > /tmp/fixture/.logistech-platform; fi; '
            "export PGDATA=/tmp/fixture; exec sh /entrypoint.sh postgres"
        )
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--read-only",
                "--tmpfs",
                "/tmp:size=1m",
                "-v",
                f"{ROOT / 'deploy/production/db-entrypoint.sh'}:/entrypoint.sh:ro",
                "--entrypoint",
                "sh",
                sys.argv[1],
                "-c",
                script,
                "fixture",
                platform,
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert (
            result.returncode == 1
            and "Refusing an incompatible/unmarked" in result.stderr
        )
        checks.append(
            {
                "fixture": "unmarked" if not platform else "incompatible",
                "rejected": True,
            }
        )
    print(json.dumps({"checks": checks, "real_volumes_mounted": False}, indent=2))


if __name__ == "__main__":
    main()
