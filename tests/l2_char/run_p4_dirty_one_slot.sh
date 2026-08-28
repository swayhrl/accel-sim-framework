#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core_root=${GPGPUSIM_ROOT:-/workspace/worktrees/gpgpu-sim-l2-char}
out=${1:-"$root/tests/l2_char/results/closeout-p4"}
sim=$root/gpu-simulator/bin/release/accel-sim.out
base=$core_root/configs/tested-cfgs/SM7_QV100/gpgpusim.config
trace_cfg=$root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config
overlay=$root/tests/l2_char/p4_dirty_one_slot.config
trace=$root/tests/l2_char/traces/missq/kernelslist-dirty-one-slot.g

mkdir -p "$out"
(cd "$out" && "$sim" -config "$base" -config "$trace_cfg" \
  -config "$overlay" -trace "$trace") >"$out/run.log" 2>&1

python3 - "$out/run.log" <<'PY'
import re, sys
text = open(sys.argv[1]).read()
assert 'GPGPU-Sim: *** exit detected ***' in text
def values(name): return [int(x) for x in re.findall(r'^'+re.escape(name)+r'\s*=\s*(\d+)\s*$', text, re.M)]
npart = values('Total number of memory sub partition')[-1]
def total(name): return sum(values(name)[-npart:])
assert total('L2_char_missq_dirty_miss_block_one_slot') > 0
assert total('L2_char_missq_dirty_block_no_mutation') > 0
assert total('L2_char_missq_dirty_block_partial_mutation') == 0
assert total('L2_char_missq_dirty_miss_admit_two_slots') > 0
for name in ('L2_char_preview_commit_mismatch',): assert total(name) == 0
for name in ('L2_char_resource_leak_free','L2_char_credit_leak_free'):
    assert all(x == 1 for x in values(name)[-npart:])
print('P4 PASS dirty-one-slot block/no-mutation/admit-two-slot validated')
PY
