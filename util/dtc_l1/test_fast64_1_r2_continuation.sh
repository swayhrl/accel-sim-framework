#!/usr/bin/env bash
# Non-scientific static regression: the continuation dispatcher must retain its
# fixed five-row scope and must not address either cohort-1 namespace.
set -euo pipefail
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
dispatcher="$repo_root/util/dtc_l1/prepare_fast64_1_r2_continuation.sh"
auditor="$repo_root/util/dtc_l1/audit_fast64_r2_continuation_resources.sh"
bash -n "$dispatcher" "$auditor"
test "$(rg -c "^  'fast64_1r2_" "$dispatcher")" = 5
! rg -q "fast64_1r2_bicg_base_cap8192_a1|fast64_1r2_bicg_io_cap8192_a1" "$dispatcher"
rg -q 'full_wave_continuation_dispatch.lock' "$dispatcher"
rg -q 'exec 9>&-' "$dispatcher"
rg -q 'requested_new_workers\\t5' "$auditor"
rg -q 'memory_required=\$\(\(p95_rss \* 6\)\)' "$auditor"
printf 'FAST64_R2_CONTINUATION_STATIC_REGRESSION_PASS\n'
