#!/usr/bin/env bash
set -euo pipefail
[[ $# == 1 ]] || { echo "usage: $0 ABSENT_NATIVE_RESTORE_PARENT" >&2; exit 2; }
here=$(cd -- "$(dirname -- "$0")" && pwd)
dest=$1
[[ ! -e "$dest" && ! -L "$dest" ]] || { echo "restore destination must be ABSENT" >&2; exit 3; }
[[ $(id -u) == 0 ]] || { echo "root is required to restore original numeric UID/GID" >&2; exit 4; }
(cd -- "$here" && sha256sum -c ARCHIVE_SHA256SUMS)
mkdir -- "$dest"
zstd -dc -- "$here/postcheck.tar.zst" | tar -xpf - --numeric-owner --same-owner --acls --xattrs --selinux --delay-directory-restore -C "$dest"
python3 "$here/VERIFY_RESTORE.py" "$dest/postcheck"
