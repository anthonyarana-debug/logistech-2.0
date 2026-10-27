"""Genera secretos locales sin imprimirlos ni sobrescribir configuraciones."""

import os
import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
target = root / ".env"
template = (root / ".env.example").read_text(encoding="utf-8")
value = template.replace(
    "SECRET_KEY=REEMPLAZAR_POR_UN_SECRETO_ALEATORIO",
    f"SECRET_KEY={secrets.token_urlsafe(64)}",
).replace(
    "POSTGRES_PASSWORD=REEMPLAZAR_POR_UN_SECRETO_ALEATORIO",
    f"POSTGRES_PASSWORD={secrets.token_urlsafe(40)}",
)
try:
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError:
    raise SystemExit(".env ya existe; no se modificó.") from None
with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
    stream.write(value)
print(".env local creado. Secretos omitidos de la salida.")
