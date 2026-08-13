#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/make_decoupled_l2_trace_fraction_from_archive.sh \
       --archive SUITE.tgz --trace-member PATH/kernelslist.g \
       --output-dir DIR --fraction N [--trim-cta-insts]

Create a trace view directly from a compressed archive, without materializing
the source workload on disk.  Every kernel named by kernelslist.g is retained;
by default each output kernel keeps complete CTA records through
ceil(grid_ctas / N) #END_TB boundaries and advertises the matching
one-dimensional grid.

--trim-cta-insts additionally caps each retained warp's instruction record
count by the compensating CTA-rounding ratio.  Use it for functional smoke
runs when a kernel has fewer than N CTAs and one complete CTA alone exceeds
the intended memory budget.  The resulting trace remains syntactically valid
and runs every kernel, but is not suitable for performance comparison.

The archive is read twice: once for kernelslist.g and once to stream every
selected kernel through GNU tar's --to-command hook.  This keeps the working
set bounded without multiplying compressed-archive reads by kernel count.  It
is intended for on-demand large-suite smoke runs such as CUTLASS, not
performance experiments.
EOF
}

archive=""
trace_member=""
output_dir=""
fraction=""
trim_cta_insts=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --archive) archive="$2"; shift 2 ;;
    --trace-member) trace_member="$2"; shift 2 ;;
    --output-dir) output_dir="$2"; shift 2 ;;
    --fraction) fraction="$2"; shift 2 ;;
    --trim-cta-insts) trim_cta_insts=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$archive" ]] || { echo "error: --archive must name a readable archive" >&2; exit 2; }
[[ "$trace_member" == */kernelslist.g ]] || {
  echo "error: --trace-member must end in /kernelslist.g" >&2
  exit 2
}
[[ "$fraction" =~ ^[0-9]+$ && "$fraction" -ge 2 ]] || {
  echo "error: --fraction must be an integer of at least two" >&2
  exit 2
}
[[ ! -e "$output_dir" ]] || {
  echo "error: --output-dir already exists; keep generated traces immutable" >&2
  exit 2
}

archive="$(cd "$(dirname "$archive")" && pwd)/$(basename "$archive")"
trace_prefix="${trace_member%/kernelslist.g}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
member_filter="$repo_root/scripts/filter_decoupled_l2_archive_trace_member.sh"
[[ -x "$member_filter" ]] || { echo "error: missing $member_filter" >&2; exit 2; }
mkdir -p "$output_dir/traces"
output_dir="$(cd "$output_dir" && pwd)"

# A full member read is deliberate: it avoids a broken tar/SIGPIPE pipeline
# after the selected final CTA while leaving no full source trace on disk.
tar --extract --to-stdout --file "$archive" "$trace_member" \
  > "$output_dir/traces/kernelslist.g"

mapfile -t kernels < <(
  rg -o 'kernel-[0-9]+\.traceg' "$output_dir/traces/kernelslist.g" | sort -u
)
(( ${#kernels[@]} > 0 )) || {
  echo "error: kernelslist member contains no kernel traces" >&2
  exit 1
}

members_file="$output_dir/.archive_members"
for kernel in "${kernels[@]}"; do
  printf '%s/%s\n' "$trace_prefix" "$kernel"
done > "$members_file"

TRACE_FRACTION_OUTPUT_DIR="$output_dir" \
TRACE_FRACTION_FRACTION="$fraction" \
TRACE_FRACTION_TRIM_CTA_INSTS="$trim_cta_insts" \
tar --extract --to-command="$member_filter" --files-from="$members_file" --file "$archive"

manifest="$output_dir/trace_fraction_manifest.csv"
printf 'kernel,source_grid,selected_ctas,fraction,trim_cta_insts,output_bytes\n' > "$manifest"
for kernel in "${kernels[@]}"; do
  meta="$output_dir/.${kernel}.meta"
  [[ -f "$output_dir/traces/$kernel" && -s "$meta" ]] || {
    echo "error: archive did not provide $kernel" >&2
    exit 1
  }
  IFS=$'\t' read -r recorded_kernel source_grid selected_ctas recorded_trim < "$meta"
  [[ "$recorded_kernel" == "-" || "$recorded_kernel" == "$kernel" ]] || {
    echo "error: mismatched archive member metadata for $kernel" >&2
    exit 1
  }
  [[ "$recorded_trim" == "$trim_cta_insts" ]] || {
    echo "error: mismatched instruction-trim metadata for $kernel" >&2
    exit 1
  }
  printf '%s,"%s",%s,%s,%s,%s\n' "$kernel" "$source_grid" "$selected_ctas" "$fraction" "$trim_cta_insts" \
    "$(stat -c %s "$output_dir/traces/$kernel")" >> "$manifest"
done

while IFS= read -r kernel; do
  [[ -f "$output_dir/traces/$kernel" ]] || {
    echo "error: kernelslist references missing $kernel" >&2
    exit 1
  }
done < <(printf '%s\n' "${kernels[@]}")

: > "$output_dir/.trace_fraction_complete"
printf 'PASS archive=%s fraction=1/%s trim_cta_insts=%s kernels=%s output=%s manifest=%s\n' \
  "$archive" "$fraction" "$trim_cta_insts" "${#kernels[@]}" "$output_dir/traces" "$manifest"
