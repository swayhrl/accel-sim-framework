#!/usr/bin/env bash
# Future-only, fail-closed continuation for the Core-41 2DConvolution triplet.
# It never touches a live simulator.  It can dispatch only the two missing
# primary rows after the exact Core-41 Base strict and structural artifacts
# exist, a new two-worker admission audit passes, and pinned helpers match.
set -euo pipefail

usage() {
  echo "usage: $0 --once|--watch [--poll-seconds N] [--log FILE]" >&2
  exit 2
}

case "${1:-}" in
  --once) watch=0; shift ;;
  --watch) watch=1; shift ;;
  *) usage ;;
esac
poll=120
log=/workspace/fast64-primary-r4/fast64_4_2d_core41_autodispatch_v1.log
while [ "$#" -gt 0 ]; do
  case "$1" in
    --poll-seconds) poll=${2:-}; shift 2 ;;
    --log) log=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
[[ "$poll" =~ ^[1-9][0-9]*$ ]] || usage

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
dispatcher="$repo/util/dtc_l1/dispatch_fast64_4_2d_core41_v1.sh"
monitor="$repo/util/dtc_l1/monitor_fast64_repaired_core_row_v2.sh"
auditor="$repo/util/dtc_l1/audit_fast64_future_precompute_resources_v3.sh"
dispatcher_sha=e26f090f076f7929d4933aad743964c757ddabfa0514858768e365add286b441
monitor_sha=266a489c246512d5d321d77c2ef6e10794b0b0deb4e6aa7bb9bd2ee3f37b67ff
auditor_sha=2a806549ebbe1870609f03fab396a4b78f01945091683f7cfa93e2f447470355
base="$repo/docs/dtc_l1/fast64/generated/fast64_3_repair_v1/fast64_3_2DConvolution_base_core41d740e8_a1_v1.json"
structural="$repo/docs/dtc_l1/fast64/generated/fast64_3_repair_v1/FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V1.json"
generated="$repo/docs/dtc_l1/fast64/generated/fast64_4_primary_core41_v1"
runs=/workspace/fast64-primary-r4
core=41d740e862a6ad89ab0fc32b7b927ec787752862
runtime=6e72d36665cde18e2845914ee9c2a9f2e65b37b7b3c216edf4b676ad17e2c21c
framework=037f008b330eb230353b60edf126d6be9f45afdc
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
classification=PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE

mkdir -p "$runs" "$(dirname "$log")"
exec 9>"$runs/.fast64_4_2d_core41_autodispatch_v1.lock"
flock -n 9 || { echo FAST64_4_2D_CORE41_AUTODISPATCH_ALREADY_ACTIVE >&2; exit 1; }
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" | tee -a "$log"; }
sha_ok() { test -r "$1" && test "$(sha256sum "$1" | awk '{print $1}')" = "$2"; }

helpers_ok() {
  sha_ok "$dispatcher" "$dispatcher_sha" && sha_ok "$monitor" "$monitor_sha" && sha_ok "$auditor" "$auditor_sha"
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
    .schema == "FAST64_3_BASE_STRUCTURAL_METRICS_V1" and
    .classification == "PRECOMPUTED_STRUCTURAL_METRIC_COMPANION_NOT_FAST64_3_PASS" and
    .source_summary == $base and .metrics.terminal_lower_outstanding == 0 and
    .metrics.terminal_pib_occupancy == 0
  ' "$structural" >/dev/null
}

start_monitor() {
  local mode=$1 lower=$2 config=$3 config_id=$4 run="$runs/fast64_4_primary_2dconvolution_${lower}_core41d740e8_a1_v1"
  local output="$generated/fast64_4_primary_2dconvolution_${lower}_core41d740e8_a1_v1.json"
  local monitor_log="$runs/fast64_4_primary_2dconvolution_${lower}_core41d740e8_a1_v1.closeout.log"
  local pidfile="$runs/fast64_4_primary_2dconvolution_${lower}_core41d740e8_a1_v1.closeout.pid"
  test -d "$run" || { emit FAST64_4_2D_CORE41_MONITOR_RUN_MISSING "mode=$mode run=$run"; exit 1; }
  test ! -e "$output" || { emit FAST64_4_2D_CORE41_MONITOR_OUTPUT_EXISTS "mode=$mode output=$output"; return; }
  if test -f "$pidfile" && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
    emit FAST64_4_2D_CORE41_MONITOR_ALREADY_LIVE "mode=$mode pid=$(cat "$pidfile")"
    return
  fi
  (
    exec setsid bash "$monitor" --run-dir "$run" --workload-id 2DConvolution --mode "$mode" \
      --config-id "$config_id" --config-file "$config" --core-sha "$core" --runtime-sha "$runtime" \
      --classification "$classification" --output "$output" --log "$monitor_log" --poll-seconds 120
  ) >>"$monitor_log" 2>&1 &
  local pid=$!
  printf '%s\n' "$pid" > "$pidfile"
  emit FAST64_4_2D_CORE41_MONITOR_STARTED "mode=$mode pid=$pid output=$output"
}

while :; do
  helpers_ok || { emit FAST64_4_2D_CORE41_HELPER_HASH_MISMATCH "dispatcher=$dispatcher monitor=$monitor auditor=$auditor"; exit 1; }
  if ! base_ready; then
    emit FAST64_4_2D_CORE41_WAIT_BASE_STRICT_GATE "base=$base structural=$structural"
    test "$watch" = 1 || exit 0
    sleep "$poll"
    continue
  fi

  stamp=$(date -u +%Y%m%dT%H%M%SZ)
  audit="$runs/fast64_4_2d_core41_admission_$stamp.tsv"
  if ! "$auditor" --output "$audit" --workers 2 --interval 10 --samples 3 --mem-reserve-gib 16; then
    emit FAST64_4_2D_CORE41_RESOURCE_AUDIT_TOOL_FAILURE "audit=$audit"
    test "$watch" = 1 || exit 1
    sleep "$poll"
    continue
  fi
  safe=$(awk -F '\t' '$1=="safe_to_launch" {print $2; exit}' "$audit")
  admitted=$(awk -F '\t' '$1=="authorized_workers" {print $2; exit}' "$audit")
  cpus=$(awk -F '\t' '$1=="candidate_cpus" {print $2; exit}' "$audit")
  if test "$safe" != YES || test "$admitted" -lt 2 || ! [[ ",$cpus," == *,36,* && ",$cpus," == *,37,* ]]; then
    emit FAST64_4_2D_CORE41_RESOURCE_WAIT "audit=$audit safe=$safe admitted=$admitted"
    test "$watch" = 1 || exit 0
    sleep "$poll"
    continue
  fi

  io_run="$runs/fast64_4_primary_2dconvolution_io_core41d740e8_a1_v1"
  oo_run="$runs/fast64_4_primary_2dconvolution_oo_core41d740e8_a1_v1"
  if ! test -e "$io_run"; then
    bash "$dispatcher" --dispatch --mode IO --cpu 36
    emit FAST64_4_2D_CORE41_IO_DISPATCHED "run=$io_run audit=$audit cpu=36"
  fi
  start_monitor IO io "$repo/configs/dtc_l1/fast64/FAST64_IO.config" FAST64_IO_A1
  if ! test -e "$oo_run"; then
    bash "$dispatcher" --dispatch --mode OO --cpu 37
    emit FAST64_4_2D_CORE41_OO_DISPATCHED "run=$oo_run audit=$audit cpu=37"
  fi
  start_monitor OO oo "$repo/configs/dtc_l1/fast64/FAST64_OO.config" FAST64_OO_A1
  emit FAST64_4_2D_CORE41_DISPATCH_AND_CLOSEOUT_ARMED "audit=$audit"
  exit 0
done
