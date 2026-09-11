#!/usr/bin/env bash
# Future-only collector for the two nonformal GESUMMV/16.5-KiB f283 diagnostics.
# It reads immutable terminal output only and cannot publish a formal result.
set -euo pipefail
test "${1:-}" = --collect || { echo "usage: $0 --collect" >&2; exit 2; }

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
analyzer="$repo/util/dtc_l1/analyze_fast64_6_physical16p5_diagnostic_v1.py"
outdir="$repo/docs/dtc_l1/fast64/generated/fast64_6_diagnostics_v2"
test -r "$analyzer"

for mode in IO OO; do
  lower=${mode,,}
  run="/workspace/fast64-diagnostics/fast64_6_gesummv_physical16p5_${lower}_coref283_diag_v2"
  output="$outdir/fast64_6_gesummv_physical16p5_${lower}_coref283_diag_v2.json"
  if test -e "$output"; then
    printf 'FAST64_6_GES16P5_DIAG_V2_SKIP_PRESENT\tmode=%s\n' "$mode"
    continue
  fi
  if ! test -f "$run/RUN_TERMINAL.tsv"; then
    printf 'FAST64_6_GES16P5_DIAG_V2_WAIT_TERMINAL\tmode=%s\n' "$mode"
    continue
  fi
  status=$(awk -F '\t' '$1 == "simulator_exit_status" {print $2; exit}' "$run/RUN_TERMINAL.tsv")
  test "$status" = 1 || { printf 'FAST64_6_GES16P5_DIAG_V2_UNEXPECTED_EXIT\tmode=%s\tstatus=%s\n' "$mode" "$status" >&2; exit 1; }
  test -r "$run/simulator.stdout"
  marker="DTC_L1_${mode}_DEADLOCK"
  rg -q "^${marker} " "$run/simulator.stdout" || { printf 'FAST64_6_GES16P5_DIAG_V2_MARKER_MISSING\tmode=%s\n' "$mode" >&2; exit 1; }
  mkdir -p "$outdir"
  test ! -e "$output"
  python3 "$analyzer" --input "$run/simulator.stdout" --mode "$mode" --output "$output"
  jq -e --arg mode "$mode" '.classification == "NONFORMAL_DIAGNOSTIC_NOT_RESULT" and .mode == $mode and (.resource_state | length > 0)' "$output" >/dev/null
  printf 'FAST64_6_GES16P5_DIAG_V2_PUBLISHED\tmode=%s\toutput=%s\n' "$mode" "$output"
done
