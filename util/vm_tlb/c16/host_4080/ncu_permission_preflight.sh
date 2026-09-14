#!/usr/bin/env bash
# N0 only: read configuration/identity. It deliberately does not profile a kernel.
set -euo pipefail
umask 077
usage() { echo "usage: $0 --collect --research-user <user> --output <receipt.txt>" >&2; }
[[ $# -eq 5 && $1 == "--collect" && $2 == "--research-user" && $4 == "--output" ]] || { usage; exit 2; }
user=$3 out=$5
[[ $(id -un) == "$user" ]] || { echo "run N0 as the research user, not administrator/root" >&2; exit 2; }
[[ ! -e $out ]] || { echo "refusing to overwrite: $out" >&2; exit 2; }
mkdir -p "$(dirname "$out")"
groups=$(id -nG)
{
  echo '# C16 N0 ordinary-user permission preflight'
  echo "uid=$(id -u) user=$(id -un) groups=$groups"
  echo "sudo_group_member=$(grep -qw sudo <<<"$groups" && echo YES || echo NO)"
  echo "docker_group_member=$(grep -qw docker <<<"$groups" && echo YES || echo NO)"
  echo '## capabilities'; capsh --print 2>&1 || echo UNAVAILABLE
  echo '## ncu_version'; ncu --version 2>&1 || echo UNAVAILABLE
  echo '## loaded_nvidia_parameters'; cat /proc/driver/nvidia/params 2>&1 || echo UNAVAILABLE
  echo '## expected_loaded_state'; echo 'Review for RmProfilingAdminOnly: 0 (or distribution-equivalent proof of NVreg_RestrictProfilingToAdminUsers=0).'
  echo 'N0 does not run a CUDA application, NCU capture, NVBit tool, or Docker command.'
} >"$out"
sha256sum "$out"
