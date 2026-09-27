# CODEX GOAL — AWMA R101R1 Existing L2 Lifetime-Control Requalification V1

## Mission

Run one bounded **native software/ISA control** before any architecture simulation.

Stage:

`AWMA_R101_L2_LIFETIME_CONTROL_REQUALIFICATION_V1R1`

Scientific question:

> Can existing SM89 L2 lifetime controls — especially PTX `discard.global.L2`, optionally combined with supported L2 persistence/access-policy — suppress the accepted R101 short-lived intermediate writeback traffic without changing the fixed Newton–Schulz map, and does that materially reduce runtime?

This Goal decides whether R101 should:
- close as an existing-software/ISA opportunity,
- downgrade because DRAM writeback is not performance-primary,
- or proceed to later architecture mechanism review because existing controls are insufficient.

It does **not** authorize node174 or Accel-Sim.

Repository:
`swayhrl/accel-sim-framework`

Handoff branch:
`hrl/awma-r101-l2-lifetime-control-v1r1-handoff`

Accepted R101 execution:
- branch: `hrl/awma-r101-fixed-ns-intermediate-lifecycle-v1`
- commit: `cfbe6503585fa1b10d979db5d26fb9be3a80e563`
- accepted state: `R101_INTERMEDIATE_RETENTION_READY_FOR_ARCH_REVIEW_V1`

Suggested execution branch:
`hrl/awma-r101-l2-lifetime-control-v1r1`

Literature/architecture-review authority:
`hrl/awma-chatgpt-literature-notes-v1 @ 002020ca5d1b486c1143c8a64d5ebd9f391d337b`

Read:
`docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_12_R101_ARCH_REVIEW_L2_LIFETIME.md`

Node:
109 / RTX4080 / SM89 only.

Every CUDA operation holds:
`/data/c16/locks/c16_gpu_campaign.lock`.

No node174, no Accel-Sim, no NVBit full trace, no new model download.

---

# 0. Preserve R101 history

Do not modify or reinterpret the accepted R101 review pack.

R101 remains valid for exactly what it established:

- real Qwen-derived gradient/momentum input;
- same-map S128 F128 vs K128 material response;
- independent holdout;
- material L256/L512 author-path cost;
- source/NCU evidence of large intermediate materialization;
- unresolved marginal attribution between traffic, compute scheduling, occupancy and instruction differences.

R101R1 is a **new control**, not a replacement for R101.

Do not rerun gradient generation unless accepted raw payload cannot be deterministically recovered.

---

# 1. Reuse exact accepted payloads

First locate the accepted node164 authority and R101 raw index:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_fixed_ns_intermediate_lifecycle_20260927/`

Reuse the accepted frozen:
- discovery S128 input batch;
- discovery L512 input batch;
- holdout S128/L512 input batches if needed;
- exact model/source/environment receipts.

Verify against accepted hashes:
- S128 discovery payload:
  `09358f3f21265a9c3a8cdd9681efdaa93a06db7c8d1e1afdbb017e60f0e85544`
- L512 discovery payload:
  `1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234`

If raw tensor files were intentionally not retained but accepted gradient microstate + deterministic tiling can reproduce them, deterministic reconstruction is allowed only if the resulting hashes match exactly.

Do not classify a reconstructible wrapper/cache path as missing science.

If the exact payload cannot be recovered:
`R101R1_ACCEPTED_PAYLOAD_NOT_RECOVERABLE`
and STOP.

---

# 2. Pin the exact author baseline

Reuse:

`tang0389/himuon@af89eda9a0176effed99e1fe19cc1f8a1a2c9588`

The arithmetic path must remain:

1. normalization;
2. for five iterations:
   - `XXT(X,out=A)`;
   - `ba_plus_cAA(A,out=B)`;
   - `fused_bmm_add(B,X,a,out=C)`;
   - swap `X,C`.

Coefficients remain:

`a=3.4445, b=-4.7750, c=2.0315`

No:
- Gram Newton–Schulz;
- different polynomial;
- different NS step count;
- different tile size;
- fused-muon/Flash-Muon substitution;
- algorithmic pruning.

HiMuon already uses symmetry and fused epilogues. Do not weaken the baseline.

Create:
`R101R1_BASELINE_IDENTITY.json`.

---

# 3. ISA capability audit before scientific execution

The PTX contract to test is:

`discard.global.L2 [ptr], 128;`

Requirements:
- PTX 7.4+ semantics;
- target sm_80+;
- 128-byte aligned address;
- exactly 128-byte discard granularity.

Compile one minimal SM89 canary in the isolated lane environment.

Record:
- nvcc/ptxas version;
- PTX target;
- cubin hash;
- PTX/SASS evidence that the intended instruction survives;
- runtime success.

Query and record device properties relevant to L2:
- L2 size;
- persisting-L2 maximum set-aside;
- maximum access-policy-window size;
- relevant CUDA runtime support.

Do not assume consumer Ada exposes a useful persistence capacity.

Create:
`R101R1_L2_CAPABILITY_RECEIPT.json`.

If `discard.global.L2` cannot execute naturally on the accepted SM89 environment after at most two bounded engineering repairs:
`R101R1_L2_CONTROL_NOT_QUALIFIED`
and STOP.

Do not substitute another GPU.

---

# 4. Freeze dead-value lifetime

The following lifetime is part of the scientific contract and must be enforced by stream order.

For each NS iteration:

### After `ba_plus_cAA(A -> B)` completes
`A` is dead:
- it is not read again in the current iteration;
- the next iteration overwrites all of A via `XXT`.

### After `fused_bmm_add(B, X -> C)` completes
both are dead:
- `B` is not read again before full overwrite next iteration;
- old `X` is not read again; after X/C swap that old buffer is only a future output destination.

### Final output
The final new-X buffer remains live.
Do **not** discard it before the caller/optimizer consumes it.

No discard may race a producer or consumer.
All discard kernels are launched in the same ordered stream/graph as the arithmetic kernels.

Create:
`R101R1_LIFETIME_CONTRACT.md`.

---

# 5. Implement D1: discard-only

Implement one minimal range-discard CUDA kernel.

Recommended semantics:

- one logical work item per 128-byte aligned cache line;
- inline PTX `discard.global.L2 [addr], 128`;
- no load from the discarded range;
- no CPU synchronization;
- launch is capturable in CUDA Graph;
- no allocator/free inside the timed graph.

Apply it exactly at the dead points from Section 4:

- after BA: discard A;
- after BMM-add: discard B and old X;
- final live X stays intact.

Use accepted K128 and L512 exact maps.

Names:

- `K128_B0_GRAPH` — accepted-style baseline;
- `K128_D1_DISCARD_GRAPH`;
- `L512_B0_GRAPH`;
- `L512_D1_DISCARD_GRAPH`.

The arithmetic kernels and inputs are identical between B0 and D1.

---

# 6. Correctness gate for D1

Before timing, require for K128 and L512:

- output shape exact;
- finite;
- exact same fixed input;
- all arithmetic kernel identities/counts unchanged;
- discard kernels only added at declared dead points.

Primary correctness requirement:

`D1 output is bitwise equal to B0 output`.

If a source-identical deterministic replay demonstrably produces benign non-bitwise variation even without D1, freeze an exact control explanation before using the accepted R101 `rtol=atol=1e-2` fallback. Do not weaken the contract because D1 differs.

Also run a liveness canary:
- perturb one frozen input element;
- graph replay must change output;
- restore input;
- output returns to reference.

If D1 changes live semantics:
`R101R1_DISCARD_PLACEMENT_NOT_QUALIFIED`
and STOP scientific timing.

---

# 7. Formal D1 timing

For K128 and L512:

- 1 canary;
- 2 warmups;
- 7 formal repetitions;
- paired/interleaved B0/D1 ordering;
- fixed pointers;
- graph replay;
- no profiler in primary timing.

Measure:
- CUDA-event complete operator time;
- host elapsed secondary;
- discard-kernel duration/count separately;
- peak allocation.

Primary materiality:
- >=5% median improvement;
- >3x the larger relative jitter/noise envelope.

Do not compare K128 and L512 against each other as equivalent maps.

---

# 8. NCU traffic audit for D1

Use accepted R101 baseline NCU as authority only if:
- exact arithmetic cubin/source identity matches;
- input hashes match;
- execution path is unchanged.

Otherwise recollect the matching B0 profile.

Collect D1 NCU for:
- K128;
- L512.

Maximum new D1 NCU profiles: 2.

Required metrics:
- NS-family `dram__bytes_read.sum`;
- NS-family `dram__bytes_write.sum`;
- L2 requested bytes;
- active cycles;
- registers/shared as explanatory metadata.

The discard kernels must be listed separately.

Define:

`write_reduction = 1 - D1_NS_family_DRAM_write / B0_NS_family_DRAM_write`.

Accepted B0 context:
- K128 NS-family DRAM write ~270.537472 MB;
- L512 NS-family DRAM write ~344.716928 MB.

Do not use NCU replay duration as primary timing.

---

# 9. D1 decision and D2 admission

## Case A — D1 reduces L512 NS-family DRAM writes by >=50%

Do **not** run D2.

Interpret using timing:

### A1. runtime also improves materially
Proceed to holdout with D1.
Potential final:
`R101R1_EXISTING_DISCARD_SOFTWARE_EFFECTIVE`.

### A2. runtime improvement <5% or <=3x jitter
Final:
`R101R1_WRITEBACK_NOT_PERFORMANCE_PRIMARY`.

This means destructive writeback elimination works but does not explain the material R101 performance gap well enough to motivate a writeback-focused architecture.

STOP after publication.

## Case B — D1 reduces L512 NS-family DRAM writes by <50%

D2 is admitted only if device capabilities expose a useful L2 persistence/access-policy mechanism.

Reason:
D1 may arrive too late because dirty lines were already evicted/written back before their explicit last-use discard.

---

# 10. Implement D2: persistence + discard, conditionally

Do not run D2 unless Case B occurs.

First create an **arena control** with the exact arithmetic map:
- A and B allocated as deterministic contiguous views from one preallocated arena;
- no persistence;
- no discard;
- same output and author tolerance;
- timing recorded as `L512_A0_ARENA_GRAPH`.

Arena use is only to expose one bounded access-policy window; it must not change math.

D2:

`L512_D2_PERSIST_DISCARD_GRAPH`

Use existing CUDA L2 persistence/access-policy APIs on the A/B arena if and only if:

- persisting-L2 set-aside is nonzero;
- maximum access-policy window is sufficient for the declared region;
- all API calls succeed naturally.

Preferred region:
- A+B together if supported.

If A+B cannot be covered but at least one full L512 A or B buffer can be covered, pre-register **one** buffer before running D2; choose A first and do not switch based on timing.

Do not invent multiple policy sweeps.

After each declared last use, still issue D1-style discard.

Record:
- set-aside bytes;
- policy window base/size;
- hit ratio;
- exact API values;
- arena hashes.

If persistence is unsupported or too small for one complete 23,068,672-byte L512 buffer:
record:
`D2_NOT_AVAILABLE_CURRENT_SM89_RUNTIME`
and do not replace it with another cache trick.

---

# 11. D2 correctness/timing/profile

Same correctness contract as D1.

Formal:
- 1 canary;
- 2 warmups;
- 7 paired A0-arena/D2 repetitions.

NCU:
- maximum 1 additional L512 D2 profile.

No parameter sweep.

D2 is material only if:
- exact semantics pass;
- L512 DRAM write reduction is stable and substantial;
- runtime >=5% faster than A0 arena;
- >3x noise.

---

# 12. Conditional holdout

Run accepted layer12 holdout only if D1 or D2 produces a material >=5% timing effect.

Use the exact accepted holdout payloads from R101.

No retuning.

Only the already-selected winning software arm is run.

Require:
- correctness;
- direction reproduced;
- >=5% effect or a clearly reported weaker result;
- traffic direction consistent where one bounded NCU holdout profile is not necessary by default.

No holdout NCU unless discovery evidence becomes contradictory.

---

# 13. Architecture interpretation

R101R1 is specifically a **boundary test** between existing ISA/software and new architecture.

Choose exactly one final state.

## `R101R1_ACCEPTED_PAYLOAD_NOT_RECOVERABLE`
Scientific payload cannot be recovered/reconstructed exactly.

## `R101R1_L2_CONTROL_NOT_QUALIFIED`
Existing PTX control cannot be executed/verified on SM89.

## `R101R1_DISCARD_PLACEMENT_NOT_QUALIFIED`
Lifetime placement changes live semantics.

## `R101R1_EXISTING_DISCARD_SOFTWARE_EFFECTIVE`
Existing discard (with or without admitted persistence) materially reduces both write traffic and runtime, with holdout support.

Interpretation:
R101 becomes primarily a compiler/runtime/ISA opportunity.
Do not start architecture simulation.

## `R101R1_WRITEBACK_NOT_PERFORMANCE_PRIMARY`
Existing control removes >=50% of NS-family DRAM writes but does not produce a material timing gain.

Interpretation:
writeback traffic is not sufficient to explain the R101 performance gap.
Do not build a writeback-suppression architecture from R101.

## `R101R1_EXISTING_L2_CONTROL_INSUFFICIENT_READY_FOR_ARCH_REVIEW`
Allowed only if all hold:

1. accepted R101 problem evidence remains valid;
2. D1 exact semantics pass;
3. D1 cannot suppress >=50% of L512 write traffic, or its explicit 128B range-discard overhead materially cancels the benefit;
4. if D2 is legally available, D2 also fails to close the residual;
5. the reason is localized to current lifetime-control granularity/capacity/early eviction rather than Python/launch overhead;
6. current closest software (HiMuon, Flash-Muon, fused-muon, Gram NS for square tiles) does not already provide an equivalent exact-map retained-intermediate implementation;
7. no final hardware speedup is claimed.

Only this state authorizes a **later ChatGPT architecture mechanism design/review**.

It still does not automatically authorize node174.

## `R101R1_MIXED_L2_CONTROL_RESULT`
Use if traffic/timing evidence is contradictory and none of the above is scientifically justified.

---

# 14. Closest-work boundary to retain

The final review must explicitly note:

- HiMuon already uses symmetric half-work kernels and fused epilogues.
- Flash-Muon reduces symmetric compute but materializes global intermediates.
- fused-muon uses SYRK/fused epilogue but still keeps A/B global workspace and X/X_new ping-pong; its documented future work includes GEMM2+GEMM3 fusion and multi-step NS pipeline.
- Gram Newton–Schulz changes the algebra for rectangular matrices; its code selects standard NS for square matrices like R101 L512.
- PTX `discard.global.L2` already expresses destructive line discard.
- CUDA L2 persistence already expresses a form of producer-consumer residency influence.
- Hopper DSMEM/thread-block clusters are a separate later-hardware capability, not present on SM89.

Do not claim novelty from any of these.

---

# 15. Publication

Durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_l2_lifetime_control_v1r1_20260927/`

Review pack:

`docs/vm_tlb/review_packs/AWMA_R101_L2_LIFETIME_CONTROL_V1R1/`

Minimum:
- README.md
- R101_INHERITANCE.md
- SOURCE_AND_CLOSEST_WORK_AUDIT.md
- ENVIRONMENT_RECEIPT.json
- R101R1_BASELINE_IDENTITY.json
- R101R1_L2_CAPABILITY_RECEIPT.json
- R101R1_LIFETIME_CONTRACT.md
- PREREGISTRATION.json
- SEMANTIC_RESULTS.tsv
- TIMING_RESULTS.tsv
- TRAFFIC_RESULTS.tsv
- optional ARENA_CONTROL.tsv
- optional D2_PERSISTENCE_RECEIPT.json
- optional HOLDOUT_RESULTS.tsv
- R101R1_DECISION.md
- FINAL_DECISION.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Closure:

`science/engineering -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree -> clean -> GPU released -> STOP`.

No auto merge.
