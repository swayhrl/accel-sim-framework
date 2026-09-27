#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/r81_legal_vocab_20260927
SRC="$ROOT/raw/full_generation/C0_SHARED_DISCOVERY"
DST="$ROOT/raw/full_generation/C0_ATTEMPT0_HIGH_VARIANCE"
mkdir -p "$DST"
for name in CANARY_RESULTS.json TIMING_RESULTS.tsv FORMAL_RUNS.json TIMING_SUMMARY.json; do
  cp -p "$SRC/$name" "$DST/$name"
done
cp -p "$ROOT/logs/full_generation_C0_SHARED_DISCOVERY.stdout.log" "$DST/full_generation.stdout.log"
cp -p "$ROOT/logs/full_generation_C0_SHARED_DISCOVERY.stderr.log" "$DST/full_generation.stderr.log"
echo C0_ATTEMPT0_ARCHIVED
