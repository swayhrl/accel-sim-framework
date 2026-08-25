#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_decoupled_l2_smoke.sh --trace KERNELSLIST --config CONFIG
       [--trace-config FILE] [--config-extra FILE ...]
       [--backend baseline|fixed|decoupled]
       [--run-dir DIR] [--build]

CONFIG is a generated gpgpusim.config.  Its sibling .xml and .icnt files are
copied into the disposable run directory.  The script must be invoked after
setting DECOUPLED_L2_GPGPUSIM_ROOT; it sources setup_decoupled_l2_env.sh and
rejects an accidental GPGPU-Sim checkout.

TRACE-CONFIG is optional.  Supply it only when CONFIG is an unexpanded base
GPGPU-Sim configuration; generated SASS configurations already contain the
matching Accel-Sim trace configuration.

CONFIG-EXTRA is optional experiment-only configuration text appended after the
base and trace configurations.  It may be repeated; files are appended in
argument order, letting a common workload geometry and a candidate resource
override remain separately reviewable.
EOF
}

trace=""
config=""
trace_config=""
config_extras=()
backend="decoupled"
run_dir=""
build=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace) trace="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --config-extra) config_extras+=("$2"); shift 2 ;;
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
for config_extra in "${config_extras[@]}"; do
  [[ -f "$config_extra" ]] || {
    echo "error: --config-extra must name an existing file" >&2; exit 2;
  }
done
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

# A run directory is the unit of reproducibility: it owns the copied binary,
# generated config, and output log.  Concurrent invocations using the same
# directory would otherwise race while replacing accel-sim.out and can yield a
# misleading Text file busy failure.  Backend pairs use separate directories,
# so this excludes only an accidental duplicate launch.
run_lock="$run_dir/.decoupled_l2_smoke_lock"
if ! mkdir "$run_lock" 2>/dev/null; then
  echo "error: run directory is already active: $run_dir" >&2
  exit 2
fi
cleanup_run_lock() {
  rmdir "$run_lock"
}
trap cleanup_run_lock EXIT

cp "$config" "$run_dir/gpgpusim.config"
config_dir="$(cd "$(dirname "$config")" && pwd)"
for asset in "$config_dir"/*.xml "$config_dir"/*.icnt; do
  [[ -f "$asset" ]] && cp "$asset" "$run_dir/"
done
if [[ -n "$trace_config" ]]; then
  printf '\n# Accel-Sim trace parameters\n' >> "$run_dir/gpgpusim.config"
  cat "$trace_config" >> "$run_dir/gpgpusim.config"
fi
if (( ${#config_extras[@]} > 0 )); then
  printf '\n# Decoupled-L2 experiment overrides\n' >> "$run_dir/gpgpusim.config"
  for config_extra in "${config_extras[@]}"; do
    cat "$config_extra" >> "$run_dir/gpgpusim.config"
  done
fi
printf '\n-gpgpu_l2_backend %s\n' "$backend" >> "$run_dir/gpgpusim.config"
ln -sfn "$(cd "$(dirname "$trace")" && pwd)" "$run_dir/traces"

if [[ "$build" -eq 1 ]]; then
  make -C "$repo_root/gpu-simulator" -j"$(nproc)"
fi
sim_bin="$repo_root/gpu-simulator/bin/release/accel-sim.out"
[[ -x "$sim_bin" ]] || {
  echo "error: missing $sim_bin (rerun with --build)" >&2; exit 2; }

# Pin the executable used by this run.  Archive experiments can take hours and
# a rebuild replaces the shared release binary in place; a run-local copy
# keeps the result reproducible and lets provenance identify the exact image.
sim_run_bin="$run_dir/accel-sim.out"
cp "$sim_bin" "$sim_run_bin"
source_dirty=0
if ! git -C "$GPGPUSIM_ROOT" diff --quiet HEAD --; then
  source_dirty=1
fi
source_diff_sha256="$(git -C "$GPGPUSIM_ROOT" diff --no-ext-diff --binary HEAD -- | sha256sum | awk '{print $1}')"
{
  printf 'sim_bin_source=%s\n' "$sim_bin"
  printf 'sim_bin_run=%s\n' "$sim_run_bin"
  printf 'sim_bin_sha256=%s\n' "$(sha256sum "$sim_run_bin" | awk '{print $1}')"
  printf 'sim_bin_build_id=%s\n' "$(readelf -n "$sim_run_bin" | awk '/Build ID:/ {print $3; exit}')"
  printf 'sim_bin_stat=%s\n' "$(stat -c 'size=%s mtime=%y' "$sim_run_bin")"
  printf 'gpgpusim_source_commit=%s\n' "$(git -C "$GPGPUSIM_ROOT" rev-parse HEAD)"
  printf 'gpgpusim_source_dirty=%s\n' "$source_dirty"
  printf 'gpgpusim_source_diff_sha256=%s\n' "$source_diff_sha256"
  printf 'config_sha256=%s\n' "$(sha256sum "$run_dir/gpgpusim.config" | awk '{print $1}')"
  # backend is the only intentional B/D configuration difference.  Preserve
  # a normalized fingerprint so result checkers can reject every other drift.
  printf 'non_backend_config_sha256=%s\n' \
    "$(rg -v '^-gpgpu_l2_backend ' "$run_dir/gpgpusim.config" | sha256sum | awk '{print $1}')"
  if (( ${#config_extras[@]} == 0 )); then
    printf 'config_extra_sha256=\n'
    printf 'config_extra_files=\n'
  elif (( ${#config_extras[@]} == 1 )); then
    printf 'config_extra_sha256=%s\n' "$(sha256sum "${config_extras[0]}" | awk '{print $1}')"
    printf 'config_extra_files=%s\n' "${config_extras[0]}"
  else
    printf 'config_extra_sha256=%s\n' \
      "$(for config_extra in "${config_extras[@]}"; do cat "$config_extra"; done | sha256sum | awk '{print $1}')"
    printf 'config_extra_files=%s\n' "$(IFS=,; echo "${config_extras[*]}")"
  fi
  printf 'trace_kernelslist_sha256=%s\n' "$(sha256sum "$trace" | awk '{print $1}')"
  printf 'backend=%s\n' "$backend"
} > "$run_dir/simulator_provenance.txt"

run_start_iso="$(date -Is)"
run_start_epoch="$(date +%s)"
set +e
(
  cd "$run_dir"
  /usr/bin/time --verbose --output="$run_dir/resource_usage.txt" \
    ./accel-sim.out -config ./gpgpusim.config -trace ./traces/kernelslist.g \
    > smoke.out 2>&1
)
sim_rc=$?
set -e
run_end_iso="$(date -Is)"
run_end_epoch="$(date +%s)"
{
  printf 'start_time=%s\n' "$run_start_iso"
  printf 'end_time=%s\n' "$run_end_iso"
  printf 'wall_seconds=%s\n' "$((run_end_epoch - run_start_epoch))"
  printf 'sim_exit_status=%s\n' "$sim_rc"
} > "$run_dir/runtime_metrics.txt"

if (( sim_rc != 0 )); then
  echo "error: simulator failed; preserved $run_dir/smoke.out" >&2
  tail -50 "$run_dir/smoke.out" >&2 || true
  exit 1
fi
grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$run_dir/smoke.out"
if [[ "$backend" != baseline ]]; then
  grep -q 'decoupled_l2\[' "$run_dir/smoke.out"
fi
printf 'PASS backend=%s run_dir=%s\n' "$backend" "$run_dir"
rg 'decoupled_l2\[.*access=[1-9]|gpu_tot_sim_cycle =|exit detected' \
  "$run_dir/smoke.out" | tail -20 || true
