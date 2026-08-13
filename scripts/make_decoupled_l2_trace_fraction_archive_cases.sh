#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/make_decoupled_l2_trace_fraction_archive_cases.sh \
       --archive SUITE.tgz --case-list CASES.txt --output-dir DIR --fraction N
       [--trim-cta-insts] [--min-free-gib N]

Create 1/N functional-smoke trace views for several workload directories in
two archive passes: first their kernelslist.g files, then all referenced kernel
traces.  This avoids a full compressed-archive scan for every case and does
not materialize the original trace payload.  Each output case receives a
.trace_fraction_complete marker and manifest; the output root receives
.trace_fraction_cases_complete only after every selected case is verified.
Writing stops before a kernel if the filesystem would have less than the
requested free-space reserve (20 GiB by default).
EOF
}

archive=""; case_list=""; output_dir=""; fraction=""; trim_cta_insts=0
min_free_gib=20
while [[ $# -gt 0 ]]; do
  case "$1" in
    --archive) archive="$2"; shift 2 ;;
    --case-list) case_list="$2"; shift 2 ;;
    --output-dir) output_dir="$2"; shift 2 ;;
    --fraction) fraction="$2"; shift 2 ;;
    --trim-cta-insts) trim_cta_insts=1; shift ;;
    --min-free-gib) min_free_gib="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$archive" && -f "$case_list" ]] || { echo 'error: missing archive or case list' >&2; exit 2; }
[[ "$fraction" =~ ^[0-9]+$ && "$fraction" -ge 2 ]] || {
  echo 'error: --fraction must be at least two' >&2; exit 2;
}
[[ "$min_free_gib" =~ ^[0-9]+$ ]] || {
  echo 'error: --min-free-gib must be a non-negative integer' >&2; exit 2;
}
[[ ! -e "$output_dir" ]] || { echo "error: output already exists: $output_dir" >&2; exit 2; }

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
case_filter="$repo_root/scripts/filter_decoupled_l2_archive_trace_case_member.sh"
[[ -x "$case_filter" ]] || { echo "error: missing $case_filter" >&2; exit 2; }
archive="$(cd "$(dirname "$archive")" && pwd)/$(basename "$archive")"

mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"
selected="$output_dir/.selected_cases"
awk -F, 'NF && $1 != "case" { sub(/^\.\//, "", $1); print $1 }' "$case_list" | sort -u > "$selected"
[[ -s "$selected" ]] || { echo 'error: case list is empty' >&2; exit 2; }
while IFS= read -r case_path; do
  [[ "$case_path" != /* && "$case_path" != *".."* ]] || {
    echo "error: invalid case path $case_path" >&2; exit 2;
  }
done < "$selected"

kernelslists="$output_dir/.kernelslists"
awk '{ printf "%s/traces/kernelslist.g\n", $0 }' "$selected" > "$kernelslists"
# Keep just the tiny kernelslists on disk.  GNU tar scans the compressed
# archive once for all requested members rather than once per workload.
tar --extract --file "$archive" --directory "$output_dir" --files-from="$kernelslists"

members="$output_dir/.kernel_members"
: > "$members"
while IFS= read -r case_path; do
  list="$output_dir/$case_path/traces/kernelslist.g"
  [[ -s "$list" ]] || { echo "error: archive lacks $case_path kernelslist" >&2; exit 1; }
  while IFS= read -r kernel; do printf '%s/traces/%s\n' "$case_path" "$kernel" >> "$members"; done \
    < <(rg -o 'kernel-[0-9]+\.traceg' "$list" | sort -u)
done < "$selected"
[[ -s "$members" ]] || { echo 'error: no kernel members selected' >&2; exit 1; }

# The adapter maps each streamed member to its own case directory, preserving
# names such as kernel-0.traceg that recur across workloads.
TRACE_FRACTION_CASE_OUTPUT_DIR="$output_dir" \
TRACE_FRACTION_FRACTION="$fraction" \
TRACE_FRACTION_TRIM_CTA_INSTS="$trim_cta_insts" \
TRACE_FRACTION_MIN_FREE_KIB="$((min_free_gib * 1024 * 1024))" \
tar --extract --to-command="$case_filter" --files-from="$members" --file "$archive"

while IFS= read -r case_path; do
  case_dir="$output_dir/$case_path"
  list="$case_dir/traces/kernelslist.g"
  manifest="$case_dir/trace_fraction_manifest.csv"
  printf 'kernel,source_grid,selected_ctas,fraction,trim_cta_insts,output_bytes\n' > "$manifest"
  while IFS= read -r kernel; do
    output="$case_dir/traces/$kernel"
    meta="$case_dir/.${kernel}.meta"
    [[ -s "$output" && -s "$meta" ]] || {
      echo "error: filtered output missing $case_path/$kernel" >&2; exit 1;
    }
    IFS=$'\t' read -r _ source_grid selected_ctas recorded_trim < "$meta"
    [[ "$recorded_trim" == "$trim_cta_insts" ]] || {
      echo "error: mismatched trim metadata $case_path/$kernel" >&2; exit 1;
    }
    printf '%s,"%s",%s,%s,%s,%s\n' "$kernel" "$source_grid" "$selected_ctas" \
      "$fraction" "$trim_cta_insts" "$(stat -c %s "$output")" >> "$manifest"
  done < <(rg -o 'kernel-[0-9]+\.traceg' "$list" | sort -u)
  : > "$case_dir/.trace_fraction_complete"
done < "$selected"

: > "$output_dir/.trace_fraction_cases_complete"
printf 'PASS archive=%s cases=%s fraction=1/%s trim_cta_insts=%s min_free_gib=%s output=%s\n' \
  "$archive" "$(wc -l < "$selected")" "$fraction" "$trim_cta_insts" "$min_free_gib" "$output_dir"
