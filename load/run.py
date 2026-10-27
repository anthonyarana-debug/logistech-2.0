"""Orquesta humo/A/B, CSV y muestras de recursos; nunca apunta fuera de loopback."""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
compose = [
    "docker",
    "compose",
    "-p",
    "logistech-f5",
    "-f",
    "docker-compose.yml",
    "-f",
    "compose.validation.yml",
]
parser = argparse.ArgumentParser()
parser.add_argument("--scenario", choices=["smoke", "a-50", "b-100"], required=True)
args = parser.parse_args()
users, rate, warmup, duration = {
    "smoke": (2, 1, 5, 20),
    "a-50": (50, 5, 30, 210),
    "b-100": (100, 10, 30, 210),
}[args.scenario]
stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
namespace = f"f5load-{args.scenario}-{stamp}"
private = root / f".env.load-{namespace}.json"
container_path = f"/tmp/{namespace}.json"
output = root / "docs/evidencias/carga-fase5" / f"{args.scenario}-{stamp}"
output.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(
    compose
    + [
        "exec",
        "-T",
        "backend",
        "python",
        "-m",
        "tools.preparar_carga",
        "--namespace",
        namespace,
        "--users",
        str(users),
        "--output",
        container_path,
    ],
    cwd=root,
    check=True,
)
subprocess.run(compose + ["cp", f"backend:{container_path}", str(private)], cwd=root, check=True)
if os.name == "nt":
    owner = subprocess.check_output(["whoami"], text=True).strip()
    subprocess.run(
        ["icacls", str(private), "/inheritance:r", "/grant:r", f"{owner}:(F)"],
        capture_output=True,
        check=True,
    )
environment = {
    **os.environ,
    "F5_MANIFEST": str(private),
    "F5_WARMUP": str(warmup),
    "F5_SUMMARY": f"{output}_summary.json",
}
command = [
    sys.executable,
    "-m",
    "locust",
    "-f",
    "load/locustfile.py",
    "--headless",
    "--host",
    "http://127.0.0.1:8001",
    "-u",
    str(users),
    "-r",
    str(rate),
    "--run-time",
    f"{duration}s",
    "--json-file",
    f"{output}_stats_final",
    "--html",
    f"{output}.html",
    "--only-summary",
    "--stop-timeout",
    "0",
]
resources = []
try:
    with Path(f"{output}_console.txt").open("w", encoding="utf-8") as console:
        process = subprocess.Popen(
            command, cwd=root, env=environment, stdout=console, stderr=subprocess.STDOUT
        )
        while process.poll() is None:
            probe = subprocess.run(
                [
                    "docker",
                    "stats",
                    "--no-stream",
                    "--format",
                    "{{json .}}",
                    "logistech-f5-backend-1",
                    "logistech-f5-db-1",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            resources.append(
                {
                    "fecha_utc": datetime.now(timezone.utc).isoformat(),
                    "contenedores": [
                        json.loads(line) for line in probe.stdout.splitlines() if line
                    ],
                }
            )
            time.sleep(3)
    code = process.returncode
finally:
    subprocess.run(
        compose
        + [
            "exec",
            "-T",
            "backend",
            "python",
            "-m",
            "tools.preparar_carga",
            "--namespace",
            namespace,
            "--retire",
            "--output",
            container_path,
        ],
        cwd=root,
        check=True,
    )
    private.unlink(missing_ok=True)
Path(f"{output}_resources.json").write_text(
    json.dumps(resources, indent=2) + "\n", encoding="utf-8"
)
print(
    json.dumps(
        {
            "escenario": args.scenario,
            "codigo_locust": code,
            "evidencia": str(output.relative_to(root)),
        }
    )
)
raise SystemExit(code)
