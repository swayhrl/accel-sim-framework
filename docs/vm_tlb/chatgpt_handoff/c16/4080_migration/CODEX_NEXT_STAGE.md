# C16 RTX4080 CODEX_NEXT_STAGE

## Status

AUTHORIZED: provenance-only R5 evidence closeout.

Do **not** rerun U5/U6/U7/U9 unless an existing R5 artifact/receipt is missing or fails its recorded hash. Do not enter multi-model characterization yet.

Create a fresh execution branch/worktree from this coordination branch. Do not modify ChatGPT-owned handoff files.

Recommended branch:

`hrl/c16-4080-r5-evidence-closeout-r6`

## Reviewed execution

R5:

`hrl/c16-4080-u5-u9-r5-clean@b75f26674a09705659e770ab2134351414aa3c93`

R5 is accepted as the first clean isolated Llama measurement run for this platform. The measurement procedure is scientifically usable for the frozen Llama qualification scope.

R4 remains mechanism-only/non-authoritative for quantitative measurements.

## Objective

Close the reviewability/provenance gap in the committed R5 review pack using only already-existing R5 artifacts and receipts under `/data/c16`.

The current R5 review pack is too terse and does not expose the detailed identities/hashes required by the prior handoff contract.

This task is documentation/evidence closure, not a new measurement run.

## Required checks

Before writing summaries, verify every referenced local R5 artifact still exists and recompute its SHA256. Compare against any R5-local recorded receipt/hash where available. If a required artifact is missing or a recorded hash mismatches, STOP fail-closed and report the exact gap. Do not regenerate or replace scientific artifacts silently.

## Required review-pack expansion

Update/create detailed files under:

`docs/vm_tlb/review_packs/C16_4080_U5_U9_R5_CLEAN/`

At minimum add review-readable summaries for:

### 1. Isolation/preflight

Record:

- timestamp;
- GPU UUID/driver/kernel/runtime identity;
- compute-process state;
- bulk-writer process state;
- `.transfer`/`.partial` two-snapshot result;
- residual NCU/NVBit/model-process state;
- local receipt path and SHA256.

### 2. U5 clean repeated native measurement

Record from the existing R5 U5 output receipt:

- exact receipt absolute path and SHA256;
- U4 receipt path and expected/recomputed SHA256;
- frozen token-ID payload path and SHA256;
- semantic contract `S0/B1/T128/Decode4/TEXT`;
- dtype/backend/CUDA-only binding;
- warmup duration;
- all five measured durations;
- median/min/max and CV if derivable without altering source data;
- checksum for warmup and all five repetitions, or the authoritative receipt evidence proving all matched;
- runner source/blob identity or SHA256.

Do not recompute timing by rerunning the model.

### 3. U6 R5-local census / target contract

Record:

- R5 census receipt/path/SHA256;
- exact live mangled function identity;
- R5-local code-object/address/launch mapping identity;
- static instruction map evidence;
- target contract path/SHA256;
- frozen target: `indexSelectLargeIndex`, static index `101`, opcode `LDG.E.U16`;
- explicit statement that R4 absolute addresses/launch IDs were not reused.

### 4. U7 NCU

Record:

- NCU executable absolute path/version/SHA256;
- metric manifest content or concise metric list and manifest SHA256;
- exact argv in execution order;
- target-contract SHA256;
- model/input/runtime authority hashes;
- timeout/cleanup policy;
- raw `.ncu-rep` absolute path, byte size, recomputed SHA256;
- CSV/export absolute path, byte size, recomputed SHA256;
- pass/replay count if recorded;
- clean termination state;
- concise metric-result summary sufficient for later scientific review.

Do not commit the raw `.ncu-rep` or large export.

### 5. U9 NVBit

Record:

- exact NVBit 1.7.5/custom tool identity and relevant build/tool SHA;
- U8.5 lifecycle authority anchor;
- R5 target-contract SHA256;
- no-match prewarm READY evidence path/SHA;
- immutable arm/target binding path/SHA;
- actual target launch observation;
- address-bearing record count;
- raw stdout/trace absolute paths, sizes and recomputed SHA256 values;
- final newline/schema/TERMINAL state;
- frozen model output checksum;
- clean process termination.

Do not commit raw trace payloads.

## Review-pack quality

Replace boilerplate-only files with meaningful content:

- `README.md`: R5 scope and conclusions;
- `SOURCE_ANCHORS.md`: exact commit/model/input/runtime/U8.5 authorities;
- `COMMIT_HISTORY.md`: coordination -> R4 -> R5 -> closeout lineage;
- `CHANGED_FILES.md`: actual code/evidence changes;
- `VALIDATION_SUMMARY.md`: concrete U5/U6/U7/U9 closure facts and important numerical summaries;
- `OPEN_ISSUES.md`: real remaining issues, if any;
- `MANIFEST.json`: machine-readable key artifact/hash/status anchors;
- `SHA256SUMS`: regenerate over the final review-pack files.

You may add dedicated files such as:

- `ISOLATION_PREFLIGHT_SUMMARY.md`
- `U5_NATIVE_REPETITIONS.md`
- `U6_TARGET_CONTRACT.md`
- `U7_NCU_MANIFEST.md`
- `U9_NVBIT_MANIFEST.md`

## LATEST_REPORT

Update `docs/vm_tlb/codex_handoff/c16/4080_migration/LATEST_REPORT.md` to include concise exact paths/hashes for the R5 isolation, U5, U6, U7 and U9 evidence.

Final status may remain `READY_FOR_MULTIMODEL_REVIEW` only if all required existing artifacts/hash relationships close.

## Forbidden scope

Do not:

- rerun formal GPU measurements merely to improve documentation;
- mutate model/input assets;
- use root/sudo or host mutation;
- start multi-model characterization;
- transfer new large model assets into `/data/c16` during this closeout;
- invent missing provenance.

## STOP

Commit/push the provenance-only closeout and STOP. If any required R5 artifact is missing or hash-inconsistent, set `NOT_READY` and report exactly what cannot be closed.
