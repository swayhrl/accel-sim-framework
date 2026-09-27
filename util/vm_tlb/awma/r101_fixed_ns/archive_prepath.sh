#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927
DST="$ROOT/raw/PRE_DYNAMIC_PATH_QUALIFICATION_ATTEMPT0"
mkdir -p "$DST"
for name in OPERATOR_TIMING.tsv OPERATOR_TIMING_ANALYSIS.json \
            GRAPH_CONTROL_TIMING.tsv GRAPH_CONTROL_ANALYSIS.json GRAPH_CONTROL_CANARY.json; do
  cp -p "$ROOT/$name" "$DST/$name"
done
cp -p "$ROOT/logs/operator_timing.stdout.log" "$DST/operator_timing.stdout.log"
cp -p "$ROOT/logs/operator_timing.stderr.log" "$DST/operator_timing.stderr.log"
cp -p "$ROOT/logs/graph_control.stdout.log" "$DST/graph_control.stdout.log"
cp -p "$ROOT/logs/graph_control.stderr.log" "$DST/graph_control.stderr.log"
echo PRE_PATH_ATTEMPT0_ARCHIVED
