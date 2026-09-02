#!/usr/bin/env bash
# Checksum-verifying Route-E bootstrap. Actual execution is M4A-C-only.
set -euo pipefail
url='https://github.com/NVlabs/NVBit/releases/download/v1.7.6/nvbit-Linux-x86_64-1.7.6.tar.bz2'
sha='dba61708b702ff4562343716bb8b38a2d14aae5991b9719aece097afe505467f'
framework_root='' work_root='' cuda_home='' dry_run=0
while [[ $# -gt 0 ]]; do case "$1" in --framework-root) framework_root=$2;shift 2;; --work-root) work_root=$2;shift 2;; --cuda-home) cuda_home=$2;shift 2;; --dry-run) dry_run=1;shift;; *) echo "usage: $0 --framework-root DIR --work-root DIR --cuda-home DIR [--dry-run]" >&2;exit 2;; esac;done
[[ -n "$framework_root" && -n "$work_root" && -n "$cuda_home" ]] || { echo 'missing required argument' >&2;exit 2; }
[[ $dry_run == 1 || ${M4A_C_AUTHORIZED:-0} == 1 ]] || { echo 'BLOCKED: bootstrap execution requires future M4A-C authorization; --dry-run is safe now' >&2;exit 3; }
archive="$work_root/bootstrap/nvbit-Linux-x86_64-1.7.6.tar.bz2"; release="$framework_root/util/tracer_nvbit/nvbit_release"
if [[ $dry_run == 1 ]]; then printf 'DRY-RUN url=%s\nsha256=%s\narchive=%s\nrelease=%s\nCUDA_HOME=%s\n' "$url" "$sha" "$archive" "$release" "$cuda_home"; exit 0;fi
[[ -x "$cuda_home/bin/nvcc" ]] || { echo "missing explicit nvcc: $cuda_home/bin/nvcc" >&2;exit 1; }
mkdir -p "$(dirname "$archive")"; curl --fail --location --retry 3 --output "$archive" "$url"; echo "$sha  $archive" | sha256sum --check --status || { echo 'NVBit checksum mismatch' >&2;exit 1; }
rm -rf "$release"; mkdir -p "$release"; tar -xjf "$archive" -C "$release" --strip-components=1
printf '%s  %s\n' "$sha" "$archive" > "$work_root/bootstrap/nvbit-1.7.6.sha256"
CUDA_HOME="$cuda_home" make -C "$framework_root/util/tracer_nvbit/tracer_tool" |& tee "$work_root/bootstrap/tracer-build.log"
CUDA_HOME="$cuda_home" make -C "$framework_root/util/tracer_nvbit/tracer_tool/traces-processing" |& tee "$work_root/bootstrap/postprocess-build.log"
"$cuda_home/bin/nvcc" --version > "$work_root/bootstrap/nvcc-version.txt"; echo 'PASS Route-E NVBit bootstrap'
