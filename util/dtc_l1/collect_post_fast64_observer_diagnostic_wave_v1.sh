#!/usr/bin/env bash
# Compact natural-terminal D4/D5 rows and retain no raw simulator blobs in Git.
set -euo pipefail

usage() {
  echo "usage: $0 --root DIR --framework DIR --d3b-btree-oo DIR --output-d4 TSV --output-d5 TSV --output-index TSV" >&2
  exit 2
}

root= framework= d3b_btree_oo= output_d4= output_d5= output_index=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --root) root=${2:-}; shift 2 ;;
    --framework) framework=${2:-}; shift 2 ;;
    --d3b-btree-oo) d3b_btree_oo=${2:-}; shift 2 ;;
    --output-d4) output_d4=${2:-}; shift 2 ;;
    --output-d5) output_d5=${2:-}; shift 2 ;;
    --output-index) output_index=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
test -d "$root" && test -d "$framework" && test -d "$d3b_btree_oo" && \
  test -n "$output_d4" && test -n "$output_d5" && test -n "$output_index" || usage
test ! -e "$output_d4" && test ! -e "$output_d5" && test ! -e "$output_index" || {
  echo "refusing to overwrite a committed diagnostic table" >&2; exit 2; }

self_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
collector="$self_dir/collect_post_fast64_observer_diagnostic_v1.py"
materializer="$self_dir/materialize_post_fast64_observer_wave_v1.py"
plan="$root/WAVE_PLAN.tsv"
compact="$root/compact"
test -x "$collector" && test -x "$materializer" && test -r "$plan" && test ! -e "$compact"
mkdir -- "$compact"

while IFS=$'\t' read -r wave workload dimension point mode summary config config_sha trace trace_sha simulator core_sha cpu run; do
  [ "$wave" = "wave" ] && continue
  case "$wave" in D4|D5) ;; *) echo "invalid wave in plan: $wave" >&2; exit 2 ;; esac
  test -d "$run"
  python3 "$collector" --run "$run" --accepted-summary "$summary" \
    --expected-core-sha "$core_sha" --wave "$wave" \
    --output "$compact/$(basename "$run").tsv"
done <"$plan"

btree_summary=$(awk -F '\t' '$1=="Btree" && $2=="OO" {print $3}' \
  "$framework/docs/dtc_l1/fast64/generated/FAST64_4_CAP_RESOLVED_PRIMARY_REGISTRY_V1.tsv")
test -n "$btree_summary"
python3 "$collector" --run "$d3b_btree_oo" \
  --accepted-summary "$framework/$btree_summary" \
  --expected-core-sha 2fcde3eb3fce1502cc0f910cad6f807e530018c5 --wave D5 \
  --output "$compact/d5_btree_d3b_exact_reuse.tsv"

python3 "$materializer" --plan "$plan" --compact-dir "$compact" \
  --reuse-row "$compact/d5_btree_d3b_exact_reuse.tsv" \
  --output-d4 "$output_d4" --output-d5 "$output_d5" --output-index "$output_index"
