#!/usr/bin/env bash
# Static/once regression for the BICG coupled closeout monitor.  No simulator
# control or evidence creation is permitted before its immutable terminal.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
monitor="$repo/util/dtc_l1/monitor_fast64_2_bicg_coupled_closeout_v2.sh"
log=$(mktemp /tmp/fast64-2-bicg-closeout-monitor-test.XXXXXX)
evidence="$repo/docs/dtc_l1/fast64/generated/fast64_2_coupled_stress_bicg_alias_v2"
bash -n "$monitor"
rg -q 'RUN_TERMINAL.tsv' "$monitor"
rg -q 'collect_fast64_2_coupled_stress_bicg_alias_v2.sh' "$monitor"
"$monitor" --log "$log" --once
rg -q 'FAST64_2_BICG_COUPLED_WAIT_TERMINAL' "$log"
test ! -e "$evidence"
printf 'FAST64_2_BICG_COUPLED_CLOSEOUT_MONITOR_STATIC_REGRESSION_PASS\n'
