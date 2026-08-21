#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_latebind_l2_smoke.sh --trace KERNELSLIST --config CONFIG
       [--trace-config FILE] [--config-extra FILE] [--run-dir DIR] [--build]

Runs the selected GPGPU-Sim baseline or LateBind oracle configuration.  The
cache behavior is selected only by CONFIG/CONFIG-EXTRA; this script never
injects a backend option.
EOF
}

trace=""
config=""
trace_config=""
config_extra=""
run_dir=""
build=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace) trace="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --config-extra) config_extra="$2"; shift 2 ;;
    --run-dir) run_dir="$2"; shift 2 ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$trace" ]] || { echo "error: --trace must name kernelslist.g" >&2; exit 2; }
[[ -f "$config" ]] || { echo "error: --config must name gpgpusim.config" >&2; exit 2; }
[[ -z "$trace_config" || -f "$trace_config" ]] || {
  echo "error: --trace-config must name an existing file" >&2; exit 2;
}
[[ -z "$config_extra" || -f "$config_extra" ]] || {
  echo "error: --config-extra must name an existing file" >&2; exit 2;
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
set +u
source "$repo_root/scripts/setup_latebind_l2_env.sh" release
set -u

if [[ -z "$run_dir" ]]; then
  run_dir="$(mktemp -d "${TMPDIR:-/tmp}/accel-latebind-l2.XXXXXX")"
else
  mkdir -p "$run_dir"
  run_dir="$(cd "$run_dir" && pwd)"
fi
lock="$run_dir/.latebind_l2_lock"
mkdir "$lock" || { echo "error: run directory is active: $run_dir" >&2; exit 2; }
trap 'rmdir "$lock"' EXIT

cp "$config" "$run_dir/gpgpusim.config"
config_dir="$(cd "$(dirname "$config")" && pwd)"
for asset in "$config_dir"/*.xml "$config_dir"/*.icnt; do
  [[ -f "$asset" ]] && cp "$asset" "$run_dir/"
done
if [[ -n "$trace_config" ]]; then
  printf '\n# Accel-Sim trace parameters\n' >> "$run_dir/gpgpusim.config"
  cat "$trace_config" >> "$run_dir/gpgpusim.config"
fi
if [[ -n "$config_extra" ]]; then
  printf '\n# LateBind-L2 experiment overrides\n' >> "$run_dir/gpgpusim.config"
  cat "$config_extra" >> "$run_dir/gpgpusim.config"
fi
ln -sfn "$(cd "$(dirname "$trace")" && pwd)" "$run_dir/traces"

if [[ "$build" -eq 1 ]]; then
  nice -n 10 make -C "$repo_root/gpu-simulator" -j2
fi
sim_bin="$repo_root/gpu-simulator/bin/release/accel-sim.out"
[[ -x "$sim_bin" ]] || { echo "error: missing $sim_bin (rerun with --build)" >&2; exit 2; }
cp "$sim_bin" "$run_dir/accel-sim.out"
{
  printf 'sim_bin_sha256=%s\n' "$(sha256sum "$run_dir/accel-sim.out" | awk '{print $1}')"
  printf 'accelsim_source_commit=%s\n' "$(git -C "$repo_root" rev-parse HEAD)"
  printf 'gpgpusim_source_commit=%s\n' "$(git -C "$GPGPUSIM_ROOT" rev-parse HEAD)"
  printf 'config_sha256=%s\n' "$(sha256sum "$run_dir/gpgpusim.config" | awk '{print $1}')"
  printf 'trace_kernelslist_sha256=%s\n' "$(sha256sum "$trace" | awk '{print $1}')"
} > "$run_dir/simulator_provenance.txt"

if ! (
  cd "$run_dir"
  ./accel-sim.out -config ./gpgpusim.config -trace ./traces/kernelslist.g > smoke.out 2>&1
); then
  echo "error: simulator failed; preserved $run_dir/smoke.out" >&2
  tail -50 "$run_dir/smoke.out" >&2 || true
  exit 1
fi
grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$run_dir/smoke.out"
printf 'PASS run_dir=%s\n' "$run_dir"
rg 'latebind_l2_global|gpu_tot_sim_cycle =|exit detected' "$run_dir/smoke.out" | tail -20 || true
