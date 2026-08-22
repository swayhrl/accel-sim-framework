#!/usr/bin/env bash
# Summarize elapsed time and peak RSS retained by Decoupled-L2 experiment runs.
# Old runs have no resource_usage.txt; their smoke.out simulation time is still
# useful for planning, but is explicitly labelled as simulator-reported.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/report_decoupled_l2_resources.sh --run-root DIR [--out FILE]
       [--live-pid PID]...

Read every summary.csv below DIR and write a Markdown resource-planning report.
Preferred future source: runtime_metrics.txt + resource_usage.txt, produced by
run_decoupled_l2_smoke.sh.  Older runs fall back to the final
gpgpu_simulation_time line in smoke.out, then file-mtime inference.

--live-pid adds a point-in-time RSS/elapsed snapshot for an active simulator.
It is not a recorded peak and is kept separate from completed-run statistics.
EOF
}

run_root=""
out=""
live_pids=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-root) run_root="$2"; shift 2 ;;
    --out) out="$2"; shift 2 ;;
    --live-pid) live_pids+=("$2"); shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -d "$run_root" ]] || { echo "error: --run-root must be a directory" >&2; exit 2; }
run_root="$(cd "$run_root" && pwd)"
if [[ -z "$out" ]]; then
  out="$run_root/RESOURCE_PLANNING.md"
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

# summary.csv has either suite,case,backend,cycles,run_dir or an additional
# tier field between suite and case.  Use its run_dir rather than path naming.
while IFS=$'\t' read -r suite case backend run_dir; do
  [[ -f "$run_dir/smoke.out" ]] || continue
  rg -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$run_dir/smoke.out" || continue

  elapsed=""
  elapsed_source=""
  if [[ -f "$run_dir/runtime_metrics.txt" ]]; then
    elapsed="$(sed -n 's/^wall_seconds=//p' "$run_dir/runtime_metrics.txt" | tail -1)"
    elapsed_source="wall-clock"
  fi
  if [[ ! "$elapsed" =~ ^[0-9]+$ ]]; then
    elapsed="$(sed -n 's/.*gpgpu_simulation_time = .* (\([0-9][0-9]*\) sec).*/\1/p' \
      "$run_dir/smoke.out" | tail -1)"
    elapsed_source="simulator-log"
  fi
  if [[ ! "$elapsed" =~ ^[0-9]+$ && -f "$run_dir/gpgpusim.config" ]]; then
    elapsed="$(( $(stat -c %Y "$run_dir/smoke.out") - $(stat -c %Y "$run_dir/gpgpusim.config") ))"
    elapsed_source="mtime-inferred"
  fi
  [[ "$elapsed" =~ ^[0-9]+$ ]] || { elapsed="-"; elapsed_source="unavailable"; }

  peak_kib=""
  if [[ -f "$run_dir/resource_usage.txt" ]]; then
    peak_kib="$(sed -n 's/^\tMaximum resident set size (kbytes): \([0-9][0-9]*\)$/\1/p' \
      "$run_dir/resource_usage.txt" | tail -1)"
  fi
  if [[ "$peak_kib" =~ ^[0-9]+$ ]]; then
    peak_mib="$((peak_kib / 1024))"
  else
    peak_mib="-"
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$suite" "$case" "$backend" "$elapsed" "$elapsed_source" "$peak_mib" "$run_dir" >> "$tmp"
done < <(
  find "$run_root" -type f -name summary.csv -print0 | while IFS= read -r -d '' summary; do
    awk -F, 'NR > 1 {
      if (NF == 5) print $1 "\t" $2 "\t" $3 "\t" $5;
      else if (NF == 6) print $1 "\t" $3 "\t" $4 "\t" $6;
    }' "$summary"
  done | awk '!seen[$4]++'
)

format_duration() {
  local sec="$1"
  if [[ ! "$sec" =~ ^[0-9]+$ ]]; then
    printf '%s' '-'
  else
    printf '%02dh%02dm%02ds' "$((sec / 3600))" "$(((sec / 60) % 60))" "$((sec % 60))"
  fi
}

{
  printf '# Decoupled-L2 resource-planning report\n\n'
  printf 'Generated: %s  \n' "$(date -Is)"
  printf 'Run root: `%s`\n\n' "$run_root"
  printf 'A row requires a normal simulator exit.  `wall-clock` and peak RSS are exact only for runs launched after the resource recorder was added.  `simulator-log` is the simulator’s final `gpgpu_simulation_time`; `mtime-inferred` is a weaker fallback.  Historical runs did not retain peak RSS.\n\n'
  printf '| Workload | Backend | Elapsed | Seconds | Source | Peak RSS (MiB) | Run directory |\n'
  printf '|---|---|---:|---:|---|---:|---|\n'
  while IFS=$'\t' read -r suite case backend elapsed source peak_mib run_dir; do
    printf '| `%s/%s` | `%s` | %s | %s | %s | %s | `%s` |\n' \
      "$suite" "$case" "$backend" "$(format_duration "$elapsed")" "$elapsed" "$source" "$peak_mib" "$run_dir"
  done < <(sort -t$'\t' -k1,1 -k2,2 -k3,3 "$tmp")

  printf '\n## Aggregate wall-time planning\n\n'
  printf '| Backend | Completed runs | Total elapsed | Median elapsed | Longest run |\n'
  printf '|---|---:|---:|---:|---:|\n'
  for backend in baseline decoupled fixed; do
    mapfile -t samples < <(awk -F$'\t' -v b="$backend" '$3 == b && $4 ~ /^[0-9]+$/ { print $4 }' "$tmp" | sort -n)
    count="${#samples[@]}"
    (( count > 0 )) || continue
    total=0
    for sec in "${samples[@]}"; do total=$((total + sec)); done
    median="${samples[$(((count - 1) / 2))]}"
    longest="${samples[$((count - 1))]}"
    printf '| `%s` | %s | %s | %s | %s |\n' "$backend" "$count" \
      "$(format_duration "$total")" "$(format_duration "$median")" "$(format_duration "$longest")"
  done

  if (( ${#live_pids[@]} > 0 )); then
    printf '\n## Active-process snapshots\n\n'
    printf 'These values are sampled when this report is generated.  RSS is neither a peak nor a reservation recommendation.\n\n'
    printf '| PID | Elapsed | Current RSS (MiB) | Command |\n'
    printf '|---:|---:|---:|---|\n'
    for pid in "${live_pids[@]}"; do
      if ps -p "$pid" >/dev/null 2>&1; then
        read -r elapsed rss cmd < <(ps -p "$pid" -o etime=,rss=,args=)
        printf '| `%s` | `%s` | %s | `%s` |\n' "$pid" "$elapsed" \
          "$((rss / 1024))" "$cmd"
      else
        printf '| `%s` | exited | - | - |\n' "$pid"
      fi
    done
  fi

  printf '\n## Scheduling guidance\n\n'
  printf -- '- Treat the table as a planning prior, not a performance result: elapsed time depends on host contention and the exact simulator binary/configuration.\n'
  printf -- '- Do not derive a process peak from today’s cgroup peak or a one-time `ps` RSS sample.  Use the recorded maximum RSS once several same-class runs are available, then reserve at least 25%% headroom per simulator.\n'
  printf -- '- Keep the existing global archive admission gate until those data exist; it protects disk staging and aggregate memory even when CPU is idle.\n'
  printf -- '- Capacity planning must retain the configured free-disk reserve in addition to each staged trace.  A fast simulator run can still require a large temporary trace extraction.\n'
} > "$out"

printf 'wrote %s (%s completed runs)\n' "$out" "$(wc -l < "$tmp")"
