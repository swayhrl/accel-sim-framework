#!/usr/bin/env bash
set -euo pipefail

# Invoked by GNU tar --to-command.  TAR_FILENAME is the member being streamed
# on stdin.  Keep this helper separate so the archive driver can consume every
# selected kernel in one tar pass.
: "${TRACE_FRACTION_OUTPUT_DIR:?}"
: "${TRACE_FRACTION_FRACTION:?}"
: "${TAR_FILENAME:?}"
trim_cta_insts="${TRACE_FRACTION_TRIM_CTA_INSTS:-0}"

kernel="$(basename "$TAR_FILENAME")"
output="$TRACE_FRACTION_OUTPUT_DIR/traces/$kernel"
tmp="$output.tmp.$$"
meta="$TRACE_FRACTION_OUTPUT_DIR/.${kernel}.meta"

awk -v fraction="$TRACE_FRACTION_FRACTION" -v trim_cta_insts="$trim_cta_insts" -v meta="$meta" '
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
  /^insts = / && trim_cta_insts {
    if (!match($0, /^insts = ([0-9]+)/, inst)) {
      print "error: malformed inst count" > "/dev/stderr"
      exit 2
    }
    source_insts = inst[1]
    # CTA selection is rounded up to retain every kernel.  Trim each retained
    # warp by the compensating ratio so the dynamic instruction budget remains
    # approximately 1/fraction even when a kernel has fewer CTAs than that.
    kept_insts = int((source_insts * source_ctas + fraction * selected_ctas - 1) / (fraction * selected_ctas))
    if (source_insts > 0 && kept_insts < 1) kept_insts = 1
    print "insts = " kept_insts
    skipped_insts = source_insts - kept_insts
    next
  }
  skipped_insts > 0 {
    skipped_insts--
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
    printf "%s\t(%s,%s,%s)\t%s\t%s\n", FILENAME, grid_x, grid_y, grid_z, selected_ctas, trim_cta_insts > meta
  }
' > "$tmp"
mv "$tmp" "$output"
