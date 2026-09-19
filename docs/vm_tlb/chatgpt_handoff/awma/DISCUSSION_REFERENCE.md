# AWMA Discussion Reference — Post-Repair Requalification + 20h Pipeline

Date: 2026-09-19

## 1. Why the project state changed

The global-access-determinism stage had already shown that Q05 generation-time GLOBAL access creation was stable while
legacy VM READY coverage was not. The dedicated repair qualification now directly proves that legacy downstream admission
allowed VM-eligible accesses to bypass the modeled translation gate.

Accepted repair evidence:

```text
legacy P34:
downstream admissions = 3,090,304
translated            =   776,666
untranslated          = 2,313,638
unobserved            = 2,313,638

repaired P34:
downstream admissions = 3,090,304
translated            = 3,090,304
untranslated          = 0
unobserved            = 0
post-ready retranslation = 0
```

Target completion cycles changed:

`871835 -> 1619068`

with unchanged completed instruction count.

Therefore old translation-dependent timing conclusions cannot be used as the baseline for mechanism design.

## 2. What the repair does and does not mean

The repair requires the exact current `accessq_back()` to have accepted VM translation before L1D/ICNT admission.

If untranslated:
- it stays queued;
- existing COAL_STALL semantics apply;
- the next normal memory-cycle invocation uses the existing VM translation helper.

This restores the modeled VM gate. It is not a new architecture mechanism.

The performance change caused by restoring the gate is expected and must not be described as a new stall mechanism
invented by the repair.

## 3. Why one more telemetry-scoping step is mandatory

The repair proof counters are target-kernel gated, but not every auxiliary simulator statistic is.

The compact repair impact matrix reports `walk_starts=499`, while historical contextual analysis used a different
P34 target-only walk count.

This strongly indicates different accumulation scopes (for example full prefix versus target delta), but the next stage
must prove that directly.

Hence:
- the coverage defect/repair decision is accepted;
- auxiliary translation-count interpretation is not accepted until target-boundary deltas close;
- old and new telemetry must be compared only at the same scope.

## 4. Requalification philosophy

Do not rerun the whole historical matrix.

The minimum repaired question is:

> Under correct per-access VM coverage, how much target translation sensitivity remains in isolated and contextual Q05?

Use:
- same-source formal isolated R0/I0;
- P34 repaired natural R0;
- P34 repaired Q05-only I0;
- P8 repaired natural R0;
- target-scoped translation/timeline sanity.

P34 Q05-only I0 must keep all predecessor kernels on repaired natural R0.

The old P1/P2/P4/P16 matrix and old mechanism-like diagnostics are not automatically replayed.

## 5. Claim boundaries after repair

Still valid unless separately contradicted:
- producer/raw trace identity;
- Q05 semantic identity;
- contiguous prefix identity;
- native kernel census;
- native page/line structural evidence;
- 109 V1/V2.1 capture integrity;
- lookup-latency provenance: 10/80 are generic simulator assumptions, not RTX4080 facts;
- generation-time GLOBAL determinism.

Pending requalification:
- isolated R0/I0 quantitative sensitivity;
- contextual R0/I0 quantitative sensitivity;
- P8/P34 translation timing interpretation;
- translation timeline/retry quantitative interpretation;
- lookup-latency quantitative sensitivity;
- any translation opportunity magnitude.

Retired as a scientific count source:
- legacy VM-boundary stream telemetry that was already shown to be an artifact.

## 6. Why 109 now studies workload questions in parallel

The repaired simulator baseline must be requalified, but 109 can still produce native evidence that does not depend on the
legacy VM timing path.

The literature audit supports three research-design questions:

### E2
Execution-history sensitivity.
This maps to the repaired Q05 mainline and stays primarily on 174.

### E1
Shape x low-bit implementation.
This maps to Qwen2.5-7B raw/AWQ on 109.

### E3
Natural vs controlled MoE routing.
This is conditional and maps first to Qwen3-30B-A3B exact state/replay.

The point is not to add models for coverage.
The point is to build controlled contrasts that separate competing explanations.

## 7. 109 E1 interpretation

Core matrix:

`{down_proj,q_proj} x {M1,M256} x {raw,AWQ}`

M is GEMM token-row count, not automatically Prefill/Decode identity.

Required distinctions:
- raw/AWQ semantic comparability;
- actual dtype differences;
- dequantization/layout/kernel-path differences;
- uninstrumented timing versus NCU resource diagnosis.

No-effect is a valid result.

## 8. 109 E3 interpretation

The first useful routing comparison is not arbitrary uniform-versus-natural over all experts.

Use:
- N natural;
- P histogram-preserving permutation;
- U-active balancing within the naturally active expert set.

This separates token ordering and load distribution while avoiding an unnecessary active-working-set change in the first
diagnostic.

Synthetic routing must remain labeled synthetic.

## 9. Opportunity work

After mandatory work, remaining time may be used for:
- long-context then batch extension of current Qwen0.5B;
- same-quantized-weight execution decomposition;
- NCU protocol sensitivity;
- Llama raw shape holdout;
- on 174, cross-family evidence synthesis and at most one non-Attention repaired R0/I0 isolated screen.

These are bounded opportunities, not a requirement to keep hardware busy at all costs.

## 10. Literature-method lessons carried into this stage

The literature audit established several rules now adopted as project policy:
- real GPU, local detailed simulation, and whole-system estimation may legitimately coexist if evidence levels are explicit;
- model names alone do not define a controlled experiment;
- proxy inputs and natural execution must be labeled separately;
- representative kernels require validation by target metric;
- state checkpoints do not imply restored microarchitectural state;
- profiler replay/cache policy is part of measurement semantics.

## 11. Still forbidden

No architecture mechanism until repaired VM correctness and minimum baseline requalification close.

Do not start:
- TLB capacity/port mechanisms;
- PTW/PWC mechanisms;
- segmentation/page-size mechanisms;
- translation prefetch/speculation;
- cache redesign;
- broad simulator sweep.

The 20h campaign is characterization/requalification, not mechanism design.
