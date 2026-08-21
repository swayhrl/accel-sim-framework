#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/check_l2_frc_baseline_preservation.sh --trace KERNELSLIST
       --config CONFIG --reference-sim-bin BIN --reference-runtime-dir DIR
       [--trace-config FILE] [--frc-config-extra FILE]
       [--reference-config-extra FILE] [--run-root DIR]

Compares the current FRC core with FRC disabled against a separately built
corrected conventional-control simulator.  The two binaries and their runtime
directories are explicit so the check cannot silently compare a binary with a
different GPGPU-Sim shared library.
EOF
}

trace=""
config=""
trace_config=""
frc_config_extra=""
reference_config_extra=""
reference_sim_bin=""
reference_runtime_dir=""
run_root=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace) trace="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --frc-config-extra) frc_config_extra="$2"; shift 2 ;;
    --reference-config-extra) reference_config_extra="$2"; shift 2 ;;
    --reference-sim-bin) reference_sim_bin="$2"; shift 2 ;;
    --reference-runtime-dir) reference_runtime_dir="$2"; shift 2 ;;
    --run-root) run_root="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$trace" && -f "$config" && -x "$reference_sim_bin" ]] || {
  usage >&2; exit 2;
}
[[ -z "$trace_config" || -f "$trace_config" ]] || { usage >&2; exit 2; }
[[ -z "$frc_config_extra" || -f "$frc_config_extra" ]] || { usage >&2; exit 2; }
[[ -z "$reference_config_extra" || -f "$reference_config_extra" ]] || {
  usage >&2; exit 2;
}
[[ -d "$reference_runtime_dir" ]] || { usage >&2; exit 2; }

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$run_root" ]]; then
  run_root="$(mktemp -d "${TMPDIR:-/tmp}/l2-frc-preservation.XXXXXX")"
else
  mkdir -p "$run_root"
  run_root="$(cd "$run_root" && pwd)"
fi

# The current side always forces FRC off.  The reference side must receive
# only options its conventional-control core understands.
frc_extra="$run_root/frc-off.config"
if [[ -n "$frc_config_extra" ]]; then
  cat "$frc_config_extra" > "$frc_extra"
else
  : > "$frc_extra"
fi
cat "$repo_root/configs/l2_frc/disabled.config" >> "$frc_extra"

current=(--trace "$trace" --config "$config" --config-extra "$frc_extra"
         --run-dir "$run_root/frc-off")
if [[ -n "$trace_config" ]]; then
  current+=(--trace-config "$trace_config")
fi
"$repo_root/scripts/run_latebind_l2_smoke.sh" "${current[@]}"

reference_dir="$run_root/reference"
mkdir -p "$reference_dir"
cp "$config" "$reference_dir/gpgpusim.config"
config_dir="$(cd "$(dirname "$config")" && pwd)"
for asset in "$config_dir"/*.xml "$config_dir"/*.icnt; do
  [[ -f "$asset" ]] && cp "$asset" "$reference_dir/"
done
if [[ -n "$trace_config" ]]; then
  cat "$trace_config" >> "$reference_dir/gpgpusim.config"
fi
if [[ -n "$reference_config_extra" ]]; then
  cat "$reference_config_extra" >> "$reference_dir/gpgpusim.config"
fi
ln -sfn "$(cd "$(dirname "$trace")" && pwd)" "$reference_dir/traces"
trace_name="$(basename "$trace")"
cp "$reference_sim_bin" "$reference_dir/accel-sim.out"
{
  printf 'reference_sim_sha256=%s\n' "$(sha256sum "$reference_sim_bin" | awk '{print $1}')"
  printf 'reference_runtime_dir=%s\n' "$(cd "$reference_runtime_dir" && pwd)"
  printf 'reference_config_sha256=%s\n' "$(sha256sum "$reference_dir/gpgpusim.config" | awk '{print $1}')"
} > "$reference_dir/simulator_provenance.txt"
(
  cd "$reference_dir"
  LD_LIBRARY_PATH="$reference_runtime_dir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    ./accel-sim.out -config ./gpgpusim.config -trace "./traces/$trace_name" > smoke.out 2>&1
)
grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$reference_dir/smoke.out"

# This set excludes FRC-only observation lines and option echoes, but retains
# all terminal architectural, L2/MSHR, DRAM and writeback-path counters.
metric_re='^(gpu_tot_sim_(cycle|insn)|gpgpu_n_mem_(read|write)_(local|global|texture|const)|total dram (reads|writes)|L2_total_cache_(accesses|misses|miss_rate|pending_hits|reservation_fails)|[[:space:]]*(Total_core_cache_stats_breakdown|L2_cache_stats_breakdown|L2_total_cache_reservation_fail_breakdown)\[)'
rg "$metric_re" "$run_root/frc-off/smoke.out" > "$run_root/frc-off.metrics"
rg "$metric_re" "$reference_dir/smoke.out" > "$run_root/reference.metrics"
diff -u "$run_root/reference.metrics" "$run_root/frc-off.metrics"

printf 'PASS frc_baseline_preservation run_root=%s\n' "$run_root"
cat "$run_root/frc-off.metrics"
