#!/usr/bin/env bash
# Non-scientific regression for the future-only immutable-v2 formal wave path.
# It uses dry-runs exclusively and creates no FAST64 run namespace.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
dispatch="$repo/util/dtc_l1/dispatch_fast64_precomputed_row_v2.sh"
pool="$repo/util/dtc_l1/run_fast64_dynamic_pool_v2.sh"
framework=037f008b330eb230353b60edf126d6be9f45afdc
base="$repo/configs/dtc_l1/fast64/FAST64_BASE.config"
io="$repo/configs/dtc_l1/fast64/FAST64_IO.config"
name=fast64_controller_regression_atax_base_v2
forbidden=fast64_controller_regression_atax_io_v2

bash -n "$dispatch" "$pool"
rg -q 'run_fast64_trace_v2.sh' "$dispatch"
rg -q -- '--immutable-runner-path' "$dispatch"
rg -q 'FAST64_2_REPAIR_PASS_REQUIRED' "$dispatch"
rg -q 'RUN_TERMINAL.tsv' "$pool"
rg -q 'validate_fast64_trace_row_alias_v2.py' "$pool"
test ! -e "/workspace/fast64-runs/$name"
test ! -e "/workspace/fast64-runs/$forbidden"
"$dispatch" --name "$name" --workload atax --mode BASE --config "$base" --cpu 11 \
  --classification PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE \
  --framework-scientific-config-source-sha "$framework" --dry-run
"$pool" --stage 3 --modes BASE --classification PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE \
  --cpus 11 --workloads atax,gesummv --dry-run
if "$dispatch" --name "$forbidden" --workload atax --mode IO --config "$io" --cpu 11 \
    --classification PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE \
    --framework-scientific-config-source-sha "$framework" --dry-run; then
  echo EARLY_IO_UNEXPECTEDLY_ACCEPTED >&2
  exit 1
fi
test ! -e "/workspace/fast64-runs/$name"
test ! -e "/workspace/fast64-runs/$forbidden"
printf 'FAST64_DYNAMIC_POOL_V2_STATIC_REGRESSION_PASS\n'
