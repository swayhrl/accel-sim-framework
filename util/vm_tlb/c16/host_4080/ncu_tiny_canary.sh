#!/usr/bin/env bash
# N1 template. Default mode prints immutable argv only; execution needs explicit later approval.
set -euo pipefail
usage() { echo "usage: $0 --print-command --canary <sha-verified-binary> --metrics <frozen-metrics.txt> --output <fresh.ncu-rep>" >&2; }
[[ $# -eq 7 && $1 == "--print-command" && $2 == "--canary" && $4 == "--metrics" && $6 == "--output" ]] || { usage; exit 2; }
bin=$3 metrics=$5 out=$7
[[ -x $bin && -f $metrics && ! -e $out ]] || { echo "invalid binary/metrics or output exists" >&2; exit 2; }
[[ -z ${CUDA_INJECTION64_PATH:-} && -z ${LD_PRELOAD:-} ]] || { echo "NVBit/LD_PRELOAD must be absent for NCU N1" >&2; exit 2; }
printf '%q ' ncu --target-processes application-only --replay-mode kernel --metrics "$(paste -sd, "$metrics")" --export "$out" "$bin"
printf '\n# N1 is not executed by this template. A separately approved host-arrival runner must record this argv, binary SHA, metrics SHA, NCU version, UID, UUID mapping, wall limit, and report SHA.\n'
