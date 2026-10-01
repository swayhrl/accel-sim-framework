#!/usr/bin/env bash
set -euo pipefail

LOCK=/data/c16/locks/c16_gpu_campaign.lock
PY=/data/c16/env/c16-awq-v6/bin/python
NSYS=/usr/local/bin/nsys
REPO=${1:?repo worktree required}
RAW=${2:?raw directory required}
PREFLIGHT=${3:?V2 source preflight required}
RUNNER=$REPO/util/vm_tlb/c16/e1_operator_family_natural.py
V1_TOOLS=$REPO/util/vm_tlb/c16/ffn_gate_up_concurrency
TIMELINE_TOOLS=$REPO/util/vm_tlb/c16/ffn_timeline_capture

python3 - "$PREFLIGHT" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
if d.get("status") != "PASS": raise SystemExit("V2 source preflight not PASS")
if d.get("result_runner_sha256") != "0297e142457ea5ac4ed3d6c37889993fda4168bfcca8392b41d74ba4b698fc0b":
    raise SystemExit("V2 runner SHA mismatch")
PY
mkdir -p "$RAW"
REQUEST_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
REQUEST_SEC=$(date +%s)
exec 9>"$LOCK"
if ! flock -w 2700 9; then
  echo GPU_LOCK_45MIN_TIMEOUT_STOP >"$RAW/GPU_LOCK_45MIN_TIMEOUT_STOP"
  exit 75
fi
START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
START_SEC=$(date +%s)
cleanup() {
  code=$?
  END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  END_SEC=$(date +%s)
  printf '{"lock":"%s","request_utc":"%s","acquired_utc":"%s","end_utc":"%s","wait_seconds":%d,"gpu_wall_seconds":%d,"max_gpu_wall_seconds":480,"exit_code":%d,"released":true,"campaign":"C16_FFN_GATE_UP_CONCURRENCY_NATIVE_DIAGNOSTIC_V2"}\n' "$LOCK" "$REQUEST_UTC" "$START_UTC" "$END_UTC" "$((START_SEC-REQUEST_SEC))" "$((END_SEC-START_SEC))" "$code" >"$RAW/GPU_LOCK_RECEIPT.json"
  flock -u 9 || true
  exit "$code"
}
trap cleanup EXIT INT TERM
remaining() {
  local used=$(( $(date +%s)-START_SEC ))
  local left=$((480-used))
  if [ "$left" -le 0 ]; then echo GPU_WALL_BUDGET_EXCEEDED >&2; exit 124; fi
  echo "$left"
}
profile_one() {
  local label=$1 arm=$2 index=$3
  local prefix=$RAW/$label
  local left; left=$(remaining)
  (cd "$REPO" && timeout "${left}s" "$NSYS" profile --trace=cuda,nvtx --sample=none --cpuctxsw=none --force-overwrite=true --output="$prefix" "$PY" "$RUNNER" --condition CONTROL_GUD84 --run-index "$index" --output "$prefix.json" --timeline-nvtx on --gate-up-concurrency "$arm") >"$prefix.stdout.log" 2>"$prefix.stderr.log"
  test -s "$prefix.nsys-rep"; test -s "$prefix.json"
  "$NSYS" export --type=sqlite --force-overwrite=true --output="$prefix.sqlite" "$prefix.nsys-rep" >"$prefix.export.stdout.log" 2>"$prefix.export.stderr.log"
  test -s "$prefix.sqlite"
}
run_formal() {
  local block=$1 position=$2 label=$3 arm=$4 index=$5
  local prefix=$RAW/formal_block$(printf '%02d' "$block")_pos${position}_${label}
  local left; left=$(remaining)
  (cd "$REPO" && timeout "${left}s" "$PY" "$RUNNER" --condition CONTROL_GUD84 --run-index "$index" --output "$prefix.json" --timeline-nvtx off --gate-up-concurrency "$arm") >"$prefix.stdout.log" 2>"$prefix.stderr.log"
  test -s "$prefix.json"
}

nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap,memory.total,memory.free --format=csv,noheader >"$RAW/GPU_PRE.csv"
profile_one canary_b0 off 17900
profile_one canary_b1_v2 on 17900
PYTHONPATH="$V1_TOOLS:$TIMELINE_TOOLS" "$PY" "$V1_TOOLS/concurrency_canary.py" --b0-json "$RAW/canary_b0.json" --b1-json "$RAW/canary_b1_v2.json" --b0-sqlite "$RAW/canary_b0.sqlite" --b1-sqlite "$RAW/canary_b1_v2.sqlite" --output-dir "$RAW"
echo PASS >"$RAW/STAGE1_CANARY_PASS"

index=18000
for block in $(seq 0 11); do
  run_formal "$block" 0 b0 off "$index"; index=$((index+1))
  run_formal "$block" 1 b1 on  "$index"; index=$((index+1))
  run_formal "$block" 2 b1 on  "$index"; index=$((index+1))
  run_formal "$block" 3 b0 off "$index"; index=$((index+1))
done
nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap,memory.total,memory.free --format=csv,noheader >"$RAW/GPU_POST.csv"
echo PASS >"$RAW/LOCKED_CAPTURE_COMPLETE"
