#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_l2_frc_core_sweep.sh --trace KERNELSLIST --config CONFIG
       [--trace-config FILE] [--run-root DIR] [--variants CSV]

Runs the Phase-3 paper-mode FRC sensitivity points (4/8/16/32/64 entries),
the capacity-fair 128/256-sector points, and the paper-relative 2x/4x
conventional capacity controls.  The baseline has 24 ways per L2
subpartition; frc128 and frc256 respectively add the payload of one and two
such ways, so they are compared with baseline25 and baseline26.  Baseline48
and baseline96 preserve the paper's 2x/4x capacity ratios instead.
EOF
}

trace=""
config=""
trace_config=""
run_root=""
variants_csv=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace) trace="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --run-root) run_root="$2"; shift 2 ;;
    --variants) variants_csv="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -f "$trace" && -f "$config" ]] || { usage >&2; exit 2; }
[[ -z "$trace_config" || -f "$trace_config" ]] || { usage >&2; exit 2; }

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$run_root" ]]; then
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/l2-frc-core.XXXXXX")"
else
  mkdir -p "$run_root"
  run_root="$(cd "$run_root" && pwd)"
fi

default_variants=(baseline24 frc4-paper frc8-paper frc16-paper frc32-paper frc64-paper frc128-paper baseline25 frc256-paper baseline26 baseline48-paper_capacity baseline96-paper_capacity)
if [[ -n "$variants_csv" ]]; then
  IFS=',' read -r -a variants <<< "$variants_csv"
else
  variants=("${default_variants[@]}")
fi
for variant in "${variants[@]}"; do
  [[ -f "$repo_root/configs/l2_frc/$variant.config" ]] || {
    echo "error: unknown FRC variant $variant" >&2
    exit 2
  }
done
for variant in "${variants[@]}"; do
  args=(--trace "$trace" --config "$config" --config-extra "$repo_root/configs/l2_frc/$variant.config" --run-dir "$run_root/$variant")
  [[ -n "$trace_config" ]] && args+=(--trace-config "$trace_config")
  "$repo_root/scripts/run_latebind_l2_smoke.sh" "${args[@]}"
done

variant_list="$(IFS=,; echo "${variants[*]}")"
"$repo_root/scripts/collect_l2_frc_core_metrics.sh" --run-root "$run_root" --variants "$variant_list"
printf 'PASS frc_core_sweep run_root=%s\n' "$run_root"
