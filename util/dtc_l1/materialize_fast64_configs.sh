#!/usr/bin/env bash
# Materialize the FAST64 resolved configs from the frozen M5 DTC configs.
# The only imported C2P properties are the approved 64x1 platform shell and
# its 20-partition/L2 timing path.  No C2P cache/peer option is emitted.
set -euo pipefail

usage() {
  echo "usage: $0 [--cap N] [--suffix TEXT]" >&2
  exit 2
}

cap=8192
suffix=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --cap) cap=${2:-}; shift 2 ;;
    --suffix) suffix=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
[[ "$cap" =~ ^[1-9][0-9]*$ ]] || usage

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
source_dir="$repo_root/configs/dtc_l1/m5"
output_dir="$repo_root/configs/dtc_l1/fast64"

mkdir -p "$output_dir"

for mode in BASE IO OO; do
  input="$source_dir/PAPER_${mode}_16KB.config"
  output="$output_dir/FAST64_${mode}${suffix}.config"
  test -r "$input"

  # The M5 input carries an explicit 32-channel address mapping.  That mapping
  # cannot represent FAST64's approved non-IPOLY 20-partition shell, so remove
  # it before appending the source-backed platform overlay below.
  sed '/^-gpgpu_mem_addr_mapping[[:space:]]/d' "$input" >"$output"
  cat >>"$output" <<'EOF'

# FAST64 64x1 platform shell.  Imported from the C2P shell only; no C2P
# cache, peer, Snapshot Matrix, ATA, CCD, or RING option is present.
-gpgpu_n_clusters 64
-gpgpu_n_cores_per_cluster 1
-gpgpu_occupancy_sm_number 64
-gpgpu_clock_domains 1410.0:1410.0:1410.0:850.0
-gpgpu_scheduler gto
-gpgpu_n_mem 20
-gpgpu_n_sub_partition_per_mchannel 2
-gpgpu_memory_partition_indexing 0
-gpgpu_cache:dl2 S:128:128:16,L:B:m:L:L,A:192:4,32:0,32
-gpgpu_l2_rop_latency 200

# FAST64 DTC mechanism contract, recorded explicitly for resolved-config
# identity.  The selected PAPER_* source config remains the sole mode selector.
-gpgpu_l1_cache_write_ratio 0
-gpgpu_dtc_l1_pib_entries 8
-gpgpu_dtc_l1_mshr_entries 32
-gpgpu_dtc_l1_lower_outstanding_cap __FAST64_LOWER_CAP__
-gpgpu_dtc_l1_tag_banks 4
-gpgpu_dtc_l1_tag_req_per_bank 1
-gpgpu_dtc_l1_tag_req_per_cycle 4
-gpgpu_dtc_l1_logical_sets 32
-gpgpu_dtc_l1_logical_ways 4
-gpgpu_dtc_l1_physical_lines 640
-gpgpu_dtc_l1_allocation_width 4
-gpgpu_dtc_l1_io_pib_entries 256
-gpgpu_dtc_l1_oo_pib_entries 128
-gpgpu_dtc_l1_ref_count_bits 13

# A1 observer, previously proven terminal-equivalent in M5.
-gpgpu_runtime_stat 500000
EOF
  sed -i "s/__FAST64_LOWER_CAP__/$cap/" "$output"
done

printf 'materialized FAST64 cap=%s configs in %s\n' "$cap" "$output_dir"
