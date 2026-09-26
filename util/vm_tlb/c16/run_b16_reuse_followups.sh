#!/usr/bin/env bash
set -euo pipefail

run_root=/root/share/mnt164/huangrulin/c16_ai_workload/consumer_runs/C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1_20260926T0506Z
framework=/root/workspace/accel-sim-framework-c16-e1-oracle-elastic-b16-reuse-canary-174new-v1
runner=$framework/util/vm_tlb/c16/run_b16_reuse_condition_v2.sh
pack=$framework/docs/vm_tlb/review_packs/C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1

while [[ ! -s $run_root/R0_BASELINE/RUN_RECEIPT.json ||
         ! -s $run_root/R0_BASELINE/OUTPUT_SHA256SUMS ||
         ! -s $run_root/M1_B16/RUN_RECEIPT.json ||
         ! -s $run_root/M1_B16/OUTPUT_SHA256SUMS ]]; do
  sleep 60
done

(cd "$run_root/R0_BASELINE" && sha256sum -c OUTPUT_SHA256SUMS)
(cd "$run_root/M1_B16" && sha256sum -c OUTPUT_SHA256SUMS)

set +e
python3 - "$run_root/R0_BASELINE/RUN_RECEIPT.json" \
          "$run_root/M1_B16/RUN_RECEIPT.json" <<'PY'
import json
import sys
expected = {
    "R0_BASELINE": {
        "config_sha256": "a8918f1407fc2a9146808625b55a5120f64bb2cf4ce8b6a5b399ac4654d36d96",
    },
    "M1_B16": {
        "config_sha256": "15e06af19200e7fb40af93c6a21b19290b581c327f420dd3fdefc3f4b3af3bdd",
    },
}
for path in sys.argv[1:]:
    receipt = json.load(open(path, encoding="utf-8"))
    if receipt.get("status") != "PASS" or receipt.get("exit_code") != 0:
        raise SystemExit(f"primary run did not close PASS: {path}")
    condition = receipt.get("condition")
    if condition not in expected:
        raise SystemExit(f"unexpected primary condition: {condition}")
    if receipt.get("core_head_at_launch") != "0271de82432db004beed43280ed01057246a0f2c":
        raise SystemExit(f"Core launch identity drift: {path}")
    if receipt.get("binary_sha256") != "6be0986958ffbb8a128ce19e8a88b53a4c4838f97202c2f3d1c9dec6e9a02186":
        raise SystemExit(f"binary launch identity drift: {path}")
    if receipt.get("config_sha256") != expected[condition]["config_sha256"]:
        raise SystemExit(f"config launch identity drift: {path}")
PY
primary_gate_exit=$?
set -e

diagnostic=$run_root/M1_B16_DIAGNOSTIC
repeat=$run_root/R0_BASELINE_REPEAT
mkdir -p "$diagnostic" "$repeat"
if [[ $primary_gate_exit -ne 0 ]]; then
  cat > "$diagnostic/ADMISSION_STATUS.json" <<'EOF'
{
  "schema": "C16_E1_B16_DIAGNOSTIC_ADMISSION_STATUS_V1",
  "status": "QUARANTINED_PRIMARY_GATE_FAIL",
  "scientific_admission": "QUARANTINED",
  "failure_policy": "EXCLUDE_FROM_ALL_SCIENTIFIC_RESULTS"
}
EOF
  cp "$diagnostic/ADMISSION_STATUS.json" "$pack/M1_B16_DIAGNOSTIC_ADMISSION_STATUS.json"
  cat > "$run_root/FOLLOWUP_RECEIPT.json" <<EOF
{
  "schema": "C16_E1_B16_REUSE_FOLLOWUP_RECEIPT_V2",
  "status": "QUARANTINED_PRIMARY_GATE_FAIL",
  "primary_gate_exit_code": $primary_gate_exit
}
EOF
  exit 1
fi

cat > "$diagnostic/ADMISSION_STATUS.json" <<'EOF'
{
  "schema": "C16_E1_B16_DIAGNOSTIC_ADMISSION_STATUS_V1",
  "status": "ADMITTED_PRIMARY_GATES_PASS",
  "scientific_admission": "ADMITTED",
  "primary_terminal_PASS": true,
  "primary_workload_kernel_instruction_CTA_identity": true,
  "primary_correctness_comparison": true
}
EOF
cp "$diagnostic/ADMISSION_STATUS.json" "$pack/M1_B16_DIAGNOSTIC_ADMISSION_STATUS.json"

if [[ ! -s $diagnostic/RUN_RECEIPT.json ]]; then
  diagnostic_pid=""
  if [[ -s $diagnostic/RUNNER_PID ]]; then
    candidate_pid=$(<"$diagnostic/RUNNER_PID")
    if kill -0 "$candidate_pid" 2>/dev/null; then diagnostic_pid=$candidate_pid; fi
  fi
  if [[ -z $diagnostic_pid ]]; then
    cp "$pack/configs/M1_B16_DIAGNOSTIC.gpgpusim.config" "$diagnostic/gpgpusim.config"
    "$runner" M1_B16_DIAGNOSTIC "$diagnostic" "$diagnostic/gpgpusim.config" \
      > "$diagnostic/runner.stdout" 2> "$diagnostic/runner.stderr" &
    diagnostic_pid=$!
    printf '%s\n' "$diagnostic_pid" > "$diagnostic/RUNNER_PID"
  fi
fi
while [[ ! -s $diagnostic/RUN_RECEIPT.json ||
         ! -s $diagnostic/OUTPUT_SHA256SUMS ]]; do
  if [[ -s $diagnostic/RUNNER_PID ]] &&
     ! kill -0 "$(<"$diagnostic/RUNNER_PID")" 2>/dev/null; then
    echo "diagnostic exited without complete authority" >&2
    exit 1
  fi
  sleep 60
done
(cd "$diagnostic" && sha256sum -c OUTPUT_SHA256SUMS)
set +e
python3 - "$diagnostic/RUN_RECEIPT.json" <<'PY'
import json
import sys
receipt = json.load(open(sys.argv[1], encoding="utf-8"))
valid = (receipt.get("condition") == "M1_B16_DIAGNOSTIC" and
         receipt.get("status") == "PASS" and receipt.get("exit_code") == 0 and
         receipt.get("terminal_exit_detected") is True and
         receipt.get("core_head_at_launch") == "0271de82432db004beed43280ed01057246a0f2c" and
         receipt.get("binary_sha256") == "6be0986958ffbb8a128ce19e8a88b53a4c4838f97202c2f3d1c9dec6e9a02186" and
         receipt.get("config_sha256") == "12434fee397093b2ac13cf65e1b2644b8f7a98ad97e3824a2cbfae5aba5daee7")
raise SystemExit(0 if valid else 1)
PY
diagnostic_exit=$?
set -e

bounded_repeat_exit=1
set +e
python3 - "$pack/BOUNDED_REPRODUCIBILITY_PREFIX_UID168.json" <<'PY'
import json
import sys
evidence = json.load(open(sys.argv[1], encoding="utf-8"))
valid = (evidence.get("status") == "PASS" and
         evidence.get("claim") == "BOUNDED_REPRODUCIBILITY_PREFIX_PASS_UID168" and
         evidence.get("bounded_prefix_last_uid") == 168 and
         evidence.get("full_1565_kernel_repeat_claimed") is False)
raise SystemExit(0 if valid else 1)
PY
bounded_repeat_exit=$?
set -e

analysis_exit=1
if [[ $diagnostic_exit -eq 0 && $bounded_repeat_exit -eq 0 ]]; then
  set +e
  python3 "$framework/util/vm_tlb/c16/e1_b16_reuse_canary.py" analyze \
    --scope "$pack/REUSE_WINDOW_SCOPE.json" \
    --sequence "$pack/REUSE_WINDOW_SEQUENCE.tsv" \
    --r0 "$run_root/R0_BASELINE" \
    --m1 "$run_root/M1_B16" \
    --diagnostic "$diagnostic" \
    --repeat "$repeat" \
    --bounded-repeat-evidence "$pack/BOUNDED_REPRODUCIBILITY_PREFIX_UID168.json" \
    --output "$pack" \
    > "$run_root/analysis.stdout" 2> "$run_root/analysis.stderr"
  analysis_exit=$?
  set -e
fi

status=FAIL
if [[ $diagnostic_exit -eq 0 && $bounded_repeat_exit -eq 0 && $analysis_exit -eq 0 ]]; then
  status=PASS
fi
cat > "$run_root/FOLLOWUP_RECEIPT.json" <<EOF
{
  "schema": "C16_E1_B16_REUSE_FOLLOWUP_RECEIPT_V2",
  "status": "$status",
  "diagnostic_exit_code": $diagnostic_exit,
  "bounded_repeat_exit_code": $bounded_repeat_exit,
  "reproducibility_claim": "BOUNDED_REPRODUCIBILITY_PREFIX_PASS_UID168",
  "analysis_exit_code": $analysis_exit
}
EOF
exit $(( diagnostic_exit != 0 || bounded_repeat_exit != 0 || analysis_exit != 0 ))
