#!/usr/bin/env bash
# Map or physically implement the complete 128-engine C2P Snapshot front end.
#
# The top exposes its internal 256-command/256-response array directly, so
# its 66,050 top-level pins need a deliberately sparse proxy floorplan.  This
# is a reproducibility fixture for the scalable control plane, not a chip-top
# PPA result; a real L2 integration absorbs these ports in local bank queues.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

export C2P_PPA_TOP=c2p_snapshot_banked_frontend
export C2P_PPA_RTL_FILES="${script_dir}/rtl/c2p_bf_engine.v \
${script_dir}/rtl/c2p_bf_engine_array.v \
${script_dir}/rtl/c2p_snapshot_prio_tree.v \
${script_dir}/rtl/c2p_snapshot_bank_copy_arbiter.v \
${script_dir}/rtl/c2p_snapshot_bank_arbiter.v \
${script_dir}/rtl/c2p_snapshot_response_fabric.v \
${script_dir}/rtl/c2p_snapshot_response_joiner.v \
${script_dir}/rtl/c2p_snapshot_banked_frontend.v"
export C2P_PPA_UTILIZATION=${C2P_PPA_UTILIZATION:-8}
export C2P_PPA_RESULT_DIR=${C2P_PPA_RESULT_DIR:-"${script_dir}/results/openroad_c2p_banked_frontend"}

exec "${script_dir}/run_openroad_control_proxy.sh"
