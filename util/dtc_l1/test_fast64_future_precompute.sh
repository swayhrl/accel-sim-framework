#!/usr/bin/env bash
set -euo pipefail
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
audit="$repo/util/dtc_l1/audit_fast64_future_precompute_resources.sh"
dispatch="$repo/util/dtc_l1/prepare_fast64_2_coupled_stress_v2.sh"
gesummv_collector="$repo/util/dtc_l1/collect_fast64_3_gesummv_base_alias_v2.sh"
bash -n "$audit" "$dispatch" "$gesummv_collector"
rg -q 'FAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_V1' "$audit"
rg -q 'requested_new_workers' "$audit"
rg -q 'FAST64_2_FUTURE_DRY_RUN_PASS' "$dispatch"
rg -q 'select_fast64_r2_cpus.py' "$dispatch"
rg -q 'exec 9>&-' "$dispatch"
rg -q 'RUN_TERMINAL.tsv' "$gesummv_collector"
rg -q 'require-immutable-attempt' "$gesummv_collector"
rg -q 'FAST64_3_GESUMMV_BASE_ALIAS_V2' "$gesummv_collector"
printf 'FAST64_FUTURE_PRECOMPUTE_STATIC_REGRESSION_PASS\n'
