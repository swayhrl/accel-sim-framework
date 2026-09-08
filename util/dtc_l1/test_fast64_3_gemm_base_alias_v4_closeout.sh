#!/usr/bin/env bash
# Static regression for the future-only GEMM/Base closeout path.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
collector="$repo/util/dtc_l1/collect_fast64_3_gemm_base_alias_v4.sh"
monitor="$repo/util/dtc_l1/monitor_fast64_3_gemm_base_alias_v4_closeout.sh"

bash -n "$collector" "$monitor"
rg -q 'deadlock detected' "$collector"
! rg -q "'assert\\|fatal\\|deadlock\\|output mismatch" "$collector"
! rg -q 'fast64_1r2_|monitor_fast64_1_r2|collect_fast64_1_r2' "$collector" "$monitor"
printf 'FAST64_3_GEMM_BASE_ALIAS_V4_CLOSEOUT_STATIC_REGRESSION_PASS\n'
