#!/usr/bin/env bash
# Isolated recovery continuation for the Core-658 2D triplet.
# It deliberately never changes the live v2 controller or its pinned helpers.
set -euo pipefail

case "${1:-}" in
  --watch) watch=1 ;;
  --once) watch=0 ;;
  *) echo "usage: $0 --watch|--once [--poll-seconds N]" >&2; exit 2 ;;
esac
shift
poll=300
if test "${1:-}" = --poll-seconds; then poll=${2:-}; shift 2; fi
test "$#" -eq 0 && [[ "$poll" =~ ^[1-9][0-9]*$ ]] || { echo INVALID_ARGUMENTS >&2; exit 2; }

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
base_run=/workspace/fast64-stage3-tag-identity-repair-v2/fast64_3_2DConvolution_base_core6587238c_a1_v1
old_controller=2314298
summary="$repo/docs/dtc_l1/fast64/generated/fast64_3_tag_identity_repair_v2/fast64_3_2DConvolution_base_core6587238c_a1_v1.json"
v1="$repo/docs/dtc_l1/fast64/generated/fast64_3_tag_identity_repair_v2/FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V1.json"
v2="$repo/docs/dtc_l1/fast64/generated/fast64_3_tag_identity_repair_v2/FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V2.json"
registry="$repo/docs/dtc_l1/fast64/generated/FAST64_3_BASE_SOURCE_REGISTRY_V4_CORE658.tsv"
stage3_out="$repo/docs/dtc_l1/fast64/generated/fast64_3_core658_candidate_v1"
reconstruct="$repo/util/dtc_l1/reconstruct_fast64_3_2d_tag_identity_structural_v2.py"
prepare="$repo/util/dtc_l1/prepare_fast64_3_core658_registry_v1.py"
base_collect="$repo/util/dtc_l1/collect_fast64_3_base_matrix_v2.py"
dispatch="$repo/util/dtc_l1/dispatch_fast64_4_2d_tag_identity_v2.sh"
mode_collect="$repo/util/dtc_l1/collect_fast64_4_2d_tag_identity_v2.sh"
auditor="$repo/util/dtc_l1/audit_fast64_future_precompute_resources_v3.sh"
run_root=/workspace/fast64-primary-r4-tag-identity-v2
output_dir="$repo/docs/dtc_l1/fast64/generated/fast64_4_2d_tag_identity_v2"
log="$run_root/fast64_2d_tag_identity_v3.log"

emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" | tee -a "$log"; }
old_controller_live() {
  test -r "/proc/$old_controller/cmdline" || return 1
  tr '\0' ' ' < "/proc/$old_controller/cmdline" | rg -q 'auto_continue_fast64_2d_tag_identity_v2.sh'
}
run_for() { printf '%s/fast64_4_primary_2DConvolution_%s_core6587238c_a1_v1' "$run_root" "$1"; }
output_for() { printf '%s/fast64_4_primary_2DConvolution_%s_core6587238c_a1_v1.json' "$output_dir" "$1"; }
wait_or_exit() { test "$watch" = 1 || exit 0; sleep "$poll"; }

mkdir -p "$run_root"
exec 9>"$run_root/.fast64_2d_tag_identity_v3.lock"
flock -n 9 || { echo FAST64_2D_TAG_IDENTITY_V3_LOCK_HELD >&2; exit 1; }

while :; do
  if ! test -f "$summary" || ! test -f "$v1"; then
    emit FAST64_2D_TAG_IDENTITY_V3_WAIT_V2_BASE_COLLECT "run=$base_run"
    wait_or_exit
    continue
  fi
  if old_controller_live; then
    emit FAST64_2D_TAG_IDENTITY_V3_WAIT_V2_CONTROLLER_EXIT "pid=$old_controller"
    wait_or_exit
    continue
  fi
  if ! test -f "$v2"; then
    python3 "$reconstruct"
    emit FAST64_2D_TAG_IDENTITY_V3_STRUCTURAL_V2_PUBLISHED "summary=$summary structural=$v2"
  fi
  if ! test -f "$registry"; then
    python3 "$prepare" --output "$registry"
    python3 "$base_collect" --registry "$registry" --output-dir "$stage3_out"
    emit FAST64_2D_TAG_IDENTITY_V3_BASE_CANDIDATE_COLLECTED "registry=$registry output=$stage3_out"
  fi
  io=$(run_for io); oo=$(run_for oo)
  if ! test -e "$io" && ! test -e "$oo"; then
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    audit="$run_root/fast64_2d_tag_identity_v3_admission_$stamp.tsv"
    "$auditor" --output "$audit" --workers 2 --interval 10 --samples 3 --mem-reserve-gib 16
    safe=$(awk -F '\t' '$1=="safe_to_launch" {print $2; exit}' "$audit")
    cpus=$(awk -F '\t' '$1=="candidate_cpus" {print $2; exit}' "$audit")
    if test "$safe" != YES || ! test -n "$cpus"; then
      emit FAST64_2D_TAG_IDENTITY_V3_RESOURCE_WAIT "audit=$audit safe=$safe"
      wait_or_exit
      continue
    fi
    cpu_io=${cpus%%,*}; rest=${cpus#*,}; cpu_oo=${rest%%,*}
    test "$cpu_io" != "$cpus" && test "$cpu_oo" != "$rest" || { emit FAST64_2D_TAG_IDENTITY_V3_CPU_SET_INVALID "audit=$audit cpus=$cpus"; exit 1; }
    bash "$dispatch" --dispatch --mode IO --cpu "$cpu_io"
    bash "$dispatch" --dispatch --mode OO --cpu "$cpu_oo"
    emit FAST64_2D_TAG_IDENTITY_V3_MODES_DISPATCHED "io=$io oo=$oo audit=$audit"
  elif ! test -e "$io" || ! test -e "$oo"; then
    emit FAST64_2D_TAG_IDENTITY_V3_PARTIAL_NAMESPACE_REFUSE "io=$io oo=$oo"
    exit 1
  fi
  done=0
  for mode in IO OO; do
    lower=${mode,,}; run=$(run_for "$lower"); output=$(output_for "$lower")
    if test -f "$output"; then done=$((done+1)); continue; fi
    if test -f "$run/RUN_TERMINAL.tsv"; then
      bash "$mode_collect" --collect --mode "$mode"
      emit FAST64_2D_TAG_IDENTITY_V3_MODE_COLLECTED "mode=$mode output=$output"
      done=$((done+1))
    fi
  done
  if test "$done" -eq 2; then
    emit FAST64_2D_TAG_IDENTITY_V3_TRIPLET_COLLECTED "base=$summary io=$(output_for io) oo=$(output_for oo)"
    exit 0
  fi
  emit FAST64_2D_TAG_IDENTITY_V3_WAIT_IO_OO_TERMINAL "io=$io oo=$oo"
  wait_or_exit
done
