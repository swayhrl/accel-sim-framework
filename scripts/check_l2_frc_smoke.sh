#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/check_l2_frc_smoke.sh --trace KERNELSLIST --config CONFIG
       [--trace-config FILE] [--run-root DIR]

Runs the corrected conventional control and frc32-paper.  The selected trace
must exercise at least one FRC allocation and finish with no live FRC state.
Set LATEBIND_L2_GPGPUSIM_ROOT to the FRC core worktree first.
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
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/l2-frc-smoke.XXXXXX")"
else
  mkdir -p "$run_root"
  run_root="$(cd "$run_root" && pwd)"
fi

common=(--trace "$trace" --config "$config")
if [[ -n "$trace_config" ]]; then
  common+=(--trace-config "$trace_config")
fi
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --run-dir "$run_root/control"
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --run-dir "$run_root/frc" \
  --config-extra "$repo_root/configs/l2_frc/frc32-paper.config"

grep -Eq 'frc_l2 .*allocations=[1-9]' "$run_root/frc/smoke.out"
grep -Eq 'frc_l2 .*allocations=1 lower_reads=4' "$run_root/frc/smoke.out"
grep -Eq 'frc_l2 .*fetching=0 fetched=0 evicting=0' "$run_root/frc/smoke.out"
printf 'PASS frc_smoke run_root=%s\n' "$run_root"
grep 'frc_l2' "$run_root/frc/smoke.out"
