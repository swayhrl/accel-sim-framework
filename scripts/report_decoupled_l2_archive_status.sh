#!/usr/bin/env bash
# Summarize archived Decoupled-L2 workload evidence without changing a run.
# A workload is PASS only when one baseline/decoupled pair both reached the
# simulator terminal marker; a directory or a single surviving backend is not
# sufficient evidence.
set -euo pipefail

root="${1:-$(pwd)}"
marker='GPGPU-Sim: \*\*\* exit detected \*\*\*'

terminal() {
    [[ -f "$1" ]] && rg -q "$marker" "$1"
}

pair_passed() {
    local name="$1" base run candidate
    while IFS= read -r -d '' base; do
        terminal "$base" || continue
        run="${base%/baseline/smoke.out}"
        for candidate in "$run"/decoupled*/smoke.out; do
            terminal "$candidate" && return 0
        done
    done < <(find "$root/hw_run" -type f -path "*${name}*/baseline/smoke.out" -print0)
    return 1
}

running_state() {
    local name="$1" proc cwd baseline=0 decoupled=0
    for proc in /proc/[0-9]*; do
        [[ -r "$proc/comm" && "$(<"$proc/comm")" == accel-sim.out ]] || continue
        cwd="$(readlink "$proc/cwd" 2>/dev/null || true)"
        [[ "$cwd" == *"$name"* ]] || continue
        [[ "$cwd" == */baseline ]] && baseline=1
        [[ "$cwd" == */decoupled* ]] && decoupled=1
    done
    if (( baseline && decoupled )); then
        printf 'ACTIVE_PAIR'
    elif (( baseline || decoupled )); then
        printf 'ACTIVE_PARTIAL'
    else
        printf 'PENDING'
    fi
}

report_cases() {
    local suite="$1" cases="$2" path name alt_name state passed=0 pairs=0 partial=0 pending=0
    while IFS= read -r path; do
        [[ -n "$path" && "$path" != \#* ]] || continue
        name="$(awk -F/ '{print $3}' <<<"$path")"
        # mri-gridding's retained retry predates the archive namespace and
        # therefore uses mri-gridding rather than parboil-mri-gridding.  Keep
        # this narrowly scoped: a general prefix drop could match an unrelated
        # workload with the same short name.
        alt_name=""
        [[ "$name" == parboil-mri-gridding ]] && alt_name=mri-gridding
        if pair_passed "$name" || { [[ -n "$alt_name" ]] && pair_passed "$alt_name"; }; then
            state=PASS; ((passed += 1))
        else
            state="$(running_state "$name")"
            if [[ "$state" == PENDING && -n "$alt_name" ]]; then
                state="$(running_state "$alt_name")"
            fi
            case "$state" in
                ACTIVE_PAIR) ((pairs += 1)) ;;
                ACTIVE_PARTIAL) ((partial += 1)) ;;
                PENDING) ((pending += 1)) ;;
            esac
        fi
        printf '%s,%s,%s\n' "$suite" "$state" "$name"
    done < "$cases"
    printf '%s summary: pass=%d active_pair=%d active_partial=%d pending=%d\n' \
        "$suite" "$passed" "$pairs" "$partial" "$pending" >&2
}

poly_cases="$root/hw_run/decoupled-l2-plans/polybench/cases.txt"
parboil_cases="$root/hw_run/decoupled-l2-archive-batch/parboil_all/parboil_selected_cases.txt"

printf 'suite,state,workload\n'
report_cases polybench "$poly_cases"
report_cases parboil "$parboil_cases"

cutlass_cases="$root/hw_run/decoupled-l2-plans/cutlass/cases.txt"
cutlass_total="$(awk 'NF && $1 !~ /^#/' "$cutlass_cases" | wc -l)"
cutlass_root="$root/hw_run/decoupled-l2-trace-fraction/cutlass-all-1of40-trim-v1"
if [[ -f "$cutlass_root/.trace_fraction_cases_complete" ]]; then
    printf 'cutlass,TRACE_READY,%s planned cases\n' "$cutlass_total"
else
    printf 'cutlass,TRACE_PREPARING,%s planned cases\n' "$cutlass_total"
fi
