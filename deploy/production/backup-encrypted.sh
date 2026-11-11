#!/bin/bash
# Intended for the production operator or a private systemd service.
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"

backup_dir=${F7_BACKUP_DIR:-"$ROOT/backups/f7"}
recipient=${F7_BACKUP_RECIPIENT_CERT:-"$ROOT/.env.f7-secrets/backup-recovery.crt"}
outbox="$backup_dir/encrypted"
install -d -m 0700 "$outbox"
exec 9>"$outbox/.lock"
flock -n 9
shopt -s nullglob
existing=("$outbox"/*.cms)
(( ${#existing[@]} < 14 )) || {
    echo 'Backup outbox is full. Verify off-site copies and review retention.' >&2
    exit 1
}
[[ -r "$recipient" ]] || { echo 'Missing backup recipient certificate.' >&2; exit 1; }
available=$(df -Pk -- "$backup_dir" | awk 'NR==2 {print $4}')
(( available >= 2097152 )) || { echo 'Less than 2 GiB available for backup.' >&2; exit 1; }

result=$(bash "$ROOT/deploy/production/backup.sh")
if [[ ! $result =~ Backup\ complete:\ (logistech-[0-9]{8}T[0-9]{6}Z-[a-f0-9]{8}\.dump) ]]; then
    echo 'Could not identify the newly created backup.' >&2
    exit 1
fi
name=${BASH_REMATCH[1]}
(cd "$backup_dir" && sha256sum -c "$name.sha256")
bash "$ROOT/deploy/production/encrypt-offsite.sh" "$backup_dir/$name" "$recipient" "$outbox/$name.cms"
(cd "$outbox" && sha256sum "$name.cms" > "$name.cms.sha256")
rm -- "$backup_dir/$name" "$backup_dir/$name.sha256"
echo "Encrypted backup ready for off-site copy: $name.cms"
