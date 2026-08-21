#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/collect_l2_frc_core_metrics.sh --run-root DIR [--variants CSV]

Rebuild summary.tsv from completed run_l2_frc_core_sweep logs.  Multi-kernel
traces emit intermediate statistics, so every metric is taken from the final
cumulative occurrence in each smoke.out.
EOF
}

run_root=""
variants_csv=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-root) run_root="$2"; shift 2 ;;
    --variants) variants_csv="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -d "$run_root" ]] || { usage >&2; exit 2; }
run_root="$(cd "$run_root" && pwd)"

default_variants=(baseline24 frc4-paper frc8-paper frc16-paper frc32-paper frc64-paper frc128-paper baseline25 frc256-paper baseline26 baseline48-paper_capacity baseline96-paper_capacity)
if [[ -n "$variants_csv" ]]; then
  IFS=',' read -r -a variants <<< "$variants_csv"
else
  variants=("${default_variants[@]}")
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

summary="$run_root/summary.tsv"
printf 'variant\tcycles\tinstructions\tscalar_opc\tl2_accesses\tl2_misses\tl2_mpko\tfrc_allocations\tfrc_lower_reads\tfrc_swaps\tfrc_set_full_fallbacks\tfrc_write_fallbacks\tfrc_atomic_fallbacks\n' \
  > "$summary"
for variant in "${variants[@]}"; do
  log="$run_root/$variant/smoke.out"
  [[ -f "$log" ]] || { echo "error: missing log for $variant: $log" >&2; exit 1; }
  rg -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$log" || {
    echo "error: incomplete run for $variant: $log" >&2
    exit 1
  }
  cycles="$(awk '/^gpu_tot_sim_cycle =/{value=$3} END{print value}' "$log")"
  instructions="$(awk '/^gpu_tot_sim_insn =/{value=$3} END{print value}' "$log")"
  accesses="$(awk '/^L2_total_cache_accesses =/{value=$3} END{print value}' "$log")"
  misses="$(awk '/^L2_total_cache_misses =/{value=$3} END{print value}' "$log")"
  [[ -n "$cycles" && -n "$instructions" && -n "$accesses" && -n "$misses" ]] || {
    echo "error: incomplete statistics for $variant: $log" >&2
    exit 1
  }
  opc="$(awk -v insn="$instructions" -v cycles="$cycles" 'BEGIN { printf "%.6f", insn / cycles }')"
  mpko="$(awk -v misses="$misses" -v insn="$instructions" 'BEGIN { printf "%.6f", 1000 * misses / insn }')"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$variant" "$cycles" "$instructions" "$opc" "$accesses" "$misses" "$mpko" \
    "$(sum_frc_field "$log" allocations)" \
    "$(sum_frc_field "$log" lower_reads)" \
    "$(sum_frc_field "$log" swaps)" \
    "$(sum_frc_field "$log" set_full_fallbacks)" \
    "$(sum_frc_field "$log" write_fallbacks)" \
    "$(sum_frc_field "$log" atomic_fallbacks)" \
    >> "$summary"
done

printf 'PASS frc_core_metrics run_root=%s\n' "$run_root"
column -ts $'\t' "$summary" 2>/dev/null || cat "$summary"
