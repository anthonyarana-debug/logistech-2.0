#!/bin/bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
"${COMPOSE[@]}" --profile tools run --rm -T backup
