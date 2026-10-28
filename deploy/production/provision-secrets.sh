#!/bin/bash
set -euo pipefail
umask 077
target=${1:-/secrets}
[[ "$target" == /* && -d "$target" ]] || { echo 'Use an existing absolute secrets directory.' >&2; exit 1; }
chmod 700 "$target"
for name in django_secret_key db_owner_password db_app_password postgresql-ca.key postgresql-ca.pem postgresql.key postgresql.crt; do
  [[ ! -e "$target/$name" ]] || { echo "Refusing to overwrite $name" >&2; exit 1; }
done
# Offline CA key stays on the operator machine; never mount it in production.
openssl rand -hex 48 > "$target/django_secret_key"
openssl rand -hex 32 > "$target/db_owner_password"
openssl rand -hex 32 > "$target/db_app_password"
openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 3650 \
  -subj /CN=Logistech-PostgreSQL-CA -keyout "$target/postgresql-ca.key" -out "$target/postgresql-ca.pem" 2>/dev/null
openssl req -newkey rsa:3072 -sha256 -nodes -subj /CN=db \
  -keyout "$target/postgresql.key" -out "$target/postgresql.csr" 2>/dev/null
printf 'subjectAltName=DNS:db\nextendedKeyUsage=serverAuth\nkeyUsage=digitalSignature,keyEncipherment\n' > "$target/db.ext"
openssl x509 -req -sha256 -days 365 -in "$target/postgresql.csr" \
  -CA "$target/postgresql-ca.pem" -CAkey "$target/postgresql-ca.key" -CAcreateserial \
  -extfile "$target/db.ext" -out "$target/postgresql.crt" 2>/dev/null
rm -- "$target/postgresql.csr" "$target/db.ext" "$target/postgresql-ca.srl"
chmod 600 "$target"/*
# Container app UID reads only its individual mounted secret files.
chown 10001:10001 "$target/django_secret_key" "$target/db_owner_password" "$target/db_app_password"
# The CA is public verification material (not a credential), readable by app UID.
chmod 644 "$target/postgresql-ca.pem" "$target/postgresql.crt"
echo 'Created secrets and db SAN certificate. Protect offline CA key; no values printed.'
