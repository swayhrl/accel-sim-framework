# START HERE — AWMA Round08 parallel exploration V1

## Mission and authority

Read the Round08 literature note at:
`hrl/awma-chatgpt-literature-notes-v1 @ 214b30039cc579c28457cb17bfbd7e9d88d00fcd`
`docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_08_PARALLEL_PROBLEM_DISCOVERY.md`

Execution base: `d6ef29505de75985181afc74dffc3cf1b652afc2`.
Coordination branch: `hrl/awma-round08-parallel-exploration-handoff-v1`.

Two independent windows:
- R81: `CODEX_GOAL_109_R81_LEGAL_VOCAB_V1.md`
- R82: `CODEX_GOAL_109_R82_LAYOUT_TRANSFER_V1.md`
Both files are in this directory.

Only run the Goal assigned to your window. A stopped lane does not stop the other. Do not wait for the other lane's scientific result. No auto-merge and no shared mutable working tree.

## Scientific scope

These are literature-guided small prototype/diagnostic explorations, NOT established novel hardware problems. A small prototype may help discover a mechanism response; 5% prior headroom is not a prerequisite for trying it. Later promotion requires strong baselines, causal discrimination, cost and validation.

Accepted R51–R54 and older AWMA evidence stays immutable. Do not redo platform calibration, semantic-contract requalification or trace audits. Historical negatives only apply within their actual scope.

No new model downloads, driver/system-CUDA changes, full NVBit traces, Accel-Sim runs, PPA, parameter sweeps, or third GPU research question. Reuse accepted weights/read-only inputs; new source packages go to lane-isolated environments. Source and kernel adaptations must retain licenses.

## Parallel execution without measurement contamination

Both Codex windows can be on109. CPU source audits, literature, unit tests, parsers and builds that do not touch GPU may proceed in parallel after RAM/I/O inspection. Every operation touching CUDA — including model loading, GPU JIT/warmup/canary/profile — holds:
`/data/c16/locks/c16_gpu_campaign.lock`

Each lane uses separate branch, worktree, environment, build, HF/TRITON/CUDA cache, TMPDIR, logs and output directory. Suggested execution branches:
- `hrl/awma-r81-legal-vocab-exploration-v1`
- `hrl/awma-r82-layout-transfer-exploration-v1`

Use existing lock utilities, not a new scheduler. Hold the lock for one bounded paired measurement bundle, then drain your streams, terminate your GPU subprocess/release your device allocations, and release the lock. Do not leave a model resident after releasing the lock. Do not kill another job or modify GPU clocks globally. When waiting for the GPU, continue independent CPU work or block using the existing lock; no high-frequency polling. Record any external activity; do not accept contaminated timing.

Only read shared model assets. Reuse verified hashes/receipts rather than repeatedly copying or hashing multi-GB inputs without cause. 164 remains durable authority;174 may perform offline analysis only, not unapproved simulations. Do not write large raw into174 local storage.

## Ordinary engineering

Solve routine wrapper/parser/path/build issues in the lane. Classify missing material: scientific payload versus deterministically reconstructible control/index/receipt or ephemeral cache. Reconstruct derivable wrappers in isolated staging with explicit provenance; do not report a missing filename as missing science.

Count a bounded repair as a substantive implementation/environment strategy, not each shell command. Keep at most two implementation strategies per intervention and one necessary correctness correction; no cycling through new models/prompts to obtain positive output. If scientific identity is unresolved, close that arm honestly and continue other authorized arms.

## Measurement and evidence

Freeze input IDs, exact code/runtime, numerical contract, target/shape and configurations before candidate-effect timing. First use a correctness canary; passing canaries immediately authorize the corresponding formal bundle in the same Goal.

Default formal: 2 warmups + 7 paired/interleaved repetitions. Save individual values and median/spread. Very short primitives may use a preregistered fixed repeat count for timing resolution, with outputs observable and no compiler elimination; primitive timing is not application timing. Profiling and validation are separate from primary timing. Do not sum overlapping host/GPU/copy durations into a causal decomposition.

5% is an investment-scale reference, not proof of zero cost and not a reason to prohibit cheap diagnostics. Keep small/noisy effects as such. Holdout is truly unused content or invocation, not a prefix/subset already examined for design. No tuning on holdout.

At most2 focused NCU target/arm comparisons per lane, only when answering a registered mechanism question. Query available metrics; no assumed TLB/physical-page counters. Use NSYS for control/launch/timeline questions. Neither metric changes nor local speedups alone imply end-to-end speedup.

## Closure

Each lane creates a compact review pack and a separate164 root under:
`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/round08_20260927/<R81-or-R82>/`

Git includes source/tests, compact results, README/decision, input/environment bindings, raw index and hashes. Large tensors/weights/profiles stay on164. No concurrent appends to a shared catalog; use lane-local immutable entries.

Complete: validation ->164 publish/remote hashes -> review pack -> commit/push -> fetch-back -> exact remote SHA/tree -> clean worktree -> GPU lock released -> STOP.
Publication transport failure does not invalidate science; preserve the exact local commit and use existing HTTPS/HTTP1.1/SSH/gh alternatives. Do not rerun science because push failed.

Do not use the other lane as an independent holdout. Subsequent architecture work always requires a separate review.
