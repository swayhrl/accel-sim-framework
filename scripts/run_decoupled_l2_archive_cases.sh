#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_decoupled_l2_archive_cases.sh --archive SUITE.tgz --suite NAME
       [--case NAME|all] [--case-path RELATIVE_PATH] [--config FILE]
       [--trace-config FILE]
       [--run-root DIR] [--scratch-root DIR] [--min-free-gib N]
       [--discard-failed-extract] [--reuse]

Discovers every kernelslist.g in one compressed Accel-Sim trace archive, then
tests each workload sequentially with baseline and decoupled L2 backends. Only
the current workload's traces are extracted under SCRATCH-ROOT and removed
after a successful pair. On failure, the output log, a failure manifest, and
the current extracted trace set are preserved for diagnosis; use
--discard-failed-extract to reclaim that trace set instead. MIN-FREE-GIB
(default 80) is preserved before every extraction and after normal cleanup.
EOF
}

archive=""; suite=""; case_filter="all"; case_path_filter=""; config=""; trace_config=""
config_given=0; run_root=""; scratch_root=""; min_free_gib=80
keep_failed_extract=1
reuse=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --archive) archive="$2"; shift 2 ;;
    --suite) suite="$2"; shift 2 ;;
    --case) case_filter="$2"; shift 2 ;;
    --case-path) case_path_filter="$2"; shift 2 ;;
    --config) config="$2"; config_given=1; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --run-root) run_root="$2"; shift 2 ;;
    --scratch-root) scratch_root="$2"; shift 2 ;;
    --min-free-gib) min_free_gib="$2"; shift 2 ;;
    --discard-failed-extract) keep_failed_extract=0; shift ;;
    --reuse) reuse=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$archive" ]] || { echo "error: --archive must be a readable .tgz" >&2; exit 2; }
[[ -n "$suite" ]] || { echo "error: --suite is required" >&2; exit 2; }
[[ "$min_free_gib" =~ ^[0-9]+$ ]] || { echo "error: invalid --min-free-gib" >&2; exit 2; }
[[ -n "${DECOUPLED_L2_GPGPUSIM_ROOT:-}" ]] || { echo "error: set DECOUPLED_L2_GPGPUSIM_ROOT" >&2; exit 2; }

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$config" ]]; then
  config="$DECOUPLED_L2_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
fi
[[ -f "$config" ]] || { echo "error: missing config $config" >&2; exit 2; }
if [[ -z "$trace_config" && "$config_given" -eq 0 ]]; then
  trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
fi
[[ -z "$trace_config" || -f "$trace_config" ]] || { echo "error: missing trace config" >&2; exit 2; }

if [[ -z "$run_root" ]]; then
  run_root="$repo_root/hw_run/decoupled-l2-runs/${suite}_$(date +%Y%m%d_%H%M%S)"
fi
if [[ -z "$scratch_root" ]]; then scratch_root="$repo_root/hw_run/decoupled-l2-extract"; fi
mkdir -p "$run_root" "$scratch_root"
run_root="$(cd "$run_root" && pwd)"
scratch_root="$(cd "$scratch_root" && pwd)"
min_free_kib=$((min_free_gib * 1024 * 1024))

available_kib() { df -Pk "$scratch_root" | awk 'NR == 2 { print $4 }'; }
tar_read() {
  if command -v pigz >/dev/null 2>&1; then
    tar --use-compress-program=pigz "$@"
  else
    tar --gzip "$@"
  fi
}
require_free_kib() {
  local required_kib="$1" action="$2" available
  available="$(available_kib)"
  if (( available < required_kib )); then
    printf 'error: refusing %s: need %d GiB free, have %d GiB\n' "$action" \
      "$(((required_kib + 1024 * 1024 - 1) / (1024 * 1024)))" \
      "$((available / (1024 * 1024)))" >&2
    exit 1
  fi
}

# Each path is a workload argument set, not merely an application name. The
# normal path lists the archive once; --case-path avoids that scan for a known
# development case. Extraction below is always scoped to one trace set.
case_list="$run_root/${suite}_cases.txt"
if [[ -n "$case_path_filter" ]]; then
  [[ "$case_path_filter" != /* && "$case_path_filter" != *".."* ]] || {
    echo "error: --case-path must be a relative archive path" >&2; exit 2;
  }
  printf '%s\n' "${case_path_filter#./}" > "$case_list"
else
  tar_read --list --file "$archive" | awk '
    /\/traces\/kernelslist\.g$/ {
      sub(/^\.\//, "", $0)
      sub(/\/traces\/kernelslist\.g$/, "", $0)
      print
    }
  ' > "$case_list"
fi
[[ -s "$case_list" ]] || { echo "error: no kernelslist.g in $archive" >&2; exit 1; }

summary="$run_root/summary.csv"
printf 'suite,case,backend,cycles,run_dir\n' > "$summary"
failures="$run_root/failures.csv"
printf 'time,suite,case,backend,stage,run_dir,trace_dir,smoke_out\n' > "$failures"
case_count=0
case_dir=""
current_case=""
current_backend=""
current_stage="setup"
current_run_dir=""
cleanup_case() {
  [[ -n "$case_dir" && "$case_dir" == "$scratch_root"/* ]] && rm -rf "$case_dir"
}
finish() {
  local status="$?"
  if (( status != 0 )); then
    printf '%s,%s,%s,%s,%s,%s,%s,%s\n' "$(date --iso-8601=seconds)" \
      "$suite" "$current_case" "$current_backend" "$current_stage" \
      "$current_run_dir" "$case_dir" "$current_run_dir/smoke.out" >> "$failures"
    if (( keep_failed_extract )) && [[ -n "$case_dir" && "$case_dir" == "$scratch_root"/* ]]; then
      printf 'FAIL preserved traces=%s log=%s manifest=%s\n' "$case_dir" \
        "$current_run_dir/smoke.out" "$failures" >&2
      case_dir=""
    else
      cleanup_case
    fi
  else
    cleanup_case
  fi
}
trap finish EXIT
while IFS= read -r case_path; do
  current_case="$case_path"
  case_name="${case_path##*/}"
  [[ "$case_filter" == all || "$case_filter" == "$case_name" ]] || continue
  case_count=$((case_count + 1))
  trace_kib="$(tar_read --list --verbose --wildcards --file "$archive" \
    "./$case_path/traces/*" | awk '{ bytes += $3 } END { print int((bytes + 1023) / 1024) }')"
  [[ "$trace_kib" =~ ^[0-9]+$ ]] || { echo "error: cannot size $case_path" >&2; exit 1; }
  require_free_kib "$((min_free_kib + trace_kib))" "extraction of $case_path"

  case_dir="$(mktemp -d "$scratch_root/${suite}.XXXXXX")"
  current_stage="extract"
  tar_read --extract --wildcards --file "$archive" --directory "$case_dir" \
    "./$case_path/traces/*"
  trace="$case_dir/$case_path/traces/kernelslist.g"
  [[ -f "$trace" ]] || { echo "error: extraction lost $case_path" >&2; exit 1; }

  for backend in baseline decoupled; do
    current_backend="$backend"
    current_stage="simulate"
    case_run_dir="$run_root/$suite/$case_path/$backend"
    current_run_dir="$case_run_dir"
    smoke_args=(--backend "$backend" --trace "$trace" --config "$config" --run-dir "$case_run_dir")
    if [[ -n "$trace_config" ]]; then smoke_args+=(--trace-config "$trace_config"); fi
    if [[ "$reuse" -eq 1 && -f "$case_run_dir/smoke.out" ]] && \
       rg -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$case_run_dir/smoke.out"; then
      printf 'REUSE backend=%s run_dir=%s\n' "$backend" "$case_run_dir"
    else
      if ! "$repo_root/scripts/run_decoupled_l2_smoke.sh" "${smoke_args[@]}"; then
        echo "error: $suite/$case_path backend=$backend failed; see $failures" >&2
        exit 1
      fi
    fi
    if [[ "$backend" == decoupled ]]; then
      rg -q 'decoupled_l2\[.*access=[1-9]' "$case_run_dir/smoke.out" || {
        echo "error: $case_path did not exercise decoupled L2" >&2; exit 1;
      }
    fi
    cycles="$(sed -n 's/.*gpu_tot_sim_cycle = \([0-9][0-9]*\).*/\1/p' "$case_run_dir/smoke.out" | tail -1)"
    [[ -n "$cycles" ]] || { echo "error: no final cycle count for $case_run_dir" >&2; exit 1; }
    printf '%s,%s,%s,%s,%s\n' "$suite" "$case_path" "$backend" "$cycles" "$case_run_dir" >> "$summary"
  done
  cleanup_case
  case_dir=""
  current_stage="cleanup"
  require_free_kib "$min_free_kib" "post-run cleanup of $case_path"
done < "$case_list"

[[ "$case_count" -gt 0 ]] || { echo "error: selected suite has no cases" >&2; exit 2; }
printf 'PASS cases=%s summary=%s\n' "$case_count" "$summary"
