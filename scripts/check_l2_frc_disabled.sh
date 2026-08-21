#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/check_l2_frc_disabled.sh --trace KERNELSLIST --config CONFIG
       [--trace-config FILE] [--run-root DIR]

Confirms that the explicit Phase-3 disabled configuration has the same
architectural metric stream as the corrected conventional control.  Set
LATEBIND_L2_GPGPUSIM_ROOT to the FRC core worktree first.
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
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/l2-frc-disabled.XXXXXX")"
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
  --run-dir "$run_root/frc-disabled" \
  --config-extra "$repo_root/configs/l2_frc/disabled.config"

metric_re='gpu_tot_sim_(cycle|insn) =|L2_total_cache_(accesses|misses|pending_hits|reservation_fails) ='
rg "$metric_re" "$run_root/control/smoke.out" > "$run_root/control.metrics"
rg "$metric_re" "$run_root/frc-disabled/smoke.out" > "$run_root/frc-disabled.metrics"
diff -u "$run_root/control.metrics" "$run_root/frc-disabled.metrics"
printf 'PASS frc_disabled_equivalence run_root=%s\n' "$run_root"
cat "$run_root/frc-disabled.metrics"
