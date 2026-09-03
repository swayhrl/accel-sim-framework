# M5 v1 Approval and Frozen Interpretation

Status: **APPROVED — M5 COMPUTE GOAL AUTHORIZED**

Approval date: 2026-09-03.

This file records the researcher-approved interpretation of `M5_EXPERIMENT_MATRIX.md` and activates it as the M5 v1 experiment specification. The older `PLANNING DRAFT` banner inside `M5_EXPERIMENT_MATRIX.md` is superseded by this approval file; the detailed matrix content remains authoritative unless a later researcher-approved revision explicitly changes it.

## 1. Research objective

M5 is a **mechanism/trend reproduction** of the already implemented Decoupled-Tag Cache work, not a numeric-target reproduction of the thesis' reported +22% / +30% averages.

The experiment must show whether the RTL mechanism, when represented in the validated simulator, actually produces its intended causal chain:

`traditional L1 structural limits -> constrained concurrent misses -> DTC removes those limits -> more live concurrent misses / better latency hiding -> performance effect`.

If performance is weak, negative, or differs greatly from the thesis, Codex must diagnose whether the cause is:

- implementation/modeling fidelity;
- workload or input fidelity;
- surrounding platform/downstream bottlenecks;
- traffic side effects;
- compute-bound behavior;
- or a genuine mechanism limitation.

Do not tune mechanisms, inputs, or downstream parameters to force a target speedup.

## 2. Approved workload strategy

The ten thesis general-purpose compute algorithms are the first formal workload target. Graphics preparation runs in parallel so it can attach immediately after compute review if a source-backed path becomes available.

The first M5.0 provenance audit must explicitly resolve:

- thesis `gemv` versus canonical PolyBench `gemver`;
- thesis `gesu` versus canonical PolyBench `gesummv`;
- thesis `conv2d` versus canonical PolyBench `2DConvolution` / current `pb_2dconv`.

These remain hypotheses until source/algorithm evidence confirms them.

Missing binaries, wrappers, standard inputs, or PTX are resolve-in-goal problems, not ordinary stop conditions. Canonical source should be recovered/rebuilt where scientifically justified; algorithms must not be silently substituted.

## 3. Approved Figure 4.5 primary configuration

For the primary Base/IO/OO main-result reproduction:

- PAPER_BASE: conventional 16KB L1 data cache, 128B line, 4-way, PIB=8, MSHR=32.
- PAPER_IO: **16KB logical Tag capacity + 80KB physical Cacheline Array**, PIB=256.
- PAPER_OO: **16KB logical Tag capacity + 80KB physical Cacheline Array**, PIB=128.
- Other frozen M1-M4 paper-mode defaults remain unchanged unless the platform-fidelity audit proves the runtime configuration differs.

The 16KB DTC label in the primary paper-facing result refers to the logical cache/Tag capacity; the physical Cacheline Array remains the frozen 80KB implementation default. Figure 4.9 is the experiment that explicitly varies physical capacity.

## 4. Approved Figure 4.7 concurrent-miss metric

The live-miss lifecycle is frozen as:

> a new L1/DTC miss becomes live when it is committed into lower-request ownership and remains live until its final lower response completes that request.

Pending-hit merges do not create another live miss. A real duplicate lower request created after logical-Tag eviction is a separate live miss.

The **primary Figure 4.7 plotted metric** is:

`avg_concurrent_misses_per_sm = sum(live_miss over all SMs and sampled cycles) / (num_SM * sampled_kernel_cycles)`.

Also retain GPU-total cycle-average and peak values as audit/diagnostic outputs.

Base, IO, and OO must use the same lifecycle and sampling boundary. Do not compare heterogeneous occupancy proxies (for example Base MSHR occupancy versus DTC NoC occupancy) under the Figure 4.7 label.

## 5. Approved Figure 4.2 category interpretation

The formal paper-facing Figure 4.2 contains only these four categories:

1. waiting-instruction-buffer / PIB full;
2. true Tag & Cacheline allocation failure;
3. MSHR capacity/merge failure;
4. Miss Queue / lower-request-capacity failure.

`TAG_BANK_CONFLICT` is **not** the thesis' Tag & Cacheline allocation-failure category. Tag-bank arbitration conflict and other pipeline stalls must be emitted separately as diagnostic channels.

Formal Figure 4.2 percentages use the four-category paper-equivalent denominator. A separate full diagnostic breakdown may include Tag-bank and other stalls.

## 6. Goal-mode problem policy

Once M5 starts, normal implementation and experiment problems should be solved inside the same Goal rather than stopping for human confirmation. Follow `M5_PROBLEM_RESOLUTION_POLICY.md`.

Examples that should normally be diagnosed/repaired and continued automatically include:

- missing workload/wrapper/input;
- build or PTX-extraction failures;
- missing counters/parsers;
- workload assertions or completion bugs;
- dynamic-count mismatch;
- timeouts with diagnosable progress state;
- disappointing or negative speedup;
- a paper-discussed bottleneck not appearing under the chosen input;
- Tag-bank/downstream domination;
- stale formal data after a justified repair.

A pause is reserved for a true researcher-decision boundary: changing frozen M0/M1-M4 architectural semantics, irreducible scientific ambiguity, inability to source-verify a required compute algorithm without substituting a different experiment, contradiction of a researcher-frozen metric definition, or the terminal compute review state.

## 7. Authorized progression

The persistent Goal is authorized to execute continuously:

`M5.0A -> M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`.

Each substage must satisfy the acceptance criteria and emit the handoff required by `M5_HANDOFF_CONTRACT.md`, commit/push compact evidence, update `codex_handoff/LATEST_REPORT.md`, and continue automatically.

Graphics G0-G2 may progress in parallel but must not block compute M5 or contaminate compute formal anchors.

Terminal compute state:

`M5_COMPUTE_READY_FOR_REVIEW`.

Do not begin post-review graphics formal aggregation, sector-extension paper comparisons, area claims, or other M5.7+ supplemental studies unless separately authorized after compute review.
