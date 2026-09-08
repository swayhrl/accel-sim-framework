#!/usr/bin/env bash
# Static/once regression: existing DWT companion is preserved; no live row is
# collected, signalled, or launched.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
monitor="$repo/util/dtc_l1/monitor_fast64_3_base_structural_companion_v1.sh"
log=$(mktemp /tmp/fast64-3-structural-companion-v1.XXXXXX)

bash -n "$monitor"
! rg -q 'monitor_fast64_1_r2|collect_fast64_1_r2|run_fast64_trace' "$monitor"
"$monitor" --log "$log" --poll-seconds 1 --once
rg -q 'FAST64_3_BASE_STRUCTURAL_COMPANION_V1_WAIT_TERMINAL' "$log"
test -f "$repo/docs/dtc_l1/fast64/generated/fast64_3_dwt2d_base_alias_v3/FAST64_3_DWT2D_BASE_STRUCTURAL_METRICS_V1.json"
printf 'FAST64_3_BASE_STRUCTURAL_COMPANION_V1_STATIC_REGRESSION_PASS\n'
