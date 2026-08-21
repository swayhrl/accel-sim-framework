#!/usr/bin/env bash
# Run a concrete OpenROAD implementation of a selected C2P standard-cell top.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
result_dir=${C2P_PPA_RESULT_DIR:-"$script_dir/results/openroad_control_proxy"}
top=${C2P_PPA_TOP:-c2p_control_proxy}
rtl_files=${C2P_PPA_RTL_FILES:-"$script_dir/rtl/c2p_control_proxy.v"}
orfs_root=${C2P_ORFS_ROOT:?set C2P_ORFS_ROOT to an OpenROAD-flow-scripts checkout}
stop_after_synth=${C2P_PPA_STOP_AFTER_SYNTH:-0}
abc_delay=${C2P_PPA_ABC_DELAY_PS:-}
yosys_bin=${C2P_YOSYS_BIN:-yosys}
platform_dir="$orfs_root/flow/platforms/asap7"
lib_dir="$platform_dir/lib/NLDM"

if [[ "$stop_after_synth" != 0 && "$stop_after_synth" != 1 ]]; then
    echo 'C2P_PPA_STOP_AFTER_SYNTH must be 0 or 1' >&2
    exit 2
fi
if [[ -n "$abc_delay" && ! "$abc_delay" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    echo 'C2P_PPA_ABC_DELAY_PS must be a positive number of ps' >&2
    exit 2
fi
if [[ "$stop_after_synth" == 0 ]]; then
    openroad_bin=${C2P_OPENROAD_BIN:?set C2P_OPENROAD_BIN to an OpenROAD executable}
fi

require_file() {
    if [[ ! -f "$1" ]]; then
        echo "missing required file: $1" >&2
        exit 2
    fi
}

for path in \
    "$platform_dir/lef/asap7_tech_1x_201209.lef" \
    "$platform_dir/lef/asap7sc7p5t_28_R_1x_220121a.lef" \
    "$platform_dir/openRoad/make_tracks.tcl" \
    "$platform_dir/setRC.tcl" \
    "$platform_dir/openRoad/tapcell.tcl" \
    "$platform_dir/openRoad/pdn/grid_strategy-M1-M2-M5-M6.tcl" \
    "$lib_dir/asap7sc7p5t_SIMPLE_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_INVBUF_RVT_TT_nldm_220122.lib.gz" \
    "$lib_dir/asap7sc7p5t_AO_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_OA_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_SEQ_RVT_TT_nldm_220123.lib"; do
    require_file "$path"
done
if [[ "$stop_after_synth" == 0 ]]; then
    require_file "$openroad_bin"
fi
command -v "$yosys_bin" >/dev/null

mkdir -p "$result_dir"
merged_lib="$result_dir/asap7_rvt_tt_merged.lib"
mapped_netlist="$result_dir/${top}_mapped.v"

python3 "$script_dir/make_asap7_lib_bundle.py" "$merged_lib" \
    "$lib_dir/asap7sc7p5t_SIMPLE_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_INVBUF_RVT_TT_nldm_220122.lib.gz" \
    "$lib_dir/asap7sc7p5t_AO_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_OA_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_SEQ_RVT_TT_nldm_220123.lib"

"$yosys_bin" -ql "$result_dir/yosys.log" -p "
    read_verilog $rtl_files
    hierarchy -check -top $top
    proc; opt; memory; opt; techmap; opt
    dfflibmap -liberty $merged_lib
    abc -liberty $merged_lib ${abc_delay:+-D $abc_delay}
    clean
    # The loop iterator is elaboration-only but OpenROAD's Verilog reader does
    # not accept Yosys' preserved signed declaration for it.
    delete w:i
    # OpenROAD's Verilog reader also rejects escaped function-temporary names
    # that include source-file punctuation.  Keep the mapped connectivity but
    # normalize every public generated object before export.
    rename -unescape w:* c:*
    stat -liberty $merged_lib
    write_verilog -noattr $mapped_netlist
"
# The OpenROAD Verilog reader in the pinned build accepts mapped gates but not
# Verilog's optional `wire signed` declaration.  Mapping has already resolved
# all arithmetic into gates, so this export-only normalization changes neither
# Boolean connectivity nor timing arcs.
sed -i 's/\<wire signed\>/wire/g' "$mapped_netlist"

if [[ "$stop_after_synth" == 1 ]]; then
    echo "Synthesis result: $mapped_netlist"
    exit 0
fi

export C2P_PPA_RESULT_DIR="$result_dir"
export C2P_PPA_TOP="$top"
export C2P_PPA_MAPPED_NETLIST="$mapped_netlist"
export C2P_ASAP7_TECH_LEF="$platform_dir/lef/asap7_tech_1x_201209.lef"
export C2P_ASAP7_CELL_LEF="$platform_dir/lef/asap7sc7p5t_28_R_1x_220121a.lef"
export C2P_ASAP7_MERGED_LIB="$merged_lib"
export C2P_ASAP7_MAKE_TRACKS="$platform_dir/openRoad/make_tracks.tcl"
export C2P_ASAP7_SET_RC="$platform_dir/setRC.tcl"
export C2P_ASAP7_TAP_TCL="$platform_dir/openRoad/tapcell.tcl"
export C2P_ASAP7_PDN_TCL="$platform_dir/openRoad/pdn/grid_strategy-M1-M2-M5-M6.tcl"

"$openroad_bin" -no_init -exit "$script_dir/openroad/c2p_control_proxy.tcl" \
    | tee "$result_dir/openroad.log"

echo "OpenROAD results: $result_dir"
