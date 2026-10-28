#!/bin/bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
[[ $# == 2 ]] || { echo 'Usage: restore.sh restore_unique_database backup_basename.dump' >&2; exit 1; }
export STAGING_DB=$1 RESTORE_FILE=$2
"${COMPOSE[@]}" --profile tools run --rm -T restore
