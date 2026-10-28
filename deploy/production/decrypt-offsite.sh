#!/bin/bash
set -euo pipefail
umask 077
[[ $# == 4 && -f $1 && -f $2 && -f $3 && ! -e $4 ]] || {
  echo 'Usage: decrypt-offsite.sh ARCHIVE.cms PUBLIC_CERT OFFLINE_PRIVATE_KEY NEW_OUTPUT.dump' >&2; exit 1;
}
tmp=$(mktemp "$(dirname -- "$4")/.decrypted.XXXXXX")
trap 'rm -f -- "$tmp"' EXIT
openssl cms -decrypt -binary -inform DER -in "$1" -recip "$2" -inkey "$3" -out "$tmp"
chmod 600 "$tmp"
mv -n -- "$tmp" "$4"
echo 'Authenticated backup decrypted. Keep the plaintext recovery dump private.'
