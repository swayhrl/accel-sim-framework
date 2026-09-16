#!/usr/bin/env bash
set -euo pipefail
exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo 'GPU_LOCK_BUSY'
  exit 75
fi
export PATH=/usr/local/cuda-12.8/bin:$PATH
root=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2
run=${1:?run directory required}
mkdir -p "$run/raw"
nvidia-smi --query-gpu=uuid,memory.used --format=csv,noheader > "$run/gpu_before.csv"
set +e
env LD_PRELOAD=/data/c16/awma/simcompat-v2/route_b/bin/route_b_live_raw.so \
  ROUTE_B_RAW_DIR="$run/raw" TOOL_VERBOSE=0 \
  /data/c16/awma/simcompat-v2/route_b/bin/vectoradd_sm89 \
  >"$run/vectoradd.stdout" 2>"$run/vectoradd.stderr"
rc=$?
set -e
printf '%s\n' "$rc" > "$run/vectoradd.exitcode"
if [ "$rc" -ne 0 ]; then
  echo 'ROUTE_B_LIVE_APP_FAILED'
  exit "$rc"
fi
grep -q '^ROUTEB_TERMINAL_COMPLETE ' "$run/vectoradd.stdout"
test -f "$run/raw/kernelslist"
test -n "$(find "$run/raw" -maxdepth 1 -name 'kernel-*.trace.xz' -type f -print -quit)"
test -z "$(find "$run/raw" -maxdepth 1 -name '*.partial' -type f -print -quit)"
grep '^ROUTEB_LIFECYCLE\|^ROUTEB_TERMINAL_COMPLETE' "$run/vectoradd.stdout" > "$run/lifecycle.log"
echo 'ROUTEB_LIFECYCLE postprocessing_started' >> "$run/lifecycle.log"
"$root/util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing" "$run/raw" >"$run/postprocess.stdout" 2>"$run/postprocess.stderr"
for trace in "$run"/raw/kernel-*.traceg.xz; do
  test -f "$trace"
  complete=0
  for attempt in $(seq 1 50); do
    if xz -t "$trace" 2>/dev/null; then
      complete=1
      break
    fi
    sleep 0.1
  done
  if [ "$complete" -ne 1 ]; then
    echo "TRACEG_COMPRESSION_INCOMPLETE $trace" >&2
    exit 1
  fi
  /data/c16/awma/simcompat-v1/bin/traceg_grammar_smoke "$trace" >"$trace.grammar.json"
done
echo 'ROUTEB_LIFECYCLE postprocessing_completed' >> "$run/lifecycle.log"
sha256sum "$run"/raw/kernelslist "$run"/raw/kernelslist.g "$run"/raw/kernel-*.trace.xz "$run"/raw/kernel-*.traceg.xz > "$run/SHA256SUMS"
nvidia-smi --query-gpu=uuid,memory.used --format=csv,noheader > "$run/gpu_after.csv"
echo ROUTE_B_LIVE_ONCE_PASS
