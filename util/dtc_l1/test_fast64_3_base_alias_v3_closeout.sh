#!/usr/bin/env bash
# Static/pre-terminal regression; it cannot launch or collect a simulator row.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
collector="$repo/util/dtc_l1/collect_fast64_3_base_alias_v3.sh"
monitor="$repo/util/dtc_l1/monitor_fast64_3_base_alias_v3_closeout.sh"
log=$(mktemp /tmp/fast64-3-base-alias-v3-test.XXXXXX)

bash -n "$collector" "$monitor"
rg -q 'deadlock detected' "$collector"
! rg -q "'assert\|fatal\|deadlock\|output mismatch" "$collector"
for workload in atax gesummv dwt2d; do
  test ! -e "$repo/docs/dtc_l1/fast64/generated/fast64_3_${workload}_base_alias_v3"
done
"$monitor" --log "$log" --once
rg -q 'FAST64_3_BASE_ALIAS_V3_WAIT_TERMINAL' "$log"
for workload in atax gesummv dwt2d; do
  test ! -e "$repo/docs/dtc_l1/fast64/generated/fast64_3_${workload}_base_alias_v3"
done
printf 'FAST64_3_BASE_ALIAS_V3_CLOSEOUT_STATIC_REGRESSION_PASS\n'
