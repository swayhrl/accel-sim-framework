#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_l2_frc_assoc_sensitivity.sh --trace KERNELSLIST --config CONFIG
       [--trace-config FILE] [--run-root DIR]

Runs a capacity-matched low-associativity FRC sensitivity: one-way L2 control,
one-way L2 plus 128 FRC sectors, and two-way conventional L2.  FRC128 adds one
32-set x 128B way of payload to every QV100 sector-L2 slice.
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
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/l2-frc-assoc.XXXXXX")"
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

printf 'variant\tcycles\tinstructions\tscalar_opc\tl2_accesses\tl2_misses\tl2_mpko\tl2_reservation_fails\tfrc_allocations\tfrc_set_full_fallbacks\n' \
  > "$run_root/summary.tsv"
for variant in baseline1-pressure frc128-pressure baseline2-pressure; do
  args=(--trace "$trace" --config "$config" \
        --config-extra "$repo_root/configs/l2_frc/$variant.config" \
        --run-dir "$run_root/$variant")
  [[ -n "$trace_config" ]] && args+=(--trace-config "$trace_config")
  "$repo_root/scripts/run_latebind_l2_smoke.sh" "${args[@]}"
  log="$run_root/$variant/smoke.out"
  cycles="$(awk '/^gpu_tot_sim_cycle =/{print $3; exit}' "$log")"
  instructions="$(awk '/^gpu_tot_sim_insn =/{print $3; exit}' "$log")"
  accesses="$(awk '/^L2_total_cache_accesses =/{print $3; exit}' "$log")"
  misses="$(awk '/^L2_total_cache_misses =/{print $3; exit}' "$log")"
  fails="$(awk '/^L2_total_cache_reservation_fails =/{print $3; exit}' "$log")"
  opc="$(awk -v insn="$instructions" -v cycles="$cycles" 'BEGIN { printf "%.6f", insn / cycles }')"
  mpko="$(awk -v misses="$misses" -v insn="$instructions" 'BEGIN { printf "%.6f", 1000 * misses / insn }')"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$variant" "$cycles" "$instructions" "$opc" "$accesses" "$misses" \
    "$mpko" "$fails" \
    "$(sum_frc_field "$log" allocations)" \
    "$(sum_frc_field "$log" set_full_fallbacks)" \
    >> "$run_root/summary.tsv"
done

printf 'PASS frc_assoc_sensitivity run_root=%s\n' "$run_root"
column -ts $'\t' "$run_root/summary.tsv" 2>/dev/null || cat "$run_root/summary.tsv"
