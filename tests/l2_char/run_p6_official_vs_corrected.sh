#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
corrected_core=${GPGPUSIM_ROOT:-/workspace/worktrees/gpgpu-sim-l2-char}
official_core=${GPGPUSIM_OFFICIAL_ROOT:-/workspace/worktrees/gpgpu-sim-l2-official-smoke}
official_framework=${ACCELSIM_OFFICIAL_ROOT:-/workspace/worktrees/accel-sim-l2-official-smoke}
trace_root=${L2_CHAR_TRACE_ROOT:-/workspace/worktrees/accel-sim-latebind-oracle-v1/tests/l2_latebind}
out=${1:-"$root/tests/l2_char/results/closeout-p6"}
trace=$trace_root/pressure/kernelslist.g
overlay=$root/tests/l2_char/p6_pressure.config

mkdir -p "$out/official" "$out/corrected"

run_arm() {
  local arm=$1 sim=$2 core=$3 framework=$4
  local dir=$out/$arm
  (
    set +u
    source "$core/setup_environment" >/dev/null
    source "$framework/gpu-simulator/setup_environment.sh" >/dev/null
    set -u
    cd "$dir"
    "$sim" -config "$core/configs/tested-cfgs/SM7_QV100/gpgpusim.config" \
      -config "$framework/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config" \
      -config "$overlay" -trace "$trace"
  ) >"$dir/run.log" 2>&1
}

run_arm official "$official_framework/gpu-simulator/bin/release/accel-sim.out" \
  "$official_core" "$official_framework"
run_arm corrected "$root/gpu-simulator/bin/release/accel-sim.out" \
  "$corrected_core" "$root"

sha256sum "$trace" "$overlay" \
  "$official_framework/gpu-simulator/bin/release/accel-sim.out" \
  "$root/gpu-simulator/bin/release/accel-sim.out" >"$out/hashes.sha256"
git -C "$official_core" rev-parse HEAD >"$out/official_core.sha"
git -C "$corrected_core" rev-parse HEAD >"$out/corrected_core.sha"
git -C "$official_framework" rev-parse HEAD >"$out/official_framework.sha"
git -C "$root" rev-parse HEAD >"$out/corrected_framework.sha"

python3 - "$out" <<'PY'
import re, sys
from pathlib import Path
out = Path(sys.argv[1])
def values(text, key):
    return [int(x) for x in re.findall(r'^' + re.escape(key) +
                                       r'\s*=\s*(\d+)\s*$', text, re.M)]
def final(text, key):
    vals = values(text, key)
    if not vals: raise AssertionError('missing ' + key)
    return vals[-1]
logs = {a: (out/a/'run.log').read_text() for a in ('official','corrected')}
for arm, text in logs.items():
    assert 'GPGPU-Sim: *** exit detected ***' in text, arm + ' did not finish'
insn = {a: final(t, 'gpu_tot_sim_insn') for a,t in logs.items()}
cycles = {a: final(t, 'gpu_tot_sim_cycle') for a,t in logs.items()}
reqs = {a: final(t, 'icnt_total_pkts_simt_to_mem') for a,t in logs.items()}
assert insn['official'] == insn['corrected']
assert reqs['official'] == reqs['corrected']
ct = logs['corrected']
parts = values(ct, 'Total number of memory sub partition')
npart = parts[-1] if parts else 1
def corrected_final(key):
    vals = values(ct, key)
    assert len(vals) >= npart, 'missing ' + key
    return vals[-npart:]
activation = sum(corrected_final('L2_char_corrected_path_activation_count'))
assert activation > 0
assert all(v == 0 for v in corrected_final('L2_char_preview_commit_mismatch'))
assert all(v == 1 for v in corrected_final('L2_char_resource_leak_free'))
assert all(v == 1 for v in corrected_final('L2_char_credit_leak_free'))
(out/'summary.tsv').write_text(
    'arm\tinsn\trequests\tcycles\tactivation\n' +
    f"official\t{insn['official']}\t{reqs['official']}\t{cycles['official']}\t0\n" +
    f"corrected\t{insn['corrected']}\t{reqs['corrected']}\t{cycles['corrected']}\t{activation}\n")
print('P6 PASS insn=%d requests=%d official_cycles=%d corrected_cycles=%d activation=%d' %
      (insn['official'], reqs['official'], cycles['official'],
       cycles['corrected'], activation))
PY
