#!/usr/bin/env bash
# Read-only policy audit; it does not add users/groups/capabilities or start containers.
set -euo pipefail
umask 077
usage() { echo "usage: $0 --audit --research-user <user> --output <receipt.txt>" >&2; }
[[ $# -eq 5 && $1 == "--audit" && $2 == "--research-user" && $4 == "--output" ]] || { usage; exit 2; }
user=$3 out=$5
[[ ! -e $out ]] || { echo "refusing to overwrite: $out" >&2; exit 2; }
id "$user" >/dev/null
mkdir -p "$(dirname "$out")"
groups=$(id -nG "$user")
printf '# C16 security audit\nresearch_user=%s\ngroups=%s\n' "$user" "$groups" >"$out"
printf 'sudo_group_member=%s\n' "$(grep -qw sudo <<<"$groups" && echo YES || echo NO)" >>"$out"
printf 'docker_group_member=%s\n' "$(grep -qw docker <<<"$groups" && echo YES || echo NO)" >>"$out"
printf 'research_uid=%s\n' "$(id -u "$user")" >>"$out"
printf '\n## sudo_policy_query\n' >>"$out"; sudo -n -l -U "$user" >>"$out" 2>&1 || echo 'UNAVAILABLE_OR_NO_SUDO (review manually)' >>"$out"
printf '\n## target_capability_check\nCAP_SYS_ADMIN=UNKNOWN; N0 must be run by the research user and retain capsh --print output.\n' >>"$out"
printf '\nrequired: no sudo; no docker group; no CAP_SYS_ADMIN; no privileged container; no docker.sock/root/etc/root mounts.\n' >>"$out"
sha256sum "$out"
