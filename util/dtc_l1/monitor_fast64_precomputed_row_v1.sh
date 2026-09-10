#!/usr/bin/env bash
# Future-only closeout monitor for one immutable FAST64 precompute.  It only
# reads a live namespace.  After a natural terminal receipt it invokes the
# versioned alias-v3 validator to create compact evidence at the requested
# repository path; it never signals, restarts, or alters the simulator.
set -euo pipefail

usage() {
  echo "usage: $0 --run-dir DIR --workload-id ID --mode BASE|IO|OO --config-id ID --config-file FILE --classification LABEL --output FILE --log FILE [--poll-seconds N]" >&2
  exit 2
}

run= workload= mode= config_id= config= classification= output= log= poll=120
while [ "$#" -gt 0 ]; do
  case "$1" in
    --run-dir) run=${2:-}; shift 2 ;;
    --workload-id) workload=${2:-}; shift 2 ;;
    --mode) mode=${2:-}; shift 2 ;;
    --config-id) config_id=${2:-}; shift 2 ;;
    --config-file) config=${2:-}; shift 2 ;;
    --classification) classification=${2:-}; shift 2 ;;
    --output) output=${2:-}; shift 2 ;;
    --log) log=${2:-}; shift 2 ;;
    --poll-seconds) poll=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
test -n "$run" && test -n "$workload" && test -n "$mode" && test -n "$config_id" && \
  test -n "$config" && test -n "$classification" && test -n "$output" && test -n "$log" || usage
case "$mode" in BASE|IO|OO) ;; *) usage ;; esac
[[ "$poll" =~ ^[1-9][0-9]*$ ]] || usage

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
core=bbcbb5e7565417102087bc80b14c349b4e568c05
framework=037f008b330eb230353b60edf126d6be9f45afdc
runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
test -d "$run" && test -r "$config" && test -x "$validator" && test -r "$payload"
test ! -e "$output" || { echo "FAST64_PRECOMPUTED_ROW_OUTPUT_EXISTS $output" >&2; exit 1; }

lock="${output}.lock"
mkdir -p "$(dirname "$output")"
exec 9>"$lock"
flock -n 9 || { echo FAST64_PRECOMPUTED_ROW_MONITOR_ALREADY_ACTIVE >&2; exit 1; }
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" | tee -a "$log"; }

while ! test -f "$run/RUN_TERMINAL.tsv"; do
  emit FAST64_PRECOMPUTED_ROW_V1_WAIT_TERMINAL "workload=$workload mode=$mode run=$run"
  sleep "$poll"
done

value() { awk -F '\t' -v k="$2" '$1==k {n++;v=$2} END {if(n==1)print v;else exit 1}' "$1"; }
test "$(value "$run/RUN_TERMINAL.tsv" simulator_exit_status)" = 0 || {
  emit FAST64_PRECOMPUTED_ROW_V1_NONZERO_TERMINAL "workload=$workload mode=$mode run=$run"; exit 1;
}
emit FAST64_PRECOMPUTED_ROW_V1_VALIDATE "workload=$workload mode=$mode run=$run"
"$validator" --run-dir "$run" --workload-id "$workload" --mode "$mode" --config-id "$config_id" \
  --config-file "$config" --core-sha "$core" --framework-sha "$framework" --observer-sha "$observer" \
  --runtime-sha "$runtime" --payload-manifest "$payload" --classification "$classification" \
  --require-immutable-attempt --output "$output"
if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' \
    "$run/simulator.stdout" "$run/simulator.stderr" "$run.launcher.log"; then
  emit FAST64_PRECOMPUTED_ROW_V1_FORBIDDEN_FAILURE_SIGNATURE "workload=$workload mode=$mode run=$run"
  exit 1
fi
emit FAST64_PRECOMPUTED_ROW_V1_PASS "workload=$workload mode=$mode output=$output"
