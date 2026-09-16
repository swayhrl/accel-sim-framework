#!/usr/bin/env bash
set -euo pipefail
run=/data/c16/awma/simcompat-v2/route_b/r2_tiny_frozen_live_20260917T
run="${run}$(date -u +%H%M%S)Z"
frozen=/data/c16/awma/simcompat-v2/q05_routeb_canary_r3_20260917T0110Z/frozen_consumer25/traceg_grammar_smoke_25aa
bash /tmp/run_route_b_live_once.sh "$run"
trace=$(find "$run/raw" -maxdepth 1 -type f -name 'kernel-*.trace.xz' | head -n1)
traceg=$(find "$run/raw" -maxdepth 1 -type f -name 'kernel-*.traceg.xz' | head -n1)
"$frozen" "$traceg" > "$run/frozen_parser.stdout" 2> "$run/frozen_parser.stderr"
term=$(grep '^ROUTEB_TERMINAL_COMPLETE ' "$run/lifecycle.log")
recv=$(printf '%s\n' "$term" | sed -n 's/.*receiver_accepted=\([0-9][0-9]*\).*/\1/p')
raw_count=$(xz -dc "$trace" | awk 'BEGIN{s=0;n=0} /^#traces format/{s=1;next} s&&NF{n++} END{print n}')
frozen_count=$(sed -n 's/.*"instructions":\([0-9][0-9]*\).*/\1/p' "$run/frozen_parser.stdout")
test "$recv" = "$raw_count"
test "$raw_count" = "$frozen_count"
if xz -dc "$trace" | grep -F ' 2 0x' >/dev/null; then
  echo R2_MODE2_UNEXPECTED >&2
  exit 1
fi
xz -dc "$trace" | grep -E ' (LDG|STG|LDS|STS)' >/dev/null
grep -q 'drop_count=0' "$run/lifecycle.log"
grep -q 'overflow_count=0' "$run/lifecycle.log"
grep -q ROUTEB_TERMINAL_COMPLETE "$run/lifecycle.log"
printf 'receiver_accepted=%s\nraw_dynamic_records=%s\nfrozen_parser_instructions=%s\nmode2_records=0\n' "$recv" "$raw_count" "$frozen_count" > "$run/R2_RECEIPT.txt"
sha256sum "$run"/frozen_parser.stdout "$run"/frozen_parser.stderr "$run/R2_RECEIPT.txt" >> "$run/SHA256SUMS"
echo R2_TINY_FROZEN_LIVE_PASS run="$run"
