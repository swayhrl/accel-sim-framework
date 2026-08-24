#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_decoupled_l2_pretrace_cases.sh --trace-root DIR
       [--manifest FILE] [--suite NAME|all] [--tier smoke|dev|extended|all]
       [--case NAME|all]
       [--config FILE] [--trace-config FILE] [--optimized-config-extra FILE]
       [--run-root DIR] [--reuse]

Runs every selected V100 SASS pretrace once with the unchanged baseline L2 and
once with the default experimental decoupled L2.  OPTIMIZED-CONFIG-EXTRA adds
a third decoupled arm with that experiment-only overlay. The selected GPGPU-Sim
worktree is taken from DECOUPLED_L2_GPGPUSIM_ROOT, exactly as in
run_decoupled_l2_smoke.sh.

The case manifest records a required decoupled-L2 counter regex.  A clean
simulator exit alone is insufficient: the run fails if that mechanism was not
actually exercised.
EOF
}

trace_root=""
suite="all"
tier="smoke"
case_filter="all"
manifest=""
config=""
trace_config=""
optimized_config_extra=""
config_given=0
run_root=""
reuse=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace-root) trace_root="$2"; shift 2 ;;
    --suite) suite="$2"; shift 2 ;;
    --manifest) manifest="$2"; shift 2 ;;
    --tier) tier="$2"; shift 2 ;;
    --case) case_filter="$2"; shift 2 ;;
    --config) config="$2"; config_given=1; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --optimized-config-extra) optimized_config_extra="$2"; shift 2 ;;
    --run-root) run_root="$2"; shift 2 ;;
    --reuse) reuse=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -d "$trace_root" ]] || { echo "error: --trace-root must name a directory" >&2; exit 2; }
[[ -z "$manifest" || -f "$manifest" ]] || {
  echo "error: --manifest must name an existing file" >&2; exit 2;
}
[[ -z "$optimized_config_extra" || -f "$optimized_config_extra" ]] || {
  echo "error: --optimized-config-extra must name an existing file" >&2; exit 2;
}
case "$tier" in smoke|dev|extended|all) ;; *)
  echo "error: unsupported tier $tier" >&2; exit 2 ;;
esac
[[ -n "${DECOUPLED_L2_GPGPUSIM_ROOT:-}" ]] || {
  echo "error: set DECOUPLED_L2_GPGPUSIM_ROOT" >&2; exit 2;
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sim_bin="$repo_root/gpu-simulator/bin/release/accel-sim.out"
[[ -x "$sim_bin" ]] || { echo "error: missing simulator binary $sim_bin" >&2; exit 2; }
sim_bin_sha256="$(sha256sum "$sim_bin" | awk '{print $1}')"
gpgpusim_source_commit="$(git -C "$DECOUPLED_L2_GPGPUSIM_ROOT" rev-parse HEAD)"
if [[ -z "$config" ]]; then
  config="$DECOUPLED_L2_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
fi
[[ -f "$config" ]] || { echo "error: missing config $config" >&2; exit 2; }
if [[ -z "$trace_config" && "$config_given" -eq 0 ]]; then
  trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
fi
[[ -z "$trace_config" || -f "$trace_config" ]] || {
  echo "error: missing trace config $trace_config" >&2; exit 2;
}

if [[ -z "$run_root" ]]; then
  run_root="$repo_root/hw_run/decoupled-l2-runs/$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$run_root"
run_root="$(cd "$run_root" && pwd)"

if [[ -z "$manifest" ]]; then
  manifest="$repo_root/experiments/decoupled_l2_v100_pretrace_cases.csv"
fi
summary="$run_root/summary.csv"
printf 'suite,tier,case,arm,cycles,run_dir\n' > "$summary"

run_is_reusable() {
  local case_run_dir="$1" backend="$2" config_extra="$3"
  local provenance recorded_sha recorded_commit recorded_backend recorded_extra expected_extra
  [[ -f "$case_run_dir/smoke.out" ]] || return 1
  rg -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$case_run_dir/smoke.out" || return 1
  provenance="$case_run_dir/simulator_provenance.txt"
  [[ -f "$provenance" ]] || return 1
  recorded_sha="$(sed -n 's/^sim_bin_sha256=//p' "$provenance" | tail -1)"
  recorded_commit="$(sed -n 's/^gpgpusim_source_commit=//p' "$provenance" | tail -1)"
  recorded_backend="$(sed -n 's/^backend=//p' "$provenance" | tail -1)"
  recorded_extra="$(sed -n 's/^config_extra_sha256=//p' "$provenance" | tail -1)"
  expected_extra="${config_extra:+$(sha256sum "$config_extra" | awk '{print $1}')}"
  [[ "$recorded_sha" == "$sim_bin_sha256" &&
     "$recorded_commit" == "$gpgpusim_source_commit" &&
     "$recorded_backend" == "$backend" &&
     "$recorded_extra" == "$expected_extra" ]]
}

case_count=0
while IFS=, read -r case_suite case_tier case_name trace_rel expected_regex; do
  [[ -z "$case_suite" || "${case_suite:0:1}" == "#" || "$case_suite" == "suite" ]] && continue
  [[ "$suite" == "all" || "$suite" == "$case_suite" ]] || continue
  [[ "$tier" == "all" || "$tier" == "$case_tier" ]] || continue
  [[ "$case_filter" == "all" || "$case_filter" == "$case_name" ]] || continue

  trace="$trace_root/$trace_rel/kernelslist.g"
  [[ -f "$trace" ]] || {
    echo "error: missing $case_suite/$case_name trace: $trace" >&2; exit 2;
  }
  case_count=$((case_count + 1))
  arms=(baseline decoupled)
  [[ -z "$optimized_config_extra" ]] || arms+=(optimized)
  for arm in "${arms[@]}"; do
    backend="$arm"
    config_extra=""
    if [[ "$arm" == optimized ]]; then
      backend=decoupled
      config_extra="$optimized_config_extra"
    fi
    case_run_dir="$run_root/$case_suite/$case_name/$arm"
    smoke_args=(--backend "$backend" --trace "$trace" --config "$config"
                --run-dir "$case_run_dir")
    if [[ -n "$trace_config" ]]; then
      smoke_args+=(--trace-config "$trace_config")
    fi
    [[ -z "$config_extra" ]] || smoke_args+=(--config-extra "$config_extra")
    if [[ "$reuse" -eq 1 ]] && run_is_reusable "$case_run_dir" "$backend" "$config_extra"; then
      printf 'REUSE arm=%s run_dir=%s\n' "$arm" "$case_run_dir"
    else
      "$repo_root/scripts/run_decoupled_l2_smoke.sh" "${smoke_args[@]}"
    fi
    if [[ "$backend" == decoupled ]]; then
      rg -q "$expected_regex" "$case_run_dir/smoke.out" || {
        echo "error: $case_suite/$case_name did not meet counter gate: $expected_regex" >&2
        exit 1
      }
    fi
    cycles="$(sed -n 's/.*gpu_tot_sim_cycle = \([0-9][0-9]*\).*/\1/p' \
      "$case_run_dir/smoke.out" | tail -1)"
    [[ -n "$cycles" ]] || { echo "error: no final cycle count for $case_run_dir" >&2; exit 1; }
    printf '%s,%s,%s,%s,%s,%s\n' "$case_suite" "$case_tier" "$case_name" \
      "$arm" "$cycles" "$case_run_dir" >> "$summary"
  done
done < "$manifest"

[[ "$case_count" -gt 0 ]] || { echo "error: selected suite has no cases" >&2; exit 2; }
printf 'PASS cases=%s summary=%s\n' "$case_count" "$summary"
