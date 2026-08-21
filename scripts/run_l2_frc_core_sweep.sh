#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_l2_frc_core_sweep.sh --trace KERNELSLIST --config CONFIG
       [--trace-config FILE] [--run-root DIR]

Runs the Phase-3 paper-mode FRC sensitivity points (4/8/16/32/64 entries)
and the capacity-fair controls for 32- and 64-entry FRCs.  The baseline has
24 ways per L2 subpartition; frc32 and frc64 respectively add the payload of
one and two such ways, so they are compared with baseline25 and baseline26.
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
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/l2-frc-core.XXXXXX")"
else
  mkdir -p "$run_root"
  run_root="$(cd "$run_root" && pwd)"
fi

sum_frc_field() {
  local log="$1"
  local field="$2"
  awk -v field="$field" '
    /^frc_l2 / {
      for (i = 1; i <= NF; ++i) {
        split($i, pair, "=")
        if (pair[1] == field) sum += pair[2]
      }
    }
    END { print sum + 0 }
  ' "$log"
}

printf 'variant\tcycles\tinstructions\tl2_accesses\tl2_misses\tfrc_allocations\tfrc_lower_reads\tfrc_swaps\tfrc_set_full_fallbacks\tfrc_write_fallbacks\tfrc_atomic_fallbacks\n' \
  > "$run_root/summary.tsv"

variants=(baseline24 frc4-paper frc8-paper frc16-paper frc32-paper baseline25 frc64-paper baseline26)
for variant in "${variants[@]}"; do
  args=(--trace "$trace" --config "$config" --config-extra "$repo_root/configs/l2_frc/$variant.config" --run-dir "$run_root/$variant")
  [[ -n "$trace_config" ]] && args+=(--trace-config "$trace_config")
  "$repo_root/scripts/run_latebind_l2_smoke.sh" "${args[@]}"
  log="$run_root/$variant/smoke.out"
  cycles="$(awk '/^gpu_tot_sim_cycle =/{print $3; exit}' "$log")"
  instructions="$(awk '/^gpu_tot_sim_insn =/{print $3; exit}' "$log")"
  accesses="$(awk '/^L2_total_cache_accesses =/{print $3; exit}' "$log")"
  misses="$(awk '/^L2_total_cache_misses =/{print $3; exit}' "$log")"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$variant" "$cycles" "$instructions" "$accesses" "$misses" \
    "$(sum_frc_field "$log" allocations)" \
    "$(sum_frc_field "$log" lower_reads)" \
    "$(sum_frc_field "$log" swaps)" \
    "$(sum_frc_field "$log" set_full_fallbacks)" \
    "$(sum_frc_field "$log" write_fallbacks)" \
    "$(sum_frc_field "$log" atomic_fallbacks)" \
    >> "$run_root/summary.tsv"
done

printf 'PASS frc_core_sweep run_root=%s\n' "$run_root"
column -ts $'\t' "$run_root/summary.tsv" 2>/dev/null || cat "$run_root/summary.tsv"
