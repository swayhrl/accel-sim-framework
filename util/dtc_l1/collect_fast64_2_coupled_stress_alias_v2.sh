#!/usr/bin/env bash
# Versioned, read-only closeout for the terminal FAST64.2 coupled-stress row.
# It does not modify the frozen R2 closeout dependency closure or any run
# directory.  A collected negative result is evidence, never a stage PASS.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
row=fast64_2_precomputed_nn_io_coupled_cap512_pib1_a1_r2
run="$runs/$row"
config="$runs/overlays/FAST64_IO_COUPLED_STRESS_CAP512_PIB1.config"
out="$repo/docs/dtc_l1/fast64/generated/fast64_2_coupled_stress_alias_v2"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v2.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
core=bbcbb5e7565417102087bc80b14c349b4e568c05
framework=037f008b330eb230353b60edf126d6be9f45afdc
runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
classification=PRECOMPUTED_FAST64_2_COUPLED_STRESS_PENDING_FAST64_1_ACCEPTANCE

test -f "$run/RUN_TERMINAL.tsv"
test "$(awk -F '\t' '$1=="simulator_exit_status" {n++;v=$2} END {if(n==1)print v;else exit 1}' "$run/RUN_MANIFEST.tsv")" = 0
test "$(grep -F -- '-gpgpu_dtc_l1_lower_outstanding_cap ' "$config" | tail -1)" = \
  '-gpgpu_dtc_l1_lower_outstanding_cap 512'
test "$(grep -Fxc -- '-gpgpu_dtc_l1_io_pib_entries 1' "$config")" = 1
test ! -e "$out"
mkdir -p "$out"

"$validator" --run-dir "$run" --workload-id NN --mode IO \
  --config-id FAST64_IO_COUPLED_STRESS_CAP512_PIB1_A1_R2 --config-file "$config" \
  --core-sha "$core" --framework-sha "$framework" --observer-sha "$observer" \
  --runtime-sha "$runtime" --payload-manifest "$payload" \
  --classification "$classification" --require-immutable-attempt \
  --output "$out/$row.json"

python3 - "$out/$row.json" "$out/FAST64_2_COUPLED_STRESS_ALIAS_V2.tsv" <<'PY'
import json
import pathlib
import sys

summary, evidence = map(pathlib.Path, sys.argv[1:])
metrics = json.loads(summary.read_text(encoding="utf-8"))["metrics"]
required = (
    "DTC_L1_lower_cap_full_events",
    "DTC_L1_io_lower_create_queue_full_stalls",
    "DTC_L1_io_lower_created", "DTC_L1_io_lower_issued",
    "DTC_L1_io_lower_responses", "DTC_L1_io_completion_dependency_count",
    "DTC_L1_io_completion_dependency_closed", "DTC_L1_io_inflight_current",
    "DTC_L1_io_pib_occupancy", "DTC_L1_lower_outstanding",
)
missing = [key for key in required if key not in metrics]
if missing:
    raise SystemExit("missing strict coupled-stress metrics: " + ", ".join(missing))
if not (metrics["DTC_L1_io_lower_created"] == metrics["DTC_L1_io_lower_issued"] == metrics["DTC_L1_io_lower_responses"]):
    raise SystemExit("lower create/issue/response conservation failed")
if metrics["DTC_L1_io_completion_dependency_count"] != metrics["DTC_L1_io_completion_dependency_closed"]:
    raise SystemExit("completion-dependency conservation failed")
for key in ("DTC_L1_io_inflight_current", "DTC_L1_io_pib_occupancy", "DTC_L1_lower_outstanding"):
    if metrics[key] != 0:
        raise SystemExit("nonzero terminal state: " + key)
pressure = metrics["DTC_L1_lower_cap_full_events"] > 0 and metrics["DTC_L1_io_lower_create_queue_full_stalls"] > 0
status = ("FAST64_2_COUPLED_STRESS_HARD_EVIDENCE_PASS_PENDING_FAST64_1_ACCEPTANCE"
          if pressure else "FAST64_2_COUPLED_STRESS_STRICT_NEGATIVE_PRESSURE_ABSENT")
evidence.write_text(
    "schema\tFAST64_2_COUPLED_STRESS_ALIAS_V2\n"
    f"status\t{status}\n"
    "global_lower_cap\t512\n"
    "source_coupled_bound\t-gpgpu_dtc_l1_io_pib_entries=1\n"
    f"lower_cap_full_events\t{metrics['DTC_L1_lower_cap_full_events']}\n"
    f"io_lower_create_queue_full_stalls\t{metrics['DTC_L1_io_lower_create_queue_full_stalls']}\n"
    f"io_lower_created\t{metrics['DTC_L1_io_lower_created']}\n"
    f"io_lower_issued\t{metrics['DTC_L1_io_lower_issued']}\n"
    f"io_lower_responses\t{metrics['DTC_L1_io_lower_responses']}\n"
    f"dependency_count\t{metrics['DTC_L1_io_completion_dependency_count']}\n"
    f"dependency_closed\t{metrics['DTC_L1_io_completion_dependency_closed']}\n"
    "terminal_state\tinflight=0;pib=0;lower=0\n",
    encoding="utf-8")
print(status)
PY

echo FAST64_2_COUPLED_STRESS_ALIAS_V2_COLLECTED
