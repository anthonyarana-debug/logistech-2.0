#!/bin/bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
origin=$(config_value backend CSRF_TRUSTED_ORIGINS)
args=(--fail --silent --show-error --max-time 15)
if [[ ${F7_REHEARSAL:-false} == true ]]; then
  [[ -n ${F7_CADDY_CA:-} && -f "$F7_CADDY_CA" ]] || { echo 'Set F7_CADDY_CA to exported Caddy local CA certificate.' >&2; exit 1; }
  args+=(--cacert "$F7_CADDY_CA")
fi
curl "${args[@]}" "$origin/api/v1/health/"
printf '\nHTTPS health check passed.\n'
