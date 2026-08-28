#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
CORE_ROOT=${GPGPUSIM_ROOT:-/workspace/worktrees/gpgpu-sim-l2-char}
TRACE_ROOT=${L2_CHAR_TRACE_ROOT:-/workspace/worktrees/accel-sim-latebind-oracle-v1/tests/l2_latebind}
OUT=${L2_CHAR_PRESSURE_OUT:-}

if [[ ${1:-} == --out && -n ${2:-} ]]; then
  OUT=$2
  shift 2
fi
[[ $# -eq 0 ]] || { echo "usage: $0 [--out DIR]" >&2; exit 2; }
[[ -n $OUT ]] || { echo "--out is required" >&2; exit 2; }

SIM=$ROOT/gpu-simulator/bin/release/accel-sim.out
BASE_CFG=$CORE_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config
TRACE_CFG=$ROOT/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config
[[ -x $SIM && -f $BASE_CFG && -f $TRACE_CFG ]] || {
  echo "missing corrected frontend or QV100 configuration" >&2; exit 2;
}
# The merge fixture is deliberately sourced from the FRC directed test tree.
FRC_TRACE_ROOT=${L2_CHAR_FRC_TRACE_ROOT:-/workspace/worktrees/accel-sim-frc-v1/tests/l2_frc}
[[ -f $TRACE_ROOT/pressure/kernelslist.g && -f $TRACE_ROOT/writeback/kernelslist.g && -f $FRC_TRACE_ROOT/merge/kernelslist.g ]] || {
  echo "missing directed pressure fixtures" >&2; exit 2;
}

mkdir -p "$OUT"
rm -f "$OUT/summary.tsv"
printf 'case\tresult\tcycles\tinsn\tactivation\tlowerq\trespq\tdataport\twb_progress\n' > "$OUT/summary.tsv"

run_case() {
  local name=$1 trace=$2 overlay=$3 expected=$4
  local dir=$OUT/$name
  mkdir -p "$dir"
  cp "$overlay" "$dir/overlay.config"
  sha256sum "$trace" > "$dir/trace.sha256"
  set +e
  (cd "$dir" && "$SIM" -config "$BASE_CFG" -config "$TRACE_CFG" \
      -config "$dir/overlay.config" -trace "$trace") > "$dir/run.log" 2>&1
  local rc=$?
  set -e
  [[ $rc -eq 0 ]] || { echo "$name: simulator failed ($rc)" >&2; return 1; }
  grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$dir/run.log" || {
    echo "$name: no normal completion" >&2; return 1;
  }
  python3 - "$name" "$dir/run.log" "$expected" "$OUT/summary.tsv" <<'PY'
import re, sys
name, log, expected, summary = sys.argv[1:]
text = open(log).read()
def vals(key):
    return [int(x) for x in re.findall(r'^' + re.escape(key) + r'\s*=\s*(\d+)\s*$', text, re.M)]
partitions = re.findall(r'^Total number of memory sub partition = (\d+)\s*$', text, re.M)
partitions = int(partitions[-1]) if partitions else 1
# The framework emits a per-kernel snapshot and a terminal snapshot after
# backend drain.  Integrity and pressure metrics intentionally use the latter.
def final_vals(key):
    values = vals(key)
    return values[-partitions:]
def total(key): return sum(final_vals(key))
def one(key):
    m = final_vals(key)
    return int(m[-1]) if m else 0
for key in ('L2_char_preview_commit_mismatch', 'L2_char_resource_leak_free',
            'L2_char_credit_leak_free'):
    got = final_vals(key)
    if not got:
        raise SystemExit(f'{name}: missing {key}')
    if key.endswith('mismatch') and any(got):
        raise SystemExit(f'{name}: {key}={got}')
    if key.endswith('free') and any(v != 1 for v in got):
        raise SystemExit(f'{name}: {key}={got}')
for reason in ('line_alloc','mshr_new','mshr_merge','missq','data_port','respq','other'):
    c = total('L2_char_block_cycles_' + reason)
    r = total('L2_char_block_requests_' + reason)
    e = total('L2_char_block_episodes_' + reason)
    if not (c >= e >= r):
        raise SystemExit(f'{name}: blocker sanity {reason}: cycles={c}, episodes={e}, requests={r}')
metrics = {
  'activation': total('L2_char_corrected_path_activation_count'),
  'lowerq': total('L2_char_corrected_path_lowerq_activation_count'),
  'respq': total('L2_char_corrected_path_respq_activation_count'),
  'dataport': total('L2_char_corrected_path_dataport_activation_count'),
  'wb_progress': total('L2_char_wb_progress_credit_use_count'),
  'missq_block': total('L2_char_block_cycles_missq'),
  'mshr_block': total('L2_char_block_cycles_mshr_new') + total('L2_char_block_cycles_mshr_merge'),
  'dataport_busy': total('L2_char_data_port_busy_cycles'),
  # P4 fixes each capacity to one; a maximum of one therefore proves the
  # production queue reached its exact configured boundary without overflow.
  'mshr_capacity': max(final_vals('L2_char_mshr_entries_max'), default=0),
  'missq_capacity': max(final_vals('L2_char_missq_max'), default=0),
}
for need in expected.split(','):
    if need and metrics.get(need, 0) == 0:
        raise SystemExit(f'{name}: required nonzero signature absent: {need}')
cycles = one('gpu_tot_sim_cycle')
insn = one('gpu_tot_sim_insn')
with open(summary, 'a') as f:
    f.write(f"{name}\tPASS\t{cycles}\t{insn}\t{metrics['activation']}\t{metrics['lowerq']}\t{metrics['respq']}\t{metrics['dataport']}\t{metrics['wb_progress']}\n")
PY
}

write_overlay() {
  local path=$1; shift
  printf '%s\n' "$@" > "$path"
}

# P1: lower-request FIFO full must not prevent a request that does not need a
# lower request from entering the real controller.
write_overlay "$OUT/p1.config" \
  '-gpgpu_n_mem 16' \
  '-gpgpu_n_sub_partition_per_mchannel 1' \
  '-gpgpu_dram_partition_queues 64:1:1:64' \
  '-gpgpu_frfcfs_dram_sched_queue_size 1' \
  '-gpgpu_dram_return_queue_size 1' \
  '-gpgpu_cache:dl2 S:32:128:1,L:B:m:L:P,A:8:4,4:0,1'
run_case P1_lowerq "$TRACE_ROOT/pressure/kernelslist.g" "$OUT/p1.config" lowerq

# P2: a full immediate-response queue must not block clean misses or MSHR
# merges, which do not need that queue at admission.
write_overlay "$OUT/p2.config" \
  '-gpgpu_n_mem 16' \
  '-gpgpu_n_sub_partition_per_mchannel 1' \
  '-gpgpu_dram_partition_queues 64:8:64:1' \
  '-gpgpu_cache:dl2 S:32:128:1,L:B:m:L:P,A:8:4,4:0,1'
run_case P2_respq "$TRACE_ROOT/pressure/kernelslist.g" "$OUT/p2.config" respq

# P3: fill/data-port occupancy is real for hits, but clean misses and merges
# may still enter when their plan has no data-port requirement.
write_overlay "$OUT/p3.config" \
  '-gpgpu_n_mem 16' \
  '-gpgpu_n_sub_partition_per_mchannel 1' \
  '-gpgpu_dram_partition_queues 64:8:1:64' \
  '-gpgpu_cache:dl2 S:32:128:1,L:B:m:L:P,A:8:4,4:0,1'
run_case P3_dataport "$TRACE_ROOT/writeback/kernelslist.g" "$OUT/p3.config" dataport_busy

# P4/P5/P6 each have a dedicated deterministic closeout harness.  They are
# intentionally not folded into this legacy trace batch: P4 checks dirty
# one-slot non-mutation, P5 controls a real ReturnQ/FIFO relation, and P6
# compares Official against Corrected on the same pressure trace.
echo "corrected L2 legacy pressure regressions: PASS (P1-P3)"
