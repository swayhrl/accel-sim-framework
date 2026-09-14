# C16 RTX4080 CODEX_NEXT_STAGE

## Status

AUTHORIZED.

Execute this specification from the coordination branch containing this file. Create a fresh execution branch/worktree; do not execute directly on the ChatGPT-owned coordination branch.

## Objective

Close the transferred exact Llama asset, repair the custom NVBit 1.7.5 no-match/READY gate, then complete the RTX4080 Llama native, kernel-census, NCU, and NVBit model-canary chain through U9.

## Source anchors

- Coordination base: `hrl/c16-4080-chatgpt-handoff-u4-u9-v0`.
- Scientific execution parent before this handoff: `8b1fae1b1d4eb3d95928f51020a94fa04e9635c1`.
- Known U0-U3 closure parent: `c463c017372361d8422038f1d26d5ba2cbafde41`.
- NCU N0/N1 closure parent: `ba9afb264746b3290607ae5e5e5d8642941bc11f`.

Before execution, read:

- `CURRENT_STATE.md`
- `DISCUSSION_REFERENCE.md`
- the existing `docs/vm_tlb/codex_handoff/c16/4080_migration/` receipts
- `C16_4080_MIGRATION_SOURCE_RECEIPT.md/json`

Do not modify ChatGPT-owned handoff files.

## Allowed scope

Userspace work as `huangrulin` under the repository and `/data/c16`, including:

- model import validation and promotion;
- Python/CUDA/NCU/NVBit scripts and builds;
- bounded GPU experiments;
- userspace downloads/builds where needed;
- receipts, manifests, hashes, review packs, commit/push.

## Explicitly forbidden scope

Do not:

- use sudo or attempt privilege escalation;
- mutate driver, host CUDA, kernel, modprobe, systemd, Docker daemon, network/proxy/DNS, mounts, partitions, LVM, or fstab;
- use CPU offload;
- substitute model, revision, dtype, context, batch, attention backend, or target identity;
- reuse RTX3090 launch IDs, static ranges, or `DYNAMIC_KERNEL_RANGE` as RTX4080 evidence;
- co-load NCU and NVBit in one formal model run;
- commit weights, `.ncu-rep`, raw NVBit traces, wheel payloads, or large build artifacts.

If a genuinely unavoidable root/host mutation is proven, exhaust userspace diagnosis first, generate the minimal administrator command plus impact/rollback, and STOP.

## Stage A — U4 exact local asset closure

Required model:

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

Transferred incoming payload location:

`/data/c16/models/.incoming/Llama-3.2-1B/4e20de362430cd3b72f300e6b0f18e50e7166e08`

Source host path used by the operator:

`/root/share/c16_recovery_v3/models/llama_3p2_1b/4e20de362430cd3b72f300e6b0f18e50e7166e08`

The source-side operator reported an `R1_LLAMA3P2_1B_ASSET_RECEIPT.json` with exact model/revision and payload hash closure. The six transferred payload files were manually checked source-vs-destination by SHA256.

### A1. Fix importer semantics before promotion

The current importer may not treat the directory name itself as provenance and may not invent `C16_ASSET_PROVENANCE.json` from the path.

Support an explicit authoritative provenance input, such as `--source-receipt` or `--provenance`, with this evidence priority:

1. an existing committed/project receipt that contains the exact model/revision and exact payload hash/size manifest;
2. an externally supplied source `R1_LLAMA3P2_1B_ASSET_RECEIPT.json` or equivalent hash-closed transfer provenance;
3. otherwise fail closed with a precise request for the small provenance/receipt file from the CPU server.

Do not block unrelated U8.5 repair while waiting for an external source receipt.

### A2. Validate exact bytes

For the actual incoming revision directory:

- inventory all regular payload files;
- reject unexpected symlinks unless separately reviewed;
- compute total regular-file payload bytes;
- compute every payload SHA256;
- validate config/tokenizer/weight readability and completeness;
- compare exact payload size/hash identities against the authoritative provenance source;
- verify model ID and revision from authority, not from path text.

### A3. Promotion

Only after exact closure PASS, promote atomically to a stable final path under `/data/c16/models/` that includes the exact revision identity. Never overwrite an existing asset.

Required status:

`U4_LOCAL_ASSET_EXACT_CLOSURE_PASS`

If the only blocker is the missing small source receipt/provenance file, record it precisely, continue Stage B, and request that one file rather than Hugging Face authentication or a model redownload.

## Stage B — repair U8.5 custom NVBit tool closure

Current evidence already proves official and PyTorch NVBit paths on RTX4080/SM89/driver 580.178.04. Treat U8.5 as a userspace custom-tool defect, not a driver blocker.

Investigate the exact custom no-match/no-trace tool build and injection path:

- source hash and exported callback symbols;
- link/build argv and SM89 closure;
- injection environment and exact `.so` path;
- whether the tool is actually loaded into the target process;
- stdout/stderr buffering and callback lifecycle;
- EAGER module-loading behavior;
- bounded process cleanup.

Required gate:

1. custom C16 tool visibly loads;
2. required READY marker is emitted before any formal arm;
3. bounded no-match prewarm exits normally;
4. zero trace files are produced;
5. TERMINAL or equivalent clean tool-lifecycle evidence is present;
6. no residual child/NVBit/GPU compute process remains;
7. all source/binary/argv/environment evidence is hash-closed.

Do not satisfy the gate by replacing the custom tool with official `instr_count_bb`; official evidence remains a separate diagnostic.

Required status before U9:

`U8_5_C16_CUSTOM_TOOL_CLOSURE_PASS`

If repair proves impossible in userspace, preserve exact evidence. Do not request driver downgrade unless there is new direct evidence that the host driver is the unavoidable cause.

## Stage C — U5 native Llama baseline

Begin only after U4 PASS.

Freeze and validate the Recovery-V2-S5 semantic contract:

- S0 / B1 / T128 / Decode4 / TEXT;
- exact model revision;
- exact frozen input/token receipt;
- dtype;
- attention backend;
- CUDA-only model/tensor residency;
- no offload/substitution;
- output checksum;
- native timing only as a reference.

No NCU or NVBit injection in U5.

Produce an exact RTX4080 native receipt and hash closure.

## Stage D — U6 RTX4080-local kernel census

Begin only after U5 PASS.

Build a new local census from the actual RTX4080 runtime/code objects. Record exact kernel identities and launch/correlation evidence needed for target selection.

Do not reuse RTX3090 kernel ordinals, launch IDs, static instruction indices, or static ranges.

Freeze the U6 target authority before U7/U9 target-specific work.

## Stage E — U7 bounded Llama NCU capture

Begin only after U6 target authority is frozen.

Use the qualified NCU 2025.1.1 path. Select a compact, research-useful memory-characterization metric set from metrics actually supported on this RTX4080; do not use `--set full`.

Before capture freeze:

- exact metric manifest/hash;
- exact target/window identity from U6;
- exact argv;
- exact model/input/runtime identity;
- bounded timeout/cleanup policy.

Run NCU alone, never with NVBit. Store raw `.ncu-rep` under `/data/c16/ncu`, reopen/export with the same NCU, and hash-close raw report/export/command/target identity. Raw reports stay out of Git.

## Stage F — U9 Llama NVBit address-bearing canary

Begin only when ALL are true:

- U4 PASS;
- U5 PASS;
- U6 target authority frozen;
- `U8_5_C16_CUSTOM_TOOL_CLOSURE_PASS`.

Rebuild/map the actual RTX4080 live function and SASS/static instruction target. Never copy RTX3090 static indices/ranges.

Required sequence:

1. exact live-function/code-object mapping;
2. SASS/static memory-instruction map;
3. no-match prewarm with READY proof;
4. immutable arm/target binding;
5. one bounded target capture;
6. clean process-group cleanup.

PASS requires:

- exact target launch observed;
- address-bearing records > 0;
- complete schema and final newline;
- expected function/static binding;
- checksum-stable model output;
- clean process exit;
- raw trace size/SHA closure;
- raw trace remains outside Git.

Do not broaden targets or reselect after freeze merely to obtain nonzero data.

## Required Codex handoff output

From this stage onward, use the structured coordination workflow.

Update/create:

`docs/vm_tlb/codex_handoff/c16/4080_migration/LATEST_REPORT.md`

Create/update a browsable review pack:

`docs/vm_tlb/review_packs/C16_4080_U4_U9_R1/`

The review pack should contain at minimum:

- `README.md` as the single review entry point;
- `MANIFEST.json`;
- `SOURCE_ANCHORS.md`;
- `COMMIT_HISTORY.md`;
- `CHANGED_FILES.md`;
- `VALIDATION_SUMMARY.md`;
- `OPEN_ISSUES.md`;
- `SHA256SUMS`;
- compact evidence extracts/indexes, not large raw payloads.

`LATEST_REPORT.md` must state:

- Stage and PASS/CONDITIONAL PASS/FAIL;
- final branch/commit;
- U4/U5/U6/U7/U8.5/U9 status;
- remaining blockers;
- review-pack entry path;
- most important evidence files;
- `READY_FOR_NEXT_STAGE` or `NOT_READY`.

## Git requirements

- Create a fresh execution branch/worktree from the coordination branch containing this specification.
- Do not rewrite ChatGPT-owned files.
- Use explicit-path `git add`; avoid `git add .` / `git add -A`.
- Keep raw artifacts out of Git.
- Run focused tests, `git diff --check`, and verify clean status before push.

## STOP conditions

STOP when any of these occurs:

1. U4 requires an external small provenance/source-receipt file that is not locally available AND U8.5 repair work is exhausted for this round;
2. a genuine root/host mutation becomes unavoidable;
3. scientific identity cannot be closed without substitution;
4. U8.5 yields a precise unresolved custom-tool blocker after bounded userspace diagnosis;
5. U9 is completed.

Do not proceed to multi-model expansion in this stage.
