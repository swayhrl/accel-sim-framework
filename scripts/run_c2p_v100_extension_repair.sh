#!/usr/bin/env bash
# Cleanly replay V100 extension cases interrupted by a duplicate queue race.
# Each case owns its own repair roots; the strict extension audit gives these
# roots precedence and falls back to the original root for unaffected cases.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
gpgpusim_root="${C2P_GPGPUSIM_ROOT:?set C2P_GPGPUSIM_ROOT to the C2P worktree}"
stage_root="$repo_root/hw_run/c2p-v100-baseline-compat-smoke-v2-20260822/stage"
main_root="$repo_root/hw_run/c2p-v100-main-matrix-repair-v1-20260822"
fast_root="$repo_root/hw_run/c2p-v100-l2-50-matrix-repair-v1-20260822"
lock_dir="$repo_root/hw_run/.c2p-v100-extension-repair.lock"
cases=(c2p-ispass-lib c2p-pannotia-mis c2p-pannotia-color-max c2p-pannotia-pagerank)

if ! mkdir "$lock_dir" 2>/dev/null; then
  echo "repair queue already claimed: $lock_dir" >&2
  exit 1
fi
printf 'pid=%s started=%s cases=%s\n' "$$" "$(date -Is)" "${cases[*]}" > "$lock_dir/owner"

run_matrix() {
  local case_name="$1" root="$2" l2_50="$3"
  local -a extra=()
  mkdir -p "$root"
  if [[ "$l2_50" == yes ]]; then
    extra+=(--config-extra "$repo_root/configs/c2p-cache/paper-table-l2-50.config")
  fi
  C2P_GPGPUSIM_ROOT="$gpgpusim_root" \
  "$repo_root/scripts/run_c2p_cache_cases.sh" \
    --trace "$stage_root/$case_name/$case_name/traces/kernelslist.g" \
    --config "$repo_root/gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config" \
    --config-extra "$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config" \
    --config-extra "$repo_root/configs/c2p-cache/paper-table.config" \
    "${extra[@]}" \
    --strip-mem-addr-mapping --skip-complete \
    --modes baseline,oracle,ideal,c2p,ata,ccd,ring --out-dir "$root/$case_name" \
    >"$root/$case_name.driver.log" 2>&1
}

for case_name in "${cases[@]}"; do
  printf 'START repair case=%s time=%s\n' "$case_name" "$(date -Is)"
  run_matrix "$case_name" "$main_root" no &
  main_pid=$!
  run_matrix "$case_name" "$fast_root" yes &
  fast_pid=$!
  wait "$main_pid"
  wait "$fast_pid"
  printf 'PASS repair case=%s time=%s\n' "$case_name" "$(date -Is)"
done

printf 'PASS V100 extension repair queue time=%s\n' "$(date -Is)"
