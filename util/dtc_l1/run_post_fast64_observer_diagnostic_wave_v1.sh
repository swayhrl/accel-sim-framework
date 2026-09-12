#!/usr/bin/env bash
# Launch the reviewed Lane-D D4/D5 observer-only diagnostic rows once.
set -euo pipefail

usage() {
  echo "usage: $0 --root DIR --framework DIR --sim95 PATH --sim658 PATH --core95 SHA --core658 SHA --trace-config PATH" >&2
  exit 2
}

root= framework= sim95= sim658= core95= core658= trace_config=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --root) root=${2:-}; shift 2 ;;
    --framework) framework=${2:-}; shift 2 ;;
    --sim95) sim95=${2:-}; shift 2 ;;
    --sim658) sim658=${2:-}; shift 2 ;;
    --core95) core95=${2:-}; shift 2 ;;
    --core658) core658=${2:-}; shift 2 ;;
    --trace-config) trace_config=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
test -n "$root" && test ! -e "$root" && test -d "$framework" && test -x "$sim95" && \
  test -x "$sim658" && test -n "$core95" && test -n "$core658" && test -r "$trace_config" || usage

self_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
runner="$self_dir/run_post_fast64_observer_d3b_v1.sh"
test -x "$runner"
registry="$framework/docs/dtc_l1/fast64/generated/FAST64_4_CAP_RESOLVED_PRIMARY_REGISTRY_V1.tsv"
numeric="$framework/docs/dtc_l1/fast64/generated/FAST64_6_NUMERIC_REGISTRY_V1.tsv"
test -r "$registry" && test -r "$numeric"
mkdir -- "$root"
plan="$root/WAVE_PLAN.tsv"
printf 'wave\tworkload\tdimension\tpoint\tmode\taccepted_summary\tconfig\tconfig_sha256\ttrace_list\ttrace_list_sha256\tsimulator\tcore_sha\tcpu\trun_directory\n' >"$plan"

config_for_id() {
  case "$1" in
    FAST64_OO_A1) printf '%s\n' "$framework/configs/dtc_l1/fast64/FAST64_OO.config" ;;
    FAST64_OO_CAP16384_A1) printf '%s\n' "$framework/configs/dtc_l1/fast64/FAST64_OO_CAP16384.config" ;;
    FAST64_OO_CAP32768_A1) printf '%s\n' "$framework/configs/dtc_l1/fast64/FAST64_OO_CAP32768.config" ;;
    FAST64_SENS_PHYSICAL_24KB_IO) printf '%s\n' "$framework/configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_24/FAST64_SENS_PHYSICAL_24KB_IO.config" ;;
    FAST64_SENS_PHYSICAL_24KB_OO) printf '%s\n' "$framework/configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_24/FAST64_SENS_PHYSICAL_24KB_OO.config" ;;
    FAST64_SENS_PHYSICAL_32KB_IO) printf '%s\n' "$framework/configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_32/FAST64_SENS_PHYSICAL_32KB_IO.config" ;;
    FAST64_SENS_PHYSICAL_32KB_OO) printf '%s\n' "$framework/configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_32/FAST64_SENS_PHYSICAL_32KB_OO.config" ;;
    FAST64_SENS_PHYSICAL_48KB_IO) printf '%s\n' "$framework/configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_48/FAST64_SENS_PHYSICAL_48KB_IO.config" ;;
    FAST64_SENS_PHYSICAL_48KB_OO) printf '%s\n' "$framework/configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_48/FAST64_SENS_PHYSICAL_48KB_OO.config" ;;
    *) echo "unknown frozen config id: $1" >&2; return 2 ;;
  esac
}

pids=()
launch() {
  local wave=$1 workload=$2 dimension=$3 point=$4 mode=$5 summary=$6 cpu=$7
  local config_id config_sha trace trace_sha config sim core run
  config_id=$(jq -r '.provenance.config_id' "$summary")
  config_sha=$(jq -r '.provenance.config_sha256' "$summary")
  trace=$(jq -r '.external_artifacts.trace_list' "$summary")
  trace_sha=$(jq -r '.external_artifacts.trace_list_sha256' "$summary")
  test "$workload" = "$(jq -r '.provenance.workload_id' "$summary")"
  config=$(config_for_id "$config_id")
  test -r "$config" && test -r "$trace"
  test "$config_sha" = "$(sha256sum "$config" | awk '{print $1}')"
  test "$trace_sha" = "$(sha256sum "$trace" | awk '{print $1}')"
  if [ "$workload" = "2DConvolution" ]; then sim=$sim658; core=$core658; else sim=$sim95; core=$core95; fi
  run="$root/${wave,,}_${workload,,}_${dimension}${point}_${mode,,}"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$wave" "$workload" "$dimension" "$point" "$mode" "$summary" "$config" "$config_sha" "$trace" "$trace_sha" "$sim" "$core" "$cpu" "$run" >>"$plan"
  "$runner" --simulator "$sim" --core-sha "$core" --config "$config" --trace "$trace" \
    --trace-config "$trace_config" --run-dir "$run" --workload "$workload" --mode "$mode" --observer 1 --cpu "$cpu" &
  pids+=("$!")
}

cpu=220
while IFS=$'\t' read -r workload dimension point mode summary origin; do
  [ "$workload" = "workload" ] && continue
  case "$workload:$dimension:$point" in
    BICG:physical:24|BICG:physical:32|BICG:physical:48|GESUMMV:physical:24|GESUMMV:physical:32|GESUMMV:physical:48|Btree:physical:24|Btree:physical:32|Btree:physical:48)
      launch D4 "$workload" "$dimension" "$point" "$mode" "$framework/$summary" "$cpu"
      cpu=$((cpu + 1))
      ;;
  esac
done <"$numeric"

while IFS=$'\t' read -r workload mode summary origin cap retry; do
  [ "$workload" = "workload" ] && continue
  [ "$mode" = "OO" ] || continue
  # The exact Btree OO primary is retained from D3B; it is not re-launched.
  [ "$workload" = "Btree" ] && continue
  launch D5 "$workload" primary primary "$mode" "$framework/$summary" "$cpu"
  cpu=$((cpu + 1))
done <"$registry"

chmod 444 "$plan"
status=0
for pid in "${pids[@]}"; do
  if ! wait "$pid"; then status=1; fi
done
printf 'POST_FAST64_OBSERVER_DIAGNOSTIC_WAVE_TERMINAL\troot=%s\trows=%s\tstatus=%s\n' "$root" "${#pids[@]}" "$status"
exit "$status"
