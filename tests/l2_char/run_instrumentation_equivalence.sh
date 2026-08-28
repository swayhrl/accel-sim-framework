#!/usr/bin/env bash
# Small C1/C2 timing-neutrality check.  This is deliberately a fixed directed
# trace, not a Round-1 characterization workload launch.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core=${GPGPUSIM_ROOT:?source the fixed characterization core environment first}
frozen_root=${L2_CHAR_FROZEN_FRAMEWORK_ROOT:-/workspace/worktrees/accel-sim-l2-char}
frozen_core=${L2_CHAR_FROZEN_CORE_ROOT:-/workspace/worktrees/gpgpu-sim-l2-char}
out=${1:-"$root/tests/l2_char/results/fixed-equivalence"}
sim="$root/gpu-simulator/bin/release/accel-sim.out"
frozen_sim="$frozen_root/gpu-simulator/bin/release/accel-sim.out"
base="$core/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
frozen_base="$frozen_core/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
trace_cfg="$root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
frozen_trace_cfg="$frozen_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
trace="$root/tests/l2_char/traces/writeback/kernelslist.g"
char_cfg="$root/tests/l2_char/char_enabled.config"

[[ -x $sim && -x $frozen_sim && -f $base && -f $frozen_base && -f $trace_cfg && -f $frozen_trace_cfg && -f $trace ]] || {
  echo "missing simulator/config/trace for instrumentation equivalence" >&2
  exit 2
}
mkdir -p "$out"

run_current() {
  local name=$1; shift
  mkdir -p "$out/$name"
  (cd "$out/$name" && /usr/bin/time -f 'wall_sec=%e\nmax_rss_kib=%M' \
      -o host_profile.txt "$@") >"$out/$name/run.log" 2>&1
  grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$out/$name/run.log"
}

run_frozen() {
  local dir="$out/frozen"
  mkdir -p "$dir"
  (
    set +u
    unset GPGPUSIM_SETUP_ENVIRONMENT_WAS_RUN
    export GPGPUSIM_ROOT="$frozen_core"
    source "$frozen_core/setup_environment" release >/dev/null
    source "$frozen_root/gpu-simulator/setup_environment.sh" release >/dev/null
    set -u
    cd "$dir"
    /usr/bin/time -f 'wall_sec=%e\nmax_rss_kib=%M' -o host_profile.txt \
      "$frozen_sim" -config "$frozen_base" -config "$frozen_trace_cfg" -trace "$trace"
  ) >"$dir/run.log" 2>&1
  grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$dir/run.log"
}

# Frozen C1 arm and fixed char-off arm use no characterization overlay.
run_frozen
run_current char_off "$sim" -config "$base" -config "$trace_cfg" -trace "$trace"
run_current char_on "$sim" -config "$base" -config "$trace_cfg" -config "$char_cfg" -trace "$trace"

python3 - "$out/frozen/run.log" "$out/char_off/run.log" "$out/char_on/run.log" <<'PY'
import re
import sys

frozen, off, on = sys.argv[1:]

def final_scalars(path):
    values = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        match = re.match(r'^(gpu_tot_sim_(?:cycle|insn)|L2_char_[A-Za-z0-9_]+)\s*=\s*(\S+)', line)
        if match:
            values[match.group(1)] = match.group(2)
    return values

def native_output(path):
    result = []
    for line in open(path, encoding='utf-8', errors='replace'):
        if line.startswith('L2CHARV1|'):
            continue
        if (line.startswith('GPGPU-Sim version') or
                'GPGPU-Sim Simulator Version' in line or
                'accelsim-commit-' in line):
            continue
        if line.startswith('-gpgpu_l2_char_'):
            continue
        if (line.startswith('gpgpu_simulation_time') or
                line.startswith('gpgpu_simulation_rate') or
                line.startswith('gpgpu_silicon_slowdown') or
                line.startswith('gpu_total_sim_rate')):
            # Host-time reporting is expected to differ when instrumentation
            # is enabled and is not simulated/native model state.
            continue
        result.append(line)
    return result

frozen_stats, off_stats, on_stats = map(final_scalars, (frozen, off, on))
for name, reference, candidate in (('C1 frozen_vs_char_off', frozen_stats, off_stats),
                                   ('C2 char_off_vs_char_on', off_stats, on_stats)):
    if reference != candidate:
        missing = sorted(set(reference) ^ set(candidate))
        changed = sorted(key for key in set(reference) & set(candidate)
                         if reference[key] != candidate[key])
        raise SystemExit('%s scalar mismatch: missing=%s changed=%s' %
                         (name, missing, changed))
if native_output(off) != native_output(on):
    raise SystemExit('C2 native production output differs after removing L2CHAR records/config echo')
if native_output(frozen) != native_output(off):
    raise SystemExit('C1 native production output differs between frozen and fixed char-off')
print('C1 PASS: frozen corrected vs fixed char-off scalar statistics identical')
print('C2 PASS: fixed char-off vs char-on scalar/native output identical')
PY
