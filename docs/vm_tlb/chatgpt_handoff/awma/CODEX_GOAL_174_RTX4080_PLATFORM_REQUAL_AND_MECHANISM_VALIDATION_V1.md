# CODEX 174 GOAL — Frozen RTX4080 Requalification + Exact Cross-Cal + Mechanism-Sensitive Matrix V1

Date: 2026-09-23

Mode:

`GOAL MODE / LONG-RUN / CONDITIONAL CONTINUE / SOLVE-AND-CONTINUE`

Node:

`174-new`

Stage:

`AWMA_RTX4080_PLATFORM_REQUAL_AND_MECHANISM_VALIDATION_V1`

Read first:

`docs/vm_tlb/chatgpt_handoff/awma/REVIEW_RTX4080_PLATFORM_V1_AND_MECHANISM_NATIVE_V1_2026-09-23.md`

Accepted authorities:

- RTX4080 platform V1:
  `646844c513ba316eae4188cb517c2eef7282132d`
- implementation:
  `aeec5b9a69865012b16ac0a6627143e29f1fee06`
- mechanism-sensitive Native:
  `6b75a3da3e3fedea6a359cd3657bf3e3fa2655d7`
- exact M0–M3 Native/context pairs:
  `149af0566cc6720621fdfe88d3cd3ca9b32cba67`
- V1 semantic authority:
  `ad6f38878bc1e7c268b17e65fdb3793a3899a84d`
- V2R1 semantic authority:
  `dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`

Create fresh execution branch:

`hrl/awma-174-rtx4080-platform-requal-mechanism-v1`

Use isolated worktree/runtime roots.

---

# Phase A — restore the frozen final RTX4080 platform exactly

Recover the exact final V1 candidate.

Required frozen config SHA256:

`de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`

Do not modify any platform parameter.

Do not perform a third tuning pass.

Do not change:

- L1 latency;
- L2/ROP latency;
- DRAM latency;
- clock domains;
- L2 capacity;
- SM count;
- memory-controller topology;
- parser support;
- pipeline parameters.

Record exact binary/config/source authority.

If reconstruction cannot reproduce the frozen config SHA, STOP:

`FROZEN_RTX4080_CONFIG_IDENTITY_NOT_REPRODUCIBLE`

---

# Phase B — obtain corrected node109 held-out Native evidence

Search node164 for the new bundle whose evidence class is:

`RTX4080_HELDOUT_MATCHED_NATIVE_TIMING_V1`

Expected node109 branch will be:

`hrl/awma-109-rtx4080-heldout-scale-match-v1`

Do not require a hard-coded commit before it is published; verify the final Git and node164 authority once found.

If not yet available:

- complete all independent reconstruction/setup work first;
- then poll/wait for a bounded period;
- if still absent, STOP:
  `WAITING_FOR_MATCHED_HELDOUT_NATIVE_EVIDENCE`

Do not substitute old mismatched H_STREAM/H_COMPUTE timings.

---

# Phase C — no-tuning held-out requalification

Use exactly the frozen final RTX4080 platform.

Replay exactly the existing immutable held-out traces:

- H_CACHE;
- H_STREAM;
- H_COMPUTE.

Use the corrected matched-scale Native timing.

Do not recapture traces on 174.

For each point compute:

`absolute_relative_error = |sim_us_per_launch - native_us_per_launch| / native_us_per_launch`

Use the same simulator-cycle→time conversion contract as V1.

Publish exact source/trace/config/binary SHA for each row.

## C1. Decision gate

Use the ORIGINAL predeclared policy:

### PASS

`RTX4080_ADA_PLATFORM_QUALIFIED`

if median held-out absolute error <=25%, key trends credible, and no essential point >2× wrong.

### Scoped PASS

`RTX4080_ADA_PLATFORM_QUALIFIED_WITH_SCOPE`

if 25% < median <=35%, trends credible, no systematic gross mismatch, and no essential point >2× wrong.

The existing H_CACHE 43.48% row is allowed to be a single outlier if the three-point median passes and it is <2×.

### FAIL

`RTX4080_ADA_PLATFORM_NOT_QUALIFIED`

if median >35%, major trend is wrong, or multiple essential points are >2× wrong.

If FAIL:

- publish the no-tuning requalification;
- STOP;
- do not tune;
- do not run later science phases.

This is the final platform gate.

---

# Phase D — freeze platform baseline if PASS/scoped PASS

If Phase C passes:

promote the exact unchanged config as:

`RTX4080_ADA_ACCELSIM_BASE_V1`

Record:

- qualification class;
- exact config SHA;
- exact binary SHA;
- parameter provenance;
- V1 tuning ledger;
- matched held-out V1R1 results.

Do not alter the config later in this Goal.

---

# Phase E — AWMA VM overlay integration smoke

Layer the accepted AWMA VM model on top of the frozen RTX4080 base.

Use existing research overlay:

`10/80`

This does NOT mean RTX4080 hardware TLB latency is 10/80.

It remains:

`AWMA_MODEL_RELATIVE_VM_CONFIG`

Run only:

- M0 one contextual point;
- M1 one contextual point.

Require:

- terminal;
- no parser/config failure;
- translation coverage closes where emitted;
- controller quiescent.

If ordinary engineering mismatch:

solve-and-continue.

Do not tune platform or VM parameters.

---

# Phase F — exact M0–M3 contextual control cross-calibration

Use the exact node109 bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/crosscal_exact_v1r1_20260923T111500Z`

For every M0–M3:

replay:

`warmup occurrence0 → measurement occurrence1`

sequentially in one simulator context/process.

Collect primary metric only from measurement occurrence1:

`CLOCK64_BRACKET_SIM_CYCLES_PER_DEPENDENT_STEP`

Expected measurement brackets:

```text
M0 = 50
M1 = 50
M2 = 800
M3 = 50
```

## F1. Context-persistence audit

Before admission, explicitly document whether across the warmup→measurement boundary the simulator preserves:

- L1/L2 cache state;
- TLB state;
- PWC state;
- relevant VM/controller state;
- memory contents/mapping.

Do not change simulator semantics merely to force state persistence.

Any natural simulator boundary reset must be reported as scope.

## F2. Control matrix

Because M0–M3 are mechanism-inactive controls, run:

```text
M0 Legacy 10/80
M0 Legacy 0/80
M1 Legacy 10/80
M1 Legacy 0/80
M2 Legacy 10/80
M2 Legacy 0/80
M3 Legacy 10/80
M3 Legacy 0/80
```

plus semantic sentinels:

```text
M1 V1 10/80
M1 V2R1 10/80
M2 V1 10/80
M2 V2R1 10/80
```

Total:

`12 points`

Do not run redundant full 24-point control matrix.

## F3. Exact Native references

Use:

```text
M0 = 52.0
M1 = 294.0
M2 = 280.0
M3 = 152.5
M1→M2 = -4.7619047619%
```

Primary comparison is relative behavior, not absolute cycles.

Compute:

- M1/M0;
- M2/M1;
- M3 supporting ratio(s);
- 10/80→0/80 model-relative sensitivity.

Carry explicit scope:

`RTX4080_ADA_BASE_V1 + AWMA_MODEL_RELATIVE_VM`

Do not claim hardware TLB latency/capacity.

---

# Phase G — bind mechanism-sensitive node109 bundle

Use:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/mechanism_sensitive_accessq_v1_20260923T114500Z`

Configs:

```text
A1_CONTROL
A8
A32
A32_W8
```

Native medians:

```text
A1_CONTROL = 321
A8         = 338
A32        = 388
A32_W8     = 393
```

Native relative behavior:

```text
A8/A1      = 1.0529595016
A32/A1     = 1.2087227414
A32_W8/A32 = 1.0128865979
```

Each pair must replay:

`warmup occurrence0 → measurement occurrence1`

in one context.

Expected measurement brackets:

```text
A1  = 50
A8  = 50
A32 = 50
A32_W8 = 400
```

---

# Phase H — actual simulator mechanism-opportunity closure

Reuse the accepted opt-in accessq-cardinality telemetry.

If extension is needed for new PCs, keep it observational-only and opt-in.

For the target measurement LDG, publish actual:

- active lanes;
- accessq entry count;
- histogram;
- min/mean/max;
- fraction >1.

Required admission:

```text
A1_CONTROL: cardinality approximately 1
A8:         cardinality >1 and consistent with ~8 transaction opportunity
A32:        cardinality >1 and consistent with ~32 transaction opportunity
A32_W8:     same per-warp multi-entry opportunity
```

Exact accessq count need not equal trace-level unique 128B-line count if the simulator's coalescing contract groups differently, but the relation must be explained.

If A8/A32 fail to create >1 accessq entry:

STOP:

`MECHANISM_SENSITIVE_ACCESSQ_OPPORTUNITY_NOT_REALIZED`

Do not use them to judge V1/V2R1.

---

# Phase I — Native-aligned mechanism observable

Inspect the new benchmark SASS and identify its `clock64`/CS2R bracket PCs.

Do not reuse old M0–M3 PC constants unless they are actually identical.

Use/extend opt-in cross-cal diagnostics so the new bracket metric is:

`cycles per dependent warp-load step`

on measurement occurrence1 only.

Any new diagnostic implementation must pass OFF/ON neutrality on at least:

- A1 Legacy 10/80;
- A32 Legacy 10/80.

---

# Phase J — full mechanism-sensitive semantics matrix

Once Phase H/I pass, run:

`4 configs × 3 semantics × 2 VM latency configs = 24 points`

Semantics:

```text
LEGACY
V1_PIPELINED_LAUNCH
V2R1_READY_CONSUME_APPLY
```

VM configs:

```text
10/80
0/80
```

All runs use the frozen RTX4080 base config.

No platform or VM tuning after seeing results.

Use maximum safe parallelism with isolated outputs.

Every point requires:

- terminal;
- bracket identity;
- accessq opportunity identity;
- full translation coverage where emitted;
- duplicate application = 0 for V2R1;
- controller quiescence.

---

# Phase K — mechanism-sensitive analysis

For each semantic at 10/80 compute:

```text
A8/A1
A32/A1
A32_W8/A32
```

Compare with Native:

```text
1.0529595
1.2087227
1.0128866
```

Also compute 10/80→0/80 sensitivity for each config.

The main scientific question:

> Does V1 or V2R1 move the simulator's fanout/concurrency behavior toward Native relative behavior compared with Legacy when the exact multi-entry accessq opportunity is active?

Do NOT score by absolute cycle equality.

Do NOT tune parameters to improve the answer.

Allowed semantic classifications:

- `V1_EXTERNAL_SEMANTIC_SUPPORT`
- `V1_EXTERNAL_SEMANTIC_SUPPORT_PARTIAL`
- `V1_EXTERNAL_SEMANTIC_NOT_SUPPORTED`
- `V2R1_ADDS_EXTERNAL_ALIGNMENT_BENEFIT`
- `V2R1_ADDS_NO_EXTERNAL_ALIGNMENT_BENEFIT`
- `MECHANISM_SENSITIVE_ALIGNMENT_MIXED`

If V1 is supported/partial and V2R1 adds no necessary benefit, this may justify:

`V1_BASELINE_PROMOTION_CANDIDATE`

but do NOT automatically promote the project baseline in this Goal.

---

# Phase L — paper-oriented combined interpretation

Create one combined analysis separating:

## Platform

- qualification class;
- held-out errors;
- known scope.

## Control probes M0–M3

- base memory/translation behavior;
- mechanism inactive.

## Mechanism-sensitive probes A1/A8/A32/A32_W8

- actual multi-entry accessq behavior;
- Native relative behavior;
- Legacy/V1/V2R1 differences.

## Existing AI evidence

Reference accepted historical AI results only as simulator-internal causal evidence.

Do not reuse SM86 AI cycle values as RTX4080-platform external calibration evidence.

Do not rerun expensive T0/T1/T2 in this Goal.

---

# Phase M — publication

Report:

`docs/vm_tlb/codex_handoff/awma/RTX4080_PLATFORM_REQUAL_AND_MECHANISM_VALIDATION_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_RTX4080_PLATFORM_REQUAL_AND_MECHANISM_VALIDATION_V1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
FROZEN_PLATFORM_AUTHORITY.json
MATCHED_HELDOUT_AUTHORITY.tsv
HELDOUT_REQUALIFICATION.tsv
PLATFORM_REQUALIFICATION_DECISION.md
AWMA_VM_OVERLAY_SMOKE.tsv

CONTROL_TRACE_AUTHORITY.tsv
CONTROL_CONTEXT_PERSISTENCE.md
CONTROL_MATRIX.tsv
CONTROL_NATIVE_ALIGNED_OBSERVABLE.tsv
CONTROL_ANALYSIS.md

MECHANISM_TRACE_AUTHORITY.tsv
MECHANISM_ACCESSQ_CARDINALITY.tsv
MECHANISM_DIAGNOSTIC_CONTRACT.md
MECHANISM_DIAGNOSTIC.patch
MECHANISM_TELEMETRY_NEUTRALITY.tsv
MECHANISM_MATRIX.tsv
MECHANISM_NATIVE_ALIGNED_OBSERVABLE.tsv
MECHANISM_ANALYSIS.md

COMBINED_PAPER_EVIDENCE_ANALYSIS.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

If platform gate fails, only publish the platform-requalification subset and STOP; mechanism/control files must not be fake placeholders.

If platform passes, complete the whole pack.

---

# Phase N — publication close

```text
science closure
→ report/review pack
→ SHA256SUMS
→ commit/push
→ fetch-back
→ remote HEAD == local HEAD
→ remote tree verify
→ non-empty required files
→ sha256sum -c
→ clean worktree
→ STOP
```

No new TLB/PTW/cache mechanism design in this Goal.

No third platform tuning pass.

No parameter fitting to M0–M3 or A1/A8/A32/A32_W8.
