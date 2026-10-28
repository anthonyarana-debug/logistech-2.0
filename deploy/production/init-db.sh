#!/bin/bash
set -euo pipefail
# psql variables use SQL literal quoting; passwords never become command arguments.
export LOGISTECH_APP_PASSWORD
LOGISTECH_APP_PASSWORD=$(cat /run/postgresql-tls/db_app_password)
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set=ON_ERROR_STOP=1 <<'SQL'
\getenv app_password LOGISTECH_APP_PASSWORD
\getenv database_name POSTGRES_DB
CREATE ROLE logistech_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT PASSWORD :'app_password';
REVOKE ALL ON DATABASE :"database_name" FROM PUBLIC;
GRANT CONNECT ON DATABASE :"database_name" TO logistech_app;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO logistech_app;
ALTER DEFAULT PRIVILEGES FOR ROLE logistech_owner IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO logistech_app;
ALTER DEFAULT PRIVILEGES FOR ROLE logistech_owner IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO logistech_app;
SQL
unset LOGISTECH_APP_PASSWORD
