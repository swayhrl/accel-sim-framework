#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/make_decoupled_l2_trace_fraction.sh --trace-dir DIR --output-dir DIR
       --fraction N [--trim-cta-insts]

Create an independent trace view that replays approximately 1/N of each
kernel's CTAs.  The source trace is never changed.  By default every generated
kernel retains a complete header and complete CTA records through the selected
final #END_TB, then advertises a matching one-dimensional grid.  This is
suited to functional/protocol smoke experiments, not performance comparison.

--trim-cta-insts also caps instruction records inside each retained CTA by
the compensating CTA-rounding ratio.  It is needed when one complete CTA from
a low-grid kernel dominates host memory; it preserves every kernel and a
valid trace format, but is functional-smoke-only.
EOF
}

trace_dir=""
output_dir=""
fraction=""
trim_cta_insts=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace-dir) trace_dir="$2"; shift 2 ;;
    --output-dir) output_dir="$2"; shift 2 ;;
    --fraction) fraction="$2"; shift 2 ;;
    --trim-cta-insts) trim_cta_insts=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -d "$trace_dir" && -f "$trace_dir/kernelslist.g" ]] || {
  echo "error: --trace-dir must contain kernelslist.g" >&2
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

trace_dir="$(cd "$trace_dir" && pwd)"
mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"
mkdir "$output_dir/traces"
cp "$trace_dir/kernelslist.g" "$output_dir/traces/kernelslist.g"

manifest="$output_dir/trace_fraction_manifest.csv"
printf 'kernel,source_grid,selected_ctas,fraction,trim_cta_insts,source_bytes,output_bytes\n' > "$manifest"
shopt -s nullglob
inputs=("$trace_dir"/kernel-*.traceg)
(( ${#inputs[@]} > 0 )) || { echo "error: no kernel traces in $trace_dir" >&2; exit 1; }

for input in "${inputs[@]}"; do
  kernel="$(basename "$input")"
  grid="$(rg -m1 '^-grid dim = ' "$input" || true)"
  if [[ ! "$grid" =~ \(([0-9]+),([0-9]+),([0-9]+)\) ]]; then
    echo "error: cannot parse grid in $input" >&2
    exit 1
  fi
  grid_x="${BASH_REMATCH[1]}"
  grid_y="${BASH_REMATCH[2]}"
  grid_z="${BASH_REMATCH[3]}"
  source_ctas=$((grid_x * grid_y * grid_z))
  selected_ctas=$(((source_ctas + fraction - 1) / fraction))
  output="$output_dir/traces/$kernel"
  awk -v selected_ctas="$selected_ctas" -v source_ctas="$source_ctas" \
      -v fraction="$fraction" -v trim_cta_insts="$trim_cta_insts" '
    /^-grid dim = \(/ {
      print "-grid dim = (" selected_ctas ",1,1)"
      next
    }
    /^insts = / && trim_cta_insts {
      if (!match($0, /^insts = ([0-9]+)/, inst)) {
        print "error: malformed inst count" > "/dev/stderr"
        exit 2
      }
      source_insts = inst[1]
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
      if (completed_ctas < selected_ctas) {
        printf "error: requested %d CTAs but found %d\n", selected_ctas, completed_ctas > "/dev/stderr"
        exit 2
      }
    }
  ' "$input" > "$output"
  printf '%s,"(%s,%s,%s)",%s,%s,%s,%s,%s\n' "$kernel" "$grid_x" "$grid_y" "$grid_z" \
    "$selected_ctas" "$fraction" "$trim_cta_insts" "$(stat -c %s "$input")" "$(stat -c %s "$output")" >> "$manifest"
done

while IFS= read -r kernel; do
  [[ -f "$output_dir/traces/$kernel" ]] || {
    echo "error: kernelslist references missing $kernel" >&2
    exit 1
  }
done < <(rg -o 'kernel-[0-9]+\.traceg' "$output_dir/traces/kernelslist.g" | sort -u)

: > "$output_dir/.trace_fraction_complete"
printf 'PASS fraction=1/%s trim_cta_insts=%s kernels=%s output=%s manifest=%s\n' "$fraction" \
  "$trim_cta_insts" "${#inputs[@]}" "$output_dir/traces" "$manifest"
