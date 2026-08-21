#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/check_latebind_l2_phase1.sh --trace KERNELSLIST --config CONFIG
       [--trace-config FILE] [--run-root DIR]

Runs the frozen-baseline characterization build with statistics off and on.
The architectural metric stream must match; the stats-on run must emit a
nonempty LateBind L2 aggregate.  Set LATEBIND_L2_GPGPUSIM_ROOT first.
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
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/latebind-l2-phase1.XXXXXX")"
else
  mkdir -p "$run_root"
  run_root="$(cd "$run_root" && pwd)"
fi

printf '%s\n' '-gpgpu_l2_latebind_stats 0' > "$run_root/stats-off.config"
printf '%s\n' '-gpgpu_l2_latebind_stats 1' > "$run_root/stats-on.config"

common=(--trace "$trace" --config "$config")
if [[ -n "$trace_config" ]]; then
  common+=(--trace-config "$trace_config")
fi
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --run-dir "$run_root/stats-off" --config-extra "$run_root/stats-off.config"
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${common[@]}" \
  --run-dir "$run_root/stats-on" --config-extra "$run_root/stats-on.config"

metric_re='gpu_tot_sim_(cycle|insn) =|L2_total_cache_(accesses|misses|pending_hits|reservation_fails) ='
rg "$metric_re" "$run_root/stats-off/smoke.out" > "$run_root/off.metrics"
rg "$metric_re" "$run_root/stats-on/smoke.out" > "$run_root/on.metrics"
diff -u "$run_root/off.metrics" "$run_root/on.metrics"
rg -q 'latebind_l2_global .*probes_miss=[1-9]' "$run_root/stats-on/smoke.out"

printf 'PASS phase1_equivalence run_root=%s\n' "$run_root"
cat "$run_root/on.metrics"
rg 'latebind_l2_global' "$run_root/stats-on/smoke.out"
