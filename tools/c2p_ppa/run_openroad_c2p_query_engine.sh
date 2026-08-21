#!/usr/bin/env bash
# Physically implement the real C2P single-query control lane.  Snapshot SRAM
# remains outside this top as an explicit macro boundary; use the CACTI result
# and a foundry macro view when reporting total C2P PPA.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
export C2P_PPA_TOP=c2p_query_engine
export C2P_PPA_RTL_FILES="$script_dir/rtl/c2p_query_engine.v"
export C2P_PPA_RESULT_DIR=${C2P_PPA_RESULT_DIR:-"$script_dir/results/openroad_c2p_query_engine"}
exec "$script_dir/run_openroad_control_proxy.sh"
