# AWMA PAPER-GRADE PLATFORM / MECHANISM CALIBRATION HANDOFF

Date: 2026-09-23

This handoff defines the next two parallel long Goals:

1. node174-new:
   `AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1`
2. node109:
   `AWMA_MECHANISM_SENSITIVE_NATIVE_CALIBRATION_109_V1`

The project objective is publication-quality architecture research.

The simulator platform is infrastructure for evaluating architectural mechanisms. It must be credible enough that large conclusions are not artifacts of an obviously wrong GPU model, but it does **not** need to reproduce every RTX4080 cycle or undocumented microarchitectural detail perfectly.

The policy is:

> validate the major architecture / memory-hierarchy behavior, bound the error, freeze the platform, and move on to the research mechanism.

Do not spend unlimited time tuning infrastructure.

---

# 1. Accepted authorities

## Native exact control evidence

`hrl/awma-crosscal-exact-measured-trace-v1r1 @ 149af0566cc6720621fdfe88d3cd3ca9b32cba67`

Exact Native M0–M3 command authority:

```text
steps=512
samples=50
warmup=2
policy=default
seed=102
```

Native contemporaneous medians-of-medians:

```text
M0 = 52.0 cycles/load
M1 = 294.0 cycles/load
M2 = 280.0 cycles/load
M3 = 152.5 cycles/load
```

M1→M2:

`-4.7619047619%`

Same-process/context ordered trace pairs exist for every M0–M3:

`warmup occurrence0 → measured occurrence1`

Node164 bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/crosscal_exact_v1r1_20260923T111500Z`

## Cross-Cal V1R1 prep authority

`hrl/awma-174-crosscal-v1r1-prep @ a04085f73458c9d30537640c2f7daad4a3aa3dd7`

Frozen conclusions:

- old Cross-Cal V1 used warmup occurrence0;
- old trace seed was unresolved;
- old evidence is `CROSSCAL_V1_WARMUP_TRACE_SUPPORTING_ONLY`;
- M0–M3 are `M0_M3_MECHANISM_INACTIVE_CONTROL_SUITE`;
- every active dependent LDG had exactly one active lane and `accessq_entries=1`;
- SM89 trace subset used by M0–M3 is parser-compatible with the Ampere opcode map;
- that parser audit is not a full Ada fidelity claim.

## Translation semantic authorities

V1:

`ad6f38878bc1e7c268b17e65fdb3793a3899a84d`

V2R1:

`dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`

Do not reopen these semantics during platform qualification.

---

# 2. Why platform qualification is now required

Current simulator base hardware authority is:

`SM86_RTX3070`

while Native evidence is:

`RTX4080 / Ada / SM89`

The existing cross-cal therefore mixes:

```text
RTX4080-generated SM89 trace
+ RTX4080 Native timing
+ SM86 RTX3070 simulator hardware model
```

This is adequate for simulator-internal causal debugging, but not for a paper claim that a simulator matches RTX4080 hardware behavior.

Therefore the next publication-quality step is to establish a scoped:

`RTX4080/Ada Accel-Sim platform baseline`

before external Native↔simulator calibration is resumed.

---

# 3. Platform philosophy: paper-grade, not perfectionist

The platform qualification must be bounded.

## 3.1 What must be right

At minimum:

- SM89/Ada trace admission for the instruction subset actually used;
- major GPU scale:
  - SM count;
  - memory bus / bandwidth class;
  - L2 capacity;
  - clock-domain order of magnitude;
- broad latency/bandwidth behavior of:
  - L1;
  - L2;
  - DRAM;
- simple compute/memory kernel ranking;
- no gross >2× systematic timing error on the small held-out platform-validation set;
- no obviously wrong direction of key memory-hierarchy trends.

## 3.2 What does NOT need to be perfect

Do not attempt to reverse-engineer or perfectly reproduce:

- proprietary scheduler heuristics;
- undocumented cache replacement details;
- exact internal Ada issue-port topology;
- exact RTX4080 TLB sizes/latencies;
- exact per-opcode timing for every SM89 instruction;
- dynamic GPU Boost behavior for every run;
- every benchmark in Accel-Sim.

If a parameter is undocumented and has little effect on the AWMA research path, inherit a reasonable Ada/nearest validated value and label it.

## 3.3 Hard effort bound

For platform calibration:

- maximum **two bounded tuning passes** after the first runnable RTX4080 config;
- every tuned parameter must be justified by:
  1. public hardware specification, or
  2. dedicated platform calibration anchor;
- no tuning against:
  - AWMA M0–M3 exact control probes;
  - T0/T1/T2 AI targets;
  - future mechanism-sensitive workloads;
- after two passes, freeze the best defensible config and classify it honestly.

This prevents infrastructure work from consuming the research project.

---

# 4. Upstream Ada engineering reference

As of 2026-09-23, upstream Accel-Sim PR:

`accel-sim/accel-sim-framework #548`

Title:

`Add sm_89 (Ada) support and RTX 4060 Laptop config`

State:

`OPEN / UNMERGED`

PR head:

`0c840b276bfecc6c7d1590efd7d5a22b8dff05f6`

The PR explicitly:

- defines binary version 89;
- maps SM89 to the Ampere opcode table;
- adds an `SM89_RTX4060_LAPTOP` trace config;
- points to a matching gpgpu-sim config in the contributor's submodule.

This is an engineering reference, not accepted project authority.

Node174 may reuse/adapt it after source review and exact commit recording.

Do not blindly merge an open PR.

---

# 5. RTX4080 platform qualification acceptance policy

The qualification is deliberately pragmatic.

Use two evidence groups:

## Calibration anchors

A small independent set used to set uncertain base-platform parameters.

Target dimensions:

- L1 hit latency / short working-set behavior;
- L2 hit latency / medium working-set behavior;
- DRAM latency;
- DRAM streaming bandwidth.

Optional only if easy:

- one arithmetic throughput anchor.

## Held-out validation anchors

At least 3 simple kernels / points not used to tune parameters, including:

- one cache-friendly memory kernel;
- one streaming / bandwidth-oriented kernel;
- one compute or mixed kernel.

The exact benchmark names may be selected from already-working Accel-Sim / CUDA microbench infrastructure.

Do not create a large new validation suite.

## Qualification thresholds

Primary target:

`median absolute runtime/cycle error <= 25%`

Acceptable scoped range:

`25% < median error <= 35%`

provided:

- key memory-hierarchy trends have the correct direction;
- no systematic gross mismatch;
- no essential held-out point exceeds 2× error without a clear unsupported-feature explanation.

Classification:

### PASS

`RTX4080_ADA_PLATFORM_QUALIFIED`

if primary target is met.

### Scoped PASS

`RTX4080_ADA_PLATFORM_QUALIFIED_WITH_SCOPE`

if median error is <=35% and the model is credible for relative AWMA mechanism evaluation.

### FAIL

`RTX4080_ADA_PLATFORM_NOT_QUALIFIED`

if:

- median held-out error >35%; or
- key memory trend has the wrong direction; or
- multiple essential held-out points are >2× wrong.

Do not keep tuning indefinitely after FAIL.

Return the exact mismatch for review.

---

# 6. Separation of data roles

For publication credibility, preserve this split:

| Evidence | Purpose | May tune platform? |
|---|---|---|
| basic GPU calibration anchors | RTX4080 base config | YES |
| held-out generic GPU anchors | platform validation | NO |
| M0–M3 Native control probes | translation/base-model research validation | NO |
| T0/T1/T2 AI targets | research evaluation | NO |
| mechanism-sensitive benchmark | V1/V2R1 external validation | NO |
| final proposed mechanism workloads | paper result | NO |

Do not violate this split.

---

# 7. New mechanism-sensitive benchmark purpose

Existing M0–M3 have `accessq_entries=1`.

They cannot exercise V1/V2R1.

Node109 therefore creates a new calibration-only benchmark family that deliberately produces:

`accessq_entries > 1`

for one warp memory instruction.

The intended mechanism opportunity is:

```text
one warp LDG
→ multiple coalesced memory transactions / accessq entries
→ multiple translation requests resident for the same memory instruction
```

This benchmark is for external semantic validation.

It is not a proposed architecture mechanism.

---

# 8. Coordination contract between node109 and node174

Node109 publishes a small platform-anchor bundle to node164 early in its Goal.

Suggested durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/rtx4080_platform_anchors_v1_<timestamp>`

Node174 should:

1. complete all Ada/config engineering work independently first;
2. then consume the node109 platform-anchor bundle if it has appeared;
3. do not block early progress waiting for node109;
4. if the bundle is still absent only at the final calibration phase, wait/poll for a bounded period or STOP with:
   `WAITING_FOR_RTX4080_PLATFORM_ANCHOR_BUNDLE`
   rather than inventing Native data.

The mechanism-sensitive benchmark bundle is separate and need not be consumed during the platform-qualification Goal.

---

# 9. After these two Goals

If node174 achieves:

`RTX4080_ADA_PLATFORM_QUALIFIED`

or:

`RTX4080_ADA_PLATFORM_QUALIFIED_WITH_SCOPE`

then the next stage will be:

1. exact M0–M3 contextual cross-calibration on the RTX4080-like simulator platform;
2. mechanism-sensitive benchmark replay under Legacy/V1/V2R1;
3. baseline promotion decision.

No new TLB/PTW/cache mechanism should be designed before that review.

