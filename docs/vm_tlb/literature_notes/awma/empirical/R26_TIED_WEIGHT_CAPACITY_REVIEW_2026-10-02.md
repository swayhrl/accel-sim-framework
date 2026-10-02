# R26 tied-weight integrated batch-capacity review

Date: 2026-10-02 (Asia/Shanghai)

Execution: [`1a2485011b300cddd5137bbccb91dd6d30cfc22f`](https://github.com/swayhrl/accel-sim-framework/commit/1a2485011b300cddd5137bbccb91dd6d30cfc22f), tree `cce37bbbd368b545bea92c7b86cb429d8da4f48b`. Parent is the exact R26 handoff `67bb4c00236e52657130dd91ddf44fb6a2e22c87`.

Stage: `AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1`. [Execution review pack](https://github.com/swayhrl/accel-sim-framework/tree/1a2485011b300cddd5137bbccb91dd6d30cfc22f/docs/vm_tlb/review_packs/AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1).

## Review decision

Accept the frozen classification `R26_INTEGRATED_BATCH_CAPACITY_EXTENSION_SUPPORTED` **for this integrated tied-W training protocol**. The demonstrated batch boundary moves from C1 B70 to S2 B71 on the accepted Llama point, with three fresh-process confirmations per endpoint and a same-B witness. It is a one-physical-batch extension (1/70 ≈ 1.43%), not a general memory-footprint, speed, full-model-training, or production-deployment result.

This closes R26 at STOP. No R27, new GPU work, node174/Accel-Sim, profiler or hardware/PPA activity is authorized by this review.

## Frozen identity and implementation

- Model: `meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`; all six model payload sizes and SHA256 are recorded as checked in the execution receipt (2,480,783,094 bytes). Input: pre-existing `ADOPTED_LLAMA_S0_T128_V1`, no re-tokenization; T=127.
- Only BF16 tied embedding/lm_head W is trainable with FP32 AdamW m/v. The complete frozen backbone still participates in forward and dH backward. The batch is B physical copies of the *same* sequence, so B does not measure data diversity or a new holdout.
- One integrated component defaults to C1. S2 requires explicit `policy="s2"` and capacity opt-in, with no OOM fallback. C1 uses compact lookup and one full V×H total gradient; S2 uses the same compact lookup with 4096-row tiles and no full V×H gradient/shadow.
- I compared the component, campaign runner and capacity-search source bytes with `IMPLEMENTATION_FREEZE.json` and their Git tree blobs. The pre-result freeze precedes the capacity trials. The capacity search/classifier is generic and fixed before outcomes; no result-driven tile, input or classifier change appears in those files.

The R25 parent supplied a start-state **hash receipt but no snapshot payload**. A B1 B0 bootstrap under accepted semantics, even when replayed with the exact R25 runner, did not reproduce the parent's W/m/v bit hashes; CPU/CUDA RNG hashes matched. R26 disclosed this and froze one CPU post-bootstrap state (`COMMON_POST_BOOTSTRAP.pt`, logical step 1) for every arm, endpoint and formal sample. Accordingly, comparisons share a valid **R26 common start**, while exact bitwise continuity with the R25 parent is unproved. This does not justify describing the start as an exact recovered R25 snapshot.

## Numerical and capacity evidence

Fixed `rtol=atol=1e-2` qualification passed B1 B0/C1/S2 one-step, B1 four-step, C1/S2 32 uninterrupted steps, step-17 fresh-process resume to logical step 33, the C1-checkpoint C1/S2 policy switch to step 18, and B70 one-step endpoint comparison. Full W/m/v checkpoints were checked at trajectory indices 1/4/8/16/32. These checks establish short trajectory and state-serialization consistency, not convergence or task quality.

The frozen capacity trial is five uninterrupted complete training steps (two warmups plus three further steps) in a fresh process from the common CPU state. PASS requires every step, finite state and exact counter; only unambiguous CUDA OOM qualifies as OOM. The published search table contains 43 trials; the bracket outcomes and 3/3 endpoint confirmations are internally consistent.

| Policy | Largest confirmed PASS | Adjacent confirmed OOM | OOM phase |
| --- | ---: | ---: | --- |
| C1 | B70, 3/3 | B71, 3/3 | `BACKBONE_COMPACT_LOOKUP_BACKWARD` |
| S2 | B71, 3/3 | B72, 3/3 | `BACKBONE_COMPACT_LOOKUP_BACKWARD` |

At the selected same-B witness B71, C1 is OOM 3/3 and S2 is PASS 3/3. The node receipt reports C1 completed two steps and then failed on the third backward allocation (142 MiB), while S2 completed all five with finite losses/W/m/v/counter and no persistent active-allocation rise after the first step. The C1 OOM at B71 cannot provide a matching full-B numerical reference; equivalence is supported at B1 and B70. This is a real complete-loop feasibility distinction under the specified repeated-step allocator history; it does not identify a universal capacity gain or an isolated kernel peak as the cause. The two adjacent OOM phases are in the shared backbone/compact-lookup backward path.

## Whole-step memory and formal timing

At common B70, the formal median **whole-step peak allocated** is C1 15,942,519,296 bytes (15,203.97 MiB) versus S2 15,946,533,376 bytes (15,207.80 MiB). S2 is **4,014,080 bytes (3.828 MiB) higher**. The successful S2 B71 peak is approximately 16,112,538,624 bytes (15,366.1 MiB). The R25 target-region memory reduction therefore must not be represented as a lower R26 whole-step peak at B70.

I independently recalculated medians and MADs from all 30 retained samples for each formal region. `C1−S2` is positive in every group but below the frozen `3×max(MAD)` threshold each time:

| Region | G0 delta / threshold (ms) | G1 delta / threshold (ms) | G2 delta / threshold (ms) | Point |
| --- | ---: | ---: | ---: | --- |
| TARGET_REGION | 2.995 / 9.431 | 4.718 / 7.785 | 4.965 / 11.293 | MIXED |
| COMPLETE_TRAIN_STEP | 2.573 / 9.027 | 4.828 / 8.100 | 4.530 / 11.048 | MIXED |

The complete-step timing excludes common-state restore and loading, and measures this compute loop. No stable speedup claim follows from nominal median direction.

## Verification and evidence boundary

- Git execution SHA/tree and handoff parent match; all **31 Git review-pack file SHA256 values** match its `SHA256SUMS`. Source bytes match freeze hashes. Independent arithmetic reproduces formal timing directions, B70 memory delta and the tabulated adjacent endpoint outcomes; published numerical rows are qualified and finite.
- The execution pack reports a node164 archive/checkpoint manifest with 207 verified items, remote push/fetch-back, lock release, no campaign CUDA process and a clean execution worktree. I did **not** independently inspect the node164 raw receipts, checkpoints, OOM tracebacks, the exact 142 MiB allocation request, or current GPU process state from this review environment. Those details remain node reports.
- The CPU finalizer encodes the observed B70/B71 endpoint labels and the C1 step-3 detail in its report construction. The independently read capacity-search TSV supports the endpoint outcomes and phases; the raw step-3 traceback is outside the Git pack. Treat finalizer text as a report, not an independent raw replay.
- Model-payload verification, raw receipt/archive hashes and GPU-clean closure are execution receipts, not a new reviewer-side node attestation. No new CUDA run was made for this review.

## Research boundary

This is useful evidence for retaining S2 as an explicit capacity-oriented path in this tied-W component. A production hardening decision would need separate scope and should test whether the B71 distinction survives genuinely varied batches and longer realistic training histories, with attention to the shared backward/allocator limit. The present result does not support making S2 the default, claiming deployment readiness, or inferring full-parameter training headroom.
