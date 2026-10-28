#!/bin/bash
set -euo pipefail
umask 077
[[ $# == 3 && -f $1 && -f $2 && ! -e $3 ]] || {
  echo 'Usage: encrypt-offsite.sh DUMP PUBLIC_RECIPIENT_CERT NEW_OUTPUT.cms' >&2; exit 1;
}
tmp=$(mktemp "$(dirname -- "$3")/.encrypted.XXXXXX")
trap 'rm -f -- "$tmp"' EXIT
openssl cms -encrypt -binary -aes-256-gcm -in "$1" -out "$tmp" -outform DER "$2"
chmod 600 "$tmp"
mv -n -- "$tmp" "$3"
echo 'Authenticated encrypted backup created. Copy only the encrypted archive off-site.'
