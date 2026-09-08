#!/usr/bin/env bash
# Static/once regression: no simulator, receipt, result or monitor loop is
# created.  This only proves the monitor refuses to collect before terminal.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
monitor="$repo/util/dtc_l1/monitor_fast64_3_precompute_closeout_v2.sh"
log=$(mktemp /tmp/fast64-3-closeout-monitor-test.XXXXXX)
bash -n "$monitor"
rg -q 'RUN_TERMINAL.tsv' "$monitor"
rg -q 'collect_fast64_3_atax_base_alias_v2.sh' "$monitor"
rg -q 'collect_fast64_3_gesummv_base_alias_v2.sh' "$monitor"
"$monitor" --log "$log" --once
rg -q 'FAST64_3_PRECOMPUTE_WAIT_TERMINAL' "$log"
test ! -e "$repo/docs/dtc_l1/fast64/generated/fast64_3_atax_base_alias_v2"
test ! -e "$repo/docs/dtc_l1/fast64/generated/fast64_3_gesummv_base_alias_v2"
printf 'FAST64_3_PRECOMPUTE_CLOSEOUT_MONITOR_STATIC_REGRESSION_PASS\n'
