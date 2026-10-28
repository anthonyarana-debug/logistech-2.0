#!/bin/bash
set -euo pipefail
umask 077
mkdir -p /backups
chmod 700 /backups
export PGPASSWORD
PGPASSWORD=$(cat /run/secrets/db_owner_password)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
name="logistech-${stamp}-$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n').dump"
tmp=$(mktemp /backups/.backup.XXXXXX)
trap 'rm -f -- "$tmp"' EXIT
pg_dump --format=custom --file="$tmp" --no-password
pg_restore --list "$tmp" >/dev/null
sync -f "$tmp"
mv -n -- "$tmp" "/backups/$name"
cd /backups
sha256sum "$name" > "$name.sha256"
sync -f /backups
unset PGPASSWORD
echo "Backup complete: $name (retained; no automatic deletion)."
