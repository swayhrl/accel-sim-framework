#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core=${GPGPUSIM_ROOT:?source the characterization core environment first}
out=${1:-"$root/tests/l2_char/results/c4-dataport"}
sim=$root/gpu-simulator/bin/release/accel-sim.out
base=$core/configs/tested-cfgs/SM7_QV100/gpgpusim.config
trace_cfg=$root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config
trace=$root/tests/l2_char/traces/writeback/kernelslist.g
overlay=$root/tests/l2_char/char_dataport_pressure.config

mkdir -p "$out"
(cd "$out" && "$sim" -config "$base" -config "$trace_cfg" -config "$overlay" -trace "$trace") >"$out/run.log" 2>&1
python3 - "$out/run.log" <<'PY'
import re, sys
text = open(sys.argv[1]).read()
rows = re.findall(r'^L2CHARV1\|SLICE\|.*$', text, re.M)
assert rows and 'status=FAIL' not in text
row = rows[-1]
def field(name):
    return int(re.search(name + r'=(\d+)', row).group(1))
assert field('block_dataport_eligible') > 0
assert field('block_dataport_blocked') > 0
assert field('block_dataport_blocked') <= field('block_dataport_eligible')
assert field('block_dataport_requests') == field('block_dataport_episodes')
print('C4 DataPort PASS eligible=%d blocked=%d requests=%d' %
      (field('block_dataport_eligible'), field('block_dataport_blocked'),
       field('block_dataport_requests')))
PY
