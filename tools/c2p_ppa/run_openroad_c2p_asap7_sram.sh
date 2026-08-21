#!/usr/bin/env bash
# Run full macro-aware ASAP7 C2P single-lane PPA with real open SRAM views.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
asap7_sram_root=${C2P_ASAP7_SRAM_ROOT:-"$script_dir/third_party/asap7_sram_0p0"}
if [[ ! -f "$asap7_sram_root/generated/LEF/srambank_256x4x64_6t122.lef" ]]; then
    "$script_dir/fetch_asap7_sram.sh" "$asap7_sram_root"
fi

export C2P_PPA_TOP=c2p_cache_rtl
export C2P_PPA_TOP_PARAMS='-set USE_ASAP7_SRAM 1'
export C2P_PPA_RTL_FILES="$script_dir/rtl/c2p_snapshot_store.v $script_dir/rtl/c2p_snapshot_store_asap7.v $script_dir/rtl/c2p_snapshot_matrix.v $script_dir/rtl/c2p_query_engine.v $script_dir/rtl/c2p_cache_rtl.v $script_dir/rtl/srambank_256x4x64_6t122_blackbox.v"
export C2P_PPA_EXTRA_LEF="$asap7_sram_root/generated/LEF/srambank_256x4x64_6t122.lef"
export C2P_PPA_EXTRA_LIBERTY="$asap7_sram_root/generated/LIB/srambank_256x4x64_6t122.lib"
export C2P_PPA_FLOORPLAN_TCL="$script_dir/openroad/c2p_asap7_snapshot_floorplan.tcl"
export C2P_PPA_MACRO_SETUP_TCL="$script_dir/openroad/c2p_asap7_snapshot_macro_setup.tcl"
# Do not force 10 um buffering across real macro channels.  Ordinary repair
# still handles actual slew/capacitance violations.
export C2P_PPA_REPAIR_MAX_WIRE_LENGTH=${C2P_PPA_REPAIR_MAX_WIRE_LENGTH:-0}
export C2P_PPA_RESULT_DIR=${C2P_PPA_RESULT_DIR:-"$script_dir/results/openroad_c2p_asap7_sram"}
exec "$script_dir/run_openroad_control_proxy.sh"
