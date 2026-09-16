#!/usr/bin/env bash
set -euo pipefail
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -n 9 || { echo GPU_LOCK_BUSY; exit 75; }
export PATH=/usr/local/cuda-12.8/bin:$PATH
export NVDISASM=/usr/local/cuda-12.8/bin/nvdisasm
export NO_EAGER_LOAD=0
root=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2
run=${1:?run directory required}
mkdir -p "$run/raw"
df -B1 /data > "$run/disk_before.txt"
nvidia-smi --query-gpu=uuid,memory.used --format=csv,noheader > "$run/gpu_before.csv"
env CUDA_INJECTION64_PATH=/data/c16/awma/simcompat-v2/route_b/bin/route_b_live_raw.so \
  ROUTE_B_RAW_DIR="$run/raw" \
  ROUTE_B_FUNCTION_REGEX='^void pytorch_flash::flash_fwd_kernel.*' \
  ROUTE_B_FUNCTION_OCCURRENCE=0 \
  TOOL_VERBOSE=0 \
  /data/c16/env/c16-py310/bin/python \
  "$root/util/vm_tlb/awma/simulation/q05_s2_exact_driver.py" \
  > "$run/stdout.log" 2> "$run/stderr.log"
grep -q '"status": "EXACT_Q05_S2_EXECUTION_COMPLETE"' "$run/stdout.log"
grep -q '^ROUTEB_TERMINAL_COMPLETE ' "$run/stdout.log"
grep -q 'selector_occurrence=0 selected=1' "$run/stdout.log"
test -f "$run/raw/kernelslist"
test -n "$(find "$run/raw" -maxdepth 1 -type f -name 'kernel-*.trace.xz' -print -quit)"
test -z "$(find "$run/raw" -maxdepth 1 -type f -name '*.partial' -print -quit)"
grep '^ROUTEB_LIFECYCLE\|^ROUTEB_TERMINAL_COMPLETE' "$run/stdout.log" > "$run/lifecycle.log"
echo 'ROUTEB_LIFECYCLE postprocessing_started' >> "$run/lifecycle.log"
"$root/util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing" "$run/raw" > "$run/postprocess.stdout" 2> "$run/postprocess.stderr"
for trace in "$run"/raw/kernel-*.traceg.xz; do
  complete=0
  for attempt in $(seq 1 100); do
    if xz -t "$trace" 2>/dev/null; then complete=1; break; fi
    sleep 0.1
  done
  [ "$complete" -eq 1 ] || { echo TRACEG_COMPRESSION_INCOMPLETE >&2; exit 1; }
  /data/c16/awma/simcompat-v1/bin/traceg_grammar_smoke "$trace" > "$trace.grammar.json"
done
echo 'ROUTEB_LIFECYCLE postprocessing_completed' >> "$run/lifecycle.log"
df -B1 /data > "$run/disk_after.txt"
nvidia-smi --query-gpu=uuid,memory.used --format=csv,noheader > "$run/gpu_after.csv"
sha256sum "$run"/stdout.log "$run"/stderr.log "$run"/lifecycle.log "$run"/raw/kernelslist "$run"/raw/kernelslist.g "$run"/raw/kernel-*.trace.xz "$run"/raw/kernel-*.traceg.xz > "$run/SHA256SUMS"
echo Q05_ROUTEB_CAPTURE_PASS
