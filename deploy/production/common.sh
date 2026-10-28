#!/bin/bash
set -euo pipefail
umask 077
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)
cd -- "$ROOT"
ENV_FILE=${F7_ENV_FILE:-.env.f7}
[[ -f "$ENV_FILE" ]] || { echo 'Missing public configuration (.env.f7 or F7_ENV_FILE).' >&2; exit 1; }
PROJECT=${F7_PROJECT:-logistech-production}
if [[ ${F7_REHEARSAL:-false} == true ]]; then
  PROJECT=${F7_PROJECT:-logistech-f7-rehearsal}
fi
COMPOSE=(docker compose -p "$PROJECT" --env-file "$ENV_FILE" -f "$ROOT/compose.production.yml")
if [[ ${F7_REHEARSAL:-false} == true ]]; then
  COMPOSE+=(-f "$ROOT/compose.production-rehearsal.yml")
fi
# Read public values with Compose's parser; never source an arbitrary dotenv file.
config_value() {
  "${COMPOSE[@]}" config --format json | python3 -c 'import json,sys; c=json.load(sys.stdin); print(c["services"][sys.argv[1]]["environment"][sys.argv[2]])' "$1" "$2"
}
preflight() {
  "${COMPOSE[@]}" config --format json | python3 "$ROOT/deploy/production/preflight.py" "${F7_REHEARSAL:-false}"
}
