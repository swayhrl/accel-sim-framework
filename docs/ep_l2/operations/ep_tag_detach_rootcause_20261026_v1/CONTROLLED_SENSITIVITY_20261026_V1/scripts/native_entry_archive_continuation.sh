#!/bin/sh
set -eu
if [ "$#" -ge 3 ] && [ "$1:$2:$3" = "result:archive:EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1" ]; then
 exec /usr/bin/python3 -B /root/data/ep_memory_path_sensitivity_20261026_v1/tools/e2_archive_continuation.py "$@"
fi
exec /bin/sh /root/data/ep_memory_path_sensitivity_20261026_v1/tools/prior_postrun_native_entry.sh "$@"
