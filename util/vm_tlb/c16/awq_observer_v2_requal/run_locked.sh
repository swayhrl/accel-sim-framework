#!/usr/bin/env bash
set -euo pipefail

LOCK=/data/c16/locks/c16_gpu_campaign.lock
PY=/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/bin/python
MODEL=/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct-awq/3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd
INPUT=/data/c16/stagea_runtime_qualification_v1/inputs/QWEN_AWQ_TRAIN_A_DISCOVERY_00.json
REPO=${1:?worktree required}
RAW=${2:?raw directory required}
PREFLIGHT=${3:?CPU preflight receipt required}
RUNNER=$REPO/util/vm_tlb/c16/stagea_runtime_qualification/runner.py
CAP=60

mkdir -p "$RAW"
python3 - "$PREFLIGHT" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
if d.get("status") != "PASS" or not all(d.get("checks", {}).values()):
    raise SystemExit("CPU preflight is not an all-PASS receipt")
PY
test "$(sha256sum "$RUNNER" | awk '{print $1}')" = "7f2a76a375eaa4f652553fc523f785a753180ef1402291e54beb2256ed02bb22"

REQUEST_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
REQUEST_SEC=$(date +%s)
exec 9>"$LOCK"
if ! flock -w 2700 9; then
  echo GPU_LOCK_45MIN_TIMEOUT_STOP >"$RAW/GPU_LOCK_45MIN_TIMEOUT_STOP"
  exit 75
fi
ACQUIRED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
START_SEC=$(date +%s)
LOCK_RELEASED=false

elapsed() { echo $(( $(date +%s) - START_SEC )); }
remaining() {
  local left=$(( CAP - $(elapsed) ))
  if [ "$left" -le 0 ]; then
    echo GPU_ACTIVE_BUDGET_EXCEEDED >&2
    exit 124
  fi
  echo "$left"
}
memory_used() {
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1 | tr -d ' '
}
cleanup() {
  local code=$?
  local end_utc end_sec active
  trap - EXIT INT TERM
  end_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  end_sec=$(date +%s)
  active=$(( end_sec - START_SEC ))
  flock -u 9 || true
  LOCK_RELEASED=true
  python3 - "$RAW/GPU_LOCK_RECEIPT.json" "$LOCK" "$REQUEST_UTC" "$ACQUIRED_UTC" "$end_utc" "$((START_SEC-REQUEST_SEC))" "$active" "$CAP" "$code" <<'PY'
import json,sys
path,lock,request,acquired,end,wait,active,cap,code=sys.argv[1:]
json.dump({"lock":lock,"request_utc":request,"acquired_utc":acquired,"end_utc":end,
           "wait_seconds":int(wait),"gpu_active_wall_seconds":int(active),
           "gpu_active_cap_seconds":int(cap),"within_cap":int(active)<=int(cap),
           "exit_code":int(code),"released":True},open(path,"w"),indent=2,sort_keys=True)
open(path,"a").write("\n")
PY
  exit "$code"
}
trap cleanup EXIT INT TERM

COMPUTE_PIDS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^$/d' || true)
if [ -n "$COMPUTE_PIDS" ]; then
  echo "unexpected compute PIDs under acquired campaign lock: $COMPUTE_PIDS" >"$RAW/GPU_BUSY_OUTSIDE_LOCK_STOP"
  exit 76
fi

BASELINE_MIB=$(memory_used)
nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap,memory.total,memory.used,memory.free --format=csv,noheader >"$RAW/GPU_PRE.csv"

LEFT=$(remaining)
if (cd "$REPO" && timeout --kill-after=2s "${LEFT}s" "$PY" "$RUNNER" \
    --target QWEN_AWQ --graph-mode off --model "$MODEL" --input-json "$INPUT" \
    --output "$RAW/QWEN_AWQ_GRAPH_OFF_NATIVE.json") \
    >"$RAW/QWEN_AWQ_GRAPH_OFF_NATIVE.stdout.log" 2>"$RAW/QWEN_AWQ_GRAPH_OFF_NATIVE.stderr.log"; then
  :
else
  code=$?
  echo "$code" >"$RAW/NATIVE_EXIT_CODE"
  exit "$code"
fi
echo 0 >"$RAW/NATIVE_EXIT_CODE"
python3 - "$RAW/QWEN_AWQ_GRAPH_OFF_NATIVE.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
assert d["status"] == "PASS"
assert [x["arm"] for x in d["native_runs"]] == ["OFF","ON","ON","OFF","OFF","ON"]
PY

POST_NATIVE_MIB=$(memory_used)
if [ "$POST_NATIVE_MIB" -gt "$((BASELINE_MIB+256))" ]; then
  echo "native process did not release GPU memory" >"$RAW/GPU_MEMORY_RELEASE_FAILED"
  exit 77
fi

LEFT=$(remaining)
if (cd "$REPO" && timeout --kill-after=2s "${LEFT}s" nsys profile \
    --trace=cuda,nvtx --sample=none --cpuctxsw=none \
    --capture-range=nvtx --nvtx-capture=C16_STAGEA_QWEN_AWQ_off_INSTRUMENT_ON \
    --capture-range-end=stop --force-overwrite=true \
    --output="$RAW/QWEN_AWQ_GRAPH_OFF_OBSERVER_V2_STRUCTURAL" \
    "$PY" "$RUNNER" --target QWEN_AWQ --graph-mode off --model "$MODEL" \
    --input-json "$INPUT" --output "$RAW/QWEN_AWQ_GRAPH_OFF_NSYS.json") \
    >"$RAW/QWEN_AWQ_GRAPH_OFF_NSYS.stdout.log" 2>"$RAW/QWEN_AWQ_GRAPH_OFF_NSYS.stderr.log"; then
  :
else
  code=$?
  echo "$code" >"$RAW/NSYS_EXIT_CODE"
  exit "$code"
fi
echo 0 >"$RAW/NSYS_EXIT_CODE"

POST_NSYS_MIB=$(memory_used)
if [ "$POST_NSYS_MIB" -gt "$((BASELINE_MIB+256))" ]; then
  echo "NSYS process did not release GPU memory" >"$RAW/GPU_MEMORY_RELEASE_FAILED"
  exit 77
fi
if [ ! -s "$RAW/QWEN_AWQ_GRAPH_OFF_OBSERVER_V2_STRUCTURAL.nsys-rep" ]; then
  echo "NSYS report missing" >"$RAW/NSYS_REPORT_MISSING"
  exit 78
fi

nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap,memory.total,memory.used,memory.free --format=csv,noheader >"$RAW/GPU_POST.csv"
python3 - "$RAW/GPU_MEMORY_RELEASE.json" "$BASELINE_MIB" "$POST_NATIVE_MIB" "$POST_NSYS_MIB" <<'PY'
import json,sys
path,base,native,nsys=sys.argv[1:]
json.dump({"baseline_mib":int(base),"post_native_mib":int(native),"post_nsys_mib":int(nsys),
           "tolerance_mib":256,"native_release_pass":int(native)<=int(base)+256,
           "nsys_release_pass":int(nsys)<=int(base)+256},open(path,"w"),indent=2,sort_keys=True)
open(path,"a").write("\n")
PY

if [ "$(elapsed)" -gt "$CAP" ]; then
  echo GPU_ACTIVE_BUDGET_EXCEEDED >"$RAW/GPU_ACTIVE_BUDGET_EXCEEDED"
  exit 124
fi
echo PASS >"$RAW/LOCKED_CANARY_COMPLETE"
