#!/usr/bin/env bash
# Static regression for the future-only Core-41 2D primary continuation.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
controller="$repo/util/dtc_l1/auto_dispatch_fast64_4_2d_core41_v1.sh"
dispatcher="$repo/util/dtc_l1/dispatch_fast64_4_2d_core41_v1.sh"
monitor="$repo/util/dtc_l1/monitor_fast64_repaired_core_row_v2.sh"
auditor="$repo/util/dtc_l1/audit_fast64_future_precompute_resources_v3.sh"

bash -n "$controller"
test -x "$controller"
for entry in \
  "dispatcher_sha=$(sha256sum "$dispatcher" | awk '{print $1}')" \
  "monitor_sha=$(sha256sum "$monitor" | awk '{print $1}')" \
  "auditor_sha=$(sha256sum "$auditor" | awk '{print $1}')"; do
  rg -Fqx "$entry" "$controller" || { echo "FAST64_4_2D_CORE41_STATIC_CONTRACT_MISSING $entry" >&2; exit 1; }
done
for fragment in \
  'FAST64_4_2D_CORE41_WAIT_BASE_STRICT_GATE' \
  'FAST64_4_2D_CORE41_RESOURCE_WAIT' \
  'PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE' \
  'start_monitor IO io' \
  'start_monitor OO oo'; do
  rg -F "$fragment" "$controller" >/dev/null || { echo "FAST64_4_2D_CORE41_STATIC_FRAGMENT_MISSING $fragment" >&2; exit 1; }
done
if rg -n '\b(pkill|killall|renice|nice|restart)\b|kill[[:space:]]+-[^0]' "$controller"; then
  echo FAST64_4_2D_CORE41_FORBIDDEN_LIVE_PROCESS_CONTROL >&2
  exit 1
fi
printf 'FAST64_4_2D_CORE41_AUTODISPATCH_V1_STATIC_REGRESSION_PASS\n'
