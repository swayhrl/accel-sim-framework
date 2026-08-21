#!/usr/bin/env bash
# Implement the integrated C2P lane once real Snapshot SRAM macro views exist.
# This script intentionally refuses to substitute behavioural SRAM for a PPA
# macro: use run_openroad_c2p_query_engine.sh for the control-only result.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
: "${C2P_SNAPSHOT_MACRO_VERILOG:?set the macro implementation/black-box Verilog}"
: "${C2P_SNAPSHOT_MACRO_LEF:?set the Snapshot macro LEF}"
: "${C2P_SNAPSHOT_MACRO_LIBERTY:?set the Snapshot macro Liberty}"
: "${C2P_SNAPSHOT_MACRO_SETUP_TCL:?set the macro placement/PDN setup Tcl}"

for path in "$C2P_SNAPSHOT_MACRO_VERILOG" "$C2P_SNAPSHOT_MACRO_LEF" \
            "$C2P_SNAPSHOT_MACRO_LIBERTY" "$C2P_SNAPSHOT_MACRO_SETUP_TCL"; do
    [[ -f "$path" ]] || { echo "missing macro integration file: $path" >&2; exit 2; }
done

export C2P_PPA_TOP=c2p_cache_rtl
export C2P_PPA_TOP_PARAMS='-set USE_SRAM_MACRO 1'
export C2P_PPA_RTL_FILES="$script_dir/rtl/c2p_snapshot_store.v $script_dir/rtl/c2p_snapshot_matrix.v $script_dir/rtl/c2p_query_engine.v $script_dir/rtl/c2p_cache_rtl.v $C2P_SNAPSHOT_MACRO_VERILOG"
export C2P_PPA_EXTRA_LEF="$C2P_SNAPSHOT_MACRO_LEF"
export C2P_PPA_EXTRA_LIBERTY="$C2P_SNAPSHOT_MACRO_LIBERTY"
export C2P_PPA_MACRO_SETUP_TCL="$C2P_SNAPSHOT_MACRO_SETUP_TCL"
export C2P_PPA_RESULT_DIR=${C2P_PPA_RESULT_DIR:-"$script_dir/results/openroad_c2p_cache_rtl"}
exec "$script_dir/run_openroad_control_proxy.sh"
