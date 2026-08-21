#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/check_l2_frc_observer_preservation.sh --trace KERNELSLIST
       --config CONFIG [--trace-config FILE] [--run-root DIR]

Runs the same current FRC core twice with FRC disabled: first without and then
with the observation-only latebind L2 statistics.  The architectural metric
streams must match exactly.  This isolates observer non-interference from the
separate cross-core conventional-control preservation check.
EOF
}

trace=""
config=""
trace_config=""
run_root=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace) trace="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --run-root) run_root="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$trace" && -f "$config" ]] || { usage >&2; exit 2; }
[[ -z "$trace_config" || -f "$trace_config" ]] || { usage >&2; exit 2; }

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$run_root" ]]; then
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/l2-frc-observer.XXXXXX")"
else
  mkdir -p "$run_root"
  run_root="$(cd "$run_root" && pwd)"
fi

# Both runs are the normal current core and explicitly disable FRC.  Keeping
# the generated observer override separate makes it impossible for a caller
# to accidentally compare different L2 capacity or FRC settings.
control_extra="$run_root/frc-off.config"
observer_extra="$run_root/frc-off-observe.config"
cat "$repo_root/configs/l2_frc/disabled.config" > "$control_extra"
{
  cat "$control_extra"
  printf '%s\n' '# Observation-only FRC-off preservation point.'
  printf '%s\n' '-gpgpu_l2_latebind_stats 1'
} > "$observer_extra"

common=(--trace "$trace" --config "$config")
[[ -n "$trace_config" ]] && common+=(--trace-config "$trace_config")
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --config-extra "$control_extra" --run-dir "$run_root/control"
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --config-extra "$observer_extra" --run-dir "$run_root/observer"

# Exclude observer-only lines, but retain every cumulative architectural,
# L2/MSHR, DRAM and writeback breakdown line printed by the simulator.
metric_re='^(gpu_tot_sim_(cycle|insn)|gpgpu_n_mem_(read|write)_(local|global|texture|const)|total dram (reads|writes)|L2_total_cache_(accesses|misses|miss_rate|pending_hits|reservation_fails)|[[:space:]]*(Total_core_cache_stats_breakdown|L2_cache_stats_breakdown|L2_total_cache_reservation_fail_breakdown)\[)'
rg "$metric_re" "$run_root/control/smoke.out" > "$run_root/control.metrics"
rg "$metric_re" "$run_root/observer/smoke.out" > "$run_root/observer.metrics"
diff -u "$run_root/control.metrics" "$run_root/observer.metrics"

rg -q '^latebind_l2_global ' "$run_root/observer/smoke.out"
printf 'PASS frc_observer_preservation run_root=%s\n' "$run_root"
cat "$run_root/observer.metrics"
