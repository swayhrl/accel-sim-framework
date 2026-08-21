#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/collect_l2_frc_delay_metrics.sh --run-root DIR --variants CSV

Collect final cumulative observation-only L2 lower-read delay statistics.
The decomposition is pre-memory (L2 acceptance -> lower issue), lower-memory
(lower issue -> lower return), and post-memory (lower return -> upper reply).
Management delay is pre-memory + post-memory.
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
[[ -d "$run_root" && -n "$variants_csv" ]] || { usage >&2; exit 2; }
run_root="$(cd "$run_root" && pwd)"
IFS=',' read -r -a variants <<< "$variants_csv"

global_field() {
  local log="$1"
  local field="$2"
  awk -v field="$field" '
    /^latebind_l2_global / {
      for (i = 1; i <= NF; ++i) {
        split($i, pair, "=")
        if (pair[1] == field) value = pair[2]
      }
    }
    END {
      if (value == "") exit 1
      print value
    }
  ' "$log"
}

summary="$run_root/delay.tsv"
printf 'variant\tcycles\tlower_reads\tavg_pre_mem_cycles\tavg_lower_mem_cycles\tavg_post_mem_cycles\tavg_management_cycles\n' > "$summary"
for variant in "${variants[@]}"; do
  log="$run_root/$variant/smoke.out"
  [[ -f "$log" ]] || { echo "error: missing log for $variant: $log" >&2; exit 1; }
  rg -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$log" || {
    echo "error: incomplete run for $variant: $log" >&2
    exit 1
  }
  cycles="$(awk '/^gpu_tot_sim_cycle =/{value=$3} END{if (value == "") exit 1; print value}' "$log")"
  count="$(global_field "$log" lower_read_delay_count)"
  pre="$(global_field "$log" lower_read_pre_mem_cycles)"
  lower_mem="$(global_field "$log" lower_read_mem_cycles)"
  post="$(global_field "$log" lower_read_post_mem_cycles)"
  if [[ "$count" == 0 ]]; then
    avg_pre=0
    avg_lower_mem=0
    avg_post=0
    avg_management=0
  else
    avg_pre="$(awk -v total="$pre" -v n="$count" 'BEGIN { printf "%.6f", total / n }')"
    avg_lower_mem="$(awk -v total="$lower_mem" -v n="$count" 'BEGIN { printf "%.6f", total / n }')"
    avg_post="$(awk -v total="$post" -v n="$count" 'BEGIN { printf "%.6f", total / n }')"
    avg_management="$(awk -v pre="$pre" -v post="$post" -v n="$count" 'BEGIN { printf "%.6f", (pre + post) / n }')"
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$variant" "$cycles" "$count" "$avg_pre" "$avg_lower_mem" "$avg_post" "$avg_management" >> "$summary"
done

printf 'PASS frc_delay_metrics run_root=%s\n' "$run_root"
column -ts $'\t' "$summary" 2>/dev/null || cat "$summary"
