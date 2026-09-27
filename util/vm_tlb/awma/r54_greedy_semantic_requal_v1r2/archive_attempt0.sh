#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927
ATTEMPT="$ROOT/raw/production_attempt0_input_constructed_after_start"
mkdir -p "$ATTEMPT"
for name in \
  SNAPSHOT_PRODUCTION_TIMING.tsv SNAPSHOT_COPY_ACCOUNTING.tsv \
  PRODUCTION_CANARY_RECEIPT.json PRODUCTION_ANALYSIS.json \
  production_formal.stdout.log production_formal.stderr.log
do
  cp -p "$ROOT/$name" "$ATTEMPT/$name"
done
if [[ -d "$ROOT/raw/production_profile" && ! -e "$ROOT/raw/production_profile_attempt0" ]]; then
  mv "$ROOT/raw/production_profile" "$ROOT/raw/production_profile_attempt0"
fi
printf 'Archived attempt0 at %s\n' "$ATTEMPT"
