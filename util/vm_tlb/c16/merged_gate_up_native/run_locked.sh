#!/usr/bin/env bash
set -euo pipefail

LOCK=/data/c16/locks/c16_gpu_campaign.lock
PY_B0=/data/c16/env/c16-awq-v6/bin/python
PY_B2=/data/c16/merged_gate_up_native_v1/env/vllm-df8fd42-py312/bin/python
NSYS=/usr/local/bin/nsys
REPO=${1:?worktree required}
RAW=${2:?raw directory required}
PREFLIGHT=${3:?CPU preflight receipt required}
PRIOR_GPU_WALL_SECONDS=${4:-0}
TOTAL_MAX_GPU_WALL_SECONDS=480
MAX_GPU_WALL_SECONDS=$((TOTAL_MAX_GPU_WALL_SECONDS-PRIOR_GPU_WALL_SECONDS))
if [ "$MAX_GPU_WALL_SECONDS" -le 0 ]; then
  echo GPU_WALL_BUDGET_EXHAUSTED_BEFORE_RESTART >&2
  exit 124
fi
B0=$REPO/util/vm_tlb/c16/e1_operator_family_natural.py
B2=$REPO/util/vm_tlb/c16/merged_gate_up_native/b2_runner.py
TOOLS=$REPO/util/vm_tlb/c16/merged_gate_up_native
TIMELINE_TOOLS=$REPO/util/vm_tlb/c16/ffn_timeline_capture
export CUDA_CACHE_PATH=/data/c16/merged_gate_up_native_v1/cache/cuda
export TRITON_CACHE_DIR=/data/c16/merged_gate_up_native_v1/cache/triton
export TORCHINDUCTOR_CACHE_DIR=/data/c16/merged_gate_up_native_v1/cache/torchinductor
export PYTHONHASHSEED=0
mkdir -p "$RAW" "$CUDA_CACHE_PATH" "$TRITON_CACHE_DIR" "$TORCHINDUCTOR_CACHE_DIR"

python3 - "$PREFLIGHT" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
if d.get("status") != "PASS": raise SystemExit("CPU preflight not PASS")
PY

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
  printf '{"lock":"%s","request_utc":"%s","acquired_utc":"%s","end_utc":"%s","wait_seconds":%d,"gpu_wall_seconds":%d,"prior_aborted_engineering_gpu_wall_seconds":%d,"cumulative_gpu_wall_seconds":%d,"total_max_gpu_wall_seconds":480,"exit_code":%d,"released":true}\n' "$LOCK" "$REQUEST_UTC" "$START_UTC" "$END_UTC" "$((START_SEC-REQUEST_SEC))" "$((END_SEC-START_SEC))" "$PRIOR_GPU_WALL_SECONDS" "$((PRIOR_GPU_WALL_SECONDS+END_SEC-START_SEC))" "$code" >"$RAW/GPU_LOCK_RECEIPT.json"
  flock -u 9 || true
  exit "$code"
}
trap cleanup EXIT INT TERM
remaining() {
  local used=$(( $(date +%s)-START_SEC ))
  local left=$((MAX_GPU_WALL_SECONDS-used))
  if [ "$left" -le 0 ]; then echo GPU_WALL_BUDGET_EXCEEDED >&2; exit 124; fi
  echo "$left"
}
profile_b0() {
  local prefix=$RAW/canary_b0
  local left; left=$(remaining)
  (cd "$REPO" && timeout "${left}s" "$NSYS" profile --trace=cuda,nvtx --sample=none --cpuctxsw=none --force-overwrite=true --output="$prefix" "$PY_B0" "$B0" --condition CONTROL_GUD84 --run-index 9000 --output "$prefix.json" --timeline-nvtx on --ffn-baseline-measurement on --tensor-dump "$prefix.tensors.pt") >"$prefix.stdout.log" 2>"$prefix.stderr.log"
  test -s "$prefix.json"; test -s "$prefix.tensors.pt"; test -s "$prefix.nsys-rep"
  "$NSYS" export --type=sqlite --force-overwrite=true --output="$prefix.sqlite" "$prefix.nsys-rep" >"$prefix.export.stdout.log" 2>"$prefix.export.stderr.log"
}
profile_b2() {
  local prefix=$RAW/canary_b2
  local left; left=$(remaining)
  (cd "$REPO" && timeout "${left}s" "$NSYS" profile --trace=cuda,nvtx --sample=none --cpuctxsw=none --force-overwrite=true --output="$prefix" "$PY_B2" "$B2" --run-index 9000 --output "$prefix.json" --timeline-nvtx on --tensor-dump "$prefix.tensors.pt") >"$prefix.stdout.log" 2>"$prefix.stderr.log"
  test -s "$prefix.json"; test -s "$prefix.tensors.pt"; test -s "$prefix.nsys-rep"
  "$NSYS" export --type=sqlite --force-overwrite=true --output="$prefix.sqlite" "$prefix.nsys-rep" >"$prefix.export.stdout.log" 2>"$prefix.export.stderr.log"
}
run_formal() {
  local block=$1 position=$2 arm=$3 index=$4
  local lower; lower=$(echo "$arm" | tr '[:upper:]' '[:lower:]')
  local prefix=$RAW/formal_block$(printf '%02d' "$block")_pos${position}_${lower}
  local left; left=$(remaining)
  if [ "$arm" = B0 ]; then
    (cd "$REPO" && timeout "${left}s" "$PY_B0" "$B0" --condition CONTROL_GUD84 --run-index "$index" --output "$prefix.json" --timeline-nvtx off --ffn-baseline-measurement on) >"$prefix.stdout.log" 2>"$prefix.stderr.log"
  else
    (cd "$REPO" && timeout "${left}s" "$PY_B2" "$B2" --run-index "$index" --output "$prefix.json" --timeline-nvtx off) >"$prefix.stdout.log" 2>"$prefix.stderr.log"
  fi
  test -s "$prefix.json"
}

nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap,memory.total,memory.free --format=csv,noheader >"$RAW/GPU_PRE.csv"
profile_b0
profile_b2
"$PY_B0" "$TOOLS/compare_canary.py" --b0-json "$RAW/canary_b0.json" --b2-json "$RAW/canary_b2.json" --b0-tensors "$RAW/canary_b0.tensors.pt" --b2-tensors "$RAW/canary_b2.tensors.pt" --output-dir "$RAW"
PYTHONPATH="$TOOLS:$TIMELINE_TOOLS" "$PY_B0" "$TOOLS/timeline_audit.py" --b0-sqlite "$RAW/canary_b0.sqlite" --b2-sqlite "$RAW/canary_b2.sqlite" --b2-json "$RAW/canary_b2.json" --output-dir "$RAW"
echo PASS >"$RAW/CANARY_PASS"

index=9100
for block in $(seq 0 11); do
  run_formal "$block" 0 B0 "$index"; index=$((index+1))
  run_formal "$block" 1 B2 "$index"; index=$((index+1))
  run_formal "$block" 2 B2 "$index"; index=$((index+1))
  run_formal "$block" 3 B0 "$index"; index=$((index+1))
done
nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap,memory.total,memory.free --format=csv,noheader >"$RAW/GPU_POST.csv"
echo PASS >"$RAW/LOCKED_CAPTURE_COMPLETE"
