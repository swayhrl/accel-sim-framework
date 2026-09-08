#!/usr/bin/env bash
# Host-only, fail-closed refill monitor for the already-authorized R2 wave.
# It never touches an existing namespace or process.  The immutable dispatcher
# remains the only component that may create a future R2 attempt.
set -euo pipefail

usage() {
  echo "usage: $0 --log FILE [--poll-seconds N]" >&2
  exit 2
}

log_file=
poll_seconds=120
while [ "$#" -gt 0 ]; do
  case "$1" in
    --log) log_file=${2:-}; shift 2 ;;
    --poll-seconds) poll_seconds=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
test -n "$log_file" && [[ "$poll_seconds" =~ ^[1-9][0-9]*$ ]] || usage

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
dispatcher="$repo_root/util/dtc_l1/prepare_fast64_1_r2_full_wave.sh"
auditor="$repo_root/util/dtc_l1/audit_fast64_r2_resources.sh"
runs_root=/workspace/fast64-runs
dispatch_lock="$runs_root/.fast64_1_r2_full_wave_dispatch.lock"
monitor_lock="$runs_root/.fast64_1_r2_autorefiller.lock"
expected_dispatcher_sha=$(sha256sum "$dispatcher" | awk '{print $1}')

exec 8>"$monitor_lock"
flock -n 8 || { echo "FAST64_R2_AUTOREFILL_MONITOR_ALREADY_ACTIVE" >&2; exit 1; }
printf 'FAST64_R2_AUTOREFILL_START\tutc=%s\tdispatcher_sha=%s\n' \
  "$(date -u +%FT%TZ)" "$expected_dispatcher_sha" >>"$log_file"

while :; do
  row_count=$(find "$runs_root" -maxdepth 1 -type d -name 'fast64_1r2_*' -printf . | wc -c)
  if [ "$row_count" -ge 7 ]; then
    printf 'FAST64_R2_AUTOREFILL_DISPATCH_COMPLETE\tutc=%s\trows=%s\n' \
      "$(date -u +%FT%TZ)" "$row_count" >>"$log_file"
    exit 0
  fi
  if fuser -s "$dispatch_lock"; then
    printf 'FAST64_R2_AUTOREFILL_WAIT_LOCK_HELD\tutc=%s\trows=%s\n' \
      "$(date -u +%FT%TZ)" "$row_count" >>"$log_file"
    sleep "$poll_seconds"
    continue
  fi
  actual_dispatcher_sha=$(sha256sum "$dispatcher" | awk '{print $1}')
  if [ "$actual_dispatcher_sha" != "$expected_dispatcher_sha" ]; then
    printf 'FAST64_R2_AUTOREFILL_FAIL_CLOSED_DISPATCHER_SHA\tutc=%s\texpected=%s\tactual=%s\n' \
      "$(date -u +%FT%TZ)" "$expected_dispatcher_sha" "$actual_dispatcher_sha" >>"$log_file"
    exit 1
  fi
  audit="/tmp/fast64-r2-resource-autorefiller-$(date -u +%Y%m%dT%H%M%SZ).tsv"
  if ! bash "$auditor" --output "$audit" --interval 60 >>"$log_file" 2>&1; then
    printf 'FAST64_R2_AUTOREFILL_AUDIT_ERROR\tutc=%s\taudit=%s\n' \
      "$(date -u +%FT%TZ)" "$audit" >>"$log_file"
    sleep "$poll_seconds"
    continue
  fi
  safe=$(awk -F '\t' '$1 == "safe_to_launch" { print $2; exit }' "$audit")
  workers=$(awk -F '\t' '$1 == "authorized_workers" { print $2; exit }' "$audit")
  printf 'FAST64_R2_AUTOREFILL_AUDIT\tutc=%s\trows=%s\tsafe=%s\tauthorized_workers=%s\taudit=%s\n' \
    "$(date -u +%FT%TZ)" "$row_count" "$safe" "$workers" "$audit" >>"$log_file"
  if [ "$safe" = YES ] && [[ "$workers" =~ ^[1-7]$ ]]; then
    "$dispatcher" --launch --resource-audit "$audit" >>"$log_file" 2>&1 ||
      printf 'FAST64_R2_AUTOREFILL_DISPATCH_RETRY\tutc=%s\n' "$(date -u +%FT%TZ)" >>"$log_file"
  fi
  sleep "$poll_seconds"
done
