#!/usr/bin/env bash
# Wait for the independently scheduled paper16 replays, then run one strict
# closeout.  This script never starts, stops, or modifies a simulator run.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/watch_c2p_paper16_closeout.sh [--interval SEC] [--once]

Poll the canonical/parallel C2P paper16 result roots.  Once every required
seven-mode, L2=50, CCD, and m/k summary exists, run finalize_c2p_paper16.sh
exactly once.  A strict-analysis failure is recorded and returned; it is not
retried, because it requires diagnosis rather than another blind replay.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
interval=120
once=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --interval) interval="$2"; shift 2 ;;
    --once) once=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "$interval" =~ ^[1-9][0-9]*$ ]] || {
  echo "error: --interval must be a positive integer" >&2; exit 2;
}

main_root="$repo_root/hw_run/c2p-paper16-v7-20260821"
main_supplemental=(
  "$repo_root/hw_run/c2p-paper16-v7-parallel-v2-20260821"
  "$repo_root/hw_run/c2p-paper16-v7-parallel-v3-20260821"
)
fast_root="$repo_root/hw_run/c2p-paper16-l2-50-v7-20260821"
fast_supplemental=("$repo_root/hw_run/c2p-paper16-l2-50-v7-parallel-v2-20260821")
# CCD's counter training was corrected after the initial campaign.  Stencil
# then exposed a detector false positive and is replayed by the corrected
# detector binary in a separate root.  Both roots are fresh-training CCD
# evidence: prefer the corrected Stencil result, while allowing the earlier
# root to supply cases it already completed successfully.  Pre-training-fix
# CCD data is never in either list.
ccd_root="$repo_root/hw_run/c2p-ccd-stencil-progressfix-v1-20260821"
ccd_supplemental=("$repo_root/hw_run/c2p-paper16-ccd-refresh-v2-20260821")
# Older RING campaign runs sent a miss directly to L2 when the serialized
# discovery FIFO was full.  A correct RING keeps that miss at the L1 head
# until the FIFO drains.  Do not mix the old measurements into final figures.
ring_root="$repo_root/hw_run/c2p-ring-backpressure-v1-20260821"
sweep_root="$repo_root/hw_run/c2p-paper16-fp-sweep-v1-20260821"
sweep_supplemental=("$repo_root/hw_run/c2p-paper16-fp-sweep-parallel-v2-20260821")
queue_root="$repo_root/hw_run/c2p-btree-query-sensitivity-v1-20260821"
analysis_dir="$repo_root/hw_run/c2p-paper16-analysis-final-v7-20260821"
figures_dir="$repo_root/hw_run/c2p-paper16-figures-final-v7-20260821"
report="$repo_root/hw_run/c2p-paper16-report-final-v7-20260821.md"
lock_dir="$repo_root/hw_run/.c2p-paper16-final-closeout.lock"
log="$repo_root/hw_run/c2p-paper16-final-closeout.log"
manifest="$repo_root/configs/c2p-cache/paper16_workloads.tsv"

has_summary() {
  local case_name="$1" mode="$2" root
  shift 2
  for root in "$@"; do
    [[ -f "$root/$case_name/$mode/summary.txt" ]] && return 0
  done
  return 1
}

missing=()
failed=()
deadlocked_without_summary() {
  local root="$1" case_name="$2" mode="$3"
  local run_dir="$root/$case_name/$mode"
  [[ ! -f "$run_dir/summary.txt" && -f "$run_dir/run.out" ]] || return 1
  rg -q 'GPGPU-Sim uArch: ERROR \*\* deadlock detected' "$run_dir/run.out"
}

collect_missing() {
  missing=()
  failed=()
  local case_name mode point
  while IFS=$'\t' read -r case_name _; do
    [[ -z "$case_name" || "$case_name" == case || "$case_name" == \#* ]] && continue
    for mode in baseline oracle ideal c2p ata ccd ring; do
      if [[ "$mode" == ccd ]]; then
        has_summary "$case_name" "$mode" "$ccd_root" "${ccd_supplemental[@]}" ||
          missing+=("main:$case_name/$mode")
        deadlocked_without_summary "$ccd_root" "$case_name" "$mode" &&
          failed+=("main:$case_name/$mode")
      elif [[ "$mode" == ring ]]; then
        has_summary "$case_name" "$mode" "$ring_root" ||
          missing+=("main:$case_name/$mode")
        deadlocked_without_summary "$ring_root" "$case_name" "$mode" &&
          failed+=("main:$case_name/$mode")
      elif ! has_summary "$case_name" "$mode" "$main_root" "${main_supplemental[@]}"; then
        missing+=("main:$case_name/$mode")
        for root in "$main_root" "${main_supplemental[@]}"; do
          deadlocked_without_summary "$root" "$case_name" "$mode" &&
            failed+=("main:$case_name/$mode")
        done
      fi
    done
    has_summary "$case_name" baseline "$fast_root" "${fast_supplemental[@]}" ||
      missing+=("l2-50:$case_name/baseline")
    has_summary "$case_name" ccd "$ccd_root" "${ccd_supplemental[@]}" ||
      missing+=("ccd:$case_name/ccd")
    for point in m2048-k2 m3072-k3 m5120-k4 m9216-k5; do
      has_summary "$case_name" c2p "$sweep_root/$point" \
        "${sweep_supplemental[@]/%/$point}" ||
        missing+=("$point:$case_name/c2p")
    done
  done < "$manifest"
}

# A fresh CCD summary serves both the seven-mode matrix and the CCD-metric
# gate.  Keep both gates in ``missing`` so either cannot be bypassed, but
# report the physical-file count separately to avoid implying that the same
# replay must produce two summaries.
unique_missing_summary_count() {
  printf '%s\n' "${missing[@]}" |
    sed -E 's/^(main|ccd):([^/]+)\/ccd$/ccd:\2\/ccd/' |
    sort -u |
    wc -l
}

# A prior strict audit can fail after claiming the lock (for example, when a
# corrected campaign supersedes an old result root).  An empty lock from that
# legacy protocol must not suppress the later corrected closeout.  New locks
# receive an owner file before analysis starts: those are deliberately kept
# after a failure so it is diagnosed rather than retried blindly.
claim_closeout_lock() {
  if mkdir "$lock_dir" 2>/dev/null; then
    printf 'pid=%s started=%s\n' "$$" "$(date -Is)" > "$lock_dir/owner"
    return 0
  fi
  if [[ -f "$report" ]]; then
    printf 'strict report already exists: %s\n' "$report"
    return 1
  fi
  if [[ -f "$lock_dir/owner" ]]; then
    printf 'closeout lock has owner; inspect prior/in-progress audit: %s\n' \
      "$lock_dir/owner" >&2
    return 2
  fi
  if find "$lock_dir" -mindepth 1 -maxdepth 1 -print -quit | grep -q .; then
    printf 'closeout lock has unknown contents; refusing to remove: %s\n' \
      "$lock_dir" >&2
    return 2
  fi
  # Only an empty, owner-less legacy lock reaches this point.
  rmdir "$lock_dir"
  mkdir "$lock_dir"
  printf 'pid=%s started=%s\n' "$$" "$(date -Is)" > "$lock_dir/owner"
  printf 'reclaimed empty legacy closeout lock: %s\n' "$lock_dir"
}

while :; do
  collect_missing
  if (( ${#failed[@]} != 0 )); then
    printf '%s detected terminal failed input(s): %s\n' \
      "$(date -Is)" "${failed[*]}" >&2
    exit 1
  fi
  if (( ${#missing[@]} == 0 )); then
    if claim_closeout_lock; then
      :
    else
      lock_status=$?
      if (( lock_status == 1 )); then
        exit 0
      fi
      exit "$lock_status"
    fi
    {
      printf 'all required summaries found at %s\n' "$(date -Is)"
      PYTHONPATH=/tmp/c2p-matplotlib-py311 \
      "$repo_root/scripts/finalize_c2p_paper16.sh" \
        --results-root "$main_root" \
        --supplemental-results-root "${main_supplemental[0]}" \
        --supplemental-results-root "${main_supplemental[1]}" \
        --l2-fast-root "$fast_root" \
        --supplemental-l2-fast-root "${fast_supplemental[0]}" \
        --ccd-metrics-root "$ccd_root" \
        --supplemental-ccd-metrics-root "${ccd_supplemental[0]}" \
        --ccd-mode-root "$ccd_root" \
        --ccd-mode-root "${ccd_supplemental[0]}" \
        --ring-mode-root "$ring_root" \
        --sweep-root "$sweep_root" \
        --supplemental-sweep-root "${sweep_supplemental[0]}" \
        --queue-sensitivity-root "$queue_root" \
        --analysis-dir "$analysis_dir" \
        --figures-dir "$figures_dir" \
        --report "$report" \
        --python /scratch/root/oss-eda/oss-cad-suite/py3bin/python3
    } >>"$log" 2>&1
    printf 'strict closeout passed: %s\n' "$report" | tee -a "$log"
    exit 0
  fi
  unique_missing=$(unique_missing_summary_count)
  printf '%s waiting for %u required gates (%u unique summaries); first: %s\n' \
    "$(date -Is)" "${#missing[@]}" "$unique_missing" "${missing[0]}"
  # With ``set -e``, an ``&&`` list ending in a false arithmetic test would
  # terminate this long-lived watcher after its first normal poll.  Keep the
  # one-shot failure explicit so the default watcher reaches its next poll.
  if (( once )); then
    exit 1
  fi
  sleep "$interval"
done
