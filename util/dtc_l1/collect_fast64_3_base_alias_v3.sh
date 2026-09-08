#!/usr/bin/env bash
# Future-only strict collector for FAST64.3 Base precomputes.  It is separate
# from the live v2 monitor/collectors, which scan the normal
# -gpgpu_deadlock_detect configuration-help line too broadly.
set -euo pipefail

usage() { echo "usage: $0 --workload {atax|gesummv|dwt2d}" >&2; exit 2; }
workload=
while [ "$#" -gt 0 ]; do
  case "$1" in --workload) workload=${2:-}; shift 2 ;; *) usage ;; esac
done
case "$workload" in atax|gesummv|dwt2d) ;; *) usage ;; esac

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
row="fast64_3_precomputed_${workload}_base_cap8192_a1_r2"
run="$runs/$row"
config="$repo/configs/dtc_l1/fast64/FAST64_BASE.config"
out="$repo/docs/dtc_l1/fast64/generated/fast64_3_${workload}_base_alias_v3"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v2.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
core=bbcbb5e7565417102087bc80b14c349b4e568c05
framework=037f008b330eb230353b60edf126d6be9f45afdc
runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
classification=PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE
workload_id=$(printf '%s' "$workload" | tr '[:lower:]' '[:upper:]')

value() { awk -F '\t' -v k="$2" '$1==k {n++;v=$2} END {if(n==1)print v;else exit 1}' "$1/RUN_MANIFEST.tsv"; }
test -f "$run/RUN_TERMINAL.tsv"
test "$(value "$run" simulator_exit_status)" = 0
test "$(value "$run" core_source_head)" = "$core"
test "$(value "$run" framework_scientific_config_source_sha)" = "$framework"
test "$(value "$run" observer_overlay_sha256)" = "$observer"
test "$(value "$run" simulator_sha256)" = "$runtime"
test "$(value "$run" config_sha256)" = "$(sha256sum "$config" | awk '{print $1}')"
test "$(grep -F -- '-gpgpu_dtc_l1_lower_outstanding_cap ' "$config" | tail -1)" = '-gpgpu_dtc_l1_lower_outstanding_cap 8192'
test ! -e "$out"
mkdir -p "$out"

"$validator" --run-dir "$run" --workload-id "$workload_id" --mode BASE \
  --config-id FAST64_BASE_A1 --config-file "$config" --core-sha "$core" \
  --framework-sha "$framework" --observer-sha "$observer" --runtime-sha "$runtime" \
  --payload-manifest "$payload" --classification "$classification" \
  --require-immutable-attempt --output "$out/$row.json"

# The simulator prints the enabled -gpgpu_deadlock_detect option during normal
# config echo.  Match actual failure diagnostics, not that configuration line.
if rg -n -i 'assertion failed|assert\(|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' \
    "$run.launcher.log" "$run/simulator.stdout" "$run/simulator.stderr"; then
  echo "FAST64_3_${workload_id}_FORBIDDEN_FAILURE_SIGNATURE" >&2
  exit 1
fi

python3 - "$out/$row.json" "$out/FAST64_3_${workload_id}_BASE_ALIAS_V3.tsv" "$workload" <<'PY'
import json
import pathlib
import sys

summary, evidence = map(pathlib.Path, sys.argv[1:3])
workload = sys.argv[3]
m = json.loads(summary.read_text(encoding="utf-8"))["metrics"]
required = (
    "DTC_L1_mode", "DTC_L1_lower_outstanding_cap", "DTC_L1_lower_requests_acquired",
    "DTC_L1_lower_requests_released", "DTC_L1_lower_outstanding",
    "DTC_L1_pib_admits", "DTC_L1_pib_retires", "DTC_L1_pib_occupancy",
    "gpu_tot_sim_cycle", "gpu_tot_sim_insn",
)
missing = [key for key in required if key not in m]
if missing:
    raise SystemExit("missing strict Base metrics: " + ", ".join(missing))
if m["DTC_L1_mode"] != "PAPER_BASE" or m["DTC_L1_lower_outstanding_cap"] != 8192:
    raise SystemExit("unexpected Base mode or lower-cap identity")
if m["DTC_L1_lower_requests_acquired"] != m["DTC_L1_lower_requests_released"]:
    raise SystemExit("lower credit conservation failed")
if m["DTC_L1_pib_admits"] != m["DTC_L1_pib_retires"]:
    raise SystemExit("PIB admit/retire conservation failed")
for key in ("DTC_L1_lower_outstanding", "DTC_L1_pib_occupancy"):
    if m[key] != 0:
        raise SystemExit("nonzero terminal state: " + key)
if m["gpu_tot_sim_cycle"] <= 0 or m["gpu_tot_sim_insn"] <= 0:
    raise SystemExit("nonpositive terminal progress")
evidence.write_text(
    "schema\tFAST64_3_BASE_ALIAS_V3\n"
    "status\tFAST64_3_BASE_PRECOMPUTED_STRICT_VALID_PENDING_FAST64_1_2_ACCEPTANCE\n"
    f"workload\t{workload}\ncycles\t{m['gpu_tot_sim_cycle']}\ninstructions\t{m['gpu_tot_sim_insn']}\n"
    f"lower_acquired\t{m['DTC_L1_lower_requests_acquired']}\nlower_released\t{m['DTC_L1_lower_requests_released']}\n"
    f"pib_admits\t{m['DTC_L1_pib_admits']}\npib_retires\t{m['DTC_L1_pib_retires']}\n"
    "terminal_state\tlower=0;pib=0\n", encoding="utf-8")
print("FAST64_3_BASE_PRECOMPUTED_STRICT_VALID_PENDING_FAST64_1_2_ACCEPTANCE")
PY

echo "FAST64_3_${workload_id}_BASE_ALIAS_V3_COLLECTED"
