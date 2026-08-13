#!/usr/bin/env bash
set -euo pipefail

# Invoked by GNU tar --to-command.  TAR_FILENAME is the member being streamed
# on stdin.  Keep this helper separate so the archive driver can consume every
# selected kernel in one tar pass.
: "${TRACE_FRACTION_OUTPUT_DIR:?}"
: "${TRACE_FRACTION_FRACTION:?}"
: "${TAR_FILENAME:?}"

kernel="$(basename "$TAR_FILENAME")"
output="$TRACE_FRACTION_OUTPUT_DIR/traces/$kernel"
tmp="$output.tmp.$$"
meta="$TRACE_FRACTION_OUTPUT_DIR/.${kernel}.meta"

awk -v fraction="$TRACE_FRACTION_FRACTION" -v meta="$meta" '
  /^-grid dim = \(/ {
    if (seen_grid++) {
      print "error: multiple grid lines" > "/dev/stderr"
      exit 2
    }
    if (!match($0, /\(([0-9]+),([0-9]+),([0-9]+)\)/, dims)) {
      print "error: malformed grid line" > "/dev/stderr"
      exit 2
    }
    grid_x = dims[1]
    grid_y = dims[2]
    grid_z = dims[3]
    source_ctas = grid_x * grid_y * grid_z
    selected_ctas = int((source_ctas + fraction - 1) / fraction)
    print "-grid dim = (" selected_ctas ",1,1)"
    next
  }
  { print }
  $0 == "#END_TB" {
    completed_ctas++
    if (completed_ctas == selected_ctas) exit
  }
  END {
    if (!seen_grid) {
      print "error: missing grid line" > "/dev/stderr"
      exit 2
    }
    if (completed_ctas < selected_ctas) {
      printf "error: requested %d CTAs but found %d\n", selected_ctas, completed_ctas > "/dev/stderr"
      exit 2
    }
    printf "%s\t(%s,%s,%s)\t%s\n", FILENAME, grid_x, grid_y, grid_z, selected_ctas > meta
  }
' > "$tmp"
mv "$tmp" "$output"
