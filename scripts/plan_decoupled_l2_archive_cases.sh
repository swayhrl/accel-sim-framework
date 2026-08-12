#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/plan_decoupled_l2_archive_cases.sh --archive SUITE.tgz
       [--min-free-gib N] [--run-overhead-gib N] [--max-parallel N]
       [--output-dir DIR]

Scans a compressed trace archive once, calculates the exact uncompressed byte
count of every workload's traces/ directory, and writes cases.txt, sizes.csv, plus a
capacity-safe first-fit-decreasing schedule.csv.  Every wave preserves
MIN-FREE-GIB (default 80) and RUN-OVERHEAD-GIB (default 16) of non-trace
space. MAX-PARALLEL (default 1) is an additional per-wave concurrency cap.
EOF
}

archive=""; min_free_gib=80; run_overhead_gib=16; max_parallel=1; output_dir=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --archive) archive="$2"; shift 2 ;;
    --min-free-gib) min_free_gib="$2"; shift 2 ;;
    --run-overhead-gib) run_overhead_gib="$2"; shift 2 ;;
    --max-parallel) max_parallel="$2"; shift 2 ;;
    --output-dir) output_dir="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$archive" ]] || { echo "error: --archive must be a readable .tgz" >&2; exit 2; }
for value in "$min_free_gib" "$run_overhead_gib" "$max_parallel"; do
  [[ "$value" =~ ^[0-9]+$ && "$value" -gt 0 ]] || {
    echo "error: numeric options must be positive integers" >&2; exit 2;
  }
done

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$output_dir" ]]; then
  output_dir="$repo_root/hw_run/decoupled-l2-plans/$(basename "$archive" .tgz)"
fi
mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"

available_kib="$(df -Pk "$output_dir" | awk 'NR == 2 { print $4 }')"
reserve_kib=$(((min_free_gib + run_overhead_gib) * 1024 * 1024))
(( available_kib > reserve_kib )) || {
  echo "error: only $((available_kib / 1024 / 1024)) GiB free; reserve is $((reserve_kib / 1024 / 1024)) GiB" >&2
  exit 1
}
budget_kib=$((available_kib - reserve_kib))

tar_read() {
  if command -v pigz >/dev/null 2>&1; then
    tar --use-compress-program=pigz "$@"
  else
    tar --gzip "$@"
  fi
}

raw="$output_dir/members.raw"
cases="$output_dir/cases.txt"
sizes="$output_dir/sizes.csv"
schedule="$output_dir/schedule.csv"
tar_read --list --verbose --file "$archive" | awk '
  $6 ~ /\/traces\// {
    path = $6
    sub(/^\.\//, "", path)
    split(path, part, "/traces/")
    work = part[1]
    bytes[work] += $3
    if (path ~ /\/traces\/kernelslist\.g$/) selected[work] = 1
  }
  END {
    for (work in selected) printf "%s,%d\n", work, bytes[work]
  }
' > "$raw"
[[ -s "$raw" ]] || { echo "error: archive has no workload kernelslist.g" >&2; exit 1; }

sort -t, -k2,2nr "$raw" | cut -d, -f1 > "$cases"

printf 'case,trace_bytes,trace_gib\n' > "$sizes"
sort -t, -k2,2nr "$raw" | while IFS=, read -r case_path bytes; do
  awk -v case_path="$case_path" -v bytes="$bytes" \
    'BEGIN { printf "%s,%d,%.3f\n", case_path, bytes, bytes / 1024 / 1024 / 1024 }' >> "$sizes"
done

printf 'wave,case,trace_bytes,trace_gib,wave_trace_gib\n' > "$schedule"
declare -a wave_kib wave_count
wave_total=0
while IFS=, read -r case_path bytes; do
  case_kib=$(((bytes + 1023) / 1024))
  (( case_kib <= budget_kib )) || {
    echo "error: $case_path alone needs $((case_kib / 1024 / 1024)) GiB, above $((budget_kib / 1024 / 1024)) GiB budget" >&2
    exit 1
  }
  chosen=-1
  for ((wave = 0; wave < wave_total; ++wave)); do
    if (( wave_count[wave] < max_parallel && wave_kib[wave] + case_kib <= budget_kib )); then
      chosen=$wave
      break
    fi
  done
  if (( chosen < 0 )); then
    chosen=$wave_total
    wave_kib[chosen]=0
    wave_count[chosen]=0
    wave_total=$((wave_total + 1))
  fi
  wave_kib[chosen]=$((wave_kib[chosen] + case_kib))
  wave_count[chosen]=$((wave_count[chosen] + 1))
  awk -v wave="$((chosen + 1))" -v case_path="$case_path" -v bytes="$bytes" \
      -v wave_kib="${wave_kib[chosen]}" \
    'BEGIN { printf "%d,%s,%d,%.3f,%.3f\n", wave, case_path, bytes, bytes / 1024 / 1024 / 1024, wave_kib / 1024 / 1024 }' >> "$schedule"
done < <(sort -t, -k2,2nr "$raw")

printf 'PLAN workloads=%d waves=%d budget_gib=%d reserve_gib=%d max_parallel=%d\n' \
  "$(wc -l < "$raw")" "$wave_total" "$((budget_kib / 1024 / 1024))" \
  "$((reserve_kib / 1024 / 1024))" "$max_parallel"
printf 'cases=%s sizes=%s schedule=%s\n' "$cases" "$sizes" "$schedule"
