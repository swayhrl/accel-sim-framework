#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/check_l2_frc_forward_progress.sh --config CONFIG
       [--trace-config FILE] [--run-root DIR]

Runs a dirty-victim trace with four-entry partition FIFOs and one conventional
L2 MSHR.  The FRC-off control and FRC1 must both drain; FRC additionally must
retire its dirty swap and leave no live FRC entry.
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
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/l2-frc-progress.XXXXXX")"
else
  mkdir -p "$run_root"
  run_root="$(cd "$run_root" && pwd)"
fi

common=(--trace "$repo_root/tests/l2_frc/dirty_swap/kernelslist.g" --config "$config")
[[ -n "$trace_config" ]] && common+=(--trace-config "$trace_config")
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --config-extra "$repo_root/configs/l2_frc/baseline-constrained.config" \
  --run-dir "$run_root/control"
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --config-extra "$repo_root/configs/l2_frc/frc1-constrained.config" \
  --run-dir "$run_root/frc1"

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
frc_log="$run_root/frc1/smoke.out"
for key in wb_enqueued wb_lower_accepted wb_bytes wb_sectors; do
  [[ "$(field "$control_log" "$key")" == "$(field "$frc_log" "$key")" ]]
done
grep -Eq 'frc_l2 .*allocations=2 .*lower_reads=2 .*swaps=2 .*dirty_swaps=1 .*wb_lower_accepted=1 .*fetching=0 fetched=0 evicting=0' \
  "$frc_log"

control_cycles="$(awk '/^gpu_tot_sim_cycle =/{value=$3} END {print value}' "$control_log")"
frc_cycles="$(awk '/^gpu_tot_sim_cycle =/{value=$3} END {print value}' "$frc_log")"
printf 'PASS frc_forward_progress control_cycles=%s frc1_cycles=%s wb_bytes=%s run_root=%s\n' \
  "$control_cycles" "$frc_cycles" "$(field "$frc_log" wb_bytes)" "$run_root"
