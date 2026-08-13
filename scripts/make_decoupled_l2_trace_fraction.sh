#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/make_decoupled_l2_trace_fraction.sh --trace-dir DIR --output-dir DIR
       --fraction N

Create an independent trace view that replays approximately 1/N of each
kernel's CTAs.  The source trace is never changed.  Every generated kernel
retains a complete header and complete CTA records through the selected final
#END_TB, then advertises a matching one-dimensional grid.  This is suited to
functional/protocol smoke experiments, not performance comparison.
EOF
}

trace_dir=""
output_dir=""
fraction=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace-dir) trace_dir="$2"; shift 2 ;;
    --output-dir) output_dir="$2"; shift 2 ;;
    --fraction) fraction="$2"; shift 2 ;;
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
printf 'kernel,source_grid,selected_ctas,fraction,source_bytes,output_bytes\n' > "$manifest"
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
  awk -v selected_ctas="$selected_ctas" '
    /^-grid dim = \(/ {
      print "-grid dim = (" selected_ctas ",1,1)"
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
  printf '%s,"(%s,%s,%s)",%s,%s,%s,%s\n' "$kernel" "$grid_x" "$grid_y" "$grid_z" \
    "$selected_ctas" "$fraction" "$(stat -c %s "$input")" "$(stat -c %s "$output")" >> "$manifest"
done

while IFS= read -r kernel; do
  [[ -f "$output_dir/traces/$kernel" ]] || {
    echo "error: kernelslist references missing $kernel" >&2
    exit 1
  }
done < <(rg -o 'kernel-[0-9]+\.traceg' "$output_dir/traces/kernelslist.g" | sort -u)

: > "$output_dir/.trace_fraction_complete"
printf 'PASS fraction=1/%s kernels=%s output=%s manifest=%s\n' "$fraction" \
  "${#inputs[@]}" "$output_dir/traces" "$manifest"
