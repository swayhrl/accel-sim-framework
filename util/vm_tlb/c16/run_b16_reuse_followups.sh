#!/usr/bin/env bash
set -euo pipefail

run_root=/root/share/mnt164/huangrulin/c16_ai_workload/consumer_runs/C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1_20260926T0506Z
framework=/root/workspace/accel-sim-framework-c16-e1-oracle-elastic-b16-reuse-canary-174new-v1
runner=$framework/util/vm_tlb/c16/run_b16_reuse_condition_v2.sh
pack=$framework/docs/vm_tlb/review_packs/C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1

while [[ ! -s $run_root/R0_BASELINE/RUN_RECEIPT.json ||
         ! -s $run_root/M1_B16/RUN_RECEIPT.json ]]; do
  sleep 60
done

python3 - "$run_root/R0_BASELINE/RUN_RECEIPT.json" \
          "$run_root/M1_B16/RUN_RECEIPT.json" <<'PY'
import json
import sys
for path in sys.argv[1:]:
    receipt = json.load(open(path, encoding="utf-8"))
    if receipt.get("status") != "PASS" or receipt.get("exit_code") != 0:
        raise SystemExit(f"primary run did not close PASS: {path}")
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
"$runner" R0_BASELINE "$repeat" "$repeat/gpgpusim.config" \
  > "$repeat/runner.stdout" 2> "$repeat/runner.stderr" &
repeat_pid=$!
wait "$diagnostic_pid"
diagnostic_exit=$?
wait "$repeat_pid"
repeat_exit=$?
set -e

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
