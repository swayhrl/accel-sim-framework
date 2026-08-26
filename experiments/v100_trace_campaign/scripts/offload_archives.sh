#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: offload_archives.sh --remote HOST --port PORT --identity FILE --remote-work-root DIR --local-root DIR [options]

Copies each verified AutoDL archive to LOCAL_ROOT/archives, validates its
SHA256 locally, and (with --prune-remote) writes a remote receipt before
removing only that case's remote archive and processed trace directory.

Options:
  --minimum-local-free-gib N  Pause without pruning if local free space is below N (default: 50).
  --interval-seconds N        Poll interval; omit for a single pass.
  --prune-remote              Enable verified remote cleanup after transfer.
EOF
}

remote=""
port=""
identity=""
remote_work_root=""
local_root=""
minimum_local_free_gib=50
interval_seconds=""
prune_remote=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote) remote="$2"; shift 2 ;;
    --port) port="$2"; shift 2 ;;
    --identity) identity="$2"; shift 2 ;;
    --remote-work-root) remote_work_root="$2"; shift 2 ;;
    --local-root) local_root="$2"; shift 2 ;;
    --minimum-local-free-gib) minimum_local_free_gib="$2"; shift 2 ;;
    --interval-seconds) interval_seconds="$2"; shift 2 ;;
    --prune-remote) prune_remote=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
for value in remote port identity remote_work_root local_root; do
  [[ -n "${!value}" ]] || { echo "error: --${value//_/-} is required" >&2; exit 2; }
done
[[ -f "$identity" ]] || { echo "error: identity file does not exist: $identity" >&2; exit 2; }
[[ "$minimum_local_free_gib" =~ ^[1-9][0-9]*$ ]] || { echo "error: bad --minimum-local-free-gib" >&2; exit 2; }
[[ -z "$interval_seconds" || "$interval_seconds" =~ ^[1-9][0-9]*$ ]] || { echo "error: bad --interval-seconds" >&2; exit 2; }

mkdir -p "$local_root/archives" "$local_root/receipts"
log="$local_root/offload.log"
ssh_cmd=(ssh -i "$identity" -p "$port" -o BatchMode=yes -o StrictHostKeyChecking=accept-new "root@$remote")
rsync_ssh="ssh -i $identity -p $port -o BatchMode=yes -o StrictHostKeyChecking=accept-new"

log_line() {
  printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a "$log"
}

local_free_gib() {
  df -Pk "$local_root" | awk 'NR==2 {print int($4/1024/1024)}'
}

offload_once() {
  local free_gib
  free_gib="$(local_free_gib)"
  if (( free_gib < minimum_local_free_gib )); then
    log_line "PAUSE local_free_gib=$free_gib threshold=$minimum_local_free_gib"
    return 0
  fi
  local listing
  listing="$("${ssh_cmd[@]}" "find '$remote_work_root/archives' -maxdepth 1 -type f -name '*.tar.zst' -printf '%f\\n' 2>/dev/null | sort")"
  local archive case_id local_archive local_sha expected actual
  while IFS= read -r archive; do
    [[ -n "$archive" ]] || continue
    case_id="${archive%.tar.zst}"
    [[ "$case_id" =~ ^[a-z0-9-]+$ ]] || { log_line "SKIP unsafe_case_id=$case_id"; continue; }
    local_archive="$local_root/archives/$archive"
    local_sha="$local_archive.sha256"
    if ! "${ssh_cmd[@]}" "test -f '$remote_work_root/archives/$archive.sha256'"; then
      log_line "SKIP missing_remote_digest=$archive"
      continue
    fi
    log_line "COPY case=$case_id"
    rsync -a --partial --append-verify -e "$rsync_ssh" \
      "root@$remote:$remote_work_root/archives/$archive.sha256" "$local_sha"
    rsync -a --partial --append-verify -e "$rsync_ssh" \
      "root@$remote:$remote_work_root/archives/$archive" "$local_archive"
    expected="$(awk 'NR==1 {print $1}' "$local_sha")"
    actual="$(sha256sum "$local_archive" | awk '{print $1}')"
    if [[ "$expected" != "$actual" || ! "$expected" =~ ^[0-9a-f]{64}$ ]]; then
      log_line "ERROR sha256_mismatch case=$case_id expected=$expected actual=$actual"
      continue
    fi
    printf '%s  %s\n' "$actual" "$(basename "$local_archive")" > "$local_sha"
    log_line "PASS local_sha256 case=$case_id bytes=$(stat -c %s "$local_archive")"
    if (( ! prune_remote )); then
      continue
    fi
    "${ssh_cmd[@]}" python3 - "$remote_work_root" "$case_id" "$actual" "$local_archive" <<'PY'
import datetime
import json
import os
import pathlib
import sys

root, case_id, digest, local_archive = sys.argv[1:]
target = pathlib.Path(root) / "offloaded"
target.mkdir(parents=True, exist_ok=True)
destination = target / f"{case_id}.json"
temporary = destination.with_suffix(".json.partial")
payload = {
    "schema": "accel-sim-v100-offload-receipt-v1",
    "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
    "case_id": case_id,
    "archive_sha256": digest,
    "local_archive": local_archive,
}
temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
os.replace(temporary, destination)
PY
    # These exact paths are safe to remove only because both archive copies now
    # hash-match and the remote receipt was committed above. Logs/provenance in
    # runs/<case> remain on AutoDL for diagnosis.
    "${ssh_cmd[@]}" "rm -f -- '$remote_work_root/archives/$archive' '$remote_work_root/archives/$archive.sha256'; rm -rf -- '$remote_work_root/runs/$case_id/traces'"
    log_line "PRUNE remote case=$case_id"
  done <<< "$listing"
}

if [[ -z "$interval_seconds" ]]; then
  offload_once
else
  while true; do
    offload_once || log_line "ERROR offload_pass_failed"
    sleep "$interval_seconds"
  done
fi
