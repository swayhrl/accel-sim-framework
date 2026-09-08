#!/usr/bin/env bash
# Host-only strict-closeout monitor for the immutable FAST64.1 R2 wave.
# It never launches, signals, or changes an attempt.  Only after every fixed
# row has a terminal receipt does it invoke the existing fail-closed collector.
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
runs_root=/workspace/fast64-runs
collector="$repo_root/util/dtc_l1/collect_fast64_1_r2_full_wave.sh"
monitor_lock="$runs_root/.fast64_1_r2_closeout.lock"
marker="$runs_root/validated/FAST64_1_R2_FULL_WAVE_COLLECTOR_PASS"
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

exec 8>"$monitor_lock"
flock -n 8 || { echo "FAST64_R2_CLOSEOUT_MONITOR_ALREADY_ACTIVE" >&2; exit 1; }
printf 'FAST64_R2_CLOSEOUT_MONITOR_START\tutc=%s\tcollector_sha=%s\n' \
  "$(date -u +%FT%TZ)" "$expected_collector_sha" >>"$log_file"

while :; do
  test ! -e "$marker" || {
    printf 'FAST64_R2_CLOSEOUT_ALREADY_COLLECTED\tutc=%s\n' "$(date -u +%FT%TZ)" >>"$log_file"
    exit 0
  }
  terminal=0
  for row in "${rows[@]}"; do
    test -f "$runs_root/$row/RUN_TERMINAL.tsv" && terminal=$((terminal + 1))
  done
  if [ "$terminal" -ne "${#rows[@]}" ]; then
    printf 'FAST64_R2_CLOSEOUT_WAIT_TERMINALS\tutc=%s\tterminal_rows=%s\ttotal_rows=%s\n' \
      "$(date -u +%FT%TZ)" "$terminal" "${#rows[@]}" >>"$log_file"
    sleep "$poll_seconds"
    continue
  fi
  actual_collector_sha=$(sha256sum "$collector" | awk '{print $1}')
  if [ "$actual_collector_sha" != "$expected_collector_sha" ]; then
    printf 'FAST64_R2_CLOSEOUT_FAIL_CLOSED_COLLECTOR_SHA\tutc=%s\texpected=%s\tactual=%s\n' \
      "$(date -u +%FT%TZ)" "$expected_collector_sha" "$actual_collector_sha" >>"$log_file"
    exit 1
  fi
  if "$collector" >>"$log_file" 2>&1; then
    mkdir -p "$(dirname "$marker")"
    temp=$(mktemp "${marker}.tmp.XXXXXX")
    printf 'FAST64_1_R2_FULL_WAVE_COLLECTOR_PASS\n' >"$temp"
    chmod 444 "$temp"
    mv -n -- "$temp" "$marker"
    test -f "$marker" && test ! -e "$temp"
    printf 'FAST64_R2_CLOSEOUT_COLLECTOR_PASS\tutc=%s\tmarker=%s\n' \
      "$(date -u +%FT%TZ)" "$marker" >>"$log_file"
    exit 0
  fi
  printf 'FAST64_R2_CLOSEOUT_COLLECTOR_RETRY\tutc=%s\n' "$(date -u +%FT%TZ)" >>"$log_file"
  sleep "$poll_seconds"
done
