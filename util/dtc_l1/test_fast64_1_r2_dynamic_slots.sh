#!/usr/bin/env bash
# Non-scientific isolated regression for R2 host-slot discovery.  It supplies
# a synthetic process table only to the dispatcher's dry-run path.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
dispatcher="$repo_root/util/dtc_l1/prepare_fast64_1_r2_full_wave.sh"
work_root=$(mktemp -d /tmp/fast64-r2-slot-regression.XXXXXX)
proc_root="$work_root/proc"

mkdir -p -- "$proc_root/101" "$proc_root/202"
printf 'accel-sim.out\0-trace\0synthetic\0' >"$proc_root/101/cmdline"
printf 'Name:\taccel-sim.out\nCpus_allowed_list:\t75,77-78\n' >"$proc_root/101/status"
printf 'accel-sim.out\0-trace\0broad-synthetic\0' >"$proc_root/202/cmdline"
printf 'Name:\taccel-sim.out\nCpus_allowed_list:\t0-511\n' >"$proc_root/202/status"

output=$(FAST64_PROC_ROOT="$proc_root" FAST64_CPU_CANDIDATES='74-80' "$dispatcher" --dry-run)
printf '%s\n' "$output"
printf '%s\n' "$output" | rg -q 'R2_TOPOLOGY_AWARE_DISPATCH_DRY_RUN_PASS'
printf '%s\n' "$output" | rg -q 'available_distinct_physical_cores=4'
printf '%s\n' "$output" | rg -q 'candidate_cpus=74,76,79,80'
printf 'FAST64_R2_TOPOLOGY_SELECTOR_REGRESSION_PASS\twork_root=%s\n' "$work_root"
