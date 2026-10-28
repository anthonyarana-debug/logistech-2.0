#!/bin/sh
set -eu
install -d -m 700 -o postgres -g postgres /run/postgresql-tls
install -m 600 -o postgres -g postgres /run/secrets/postgresql.key /run/postgresql-tls/server.key
install -m 644 -o postgres -g postgres /run/secrets/postgresql.crt /run/postgresql-tls/server.crt
install -m 600 -o postgres -g postgres /run/secrets/db_owner_password /run/postgresql-tls/db_owner_password
install -m 600 -o postgres -g postgres /run/secrets/db_app_password /run/postgresql-tls/db_app_password
export POSTGRES_PASSWORD_FILE=/run/postgresql-tls/db_owner_password
exec /usr/local/bin/docker-entrypoint.sh "$@"
