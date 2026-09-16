# C16 Qwen3 S3 KV context-scaling campaign — node109 V20

## Execution mode and host contract

Execute this task in **GOAL MODE** on **node109**, using the same producer environment/workflow as the previous successful Qwen3 producer campaigns.

This is a node109 GPU-producer task. Scientific execution and Git work must use the node109 Linux Framework repository/worktree, e.g.:

`/home/huangrulin/workspace/accel-sim-framework`

or a node109 worktree created from it.

**Do not use the local Windows mirror such as `D:\repo\accel-sim-framework` for this scientific implementation branch.**

Do not install/configure `gh`, do not switch authentication mechanisms, and do not import the 174-new Git transport procedure. Node109 should keep its existing Git authentication/remote behavior that was already used successfully by prior producer Goals.

Do not stop after setup, state capture, replay preparation, static audit, S2 recapture, or partial formal capture while downstream stages remain executable.

Suggested implementation branch:

`hrl/c16-qwen3-s3-kv-scaling-109-v20`

## Scientific objective

Establish a clean apples-to-apples context-scaling comparison for the exact same Qwen3 semantic path:

`layer0.self_attn.repeat_kv(K)`

Evidence class:

`KV_STORAGE_DIRECT_READ`

Compare:

- S2_TEXT B1/T2048 first decode
- S3_TEXT B1/T8192 first decode

using the **same isolated replay and same full-scope capture method on both sides**.

This V20 deliberately does **not** depend on retrieving the V19R1 implementation branch or its literal scope classification. V19/V19R1 remain historical audit evidence only. To remove all residual baseline ambiguity, V20 always creates a fresh canonical full-scope S2 baseline before S3.

Do not relabel QK/AV as direct KV-cache reads. QK/AV remain derived-buffer evidence only.

## Immutable authorities

Model/runtime:

- `Qwen/Qwen3-8B`
- revision `b968826d9c46dd6066d109eabc6255188de91218`
- BF16
- eager attention
- pinned Transformers 4.51.0 runtime already used by accepted Qwen3 evidence

Canonical V2 inputs:

S2_TEXT:

- B1/T2048/D32
- payload SHA256 `5913c573054d23a444477394a60f3f280311325e81175663b4ae2abd5ef6aafb`

S3_TEXT:

- B1/T8192/D16
- payload SHA256 `4acf772ccf5596edb0a2589624b5fd0e61da447024ca23bf944118dc948c36c2`

Prior accepted semantic/dataflow authority:

- Qwen3 V18R2 producer HEAD `5d29ad8babe47226cbd25180a6db133e9526b6cf`
- semantic target `layer0.self_attn.repeat_kv(K)`
- proven typed chain: `KV_POST_UPDATE_K -> KV_DERIVED_REPEAT_K`
- source/destination non-aliasing
- QK consumes K-derived repeat buffer, not original K storage

V18R2/V19 dynamic totals are not used as the canonical S2 scaling baseline in V20. V20 creates a fresh S2 full-scope baseline with an unambiguous isolated replay.

## Stage 1 — generate exact S2 and S3 K-post states

For both S2 and S3, use the already-authorized exact semantic layer-streaming method:

checkpoint -> selective exact loader -> all 36 true decoder layers -> true KV cache -> true next token -> layer0 first decode -> exact post-update K

No synthetic hidden state, lower precision, backend substitution, fake KV, or model/input substitution.

Expected K-post shapes:

- S2: `[1,8,2049,128]`
- S3: `[1,8,8193,128]`

Persist scenario-specific CPU K-post tensors and receipts containing at least:

- input authority SHA
- model revision/runtime
- decode token/position
- shape/dtype/stride
- tensor SHA256
- storage size

## Stage 2 — canonical isolated repeat-K replay

For **each scenario independently**, launch a fresh process whose target CUDA work is only:

1. load the exact frozen CPU K-post tensor;
2. transfer it to CUDA;
3. call pinned `repeat_kv(K, num_key_value_groups)` exactly once under a unique NVTX range;
4. synchronize;
5. emit source/output hashes and storage metadata.

Avoid another invocation of the same direct-copy CUDA function before the target call in that process.

Require:

- source tensor hash equals the frozen exact K-post state;
- output is bitwise equal to the corresponding in-context/instrumented repeat result;
- source/destination are non-aliasing;
- source range is typed `KV_POST_UPDATE_K`;
- output range is typed `KV_DERIVED_REPEAT_K`;
- in-context and isolated target signatures are semantically equivalent for the same scenario.

Record kernel function/grid/block for S2 and S3. Grid size is expected to scale with context length and need not match.

## Stage 3 — clean full-scope capture environment

Before every formal shard subprocess construct a clean environment and explicitly remove inherited scope filters.

At minimum unset/remove:

- `C16_CTA_BEGIN`
- `C16_CTA_END`
- any equivalent inherited CTA/block range selector

Do not inherit an old C16 capture scope accidentally through `os.environ.copy()` without sanitizing it.

Use a fresh per-scenario capture root.

Bind to the exact isolated target function/occurrence. Because the isolated process executes the target direct-copy function only once, occurrence ambiguity must be eliminated by construction rather than inferred from launch order.

## Stage 4 — fresh static/global-address-path audit

For the isolated repeat-K target:

- obtain fresh SM89 SASS/static map, or prove exact binary/function identity before reusing a static set;
- audit direct GLOBAL MREF;
- independently audit LDGSTS/GLOBAL_TO_SHARED;
- audit other address-bearing special paths;
- exclude pure control/memory-control instructions from address-bearing evidence.

Freeze the complete target static set before formal capture.

If S2/S3 use the same binary function and static set, record SHA equality explicitly; do not assume it silently.

## Stage 5 — full-scope S2 formal baseline

Capture the complete frozen static MREF set for the **canonical isolated S2 repeat-K replay**.

Requirements:

- `FORMAL_ADMISSION_CONCURRENCY=1`;
- expected shard count == present shard count;
- all shards terminal closed;
- drop total 0;
- overflow total 0;
- each shard has same-process `ADDRESS_CONTEXT`;
- explicit executed vs `ZERO_EXECUTION_PROVEN` classification;
- sufficient trace capacity for the entire launch.

### Mandatory full-scope gate before admission

Independently decode all executed C16WARP1 shards and record:

- records/events;
- unique CTA coordinates;
- CTA x min/max;
- warp IDs;
- active-address min/max;
- membership in that replay's `KV_POST_UPDATE_K` and `KV_DERIVED_REPEAT_K` ranges.

For the K-source-read evidence, require:

- dynamic addresses losslessly join `KV_POST_UPDATE_K`;
- no inherited CTA slicing;
- CTA coverage is consistent with the full isolated target launch, including lower and upper launch extent where the relevant static instruction executes;
- no evidence of wrong function occurrence.

Do not infer full scope from event count alone.

If the gate fails due a correctable capture configuration error, correct it within this Goal and recapture S2. Do not proceed to S3 admission using a partial S2 baseline.

When S2 passes, close the formal bundle, perform the single serial Pipeline admission, and wait for positive verification/catalog/ACK before starting the S3 formal admission.

Do not modify/delete V18R2 or any older accepted catalog entry.

## Stage 6 — full-scope S3 formal capture

Using the exact same sanitized isolated-replay methodology, capture the S3 target.

Requirements are identical to S2, including the full-scope CTA/object-membership gate.

Capacity must be sized for the larger S3 launch; do not reuse a limit that can truncate S3.

Only after S2 ACK is positive may S3 be admitted. Keep `FORMAL_ADMISSION_CONCURRENCY=1` throughout.

Transfer/verify/admit S3 and wait for positive receiver ACK.

## Stage 7 — NCU

Preserve bounded NCU reports for canonical isolated S2 and S3 replays when feasible.

Record numeric metrics only when explicit values and units are available. Preserve any uncontrolled-cache warning. Do not infer bytes from ambiguous units and do not claim cache/TLB causality from NCU differences alone.

NCU gaps do not invalidate an otherwise hash-closed trace scaling comparison; type the gap explicitly.

## Stage 8 — S2 -> S3 context-scaling analysis

Use only the two fresh V20 full-scope captures.

Compare:

- semantic target identity;
- K-post and repeat tensor shapes;
- kernel function/grid/block;
- static MREF set size/SHA;
- executed/zero partition;
- total active-lane events;
- per-executed-shard event distribution;
- per-shard 4K/64K/2M pages;
- per-shard 128B lines;
- same-process `KV_POST_UPDATE_K` membership;
- formal completeness/drop/overflow;
- typed NCU comparability.

Safe claims:

- same-target event-count scaling;
- launch-dimension scaling;
- per-shard footprint-count scaling.

Forbidden:

- cross-process absolute-VA comparison;
- cross-replay VA union;
- cross-shard/global chronology reconstruction;
- reuse-distance inference from independent shards;
- cache/TLB causality from event scaling alone.

## Stage 9 — review pack

Create:

`docs/vm_tlb/review_packs/C16_QWEN3_S3_KV_SCALING_109_V20/`

Include at minimum:

- S2/S3 input/state receipts;
- isolated-replay equivalence/signature receipts;
- clean-environment/capture-scope receipt;
- static/path audit;
- S2 formal summary + CTA/object full-scope audit + Pipeline ACK;
- S3 formal summary + CTA/object full-scope audit + Pipeline ACK;
- NCU typed evidence;
- S2-vs-S3 comparison;
- `FINAL_DECISION`;
- `OPEN_ISSUES`;
- `SHA256SUMS`.

A PASS is scoped only to `layer0.self_attn.repeat_kv(K)` as `KV_STORAGE_DIRECT_READ` materialization behavior.

## Stage 10 — node109 Git closure

Use the **existing node109 Git authentication mechanism exactly as before**. Do not install/configure `gh` and do not switch to SSH/HTTPS merely for this Goal.

Commit the scientific artifacts on the implementation branch:

`hrl/c16-qwen3-s3-kv-scaling-109-v20`

Push using the same node109 remote workflow already proven by prior producer campaigns.

Verify the pushed branch/HEAD using the mechanisms available on node109. Do not require `gh api` if `gh` is not installed on node109.

Do not ask the user to perform routine commit/push work manually.

## Stop conditions

Fail closed only for a real scientific/execution blocker, e.g.:

- model/input/revision hash mismatch;
- exact S2/S3 K-post state cannot be generated without prohibited substitution;
- isolated replay/output/signature mismatch;
- static/address-path closure failure;
- full-scope gate cannot be satisfied after bounded correction;
- drop/overflow;
- Pipeline rejection/negative verification;
- terminal artifact corruption.

Do **not** fail closed because the V19R1 implementation branch is unavailable to node109; V20 no longer depends on it.

On a blocker, preserve all valid evidence, hash-close a typed partial review pack, commit/push it from node109, and STOP.

Otherwise continue autonomously through S2 baseline recapture, S3 capture, scaling analysis, review-pack closure, and Git push, then STOP.
