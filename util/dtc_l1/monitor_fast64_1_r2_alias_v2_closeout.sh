#!/usr/bin/env bash
# Future-only recovery monitor for the frozen FAST64.1 R2 alias defect.
# It never launches, signals, restarts, or modifies an R2 attempt or the
# frozen closeout controller.  It invokes only the versioned collector after
# all immutable terminal receipts exist and the frozen controller has recorded
# its expected fail-closed collector retry.
set -euo pipefail

usage() {
  echo "usage: $0 --log FILE [--frozen-log FILE] [--poll-seconds N] [--once]" >&2
  exit 2
}

log_file=
frozen_log=/workspace/fast64-runs/fast64_1_r2_closeout.log
poll_seconds=120
once=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --log) log_file=${2:-}; shift 2 ;;
    --frozen-log) frozen_log=${2:-}; shift 2 ;;
    --poll-seconds) poll_seconds=${2:-}; shift 2 ;;
    --once) once=1; shift ;;
    *) usage ;;
  esac
done
test -n "$log_file" && [[ "$poll_seconds" =~ ^[1-9][0-9]*$ ]] || usage

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
collector="$repo/util/dtc_l1/collect_fast64_1_r2_full_wave_alias_v2.sh"
out="$repo/docs/dtc_l1/fast64/generated/qualification_r2_full_wave_alias_v2"
pass="$out/FAST64_1_R2_FULL_WAVE_ALIAS_V2_PASS.txt"
lock="$runs/.fast64_1_r2_alias_v2_closeout.lock"
rows=(
  fast64_1r2_bicg_base_cap8192_a1
  fast64_1r2_bicg_io_cap8192_a1
  fast64_1r2_bicg_oo_cap8192_a1
  fast64_1r2_bicg_io_cap1048576_a1
  fast64_1r2_bicg_oo_cap1048576_a1
  fast64_1r2_gesummv_io_cap8192_a1
  fast64_1r2_gesummv_io_cap1048576_a1
)

expected_collector_sha=$(sha256sum "$collector" | awk '{print $1}')
exec 9>"$lock"
flock -n 9 || { echo "FAST64_R2_ALIAS_V2_MONITOR_ALREADY_ACTIVE" >&2; exit 1; }
printf 'FAST64_R2_ALIAS_V2_MONITOR_START\tutc=%s\tcollector_sha=%s\n' \
  "$(date -u +%FT%TZ)" "$expected_collector_sha" >>"$log_file"

while :; do
  if test -f "$pass"; then
    printf 'FAST64_R2_ALIAS_V2_ALREADY_COLLECTED\tutc=%s\n' "$(date -u +%FT%TZ)" >>"$log_file"
    exit 0
  fi

  terminal=0
  for row in "${rows[@]}"; do
    test -f "$runs/$row/RUN_TERMINAL.tsv" && terminal=$((terminal + 1))
  done
  if [ "$terminal" -ne "${#rows[@]}" ]; then
    printf 'FAST64_R2_ALIAS_V2_WAIT_TERMINALS\tutc=%s\tterminal_rows=%s\ttotal_rows=%s\n' \
      "$(date -u +%FT%TZ)" "$terminal" "${#rows[@]}" >>"$log_file"
  elif ! rg -q '^FAST64_R2_CLOSEOUT_COLLECTOR_RETRY' "$frozen_log"; then
    printf 'FAST64_R2_ALIAS_V2_WAIT_FROZEN_RETRY\tutc=%s\n' "$(date -u +%FT%TZ)" >>"$log_file"
  elif [ "$(sha256sum "$collector" | awk '{print $1}')" != "$expected_collector_sha" ]; then
    printf 'FAST64_R2_ALIAS_V2_FAIL_CLOSED_COLLECTOR_SHA\tutc=%s\texpected=%s\tactual=%s\n' \
      "$(date -u +%FT%TZ)" "$expected_collector_sha" "$(sha256sum "$collector" | awk '{print $1}')" >>"$log_file"
    exit 1
  elif "$collector" >>"$log_file" 2>&1; then
    test -f "$pass"
    printf 'FAST64_R2_ALIAS_V2_COLLECTOR_PASS\tutc=%s\tpass=%s\n' \
      "$(date -u +%FT%TZ)" "$pass" >>"$log_file"
    exit 0
  else
    printf 'FAST64_R2_ALIAS_V2_COLLECTOR_RETRY\tutc=%s\n' "$(date -u +%FT%TZ)" >>"$log_file"
  fi

  [ "$once" = 1 ] && exit 0
  sleep "$poll_seconds"
done
