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
printf 'unrelated\0worker\0' >"$proc_root/202/cmdline"
printf 'Name:\tunrelated\nCpus_allowed_list:\t74-80\n' >"$proc_root/202/status"

output=$(FAST64_PROC_ROOT="$proc_root" "$dispatcher" --dry-run)
printf '%s\n' "$output"
printf '%s\n' "$output" | rg -q 'free_cpu_slots=4'
printf '%s\n' "$output" | rg -q 'free_cpus=74,76,79,80'
printf 'FAST64_R2_DYNAMIC_SLOT_REGRESSION_PASS\twork_root=%s\n' "$work_root"
