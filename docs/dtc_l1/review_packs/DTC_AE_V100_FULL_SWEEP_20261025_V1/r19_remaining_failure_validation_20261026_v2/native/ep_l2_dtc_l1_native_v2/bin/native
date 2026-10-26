#!/bin/sh
set -eu
# Exact DTC continuation prefixes; EP and other routes below are preserved.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-AEV100-*|experiment:E2-AEREPAIR-LAVAMEM2-*|experiment:E2-AEREPAIR-LATE4-*|experiment:E2-AEREPAIR-REMAIN4-*|result:E2-AEREPAIR-REMAIN4-*)
   exec /usr/bin/python3 -B /root/data/dtc_failure_repair_20261025_v1/ops/revision18/frontend_v1.py "$@"
   ;;
 esac
fi
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1|result:EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1)
   exec /usr/bin/python3 -B /root/data/ep_memory_path_sensitivity_20261026_v1/tools/e2_fresh_input_dispatch.py "$@"
   ;;
 esac
fi
exec /bin/sh /root/data/ep_memory_path_sensitivity_20261026_v1/tools/prior_to_e2_entry.sh "$@"
