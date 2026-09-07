#!/usr/bin/env bash
# Fail-closed closeout for the isolated FAST64.2 forced lower-create stress.
# It never launches, signals, or waits on a simulator process.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
row=fast64_2_precomputed_bicg_io_stress_cap1048576_pib1_a1
run_dir="$runs_root/$row"
summary="$runs_root/validated/$row.summary.json"
qualification="$runs_root/validated/$row.qualification.json"
core=bbcbb5e7565417102087bc80b14c349b4e568c05
framework=5ee236f9452cd09145ab275c530c34f263a1c2e4
classification=PRECOMPUTED_FAST64_2_DIAGNOSTIC_PENDING_FAST64_1_ACCEPTANCE
config="$runs_root/overlays/FAST64_IO_CAP1048576_STRESS_PIB1.config"
payload="$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"

test -f "$run_dir/RUN_MANIFEST.tsv"
terminal=$(awk -F '\t' '$1 == "simulator_exit_status" { value=$2 } END { print value }' \
  "$run_dir/RUN_MANIFEST.tsv")
if [ -z "$terminal" ]; then
  echo "FAST64_2_STRESS_PENDING_NATURAL_TERMINAL row=$row"
  exit 0
fi
if [ "$terminal" != 0 ]; then
  echo "FAST64_2_STRESS_NONZERO_TERMINAL row=$row status=$terminal" >&2
  exit 1
fi

test ! -e "$summary" || { echo "SUMMARY_EXISTS $summary" >&2; exit 1; }
mkdir -p "$(dirname "$summary")"
python3 "$repo_root/util/dtc_l1/validate_fast64_trace_row.py" \
  --run-dir "$run_dir" --workload-id bicg --mode IO \
  --config-id FAST64_IO_STRESS_CAP1048576_PIB1_A1 --config-file "$config" \
  --core-sha "$core" --framework-sha "$framework" --payload-manifest "$payload" \
  --classification "$classification" --output "$summary"

python3 - "$summary" "$qualification" "$row" <<'PY'
import json
import pathlib
import sys

summary, qualification, row = map(pathlib.Path, sys.argv[1:])
result = json.loads(summary.read_text(encoding="utf-8"))
metrics = result["metrics"]
required = (
    "DTC_L1_io_lower_create_queue_full_stalls",
    "DTC_L1_io_lower_created",
    "DTC_L1_io_lower_issued",
    "DTC_L1_io_lower_responses",
    "DTC_L1_io_inflight_current",
    "DTC_L1_io_pib_occupancy",
    "DTC_L1_lower_outstanding",
    "DTC_L1_lower_outstanding_cap",
)
missing = [key for key in required if key not in metrics]
if missing:
    raise SystemExit("missing stress metrics: " + ", ".join(missing))
if metrics["DTC_L1_io_lower_create_queue_full_stalls"] <= 0:
    raise SystemExit("forced stress did not observe IO lower-create queue-full stalls")
if metrics["DTC_L1_lower_outstanding_cap"] != 1048576:
    raise SystemExit("stress global lower cap is not the high/non-binding value")
if not (metrics["DTC_L1_io_lower_created"] ==
        metrics["DTC_L1_io_lower_issued"] ==
        metrics["DTC_L1_io_lower_responses"]):
    raise SystemExit("IO lower create/issue/response conservation failed")
for key in ("DTC_L1_io_inflight_current", "DTC_L1_io_pib_occupancy",
            "DTC_L1_lower_outstanding"):
    if metrics[key] != 0:
        raise SystemExit("nonzero terminal state: " + key)
if qualification.exists():
    raise SystemExit("qualification output already exists: " + str(qualification))
qualification.write_text(json.dumps({
    "row": row.name,
    "status": "FAST64_2_FORCED_STRESS_HARD_EVIDENCE_PASS_PENDING_FAST64_1_ACCEPTANCE",
    "source_coupled_bound": "-gpgpu_dtc_l1_io_pib_entries",
    "queue_full_stalls": metrics["DTC_L1_io_lower_create_queue_full_stalls"],
    "global_lower_cap": metrics["DTC_L1_lower_outstanding_cap"],
    "lower_created": metrics["DTC_L1_io_lower_created"],
    "lower_issued": metrics["DTC_L1_io_lower_issued"],
    "lower_responses": metrics["DTC_L1_io_lower_responses"],
    "terminal_io_inflight": metrics["DTC_L1_io_inflight_current"],
    "terminal_io_pib": metrics["DTC_L1_io_pib_occupancy"],
    "terminal_lower_outstanding": metrics["DTC_L1_lower_outstanding"],
    "summary": str(summary),
}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("FAST64_2_STRESS_EVIDENCE_PASS row=" + row.name)
PY
