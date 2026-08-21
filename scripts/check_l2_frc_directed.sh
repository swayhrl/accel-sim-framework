#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/check_l2_frc_directed.sh --config CONFIG [--trace-config FILE]
       [--run-root DIR]

Runs the Phase-3 FRC directed tests: sector attachment while a complete line
is fetched, FRC-set-full fallback, dirty victim writeback ownership, explicit
partial-write fallback, and end-of-kernel flush.  Set
LATEBIND_L2_GPGPUSIM_ROOT to the selected FRC core worktree first.
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
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/l2-frc-directed.XXXXXX")"
else
  mkdir -p "$run_root"
  run_root="$(cd "$run_root" && pwd)"
fi

common=(--config "$config")
if [[ -n "$trace_config" ]]; then
  common+=(--trace-config "$trace_config")
fi

run_case() {
  local trace_name="$1"
  local run_name="$2"
  local extra="$3"
  "$repo_root/scripts/run_latebind_l2_smoke.sh" \
    --trace "$repo_root/tests/l2_frc/$trace_name/kernelslist.g" "${common[@]}" \
    --config-extra "$repo_root/configs/l2_frc/$extra" \
    --run-dir "$run_root/$run_name"
}

run_case merge merge frc1-directed.config
grep -Eq 'frc_l2 .*allocations=1 .*sector_attaches=[1-9]' \
  "$run_root/merge/smoke.out"

run_case set_full set_full frc1-directed.config
grep -Eq 'frc_l2 .*set_full_fallbacks=[1-9]' \
  "$run_root/set_full/smoke.out"

run_case write_conflict write_conflict frc1-directed.config
grep -Eq 'frc_l2 .*write_fallbacks=[1-9].*write_conflict_stalls=[1-9]' \
  "$run_root/write_conflict/smoke.out"

run_case dirty_swap dirty_swap frc1-directed.config
grep -Eq 'frc_l2 .*write_fallbacks=[1-9].*dirty_swaps=[1-9].*wb_lower_accepted=[1-9]' \
  "$run_root/dirty_swap/smoke.out"
grep -Eq 'frc_l2 .*fetching=0 fetched=0 evicting=0' \
  "$run_root/dirty_swap/smoke.out"

run_case dirty_swap flush frc1-directed-flush.config
grep -Eq 'frc_l2 .*flush_calls=[1-9].*fetching=0 fetched=0 evicting=0' \
  "$run_root/flush/smoke.out"

printf 'PASS frc_directed run_root=%s\n' "$run_root"
grep 'frc_l2' "$run_root/merge/smoke.out" "$run_root/set_full/smoke.out" \
  "$run_root/write_conflict/smoke.out" "$run_root/dirty_swap/smoke.out" \
  "$run_root/flush/smoke.out"
