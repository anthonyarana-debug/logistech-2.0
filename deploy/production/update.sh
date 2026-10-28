#!/bin/bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
[[ $# == 1 && $1 =~ ^[0-9a-f]{40}$ ]] || { echo 'Usage: update.sh FULL_GIT_COMMIT_SHA (already checked out clean)' >&2; exit 1; }
[[ $(git rev-parse HEAD) == "$1" ]] || { echo 'Checkout must match requested source commit.' >&2; exit 1; }
[[ -z $(git status --porcelain --untracked-files=normal) ]] || { echo 'Checkout must be clean.' >&2; exit 1; }
export SOURCE_REF=$1
"${COMPOSE[@]}" config --quiet
preflight
# Backup before migration. This intentionally fails when no existing DB is running;
# initial installation follows explicit build/up db/run migration/up steps.
bash "$ROOT/deploy/production/backup.sh"
"${COMPOSE[@]}" build db backend proxy
"${COMPOSE[@]}" up -d --wait db
"${COMPOSE[@]}" --profile tools run --rm -T migration
"${COMPOSE[@]}" up -d --wait backend proxy
bash "$ROOT/deploy/production/health.sh"
printf 'Release active: %s. Keep matching SOURCE_REF in public configuration.\n' "$SOURCE_REF"
