#!/usr/bin/env bash
# Static/dry-run proof only: it neither creates a namespace nor starts a row.
set -euo pipefail
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
dispatch="$repo/util/dtc_l1/dispatch_fast64_repaired_core_row_v4.sh"
config="$repo/configs/dtc_l1/fast64/FAST64_BASE.config"
framework=037f008b330eb230353b60edf126d6be9f45afdc

bash -n "$dispatch"
rg -q 'gpgpu-sim-fast64-formal-95ccdb7a' "$dispatch"
rg -q 'core_sha=95ccdb7a056f2d53f740d90869785cac6d4ee0f5' "$dispatch"
rg -q 'runtime_sha=462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9' "$dispatch"
rg -q 'TARGET_EXISTS_REFUSE_RERUN' "$dispatch"
rg -q 'status --porcelain' "$dispatch"
bash "$dispatch" --name fast64_repaired_core_v4_static_probe --workload NN --mode BASE --config "$config" --cpu 8 \
  --classification PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE \
  --framework-scientific-config-source-sha "$framework" --dry-run | \
  rg -q 'FAST64_REPAIRED_CORE_V4_DISPATCH_DRY_RUN_PASS'
printf 'FAST64_REPAIRED_CORE_V4_DISPATCH_STATIC_REGRESSION_PASS\n'
