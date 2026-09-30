#!/usr/bin/env bash
set -euo pipefail

LOCK=/data/c16/locks/c16_gpu_campaign.lock
PY=/data/c16/env/c16-awq-v6/bin/python
NSYS=/usr/local/bin/nsys
REPO=${1:?repo worktree required}
RAW=${2:?raw run directory required}
IDENTITY=${3:?identity receipt required}
RUNNER=$REPO/util/vm_tlb/c16/e1_operator_family_natural.py
TOOLS=$REPO/util/vm_tlb/c16/ffn_timeline_capture

python3 - "$IDENTITY" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
if d.get("status")!="PASS": raise SystemExit("identity preflight not PASS")
PY
mkdir -p "$RAW"
exec 9>"$LOCK"
if ! flock -w 2700 9; then
  printf '%s\n' GPU_LOCK_45MIN_TIMEOUT_STOP >"$RAW/GPU_LOCK_45MIN_TIMEOUT_STOP"
  exit 75
fi
START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
START_SEC=$(date +%s)
cleanup() {
  code=$?
  END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  END_SEC=$(date +%s)
  printf '{"lock":"%s","start_utc":"%s","end_utc":"%s","wall_seconds":%d,"exit_code":%d}\n' "$LOCK" "$START_UTC" "$END_UTC" "$((END_SEC-START_SEC))" "$code" >"$RAW/GPU_LOCK_RECEIPT.json"
  flock -u 9 || true
  exit "$code"
}
trap cleanup EXIT INT TERM
remaining() {
  local used=$(( $(date +%s)-START_SEC ))
  local left=$((1200-used))
  if [ "$left" -le 0 ]; then echo GPU_WALL_BUDGET_EXCEEDED >&2; exit 124; fi
  echo "$left"
}
profile_one() {
  local label=$1 mode=$2 index=$3
  local prefix=$RAW/$label
  local left
  left=$(remaining)
  (cd "$REPO" && timeout "${left}s" "$NSYS" profile --trace=cuda,nvtx --sample=none --cpuctxsw=none --force-overwrite=true --output="$prefix" "$PY" "$RUNNER" --condition CONTROL_GUD84 --run-index "$index" --output "$prefix.json" --timeline-nvtx "$mode") >"$prefix.stdout.log" 2>"$prefix.stderr.log"
  test -s "$prefix.nsys-rep"
  test -s "$prefix.json"
  "$NSYS" export --type=sqlite --force-overwrite=true --output="$prefix.sqlite" "$prefix.nsys-rep" >"$prefix.export.stdout.log" 2>"$prefix.export.stderr.log"
  test -s "$prefix.sqlite"
}
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total,memory.free --format=csv,noheader >"$RAW/GPU_PRE.csv"
profile_one canary_off off 700
profile_one canary_on on 700
"$PY" "$TOOLS/compare_runs.py" --left-json "$RAW/canary_off.json" --right-json "$RAW/canary_on.json" --left-sqlite "$RAW/canary_off.sqlite" --right-sqlite "$RAW/canary_on.sqlite" --mode OFF_ON --output "$RAW/INSTRUMENTATION_NEUTRALITY.json"
profile_one formal on 701
"$PY" "$TOOLS/compare_runs.py" --left-json "$RAW/canary_on.json" --right-json "$RAW/formal.json" --left-sqlite "$RAW/canary_on.sqlite" --right-sqlite "$RAW/formal.sqlite" --mode ON_FORMAL --output "$RAW/FORMAL_SANITY.json"
"$PY" "$TOOLS/extract_timeline.py" --sqlite "$RAW/formal.sqlite" --runner-json "$RAW/formal.json" --run-id FORMAL_701 --output-dir "$RAW"
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total,memory.free --format=csv,noheader >"$RAW/GPU_POST.csv"
printf '%s\n' PASS >"$RAW/LOCKED_CAPTURE_COMPLETE"
