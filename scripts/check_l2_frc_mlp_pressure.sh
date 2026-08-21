#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/check_l2_frc_mlp_pressure.sh --config CONFIG
       [--trace-config FILE] [--run-root DIR]

Runs the deterministic two-read, one-way-L2 pressure trace with observation
enabled.  The conventional control may have only one lower read in flight;
FRC4 must issue both independent reads before either one returns.
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
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/l2-frc-mlp.XXXXXX")"
else
  mkdir -p "$run_root"
  run_root="$(cd "$run_root" && pwd)"
fi

common=(--trace "$repo_root/tests/l2_frc/replacement_pressure/kernelslist.g" --config "$config")
[[ -n "$trace_config" ]] && common+=(--trace-config "$trace_config")
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --config-extra "$repo_root/configs/l2_frc/baseline-pressure-observe.config" \
  --run-dir "$run_root/control"
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --config-extra "$repo_root/configs/l2_frc/frc4-pressure-observe.config" \
  --run-dir "$run_root/frc4"

field() {
  local log="$1"
  local key="$2"
  awk -v key="$key" '
    /^latebind_l2_global / {
      for (i = 1; i <= NF; ++i) {
        split($i, pair, "=")
        if (pair[1] == key) value = pair[2]
      }
    }
    END { if (value == "") exit 1; print value }
  ' "$log"
}

control_log="$run_root/control/smoke.out"
frc_log="$run_root/frc4/smoke.out"
control_peak="$(field "$control_log" lower_read_inflight_peak)"
frc_peak="$(field "$frc_log" lower_read_inflight_peak)"
control_cycles="$(awk '/^gpu_tot_sim_cycle =/{value=$3} END {print value}' "$control_log")"
frc_cycles="$(awk '/^gpu_tot_sim_cycle =/{value=$3} END {print value}' "$frc_log")"
frc_allocations="$(awk '/^frc_l2 / { for (i = 1; i <= NF; ++i) { split($i, pair, "="); if (pair[1] == "allocations") sum += pair[2] } } END { print sum + 0 }' "$frc_log")"
frc_live="$(awk '/^frc_l2 / { for (i = 1; i <= NF; ++i) { split($i, pair, "="); if (pair[1] == "fetching" || pair[1] == "fetched" || pair[1] == "evicting") sum += pair[2] } } END { print sum + 0 }' "$frc_log")"

[[ "$control_peak" -eq 1 ]]
[[ "$frc_peak" -ge 2 ]]
[[ "$frc_allocations" -ge 2 ]]
[[ "$frc_live" -eq 0 ]]
[[ "$frc_cycles" -lt "$control_cycles" ]]
printf 'PASS frc_mlp_pressure control_cycles=%s frc4_cycles=%s control_peak=%s frc_peak=%s frc_allocations=%s run_root=%s\n' \
  "$control_cycles" "$frc_cycles" "$control_peak" "$frc_peak" "$frc_allocations" "$run_root"
