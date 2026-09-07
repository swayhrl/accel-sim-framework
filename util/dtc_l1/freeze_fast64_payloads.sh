#!/usr/bin/env bash
# Freeze the ordered FAST12 C2P trace payload identity without copying traces.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
out_dir="$repo_root/docs/dtc_l1/fast64/generated"
mkdir -p "$out_dir"
members="$out_dir/FAST64_PAYLOAD_MEMBERS.tsv"
summary="$out_dir/FAST64_PAYLOAD_MANIFEST.tsv"

cat >"$members" <<'EOF'
workload	trace_root	ordinal	member	bytes	sha256
EOF
cat >"$summary" <<'EOF'
workload	trace_root	kernelslist_g_sha256	traceg_members	traceg_bytes	ordered_traceg_set_sha256	trace_format	provenance_label
EOF

declare -A roots=(
  [atax]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/polybench-atax/NO_ARGS/traces'
  [bicg]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/polybench-bicg/NO_ARGS/traces'
  [gesummv]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/polybench-gesummv/NO_ARGS/traces'
  [gemm]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/polybench-gemm/NO_ARGS/traces'
  [2DConvolution]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/polybench-2DConvolution/NO_ARGS/traces'
  [btree]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/b+tree-rodinia-3.1/file___data_mil_txt_command___data_command_txt/traces'
  [dwt2d]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/dwt2d-rodinia-3.1/__data_rgb_bmp__d_1024x1024__f__5__l_3/traces'
  [gaussian]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/gaussian-rodinia-3.1/_s_256/traces'
  [hotspot1]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/hotspot-rodinia-3.1/1024_2_2___data_temp_1024___data_power_1024_output_out/traces'
  [lud]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/lud-rodinia-3.1/_i___data_512_dat/traces'
  [nn]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/nn-rodinia-3.1/__data_filelist_4__r_5__lat_30__lng_90/traces'
  [mri-q]='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-mri-q/_i___data_small_input_32_32_32_dataset_bin__o_32_32_32_dataset_out/traces'
)
workloads=(atax bicg gesummv gemm 2DConvolution btree dwt2d gaussian hotspot1 lud nn mri-q)

for workload in "${workloads[@]}"; do
  root=${roots[$workload]}
  list="$root/kernelslist.g"
  test -r "$list"
  list_sha=$(sha256sum "$list" | awk '{print $1}')
  ordinal=0
  total=0
  set_file=$(mktemp /tmp/fast64-payload-set-XXXXXX)
  while IFS= read -r member || [ -n "$member" ]; do
    case "$member" in
      *.traceg)
        path="$root/$member"
        test -r "$path"
        ordinal=$((ordinal + 1))
        bytes=$(stat -c '%s' "$path")
        sha=$(sha256sum "$path" | awk '{print $1}')
        total=$((total + bytes))
        printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$workload" "$root" "$ordinal" "$member" "$bytes" "$sha" >>"$members"
        printf '%08d\t%s\t%s\n' "$ordinal" "$member" "$sha" >>"$set_file"
        ;;
    esac
  done <"$list"
  test "$ordinal" -gt 0
  set_sha=$(sha256sum "$set_file" | awk '{print $1}')
  rm -f "$set_file"
  printf '%s\t%s\t%s\t%s\t%s\t%s\tNVBit-v1.4-text-traceg\tC2P_CANONICAL_TRACE_REUSED_FOR_DTC_FAST64\n' \
    "$workload" "$root" "$list_sha" "$ordinal" "$total" "$set_sha" >>"$summary"
done

printf 'wrote %s and %s\n' "$members" "$summary"
