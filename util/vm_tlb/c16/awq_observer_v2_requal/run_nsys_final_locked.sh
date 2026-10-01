#!/usr/bin/env bash
set -euo pipefail

LOCK=/data/c16/locks/c16_gpu_campaign.lock
PY=/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/bin/python
MODEL=/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct-awq/3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd
INPUT=/data/c16/stagea_runtime_qualification_v1/inputs/QWEN_AWQ_TRAIN_A_DISCOVERY_00.json
REPO=${1:?worktree required}
RAW=${2:?raw directory required}
RUNNER=$REPO/util/vm_tlb/c16/stagea_runtime_qualification/runner.py
STRUCTURAL=$REPO/util/vm_tlb/c16/awq_observer_v2_requal/nsys_structural.py
TOTAL_CAP=60

test "$(sha256sum "$RUNNER" | awk '{print $1}')" = "7f2a76a375eaa4f652553fc523f785a753180ef1402291e54beb2256ed02bb22"
python3 - "$RAW/GPU_LOCK_RECEIPT_NSYS_RETRY.json" "$RAW/QWEN_AWQ_GRAPH_OFF_NATIVE.json" <<'PY'
import json,sys
lock=json.load(open(sys.argv[1])); native=json.load(open(sys.argv[2]))
assert lock["released"] is True and lock["cumulative_gpu_active_wall_seconds"] < 60
assert native["status"] == "PASS"
PY
PRIOR_ACTIVE=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["cumulative_gpu_active_wall_seconds"])' "$RAW/GPU_LOCK_RECEIPT_NSYS_RETRY.json")
FINAL_CAP=$((TOTAL_CAP-PRIOR_ACTIVE))
if [ "$FINAL_CAP" -le 0 ]; then exit 124; fi

REQUEST_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
REQUEST_SEC=$(date +%s)
exec 9>"$LOCK"
if ! flock -w 2700 9; then exit 75; fi
ACQUIRED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
START_SEC=$(date +%s)
cleanup() {
  local code=$?
  local end_utc end_sec active cumulative
  trap - EXIT INT TERM
  end_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  end_sec=$(date +%s)
  active=$((end_sec-START_SEC))
  cumulative=$((PRIOR_ACTIVE+active))
  flock -u 9 || true
  python3 - "$RAW/GPU_LOCK_RECEIPT_NSYS_FINAL.json" "$LOCK" "$REQUEST_UTC" "$ACQUIRED_UTC" "$end_utc" "$((START_SEC-REQUEST_SEC))" "$active" "$cumulative" "$TOTAL_CAP" "$code" <<'PY'
import json,sys
path,lock,request,acquired,end,wait,active,cumulative,cap,code=sys.argv[1:]
json.dump({"lock":lock,"request_utc":request,"acquired_utc":acquired,"end_utc":end,
           "wait_seconds":int(wait),"gpu_active_wall_seconds":int(active),
           "cumulative_gpu_active_wall_seconds":int(cumulative),"gpu_active_cap_seconds":int(cap),
           "within_cumulative_cap":int(cumulative)<=int(cap),"exit_code":int(code),"released":True},
          open(path,"w"),indent=2,sort_keys=True)
open(path,"a").write("\n")
PY
  exit "$code"
}
trap cleanup EXIT INT TERM

COMPUTE_PIDS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^$/d' || true)
if [ -n "$COMPUTE_PIDS" ]; then exit 76; fi
BASELINE_MIB=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1 | tr -d ' ')

if (cd "$REPO" && timeout --kill-after=2s "${FINAL_CAP}s" nsys profile \
    --trace=cuda,nvtx --sample=none --cpuctxsw=none --force-overwrite=true \
    --output="$RAW/QWEN_AWQ_GRAPH_OFF_OBSERVER_V2_STRUCTURAL_FINAL" \
    "$PY" "$STRUCTURAL" --runner "$RUNNER" --model "$MODEL" --input-json "$INPUT" \
    --output "$RAW/QWEN_AWQ_GRAPH_OFF_NSYS_FINAL.json") \
    >"$RAW/QWEN_AWQ_GRAPH_OFF_NSYS_FINAL.stdout.log" 2>"$RAW/QWEN_AWQ_GRAPH_OFF_NSYS_FINAL.stderr.log"; then
  :
else
  code=$?
  echo "$code" >"$RAW/NSYS_FINAL_EXIT_CODE"
  exit "$code"
fi
echo 0 >"$RAW/NSYS_FINAL_EXIT_CODE"

test -s "$RAW/QWEN_AWQ_GRAPH_OFF_OBSERVER_V2_STRUCTURAL_FINAL.nsys-rep"
python3 - "$RAW/QWEN_AWQ_GRAPH_OFF_NSYS_FINAL.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
assert d["status"] == "PASS"
assert d["qualified_v2_runner_sha256"] == "7f2a76a375eaa4f652553fc523f785a753180ef1402291e54beb2256ed02bb22"
assert d["per_occurrence_cuda_events"] == 0 and d["request_level_cuda_events"] == 2
assert len(d["instrumentation"]["semantic_order"]) == 576
PY
POST_MIB=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1 | tr -d ' ')
if [ "$POST_MIB" -gt "$((BASELINE_MIB+256))" ]; then exit 77; fi
echo PASS >"$RAW/NSYS_FINAL_COMPLETE"
