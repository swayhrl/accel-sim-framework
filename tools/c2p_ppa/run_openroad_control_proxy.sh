#!/usr/bin/env bash
# Run a concrete OpenROAD implementation of the C2P control-slice proxy.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
result_dir=${C2P_PPA_RESULT_DIR:-"$script_dir/results/openroad_control_proxy"}
orfs_root=${C2P_ORFS_ROOT:?set C2P_ORFS_ROOT to an OpenROAD-flow-scripts checkout}
openroad_bin=${C2P_OPENROAD_BIN:?set C2P_OPENROAD_BIN to an OpenROAD executable}
yosys_bin=${C2P_YOSYS_BIN:-yosys}
platform_dir="$orfs_root/flow/platforms/asap7"
lib_dir="$platform_dir/lib/NLDM"

require_file() {
    if [[ ! -f "$1" ]]; then
        echo "missing required file: $1" >&2
        exit 2
    fi
}

for path in \
    "$openroad_bin" \
    "$platform_dir/lef/asap7_tech_1x_201209.lef" \
    "$platform_dir/lef/asap7sc7p5t_28_R_1x_220121a.lef" \
    "$platform_dir/openRoad/make_tracks.tcl" \
    "$platform_dir/setRC.tcl" \
    "$lib_dir/asap7sc7p5t_SIMPLE_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_INVBUF_RVT_TT_nldm_220122.lib.gz" \
    "$lib_dir/asap7sc7p5t_AO_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_OA_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_SEQ_RVT_TT_nldm_220123.lib"; do
    require_file "$path"
done
command -v "$yosys_bin" >/dev/null

mkdir -p "$result_dir"
merged_lib="$result_dir/asap7_rvt_tt_merged.lib"
mapped_netlist="$result_dir/c2p_control_proxy_mapped.v"

python3 "$script_dir/make_asap7_lib_bundle.py" "$merged_lib" \
    "$lib_dir/asap7sc7p5t_SIMPLE_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_INVBUF_RVT_TT_nldm_220122.lib.gz" \
    "$lib_dir/asap7sc7p5t_AO_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_OA_RVT_TT_nldm_211120.lib.gz" \
    "$lib_dir/asap7sc7p5t_SEQ_RVT_TT_nldm_220123.lib"

"$yosys_bin" -ql "$result_dir/yosys.log" -p "
    read_verilog $script_dir/rtl/c2p_control_proxy.v
    hierarchy -check -top c2p_control_proxy
    proc; opt; memory; opt; techmap; opt
    dfflibmap -liberty $merged_lib
    abc -liberty $merged_lib
    clean
    # The loop iterator is elaboration-only but OpenROAD's Verilog reader does
    # not accept Yosys' preserved signed declaration for it.
    delete w:i
    stat -liberty $merged_lib
    write_verilog -noattr $mapped_netlist
"

export C2P_PPA_RESULT_DIR="$result_dir"
export C2P_PPA_MAPPED_NETLIST="$mapped_netlist"
export C2P_ASAP7_TECH_LEF="$platform_dir/lef/asap7_tech_1x_201209.lef"
export C2P_ASAP7_CELL_LEF="$platform_dir/lef/asap7sc7p5t_28_R_1x_220121a.lef"
export C2P_ASAP7_MERGED_LIB="$merged_lib"
export C2P_ASAP7_MAKE_TRACKS="$platform_dir/openRoad/make_tracks.tcl"
export C2P_ASAP7_SET_RC="$platform_dir/setRC.tcl"

"$openroad_bin" -no_init -exit "$script_dir/openroad/c2p_control_proxy.tcl" \
    | tee "$result_dir/openroad.log"

echo "OpenROAD results: $result_dir"
