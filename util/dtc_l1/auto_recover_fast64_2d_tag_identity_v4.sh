#!/usr/bin/env bash
# Future-only recovery after V3's obsolete V1-structural dispatcher refusal.
# It never modifies the V2/V3 controllers or their evidence.  It dispatches
# the Core-658 2D IO/OO pair only after the V2 structural companion and a
# fresh resource audit pass, then delegates strict terminal collection to the
# frozen V2 collector.
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
base="$repo/docs/dtc_l1/fast64/generated/fast64_3_tag_identity_repair_v2/fast64_3_2DConvolution_base_core6587238c_a1_v1.json"
structural="$repo/docs/dtc_l1/fast64/generated/fast64_3_tag_identity_repair_v2/FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V2.json"
dispatch="$repo/util/dtc_l1/dispatch_fast64_4_2d_tag_identity_v3.sh"
collect="$repo/util/dtc_l1/collect_fast64_4_2d_tag_identity_v2.sh"
auditor="$repo/util/dtc_l1/audit_fast64_future_precompute_resources_v3.sh"
run_root=/workspace/fast64-primary-r4-tag-identity-v2
log="$run_root/fast64_2d_tag_identity_v4.log"
run_for() { printf '%s/fast64_4_primary_2DConvolution_%s_core6587238c_a1_v1' "$run_root" "$1"; }
out_for() { printf '%s/docs/dtc_l1/fast64/generated/fast64_4_2d_tag_identity_v2/fast64_4_primary_2DConvolution_%s_core6587238c_a1_v1.json' "$repo" "$1"; }
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" | tee -a "$log"; }
wait_or_exit() { test "$watch" = 1 || exit 0; sleep "$poll"; }

mkdir -p "$run_root"
exec 9>"$run_root/.fast64_2d_tag_identity_v4.lock"
flock -n 9 || { echo FAST64_2D_TAG_IDENTITY_V4_LOCK_HELD >&2; exit 1; }

while :; do
  test -f "$base" && test -f "$structural" || { emit FAST64_2D_TAG_IDENTITY_V4_BASE_GATE_WAIT "base=$base structural=$structural"; wait_or_exit; continue; }
  io=$(run_for io); oo=$(run_for oo)
  if ! test -e "$io" && ! test -e "$oo"; then
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    audit="$run_root/fast64_2d_tag_identity_v4_admission_$stamp.tsv"
    "$auditor" --output "$audit" --workers 2 --interval 10 --samples 3 --mem-reserve-gib 16
    safe=$(awk -F '\t' '$1=="safe_to_launch" {print $2; exit}' "$audit")
    cpus=$(awk -F '\t' '$1=="candidate_cpus" {print $2; exit}' "$audit")
    if test "$safe" != YES || ! test -n "$cpus"; then emit FAST64_2D_TAG_IDENTITY_V4_RESOURCE_WAIT "audit=$audit safe=$safe"; wait_or_exit; continue; fi
    cpu_io=${cpus%%,*}; rest=${cpus#*,}; cpu_oo=${rest%%,*}
    test "$cpu_io" != "$cpus" && test "$cpu_oo" != "$rest" || { emit FAST64_2D_TAG_IDENTITY_V4_CPU_SET_INVALID "audit=$audit cpus=$cpus"; exit 1; }
    bash "$dispatch" --dispatch --mode IO --cpu "$cpu_io"
    bash "$dispatch" --dispatch --mode OO --cpu "$cpu_oo"
    emit FAST64_2D_TAG_IDENTITY_V4_MODES_DISPATCHED "io=$io oo=$oo audit=$audit"
  elif ! test -e "$io" || ! test -e "$oo"; then
    emit FAST64_2D_TAG_IDENTITY_V4_PARTIAL_NAMESPACE_REFUSE "io=$io oo=$oo"
    exit 1
  fi
  done=0
  for mode in IO OO; do
    lower=${mode,,}; run=$(run_for "$lower"); output=$(out_for "$lower")
    if test -f "$output"; then done=$((done+1)); continue; fi
    if test -f "$run/RUN_TERMINAL.tsv"; then
      bash "$collect" --collect --mode "$mode"
      emit FAST64_2D_TAG_IDENTITY_V4_MODE_COLLECTED "mode=$mode output=$output"
      done=$((done+1))
    fi
  done
  if test "$done" -eq 2; then emit FAST64_2D_TAG_IDENTITY_V4_TRIPLET_COLLECTED "base=$base io=$(out_for io) oo=$(out_for oo)"; exit 0; fi
  emit FAST64_2D_TAG_IDENTITY_V4_WAIT_IO_OO_TERMINAL "io=$io oo=$oo"
  wait_or_exit
done
