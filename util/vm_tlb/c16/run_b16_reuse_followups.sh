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

diagnostic=$run_root/M1_B16_DIAGNOSTIC
repeat=$run_root/R0_BASELINE_REPEAT
mkdir -p "$diagnostic" "$repeat"
cp "$pack/configs/M1_B16_DIAGNOSTIC.gpgpusim.config" "$diagnostic/gpgpusim.config"
cp "$pack/configs/R0_BASELINE.gpgpusim.config" "$repeat/gpgpusim.config"

set +e
"$runner" M1_B16_DIAGNOSTIC "$diagnostic" "$diagnostic/gpgpusim.config" \
  > "$diagnostic/runner.stdout" 2> "$diagnostic/runner.stderr" &
diagnostic_pid=$!
if [[ ! -s $repeat/RUN_RECEIPT.json ]]; then
  repeat_pid=""
  if [[ -s $repeat/RUNNER_PID ]]; then
    candidate_pid=$(<"$repeat/RUNNER_PID")
    if kill -0 "$candidate_pid" 2>/dev/null; then repeat_pid=$candidate_pid; fi
  fi
  if [[ -z $repeat_pid ]]; then
    "$runner" R0_BASELINE "$repeat" "$repeat/gpgpusim.config" \
      > "$repeat/runner.stdout" 2> "$repeat/runner.stderr" &
    repeat_pid=$!
    printf '%s\n' "$repeat_pid" > "$repeat/RUNNER_PID"
  fi
fi
wait "$diagnostic_pid"
diagnostic_exit=$?
set -e
if [[ $diagnostic_exit -eq 0 ]]; then
  (cd "$diagnostic" && sha256sum -c OUTPUT_SHA256SUMS)
fi

while [[ ! -s $repeat/RUN_RECEIPT.json || ! -s $repeat/OUTPUT_SHA256SUMS ]]; do
  if [[ -s $repeat/RUNNER_PID ]] && ! kill -0 "$(<"$repeat/RUNNER_PID")" 2>/dev/null; then
    echo "R0 repeat exited without complete authority" >&2
    exit 1
  fi
  sleep 60
done
(cd "$repeat" && sha256sum -c OUTPUT_SHA256SUMS)
repeat_exit=$(python3 - "$repeat/RUN_RECEIPT.json" <<'PY'
import json
import sys
receipt = json.load(open(sys.argv[1], encoding="utf-8"))
valid = (receipt.get("condition") == "R0_BASELINE" and
         receipt.get("status") == "PASS" and
         receipt.get("exit_code") == 0 and
         receipt.get("core_head_at_launch") == "0271de82432db004beed43280ed01057246a0f2c" and
         receipt.get("binary_sha256") == "6be0986958ffbb8a128ce19e8a88b53a4c4838f97202c2f3d1c9dec6e9a02186" and
         receipt.get("config_sha256") == "a8918f1407fc2a9146808625b55a5120f64bb2cf4ce8b6a5b399ac4654d36d96")
print(0 if valid else 1)
PY
)

status=FAIL
if [[ $diagnostic_exit -eq 0 && $repeat_exit -eq 0 ]]; then status=PASS; fi
cat > "$run_root/FOLLOWUP_RECEIPT.json" <<EOF
{
  "schema": "C16_E1_B16_REUSE_FOLLOWUP_RECEIPT_V1",
  "status": "$status",
  "diagnostic_exit_code": $diagnostic_exit,
  "repeat_exit_code": $repeat_exit
}
EOF
exit $(( diagnostic_exit != 0 || repeat_exit != 0 ))
