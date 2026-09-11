#!/usr/bin/env bash
# Immutable future-only continuation for the Core-658 2D triplet.  It watches
# but never signals a simulator; all acquisitions remain resource-gated.
set -euo pipefail

usage() { echo "usage: $0 --once|--watch [--poll-seconds N] [--log FILE]" >&2; exit 2; }
case "${1:-}" in
  --once) watch=0; shift ;;
  --watch) watch=1; shift ;;
  *) usage ;;
esac
poll=180
log=/workspace/fast64-primary-r4-tag-identity-v2/fast64_2d_tag_identity_v2.log
while [ "$#" -gt 0 ]; do
  case "$1" in
    --poll-seconds) poll=${2:-}; shift 2 ;;
    --log) log=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
[[ "$poll" =~ ^[1-9][0-9]*$ ]] || usage

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
base_collect="$repo/util/dtc_l1/collect_fast64_3_2d_base_tag_identity_v2.sh"
dispatch="$repo/util/dtc_l1/dispatch_fast64_4_2d_tag_identity_v2.sh"
mode_collect="$repo/util/dtc_l1/collect_fast64_4_2d_tag_identity_v2.sh"
auditor="$repo/util/dtc_l1/audit_fast64_future_precompute_resources_v3.sh"
base_collect_sha=dd0a5ffeeccf81d61b0bc6f1cc1d6ca2e87f6c618738312e83dc1785a42eb1e1
dispatch_sha=f70753e9532a70800677785f72a5cb2fd2fbdce5dfaf1a855976df26142a2848
mode_collect_sha=376227b695c4e25936b4b6e1bf68530794af90800015f8617daab8fc4dd0b139
auditor_sha=2a806549ebbe1870609f03fab396a4b78f01945091683f7cfa93e2f447470355
base_run=/workspace/fast64-stage3-tag-identity-repair-v2/fast64_3_2DConvolution_base_core6587238c_a1_v1
base="$repo/docs/dtc_l1/fast64/generated/fast64_3_tag_identity_repair_v2/fast64_3_2DConvolution_base_core6587238c_a1_v1.json"
structural="$repo/docs/dtc_l1/fast64/generated/fast64_3_tag_identity_repair_v2/FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V1.json"
run_root=/workspace/fast64-primary-r4-tag-identity-v2
output_dir="$repo/docs/dtc_l1/fast64/generated/fast64_4_2d_tag_identity_v2"
core=6587238c60214d99491f4048e28ce8a3458c1509
runtime=29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1
framework=037f008b330eb230353b60edf126d6be9f45afdc
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e

mkdir -p "$run_root" "$(dirname "$log")"
exec 9>"$run_root/.fast64_2d_tag_identity_v2.lock"
flock -n 9 || { echo FAST64_2D_TAG_IDENTITY_V2_CONTROLLER_ALREADY_ACTIVE >&2; exit 1; }
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" | tee -a "$log"; }
sha_ok() { test -r "$1" && test "$(sha256sum "$1" | awk '{print $1}')" = "$2"; }
helpers_ok() {
  sha_ok "$base_collect" "$base_collect_sha" && sha_ok "$dispatch" "$dispatch_sha" &&
  sha_ok "$mode_collect" "$mode_collect_sha" && sha_ok "$auditor" "$auditor_sha"
}
base_ready() {
  test -f "$base" && test -f "$structural" || return 1
  jq -e --arg core "$core" --arg runtime "$runtime" --arg framework "$framework" --arg observer "$observer" '
    .provenance.workload_id == "2DConvolution" and .provenance.config_id == "FAST64_BASE_A1" and
    .provenance.core_sha == $core and .provenance.runtime_binary_sha256 == $runtime and
    .provenance.framework_sha == $framework and .provenance.observer_overlay_sha256 == $observer and
    .provenance.result_classification == "PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE"
  ' "$base" >/dev/null &&
  jq -e --arg base "$base" '
    .schema == "FAST64_3_BASE_STRUCTURAL_METRICS_V1" and .source_summary == $base and
    .metrics.terminal_lower_outstanding == 0 and .metrics.terminal_pib_occupancy == 0
  ' "$structural" >/dev/null
}
terminal() { test -f "$1/RUN_TERMINAL.tsv"; }
output_for() { printf '%s/fast64_4_primary_2DConvolution_%s_core6587238c_a1_v1.json' "$output_dir" "$1"; }
run_for() { printf '%s/fast64_4_primary_2DConvolution_%s_core6587238c_a1_v1' "$run_root" "$1"; }

while :; do
  helpers_ok || { emit FAST64_2D_TAG_IDENTITY_V2_HELPER_HASH_MISMATCH "base_collect=$base_collect dispatch=$dispatch mode_collect=$mode_collect auditor=$auditor"; exit 1; }
  if ! base_ready; then
    if terminal "$base_run"; then
      "$base_collect" --collect
      emit FAST64_2D_TAG_IDENTITY_V2_BASE_COLLECTED "base=$base structural=$structural"
      continue
    fi
    emit FAST64_2D_TAG_IDENTITY_V2_WAIT_BASE_TERMINAL "run=$base_run"
    test "$watch" = 1 || exit 0
    sleep "$poll"
    continue
  fi

  io_run=$(run_for io); oo_run=$(run_for oo)
  if ! test -e "$io_run" || ! test -e "$oo_run"; then
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    audit="$run_root/fast64_2d_tag_identity_v2_admission_$stamp.tsv"
    "$auditor" --output "$audit" --workers 2 --interval 10 --samples 3 --mem-reserve-gib 16
    safe=$(awk -F '\t' '$1=="safe_to_launch" {print $2; exit}' "$audit")
    admitted=$(awk -F '\t' '$1=="authorized_workers" {print $2; exit}' "$audit")
    cpus=$(awk -F '\t' '$1=="candidate_cpus" {print $2; exit}' "$audit")
    IFS=, read -r cpu_io cpu_oo _ <<<"$cpus"
    if test "$safe" != YES || test "$admitted" -lt 2 || ! [[ "$cpu_io" =~ ^[0-9]+$ && "$cpu_oo" =~ ^[0-9]+$ ]] || test "$cpu_io" = "$cpu_oo"; then
      emit FAST64_2D_TAG_IDENTITY_V2_RESOURCE_WAIT "audit=$audit safe=$safe admitted=$admitted cpus=$cpus"
      test "$watch" = 1 || exit 0
      sleep "$poll"
      continue
    fi
    if ! test -e "$io_run"; then
      bash "$dispatch" --dispatch --mode IO --cpu "$cpu_io"
      emit FAST64_2D_TAG_IDENTITY_V2_IO_DISPATCHED "run=$io_run audit=$audit cpu=$cpu_io"
    fi
    if ! test -e "$oo_run"; then
      bash "$dispatch" --dispatch --mode OO --cpu "$cpu_oo"
      emit FAST64_2D_TAG_IDENTITY_V2_OO_DISPATCHED "run=$oo_run audit=$audit cpu=$cpu_oo"
    fi
  fi

  done=0
  for mode in IO OO; do
    lower=${mode,,}; run=$(run_for "$lower"); output=$(output_for "$lower")
    if test -f "$output"; then done=$((done+1)); continue; fi
    if terminal "$run"; then
      "$mode_collect" --collect --mode "$mode"
      emit FAST64_2D_TAG_IDENTITY_V2_MODE_COLLECTED "mode=$mode output=$output"
      done=$((done+1))
    fi
  done
  if test "$done" -eq 2; then emit FAST64_2D_TAG_IDENTITY_V2_TRIPLET_COLLECTED "base=$base io=$(output_for io) oo=$(output_for oo)"; exit 0; fi
  emit FAST64_2D_TAG_IDENTITY_V2_WAIT_IO_OO_TERMINAL "io=$io_run oo=$oo_run"
  test "$watch" = 1 || exit 0
  sleep "$poll"
done
