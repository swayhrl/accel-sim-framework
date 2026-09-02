#!/usr/bin/env bash
# Checksum-verifying Route-E bootstrap. Actual execution is M4A-C-only.
set -euo pipefail
url='https://github.com/NVlabs/NVBit/releases/download/v1.7.6/nvbit-Linux-x86_64-1.7.6.tar.bz2'
sha='dba61708b702ff4562343716bb8b38a2d14aae5991b9719aece097afe505467f'
framework_root='' work_root='' cuda_home='' dry_run=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --framework-root) framework_root=$2; shift 2 ;;
    --work-root) work_root=$2; shift 2 ;;
    --cuda-home) cuda_home=$2; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    *) echo "usage: $0 --framework-root DIR --work-root DIR --cuda-home DIR [--dry-run]" >&2; exit 2 ;;
  esac
done
[[ -n "$framework_root" && -n "$work_root" && -n "$cuda_home" ]] || { echo 'missing required argument' >&2; exit 2; }
[[ $dry_run == 1 || ${M4A_C_AUTHORIZED:-0} == 1 ]] || { echo 'BLOCKED: bootstrap execution requires future M4A-C authorization; --dry-run is safe now' >&2; exit 3; }
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
archive="$work_root/bootstrap/nvbit-Linux-x86_64-1.7.6.tar.bz2"; release="$framework_root/util/tracer_nvbit/nvbit_release"
nvcc="$cuda_home/bin/nvcc"; ptxas="$cuda_home/bin/ptxas"
if [[ $dry_run == 1 ]]; then
  printf 'DRY-RUN url=%s\nsha256=%s\narchive=%s\nrelease=%s\nCUDA_HOME=%s\nNVCC=%s\nPTXAS=%s\n' "$url" "$sha" "$archive" "$release" "$cuda_home" "$nvcc" "$ptxas"
  exit 0
fi
[[ -x "$nvcc" && -x "$ptxas" ]] || { echo "missing explicit nvcc/ptxas under $cuda_home/bin" >&2; exit 1; }
mkdir -p "$(dirname "$archive")"
if ! test -f "$archive" || ! echo "$sha  $archive" | sha256sum --check --status; then
  # A verified archive may be staged from the main development host when the
  # rental image cannot reach GitHub.  Never trust an unverified cache entry.
  partial="$archive.partial"
  curl --fail --location --retry 3 --output "$partial" "$url"
  echo "$sha  $partial" | sha256sum --check --status || { echo 'NVBit checksum mismatch' >&2; exit 1; }
  mv "$partial" "$archive"
fi
echo "$sha  $archive" | sha256sum --check --status || { echo 'NVBit checksum mismatch' >&2; exit 1; }
rm -rf "$release"; mkdir -p "$release"; tar -xjf "$archive" -C "$release" --strip-components=1
printf '%s  %s\n' "$sha" "$archive" > "$work_root/bootstrap/nvbit-1.7.6.sha256"
"$script_dir/build_nvbit_with_toolchain.sh" --framework-root "$framework_root" --work-root "$work_root" --cuda-home "$cuda_home"
echo 'PASS Route-E NVBit bootstrap'
