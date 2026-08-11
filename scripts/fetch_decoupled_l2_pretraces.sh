#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/fetch_decoupled_l2_pretraces.sh [--suite ubench|cudasdk|all]
       [--dest DIR] [--min-free-gib N]

Downloads public Tesla-V100 SASS trace archives, verifies their gzip/tar
structure, and extracts them below DIR.  Archives and extracted traces are
kept under ignored hw_run/ storage; neither is source-controlled.

The script reserves MIN-FREE-GIB (default: 100) before download and
extraction.  It reads the archive content length before downloading and sums
the uncompressed members before extraction, so either action cannot take the
filesystem below that reserve.
EOF
}

suite="all"
dest=""
min_free_gib=100
while [[ $# -gt 0 ]]; do
  case "$1" in
    --suite) suite="$2"; shift 2 ;;
    --dest) dest="$2"; shift 2 ;;
    --min-free-gib) min_free_gib="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "$min_free_gib" =~ ^[0-9]+$ ]] || {
  echo "error: --min-free-gib must be a nonnegative integer" >&2; exit 2;
}
case "$suite" in ubench|cudasdk|all) ;; *)
  echo "error: unsupported suite $suite" >&2; exit 2 ;;
esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$dest" ]]; then
  dest="$repo_root/hw_run/decoupled-l2-pretraces"
fi
mkdir -p "$dest"
dest="$(cd "$dest" && pwd)"
min_free_kib=$((min_free_gib * 1024 * 1024))

available_kib() {
  df -Pk "$dest" | awk 'NR == 2 { print $4 }'
}

require_free_kib() {
  local required_kib="$1"
  local action="$2"
  local available
  available="$(available_kib)"
  if (( available < required_kib )); then
    printf 'error: refusing %s: need %d GiB free, have %d GiB\n' \
      "$action" \
      "$(((required_kib + 1024 * 1024 - 1) / (1024 * 1024)))" \
      "$((available / (1024 * 1024)))" >&2
    exit 1
  fi
}

remote_size_kib() {
  local url="$1"
  local bytes
  bytes="$(curl --fail --silent --show-error --location --head "$url" | \
    awk 'BEGIN { IGNORECASE = 1 } /^content-length:/ { value = $2; gsub("\\r", "", value) } END { if (value ~ /^[0-9]+$/) print value }')"
  [[ -n "$bytes" ]] || {
    echo "error: unable to determine Content-Length for $url" >&2
    exit 1
  }
  printf '%s\n' "$(((bytes + 1023) / 1024))"
}

base_url="https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/latest"

fetch_one() {
  local name="$1"
  local archive="$dest/$name.tgz"
  local url="$base_url/$name.tgz"
  local archive_kib

  archive_kib="$(remote_size_kib "$url")"
  # This reserves the full archive even when --continue can reuse a partial
  # download, which keeps the check simple and safely conservative.
  require_free_kib "$((min_free_kib + archive_kib))" "download of $name"
  if command -v aria2c >/dev/null 2>&1; then
    aria2c --continue=true --file-allocation=none \
      --max-connection-per-server=8 --split=8 \
      --dir "$dest" --out "$name.tgz" "$url"
  else
    curl --fail --location --continue-at - --output "$archive" "$url"
  fi
  tar -tzf "$archive" >/dev/null
  # GNU tar's verbose layout is mode owner/group size date path.  Summing the
  # size column is deliberately conservative when --skip-old-files will omit
  # already-extracted members.
  local extract_kib
  extract_kib="$(tar -tvzf "$archive" | awk '{ bytes += $3 } END { print int((bytes + 1023) / 1024) }')"
  require_free_kib "$((min_free_kib + extract_kib))" "extraction of $name"
  tar --extract --gzip --skip-old-files --file "$archive" --directory "$dest"
  require_free_kib "$min_free_kib" "post-extraction reserve for $name"
}

if [[ "$suite" == all || "$suite" == ubench ]]; then
  fetch_one ubench
fi
if [[ "$suite" == all || "$suite" == cudasdk ]]; then
  fetch_one cudasdk
fi
