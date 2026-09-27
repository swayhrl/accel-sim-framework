# CODEX GOAL — R82 native on-chip layout-transfer exploration V1

Enter Goal mode. Read START_HERE.md and follow its shared isolation/lock/publication rules. Execute only R82. Do not wait for R81.
Stage: `AWMA_R82_LAYOUT_TRANSFER_EXPLORATION_V1`.

## 1. Question and existing capabilities

After modern layout lowering, does an already optimized real AI kernel still pay material or mechanistically informative on-chip redistribution/synchronization cost between producer and consumer layouts? Can a small legal layout/communication intervention expose the cause?

This is not generic GPU resource scaling, a global layout optimizer, or a new thread-register-decoupled architecture. A data transfer is not automatically a bottleneck; an IR convert_layout is not automatically a native instruction.

Read:
- Linear Layouts: https://arxiv.org/html/2505.23819v5 — conversion optimizations and actual hardware evaluation.
- FIBER: https://arxiv.org/abs/2608.19628 — directly relevant shared-register architecture. Round08 has only the original abstract, so do not invent its full boundaries.
- Tensor Seeks Layout: https://arxiv.org/abs/2608.21555 — global layout choice/cost modeling; only original abstract audited in Round08.

Source authority:
`triton-lang/triton@eb93a9a97e5dfc6a20c29da0096c047dbabd514c`
`lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp`
blob `f5c1b400a8a45b579271696e73b9ebf9fb16e7f2`.

This source eliminates no-op conversions, permits register-only permutation, then warp shuffle, else swizzled shared-memory exchange with scoped synchronization. Those are mandatory baseline capabilities, not candidate contributions.

## 2. Target scope and deterministic selection

Use accepted assets from execution base `d6ef29505de75985181afc74dffc3cf1b652afc2`.
Audit at most3 source paths in this order:
1. Accepted Qwen3.5-0.8B FLA chunk GatedDeltaNet path, Hub FLA revision `6d22ed1d2bb627375b6ca8fc135f7f417863e639`; use a real prefilling call with model-derived tensors.
2. Accepted P1 parallel Triton fixed-split-256 attention/reduction implementation; bind its source and input from the original P1/P2 review pack.
3. One other already-accepted source-accessible Triton AI kernel, chosen by descending existing native duration, lexical identity to break ties. No new model/framework to fill a quota.

First inspect generated optimized IR and native lowering. Advance at most2 targets with a nontrivial conversion that can actually be identified. If a path has no surviving nontrivial conversion, record it and continue the bounded list. Do not manufacture redundant conversions in the baseline.

For each target bind model/operator/layer/scenario or explicit diagnostic-fixture identity, shapes/dtypes, tensor hashes, exact implementation, compiler options and kernel signature. Real input missing but deterministically recoverable from accepted model is allowed one bounded capture under GPU lock; no new model download. Synthetic primitive fixtures must remain DIAGNOSTIC_ONLY.

## 3. Current compiler versus accepted runtime

Reuse the accepted installed Triton/kernel binary initially. Record its actual version/source/hash, not just the latest upstream version. Compare the relevant lowering capabilities with the pinned current source above.

If the installed compiler lacks a directly relevant already-known conversion optimization, use a separate environment and one bounded source-correct update/adaptation to establish a modern software control. Never silently compare a newly optimized candidate only against an obsolete baseline.

A complete build of all upstream toolchains is not required. If a credible equivalent control cannot be established within two implementation strategies, report BASELINE_NOT_QUALIFIED rather than claim hardware need.

Do not mutate accepted C16/R54 environments or kernels. Compiler/source experiments are lane-local. All GPU JIT, model loading and testing use the shared GPU lock.

## 4. Conversion evidence ledger before candidate timing

For each surviving conversion record:
- tensor/producer/consumer identity;
- source and destination logical-to-register/lane/warp/block mapping;
- class: NOOP, REGISTER_ONLY, INTRA_WARP_SHUFFLE, INTER_WARP_SHARED, OTHER_UNKNOWN;
- optimized IR instruction/region;
- emitted PTX/SASS range where traceable;
- static shared/register/scratch use;
- required synchronization scope;
- whether the same barrier also protects another pipeline dependence;
- repetition structure/dynamic multiplicity if actually known.

Unknown mapping/count remains unknown. Do not assign all shared loads/stores or barriers in a kernel to layout conversion. Do not derive data-cache/TLB claims from these instructions.

Freeze target choice, candidates, launch shape, arithmetic contract and holdout source before candidate-effect timing.

## 5. Two bounded interventions per target

B0 CURRENT_STRONG: the credible current compiler/library implementation with relevant known optimizations.

C1 JOINT_LAYOUT: at most one source-level producer/consumer layout change selected from the code/dataflow, designed to reduce or change the specific transfer. Keep logical tile coverage, precision, mathematical operations and reduction arithmetic structure unchanged where possible. If that is impossible, record the changed variables and do not label it pure layout causality.

C2 LEGAL_TRANSFER: at most one alternative lowering using real existing SM89 instructions and finite resources — e.g. a legal shuffle/permutation sequence versus shared staging, or reduced-scope synchronization only where all consumers are covered. No new imaginary ISA, free communication, lost values, or removing a barrier that protects non-layout dependencies.

Not every target needs both interventions. A small intervention can be diagnostic even if it slows execution. Do not scan block sizes, warp counts or shared capacity to find a winner. Do not implement FIBER wholesale.

## 6. Correctness distinct from backend logit rankings

For an extracted redistribution primitive, use unique integer-tag values and nontrivial permutations to require exact element coverage/bitwise transfer. Include tail masks, broadcast/duplicate semantics, warp boundaries and actual relevant tensor shape. Keep outputs externally observable so compiler dead-code elimination cannot fake savings.

For full kernels, compare the same input/output under B0/C1/C2. Pure movement that preserves arithmetic must preserve values exactly, subject to demonstrated baseline repeatability. Also check no races/source overwrite with an available legal sanitizer/canary; no shared mutable result buffers across runs.

If a candidate changes reduction order/precision, it is a different arithmetic implementation, not a pure data-movement comparison. Do not add top2/top8 ranking gates unrelated to this kernel. A numerical difference must be localized and recorded; no post-hoc tolerance or repeated redesign to obtain passing output.

The accepted baseline remains immutable. Correctness failures invalidate the candidate arm, not unrelated valid candidates or the entire research field.

## 7. Native measurements

At most2 real targets × (B0 plus up to2 candidates) =6 main discovery configurations.
Each: canary,2 warmups,7 paired/interleaved formal repetitions. For sub-resolution kernels use one fixed timing batch count chosen before candidate effects; classify repeated microkernel context separately from natural application context.

Primary: complete target-kernel or fixed operator-region runtime, with exact output checks outside timing. Record registers, shared bytes, grid/block, output identity and whether global reads/writes or compute instructions changed. Do not call a primitive speedup an end-to-end model speedup.

When evidence calls for it, at most2 focused NCU comparisons may distinguish shuffle/shared/barrier execution, occupancy/resource limits or memory traffic; bind actual available metrics and replay/cache policy. Native timing stays the authority. NSYS is appropriate for launch/host timing, not for claiming individual register-bank delays.

A disabled conversion replaced by an identity/no-op with incorrect data is not a valid optimized implementation or strict speedup bound. Compiler IR counts and barrier-stall counters alone are not a causal time decomposition.

## 8. Holdout and literature closure

If a real target has a reproducible effect or informative cost tradeoff worth following, use one pre-reserved input or invocation from an unused layer/step. Select it before candidate timing; the original target and a leading prefix subset are not independent validation. Run B0 plus the chosen candidate once as a formal paired bundle; no retuning.

Before any architecture novelty suggestion, compare the observed missing capability with Linear Layouts, global layout selection and FIBER. Obtain the latter's full primary text if available; otherwise say NOVELTY_NOT_CLOSED. A different name or smaller test model is not differentiation. A demonstrably lower-cost capability at fixed resources may justify future study, but no such result is assumed.

Possible final states:
- R82_NO_SURVIVING_TRANSFER_IN_SCOPE
- R82_CURRENT_SOFTWARE_SUFFICIENT_IN_SCOPE
- R82_PRIMITIVE_ONLY_NO_APPLICATION_EVIDENCE
- R82_BASELINE_OR_SEMANTICS_NOT_QUALIFIED
- R82_NATIVE_TRANSFER_RESPONSE_REQUIRES_REVIEW

The last state is permission to discuss a future hypothesis, not to modify174. 5% is a scale for further investment, not a precondition for the small prototype and not proof of zero effect below it.

## 9. Deliverables and STOP

Review pack:
`docs/vm_tlb/review_packs/AWMA_R82_LAYOUT_TRANSFER_EXPLORATION_V1/`.
Minimum: README/DECISION, SOURCE_CAPABILITY_MAP.md, TARGETS_AND_PREREGISTRATION.json, CONVERSION_LEDGER.tsv, IR_NATIVE_BINDINGS.md, TEST_RESULTS.tsv, TIMING_RESULTS.tsv, optional diagnostics/holdout, finite resource/cost notes, code/tests, RAW_DATA_INDEX.tsv and SHA256SUMS.

Keep incomplete source/measurement claims explicit. Complete shared164/Git closure, release GPU, STOP independently of R81. No new calibration, simulator run, full trace, PPA or further research topic.
