# C16 RTX4080 Current State

## Scope and ownership

This is the ChatGPT-owned coordination state for the C16 RTX4080 platform lane.

## Latest reviewed execution

- R5 branch: `hrl/c16-4080-u5-u9-r5-clean`
- R5 commit: `b75f26674a09705659e770ab2134351414aa3c93`
- R5 status reported by Codex: `READY_FOR_MULTIMODEL_REVIEW`
- R4 remains `MECHANISM_QUALIFICATION_PASS / SCIENTIFIC_MEASUREMENT_NOT_ACCEPTED` because bulk model transfer was active during R4.

## Scientific review of R5

R5 is accepted as the first clean, isolated Llama measurement run for this RTX4080 platform. The measurement procedure itself is materially improved and scientifically usable:

- formal measurement started only after bulk model migration finished and an isolation preflight showed no unrelated GPU compute process and no active/changing bulk transfer state;
- U5 scientific `assert` gates were replaced by explicit fail-closed checks;
- U5 binds the formal promoted model through the U4 receipt path and records the U4 receipt hash;
- per-token GPU-to-CPU copies were removed from the timed region;
- U5 uses one untimed warmup plus five same-process measured repetitions, with CUDA synchronization before/after each timed inference and checksum equality required for every repetition;
- U6 regenerated a fresh R5-local live function/address map instead of reusing R4 absolute identities;
- the previously selected canary target remained fixed as `indexSelectLargeIndex`, static index `101`, opcode `LDG.E.U16`;
- U7 ran NCU alone and reports raw report plus CSV export hash closure;
- U9 ran after NCU and reports exact target launch, nonzero address-bearing output and raw stdout closure.

Therefore R5 quantitative results may be treated as authoritative for the frozen Llama S0/B1/T128/Decode4/TEXT qualification scope, subject to the evidence-pack closeout below.

Important scope limit: U7/U9 are a canary/qualification measurement of the fixed `indexSelectLargeIndex` target. They are not, by themselves, a representative characterization of overall Llama memory behavior.

## Remaining evidence-pack deficiency

The R5 committed review pack is too sparse relative to the requested handoff contract. `README.md`, `SOURCE_ANCHORS.md`, `COMMIT_HISTORY.md`, `CHANGED_FILES.md` and `VALIDATION_SUMMARY.md` are essentially boilerplate, and the detailed U5/U6/U7/U9 artifact identities and hashes are not committed in review-readable form.

This is an evidence packaging/reviewability problem, not a reason to rerun the measurement if the existing local receipts/artifacts remain intact.

Before formal multi-model characterization, perform a provenance-only R5 evidence closeout from the already-existing `/data/c16` artifacts. Do not rerun U5/U6/U7/U9 unless an expected artifact/receipt is missing or fails its recorded hash.

## Immutable scientific identities

### Model

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

Formal path:

`/data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

U4 receipt SHA256:

`5b1aed870cd03d50a0da5f6721ab639d56ca0f3a1c3782a9fed9cf8e3dc84a3b`

### Frozen input

`S0 / B1 / T128 / Decode4 / TEXT`

Transfer receipt SHA256:

`5eff72842b2e87c79d2070b9085215e5bfca0e98c25e91155aec04aa12d6fe0d`

Historical identities:

- raw TEXT: `bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208`
- token authority receipt: `0b5a86fdee44452e74e5d80e8043ebd97054fbbe29a6232a4f5cf5d06568c7dd`
- canonical 128-token compact-JSON SHA256: `f9cf1ea6dca7956c740b3aa0af59acadd17be014df2aaffb75d240383502e3a7`
- derived token-ID payload: `fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624`

### Platform/runtime

- GPU: RTX4080, UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`
- driver: `580.178.04`
- NCU: `2025.1.1.0`
- CPython: `3.10.12`
- torch: `2.5.1+cu124`
- `libtorch_cuda.so` SHA256: `761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`
- U8.5 NVBit 1.7.5 custom lifecycle qualification remains reviewed PASS.

## Multi-model readiness

Bulk transfer of the five future model assets has completed on 109. The CPU-source lane also transferred 21 exact historical Qwen bindings:

- Qwen2.5-0.5B-Instruct: 7 exact bindings;
- Qwen2.5-7B-Instruct raw: 7 exact bindings;
- Qwen2.5-7B-Instruct-AWQ: 7 exact bindings.

Qwen3-8B and DeepSeek-V2-Lite remain `NO_HISTORICAL_FROZEN_BINDING`; do not manufacture historical bindings for them. A future unified multi-model input contract is required for those two models.

## Immediate execution order

1. Perform the provenance-only R5 evidence closeout in `CODEX_NEXT_STAGE.md`.
2. Review that closeout; if all existing R5 artifact hashes close, no measurement rerun is required.
3. Then authorize formal multi-model admission/characterization.

## Root policy

No root or host mutation is expected. Preserve current host/runtime state.
