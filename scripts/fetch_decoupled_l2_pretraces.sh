#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/fetch_decoupled_l2_pretraces.sh [--suite ubench|cudasdk|all]
       [--dest DIR]

Downloads public Tesla-V100 SASS trace archives, verifies their gzip/tar
structure, and extracts them below DIR.  Archives and extracted traces are
kept under ignored hw_run/ storage; neither is source-controlled.
EOF
}

suite="all"
dest=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --suite) suite="$2"; shift 2 ;;
    --dest) dest="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
case "$suite" in ubench|cudasdk|all) ;; *)
  echo "error: unsupported suite $suite" >&2; exit 2 ;;
esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$dest" ]]; then
  dest="$repo_root/hw_run/decoupled-l2-pretraces"
fi
mkdir -p "$dest"
dest="$(cd "$dest" && pwd)"

base_url="https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/latest"

fetch_one() {
  local name="$1"
  local archive="$dest/$name.tgz"
  local url="$base_url/$name.tgz"

  if command -v aria2c >/dev/null 2>&1; then
    aria2c --continue=true --file-allocation=none \
      --max-connection-per-server=8 --split=8 \
      --dir "$dest" --out "$name.tgz" "$url"
  else
    curl --fail --location --continue-at - --output "$archive" "$url"
  fi
  tar -tzf "$archive" >/dev/null
  tar --extract --gzip --skip-old-files --file "$archive" --directory "$dest"
}

if [[ "$suite" == all || "$suite" == ubench ]]; then
  fetch_one ubench
fi
if [[ "$suite" == all || "$suite" == cudasdk ]]; then
  fetch_one cudasdk
fi
