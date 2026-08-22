#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_cache_cases.sh --trace KERNELSLIST --config CONFIG --out-dir DIR
       [--modes baseline,oracle,ideal,c2p,ata,ccd,ring] [--config-extra FILE]
       [--mode-config-extra FILE]
       [--strip-mem-addr-mapping] [--skip-complete] [--build]

Run the same trace through selected C2P and prior-mechanism comparison points.
C2P_GPGPUSIM_ROOT
must name the matching hrl/c2p-cache-v0 worktree. CONFIG may be a generated
Accel-Sim config; legacy -gpgpu_l2_backend lines are removed because C2P uses
the clean upstream L2 baseline. For the stock QV100 base configuration pass
SM7_QV100/trace.config through --config-extra.
EOF
}

trace=""
config=""
out_dir=""
modes="baseline,oracle,ideal,c2p"
config_extras=()
mode_config_extras=()
strip_mem_addr_mapping=0
build=0
skip_complete=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace) trace="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --out-dir) out_dir="$2"; shift 2 ;;
    --modes) modes="$2"; shift 2 ;;
    --config-extra) config_extras+=("$2"); shift 2 ;;
    --mode-config-extra) mode_config_extras+=("$2"); shift 2 ;;
    --strip-mem-addr-mapping) strip_mem_addr_mapping=1; shift ;;
    --skip-complete) skip_complete=1; shift ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$trace" ]] || { echo "error: --trace must name kernelslist.g" >&2; exit 2; }
[[ -f "$config" ]] || { echo "error: --config must name a config" >&2; exit 2; }
[[ -n "$out_dir" ]] || { echo "error: --out-dir is required" >&2; exit 2; }
for config_extra in "${config_extras[@]}"; do
  [[ -f "$config_extra" ]] || {
    echo "error: --config-extra must exist: $config_extra" >&2; exit 2;
  }
done
for config_extra in "${mode_config_extras[@]}"; do
  [[ -f "$config_extra" ]] || {
    echo "error: --mode-config-extra must exist: $config_extra" >&2; exit 2;
  }
done
[[ -n "${C2P_GPGPUSIM_ROOT:-}" ]] || {
  echo "error: set C2P_GPGPUSIM_ROOT to the C2P GPGPU-Sim worktree" >&2; exit 2;
}
[[ -d "$C2P_GPGPUSIM_ROOT/.git" || -f "$C2P_GPGPUSIM_ROOT/.git" ]] || {
  echo "error: invalid C2P_GPGPUSIM_ROOT: $C2P_GPGPUSIM_ROOT" >&2; exit 2;
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sim_bin="$repo_root/gpu-simulator/bin/release/accel-sim.out"
if (( build )); then
  # The front end includes public GPGPU-Sim configuration headers.  Build it
  # against the selected worktree before copying the per-run simulator image;
  # loading a newer libcudart into an older front end can otherwise corrupt
  # configuration parsing before a trace starts.
  (
    export GPGPUSIM_ROOT="$C2P_GPGPUSIM_ROOT"
    set +u
    source "$C2P_GPGPUSIM_ROOT/setup_environment" >/dev/null
    export GPGPUSIM_SETUP_ENVIRONMENT_WAS_RUN=1
    source "$repo_root/gpu-simulator/setup_environment.sh" >/dev/null
    set -u
    make -C "$repo_root/gpu-simulator" -j1
  )
fi
[[ -x "$sim_bin" ]] || { echo "error: build $sim_bin first" >&2; exit 2; }
cudart_path="$(find "$C2P_GPGPUSIM_ROOT/lib" -type f -name libcudart.so -print -quit)"
[[ -n "$cudart_path" ]] || {
  echo "error: build libcudart.so in $C2P_GPGPUSIM_ROOT first" >&2; exit 2;
}
mkdir -p "$out_dir"
out_dir="$(cd "$out_dir" && pwd)"

config_dir="$(cd "$(dirname "$config")" && pwd)"
trace_dir="$(cd "$(dirname "$trace")" && pwd)"
for mode in ${modes//,/ }; do
  case "$mode" in
    baseline|oracle|ideal|c2p|ata|ccd|ring) ;;
    *) echo "error: invalid mode $mode" >&2; exit 2 ;;
  esac
  run_dir="$out_dir/$mode"
  if (( skip_complete )) && [[ -f "$run_dir/summary.txt" && -f "$run_dir/run.out" ]] && \
      grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$run_dir/run.out"; then
    printf 'SKIP completed mode=%s run_dir=%s\n' "$mode" "$run_dir"
    continue
  fi
  mkdir -p "$run_dir"
  # A generated config can include the prior decoupled-L2 selector; C2P is
  # intentionally based on clean upstream GPGPU-Sim and must not parse it.
  if (( strip_mem_addr_mapping )); then
    sed -e '/^-gpgpu_l2_backend[[:space:]]/d' \
        -e '/^-gpgpu_mem_addr_mapping[[:space:]]/d' \
        "$config" > "$run_dir/gpgpusim.config"
  else
    sed '/^-gpgpu_l2_backend[[:space:]]/d' "$config" > "$run_dir/gpgpusim.config"
  fi
  for asset in "$config_dir"/*.xml "$config_dir"/*.icnt; do
    [[ -f "$asset" ]] && cp "$asset" "$run_dir/"
  done
  for config_extra in "${config_extras[@]}"; do
    printf '\n# Experiment-specific base overrides\n' >> "$run_dir/gpgpusim.config"
    cat "$config_extra" >> "$run_dir/gpgpusim.config"
  done
  case "$mode" in
    baseline)
      printf '\n-c2p_cache_enable 0\n-c2p_cache_oracle_only 0\n' >> "$run_dir/gpgpusim.config" ;;
    oracle|ideal|c2p|ata|ccd|ring)
      # Every sharing comparison starts from the same explicitly pinned C2P
      # timing/queue baseline.  Mode files then change only the intended
      # mechanism selector.  Do not let ideal/ATA/CCD/RING silently inherit a
      # future C++ constructor default that C2P itself spells out here.
      cat "$repo_root/configs/c2p-cache/c2p.config" >> "$run_dir/gpgpusim.config"
      [[ "$mode" == c2p ]] || \
        cat "$repo_root/configs/c2p-cache/$mode.config" >> "$run_dir/gpgpusim.config" ;;
  esac
  for config_extra in "${mode_config_extras[@]}"; do
    printf '\n# Mode-specific experiment overrides\n' >> "$run_dir/gpgpusim.config"
    cat "$config_extra" >> "$run_dir/gpgpusim.config"
  done
  ln -sfn "$trace_dir" "$run_dir/traces"
  cp "$sim_bin" "$run_dir/accel-sim.out"
  {
    printf 'mode=%s\n' "$mode"
    printf 'gpgpusim_commit=%s\n' "$(git -C "$C2P_GPGPUSIM_ROOT" rev-parse HEAD)"
    printf 'accelsim_commit=%s\n' "$(git -C "$repo_root" rev-parse HEAD)"
    printf 'config_sha256=%s\n' "$(sha256sum "$run_dir/gpgpusim.config" | awk '{print $1}')"
    printf 'trace_sha256=%s\n' "$(sha256sum "$trace" | awk '{print $1}')"
    printf 'sim_sha256=%s\n' "$(sha256sum "$run_dir/accel-sim.out" | awk '{print $1}')"
    printf 'cudart_sha256=%s\n' "$(sha256sum "$cudart_path" | awk '{print $1}')"
  } > "$run_dir/provenance.txt"
  # Host-side scheduling metadata.  These values are deliberately kept out of
  # summary.txt: they describe this replay host, not an architectural result.
  # They make later campaign sizing reproducible without changing the copied
  # simulator, resolved configuration, or simulator stdout.
  host_start_epoch="$(date +%s)"
  host_start_utc="$(date --utc --iso-8601=seconds)"
  sim_rc=0
  if (
    # accel-sim.out dynamically links the selected GPGPU-Sim libcudart.  Do
    # not accidentally run against the host CUDA runtime, which may have the
    # same SONAME but lacks this branch's cache-model C++ symbols.
    export GPGPUSIM_ROOT="$C2P_GPGPUSIM_ROOT"
    set +u
    source "$C2P_GPGPUSIM_ROOT/setup_environment" >/dev/null
    set -u
    cd "$run_dir"
    /usr/bin/time \
      -f 'user_cpu_sec=%U\nsys_cpu_sec=%S\ncpu_percent=%P\nmax_rss_kib=%M\nexit_status=%x' \
      -o host_profile.txt \
      ./accel-sim.out -config ./gpgpusim.config -trace ./traces/kernelslist.g > run.out 2>&1
  ); then
    sim_rc=0
  else
    sim_rc=$?
  fi
  host_end_epoch="$(date +%s)"
  host_end_utc="$(date --utc --iso-8601=seconds)"
  {
    printf 'wall_start_utc=%s\n' "$host_start_utc"
    printf 'wall_end_utc=%s\n' "$host_end_utc"
    printf 'wall_elapsed_sec=%s\n' "$((host_end_epoch - host_start_epoch))"
  } >> "$run_dir/host_profile.txt"
  (( sim_rc == 0 )) || exit "$sim_rc"
  grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$run_dir/run.out"
  awk '
    /^gpu_tot_sim_cycle = / { cycle=$3 }
    /^gpu_sim_insn = / { insn=$3 }
    /^[[:space:]]*L2_total_cache_accesses = / { l2_total_accesses=$3 }
    /^[[:space:]]*L2_cache_stats_breakdown\[GLOBAL_ACC_R\]\[TOTAL_ACCESS\] = / {
      l2_global_read_accesses=$3
    }
    /^c2p_l1_misses = / { misses=$3 }
    /^c2p_oracle_peer_hits = / { oracle=$3 }
    /^c2p_queries_accepted = / { accepted=$3 }
    /^c2p_candidate_total = / { candidates=$3 }
    /^c2p_candidate_queries = / { candidate_queries=$3 }
    /^c2p_remote_hits = / { remote_hits=$3 }
    /^c2p_l2_requests_avoided = / { l2_avoided=$3 }
    /^c2p_peer_probes = / { probes=$3 }
    /^c2p_peer_probe_hits = / { probe_hits=$3 }
    /^c2p_peer_probe_misses = / { probe_misses=$3 }
    /^c2p_peer_l1_accesses = / { peer_l1_accesses=$3 }
    /^c2p_target_probe_port_busy_cycles = / { target_port_busy_cycles=$3 }
    /^c2p_target_tag_port_busy_cycles = / { target_tag_port_busy_cycles=$3 }
    /^c2p_target_probe_queue_wait_cycles = / { target_queue_wait_cycles=$3 }
    /^c2p_target_probe_queue_full_cycles = / { target_queue_full_cycles=$3 }
    /^c2p_requester_fill_wait_cycles = / { requester_fill_wait_cycles=$3 }
    /^c2p_residence_encode_cycles = / { residence_encode_cycles=$3 }
    /^c2p_residence_rows_cycles = / { residence_rows_cycles=$3 }
    /^c2p_residence_match_cycles = / { residence_match_cycles=$3 }
    /^c2p_residence_ready_cycles = / { residence_ready_cycles=$3 }
    /^c2p_residence_target_probe_cycles = / { residence_target_probe_cycles=$3 }
    /^c2p_residence_probe_cycles = / { residence_probe_cycles=$3 }
    /^c2p_residence_return_cycles = / { residence_return_cycles=$3 }
    /^c2p_residence_fallback_cycles = / { residence_fallback_cycles=$3 }
    /^c2p_remote_hit_probe_ordinal_total = / { remote_hit_probe_ordinal_total=$3 }
    /^c2p_remote_hit_probe_ordinal_samples = / { remote_hit_probe_ordinal_samples=$3 }
    /^c2p_fallback_probe_ordinal_total = / { fallback_probe_ordinal_total=$3 }
    /^c2p_fallback_probe_ordinal_samples = / { fallback_probe_ordinal_samples=$3 }
    /^c2p_fallback_target_wait_timeout = / { fallback_target_wait_timeout=$3 }
    /^c2p_fallback_target_admission_timeout = / { fallback_target_admission_timeout=$3 }
    /^c2p_peer_lost_before_query = / { peer_lost_before_query=$3 }
    /^c2p_peer_gained_before_query = / { peer_gained_before_query=$3 }
    /^c2p_queries_queue_bypass = / { queue_bypass=$3 }
    /^c2p_updates_queue_bypass = / { update_queue_bypass=$3 }
    /^c2p_fallback_no_candidate = / { no_candidate=$3 }
    /^c2p_fallback_candidates_exhausted = / { candidates_exhausted=$3 }
    /^c2p_fallback_candidate_budget = / { candidate_budget=$3 }
    /^c2p_fallback_probe_timeout = / { probe_timeout=$3 }
    /^c2p_fallback_queue = / { fallback_queue=$3 }
    /^c2p_snapshot_false_positive = / { false_positive=$3 }
    /^c2p_snapshot_false_negative = / { false_negative=$3 }
    /^c2p_snapshot_true_positive = / { true_positive=$3 }
    /^c2p_snapshot_true_negative = / { true_negative=$3 }
    /^c2p_snapshot_query_false_positive = / { query_false_positive=$3 }
    /^c2p_snapshot_query_false_negative = / { query_false_negative=$3 }
    /^c2p_snapshot_query_true_positive = / { query_true_positive=$3 }
    /^c2p_snapshot_query_true_negative = / { query_true_negative=$3 }
    /^c2p_ccd_false_positive = / { ccd_false_positive=$3 }
    /^c2p_ccd_false_negative = / { ccd_false_negative=$3 }
    /^c2p_ccd_true_positive = / { ccd_true_positive=$3 }
    /^c2p_ccd_true_negative = / { ccd_true_negative=$3 }
    /^c2p_peer_access_hit_samples = / { peer_hit_samples=$3 }
    /^c2p_peer_access_hit_p90 = / { peer_hit_p90=$3 }
    /^c2p_peer_access_hit_p95 = / { peer_hit_p95=$3 }
    /^c2p_peer_access_hit_p99 = / { peer_hit_p99=$3 }
    /^c2p_peer_access_hit_max = / { peer_hit_max=$3 }
    /^c2p_peer_access_miss_samples = / { peer_miss_samples=$3 }
    /^c2p_peer_access_miss_p90 = / { peer_miss_p90=$3 }
    /^c2p_peer_access_miss_p95 = / { peer_miss_p95=$3 }
    /^c2p_peer_access_miss_p99 = / { peer_miss_p99=$3 }
    /^c2p_peer_access_miss_max = / { peer_miss_max=$3 }
    /^c2p_snapshot_updates = / { updates=$3 }
    /^c2p_snapshot_rebuilds = / { rebuilds=$3 }
    /^c2p_snapshot_rebuild_transport_tags = / { rebuild_tags=$3 }
    END {
      printf "gpu_tot_sim_cycle = %s\n", cycle
      printf "gpu_sim_insn = %s\n", insn
      printf "l2_total_cache_accesses = %s\n", l2_total_accesses
      printf "l2_global_read_accesses = %s\n", l2_global_read_accesses
      printf "c2p_l1_misses = %s\n", misses
      printf "c2p_oracle_peer_hits = %s\n", oracle
      printf "c2p_queries_accepted = %s\n", accepted
      printf "c2p_candidate_total = %s\n", candidates
      printf "c2p_candidate_queries = %s\n", candidate_queries
      printf "c2p_peer_probes = %s\n", probes
      printf "c2p_peer_probe_hits = %s\n", probe_hits
      printf "c2p_peer_probe_misses = %s\n", probe_misses
      printf "c2p_peer_l1_accesses = %s\n", peer_l1_accesses
      printf "c2p_target_probe_port_busy_cycles = %s\n", target_port_busy_cycles
      printf "c2p_target_tag_port_busy_cycles = %s\n", target_tag_port_busy_cycles
      printf "c2p_target_probe_queue_wait_cycles = %s\n", target_queue_wait_cycles
      printf "c2p_target_probe_queue_full_cycles = %s\n", target_queue_full_cycles
      printf "c2p_requester_fill_wait_cycles = %s\n", requester_fill_wait_cycles
      printf "c2p_residence_encode_cycles = %s\n", residence_encode_cycles
      printf "c2p_residence_rows_cycles = %s\n", residence_rows_cycles
      printf "c2p_residence_match_cycles = %s\n", residence_match_cycles
      printf "c2p_residence_ready_cycles = %s\n", residence_ready_cycles
      printf "c2p_residence_target_probe_cycles = %s\n", residence_target_probe_cycles
      printf "c2p_residence_probe_cycles = %s\n", residence_probe_cycles
      printf "c2p_residence_return_cycles = %s\n", residence_return_cycles
      printf "c2p_residence_fallback_cycles = %s\n", residence_fallback_cycles
      printf "c2p_remote_hit_probe_ordinal_total = %s\n", remote_hit_probe_ordinal_total
      printf "c2p_remote_hit_probe_ordinal_samples = %s\n", remote_hit_probe_ordinal_samples
      printf "c2p_fallback_probe_ordinal_total = %s\n", fallback_probe_ordinal_total
      printf "c2p_fallback_probe_ordinal_samples = %s\n", fallback_probe_ordinal_samples
      printf "c2p_fallback_target_wait_timeout = %s\n", fallback_target_wait_timeout
      printf "c2p_fallback_target_admission_timeout = %s\n", fallback_target_admission_timeout
      printf "c2p_peer_lost_before_query = %s\n", peer_lost_before_query
      printf "c2p_peer_gained_before_query = %s\n", peer_gained_before_query
      printf "c2p_remote_hits = %s\n", remote_hits
      printf "c2p_l2_requests_avoided = %s\n", l2_avoided
      printf "c2p_queries_queue_bypass = %s\n", queue_bypass
      printf "c2p_updates_queue_bypass = %s\n", update_queue_bypass
      printf "c2p_fallback_no_candidate = %s\n", no_candidate
      printf "c2p_fallback_candidates_exhausted = %s\n", candidates_exhausted
      printf "c2p_fallback_candidate_budget = %s\n", candidate_budget
      printf "c2p_fallback_probe_timeout = %s\n", probe_timeout
      printf "c2p_fallback_queue = %s\n", fallback_queue
      printf "c2p_snapshot_false_positive = %s\n", false_positive
      printf "c2p_snapshot_false_negative = %s\n", false_negative
      printf "c2p_snapshot_true_positive = %s\n", true_positive
      printf "c2p_snapshot_true_negative = %s\n", true_negative
      printf "c2p_snapshot_query_false_positive = %s\n", query_false_positive
      printf "c2p_snapshot_query_false_negative = %s\n", query_false_negative
      printf "c2p_snapshot_query_true_positive = %s\n", query_true_positive
      printf "c2p_snapshot_query_true_negative = %s\n", query_true_negative
      printf "c2p_ccd_false_positive = %s\n", ccd_false_positive
      printf "c2p_ccd_false_negative = %s\n", ccd_false_negative
      printf "c2p_ccd_true_positive = %s\n", ccd_true_positive
      printf "c2p_ccd_true_negative = %s\n", ccd_true_negative
      printf "c2p_peer_access_hit_samples = %s\n", peer_hit_samples
      printf "c2p_peer_access_hit_p90 = %s\n", peer_hit_p90
      printf "c2p_peer_access_hit_p95 = %s\n", peer_hit_p95
      printf "c2p_peer_access_hit_p99 = %s\n", peer_hit_p99
      printf "c2p_peer_access_hit_max = %s\n", peer_hit_max
      printf "c2p_peer_access_miss_samples = %s\n", peer_miss_samples
      printf "c2p_peer_access_miss_p90 = %s\n", peer_miss_p90
      printf "c2p_peer_access_miss_p95 = %s\n", peer_miss_p95
      printf "c2p_peer_access_miss_p99 = %s\n", peer_miss_p99
      printf "c2p_peer_access_miss_max = %s\n", peer_miss_max
      printf "c2p_snapshot_updates = %s\n", updates
      printf "c2p_snapshot_rebuilds = %s\n", rebuilds
      printf "c2p_snapshot_rebuild_transport_tags = %s\n", rebuild_tags
    }
  ' "$run_dir/run.out" > "$run_dir/summary.txt"
  # The adaptive-policy observation counters are intentionally emitted as a
  # small indexed family.  Keep them verbatim rather than teaching this
  # generic runner every future histogram bin; legacy summary consumers simply
  # ignore the additional keys.
  grep -E '^c2p_(probe_ordinal_|probe_pc_bucket_|continuation_after_fail_|adaptive_)' \
      "$run_dir/run.out" >> "$run_dir/summary.txt" || true
  printf 'PASS mode=%s run_dir=%s\n' "$mode" "$run_dir"
done
