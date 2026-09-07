#!/usr/bin/env bash
# Fail-closed closeout for the immutable, source-reachable FAST64.2 positive
# stress.  It never launches, waits on, or signals a simulator process.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
row=fast64_2_precomputed_nn_io_coupled_cap512_pib1_a1_r2
run_dir="$runs_root/$row"
config="$runs_root/overlays/FAST64_IO_COUPLED_STRESS_CAP512_PIB1.config"
summary="$runs_root/validated/$row.summary.json"
qualification="$runs_root/validated/$row.qualification.json"
core=bbcbb5e7565417102087bc80b14c349b4e568c05
framework=037f008b330eb230353b60edf126d6be9f45afdc
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
classification=PRECOMPUTED_FAST64_2_COUPLED_STRESS_PENDING_FAST64_1_ACCEPTANCE
payload="$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"

test -f "$run_dir/RUN_MANIFEST.tsv"
test ! -e "$summary" || { echo "SUMMARY_EXISTS $summary" >&2; exit 1; }
test ! -e "$qualification" || { echo "QUALIFICATION_EXISTS $qualification" >&2; exit 1; }
test "$(grep -F -- '-gpgpu_dtc_l1_lower_outstanding_cap ' "$config" | tail -1)" = '-gpgpu_dtc_l1_lower_outstanding_cap 512'
test "$(grep -Fxc -- '-gpgpu_dtc_l1_io_pib_entries 1' "$config")" = 1

python3 "$repo_root/util/dtc_l1/validate_fast64_trace_row.py" \
  --run-dir "$run_dir" --workload-id NN --mode IO \
  --config-id FAST64_IO_COUPLED_STRESS_CAP512_PIB1_A1_R2 --config-file "$config" \
  --core-sha "$core" --framework-sha "$framework" --observer-sha "$observer" --payload-manifest "$payload" \
  --classification "$classification" --require-immutable-attempt --output "$summary"

if rg -n -i 'post-allocation|output mismatch|checker.*fail' \
    "$run_dir/simulator.stdout" "$run_dir/simulator.stderr"; then
  echo "FORCED_STRESS_FORBIDDEN_FAILURE_SIGNATURE" >&2
  exit 1
fi

python3 - "$summary" "$qualification" "$row" <<'PY'
import json
import pathlib
import sys

summary, qualification, row = map(pathlib.Path, sys.argv[1:])
metrics = json.loads(summary.read_text(encoding="utf-8"))["metrics"]
required = (
    "DTC_L1_lower_outstanding_cap", "DTC_L1_lower_cap_full_events",
    "DTC_L1_io_lower_create_queue_full_stalls", "DTC_L1_io_lower_created",
    "DTC_L1_io_lower_issued", "DTC_L1_io_lower_responses",
    "DTC_L1_io_completion_dependency_count", "DTC_L1_io_completion_dependency_closed",
    "DTC_L1_io_inflight_current", "DTC_L1_io_pib_occupancy",
    "DTC_L1_lower_outstanding",
)
missing = [key for key in required if key not in metrics]
if missing:
    raise SystemExit("missing coupled-stress metrics: " + ", ".join(missing))
if metrics["DTC_L1_lower_outstanding_cap"] != 512:
    raise SystemExit("positive stress global cap is not the source-selected binding value")
if metrics["DTC_L1_lower_cap_full_events"] <= 0:
    raise SystemExit("positive stress did not make global lower credit binding")
if metrics["DTC_L1_io_lower_create_queue_full_stalls"] <= 0:
    raise SystemExit("positive stress did not observe IO lower-create queue-full stalls")
if not (metrics["DTC_L1_io_lower_created"] == metrics["DTC_L1_io_lower_issued"] ==
        metrics["DTC_L1_io_lower_responses"]):
    raise SystemExit("IO lower create/issue/response conservation failed")
if metrics["DTC_L1_io_completion_dependency_count"] != metrics["DTC_L1_io_completion_dependency_closed"]:
    raise SystemExit("IO dependency conservation failed")
for key in ("DTC_L1_io_inflight_current", "DTC_L1_io_pib_occupancy", "DTC_L1_lower_outstanding"):
    if metrics[key] != 0:
        raise SystemExit("nonzero terminal state: " + key)
if metrics["DTC_L1_io_lower_created"] <= metrics["DTC_L1_lower_outstanding_cap"]:
    raise SystemExit("insufficient post-pressure lower progress evidence")
qualification.write_text(json.dumps({
    "row": row.name,
    "status": "FAST64_2_COUPLED_STRESS_HARD_EVIDENCE_PASS_PENDING_FAST64_1_ACCEPTANCE",
    "classification": "MissQueue/lower-capacity pressure",
    "source_coupled_bound": "-gpgpu_dtc_l1_io_pib_entries",
    "global_lower_cap": metrics["DTC_L1_lower_outstanding_cap"],
    "lower_cap_full_events": metrics["DTC_L1_lower_cap_full_events"],
    "queue_full_stalls": metrics["DTC_L1_io_lower_create_queue_full_stalls"],
    "lower_created": metrics["DTC_L1_io_lower_created"],
    "lower_issued": metrics["DTC_L1_io_lower_issued"],
    "lower_responses": metrics["DTC_L1_io_lower_responses"],
    "dependency_created": metrics["DTC_L1_io_completion_dependency_count"],
    "dependency_completed": metrics["DTC_L1_io_completion_dependency_closed"],
    "summary": str(summary),
}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("FAST64_2_COUPLED_STRESS_EVIDENCE_PASS row=" + row.name)
PY
