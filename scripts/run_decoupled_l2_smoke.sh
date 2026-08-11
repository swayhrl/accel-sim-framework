#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_decoupled_l2_smoke.sh --trace KERNELSLIST --config CONFIG
       [--trace-config FILE] [--backend baseline|fixed|decoupled]
       [--run-dir DIR] [--build]

CONFIG is a generated gpgpusim.config.  Its sibling .xml and .icnt files are
copied into the disposable run directory.  The script must be invoked after
setting DECOUPLED_L2_GPGPUSIM_ROOT; it sources setup_decoupled_l2_env.sh and
rejects an accidental GPGPU-Sim checkout.

TRACE-CONFIG is optional.  Supply it only when CONFIG is an unexpanded base
GPGPU-Sim configuration; generated SASS configurations already contain the
matching Accel-Sim trace configuration.
EOF
}

trace=""
config=""
trace_config=""
backend="decoupled"
run_dir=""
build=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace) trace="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --backend) backend="$2"; shift 2 ;;
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
case "$backend" in baseline|fixed|decoupled) ;; *)
  echo "error: unsupported backend $backend" >&2; exit 2 ;; esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1090
set +u  # GPGPU-Sim's environment script probes optional unset variables.
source "$repo_root/scripts/setup_decoupled_l2_env.sh" release
set -u

if [[ -z "$run_dir" ]]; then
  run_dir="$(mktemp -d "${TMPDIR:-/tmp}/accel-decoupled-l2.XXXXXX")"
else
  mkdir -p "$run_dir"
  run_dir="$(cd "$run_dir" && pwd)"
fi

cp "$config" "$run_dir/gpgpusim.config"
config_dir="$(cd "$(dirname "$config")" && pwd)"
for asset in "$config_dir"/*.xml "$config_dir"/*.icnt; do
  [[ -f "$asset" ]] && cp "$asset" "$run_dir/"
done
if [[ -n "$trace_config" ]]; then
  printf '\n# Accel-Sim trace parameters\n' >> "$run_dir/gpgpusim.config"
  cat "$trace_config" >> "$run_dir/gpgpusim.config"
fi
printf '\n-gpgpu_l2_backend %s\n' "$backend" >> "$run_dir/gpgpusim.config"
ln -sfn "$(cd "$(dirname "$trace")" && pwd)" "$run_dir/traces"

if [[ "$build" -eq 1 ]]; then
  make -C "$repo_root/gpu-simulator" -j"$(nproc)"
fi
sim_bin="$repo_root/gpu-simulator/bin/release/accel-sim.out"
[[ -x "$sim_bin" ]] || {
  echo "error: missing $sim_bin (rerun with --build)" >&2; exit 2; }

(
  cd "$run_dir"
  "$sim_bin" -config ./gpgpusim.config -trace ./traces/kernelslist.g > smoke.out 2>&1
)
grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$run_dir/smoke.out"
if [[ "$backend" != baseline ]]; then
  grep -q 'decoupled_l2\[' "$run_dir/smoke.out"
fi
printf 'PASS backend=%s run_dir=%s\n' "$backend" "$run_dir"
rg 'decoupled_l2\[.*access=[1-9]|gpu_tot_sim_cycle =|exit detected' \
  "$run_dir/smoke.out" | tail -20 || true
