#!/bin/sh
set -eu
# COPY_ONLY asset queries only; scientific argv delegate remains unchanged.
if [ "$#" -ge 2 ]; then
  case "$1:$2" in
    asset:ensure|project:assets)
      exec /usr/bin/python3 -B /root/data/ep_dtc_trace_migration_20261024_v1/tools/trace_assets.py "$@"
      ;;
  esac
fi
exec /usr/bin/python3 -B /root/data/dtc_main_short3_20261024_v1/tools/short3_frontend_floor5_v3.py "$@"
