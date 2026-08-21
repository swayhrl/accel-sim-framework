#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/check_l2_frc_replacement_pressure.sh --config CONFIG
       [--trace-config FILE] [--run-root DIR]

Runs a deterministic two-read, one-way-L2 pressure trace.  Both requests map
to one L2 slice/set.  The control must report reservation failures; FRC4 must
accept both reads and finish sooner.
EOF
}

config=""
trace_config=""
run_root=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) config="$2"; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --run-root) run_root="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -f "$config" ]] || { usage >&2; exit 2; }
[[ -z "$trace_config" || -f "$trace_config" ]] || { usage >&2; exit 2; }

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$run_root" ]]; then
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/l2-frc-pressure.XXXXXX")"
else
  mkdir -p "$run_root"
  run_root="$(cd "$run_root" && pwd)"
fi

common=(--trace "$repo_root/tests/l2_frc/replacement_pressure/kernelslist.g" --config "$config")
[[ -n "$trace_config" ]] && common+=(--trace-config "$trace_config")
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --config-extra "$repo_root/configs/l2_frc/baseline-pressure.config" \
  --run-dir "$run_root/control"
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --config-extra "$repo_root/configs/l2_frc/frc4-pressure.config" \
  --run-dir "$run_root/frc4"

control_log="$run_root/control/smoke.out"
frc_log="$run_root/frc4/smoke.out"
control_cycles="$(awk '/^gpu_tot_sim_cycle =/{print $3; exit}' "$control_log")"
frc_cycles="$(awk '/^gpu_tot_sim_cycle =/{print $3; exit}' "$frc_log")"
control_fails="$(awk '/^L2_total_cache_reservation_fails =/{print $3; exit}' "$control_log")"
frc_allocations="$(awk '/^frc_l2 / { for (i = 1; i <= NF; ++i) { split($i, pair, "="); if (pair[1] == "allocations") sum += pair[2] } } END { print sum + 0 }' "$frc_log")"

[[ "$control_fails" -gt 0 ]]
[[ "$frc_allocations" -ge 2 ]]
[[ "$frc_cycles" -lt "$control_cycles" ]]
printf 'PASS frc_replacement_pressure control_cycles=%s frc4_cycles=%s control_reservation_fails=%s frc_allocations=%s run_root=%s\n' \
  "$control_cycles" "$frc_cycles" "$control_fails" "$frc_allocations" "$run_root"
