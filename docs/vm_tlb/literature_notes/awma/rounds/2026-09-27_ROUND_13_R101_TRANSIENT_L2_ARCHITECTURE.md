# Round13｜R101R1合并架构轮：Transient L2 lifetime的最小机制验证

日期：2026-09-27。维护：ChatGPT。

本轮按用户要求合并“结果审查→最近邻排雷→机制定义→最小反证实验”到同一轮。R101R1已独立接受，不再拆出单独审查轮。

## 1. R101R1 accepted result

Authority:
- branch `hrl/awma-r101-l2-lifetime-control-v1r1`
- commit `422faf4d8fcdb5ac49068dcf19a6e783954a29a8`
- remote compare identical 0/0
- final `R101R1_EXISTING_L2_CONTROL_INSUFFICIENT_READY_FOR_ARCH_REVIEW`

Qualified L512 evidence:
- D1 `discard.global.L2`: NS-family DRAM write 346.920064 -> 255.806848 MB, -26.263%; graph 1.42259 -> 1.47078 ms, -3.39% performance.
- D2 full 44 MiB A+B persistence+discard: 337.549824 -> 338.222336 MB, no write reduction; graph 1.41718 -> 1.45402 ms, -2.60%.
- D1/D2 exact arithmetic/semantics pass; D2 policy readback verified.
- K128 NCU B0/D1 had XXT autotune block mismatch, so no K128 traffic ratio is used.
- no holdout because neither existing-control arm met timing gate.

Interpretation: current line-granular post-last-use discard can reach some dirty state but arrives too late for most traffic; the current persistence hint is not a guaranteed live-set reservation and did not reduce writes. Exact microcause (early eviction, capacity pressure, policy granularity, or combination) is not yet isolated.

## 2. Closest-work boundary

The next mechanism cannot be described merely as cache persistence, inter-kernel reuse, scratchpad sharing, or dead-block prediction.

Relevant closest capabilities:

1. NVIDIA PTX `discard.global.L2` (PTX 7.4+, sm_80+) already supports destructive 128-B L2 discard.
2. CUDA L2 access-policy/persisting controls already provide priority hints for selected regions.
3. Locality Descriptor (ISCA 2018, Vijaykumar et al.) is a cross-layer software/architecture abstraction that can coordinate CTA scheduling, cache management and placement from locality semantics.
   Source: https://research.nvidia.com/publication/2018-06_locality-descriptor-holistic-cross-layer-abstraction-express-data-locality-gpus
4. Inter-kernel Reuse-aware Thread Block Scheduling (TACO 2020) preserves/reuses data across kernel boundaries by scheduling related work on locality-compatible cores.
5. NVIDIA patent US10725837 describes persistent scratchpad data exchange across kernels. It is prior-art context for persistent on-chip kernel-to-kernel state; it is not a peer-reviewed performance baseline.
6. Classic dead-block/reuse-prediction work predicts last use for replacement/bypass; R101 has exact software-known region lifetime instead of prediction.
7. HiMuon/Flash-Muon/fused-muon already exploit symmetric compute/fused epilogues. fused-muon still materializes A/B and X/X_new across steps and lists multi-step pipeline/further fusion as future work.
8. Gram Newton-Schulz changes the algebra for rectangular matrices but routes square matrices to standard NS; R101 L512 is square.

Thus novelty cannot be “software tells cache about locality” or “keep intermediates on chip.” The first architecture experiment must be narrower and diagnostic.

## 3. Working architecture hypothesis

### Problem

R101's three-kernel step has exact software-known transient regions A, B and ping-pong X/C.

For each iteration:
- current X must survive XXT and BA until BMM;
- A is produced by XXT and dies after BA;
- B is produced by BA and dies after BMM;
- old X dies after BMM;
- new C becomes next X.

A/B/X buffers are each about 23.07 MB for the accepted L512 population. Two live buffers are about 44 MiB, close to the current device's persisting set-aside, while producer output can temporarily create a third large stream. Kernel-boundary lifetime control therefore arrives after some dirty lines may already have been replaced.

### Minimal hypothesis

A cache policy that knows “this dirty line belongs to a currently-live transient region” can preferentially retain it during the producer-consumer interval, while a line whose region is dead may be dropped without writeback.

No extra data capacity is required in the first prototype.

Working name:
`TRANSIENT_L2_V1`.

The mechanism is not claimed novel or publishable at this point.

## 4. First two interventions

### O1 — DEAD_DROP_ORACLE

Purpose: simulator/native-semantic cross-check.

At the exact accepted region-death boundaries, any resident dirty transient line is invalidated without writeback. Zero-cost range scan is allowed only as an ORACLE diagnostic.

This should reproduce the direction of D1: some writeback should disappear, but early-evicted dirty lines remain unrecoverable.

O1 is not a hardware proposal.

### M1 — BOUNDED_LIVE_RETENTION_DEAD_DROP

Finite, capacity-preserving prototype:
- tag accesses/stores that fall in the active transient ranges;
- mark transient lines with bounded region/generation metadata;
- replacement priority: invalid > dead-transient > ordinary > live-transient;
- live-transient lines are protected only while another legal victim exists;
- if all ways are live-transient, fall back to normal victim and write back if dirty;
- dirty live-transient eviction always writes back: no correctness shortcut;
- once a region is dead, its dirty resident lines may be dropped rather than written back;
- dead-transient lines become first replacement victims;
- no new data array/capacity, no unlimited pinning, no infinite victim buffer.

This tests whether current L2 capacity plus exact lifetime-aware replacement is sufficient.

M1 is an exploratory mechanism, not final architecture.

## 5. Why not start with fine-grain last-read tracking

A/B matrices are multiply inputs with repeated line reuse across many CTAs. Declaring a line dead after its first consumer load would be wrong. Future-trace last-read knowledge is forbidden.

The first mechanism therefore uses only region/kernel-phase lifetime already known by the program.

If M1 fails because region-level lifetime is too coarse, that result motivates a later question about finer producer-consumer partitioning or kernel fusion; do not silently add future knowledge.

## 6. Expected metadata/cost envelope

First-pass metadata must be finite and reported.

Suggested upper-bound accounting:
- <=4 transient descriptors: base, limit, region id, epoch/state;
- per L2 line: transient region id + bounded generation/liveness bits, no data-capacity increase;
- current RTX4080 model L2 line count is derived from accepted simulator config/line size, not assumed from native marketing specs.

A later design may compress metadata, but first-pass performance cannot ignore its logical storage size.

Do not add ports or zero-latency control messages without recording them.

## 7. Workload and simulator requirement

The existing `AWMA_RTX4080_SIM_BASELINE_V1` is scoped to AWMA memory/translation studies, not automatically qualified for L2 lifetime claims on HiMuon.

Therefore this merged round needs:

### 109 producer
Capture one exact, hash-bound R101 L512 three-kernel recurrence in simulator-native trace form, with sidecar mapping for A/B/X/C regions and kernel-phase lifetime.

Use accepted R101 payload; do not invent a synthetic workload.

A full five-step trace may be captured, but simulation may use a preregistered bounded contiguous ROI (prefer two consecutive iterations with the second as measured ROI) if full replay cost is excessive. ROI must be explicitly named and must preserve kernel order/address semantics.

### 174-new consumer
Before mechanism claims:
- admit trace with exact parser/identity gates;
- close instruction/CTA/kernel sequence;
- establish baseline cache/writeback counters;
- compare simulator baseline traffic direction/scale with accepted native R101/R101R1 without tuning platform parameters.

Absolute cycle fidelity is secondary; structural writeback behavior is primary.

If simulator cannot represent dirty L2 writeback/lifetime semantics credibly, STOP rather than fabricating a mechanism result.

## 8. Promotion logic

### O1 fails to reduce any simulated writebacks
This indicates simulator/input mapping is not representing the native D1 phenomenon. Mechanism study is blocked pending model correction.

### O1 reduces writebacks but M1 has little additional effect
Region-level retention is insufficient; do not build a full architecture around it.

### M1 substantially reduces writebacks but cycles do not improve
Traffic is not performance-primary in the simulator. Architecture performance claim remains weak.

### M1 reduces writebacks and gives a stable material cycle response
Freeze M1 before any tuning. Then add:
- one matched capacity/replacement control;
- one independent holdout/second input only if already available or cheaply captured;
- nearest-work comparison.

Only then consider a paper mechanism.

## 9. Execution organization

Run producer and consumer in parallel:

- Lane F on109: exact trace producer + native binding only.
- existing 174-new AWMA window: simulator preparation, directed tests, O1/M1 implementation; consume producer only after READY.
- Lane G remains free; do not create a third GPU question.

All simulator features opt-in/default OFF. OFF must reproduce accepted baseline exactly.

No auto-merge.

## 10. Efficiency rule from this round onward

A normal architecture round should combine:
`audit + closest-work + input prep + implementation + directed tests + first screen + diagnosis + publication`.

Do not create a new round for deterministic wrapper fixes, report cleanup, or one extra already-authorized ablation.

STOP only for scientific identity/semantics/claim changes or genuine unrecoverable payload/tool limitations.
