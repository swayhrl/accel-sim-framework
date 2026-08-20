#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_cache_cases.sh --trace KERNELSLIST --config CONFIG --out-dir DIR
       [--modes baseline,oracle,ideal,c2p] [--config-extra FILE]

Run the same trace through the four C2P comparison points.  C2P_GPGPUSIM_ROOT
must name the matching hrl/c2p-cache-v0 worktree.  CONFIG may be a generated
Accel-Sim config; legacy -gpgpu_l2_backend lines are removed because C2P uses
the clean upstream L2 baseline.
EOF
}

trace=""
config=""
out_dir=""
modes="baseline,oracle,ideal,c2p"
config_extra=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace) trace="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --out-dir) out_dir="$2"; shift 2 ;;
    --modes) modes="$2"; shift 2 ;;
    --config-extra) config_extra="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$trace" ]] || { echo "error: --trace must name kernelslist.g" >&2; exit 2; }
[[ -f "$config" ]] || { echo "error: --config must name a config" >&2; exit 2; }
[[ -n "$out_dir" ]] || { echo "error: --out-dir is required" >&2; exit 2; }
[[ -z "$config_extra" || -f "$config_extra" ]] || {
  echo "error: --config-extra must exist" >&2; exit 2;
}
[[ -n "${C2P_GPGPUSIM_ROOT:-}" ]] || {
  echo "error: set C2P_GPGPUSIM_ROOT to the C2P GPGPU-Sim worktree" >&2; exit 2;
}
[[ -d "$C2P_GPGPUSIM_ROOT/.git" || -f "$C2P_GPGPUSIM_ROOT/.git" ]] || {
  echo "error: invalid C2P_GPGPUSIM_ROOT: $C2P_GPGPUSIM_ROOT" >&2; exit 2;
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sim_bin="$repo_root/gpu-simulator/bin/release/accel-sim.out"
[[ -x "$sim_bin" ]] || { echo "error: build $sim_bin first" >&2; exit 2; }
mkdir -p "$out_dir"
out_dir="$(cd "$out_dir" && pwd)"

config_dir="$(cd "$(dirname "$config")" && pwd)"
trace_dir="$(cd "$(dirname "$trace")" && pwd)"
for mode in ${modes//,/ }; do
  case "$mode" in baseline|oracle|ideal|c2p) ;; *)
    echo "error: invalid mode $mode" >&2; exit 2 ;; esac
  run_dir="$out_dir/$mode"
  mkdir -p "$run_dir"
  # A generated config can include the prior decoupled-L2 selector; C2P is
  # intentionally based on clean upstream GPGPU-Sim and must not parse it.
  sed '/^-gpgpu_l2_backend[[:space:]]/d' "$config" > "$run_dir/gpgpusim.config"
  for asset in "$config_dir"/*.xml "$config_dir"/*.icnt; do
    [[ -f "$asset" ]] && cp "$asset" "$run_dir/"
  done
  if [[ -n "$config_extra" ]]; then
    printf '\n# Experiment-specific base overrides\n' >> "$run_dir/gpgpusim.config"
    cat "$config_extra" >> "$run_dir/gpgpusim.config"
  fi
  case "$mode" in
    baseline)
      printf '\n-c2p_cache_enable 0\n-c2p_cache_oracle_only 0\n' >> "$run_dir/gpgpusim.config" ;;
    *)
      cat "$repo_root/configs/c2p-cache/$mode.config" >> "$run_dir/gpgpusim.config" ;;
  esac
  ln -sfn "$trace_dir" "$run_dir/traces"
  cp "$sim_bin" "$run_dir/accel-sim.out"
  {
    printf 'mode=%s\n' "$mode"
    printf 'gpgpusim_commit=%s\n' "$(git -C "$C2P_GPGPUSIM_ROOT" rev-parse HEAD)"
    printf 'accelsim_commit=%s\n' "$(git -C "$repo_root" rev-parse HEAD)"
    printf 'config_sha256=%s\n' "$(sha256sum "$run_dir/gpgpusim.config" | awk '{print $1}')"
    printf 'trace_sha256=%s\n' "$(sha256sum "$trace" | awk '{print $1}')"
    printf 'sim_sha256=%s\n' "$(sha256sum "$run_dir/accel-sim.out" | awk '{print $1}')"
  } > "$run_dir/provenance.txt"
  (
    cd "$run_dir"
    ./accel-sim.out -config ./gpgpusim.config -trace ./traces/kernelslist.g > run.out 2>&1
  )
  grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$run_dir/run.out"
  grep -E 'gpu_tot_sim_cycle =|c2p_(l1_misses|oracle_peer_hits|remote_hits|candidate_total)' \
      "$run_dir/run.out" > "$run_dir/summary.txt" || true
  printf 'PASS mode=%s run_dir=%s\n' "$mode" "$run_dir"
done
