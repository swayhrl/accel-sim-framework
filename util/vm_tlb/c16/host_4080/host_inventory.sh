#!/usr/bin/env bash
# Read-only host-arrival inventory. Do not run during CPU-only source preparation.
set -euo pipefail
umask 077

usage() { echo "usage: $0 --collect --output <receipt.txt>" >&2; }
[[ $# -eq 3 && $1 == "--collect" && $2 == "--output" ]] || { usage; exit 2; }
out=$3
[[ ! -e $out ]] || { echo "refusing to overwrite: $out" >&2; exit 2; }
mkdir -p "$(dirname "$out")"

emit() { printf '\n## %s\n' "$1" >>"$out"; shift; "$@" >>"$out" 2>&1 || printf 'UNAVAILABLE (exit=%s)\n' "$?" >>"$out"; }
printf '# C16 4080 host inventory (read-only)\ncollected_utc=%s\ncollector_uid=%s\n' "$(date -u +%FT%TZ)" "$(id -u)" >"$out"
emit os_kernel uname -a
emit os_release cat /etc/os-release
emit cpu lscpu
emit memory free -b
emit block_devices lsblk --bytes --json
emit mounts findmnt --json
emit free_space df -B1 --output=source,target,size,avail,pcent
emit docker_version docker version
emit docker_info docker info
emit nvidia_container_toolkit nvidia-ctk --version
emit nvidia_container_cli nvidia-container-cli --version
emit gpu_identity nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap --format=csv,noheader
emit cuda_nvcc nvcc --version
emit cuda_nvdisasm nvdisasm --version
emit nvidia_profiling_state cat /proc/driver/nvidia/params
printf '\n# No GPU workload, NCU profile, NVBit injection, or host-state mutation was performed.\n' >>"$out"
sha256sum "$out"
