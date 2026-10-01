#!/usr/bin/env bash
set -euo pipefail

LOCK=/data/c16/locks/c16_gpu_campaign.lock
PY=/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/bin/python
REPO=${1:?worktree required}
RAW=${2:?raw directory required}
PREFLIGHT=${3:?CPU preflight directory required}
RUNNER=$REPO/util/vm_tlb/c16/stagea_runtime_qualification/runner.py
DATA=/data/c16/stagea_runtime_qualification_v1
mkdir -p "$RAW"

python3 - "$PREFLIGHT" <<'PY'
import json, pathlib, sys
p=pathlib.Path(sys.argv[1])
for name in ("CANARY_AUTHORITY.json","ASSET_VISIBILITY_AND_SHA.json","CORRECTNESS_AND_NEUTRALITY_THRESHOLDS.json","GPU_CANARY_PLAN.json","AWQ_REPACK_CANONICAL_RECEIPT.json","SOURCE_PREFLIGHT.json"):
    d=json.load(open(p/name))
    if d.get("status") not in ("PASS","FROZEN_BEFORE_GPU_RESULTS","READY_FOR_LOCKED_CANARY"):
        raise SystemExit(f"preflight not PASS: {name} {d.get('status')}")
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
  printf '{"lock":"%s","request_utc":"%s","acquired_utc":"%s","end_utc":"%s","wait_seconds":%d,"gpu_active_wall_seconds":%d,"gpu_active_cap_seconds":240,"exit_code":%d,"released":true}\n' "$LOCK" "$REQUEST_UTC" "$START_UTC" "$END_UTC" "$((START_SEC-REQUEST_SEC))" "$((END_SEC-START_SEC))" "$code" >"$RAW/GPU_LOCK_RECEIPT.json"
  flock -u 9 || true
  exit "$code"
}
trap cleanup EXIT INT TERM
remaining() {
  local used=$(( $(date +%s)-START_SEC ))
  local left=$((240-used))
  if [ "$left" -le 0 ]; then echo GPU_ACTIVE_BUDGET_EXCEEDED >&2; exit 124; fi
  echo "$left"
}
memory_used() {
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1 | tr -d ' '
}
BASELINE_MIB=$(memory_used)
COMPUTE_PIDS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^$/d' || true)
if [ -n "$COMPUTE_PIDS" ]; then
  echo "unexpected compute PIDs under acquired campaign lock: $COMPUTE_PIDS" >"$RAW/GPU_BUSY_OUTSIDE_LOCK_STOP"
  exit 76
fi
nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap,memory.total,memory.used,memory.free --format=csv,noheader >"$RAW/GPU_PRE.csv"
echo -e "target\tgraph_mode\texit_code\tprocess_wall_seconds\tresult_status\terror_type\toom" >"$RAW/TARGET_EXECUTION.tsv"
echo -e "target\tgraph_mode\tbaseline_mib\tpost_exit_mib\trelease_status" >"$RAW/GPU_MEMORY_RELEASE.tsv"

run_condition() {
  local target=$1 mode=$2 model=$3 input=$4
  local prefix=$RAW/${target}_${mode}
  local left started ended code status error oom post release
  left=$(remaining); started=$(date +%s)
  if (cd "$REPO" && timeout "${left}s" "$PY" "$RUNNER" --target "$target" --graph-mode "$mode" --model "$model" --input-json "$input" --output "$prefix.json") >"$prefix.stdout.log" 2>"$prefix.stderr.log"; then
    code=0
  else
    code=$?
  fi
  ended=$(date +%s)
  if [ "$code" -eq 124 ]; then exit 124; fi
  if [ -s "$prefix.json" ]; then
    readarray -t FIELDS < <(python3 - "$prefix.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print(d.get("status","MISSING"));print(d.get("error_type") or "");print(str(bool(d.get("oom",False))).lower())
PY
)
    status=${FIELDS[0]}; error=${FIELDS[1]}; oom=${FIELDS[2]}
  else
    status=MISSING_RESULT; error=PROCESS_EXIT_$code; oom=false
  fi
  echo -e "$target\t$mode\t$code\t$((ended-started))\t$status\t$error\t$oom" >>"$RAW/TARGET_EXECUTION.tsv"
  release=FAIL; post=$(memory_used)
  for attempt in 1 2 3 4 5; do
    post=$(memory_used)
    if [ "$post" -le "$((BASELINE_MIB+256))" ]; then release=PASS; break; fi
    sleep 1
  done
  echo -e "$target\t$mode\t$BASELINE_MIB\t$post\t$release" >>"$RAW/GPU_MEMORY_RELEASE.tsv"
  if [ "$release" != PASS ]; then echo GPU_MEMORY_RELEASE_FAILED >"$RAW/GPU_MEMORY_RELEASE_FAILED"; exit 77; fi
  remaining >/dev/null
  return "$code"
}

BF=/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1
AWQ=/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct-awq/3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd
OL=/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e

if run_condition QWEN_BF16 off "$BF" "$DATA/inputs/QWEN_BF16_TRAIN_A_DISCOVERY_00.json"; then BF_OFF=0; else BF_OFF=$?; fi
if [ "$BF_OFF" -eq 0 ]; then if run_condition QWEN_BF16 on "$BF" "$DATA/inputs/QWEN_BF16_TRAIN_A_DISCOVERY_00.json"; then BF_ON=0; else BF_ON=$?; fi; else BF_ON=99; fi
if run_condition QWEN_AWQ off "$AWQ" "$DATA/inputs/QWEN_AWQ_TRAIN_A_DISCOVERY_00.json"; then AWQ_OFF=0; else AWQ_OFF=$?; fi
if [ "$AWQ_OFF" -eq 0 ]; then if run_condition QWEN_AWQ on "$AWQ" "$DATA/inputs/QWEN_AWQ_TRAIN_A_DISCOVERY_00.json"; then AWQ_ON=0; else AWQ_ON=$?; fi; else AWQ_ON=99; fi
if run_condition OLMOE off "$OL" "$DATA/inputs/OLMOE_TRAIN_A_DISCOVERY_00.json"; then OL_OFF=0; else OL_OFF=$?; fi
if [ "$OL_OFF" -eq 0 ]; then if run_condition OLMOE on "$OL" "$DATA/inputs/OLMOE_TRAIN_A_DISCOVERY_00.json"; then OL_ON=0; else OL_ON=$?; fi; else OL_ON=99; fi

nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap,memory.total,memory.used,memory.free --format=csv,noheader >"$RAW/GPU_POST.csv"
printf '{"QWEN_BF16":{"off":%d,"on":%d},"QWEN_AWQ":{"off":%d,"on":%d},"OLMOE":{"off":%d,"on":%d}}\n' "$BF_OFF" "$BF_ON" "$AWQ_OFF" "$AWQ_ON" "$OL_OFF" "$OL_ON" >"$RAW/CONDITION_EXIT_CODES.json"
echo PASS >"$RAW/LOCKED_CANARY_COMPLETE"
