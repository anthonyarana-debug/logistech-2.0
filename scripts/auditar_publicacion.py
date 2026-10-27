"""Audita Git local sin red ni mostrar valores privados. No crea remotos ni hace push."""

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = {".env.example", "deploy/production.env.example"}
PATTERNS = {
    "token_github": rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b",
    "clave_aws": rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "jwt_literal": rb"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b",
    "clave_privada": rb"^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\r?$",
    "clave_openai": rb"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}\b",
    "hash_password_django": rb"\bpbkdf2_sha256\$[0-9]+\$[A-Za-z0-9]+\$[A-Za-z0-9+/=]{30,}",
}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sensitive_path(name):
    if name in TEMPLATES:
        return False
    path = PurePosixPath(name.lower())
    base = path.name
    return (
        base == ".env"
        or base.startswith((".env.", ".envrc", "client_secret", "service-account"))
        or base
        in {
            ".npmrc",
            ".netrc",
            ".pypirc",
            ".git-credentials",
            "credentials.json",
            "id_rsa",
            "id_ed25519",
        }
        or base.startswith("credentials-")
        or base.endswith(
            (
                ".sqlite",
                ".sqlite3",
                ".db",
                ".sql",
                ".sql.gz",
                ".dump",
                ".backup",
                ".pem",
                ".key",
                ".p12",
                ".pfx",
                ".bundle",
            )
        )
        or any(
            part
            in {
                ".aws",
                ".ssh",
                "secrets",
                "backups",
                "dumps",
                "volumes",
                "docker-volumes",
                "postgres_data",
                "pgdata",
                "node_modules",
                ".venv",
                ".venv-load",
            }
            for part in path.parts
        )
    )


def local_values():
    values = set()
    for path in ROOT.glob(".env*"):
        if not path.is_file() or path.name == ".env.example":
            continue
        text = path.read_text(encoding="utf-8-sig")
        if path.suffix == ".json":
            data = json.loads(text)
            users = data.get("users", {})
            for user in users.values() if isinstance(users, dict) else users:
                for key in ("password", "access", "refresh", "token"):
                    if isinstance(user.get(key), str) and len(user[key]) >= 16:
                        values.add(user[key].encode())
        else:
            for line in text.splitlines():
                if "=" not in line or line.lstrip().startswith("#"):
                    continue
                key, value = line.split("=", 1)
                if any(part in key.upper() for part in ("SECRET", "PASSWORD", "TOKEN", "API_KEY")):
                    value = value.strip().strip("\"'")
                    if len(value) >= 16 and not value.startswith("REEMPLAZAR_"):
                        values.add(value.encode())
    return values


def audit():
    commits = git("rev-list", "--all").decode().splitlines()
    paths = set()
    for commit in commits:
        paths.update(
            filter(None, git("ls-tree", "-r", "-z", "--name-only", commit).decode().split("\0"))
        )
    paths.update(filter(None, git("ls-files", "-z").decode().split("\0")))
    findings = [
        {"tipo": "ruta_sensible", "ruta": name} for name in sorted(paths) if sensitive_path(name)
    ]
    objects = {}
    for line in git("rev-list", "--objects", "--all").decode().splitlines():
        oid, _, name = line.partition(" ")
        objects[oid] = name
    for line in filter(None, git("ls-files", "-s", "-z").decode().split("\0")):
        metadata, name = line.split("\t", 1)
        objects[metadata.split()[1]] = name
    inventory = subprocess.run(
        ["git", "cat-file", "--batch-check"],
        input=("\n".join(objects) + "\n").encode(),
        capture_output=True,
        cwd=ROOT,
        check=True,
    )
    private_values = local_values()
    blobs, largest = 0, 0
    for line in inventory.stdout.decode().splitlines():
        oid, kind, length = line.split()
        if kind != "blob":
            continue
        blobs += 1
        size = int(length)
        largest = max(largest, size)
        name = objects[oid]
        if size >= 90 * 1024 * 1024:
            findings.append({"tipo": "archivo_grande_requiere_revision", "ruta": name})
            continue
        data = git("cat-file", "blob", oid)
        if data.startswith((b"SQLite format 3\x00", b"PGDMP", b"-- PostgreSQL database dump")):
            findings.append({"tipo": "base_o_dump_por_contenido", "ruta": name, "objeto": oid})
        if any(value in data for value in private_values):
            findings.append({"tipo": "valor_privado_local", "ruta": name, "objeto": oid})
        for label, pattern in PATTERNS.items():
            if re.search(pattern, data, re.M):
                findings.append({"tipo": label, "ruta": name, "objeto": oid})
    checks = [
        ".env",
        ".env.demo.json",
        ".env.f5-demo.json",
        ".env.load-futuro.json",
        ".envrc",
        ".npmrc",
        ".aws/credentials",
        ".ssh/id_ed25519",
        "credentials.json",
        "secrets/token.json",
        "backups/base.dump",
        "volumes/postgres/PG_VERSION",
        "postgres_data/base/archivo",
        "pgdata/base/archivo",
        "datos.sqlite3",
        "base.sql",
        "privada.pem",
        "privada.key",
        ".venv-load/archivo",
        "frontend/node_modules/a.js",
    ]
    unprotected = []
    for name in checks:
        run = subprocess.run(["git", "check-ignore", "--no-index", "-q", "--", name], cwd=ROOT)
        if run.returncode != 0:
            unprotected.append(name)
    findings.extend({"tipo": "exclusion_faltante", "ruta": name} for name in unprotected)
    return {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "alcance": "Índice y blobs alcanzables desde todas las ramas/etiquetas locales; sin red",
        "commits": len(commits),
        "rutas_historicas": len(paths),
        "blobs": blobs,
        "mayor_blob_bytes": largest,
        "exclusiones_comprobadas": len(checks),
        "hallazgos": findings,
        "limites": "Patrones y valores privados locales conocidos; no certificación absoluta. "
        "Imágenes requieren revisión visual. Contraseñas sintéticas de tests no son cuentas DEMO.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit()
    if args.output:
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(bool(report["hallazgos"]))
