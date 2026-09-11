#!/usr/bin/env bash
# Static contract regression for the future-only Core95 primary dispatcher.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
tool="$repo/util/dtc_l1/dispatch_fast64_4_primary_core95_v1.sh"
bash -n "$tool"
rg -q '95ccdb7a056f2d53f740d90869785cac6d4ee0f5' "$tool"
rg -q '462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9' "$tool"
rg -q 'PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE' "$tool"
rg -q 'TARGET_EXISTS_REFUSE_RERUN' "$tool"
rg -q 'TARGET_RACED_REFUSE_RERUN' "$tool"
rg -q -- '--mode IO|OO' "$tool"
printf 'FAST64_4_PRIMARY_CORE95_V1_STATIC_REGRESSION_PASS\n'
