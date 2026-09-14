#!/usr/bin/env bash
# Docker plan/audit only. It never creates, starts, or mutates a container.
set -euo pipefail
usage() { echo "usage: $0 --plan --image-digest <image@sha256:...> --gpu-uuid <GPU-...> --mount-whitelist <file> | $0 --audit-container <name> --research-uid <uid>" >&2; }
if [[ $# -eq 7 && $1 == "--plan" && $2 == "--image-digest" && $4 == "--gpu-uuid" && $6 == "--mount-whitelist" ]]; then
  image=$3 uuid=$5 list=$7; [[ -f $list && $image == *@sha256:* && $uuid == GPU-* ]] || { echo "invalid immutable image/UUID/whitelist" >&2; exit 2; }
  grep -Eq '(^|/)(var/run/docker\.sock|etc|root)(:|/|$)|^/$' "$list" && { echo "prohibited mount in whitelist" >&2; exit 1; }
  printf 'PLAN_ONLY image=%s gpu_uuid=%s whitelist_sha256=%s\n' "$image" "$uuid" "$(sha256sum "$list" | awk '{print $1}')"
  echo 'Administrator must create with numeric research UID:GID, no --privileged, cap-drop ALL, no docker.sock, and only this whitelist.'
elif [[ $# -eq 4 && $1 == "--audit-container" && $2 != "" && $3 == "--research-uid" ]]; then
  name=$2 uid=$4
  inspect=$(docker inspect "$name")
  cap_add=$(docker inspect --format '{{json .HostConfig.CapAdd}}' "$name")
  configured_user=$(docker inspect --format '{{.Config.User}}' "$name")
  grep -q '"Privileged": true' <<<"$inspect" && { echo 'FAIL privileged container'; exit 1; }
  grep -Eq 'docker\.sock|"Source": "/(etc|root)"|"Source": "/"' <<<"$inspect" && { echo 'FAIL prohibited mount'; exit 1; }
  grep -q 'SYS_ADMIN' <<<"$cap_add" && { echo 'FAIL CAP_SYS_ADMIN'; exit 1; }
  [[ $configured_user == "$uid" || $configured_user == "$uid:"* ]] || { echo 'FAIL research numeric UID not bound'; exit 1; }
  echo 'PASS read-only Docker policy audit (administrator must retain inspect SHA).'
else
  usage; exit 2
fi
