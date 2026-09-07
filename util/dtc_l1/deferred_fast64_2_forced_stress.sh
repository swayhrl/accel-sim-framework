#!/usr/bin/env bash
# Passive closeout watcher for the live FAST64.2 stress diagnostic.  This
# script never signals, launches, pauses, or modifies a simulator process.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
row=fast64_2_precomputed_bicg_io_stress_cap1048576_pib1_a1
manifest="$runs_root/$row/RUN_MANIFEST.tsv"
collector="$repo_root/util/dtc_l1/collect_fast64_2_forced_stress.sh"
lock="$runs_root/.fast64_2_forced_stress_closeout.lock"

test -r "$manifest"
test -x "$collector"
exec 9>"$lock"
flock -n 9 || { echo "FAST64_2_CLOSEOUT_WATCHER_EXISTS $lock" >&2; exit 1; }

while ! awk -F '\t' '$1=="simulator_exit_status" {found=1} END {exit !found}' "$manifest"; do
  sleep 60
done

"$collector"
