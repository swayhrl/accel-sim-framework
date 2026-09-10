#!/usr/bin/env bash
# Future-only strict collector for the cap-1 FAST64.2 diagnostic.
set -euo pipefail
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
row=fast64_2_nn_io_coupled_cap1_pib1_a1_v1
run="$runs/$row"
config="$runs/overlays/FAST64_IO_COUPLED_STRESS_CAP1_PIB1_V1.config"
out="$repo/docs/dtc_l1/fast64/generated/fast64_2_coupled_stress_cap1_v1"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v2.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
test -f "$run/RUN_TERMINAL.tsv"
manifest_value() {
  awk -F '\t' -v key="$1" '$1==key {n++; value=$2} END {if(n==1) print value; else exit 1}' "$2"
}
test "$(manifest_value attempt_uuid "$run/RUN_MANIFEST.tsv")" = "$(manifest_value attempt_uuid "$run/RUN_TERMINAL.tsv")"
test "$(manifest_value runner_sha256 "$run/RUN_MANIFEST.tsv")" = "$(manifest_value runner_sha256 "$run/RUN_TERMINAL.tsv")"
test "$(manifest_value receipt_schema "$run/RUN_TERMINAL.tsv")" = FAST64_ATTEMPT_RECEIPT_V1
test "$(manifest_value receipt_type "$run/RUN_TERMINAL.tsv")" = TERMINAL
test "$(manifest_value simulator_exit_status "$run/RUN_TERMINAL.tsv")" = 0
test "$(manifest_value simulator_exit_status "$run/RUN_MANIFEST.tsv")" = 0
test "$(grep -F -- '-gpgpu_dtc_l1_lower_outstanding_cap ' "$config" | tail -1)" = '-gpgpu_dtc_l1_lower_outstanding_cap 1'
test "$(grep -Fxc -- '-gpgpu_dtc_l1_io_pib_entries 1' "$config")" = 1
test ! -e "$out"
parent=$(dirname "$out")
temporary=$(mktemp -d "$parent/.fast64_2_coupled_stress_cap1_v1.tmp.XXXXXX")
trap 'rm -rf -- "$temporary"' EXIT
"$validator" --run-dir "$run" --workload-id NN --mode IO --config-id FAST64_IO_COUPLED_STRESS_CAP1_PIB1_A1_V1 --config-file "$config" --core-sha bbcbb5e7565417102087bc80b14c349b4e568c05 --framework-sha 037f008b330eb230353b60edf126d6be9f45afdc --observer-sha 2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e --runtime-sha 6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041 --payload-manifest "$payload" --classification FAST64_2_SOURCE_REACHABLE_COUPLED_STRESS_CAP1_DIAGNOSTIC --require-immutable-attempt --output "$temporary/$row.json"
python3 - "$temporary/$row.json" "$temporary/FAST64_2_COUPLED_STRESS_CAP1_V1.tsv" <<'PY'
import json, pathlib, sys
m=json.loads(pathlib.Path(sys.argv[1]).read_text())['metrics']
keys=('DTC_L1_lower_cap_full_events','DTC_L1_io_lower_create_queue_full_stalls','DTC_L1_io_lower_created','DTC_L1_io_lower_issued','DTC_L1_io_lower_responses','DTC_L1_io_completion_dependency_count','DTC_L1_io_completion_dependency_closed','DTC_L1_io_inflight_current','DTC_L1_io_pib_occupancy','DTC_L1_lower_outstanding')
missing=[k for k in keys if k not in m]
if missing: raise SystemExit('missing metrics: '+', '.join(missing))
if not (m[keys[2]]==m[keys[3]]==m[keys[4]]): raise SystemExit('lower conservation failed')
if m[keys[5]] != m[keys[6]]: raise SystemExit('dependency conservation failed')
if any(m[k] != 0 for k in keys[7:]): raise SystemExit('terminal drain failed')
if not (m[keys[0]] > 0 and m[keys[1]] > 0): raise SystemExit('required coupled pressure absent')
pathlib.Path(sys.argv[2]).write_text('schema\tFAST64_2_COUPLED_STRESS_CAP1_V1\nstatus\tFAST64_2_COUPLED_STRESS_HARD_EVIDENCE_PASS\nglobal_lower_cap\t1\nsource_coupled_bound\t-gpgpu_dtc_l1_io_pib_entries=1\nlower_cap_full_events\t%s\nio_lower_create_queue_full_stalls\t%s\nio_lower_created\t%s\nio_lower_issued\t%s\nio_lower_responses\t%s\ndependency_count\t%s\ndependency_closed\t%s\nterminal_state\tinflight=0;pib=0;lower=0\n' % (m[keys[0]],m[keys[1]],m[keys[2]],m[keys[3]],m[keys[4]],m[keys[5]],m[keys[6]]))
PY
mv -n -- "$temporary" "$out"
test -d "$out"
trap - EXIT
echo FAST64_2_COUPLED_STRESS_CAP1_V1_PASS
