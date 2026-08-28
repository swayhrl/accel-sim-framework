#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core_root=${GPGPUSIM_ROOT:-/workspace/worktrees/gpgpu-sim-l2-char}
trace_root=${L2_CHAR_TRACE_ROOT:-/workspace/worktrees/accel-sim-latebind-oracle-v1/tests/l2_latebind}
out=${1:-"$root/tests/l2_char/results/hook-off-equivalence"}
sim=$root/gpu-simulator/bin/release/accel-sim.out
base=$core_root/configs/tested-cfgs/SM7_QV100/gpgpusim.config
trace_cfg=$root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config
overlay=$root/tests/l2_char/p6_pressure.config
trace=$trace_root/pressure/kernelslist.g

mkdir -p "$out/omitted" "$out/explicit-off"
run_arm() {
  local arm=$1 extra=${2:-}
  (cd "$out/$arm" && "$sim" -config "$base" -config "$trace_cfg" \
      -config "$overlay" $extra -trace "$trace") >"$out/$arm/run.log" 2>&1
}
run_arm omitted
run_arm explicit-off '-gpgpu_l2_char_returnq_hold_cycles 0'

python3 - "$out/omitted/run.log" "$out/explicit-off/run.log" <<'PY'
import re, sys
def normal_stats(path):
    text = open(path).read()
    assert 'GPGPU-Sim: *** exit detected ***' in text
    # Drop option echo/header noise and all closeout-only L2_char telemetry.
    # Remaining key/value statistics must be exactly equal for default-off and
    # explicitly-off runs of the same executable/configuration.
    start = text.find('gpu_tot_sim_cycle')
    assert start >= 0
    rows = []
    for line in text[start:].splitlines():
        if line.startswith('L2_char_'):
            continue
        if re.match(r'^[A-Za-z0-9_\[\]:.-]+\s*=', line):
            rows.append(line)
    return rows
a, b = map(normal_stats, sys.argv[1:])
assert a == b, 'normal statistics differ with hook omitted vs explicit off'
print('HOOK-OFF PASS cycles/statistics identical (%d normal-stat rows)' % len(a))
PY
