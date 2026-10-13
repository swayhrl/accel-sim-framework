# AWMA R27R3 independent review — B0 native reference repeatability

Review date: 2026-10-13 (Asia/Shanghai)

Stage: `AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1`

Execution branch: `hrl/awma-r27r3-numeric-attribution-capacity-109-v1`

Execution: [`7bd31fae4c54e121d54743a803d978ee02a64959`](https://github.com/swayhrl/accel-sim-framework/commit/7bd31fae4c54e121d54743a803d978ee02a64959), tree `bcd3a9ab5890a946d03a49b46df4434abff4238c`.

Exact handoff parent: `29ce051f982f3854bd4392a94e4195c59340123b`, tree `2813304af8d4f4c367f3be376a05530e336ccdba`.

Review pack: [AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1](https://github.com/swayhrl/accel-sim-framework/tree/7bd31fae4c54e121d54743a803d978ee02a64959/docs/vm_tlb/review_packs/AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1).

## Accepted scientific decision

**Accept the frozen STOP label `R27R3_B0_REFERENCE_NOT_REPEATABLE` with a strictly scoped interpretation.**

Two *preregistered*, distinct fresh-process RTX4080/native B0 controls, from the same qualified R26 CPU common start, RNG restore, fixed R27R2 WikiText-2 bank step k=0, B=1 and frozen model/CCE/backend configuration, disagree beyond the original elementwise `atol=rtol=1e-2` complete BF16 total-gradient contract. Their other required checks pass. This is an **in-contract native reference repeatability failure**, not evidence that B0 is mathematically wrong or that C1/S2 is correct/incorrect.

R27R3 correctly STOPped at B1 B0-reference repeatability. It did not run component attribution, any candidate correction, the four-step B0/C1/S2 requalification, implementation freeze, natural capacity, 32-step/resume, formal timing, profiler or hardware. No new varied-input capacity outcome exists.

## Independent review of Git and analysis artifacts

- Fetched Git commit/tree/ref directly: the execution commit is **one direct child** of the handoff; remote execution branch currently points to that exact commit. The Git diff adds only R27R3 code, review pack and final report, not historical R26–R27R2 source or contracts.
- Recomputed SHA256 independently for **all 20 Git review-pack files** against committed `SHA256SUMS`: **20/20 match**.
- Recomputed SHA256 of the `SHA256SUMS` file itself: `12afd48826240128c7003ca03911fc3ffa601ed72bbb6f2a7d0483ec325243cf`.
- Parsed `B0_REPEATABILITY.json`, `B0_REPEATABILITY_METRICS.tsv`, `FAILURE_COORDINATES.tsv` and `FIRST_MISMATCH.json`; all 25 violating coordinates satisfy the actual unchanged elementwise threshold when their recorded values are independently recomputed. All flattened indices satisfy `flat_index = vocab_row*2048 + column`. The TSV's 25 row-major records and 25 top-excess records agree with the JSON (the two categories list the same 25 failing elements).
- Read `diagnostics.py`, `repeat_controls.sh`, `audit.py`, `finalize.py` and `publish.sh`: code compares the full gradient in 2^18-element CPU chunks using `abs(got-ref) > 0.01+0.01*abs(ref)`, records first and largest failures, and uses two sequential new Python processes under one real flock. It uses `set -euo pipefail` and does not introduce any post-failure scientific gate.

This **does not mean** the reviewer reloaded/recomputed the node164 3.15GB `B0_a.pt` and `B0_b.pt` tensor payloads. The end-to-end tensor comparison is executed by the frozen node109 comparator and preserved in raw receipts; reviewer-side arithmetic independently validates the published coordinate-level material.

## Exact numerical observations

Both controls record `PyTorch 2.7.1+cu126`, CUDA 12.6, RTX4080, matching CCE meta, the same bank and R26 common-checkpoint paths, matching input/label hashes, exact post-step logical step=2, cursor=1, and tied-W pointer integrity. The recorded PIDs are 3005688 and 3005759.

Complete BF16 total gradient: `[128256,2048]`, `262668288` elements, finite. Exactly **25 violations**, fraction `9.517707748565369e-8`, distributed across two vocabulary rows:

- row **198**: 12 failing coordinates; token input frequency 1, label frequency 0;
- row **284**: 13 failing coordinates; token input frequency 2, label frequency 2.

The **first row-major mismatch** is row 198 / column 33, candidate -0.5078125 versus B0 reference -0.5234375, difference 0.015625, allowed 0.015234374441206455. The **largest tolerance-excess element** is row 198 / column 604, reference 5.40625 versus second B0 5.3125, difference 0.09375, allowed 0.06406249850988388 (excess 0.02968750149011612). Thus the first mismatch and the largest mismatch are correctly different locations.

Global max_abs=0.09375, mean_abs=`1.468182770590133e-7`, cosine=`0.999963905382874`; these global statistics are secondary and **do not override** the failed per-element criterion. Huge near-zero-sensitive max_rel is not a trustworthy global effect magnitude.

Other recorded observables satisfy the frozen tolerance: loss, next_loss, dH, updated W, FP32 m/v, step and cursor; no failing tensor contains non-finite elements. Passing W/m/v at one step cannot guarantee numerical equivalence in long training or unchanged convergence.

### Why this is not a root-cause finding

The two failing rows are both present in the input, but row 198 occurs only once. Therefore **the evidence does not support a claim that repeated-token collisions alone explain the failure**. Parallel BF16 reduction order, native embedding backward, classifier accumulation, backend/kernel scheduling, or other causes remain possibilities, not facts. Neither the baseline's elementwise variability nor the failure rows identify which kernel causes the error. The preregistered B0-repeatability gate made component-level probes terminally ineligible and the execution did not perform them.

R27R2's earlier C1/S2-vs-B0 failures on the same varied bank must now be treated as **confounded by unqualified B0 repeatability**, not retroactively reversed or reinterpreted as proven harmless. R26's separate repeated-one-sequence, tied-W-only C1 B70/B71 vs S2 B71/B72 five-step one-physical-batch finding remains unchanged.

## Provenance and closure boundary

The node164 execution receipt reports 21/21 manifest entries verified; `raw/B0_a.pt` and `raw/B0_b.pt` are each 3,152,550,620 bytes with SHA256 `fc3c975e455ce83879a8f0194d7efa98f2d46048e86de930d3455b22106d0cce` and `05e03b1fa133cb7438c3679db12cc0c5fc5ae9035ae540f47e591010e6fdd546` respectively. Archive SHA256: `802bdc5608d015f2d3e4418b957cb96cdb9e179211a6f0d44d0d2bc171bb942a`; manifest SHA256: `f5d7de83f3e363dc335e9de50b10184d537dd7b2f312eceb648195efdc87708e`.

These remote byte hashes, node164 readback, live GPU process clearance, lock release and clean worktree are **execution-side** reports: the ChatGPT reviewer did not SSH-read node164 bytes or view the node109 live processes. The Git execution branch and pack integrity were independently checked.

A minor instrumentation limitation was disclosed: an optional fd9 `/proc/$$/fd/9` readlink inside a subshell selected the parent shell PID, so no fd-owner readlink proof was produced. The launcher's real `flock -x 9` and the receipts support serialized lock use; do not describe the failed optional fd readlink as a successful independent lock-owner attestation. This does not change the scientific B0 control outcome.

## Research and authorization

R27R3 is **COMPLETE / STOP**; no GPU task is authorized by this review.

The appropriate next scientific question is how to define and establish a reproducible native numerical reference for a training reduction with BF16, and whether the permitted arithmetic order/precision error should be quantified against a valid mathematical/algorithmic reference and training-quality contract. Any kernel-level repeatability or deterministic reduction probe would require a **separate new, explicitly reviewed** bounded contract; do not restart R27R3, relax the old threshold post hoc, or jump into capacity/32-step trials.

The result is relevant to AI workload architecture research questions P08 (training gradient materialization and optimizer state) and P09 (numerical order constraining parallel/resource reorganization), but **does not establish hardware headroom**. Broader C16 and AWMA research coordination may index this accepted evidence at its own scientific evidence level; it cannot generate new experiment authorization.
