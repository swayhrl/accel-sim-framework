#!/bin/sh
set -eu
# Exact finite EP leaves; every existing operation delegates byte-for-byte.
if [ "$#" -ge 3 ]; then
  case "$1:$3" in
    experiment:EP_NATIVE_VECTOR_DRAM935_SENSITIVITY_20261026_V1|experiment:EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1|result:EP_NATIVE_VECTOR_DRAM935_SENSITIVITY_20261026_V1|result:EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1)
      exec /usr/bin/python3 -B /root/data/ep_memory_path_sensitivity_20261026_v1/tools/native_dispatch.py "$@"
      ;;
  esac
fi
exec /bin/sh /root/data/ep_memory_path_sensitivity_20261026_v1/tools/prior_native_entry.sh "$@"
