#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
iverilog_bin=${C2P_IVERILOG_BIN:-iverilog}
asap7_sram_root=${C2P_ASAP7_SRAM_ROOT:-"$script_dir/third_party/asap7_sram_0p0"}
out_dir=${1:-"$script_dir/results/rtl_test"}
mkdir -p "$out_dir"

"$iverilog_bin" -g2012 -s tb_c2p_bf_engine -o "$out_dir/tb_c2p_bf_engine.vvp" \
    "$script_dir/rtl/c2p_bf_engine.v" \
    "$script_dir/tb/tb_c2p_bf_engine.v"
vvp "$out_dir/tb_c2p_bf_engine.vvp" | tee "$out_dir/sim_bf_engine.log"
rg -q '^PASS tb_c2p_bf_engine$' "$out_dir/sim_bf_engine.log"

"$iverilog_bin" -g2012 -s tb_c2p_snapshot_bank_arbiter \
    -o "$out_dir/tb_c2p_snapshot_bank_arbiter.vvp" \
    "$script_dir/rtl/c2p_snapshot_bank_copy_arbiter.v" \
    "$script_dir/rtl/c2p_snapshot_bank_arbiter.v" \
    "$script_dir/tb/tb_c2p_snapshot_bank_arbiter.v"
vvp "$out_dir/tb_c2p_snapshot_bank_arbiter.vvp" | tee "$out_dir/sim_bank_arbiter.log"
rg -q '^PASS tb_c2p_snapshot_bank_arbiter$' "$out_dir/sim_bank_arbiter.log"

"$iverilog_bin" -g2012 -s tb_c2p_snapshot_banked_frontend \
    -o "$out_dir/tb_c2p_snapshot_banked_frontend.vvp" \
    "$script_dir/rtl/c2p_bf_engine.v" \
    "$script_dir/rtl/c2p_bf_engine_array.v" \
    "$script_dir/rtl/c2p_snapshot_bank_copy_arbiter.v" \
    "$script_dir/rtl/c2p_snapshot_bank_arbiter.v" \
    "$script_dir/rtl/c2p_snapshot_banked_frontend.v" \
    "$script_dir/tb/tb_c2p_snapshot_banked_frontend.v"
vvp "$out_dir/tb_c2p_snapshot_banked_frontend.vvp" | tee "$out_dir/sim_banked_frontend.log"
rg -q '^PASS tb_c2p_snapshot_banked_frontend$' "$out_dir/sim_banked_frontend.log"

"$iverilog_bin" -g2012 -s tb_c2p_cache_rtl -o "$out_dir/tb_c2p_cache_rtl.vvp" \
    "$script_dir/rtl/c2p_snapshot_store.v" \
    "$script_dir/rtl/c2p_bf_engine.v" \
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
    "$script_dir/rtl/c2p_bf_engine.v" \
    "$script_dir/rtl/c2p_snapshot_matrix.v" \
    "$script_dir/rtl/c2p_query_engine.v" \
    "$script_dir/rtl/c2p_cache_rtl.v" \
    "$script_dir/tb/tb_c2p_cache_rtl.v"
vvp "$out_dir/tb_c2p_cache_rtl_macro.vvp" | tee "$out_dir/sim_macro.log"
rg -q '^PASS tb_c2p_cache_rtl$' "$out_dir/sim_macro.log"
if [[ ! -f "$asap7_sram_root/generated/verilog/srambank_256x4x64_6t122.v" ]]; then
    "$script_dir/fetch_asap7_sram.sh" "$asap7_sram_root"
fi
"$iverilog_bin" -g2012 -s tb_c2p_cache_rtl \
    -P tb_c2p_cache_rtl.USE_ASAP7_SRAM=1 \
    -o "$out_dir/tb_c2p_cache_rtl_asap7.vvp" \
    "$script_dir/rtl/c2p_snapshot_store.v" \
    "$script_dir/rtl/c2p_snapshot_store_asap7.v" \
    "$script_dir/rtl/c2p_bf_engine.v" \
    "$script_dir/rtl/c2p_snapshot_matrix.v" \
    "$script_dir/rtl/c2p_query_engine.v" \
    "$script_dir/rtl/c2p_cache_rtl.v" \
    "$asap7_sram_root/generated/verilog/srambank_256x4x64_6t122.v" \
    "$script_dir/tb/tb_c2p_cache_rtl.v"
vvp "$out_dir/tb_c2p_cache_rtl_asap7.vvp" | tee "$out_dir/sim_asap7.log"
rg -q '^PASS tb_c2p_cache_rtl$' "$out_dir/sim_asap7.log"
printf 'PASS c2p_rtl_test result_dir=%s\n' "$out_dir"
