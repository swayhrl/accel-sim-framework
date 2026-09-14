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
emit current_kernel uname -r
emit cpu lscpu
emit memory free -b
emit block_devices lsblk --bytes --json
emit block_filesystems lsblk -f
emit mounts findmnt --json
emit mount_text mount
emit free_space df -B1 --output=source,target,size,avail,pcent
if command -v dpkg-query >/dev/null 2>&1; then
  emit package_inventory_dpkg dpkg-query -W -f='${binary:Package}\t${Version}\t${Architecture}\n' 'nvidia*' 'cuda*' 'docker*' 'containerd*' 'nvidia-container*'
elif command -v rpm >/dev/null 2>&1; then
  emit package_inventory_rpm rpm -qa
else
  printf '\n## package_inventory\nUNAVAILABLE: no dpkg-query or rpm\n' >>"$out"
fi
emit fstab cat /etc/fstab
printf '\n## nvidia_modprobe_files\n' >>"$out"
find /etc/modprobe.d -maxdepth 1 -type f \( -iname '*nvidia*' -o -iname '*cuda*' \) -print -exec sha256sum {} \; >>"$out" 2>&1 || true
printf '\n## docker_daemon_config\n' >>"$out"
for file in /etc/docker/daemon.json /etc/default/docker; do
  [[ -e $file ]] && { printf '### %s\n' "$file"; sha256sum "$file"; cat "$file"; }
done >>"$out" 2>&1
printf '\n## cuda_symlink_state\n' >>"$out"
ls -ld /usr/local/cuda /usr/local/cuda-* 2>&1 >>"$out" || true
readlink -f /usr/local/cuda >>"$out" 2>&1 || true
emit secureboot_state mokutil --sb-state
emit docker_version docker version
emit docker_info docker info
emit docker_containers docker ps -a --no-trunc
emit docker_images docker image ls --digests --no-trunc
emit nvidia_container_toolkit nvidia-ctk --version
emit nvidia_container_cli nvidia-container-cli --version
emit gpu_identity nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap --format=csv,noheader
emit cuda_nvcc nvcc --version
emit cuda_nvdisasm nvdisasm --version
emit ncu_version ncu --version
emit nvidia_profiling_state cat /proc/driver/nvidia/params
printf '\n## nvbit_environment_claim\nNVBIT_HOME=%s\nNVBIT_VERSION=%s\nExpected source-reference version=1.7.5; archive/core/tool closure must be reverified on the 4080.\n' "${NVBIT_HOME:-UNSET}" "${NVBIT_VERSION:-UNSET}" >>"$out"
printf '\n## smart_basic_health_no_wake\n' >>"$out"
if command -v smartctl >/dev/null 2>&1; then
  while read -r name type; do
    [[ $type == disk ]] || continue
    printf '### /dev/%s\n' "$name"
    smartctl -H --nocheck=standby "/dev/$name" 2>&1 || true
  done < <(lsblk -dn -o NAME,TYPE)
else
  echo 'UNAVAILABLE: smartctl not installed'
fi >>"$out"
printf '\n# No GPU workload, NCU profile, NVBit injection, or host-state mutation was performed.\n' >>"$out"
sha256sum "$out"
