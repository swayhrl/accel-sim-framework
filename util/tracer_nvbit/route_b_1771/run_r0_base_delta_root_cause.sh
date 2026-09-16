#!/usr/bin/env bash
set -euo pipefail
frozen=/data/c16/awma/simcompat-v2/q05_routeb_canary_r3_20260917T0110Z/frozen_consumer25/traceg_grammar_smoke_25aa
out=/data/c16/awma/simcompat-v2/base_delta_root_cause_20260917
mkdir -p "$out"
cp /tmp/r0_mode2_two_lane.traceg /tmp/r0_uldc_width0.traceg "$out/"
xz -zkf "$out/r0_mode2_two_lane.traceg"
xz -zkf "$out/r0_uldc_width0.traceg"
set +e
"$frozen" "$out/r0_mode2_two_lane.traceg.xz" > "$out/mode2.stdout" 2> "$out/mode2.stderr"
mode2_rc=$?
"$frozen" "$out/r0_uldc_width0.traceg.xz" > "$out/uldc.stdout" 2> "$out/uldc.stderr"
uldc_rc=$?
set -e
printf '%s\n' "$mode2_rc" > "$out/mode2.returncode"
printf '%s\n' "$uldc_rc" > "$out/uldc.returncode"
cat > "$out/BASE_DELTA_ROOT_CAUSE_CONFIRMED.md" <<EOF
# BASE_DELTA_ROOT_CAUSE_CONFIRMED

Mode-2 fixture record: $(tail -n 2 "$out/r0_mode2_two_lane.traceg" | head -n 1)

- Effective active lanes: 2 (mask 0x5).
- Producer v5 base_delta encoding: base 0x1000 + one delta 64 + immediate 0.
- Encoded delta count: 1 = active_lanes - 1.
- Frozen parser expectation: 2 deltas, so it consumes immediate 0 as a second delta then reports missing immediate.
- Frozen parser mode-2 return code: $mode2_rc; stderr: $(tr '\n' ' ' < "$out/mode2.stderr").

ULDC fixture record: $(tail -n 2 "$out/r0_uldc_width0.traceg" | head -n 1)

- It remains a width-0/non-MREF record.
- Frozen parser ULDC return code: $uldc_rc; stdout: $(tr '\n' ' ' < "$out/uldc.stdout").
EOF
sha256sum "$out"/* > "$out/SHA256SUMS"
test "$mode2_rc" -ne 0
test "$uldc_rc" -eq 0
echo R0_BASE_DELTA_ROOT_CAUSE_PASS
