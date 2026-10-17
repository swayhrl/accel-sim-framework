#!/usr/bin/env bash
set -euo pipefail
# Persistent ABC RPC requires each completion marker to reach the parent.
exec stdbuf -oL -eL yosys-abc "$@"
