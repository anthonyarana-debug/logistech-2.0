#!/bin/bash
set -euo pipefail
umask 077
[[ ${STAGING_DB:-} =~ ^restore_[a-z0-9_]{1,40}$ ]] || { echo 'STAGING_DB must start restore_ and contain only lowercase letters, digits, underscores (max 48).' >&2; exit 1; }
[[ ${RESTORE_FILE:-} =~ ^logistech-[A-Za-z0-9-]+\.dump$ ]] || { echo 'RESTORE_FILE must be a backup basename.' >&2; exit 1; }
[[ -f "/backups/$RESTORE_FILE" && -f "/backups/$RESTORE_FILE.sha256" ]] || { echo 'Backup and checksum required.' >&2; exit 1; }
cd /backups
sha256sum --check --status "$RESTORE_FILE.sha256"
export PGPASSWORD
PGPASSWORD=$(cat /run/secrets/db_owner_password)
exists=$(psql --no-password -At --set=ON_ERROR_STOP=1 --set=target="$STAGING_DB" <<'SQL'
SELECT 1 FROM pg_database WHERE datname = :'target';
SQL
)
[[ -z "$exists" ]] || { echo 'Refusing to restore into any existing database.' >&2; exit 1; }
createdb --no-password --owner=logistech_owner "$STAGING_DB"
psql --no-password --set=ON_ERROR_STOP=1 --set=target="$STAGING_DB" <<'SQL'
REVOKE ALL ON DATABASE :"target" FROM PUBLIC;
SQL
pg_restore --no-password --exit-on-error --single-transaction --dbname="$STAGING_DB" "/backups/$RESTORE_FILE"
psql --no-password --dbname="$STAGING_DB" --set=ON_ERROR_STOP=1 --set=target="$STAGING_DB" <<'SQL'
GRANT CONNECT ON DATABASE :"target" TO logistech_app;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM logistech_app;
GRANT USAGE ON SCHEMA public TO logistech_app;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM logistech_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO logistech_app;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM logistech_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO logistech_app;
ALTER DEFAULT PRIVILEGES FOR ROLE logistech_owner IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO logistech_app;
ALTER DEFAULT PRIVILEGES FOR ROLE logistech_owner IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO logistech_app;
SQL
unset PGPASSWORD
echo "Restored into new database $STAGING_DB. Production database untouched."
