#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
iverilog_bin=${C2P_IVERILOG_BIN:-iverilog}
out_dir=${1:-"$script_dir/results/rtl_test"}
mkdir -p "$out_dir"

"$iverilog_bin" -g2012 -s tb_c2p_cache_rtl -o "$out_dir/tb_c2p_cache_rtl.vvp" \
    "$script_dir/rtl/c2p_snapshot_store.v" \
    "$script_dir/rtl/c2p_snapshot_matrix.v" \
    "$script_dir/rtl/c2p_query_engine.v" \
    "$script_dir/rtl/c2p_cache_rtl.v" \
    "$script_dir/tb/tb_c2p_cache_rtl.v"
vvp "$out_dir/tb_c2p_cache_rtl.vvp" | tee "$out_dir/sim.log"
rg -q '^PASS tb_c2p_cache_rtl$' "$out_dir/sim.log"
"$iverilog_bin" -g2012 -s tb_c2p_cache_rtl \
    -P tb_c2p_cache_rtl.USE_SRAM_MACRO=1 \
    -o "$out_dir/tb_c2p_cache_rtl_macro.vvp" \
    "$script_dir/rtl/c2p_snapshot_store.v" \
    "$script_dir/rtl/c2p_snapshot_matrix.v" \
    "$script_dir/rtl/c2p_query_engine.v" \
    "$script_dir/rtl/c2p_cache_rtl.v" \
    "$script_dir/tb/tb_c2p_cache_rtl.v"
vvp "$out_dir/tb_c2p_cache_rtl_macro.vvp" | tee "$out_dir/sim_macro.log"
rg -q '^PASS tb_c2p_cache_rtl$' "$out_dir/sim_macro.log"
printf 'PASS c2p_rtl_test result_dir=%s\n' "$out_dir"
