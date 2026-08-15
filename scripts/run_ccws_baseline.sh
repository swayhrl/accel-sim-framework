#!/usr/bin/env bash
# Run the locally available CCWS-paper workloads with the unmodified L2
# backend.  This is a current-Accel-Sim baseline, not a bit-for-bit rerun of
# the MICRO-45 setup (which used GPGPU-Sim 3.1 and different hardware knobs).
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_ccws_baseline.sh [--scheduler lrr|gto|all]
       [--run-root DIR] [--reuse]

Runs the eight CCWS workloads for which the local Rodinia trace archive has a
kernelslist.g.  Results are appended atomically to summary.csv.  The four
paper workloads without a local trace (MEMC, GC, SSSP, WP) are recorded in
unavailable.csv rather than silently substituted.
EOF
}

scheduler=all
run_root=""
reuse=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scheduler) scheduler="$2"; shift 2 ;;
    --run-root) run_root="$2"; shift 2 ;;
    --reuse) reuse=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
case "$scheduler" in lrr|gto|all) ;; *)
  echo "error: --scheduler must be lrr, gto, or all" >&2; exit 2 ;;
esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
gpgpu_root="${DECOUPLED_L2_GPGPUSIM_ROOT:-}"
[[ -n "$gpgpu_root" ]] || {
  echo "error: set DECOUPLED_L2_GPGPUSIM_ROOT to the matching source tree" >&2
  exit 2
}
trace_root="$repo_root/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1"
config="$gpgpu_root/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
[[ -f "$config" && -f "$trace_config" ]] || { echo "error: missing config" >&2; exit 2; }

if [[ -z "$run_root" ]]; then
  run_root="$repo_root/hw_run/ccws-baseline-$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$run_root"
run_root="$(cd "$run_root" && pwd)"

source_commit="$(git -C "$gpgpu_root" rev-parse HEAD)"
{
  printf 'paper=Rogers_OConnor_Aamodt_MICRO45_CCWS\n'
  printf 'paper_url=https://people.ece.ubc.ca/aamodt/publications/papers/tgrogers.micro2012.pdf\n'
  printf 'scope=current_accel_sim_baseline_not_a_bit_exact_GPGPU_Sim_3_1_reproduction\n'
  printf 'gpgpusim_source_commit=%s\n' "$source_commit"
  printf 'base_config=%s\ntrace_config=%s\n' "$config" "$trace_config"
} > "$run_root/provenance.txt"

printf '%s\n' \
  'ccws_name,group,reason' \
  'MEMC,HCS,no local replay trace available' \
  'GC,HCS,no local replay trace available' \
  'SSSP,MCS,no local replay trace available' \
  'WP,MCS,no local replay trace available' > "$run_root/unavailable.csv"

summary="$run_root/summary.csv"
if [[ ! -f "$summary" ]]; then
  printf '%s\n' 'scheduler,ccws_name,group,workload,input,rc,cycles,instructions,ipc,wall_seconds,run_dir' > "$summary"
fi

# Use the substantial archived inputs already used in the functional screen.
# The paper's exact input data are not part of this archive; every input stays
# in the result row so later plots cannot accidentally compare unlike traces.
declare -a cases=(
  'BFS|HCS|bfs-rodinia-3.1/__data_graph1MW_6_txt'
  'KMN|HCS|kmeans-rodinia-3.1/_o__i___data_819200_txt'
  'CFD|MCS|cfd-rodinia-3.1/__data_fvcorr_domn_193K'
  'STMCL|MCS|streamcluster-rodinia-3.1/10_20_256_65536_65536_1000_none_output_txt_1'
  'BACKP|CI|backprop-rodinia-3.1/65536'
  'LUD|CI|lud-rodinia-3.1/_i___data_512_dat'
  'NDL|CI|nw-rodinia-3.1/2048_10'
  'SRAD|CI|srad_v1-rodinia-3.1/100_0_5_502_458'
)

metric() {
  local key=$1 log=$2
  awk -F= -v k="$key" '$1 ~ "^" k "[[:space:]]*$" { v=$2 } END { gsub(/[[:space:]]/, "", v); print v }' "$log"
}

run_one() {
  local sched=$1 name=$2 group=$3 rel=$4 trace run extra start end rc cycles inst ipc
  trace="$trace_root/$rel/traces/kernelslist.g"
  [[ -f "$trace" ]] || { echo "error: missing trace $trace" >&2; return 2; }
  run="$run_root/$sched/$name"
  if [[ "$reuse" -eq 1 && -f "$run/result.csv" ]]; then
    if ! grep -Fqx -- "$(sed -n '1p' "$run/result.csv")" "$summary"; then
      sed -n '1p' "$run/result.csv" >> "$summary"
    fi
    echo "REUSE scheduler=$sched workload=$name"
    return 0
  fi
  mkdir -p "$run"
  extra="$run/scheduler.config"
  printf '%s\n' "-gpgpu_scheduler $sched" > "$extra"
  start=$(date +%s)
  echo "START scheduler=$sched workload=$name trace=$rel"
  set +e
  env MALLOC_ARENA_MAX=2 DECOUPLED_L2_GPGPUSIM_ROOT="$gpgpu_root" \
    "$repo_root/scripts/run_decoupled_l2_smoke.sh" --backend baseline \
      --trace "$trace" --config "$config" --trace-config "$trace_config" \
      --config-extra "$extra" --run-dir "$run" > "$run/launcher.out" 2>&1
  rc=$?
  set -e
  end=$(date +%s)
  cycles=""; inst=""; ipc=""
  if [[ -f "$run/smoke.out" ]]; then
    cycles=$(metric gpu_tot_sim_cycle "$run/smoke.out")
    inst=$(metric gpu_tot_sim_insn "$run/smoke.out")
    ipc=$(metric gpu_tot_ipc "$run/smoke.out")
  fi
  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
    "$sched" "$name" "$group" "${rel%%/*}" "${rel#*/}" "$rc" \
    "$cycles" "$inst" "$ipc" "$((end - start))" "$run" > "$run/result.csv"
  # A run-local result is written before the aggregate row, so an interrupted
  # aggregate update can be repaired deterministically with --reuse.
  cat "$run/result.csv" >> "$summary"
  echo "DONE scheduler=$sched workload=$name rc=$rc cycles=${cycles:-NA}"
  return "$rc"
}

declare -a schedulers=()
if [[ "$scheduler" == all ]]; then schedulers=(lrr gto); else schedulers=("$scheduler"); fi
failures=0
for sched in "${schedulers[@]}"; do
  for row in "${cases[@]}"; do
    IFS='|' read -r name group rel <<< "$row"
    run_one "$sched" "$name" "$group" "$rel" || failures=$((failures + 1))
  done
done

printf 'completed_at=%s\nfailures=%s\n' "$(date -Is)" "$failures" > "$run_root/status.txt"
exit "$(( failures != 0 ))"
