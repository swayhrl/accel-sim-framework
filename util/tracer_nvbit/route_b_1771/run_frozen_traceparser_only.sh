#!/usr/bin/env bash
set -euo pipefail
wt=/home/huangrulin/workspace/worktrees/accel-sim-awma-consumer25-checkpoint
out=/data/c16/awma/simcompat-v2/ldgdepbar_diagnostic_20260917
trace=/data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z/raw/kernel-34-ctx_0x5dd0a1addd30.traceg.xz
mkdir -p "$out"
g++ -std=c++17 -O2 -Wall -Wextra -I "$wt/gpu-simulator/trace-parser" \
  /tmp/frozen_traceparser_only_smoke.cc "$wt/gpu-simulator/trace-parser/trace_parser.cc" \
  -o "$out/frozen_traceparser_only"
sha256sum /tmp/frozen_traceparser_only_smoke.cc "$wt/gpu-simulator/trace-parser/trace_parser.cc" "$out/frozen_traceparser_only" > "$out/SHA256SUMS"
set +e
"$out/frozen_traceparser_only" "$trace" > "$out/stdout" 2> "$out/stderr"
rc=$?
set -e
printf '%s\n' "$rc" > "$out/returncode"
echo FROZEN_TRACEPARSER_ONLY_DONE rc="$rc"
