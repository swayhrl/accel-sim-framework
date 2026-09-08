#!/usr/bin/env bash
# Non-scientific pre-terminal regression for the future-only alias-v2 monitor.
# It must not create result evidence or invoke a collector while R2 is live.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
monitor="$repo/util/dtc_l1/monitor_fast64_1_r2_alias_v2_closeout.sh"
log=$(mktemp /tmp/fast64-r2-alias-v2-monitor-test.XXXXXX)
out="$repo/docs/dtc_l1/fast64/generated/qualification_r2_full_wave_alias_v2"

bash -n "$monitor"
rg -q 'FAST64_R2_CLOSEOUT_COLLECTOR_RETRY' "$monitor"
rg -q 'RUN_TERMINAL.tsv' "$monitor"
rg -q 'collect_fast64_1_r2_full_wave_alias_v2.sh' "$monitor"
test ! -e "$out"
"$monitor" --log "$log" --once
rg -q 'FAST64_R2_ALIAS_V2_WAIT_TERMINALS' "$log"
test ! -e "$out"
printf 'FAST64_R2_ALIAS_V2_CLOSEOUT_MONITOR_STATIC_REGRESSION_PASS\n'
