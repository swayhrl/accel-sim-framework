# SUPERSEDED — DO NOT EXECUTE

This Goal was superseded on 2026-09-23 by the decision to qualify an RTX4080/Ada Accel-Sim base platform before any further Native↔simulator contextual cross-calibration.

The preserved text below is historical planning only.

---

# CODEX 174 GOAL — Exact Contextual Native ↔ Simulator Cross-Calibration V1R2

Date: 2026-09-23

Mode:

`GOAL MODE / LONG-RUN / SOLVE-AND-CONTINUE`

Node:

`174-new`

Stage:

`AWMA_NATIVE_SIMULATOR_CONTEXTUAL_CROSSCAL_V1R2`

Read first, completely:

`docs/vm_tlb/chatgpt_handoff/awma/AWMA_CROSSCAL_V1R2_HANDOFF_CONTEXT_2026-09-23.md`

Then execute continuously.

---

# 1. Authorities

Native exact measured-trace authority:

`hrl/awma-crosscal-exact-measured-trace-v1r1 @ 149af0566cc6720621fdfe88d3cd3ca9b32cba67`

174 prep authority:

`hrl/awma-174-crosscal-v1r1-prep @ a04085f73458c9d30537640c2f7daad4a3aa3dd7`

Frozen Cross-Cal V1:

`hrl/awma-174-native-simulator-cross-calibration-v1 @ 6f9c1df1a03bd9d26130b80be1c31f5957074630`

V1 semantic authority:

`ad6f38878bc1e7c268b17e65fdb3793a3899a84d`

V2R1 semantic authority:

`dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`

Create fresh execution branch:

`hrl/awma-174-contextual-crosscal-v1r2`

Do not modify frozen authority branches.

---

# 2. Bind the new exact node164 trace-pair bundle

Use:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/crosscal_exact_v1r1_20260923T111500Z`

For each M0–M3:

- locate the exact warmup occurrence0 payload;
- locate the exact measurement occurrence1 payload;
- bind payload SHA256;
- bind same-process/context/run identity;
- bind full command:
  - seed=102;
  - steps=512;
  - samples=50;
  - warmup=2;
  - policy=default;
  - exact stride/locations/warps;
- verify zero drop/overflow;
- xz integrity;
- trace grammar;
- exact bracket counts.

Publish:

`EXACT_TRACE_PAIR_AUTHORITY.tsv`

Do not reuse the old warmup-only payload as measurement evidence.

---

# 3. Prove contextual replay semantics before science execution

The target replay sequence is:

```text
warmup occurrence0
→ measurement occurrence1
```

inside one simulator process/context.

Before running the matrix, inspect the trace-driven simulator kernel-boundary behavior.

Explicitly determine whether the following state persists from occurrence0 to occurrence1:

- L1D/L2 cache state;
- L1/L2 TLB state;
- page-walk cache state;
- VM object/provenance state;
- any translation structures that are architecturally expected to persist;
- global memory contents / allocation mapping.

Also determine what is intentionally drained/quiesced at kernel boundary.

Do not modify simulator semantics merely to force persistence.

If the accepted simulator naturally flushes any state that Native preserves, record that as:

`CONTEXT_STATE_MISMATCH_<STATE>`

and keep it in the final scope.

If the ordered pair cannot be replayed sequentially without changing simulator semantics, STOP:

`CONTEXTUAL_PAIR_REPLAY_NOT_SUPPORTED`

Do not fall back silently to isolated occurrence1 replay.

Publish:

`CONTEXT_PERSISTENCE_AUDIT.md`

---

# 4. Reuse existing opt-in diagnostics

Reuse the already-qualified:

`GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS=1`

for CS2R bracket timing.

Reuse the accepted opt-in accessq-cardinality diagnostic from V1R1 prep if needed.

Do not change V1/V2R1 semantics.

Any new telemetry added in this Goal must:

- be opt-in;
- default OFF;
- be observational-only;
- pass OFF/ON neutrality.

---

# 5. Measurement occurrence identity

For the new measurement occurrence1:

Expected complete bracket counts:

```text
M0 = 50
M1 = 50
M2 = 800
M3 = 50
```

The primary observable is still:

`CLOCK64_BRACKET_SIM_CYCLES_PER_DEPENDENT_STEP`

computed only from **measurement occurrence1**.

Warmup occurrence0 is used only to establish context.

If bracket counts do not match exactly, STOP:

`MEASURED_OCCURRENCE1_BRACKET_IDENTITY_FAIL`

---

# 6. Reconfirm mechanism inactivity on measurement occurrence

For M1 and M2 measured occurrence1, enable accessq-cardinality diagnostics.

Require:

- dependent LDG active-lane identity;
- min/mean/max accessq entries;
- histogram;
- fraction >1.

Expected from source structure:

`accessq_entries = 1`

for every active dependent LDG.

If this is confirmed, retain:

`M0_M3_MECHANISM_INACTIVE_CONTROL_SUITE`

If not, report the actual distribution and STOP for scientific review before using V1/V2R1 sentinels.

---

# 7. Platform scope — mandatory

The simulator uses:

`SM86_RTX3070`

while Native evidence is from RTX4080 / SM89.

Carry the label:

`PLATFORM_SCOPE=SM86_RTX3070_MODEL_VS_SM89_RTX4080_NATIVE`

through all analysis.

Perform a bounded repository/local search for any already-existing accepted:

- SM89 config;
- RTX4080 config;
- RTX4090/Ada config.

Do not create or tune a new config in this Goal.

Publish:

`PLATFORM_CONFIG_SCOPE.md`

If an existing qualified Ada config exists, record it for a future stage; do not switch the current matrix to it without review.

---

# 8. Science matrix — reduced, not 24-point repetition

Because M0–M3 are mechanism-inactive controls, do NOT repeat the full 3-semantics × 2-latency matrix.

Primary contextual control matrix:

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

Total primary points:

`8`

Additionally run four semantic sentinels at 10/80:

```text
M1 V1 10/80
M1 V2R1 10/80
M2 V1 10/80
M2 V2R1 10/80
```

Total Goal science points:

`12`

Use the same contextual warmup→measurement pair for every point.

All outputs isolated.

Use maximum safe parallelism.

---

# 9. Native exact contemporaneous reference

Use only the new Native V1R1 exact timing:

```text
M0 = 52.0
M1 = 294.0
M2 = 280.0
M3 = 152.5
```

M1→M2 Native:

`-4.7619047619%`

Recompute from published rows rather than hard-coding blindly.

Do not use historical -4.5840% as the primary exact reference.

---

# 10. Required analysis

For Legacy 10/80 contextual measurement occurrence1:

## A. Working-set amplification

Compute:

`M1 / M0`

Native reference:

`294 / 52`

Do not require absolute cycle equality.

## B. Exact concurrency change

Compute:

`(M2 - M1) / M1`

Native exact reference:

`(280 - 294)/294 = -4.7619%`

## C. M3 supporting behavior

Compare M3 against its exact Native contemporaneous reference.

Do not interpret 64KiB stride as hardware TLB page size.

## D. Model-relative 10/80→0/80 sensitivity

For M0–M3:

`(metric_10_80 - metric_0_80) / metric_10_80`

This is simulator-model-relative only.

## E. Semantic sentinel equality

Compare Legacy / V1 / V2R1 at M1 and M2 10/80.

If accessq cardinality remains one, equality is expected and is only a mechanism-inactive control result.

Do not convert that equality into a V1/V2R1 external-validation claim.

---

# 11. Allowed scientific interpretations

This Goal should primarily classify the underlying control/base-model alignment.

Allowed labels:

- `EXACT_CONTEXTUAL_CONTROL_ALIGNMENT_SUPPORTED`
- `EXACT_CONTEXTUAL_CONTROL_ALIGNMENT_PARTIAL`
- `EXACT_CONTEXTUAL_CONTROL_ALIGNMENT_NOT_SUPPORTED`
- `BASE_PLATFORM_CONCURRENCY_MISMATCH_CANDIDATE`
- `CONTEXT_STATE_MISMATCH_LIMITS_CALIBRATION`
- `MECHANISM_INACTIVE_SUITE_CONFIRMED`

Do not issue:

`BASELINE_PROMOTION_CANDIDATE`

from this Goal.

Do not redesign translation semantics.

If M1→M2 still has opposite sign or large disagreement after exact phase/seed/context repair, attribute the immediate discrepancy only to:

`BASE_PLATFORM_OR_ARCHITECTURE_MODEL_MISMATCH_CANDIDATE`

not specifically to TLB/PTW/frontend semantics.

---

# 12. Required review pack

Report:

`docs/vm_tlb/codex_handoff/awma/NATIVE_SIMULATOR_CONTEXTUAL_CROSSCAL_174NEW_V1R2_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CONTEXTUAL_CROSSCAL_V1R2/`

Required:

```text
README.md
SOURCE_ANCHORS.md
EXACT_TRACE_PAIR_AUTHORITY.tsv
CONTEXT_PERSISTENCE_AUDIT.md
PLATFORM_CONFIG_SCOPE.md
MEASUREMENT_BRACKET_IDENTITY.tsv
MEASUREMENT_ACCESSQ_CARDINALITY.tsv
MATRIX_CONFIG_AUTHORITY.tsv
CONTEXTUAL_MATRIX.tsv
NATIVE_REFERENCE_MATRIX.tsv
NATIVE_ALIGNED_OBSERVABLE.tsv
SEMANTIC_SENTINELS.tsv
CROSSCAL_V1R2_ANALYSIS.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

No zero-byte placeholders.

Publication contract:

report/review pack
→ SHA256SUMS
→ commit/push
→ fetch-back
→ remote HEAD/tree verify
→ non-empty files
→ sha256sum -c
→ clean worktree
→ STOP.

No new TLB/PTW/cache mechanism in this Goal.
