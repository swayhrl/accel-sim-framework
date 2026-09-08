#!/usr/bin/env bash
# Future-only strict collector for the authorized BICG FAST64.2 fallback.
# It neither launches nor signals a simulator and never touches frozen R2
# closeout bytes.  Collection may succeed while the pressure gate is negative.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
row=fast64_2_precomputed_bicg_io_coupled_cap512_pib1_a1_r2
run="$runs/$row"
config="$runs/overlays/FAST64_IO_COUPLED_STRESS_CAP512_PIB1.config"
out="$repo/docs/dtc_l1/fast64/generated/fast64_2_coupled_stress_bicg_alias_v2"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v2.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
core=bbcbb5e7565417102087bc80b14c349b4e568c05
framework=037f008b330eb230353b60edf126d6be9f45afdc
runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
classification=PRECOMPUTED_FAST64_2_COUPLED_STRESS_PENDING_FAST64_1_ACCEPTANCE

value() { awk -F '\t' -v k="$2" '$1==k {n++;v=$2} END {if(n==1)print v;else exit 1}' "$1/RUN_MANIFEST.tsv"; }
test -f "$run/RUN_TERMINAL.tsv"
test "$(value "$run" simulator_exit_status)" = 0
test "$(value "$run" core_source_head)" = "$core"
test "$(value "$run" framework_scientific_config_source_sha)" = "$framework"
test "$(value "$run" observer_overlay_sha256)" = "$observer"
test "$(value "$run" simulator_sha256)" = "$runtime"
test "$(grep -F -- '-gpgpu_dtc_l1_lower_outstanding_cap ' "$config" | tail -1)" = '-gpgpu_dtc_l1_lower_outstanding_cap 512'
test "$(grep -Fxc -- '-gpgpu_dtc_l1_io_pib_entries 1' "$config")" = 1
test "$(sha256sum "$config" | awk '{print $1}')" = 9b01eb0c163ad825743a19e7192f4e4a934791ae11aee30699d2eda5fe42d4ba
test ! -e "$out"
mkdir -p "$out"

"$validator" --run-dir "$run" --workload-id BICG --mode IO \
  --config-id FAST64_IO_COUPLED_STRESS_CAP512_PIB1_A1_R2 --config-file "$config" \
  --core-sha "$core" --framework-sha "$framework" --observer-sha "$observer" \
  --runtime-sha "$runtime" --payload-manifest "$payload" \
  --classification "$classification" --require-immutable-attempt \
  --output "$out/$row.json"

if rg -n -i 'post-allocation|output mismatch|checker.*fail' \
    "$run/simulator.stdout" "$run/simulator.stderr"; then
  echo FAST64_2_BICG_FORBIDDEN_FAILURE_SIGNATURE >&2
  exit 1
fi

python3 - "$out/$row.json" "$out/FAST64_2_COUPLED_STRESS_BICG_ALIAS_V2.tsv" <<'PY'
import json
import pathlib
import sys

summary, evidence = map(pathlib.Path, sys.argv[1:])
m = json.loads(summary.read_text(encoding="utf-8"))["metrics"]
required = (
    "DTC_L1_lower_cap_full_events", "DTC_L1_io_lower_create_queue_full_stalls",
    "DTC_L1_io_lower_created", "DTC_L1_io_lower_issued", "DTC_L1_io_lower_responses",
    "DTC_L1_io_completion_dependency_count", "DTC_L1_io_completion_dependency_closed",
    "DTC_L1_io_inflight_current", "DTC_L1_io_pib_occupancy", "DTC_L1_lower_outstanding",
)
missing = [key for key in required if key not in m]
if missing:
    raise SystemExit("missing strict BICG fallback metrics: " + ", ".join(missing))
if not (m["DTC_L1_io_lower_created"] == m["DTC_L1_io_lower_issued"] == m["DTC_L1_io_lower_responses"]):
    raise SystemExit("lower create/issue/response conservation failed")
if m["DTC_L1_io_completion_dependency_count"] != m["DTC_L1_io_completion_dependency_closed"]:
    raise SystemExit("completion-dependency conservation failed")
for key in ("DTC_L1_io_inflight_current", "DTC_L1_io_pib_occupancy", "DTC_L1_lower_outstanding"):
    if m[key] != 0:
        raise SystemExit("nonzero terminal state: " + key)
pressure = m["DTC_L1_lower_cap_full_events"] > 0 and m["DTC_L1_io_lower_create_queue_full_stalls"] > 0
status = ("FAST64_2_BICG_COUPLED_STRESS_HARD_EVIDENCE_PASS_PENDING_FAST64_1_ACCEPTANCE"
          if pressure else "FAST64_2_BICG_COUPLED_STRESS_STRICT_NEGATIVE_PRESSURE_ABSENT")
evidence.write_text(
    "schema\tFAST64_2_COUPLED_STRESS_BICG_ALIAS_V2\n"
    f"status\t{status}\n"
    "global_lower_cap\t512\nsource_coupled_bound\t-gpgpu_dtc_l1_io_pib_entries=1\n"
    f"lower_cap_full_events\t{m['DTC_L1_lower_cap_full_events']}\n"
    f"io_lower_create_queue_full_stalls\t{m['DTC_L1_io_lower_create_queue_full_stalls']}\n"
    f"io_lower_created\t{m['DTC_L1_io_lower_created']}\nio_lower_issued\t{m['DTC_L1_io_lower_issued']}\nio_lower_responses\t{m['DTC_L1_io_lower_responses']}\n"
    f"dependency_count\t{m['DTC_L1_io_completion_dependency_count']}\ndependency_closed\t{m['DTC_L1_io_completion_dependency_closed']}\n"
    "terminal_state\tinflight=0;pib=0;lower=0\n", encoding="utf-8")
print(status)
PY

echo FAST64_2_BICG_COUPLED_STRESS_ALIAS_V2_COLLECTED
