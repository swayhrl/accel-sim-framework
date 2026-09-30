#!/usr/bin/env bash
set -euo pipefail

LOCK=/data/c16/locks/c16_gpu_campaign.lock
BINDING=${1:?gate binding receipt required}
ENTRYPOINT=${2:?candidate entrypoint required}
RAW=${3:?raw directory required}

python3 - "$BINDING" "$ENTRYPOINT" <<'PY'
import json, pathlib, sys
binding = json.load(open(sys.argv[1]))
entry = pathlib.Path(sys.argv[2]).resolve()
if binding.get("status") != "PASS_BOUND_AND_SOURCE_FEASIBLE":
    raise SystemExit("gate/source feasibility not passed")
if binding.get("gpu_discovery_authorized") is not True:
    raise SystemExit("GPU discovery not authorized")
if pathlib.Path(binding["candidate_entrypoint"]).resolve() != entry:
    raise SystemExit("candidate entrypoint mismatch")
if binding.get("target_scope") != "DISCOVERY_TARGET_ONLY":
    raise SystemExit("target scope is not discovery-only")
PY

mkdir -p "$RAW"
exec 9>"$LOCK"
if ! flock -n 9; then
  printf '%s\n' GPU_BUSY_OPPORTUNISTIC_STOP >"$RAW/GPU_BUSY_OPPORTUNISTIC_STOP"
  exit 75
fi
START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
cleanup() {
  code=$?
  END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  printf '{"lock":"%s","start_utc":"%s","end_utc":"%s","exit_code":%d}\n' "$LOCK" "$START" "$END" "$code" >"$RAW/GPU_LOCK_RECEIPT.json"
  flock -u 9 || true
  exit "$code"
}
trap cleanup EXIT INT TERM
export C16_ORACLE_FEATURE=0
export C16_ORACLE_DIAGNOSTICS=0
python3 "$ENTRYPOINT" --binding "$BINDING" --raw "$RAW"
