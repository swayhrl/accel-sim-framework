#!/usr/bin/env bash
# Materialize one frozen FAST64 sensitivity family only after FAST64.2 PASS.
# --plan-only is read-only and may be used before that gate to audit mappings.
set -euo pipefail

usage() {
  echo "usage: $0 --family logical|physical|pib --point VALUE --output-dir PATH [--plan-only]" >&2
  exit 2
}

family= point= output_dir= plan_only=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --family) family=${2:-}; shift 2 ;;
    --point) point=${2:-}; shift 2 ;;
    --output-dir) output_dir=${2:-}; shift 2 ;;
    --plan-only) plan_only=1; shift ;;
    *) usage ;;
  esac
done
test -n "$family" && test -n "$point" && test -n "$output_dir" || usage

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
config_root="$repo_root/configs/dtc_l1/fast64"
pass_artifact="$repo_root/docs/dtc_l1/fast64/handoffs/FAST64_2_REPAIR_QUALIFICATION.md"

case "$family" in
  logical)
    case "$point" in
      16) sets=32; label=16KB ;;
      32) sets=64; label=32KB ;;
      64) sets=128; label=64KB ;;
      *) echo "logical point must be 16, 32, or 64 KiB" >&2; exit 2 ;;
    esac
    modes=(BASE IO OO)
    ;;
  physical)
    case "$point" in
      16.5) lines=132; label=16p5KB ;;
      24) lines=192; label=24KB ;;
      32) lines=256; label=32KB ;;
      40) lines=320; label=40KB ;;
      48) lines=384; label=48KB ;;
      *) echo "physical point must be 16.5, 24, 32, 40, or 48 KiB" >&2; exit 2 ;;
    esac
    modes=(IO OO)
    ;;
  pib)
    case "$point" in
      32|64|128|192|256) entries=$point; label=${point}ENTRIES ;;
      *) echo "PIB point must be 32, 64, 128, 192, or 256 entries" >&2; exit 2 ;;
    esac
    modes=(IO OO)
    ;;
  *) usage ;;
esac

for mode in "${modes[@]}"; do
  input="$config_root/FAST64_${mode}.config"
  test -r "$input"
  printf 'PLAN\tfamily=%s\tpoint=%s\tmode=%s\tinput=%s\toutput=%s\n' \
    "$family" "$point" "$mode" "$input" \
    "$output_dir/FAST64_SENS_${family^^}_${label}_${mode}.config"
done

if [ "$plan_only" = 1 ]; then exit 0; fi
test -f "$pass_artifact" && grep -Fxq 'Status: **FAST64_2_REPAIR_PASS**' "$pass_artifact" || {
  echo "FAST64.2 repair PASS required before sensitivity config materialization" >&2; exit 1;
}
test ! -e "$output_dir" || { echo "output directory already exists: $output_dir" >&2; exit 1; }
mkdir -p "$output_dir"

for mode in "${modes[@]}"; do
  input="$config_root/FAST64_${mode}.config"
  output="$output_dir/FAST64_SENS_${family^^}_${label}_${mode}.config"
  case "$family" in
    logical)
      test "$(grep -Fxc -- '-gpgpu_dtc_l1_logical_sets 32' "$input")" = 1
      if [ "$mode" = BASE ]; then
        test "$(grep -Ecx -- '^-gpgpu_cache:dl1[[:space:]]+S:32:128:4,L:T:m:L:L,A:512:8,16:0,32$' "$input")" = 1
        test "$(grep -Ecx -- '^-gpgpu_cache:dl1PrefL1[[:space:]]+S:32:128:4,L:T:m:L:L,A:512:8,16:0,32$' "$input")" = 1
        test "$(grep -Ecx -- '^-gpgpu_cache:dl1PrefShared[[:space:]]+S:32:128:4,L:T:m:L:L,A:512:8,16:0,32$' "$input")" = 1
        sed -e "s/-gpgpu_dtc_l1_logical_sets 32/-gpgpu_dtc_l1_logical_sets $sets/" \
            -e "s/S:32:128:4,L:T:m:L:L,A:512:8,16:0,32/S:$sets:128:4,L:T:m:L:L,A:512:8,16:0,32/g" \
            "$input" >"$output"
      else
        sed "s/-gpgpu_dtc_l1_logical_sets 32/-gpgpu_dtc_l1_logical_sets $sets/" "$input" >"$output"
      fi
      test "$(grep -Fxc -- "-gpgpu_dtc_l1_logical_sets $sets" "$output")" = 1
      ;;
    physical)
      test "$(grep -Fxc -- '-gpgpu_dtc_l1_physical_lines 640' "$input")" = 1
      sed "s/-gpgpu_dtc_l1_physical_lines 640/-gpgpu_dtc_l1_physical_lines $lines/" "$input" >"$output"
      test "$(grep -Fxc -- "-gpgpu_dtc_l1_physical_lines $lines" "$output")" = 1
      ;;
    pib)
      key="-gpgpu_dtc_l1_${mode,,}_pib_entries"
      default=256
      [ "$mode" = OO ] && default=128
      test "$(grep -Fxc -- "$key $default" "$input")" = 1
      sed "s/$key $default/$key $entries/" "$input" >"$output"
      test "$(grep -Fxc -- "$key $entries" "$output")" = 1
      ;;
  esac
  test "$(grep -F -- '-gpgpu_dtc_l1_lower_outstanding_cap ' "$output" | tail -1)" = \
    '-gpgpu_dtc_l1_lower_outstanding_cap 8192'
done
printf 'MATERIALIZED_FAST64_SENSITIVITY family=%s point=%s output_dir=%s\n' \
  "$family" "$point" "$output_dir"
