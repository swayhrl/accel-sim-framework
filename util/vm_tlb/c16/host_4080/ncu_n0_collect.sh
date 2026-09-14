#!/usr/bin/env bash
# N0 is read-only and deliberately never launches a CUDA workload or NCU profile.
set -euo pipefail
umask 077

usage() { echo "usage: $0 --collect --output <fresh-receipt.txt>" >&2; }
[[ $# -eq 3 && $1 == --collect && $2 == --output ]] || { usage; exit 2; }
out=$3
[[ ! -e $out ]] || { echo "refusing to overwrite: $out" >&2; exit 2; }
[[ $(id -u) -eq 1004 && $(id -un) == huangrulin && $EUID -ne 0 ]] || {
  echo "N0 must run as unprivileged huangrulin UID 1004" >&2
  exit 2
}

ncu=/opt/nvidia/nsight-compute/2025.1.1/ncu
nvcc=/usr/local/cuda-12.8/bin/nvcc
[[ -x $ncu && -x $nvcc ]] || { echo "fixed NCU or nvcc is unavailable" >&2; exit 2; }
mkdir -p "$(dirname "$out")"
groups=$(id -nG)
gpu=$(nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap --format=csv,noheader)
[[ $(wc -l <<<"$gpu") -eq 1 ]] || { echo "expected exactly one visible GPU" >&2; exit 2; }

{
  printf '# C16 NCU N0 ordinary-user receipt\n'
  printf 'collected_utc=%s\n' "$(date -u +%FT%TZ)"
  printf 'research_user=%s\nuid=%s\ngid=%s\ngroups=%s\n' "$(id -un)" "$(id -u)" "$(id -g)" "$groups"
  printf 'sudo_group_member=%s\n' "$(grep -qw sudo <<<"$groups" && echo YES || echo NO)"
  printf 'docker_group_member=%s\n' "$(grep -qw docker <<<"$groups" && echo YES || echo NO)"
  printf 'kernel=%s\n' "$(uname -r)"
  printf 'gpu=%s\n' "$gpu"
  printf 'cuda_symlink=%s\n' "$(readlink -f /usr/local/cuda)"
  printf 'nvcc_path=%s\n' "$(realpath "$nvcc")"
  printf 'nvcc_sha256=%s\n' "$(sha256sum "$nvcc" | awk '{print $1}')"
  printf 'ncu_path=%s\n' "$(realpath "$ncu")"
  printf 'ncu_sha256=%s\n' "$(sha256sum "$ncu" | awk '{print $1}')"
  printf '\n## ncu_version\n'; "$ncu" --version
  printf '\n## nvcc_version\n'; "$nvcc" --version
  printf '\n## loaded_nvidia_parameters\n'; cat /proc/driver/nvidia/params
  printf '\n## effective_capabilities\n'; capsh --print
  printf '\n# No CUDA workload, NCU profile, Docker command, NVBit injection, or host mutation was performed.\n'
} >"$out"

sha256sum "$out"
