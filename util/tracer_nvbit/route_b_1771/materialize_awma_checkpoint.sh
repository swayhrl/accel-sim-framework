#!/usr/bin/env bash
set -euo pipefail
repo=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2
pack="$repo/docs/vm_tlb/review_packs/AWMA_ROUTE_B_Q05_CANARY_CHECKPOINT_109_V2"
report="$repo/docs/vm_tlb/codex_handoff/awma/AWMA_ROUTE_B_Q05_CANARY_CHECKPOINT_109_V2_REPORT.md"
run=/data/c16/awma/simcompat-v2/q05_routeb_canary_r3_20260917T0110Z
frozen="$run/frozen_consumer25"
uldc="$run/uldc_checkpoint"
post_src="$repo/util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing.cpp"
post_bin="$repo/util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing"
route_src="$repo/util/tracer_nvbit/route_b_1771/route_b_tracer.cu"
route_bin=/data/c16/awma/simcompat-v2/route_b/bin/route_b_live_raw.so
raw=$(find "$run/raw" -maxdepth 1 -type f -name 'kernel-*.trace.xz' | head -n1)
traceg=$(find "$run/raw" -maxdepth 1 -type f -name 'kernel-*.traceg.xz' | head -n1)
if [ -e "$pack" ]; then echo "checkpoint pack already exists: $pack" >&2; exit 1; fi
mkdir -p "$pack/evidence" "$pack/diff" "$(dirname "$report")"
cd "$repo"
{
  echo "branch=$(git branch --show-current)"
  echo "head=$(git rev-parse HEAD)"
  echo "head_tree=$(git rev-parse HEAD^{tree})"
  echo '--- status --short'
  git status --short
} > "$pack/GIT_STATE.txt"
git diff > "$pack/diff/TRACKED_WORKTREE_DIFF.patch"
cat > "$pack/diff/MODIFIED_FILES_12.tsv" <<'EOF'
ordinal	path	classification
1	util/tracer_nvbit/tracer_tool/tracer_tool.cu	tracked Route-A history preserved
2	util/tracer_nvbit/route_b_1771/common.h	Route-B packet schema
3	util/tracer_nvbit/route_b_1771/accelsim_instrument_inst.cu	Route-B device packet producer
4	util/tracer_nvbit/route_b_1771/route_b_raw_formatter.hpp	shared pure raw formatter
5	util/tracer_nvbit/route_b_1771/route_b_formatter_selftest.cc	formatter regression
6	util/tracer_nvbit/route_b_1771/route_b_writer_state.hpp	writer state machine
7	util/tracer_nvbit/route_b_1771/route_b_tracer.cu	official lifecycle scaffold integration
8	util/tracer_nvbit/route_b_1771/tool_func/flush_channel.c	official explicit flush module payload
9	util/tracer_nvbit/route_b_1771/tool_func/flush_channel.cu	flush module source
10	util/tracer_nvbit/route_b_1771/route_b_terminal_receipt_verify.sh	terminal receipt verifier
11	util/tracer_nvbit/route_b_1771/verify_route_b_b2.sh	B2 consistency verifier
12	util/tracer_nvbit/route_b_1771/route_b_negative_regression.sh	B2 fail-closed negative regression
EOF
: > "$pack/diff/FULL_DIFF_12.patch"
while IFS=$'\t' read -r ordinal path classification; do
  [ "$ordinal" = ordinal ] && continue
  if git ls-files --error-unmatch "$path" >/dev/null 2>&1; then
    git diff -- "$path" >> "$pack/diff/FULL_DIFF_12.patch"
  else
    git diff --no-index -- /dev/null "$path" >> "$pack/diff/FULL_DIFF_12.patch" || true
  fi
done < "$pack/diff/MODIFIED_FILES_12.tsv"
cp "$run/stdout.log" "$run/stderr.log" "$run/lifecycle.log" "$run/postprocess.stdout" "$run/postprocess.stderr" "$pack/evidence/"
if [ -f "$run/SHA256SUMS" ]; then cp "$run/SHA256SUMS" "$pack/evidence/"; fi
cp "$run/raw/kernelslist" "$run/raw/kernelslist.g" "$pack/evidence/"
cp "$frozen/parser_source_SHA256SUMS" "$frozen/parser_binary_SHA256SUMS" "$frozen/build_command.txt" "$frozen/build.stdout" "$frozen/build.stderr" "$frozen/run_command.txt" "$frozen/parser.returncode" "$frozen/parser.stdout" "$frozen/parser.stderr" "$frozen/frozen_commit.txt" "$pack/evidence/"
cp "$uldc"/* "$pack/evidence/"
cp /tmp/run_q05_routeb_capture.sh "$pack/evidence/Q05_CANARY_COMMAND_SCRIPT.sh"
cp /tmp/build_route_b_live.sh "$pack/evidence/ROUTE_B_BUILD_SCRIPT.sh"
cp /tmp/run_route_b_live_once.sh "$pack/evidence/B2_LIVE_COMMAND_SCRIPT.sh"
sha256sum "$raw" "$traceg" "$run/raw/kernelslist" "$run/raw/kernelslist.g" > "$pack/evidence/Q05_ARTIFACT_SHA256SUMS"
sha256sum "$post_src" "$post_bin" "$route_src" "$route_bin" "$repo/util/tracer_nvbit/route_b_1771/common.h" "$repo/util/tracer_nvbit/route_b_1771/accelsim_instrument_inst.cu" > "$pack/evidence/PRODUCER_SOURCE_BINARY_SHA256SUMS"
cat > "$pack/ULDC64_EVIDENCE.md" <<EOF
# ULDC.64 checkpoint evidence

- First raw record: $(cat "$uldc/first_ULDC_raw_record.txt")
- Corresponding postprocessed traceg record: $(cat "$uldc/first_ULDC_traceg_record.txt")
- Dynamic occurrence count: $(cat "$uldc/ULDC64_occurrence_count.txt").
- Dynamic PC: 0x0030; opcode: ULDC.64; active mask: 0xffffffff.
- NVBit MREF status: **0 MREF in the static instrumentation path**. The packet's is_mem=false/width 0 is source-backed: the host inserts a memory address only when an operand has type InstrType::OperandType::MREF; otherwise it passes is_mem=0. The device packet producer therefore leaves ma.is_mem=false; the shared formatter emits width 0 and immediate 0.
- Static SASS/instrumentation metadata available at checkpoint: opcode/PC above plus the source-backed MREF decision. A separate NVBit decoded-operand/SASS dump for this PC was not materialized before the review checkpoint; it is explicitly **NOT_CLAIMED**, rather than reconstructed from .64.
- Consumer failure: frozen consumer parser commit 25aa29862239a408099639ae9d5f1a0ea4fee1e1 returns TRACEG_GRAMMAR_REJECT: missing immediate. Its strict parser treats ULDC as a constant-memory access and consumes address fields after the zero-width field, making the final 0 appear to be an address mode and leaving no immediate field.
EOF
cat > "$pack/SCAN_AND_VALIDATOR_STATUS.md" <<'EOF'
# Validator status

- The broad opcode scan was intentionally stopped on explicit review-checkpoint direction before it produced a result. Its status is `STOPPED_PER_REVIEW_DIRECTIVE`; it is not used as evidence.
- The bounded required ULDC occurrence count completed: 7168.
- The current worktree grammar smoke rejected the real Q05 traceg with `missing immediate`.
- The independently built frozen consumer parser at commit `25aa29862239a408099639ae9d5f1a0ea4fee1e1` rejected the same traceg with the same error and return code 2.
- Therefore the current and accepted consumer parser results are consistent. `CURRENT_ULDC_BLOCKER_IS_NOT_ACCEPTED_CONSUMER_PARSER` is false.
EOF
cat > "$pack/CHECKPOINT_STATUS.json" <<EOF
{
  "status": "AWMA_ROUTE_B_Q05_CANARY_CHECKPOINT_REVIEW_REQUIRED",
  "producer_pass": false,
  "final_blocked": false,
  "q05_identity": {
    "model": "Qwen/Qwen2.5-0.5B-Instruct",
    "revision": "7ae557604adf67be50417f59c2c2f167def9a775",
    "scenario": "S2_TEXT",
    "phase": "PREFILL",
    "batch": 1,
    "prefill_tokens": 2048,
    "decode_tokens": 32,
    "dtype": "float16",
    "backend": "sdpa",
    "target_id": "Q05_PREFILL_ATTN_FLASH",
    "function_occurrence": 0
  },
  "q05_canary": {
    "records": 13490624,
    "terminal": "COMPLETE",
    "drop_count": 0,
    "overflow_count": 0,
    "raw_trace_path": "$raw",
    "traceg_path": "$traceg"
  },
  "frozen_consumer_parser": {
    "commit": "25aa29862239a408099639ae9d5f1a0ea4fee1e1",
    "return_code": 2,
    "result": "TRACEG_GRAMMAR_REJECT: missing immediate"
  },
  "uldc64": {"occurrences": 7168, "nvbit_mref": 0, "packet_width": 0}
}
EOF
cat > "$report" <<EOF
# AWMA Route-B Q05 Canary Checkpoint — node109 V2

Status: AWMA_ROUTE_B_Q05_CANARY_CHECKPOINT_REVIEW_REQUIRED.

The exact Q05 S2 Prefill target canary naturally completed its frozen workload and exact Decode32 output. The selected Q05 target closed with terminal COMPLETE, 13,490,624 records, zero drops and zero overflows. Its canonical raw-to-traceg conversion completed, but the accepted frozen consumer parser rejects the resulting traceg at ULDC.64 with missing immediate.

This is a review checkpoint, not producer PASS and not a final BLOCKED decision. No formal Q05 run, consumer contract relaxation, workload/target change, or synthetic ULDC address was performed.

Review pack: docs/vm_tlb/review_packs/AWMA_ROUTE_B_Q05_CANARY_CHECKPOINT_109_V2/.
EOF
find "$pack" -type f -print0 | sort -z | xargs -0 sha256sum > "$pack/SHA256SUMS"
echo CHECKPOINT_MATERIALIZED
