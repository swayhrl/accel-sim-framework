#!/bin/sh
set -eu
if [ "$#" -ge 3 ]; then
 case "$1:$2:$3" in
  experiment:accept:EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1|result:archive:EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1)
   exec /usr/bin/python3 -B /root/data/ep_memory_path_sensitivity_20261026_v1/tools/e2_postrun_entry_adapter.py "$@"
   ;;
 esac
fi
exec /bin/sh /root/data/ep_memory_path_sensitivity_20261026_v1/tools/peer_extended_native_entry.sh "$@"
