# C16 RTX4080 CODEX_NEXT_STAGE

## Status

AUTHORIZED **only after the ongoing bulk model transfer to `/data/c16` has completed or been explicitly stopped**.

Create a fresh execution branch/worktree from this coordination branch. Do not modify ChatGPT-owned handoff files.

Recommended execution branch:

`hrl/c16-4080-u5-u9-r5-clean`

## Objective

R4 at:

`hrl/c16-4080-u5-u9-r4@d6702b62717a7f6621dd4e3ca73747075113f0b0`

is accepted as an end-to-end **mechanism qualification**, but not as authoritative scientific measurement because large model assets were concurrently being copied into `/data/c16`.

Perform one clean isolated rerun of the frozen Llama path:

1. isolation/preflight gate;
2. deterministic frozen-input re-admission check;
3. corrected U5 native reference measurement;
4. fresh R5-local U6 census;
5. provenance-complete U7 NCU capture;
6. provenance-complete U9 NVBit canary using the already-selected semantic/static target;
7. STOP.

Do not enter multi-model characterization in this stage.

## Reviewed immutable prerequisites

### Model

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

Formal path:

`/data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

U4 receipt SHA256:

`5b1aed870cd03d50a0da5f6721ab639d56ca0f3a1c3782a9fed9cf8e3dc84a3b`

### Frozen input

`S0 / B1 / T128 / Decode4 / TEXT`

Package:

`/data/c16/inputs/.incoming/llama_3p2_1b/S0_B1_T128_Decode4_TEXT/`

Transfer receipt SHA256:

`5eff72842b2e87c79d2070b9085215e5bfca0e98c25e91155aec04aa12d6fe0d`

Historical identities:

- raw TEXT: `bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208`
- token authority receipt: `0b5a86fdee44452e74e5d80e8043ebd97054fbbe29a6232a4f5cf5d06568c7dd`
- canonical compact-JSON SHA256 of 128 authoritative IDs: `f9cf1ea6dca7956c740b3aa0af59acadd17be014df2aaffb75d240383502e3a7`
- derived token-ID payload: `fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624`

No tokenizer may be invoked to reconstruct the frozen IDs.

### Platform/runtime

- GPU UUID: `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`
- driver: `580.178.04`
- NCU: `/opt/nvidia/nsight-compute/2025.1.1/ncu`, version `2025.1.1.0`
- Python: CPython 3.10.12
- torch: `2.5.1+cu124`
- `libtorch_cuda.so` SHA256: `761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`
- U8.5 custom NVBit lifecycle closure remains reviewed PASS.

## Stage 0 — mandatory isolation gate

Do not start U5 until the bulk asset copy is finished/stopped.

Create a hash-closed preflight receipt containing at minimum:

- UTC timestamp;
- GPU UUID, driver, kernel, NCU version, Python/torch identity;
- `nvidia-smi` compute-process inventory showing no unrelated compute process;
- process inventory for bulk writers/downloaders (`rsync`, `scp`, `sftp`, `rclone`, `curl`, `wget`, `aria2`, known C16 model-sync processes);
- inventory of `/data/c16/models/.transfer` and any `.partial` asset path;
- evidence that no transfer file is changing during a short two-snapshot observation window;
- no residual NCU/NVBit/model process from a prior run.

If an active bulk writer into `/data/c16` is found, STOP without measuring.

Do not use root, drop caches, tune clocks/power, or mutate host configuration.

## Stage 1 — harden the U5 runner before formal measurement

The R4 runner is not accepted unchanged.

Required fixes:

1. Replace all scientific `assert` gates with explicit fail-closed checks that cannot disappear under `python -O`.
2. Bind the exact formal model path to the reviewed U4 importer receipt. The result receipt must record the U4 receipt path/SHA and verify its model/revision/promoted-path identity before model execution.
3. Keep generated-token collection on GPU during the timed region. Do not call `.cpu()`/`.tolist()` for each decode step inside timing. Synchronize the endpoint first, then copy generated IDs to host and hash them outside the timed region.
4. Record exact dtype/backend/residency/environment and output checksum in every measured sample.
5. Preserve semantic inference behavior: B1, 128 frozen input IDs, exactly 4 greedy decode tokens, float16, SDPA, CUDA-only, no offload/substitution.

Do not change model, input, dtype, backend, decode policy or semantic workload to improve timing.

## Stage 2 — clean U5 native reference

Re-run the frozen-input admission first; it is deterministic and cheap.

For timing:

- load the model before the timed section;
- perform one untimed warmup execution of the exact same semantic contract;
- require the warmup checksum to equal the frozen historical checksum;
- perform 5 measured repetitions in the same process/runtime state;
- synchronize CUDA immediately before and after each timed inference;
- copy generated IDs to CPU only after the end synchronization;
- require every repetition to produce the same frozen checksum;
- report all five durations plus median/min/max (and CV if convenient), not just one selected run.

Native timing remains a platform reference, not cross-platform-equivalent performance evidence.

## Stage 3 — fresh R5-local U6 census and frozen canary target

Regenerate the RTX4080-local live function/code-object/address mapping. Never reuse R4 absolute addresses, ordinals or launch IDs.

The canary target itself is already selected and must not be changed post hoc:

- semantic function: `indexSelectLargeIndex` (record exact mangled name from R5 live code object);
- expected static instruction index: `101`;
- expected opcode: `LDG.E.U16`.

Build the fresh SASS/static map and verify that static index 101 still matches the expected instruction under the frozen runtime/code object.

If it does not match, STOP fail-closed. Do not pick a different instruction to obtain nonzero data.

Freeze and hash a R5 target-contract receipt before U7/U9 formal captures.

## Stage 4 — provenance-complete U7 NCU capture

Run NCU alone; NVBit must not be loaded.

Before formal profiling, recover the exact R4 metric list/argv from local R4 evidence if possible. If R4 did not preserve a reconstructable metric manifest, create a compact memory-oriented metric manifest from metrics supported on this RTX4080 **before** the formal profile, record why R4 provenance was insufficient, and freeze/hash the new manifest. Never use `--set full`.

The U7 receipt/review pack must bind:

- exact NCU executable path/version/SHA256;
- exact metric manifest and SHA256;
- exact argv in execution order;
- exact R5 target contract and SHA256;
- model U4 receipt SHA;
- frozen-input admission receipt SHA;
- runtime identity;
- timeout/cleanup policy;
- raw `.ncu-rep` absolute path, size, SHA256;
- reopened/export output absolute path, size, SHA256;
- NCU pass/replay count if reported;
- clean process termination.

Profile the frozen `indexSelectLargeIndex` target only. Do not select a different kernel based on R5 metric values.

Keep `.ncu-rep` and large exports out of Git; commit only receipts/manifests/hashes and concise summaries.

## Stage 5 — provenance-complete U9 NVBit canary

NCU must be fully terminated before U9.

Use the R5 target contract frozen in Stage 3. Regenerate process-local absolute mappings as required; do not expect absolute addresses to equal R4.

Required sequence:

1. live function/code-object mapping;
2. verify static index 101 / `LDG.E.U16` against the frozen contract;
3. no-match prewarm with READY proof;
4. immutable arm/target binding;
5. one bounded target capture;
6. clean process-group cleanup.

PASS requires:

- exact frozen target launch observed;
- address-bearing rows > 0;
- complete schema/final newline;
- expected function/static-instruction binding;
- frozen model output checksum stable;
- clean exit/TERMINAL;
- raw trace/stdout size and SHA256 closure.

Do not require R5 absolute addresses or trace counts to match R4. Do not broaden/reselect the target after freeze.

## Stage 6 — R4 vs R5 comparison

R4 quantitative values are contaminated and remain non-authoritative.

After R5 closes, compare only as a diagnostic:

- output checksum equality;
- target semantic/static identity equality;
- U5 timing R4 vs clean R5 (label R4 contaminated);
- U7 metric values R4 vs R5 when comparable;
- U9 structural counts/trace size R4 vs R5 when comparable.

Do not average R4 and R5 together and do not promote R4 measurements into the final dataset.

## Multi-model state — informational only

109 already contains 21 exact historical Qwen frozen bindings transferred from the CPU source lane:

- Qwen2.5-0.5B-Instruct: 7;
- Qwen2.5-7B-Instruct raw: 7;
- Qwen2.5-7B-Instruct-AWQ: 7.

Qwen3-8B and DeepSeek-V2-Lite have no historical frozen binding and remain `NO_HISTORICAL_FROZEN_BINDING`.

Do not use these in this R5 Llama rerun and do not start multi-model characterization.

## Required handoff output

Update:

`docs/vm_tlb/codex_handoff/c16/4080_migration/LATEST_REPORT.md`

Create:

`docs/vm_tlb/review_packs/C16_4080_U5_U9_R5_CLEAN/`

At minimum include:

- `README.md`
- `MANIFEST.json`
- `SOURCE_ANCHORS.md`
- `COMMIT_HISTORY.md`
- `CHANGED_FILES.md`
- `VALIDATION_SUMMARY.md`
- `OPEN_ISSUES.md`
- `SHA256SUMS`
- isolation/preflight receipt or its concise hash-closed summary
- U5 repetition summary with exact receipt paths/hashes
- U6/R5 target contract summary/hash
- U7 metric/argv/raw/export manifest with hashes
- U9 target/trace manifest with hashes

`LATEST_REPORT.md` must explicitly say that R4 is mechanism-only/non-authoritative due to concurrent bulk model transfer, and state whether R5 is `READY_FOR_MULTIMODEL_REVIEW` or `NOT_READY`.

## Git requirements

- fresh branch/worktree from this coordination branch;
- do not modify ChatGPT-owned handoff files;
- explicit-path staging only; no `git add .` / `git add -A`;
- raw NCU/NVBit/model/input payloads stay out of Git;
- run focused tests, `git diff --check`, clean-status and remote-head verification before STOP.

## STOP conditions

STOP if:

1. any bulk writer into `/data/c16` remains active at formal measurement time;
2. scientific model/input/runtime identity fails closure;
3. R5 static index 101 no longer maps to expected `LDG.E.U16` under the frozen code object;
4. NCU metric/argv provenance cannot be frozen before capture;
5. a genuine root/host mutation becomes unavoidable;
6. U9 completes.

No root/host mutation is expected.