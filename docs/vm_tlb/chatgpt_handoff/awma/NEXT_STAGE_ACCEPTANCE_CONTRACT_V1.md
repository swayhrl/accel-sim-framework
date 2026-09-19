# AWMA Next-Stage Acceptance Contract V1

Date: 2026-09-19

Stage:
`AWMA_REPAIRED_HIT_PATH_AND_E1_AUTHORITY_V1`

## 1. Shared principles

A scientific result is accepted only with exact identity, runtime/source authority, input authority, and scoped measurement semantics.

Routine engineering failures are solve-and-continue.

A task-local scientific failure freezes only that task. Independent tasks continue.

No task may:
- invent missing activations;
- substitute a different model/revision;
- flatten/change tensor rank without authorization;
- weaken replay equivalence;
- treat generic lookup latency as RTX4080 calibration;
- promote a synthetic routing input as natural execution.

## 2. 174 repaired baseline status

Accepted for model-relative characterization:

`a7110f789a2bc6761d8885a2ca5628b4acf50f69`

Correctness repair authority:

`3f7bc0cd3cb3667b38fa0dd803ac034e19b493d6`

All new simulator runs must preserve:
- per-access downstream translation gate;
- zero untranslated/unobserved downstream admissions;
- zero post-ready retranslation attempts;
- same Q05 trace/context identity;
- same F0 architecture except the explicitly varied lookup-latency diagnostic parameter.

## 3. 174 provenance closeout

Pass without rerun if Codex can bind:

- exact applied repaired source patch;
- exact build/runtime authority;
- exact simulator binary SHA256 used for accepted M1 runs or a durable receipt proving it;
- missing final report;
- missing runtime-authority manifest;
- node164 receipt/hashes.

If exact old binary cannot be recovered, rebuild the exact accepted source semantics.

A rebuilt binary is not silently declared bit-identical.
Run one P34 10/80 sanity only if necessary to show the rebuilt runtime reproduces:
- 1,619,068 target cycles within exact deterministic expectation;
- 3,090,304/3,090,304 translated admissions;
- zero untranslated/unobserved.

Any mismatch is STOP_SCIENTIFIC.

## 4. 174 hit-path model-validity matrix

Reuse:
- P34 repaired 10/80 = 1,619,068 cycles;
- P34 repaired Q05-only I0 = 758,082 cycles.

Run target-only overrides with all predecessors on repaired natural 10/80:

- 5/80
- 2/80
- 0/80
- 10/40
- 10/0
- 0/0

Do not globally alter prefix lookup latencies.

For every point collect:
- full Q05 cycles;
- translated admission invariant;
- target-delta L1/L2 lookup launches/hits/misses;
- MSHR alloc/merge;
- walks;
- PWC/PTE;
- requester latency components;
- L2/DRAM target deltas.

Changing lookup latency may change hit/miss/order behavior.
Do not treat results as additive latency subtraction.

## 5. 174 derived metrics

Report, without silently converting them into hardware speedup claims:

- `TOTAL_I0_GAP = cycles(10/80) - cycles(I0)`
- `L1_ENVELOPE = cycles(10/80) - cycles(0/80)`
- `L2_NATURAL_L1_EFFECT = cycles(10/80) - cycles(10/0)`
- `ZERO_LOOKUP_RESIDUAL = cycles(0/0) - cycles(I0)`
- normalized fractions relative to TOTAL_I0_GAP.

Also report monotonicity/non-monotonicity across 10/80 -> 5/80 -> 2/80 -> 0/80 and 10/80 -> 10/40 -> 10/0.

No categorical architecture conclusion is required.
The next scientific review consumes the continuous envelope.

## 6. 174 source-semantics audit

Produce a source-local explanation of:

- when an L1 lookup is launched;
- whether lookup service is pipelined/overlapped;
- port acceptance semantics;
- what stalls an access while lookup is pending;
- how L1 hits are delivered;
- why per-access translated coverage creates ~3.09M L1 lookup launches;
- how the target-only latency override changes service timing without changing capacity/ports.

This audit is model semantics, not hardware validation.

## 7. 174 optional non-Attention screen

Only after hit-path matrix closure.

Preferred target:
`PREFILL_GEMM_PRIMARY_OCC0`

Use exact accepted producer authority from:
`8f49ba3b9228b5f8a9163e961225ffd415107734`

No recapture.

If consumer admission qualifies, run at most:
- repaired 10/80;
- repaired 0/80.

Optional I0 only if needed to interpret a substantial residual and remaining budget is explicitly safe.

If no matched predecessor context exists:
`ISOLATED_SCREEN_ONLY`.

## 8. 109 E1 authority producer

Use common accepted token authority:

`0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`

Note: Codex must verify this value against the historical pair-input receipt before use; if the receipt value differs, use the receipt and record the correction rather than guessing.

Authoritative historical reference:
`e1d210d662ece6975648d04f628eb3f9e938117f`

Required model revisions:

raw:
`a09a35458c702b33eeacc393d103063234e8bc28`

AWQ:
`b25037543e9394b818fdfca67ab2a00ecc7dd641`

Required module roles:
- layer 0 self_attn.q_proj
- layer 0 mlp.down_proj

Use exact module path/object binding.
Do not infer semantic identity from CUDA launch order.

## 9. Activation authority contents

For each raw/AWQ module role, produce a live authority bundle containing:

- token file/path + SHA;
- model/revision;
- runtime/source versions;
- module path/class;
- weight identity;
- input tensor rank/shape/stride/dtype;
- selected activation-pool tensor bytes + SHA;
- live output bytes + SHA;
- row-selection rule;
- module-replay output + SHA;
- exact replay equality result.

Core row-selection rule must be frozen before timing:

- pool = first 256 consecutive token rows from the accepted S2 live module input;
- M256 = `[1,256,K]`;
- M1 = first row of the same pool, `[1,1,K]`.

If the actual live input does not contain at least 256 rows, STOP that module role.

Do not flatten rank.

## 10. Replay equivalence

Fresh replay must execute the exact module implementation against saved activation authority.

Preferred acceptance:
`BITWISE_EQUAL`.

If not bitwise equal:
- record max abs/relative difference;
- do not automatically relax tolerance;
- mark `REPLAY_EQUIVALENCE_FAIL`;
- freeze that module role unless an already accepted runtime-specific numerical tolerance contract exists.

## 11. E1 core measurements

Once authority passes:

For each role and implementation measure:
- M1
- M256

This gives 8 deployment points.

Each point:
- 2 warmups;
- 5 uninstrumented CUDA-event measurements;
- retain every sample;
- median + dispersion;
- exact kernel/semantic-region fingerprint.

AWQ multi-kernel execution is measured as the complete semantic module region.

## 12. E1 semantic classification

Natural-deployment comparisons are always allowed after authority closure.

Cross raw/AWQ same-input semantic comparison is allowed only if the input mapping/scaling relation is proven and validated.

Status per pair:
- `SEMANTIC_PAIR_QUALIFIED`
- `IMPLEMENTATION_LEVEL_ONLY`

No forced semantic pair.

## 13. E1 dtype/backend diagnosis

Record:
- module input dtype;
- actual implementation/kernel path;
- rank-dependent path choice;
- dequantization kernels;
- GEMM path;
- output dtype.

If raw/AWQ execution dtypes differ, bridge points are conditional and must use a separately named experimental identity.

## 14. E1 profiling

Do not repeat whole-application exact selectors that previously matched zero kernels.

Preferred:
- isolated module-replay process containing only the target semantic call;
- NVTX range around the semantic region where supported;
- selector canary proving at least one expected kernel before collecting the metric set.

Profile only points needed to distinguish:
- traffic reduction;
- utilization/shape effect;
- implementation/dequantization overhead.

Counter absence after a successful selector is `COUNTER_UNAVAILABLE`.
Zero selected kernels is `SELECTOR_UNRESOLVED`, not counter absence.

## 15. E3 independence

E3 does not depend on E1 success.

Authority:
`ee67225edc8fc5868de585d38e0391cbeb755d9f`

Use Q30 S2 T2048 exact state/replay.

First-wave cases:
- N natural routing;
- P histogram-preserving joint permutation;
- U-active balancing within naturally active expert set.

Hold:
- M=2048;
- E/k;
- total assignments;
- expert backend/weight residency;
- exact input state;
- timing boundary.

P requires inverse-permutation output equivalence.
U-active must be labeled `SYNTHETIC_ROUTING`.

No formal detailed trace is required.

## 16. 109 task scheduling

Scientific DAG:

- A0 authority audit/producer -> E1 core;
- E3 independently READY once Q30 authority verifies;
- profiling followups depend on their own selector canary.

GPU execution is physically serial under the existing lock, but E1 STOP must not propagate to E3.

## 17. No new architecture mechanism

This stage does not authorize:
- TLB capacity/port redesign;
- PTW/PWC mechanism;
- page-size/segmentation;
- prefetch/speculation;
- cache mechanism.

174 lookup-latency variants are model-validity diagnostics only.
