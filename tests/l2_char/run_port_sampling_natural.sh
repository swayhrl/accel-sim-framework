#!/usr/bin/env bash
# Two bounded natural-workload checks for Instrumentation v1 closeout.  This
# is not a Round-1 sweep and intentionally runs only the named validation arms.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.. && pwd)
core=${GPGPUSIM_ROOT:?source the fixed characterization core environment first}
out=${1:-"$root/tests/l2_char/results/fixed-natural"}
sim="$root/gpu-simulator/bin/release/accel-sim.out"
base="$core/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
trace_cfg="$root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
overlay="$root/tests/l2_char/qv100_round1_observation.config"
data_trace=${L2_CHAR_NATURAL_DATA_TRACE:-/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/cudasdk/9.1/fastWalshTransform/_logK_11__logD_19/traces/kernelslist.g}
fill_trace=${L2_CHAR_NATURAL_FILL_TRACE:-/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-spmv/_i___data_large_input_Dubcova3_mtx_bin___data_large_input_vector_bin__o_Dubcova3_mtx_out/traces/kernelslist.g}

[[ -x $sim && -f $base && -f $trace_cfg && -f $overlay && -f $data_trace && -f $fill_trace ]] || {
  echo "missing fixed simulator, configuration, or natural-workload trace" >&2
  exit 2
}
mkdir -p "$out"
core_commit=$(git -C "$core" rev-parse HEAD)
framework_commit=$(git -C "$root" rev-parse HEAD)

run_case() {
  local name=$1 workload=$2 input=$3 expected_port=$4 trace=$5
  local dir="$out/$name"
  mkdir -p "$dir"
  (
    cd "$dir"
    /usr/bin/time -f 'wall_sec=%e\nmax_rss_kib=%M' -o host_profile.txt \
      "$sim" -config "$base" -config "$trace_cfg" -config "$overlay" -trace "$trace"
  ) >"$dir/raw.log" 2>&1
  grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$dir/raw.log"
  python3 "$root/util/l2_char/parse_l2_char.py" "$dir/raw.log" --out "$dir" \
    --production --workload "$workload" --input "$input" --kernel ALL --kernel-id all \
    --config "$base" --trace "$trace" --framework-repo "$root" --core-repo "$core" \
    --framework-commit "$framework_commit" --core-commit "$core_commit" \
    --framework-branch "$(git -C "$root" branch --show-current)" \
    --core-branch "$(git -C "$core" branch --show-current)" \
    --command "fixed-instrumentation-closeout:$name" \
    --window-l2-cycles 5000 --set-detail 1 --emit-windows 1
  python3 - "$dir" "$expected_port" <<'PY'
import csv
import pathlib
import sys

directory, expected = pathlib.Path(sys.argv[1]), sys.argv[2]
slices = list(csv.DictReader((directory / 'slice.csv').open()))
summary = next(csv.DictReader((directory / 'summary.csv').open()))
assert len(slices) == 64
for row in slices:
    for char, native in (('char_data_busy_cycles', 'native_data_busy_cycles'),
                         ('char_fill_busy_cycles', 'native_fill_busy_cycles'),
                         ('char_port_samples', 'native_port_samples')):
        assert row[char] == row[native], (row['slice'], char, row[char], row[native])
assert int(summary['invariants_pass']) == 1
assert int(summary['%s_busy_cycles' % expected]) > 0
for metric in ('mshr_target', 'icntl2q', 'l2dramq', 'draml2q', 'l2icntq', 'rop'):
    for suffix in ('global_avg', 'global_p50', 'global_p95', 'global_max'):
        assert metric + '_' + suffix in summary, metric + '_' + suffix
print('%s natural port crosscheck PASS' % expected)
PY
}

run_case fastWalshTransform_11_19 fastWalshTransform logK_11_logD_19 char_data "$data_trace"
run_case parboil_spmv_Dubcova3_large spmv Dubcova3_large char_fill "$fill_trace"
printf 'Natural port closeout PASS\n'
