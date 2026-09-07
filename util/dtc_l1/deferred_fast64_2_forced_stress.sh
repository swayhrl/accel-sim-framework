#!/usr/bin/env bash
# Retired watcher for the historical high-cap row.  The row is now a retained
# negative control; it must never re-enter the obsolete expected-PASS path.
set -euo pipefail
echo 'FAST64_2_HISTORICAL_HIGH_CAP_WATCHER_RETIRED negative control is terminal; use prepare_fast64_2_coupled_stress.sh' >&2
exit 1
