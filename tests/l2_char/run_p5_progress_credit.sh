#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core_root=${GPGPUSIM_ROOT:-/workspace/worktrees/gpgpu-sim-l2-char}
out=${1:-"$root/tests/l2_char/results/closeout-p5b"}
sim=$root/gpu-simulator/bin/release/accel-sim.out
base=$core_root/configs/tested-cfgs/SM7_QV100/gpgpusim.config
trace_cfg=$root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config
overlay=$root/tests/l2_char/p5_progress_credit.config
trace=$root/tests/l2_char/traces/writeback/kernelslist.g

mkdir -p "$out"
(cd "$out" && "$sim" -config "$base" -config "$trace_cfg" \
  -config "$overlay" -trace "$trace") >"$out/run.log" 2>&1

python3 - "$out/run.log" <<'PY'
import re, sys
text = open(sys.argv[1]).read()
def values(name):
    return [int(x) for x in re.findall(r'^' + re.escape(name) +
                                       r'\s*=\s*(\d+)\s*$', text, re.M)]
parts = values('Total number of memory sub partition')
npart = parts[-1] if parts else 1
def final(name): return values(name)[-npart:]
assert 'GPGPU-Sim: *** exit detected ***' in text
assert sum(final('L2_char_wb_progress_credit_use_count')) > 0
assert max(final('L2_char_wb_progress_credit_max')) <= \
       max(final('L2_char_wb_progress_credit_limit')) == 1
assert all(v == 0 for v in final('L2_char_wb_progress_credit_current'))
assert all(v == 1 for v in final('L2_char_credit_leak_free'))
assert all(v == 1 for v in final('L2_char_resource_leak_free'))
print('P5B PASS progress-credit use=%d max=%d limit=1 current=0 leaks=0' %
      (sum(final('L2_char_wb_progress_credit_use_count')),
       max(final('L2_char_wb_progress_credit_max'))))
PY
