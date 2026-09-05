#!/usr/bin/env bash
# M5.0BT compatibility entry point; controller is workload-resumable.
set -euo pipefail
exec "$(cd "$(dirname "$0")" && pwd)/m5_trace_capture_controller.py" "$@"
