#!/usr/bin/env bash
# Future-only collector for a newly adopted FAST64 Core/runtime identity.
# It never changes a live runner; it waits for its immutable terminal receipt
# and atomically writes only the compact result record.
set -euo pipefail

usage() {
  echo "usage: $0 --run-dir DIR --workload-id ID --mode BASE|IO|OO --config-id ID --config-file FILE --core-sha SHA --runtime-sha SHA --classification LABEL --output FILE --log FILE [--poll-seconds N]" >&2
  exit 2
}

run= workload= mode= config_id= config= core= runtime= classification= output= log= poll=120
while [ "$#" -gt 0 ]; do
  case "$1" in
    --run-dir) run=${2:-}; shift 2 ;;
    --workload-id) workload=${2:-}; shift 2 ;;
    --mode) mode=${2:-}; shift 2 ;;
    --config-id) config_id=${2:-}; shift 2 ;;
    --config-file) config=${2:-}; shift 2 ;;
    --core-sha) core=${2:-}; shift 2 ;;
    --runtime-sha) runtime=${2:-}; shift 2 ;;
    --classification) classification=${2:-}; shift 2 ;;
    --output) output=${2:-}; shift 2 ;;
    --log) log=${2:-}; shift 2 ;;
    --poll-seconds) poll=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
test -n "$run" && test -n "$workload" && test -n "$mode" && test -n "$config_id" && \
  test -n "$config" && test -n "$core" && test -n "$runtime" && test -n "$classification" && \
  test -n "$output" && test -n "$log" || usage
case "$mode" in BASE|IO|OO) ;; *) usage ;; esac
[[ "$poll" =~ ^[1-9][0-9]*$ ]] || usage

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
framework=037f008b330eb230353b60edf126d6be9f45afdc
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
test -d "$run" && test -r "$config" && test -r "$validator" && test -r "$payload"
test ! -e "$output" || { echo "FAST64_REPAIRED_CORE_OUTPUT_EXISTS $output" >&2; exit 1; }

lock="${output}.lock"; mkdir -p "$(dirname "$output")"
exec 9>"$lock"; flock -n 9 || { echo FAST64_REPAIRED_CORE_MONITOR_ALREADY_ACTIVE >&2; exit 1; }
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" | tee -a "$log"; }
while ! test -f "$run/RUN_TERMINAL.tsv"; do
  emit FAST64_REPAIRED_CORE_WAIT_TERMINAL "workload=$workload mode=$mode run=$run"
  sleep "$poll"
done
exit_status=$(awk -F '\t' '$1=="simulator_exit_status" {n++;v=$2} END {if(n==1)print v;else exit 1}' "$run/RUN_TERMINAL.tsv")
test "$exit_status" = 0 || { emit FAST64_REPAIRED_CORE_NONZERO_TERMINAL "workload=$workload mode=$mode"; exit 1; }
emit FAST64_REPAIRED_CORE_VALIDATE "workload=$workload mode=$mode run=$run"
python3 "$validator" --run-dir "$run" --workload-id "$workload" --mode "$mode" --config-id "$config_id" \
  --config-file "$config" --core-sha "$core" --framework-sha "$framework" --observer-sha "$observer" \
  --runtime-sha "$runtime" --payload-manifest "$payload" --classification "$classification" \
  --require-immutable-attempt --output "$output"
if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' \
    "$run/simulator.stdout" "$run/simulator.stderr" "$run/launcher.log"; then
  emit FAST64_REPAIRED_CORE_FORBIDDEN_FAILURE_SIGNATURE "workload=$workload mode=$mode run=$run"
  exit 1
fi
emit FAST64_REPAIRED_CORE_PASS "workload=$workload mode=$mode output=$output"
