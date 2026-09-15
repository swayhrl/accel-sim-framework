# CODEX 109 Goal — C16 V5 LDGSTS special-path capture

## Mode

GOAL MODE. Multi-hour unattended GPU task. Do not stop for intermediate approval.

Implementation base / producer authority:

`7b3e99b5bc518353c15aa808d777b0f430d4bb20`

Suggested branch:

`hrl/c16-ldgsts-special-path-109-v5`

Read first:

- `docs/vm_tlb/chatgpt_handoff/c16/formal_campaign_v5/V4_REVIEW_AND_V5_PRIORITY.md`
- `docs/vm_tlb/chatgpt_handoff/c16/formal_campaign_v5/LDGSTS_CAPTURE_QUALIFICATION_V5.md`
- prior V4 review pack `docs/vm_tlb/review_packs/C16_FORMAL_EXPANSION_109_V4/`

## Primary objective

Recover formal address-bearing coverage for the SM89 `LDGSTS` global-to-shared path that V4 proved is missing from the current direct-GLOBAL-MREF tracer.

Do not broaden to new models until this path is either formally captured or closed with a precise root-cause blocker.

## Stage 1 — static special-path normalization

For the four already audited representative functions:

- split `LDGSTS...` rows into `SPECIAL_GLOBAL_ADDRESS_PATH`;
- split `LDGDEPBAR` into `SPECIAL_MEMORY_CONTROL`;
- preserve unresolved opcodes fail-closed;
- regenerate a compact summary with counts per target.

Do not count `LDGDEPBAR` as global-address traffic.

Expected prior anchor:

- Decode Early Heavy has no special address path and remains `ALL_DETECTED_GLOBAL_PATHS_COVERED`.

## Stage 2 — exact operand qualification

Use one executed representative `LDGSTS` from S2 Prefill GEMM first.

Determine the exact NVBit MREF operand index that represents the **global source**, not the shared destination.

Required evidence:

- full operand enumeration for the selected static instruction;
- exact SASS/static-map identity;
- candidate-operand canaries run separately;
- terminal-complete, zero-overflow traces;
- same-process `C16_ADDRESS_CONTEXT_V1` for each canary;
- an explicit `LDGSTS_OPERAND_QUALIFICATION.json` with the accepted global-source operand or fail-closed ambiguity.

Do not promote an operand based on address magnitude alone if the metadata/SASS evidence disagrees.

If `nvbit_add_call_arg_mref_addr64` cannot expose the global-source operand for `GLOBAL_TO_SHARED`, diagnose the API/tool limitation precisely before attempting a different instrumentation route.

## Stage 3 — tool qualification

Once the global-source operand is qualified, implement the minimum change needed to capture one exact static `LDGSTS` row per replay.

Prefer to reuse C16WARP1 record layout and bind `path_kind` + `mref_operand_index` in the hash-closed manifest. Introduce a new binary version only if necessary for unambiguous decoding.

Qualification must include:

- one known nonzero `LDGSTS` canary;
- one zero-execution selected row if available;
- active-mask correctness;
- stable address checksum/count on repeated exact replay;
- terminal closure;
- overflow/drop = 0;
- same-process address-context binding;
- CPU decoder/quickcheck.

## Stage 4 — formal special-path capture

Capture complete frozen `LDGSTS` static sets, in this priority order:

1. Q05 S2 Prefill GEMM;
2. Q05 S2 Prefill Attention;
3. Q05 S2 Decode Early KV/Attention;
4. Q05 S2 Decode Late KV/Attention;
5. Q05 S3 Prefill Attention if the same address-bearing special path is present/executed.

For each target:

- freeze exact code object/function/occurrence/static LDGSTS set;
- execute deterministic per-static-row replay;
- preserve `EXECUTED_SHARD` vs `ZERO_EXECUTION_PROVEN`;
- bind exact global-source operand index;
- bind same-process address context;
- keep width exact only when explicit `.128` proof exists;
- classify global-source access kind as READ;
- build a logical target manifest;
- Pipeline V1 finalize/transfer/remote verify/admit/ACK every accepted formal run.

Do not reopen already accepted direct-MREF raw. New special-path evidence must be additive.

## Stage 5 — target-level coverage closure

For each selected target, combine **metadata only** from the accepted direct set and the new special set to determine set-level coverage.

Allowed final label:

`ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL`

only if:

- complete direct static set is already accepted;
- complete address-bearing LDGSTS static set is accepted;
- no remaining unresolved address-bearing global path exists.

Never merge absolute VAs across replay processes to create a physical whole-kernel footprint.

## Resource policy

- No AWQ network/source retries in this Goal unless source is already locally available at start.
- No raw7B retry on the 16GB RTX4080.
- No Qwen3/DeepSeek binding work.
- No retokenization.
- No CPU model/KV offload.
- No dtype/backend/context/batch changes.

Spend GPU time on special-path qualification and capture only.

## Failure handling

Recoverable instrumentation failures are sub-goals, not STOP conditions.

If direct NVBit MREF-address injection for `LDGSTS` is impossible, bounded fallback work is allowed to test another exact address-bearing instrumentation method, but it must preserve workload identity and produce explicit loss/drop/terminal evidence.

Final blocker classification must distinguish:

- `LDGSTS_CAPTURE_PASS`;
- `LDGSTS_CAPTURE_PARTIAL_WITH_SCOPED_EVIDENCE`;
- `LDGSTS_NVBIT_OPERAND_AMBIGUOUS`;
- `LDGSTS_ADDRESS_INJECTION_UNSUPPORTED`;
- `LDGSTS_GLOBAL_BLOCKER_WITH_ROOT_CAUSE`.

Do not silently fall back to direct-only and call the target complete.

## Required review pack

Create:

`docs/vm_tlb/review_packs/C16_LDGSTS_SPECIAL_PATH_109_V5/`

Required files:

- `README.md`
- `FINAL_DECISION.json`
- `SPECIAL_PATH_STATIC_SUMMARY.tsv`
- `LDGSTS_OPERAND_QUALIFICATION.json`
- `TRACE_METHOD_QUALIFICATION.tsv`
- `SPECIAL_STATIC_SET_INDEX.tsv`
- `PER_SPECIAL_MREF_ARTIFACT_INDEX.tsv`
- `ADDRESS_CONTEXT_INDEX.tsv`
- `SPECIAL_PATH_QUICKCHECK.tsv`
- `TARGET_COVERAGE_CLOSURE.tsv`
- `FORMAL_TRACE_INDEX.tsv`
- `PIPELINE_ACK_INDEX.tsv`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Any accepted formal bundle must be Pipeline-ACKed before final PASS.

## STOP condition

Commit and push the branch with a clean worktree and hash-closed review pack.

STOP only after the final V5 special-path decision is recorded.
