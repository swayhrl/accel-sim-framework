# Codex Goal — Lane F / node109
## VLA RTC inference-time VJP problem-boundary qualification V1

Date: 2026-09-30

This is one continuous solve-and-continue Goal for **Lane F / node109**.

Execution branch:
`hrl/awma-vla-rtc-vjp-boundary-109-v1`

Read first:
- `docs/vm_tlb/chatgpt_handoff/awma/round16_problem_contracts_v1/VLA_RTC_VJP_CONTRACT_V1.md`
- `docs/vm_tlb/chatgpt_handoff/awma/round16_problem_contracts_v1/SOURCE_AND_SCOPE_NOTES.md`
- `docs/vm_tlb/chatgpt_handoff/awma/round16_dual_lane_v1/START_HERE.md`

## 0. Question

Answer only:

> In a real, frozen VLA/RTC action-generation path with the **full network VJP actually present**, does VJP-related state/lifetime/materialization remain a material part of complete action-chunk readiness after one strong software implementation?

Do not assume memory is the bottleneck. Do not claim robot task improvement.

## 1. Phase F0 — source and semantic authority, CPU first

### F0.1 Freeze source identities

Audit and record exact current commits/blobs for:

- Hugging Face LeRobot RTC implementation;
- SmolVLA implementation;
- `lerobot/smolvla_libero` checkpoint metadata;
- required processor/tokenizer/dataset revisions;
- Physical Intelligence Kinetix RTC implementation as algorithmic reference only.

Do not pin to mutable `main` in final receipts.

Kinetix's ~60 GiB expert/data tree is **not** an allowed prerequisite. Do not download it for this Goal.

### F0.2 Prove that the current PyTorch RTC path computes the network VJP

Before any model download or GPU run, implement a CPU analytic canary around the exact RTC wrapper.

For a toy denoiser `v(x)=2x`, under the LeRobot time convention:
`x1 = x - t*v(x)`.

The VJP correction must include the denoiser Jacobian and equal:
`(1 - 2*t) * error`
for the chosen scalar/vector fixture.

Run at several nondegenerate `t` values and tensor shapes.

If the untouched current RTC code returns only the identity contribution or otherwise fails:

- classify as `UPSTREAM_RTC_VJP_SEMANTIC_GAP_OBSERVED`;
- make **one minimal reference repair** whose only purpose is to restore the published full-VJP semantics, normally by ensuring gradient tracking is established before the denoiser evaluation;
- bind the repair as a new local reference identity;
- re-run analytic canary.

Do not count repaired-vs-buggy runtime as an optimization.

If a minimal repair cannot restore the published semantics without changing the RTC algorithm, STOP:
`VLA_RTC_VJP_REFERENCE_NOT_QUALIFIED`.

### F0.3 Real-model graph canary

After CPU semantic qualification, verify on the exact SmolVLA action-expert path that:

- model weights remain frozen;
- gradients with respect to action latent exist;
- the VJP graph actually traverses action-expert/denoiser operations, not only `x -> x`;
- no parameter gradients are accumulated;
- the visual/language prefix is not unnecessarily backpropagated if the accepted implementation legally caches/detaches it;
- no cross-step unbounded `retain_graph`.

Use hooks / autograd graph inspection / a bounded directional derivative check as appropriate.

If this fails after the one allowed semantic repair, STOP.

## 2. Phase F1 — real input and asset admission

Search existing node164/node109 assets first.

If absent, a bounded public download is allowed only for:
- the exact SmolVLA LIBERO checkpoint and required config/processor files;
- the minimum dataset shards/samples needed for the frozen two-episode open-loop replay.

Store durable assets on node164; node109 may hold an active replica/cache.

Before download:
- record URLs/revisions/file sizes;
- reject accidental full-corpus or multi-tens-of-GiB downloads not required by the contract.

Input admission:
- batch = 1;
- preselect two eligible LIBERO episodes deterministically before timing;
- four consecutive chunk windows per episode;
- episode A = discovery;
- episode B = sealed validation;
- same language/state/image observations, initial noise and RTC settings across arms;
- previous action chunk must come from the same qualified reference execution, not demonstration actions.

If the exact public model/dataset cannot be obtained or run on RTX4080 without changing the model/algorithm contract, STOP:
`VLA_RTC_INPUT_OR_PLATFORM_NOT_QUALIFIED`.

Do not switch to Kinetix and call it VLA evidence.

## 3. Phase F2 — natural reference census

Acquire the shared GPU lock only after F0/F1 close.

Create A0 = the semantically qualified full-VJP reference.

Run numerical canaries first.

Then collect **uninstrumented complete chunk-ready timing**:
observation input ready -> complete action chunk committed.

Use the frozen repetition policy:
- 3 paired groups;
- 2 warmups/group;
- 5 uninstrumented measurements/group;
- save every sample, median, MAD.

Separately account:
- prefix/VLM work;
- repeated denoiser work;
- VJP;
- correction/update/commit;
- any true overlap.

Record:
- peak GPU allocation;
- saved-tensor identity/deduplicated logical bytes;
- recomputation count if measurable;
- number of denoise/VJP steps;
- kernel/launch census.

Saved-tensor bytes are **not** DRAM traffic.

Do not use profiler runtime as primary timing.

## 4. Phase F3 — headroom before optimization

Before building A1, answer:

> If only the identified VJP state/materialization/lifetime overhead were idealized away while mandatory VJP arithmetic and dependencies remain, what is the largest defensible complete-chunk gain?

Construct this from the dependency/timeline evidence.

Do not use:
- A0 minus no-guidance as hardware headroom;
- sum of independent kernel durations;
- `max(producer,consumer)` without a legal overlap dependency graph.

If no defensible numeric bound exists, label it UNKNOWN and proceed only if the natural measured component itself is clearly material and localizable.

If the defensible full-chunk upper bound is <5%:
decision = `VLA_VJP_LIFETIME_HEADROOM_BELOW_5_PERCENT`;
do not build mechanism; publish and STOP.

## 5. Phase F4 — one strong software arm

Only if F3 warrants continued work.

A1 must preserve the full RTC algorithm and VJP semantics.

Audit existing LeRobot/PyTorch compile/caching first.
Choose **one** bounded software intervention, not a tuning matrix.

Preferred order:
1. compile/capture the repeated action-denoise + VJP body if current PyTorch supports it safely;
2. otherwise use a single static-buffer / allocation-reuse implementation around the same body.

Do not:
- remove VJP;
- change denoise steps/guidance/dtype/model;
- train a new checkpoint;
- rewrite the whole framework;
- create several optimization variants and select the best afterward.

Compilation cost is reported separately and excluded from steady-state only if deployment would legitimately amortize it.

A1 must pass the frozen numerical contract on discovery data before timing.

## 6. Phase F5 — bounded profiling

Only after A0/A1 uninstrumented timing is frozen.

At most:
- one NSYS capture sufficient to bind the chunk timeline;
- two NCU exact targets chosen from the observed residual, not preselected to force a memory explanation.

Query actual SM89 metrics before NCU.
Unsupported counters remain unavailable.

Possible questions:
- is VJP dominated by Tensor/math execution?
- are saved/reloaded activations or ordinary global memory dependencies dominant?
- are launch/synchronization gaps material?
- is A1 already closing the target state/lifetime cost?

No NVBit/SASS trace in this Goal.

## 7. Phase F6 — sealed validation

Open episode B only if discovery shows:
- same algorithm/numerical contract;
- >5% defensible complete-chunk residual or improvement opportunity after strong software;
- a concrete residual class, not just "VJP is expensive".

Run the same A0/A1 timing protocol on episode B.

Do not tune A1 after viewing B.

## 8. Decision labels

Use exactly one primary label:

- `VLA_RTC_VJP_REFERENCE_NOT_QUALIFIED`
- `VLA_RTC_INPUT_OR_PLATFORM_NOT_QUALIFIED`
- `VLA_VJP_LIFETIME_HEADROOM_BELOW_5_PERCENT`
- `VLA_VJP_STRONG_SOFTWARE_SUFFICIENT`
- `VLA_VJP_COMPUTE_DOMINANT_NO_MEMORY_ARCH_GAP`
- `VLA_VJP_STATE_LIFETIME_RESIDUAL_PRESENT`
- `VLA_VJP_RESULT_MIXED_NEEDS_REVIEW`

`STATE_LIFETIME_RESIDUAL_PRESENT` requires:
- full-VJP semantic qualification;
- real VLA input;
- A1 numerical equivalence;
- >5% complete-chunk residual/headroom;
- validation episode same direction;
- evidence that the residual is a state/materialization/dependency issue rather than mandatory math alone.

No architecture mechanism is authorized even if this label is reached.

## 9. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_VLA_RTC_VJP_BOUNDARY_109_V1/`

At minimum:
- `README.md`
- `SOURCE_IDENTITY.json`
- `VJP_SEMANTIC_CANARY.tsv`
- `REFERENCE_REPAIR.md` if repair was needed
- `INPUT_RECEIPT.json`
- `TARGET_WINDOWS.tsv`
- `A0_TIMING.tsv`
- `HEADROOM_ANALYSIS.md`
- `A1_DESIGN.md` if triggered
- `A1_TIMING.tsv` if triggered
- `VALIDATION_TIMING.tsv` if triggered
- `PROFILE_SUMMARY.tsv` if profiling triggered
- `FINAL_DECISION.md`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

Large raw/assets remain on node164.

## 10. Closure

Release GPU lock.
Commit/push/fetch-back verify exact SHA/tree.
Clean worktree.
STOP.

Do not start a VLA hardware mechanism, 174 simulation, CCE/Liger, or another model automatically.
