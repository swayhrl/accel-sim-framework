#!/usr/bin/env bash
# Static regression for the future-only v2 closeout invocation contract.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
monitor="$repo/util/dtc_l1/monitor_fast64_precomputed_row_v2.sh"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"

bash -n "$monitor"
test -r "$validator"
test ! -x "$validator"
rg -q 'python3 "\$validator"' "$monitor"
rg -q -- '--require-immutable-attempt' "$monitor"
rg -q 'FAST64_PRECOMPUTED_ROW_V2_PASS' "$monitor"
printf 'FAST64_PRECOMPUTED_ROW_V2_STATIC_REGRESSION_PASS\n'
