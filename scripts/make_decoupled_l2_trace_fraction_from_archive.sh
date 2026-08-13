#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/make_decoupled_l2_trace_fraction_from_archive.sh \
       --archive SUITE.tgz --trace-member PATH/kernelslist.g \
       --output-dir DIR --fraction N

Create a trace view directly from a compressed archive, without materializing
the source workload on disk.  Every kernel named by kernelslist.g is retained;
each output kernel keeps complete CTA records through ceil(grid_ctas / N)
#END_TB boundaries and advertises the matching one-dimensional grid.

The archive is read once per selected member.  This trades archive I/O for a
bounded working-set and is intended for on-demand large-suite smoke runs such
as CUTLASS, not performance experiments.
EOF
}

archive=""
trace_member=""
output_dir=""
fraction=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --archive) archive="$2"; shift 2 ;;
    --trace-member) trace_member="$2"; shift 2 ;;
    --output-dir) output_dir="$2"; shift 2 ;;
    --fraction) fraction="$2"; shift 2 ;;
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

manifest="$output_dir/trace_fraction_manifest.csv"
printf 'kernel,source_grid,selected_ctas,fraction,output_bytes\n' > "$manifest"

for kernel in "${kernels[@]}"; do
  member="$trace_prefix/$kernel"
  # Consume the member fully so pipefail reports archive corruption instead of
  # a benign early-reader SIGPIPE.
  grid="$(tar --extract --to-stdout --file "$archive" "$member" | awk '
    !seen && /^-grid dim = / { print; seen = 1 }
  ')"
  if [[ ! "$grid" =~ \(([0-9]+),([0-9]+),([0-9]+)\) ]]; then
    echo "error: cannot parse grid in archive member $member" >&2
    exit 1
  fi
  grid_x="${BASH_REMATCH[1]}"
  grid_y="${BASH_REMATCH[2]}"
  grid_z="${BASH_REMATCH[3]}"
  source_ctas=$((grid_x * grid_y * grid_z))
  selected_ctas=$(((source_ctas + fraction - 1) / fraction))
  output="$output_dir/traces/$kernel"
  tmp="$output.tmp"

  tar --extract --to-stdout --file "$archive" "$member" | \
    awk -v selected_ctas="$selected_ctas" '
      /^-grid dim = \(/ {
        if (!finished) print "-grid dim = (" selected_ctas ",1,1)"
        next
      }
      !finished { print }
      $0 == "#END_TB" {
        completed_ctas++
        if (completed_ctas == selected_ctas) finished = 1
      }
      END {
        if (completed_ctas < selected_ctas) {
          printf "error: requested %d CTAs but found %d\\n", selected_ctas, completed_ctas > "/dev/stderr"
          exit 2
        }
      }
    ' > "$tmp"
  mv "$tmp" "$output"
  printf '%s,"(%s,%s,%s)",%s,%s,%s\n' "$kernel" "$grid_x" "$grid_y" "$grid_z" \
    "$selected_ctas" "$fraction" "$(stat -c %s "$output")" >> "$manifest"
done

while IFS= read -r kernel; do
  [[ -f "$output_dir/traces/$kernel" ]] || {
    echo "error: kernelslist references missing $kernel" >&2
    exit 1
  }
done < <(printf '%s\n' "${kernels[@]}")

: > "$output_dir/.trace_fraction_complete"
printf 'PASS archive=%s fraction=1/%s kernels=%s output=%s manifest=%s\n' \
  "$archive" "$fraction" "${#kernels[@]}" "$output_dir/traces" "$manifest"
