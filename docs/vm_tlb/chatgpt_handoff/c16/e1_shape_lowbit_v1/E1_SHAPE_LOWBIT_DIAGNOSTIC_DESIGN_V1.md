# C16 E1 — Shape × Low-Bit Implementation Diagnostic V1

## 1. Scientific question

The next C16 mainline question is:

> **For the same semantic linear operators, how much of the observed GPU execution/memory behavior is determined by tensor shape, and how much changes because the deployed low-bit implementation takes a different kernel path?**

This is deliberately narrower than “does quantization help?”

The current evidence does **not** support a pure quantization-causal claim, because RAW and AWQ are different deployment implementations and may also differ in activation/output dtype and kernel selection.

The first goal is therefore to characterize the interaction:

`semantic operator × M shape × deployed implementation`

and then determine whether a deeper memory study is justified.

---

# 2. Existing evidence — do not rerun by default

## 2.1 Qwen2.5-7B RAW/AWQ matched semantic-module closure

Accepted C16 pair closure:

`hrl/c16-qwen25-7b-pair-closure-109-v10@57ca798c851a3b9d4a2c787c01f4e2b3a16fcdea`

Accepted scope:

`MATCHED_SEMANTIC_MODULE_REPLAY_DEPLOYMENT_COMPARISON`

Important claim boundary already frozen:

- this is a **deployment-level matched semantic-module comparison**;
- RAW vs AWQ is not automatically a pure quantization causal comparison;
- natural deployment states may diverge;
- any causal wording must be supported by a separate controlled bridge.

The V10 pair gate closes:
- same token authority;
- layer 0;
- semantic role `mlp.down_proj`;
- replay/signature/coverage/ACK on both sides;
- compatible NCU units.

Historical static audit:
- AWQ direct MREF paths: 43
- RAW direct MREF paths: 243

This already shows the implementation paths are structurally different.

## 2.2 Existing eight-point shape matrix

An existing accepted experimental asset already executed the originally planned core matrix:

`hrl/awma-e1-shape-oracle-moe-harness-109-v2@56096d32bd5cd783286e1b5e5e612b6019f926d0`

Core points:

- semantic role ∈ {`q_proj`, `down_proj`}
- M ∈ {1, 256}
- implementation ∈ {RAW, AWQ}

Do **not** rerun these eight points unless their exact source/runtime/activation authority cannot be re-audited.

Existing native medians:

| role | M | RAW median ms | AWQ median ms |
|---|---:|---:|---:|
| q_proj | 1 | 0.023456 | 0.035680 |
| q_proj | 256 | 0.096480 | 0.132096 |
| down_proj | 1 | 0.214016 | 0.060992 |
| down_proj | 256 | 0.378880 | 0.472064 |

This is already a strong **shape × operator × implementation interaction**:

- AWQ is slower for q_proj at both M values;
- AWQ is much faster for down_proj at M=1;
- AWQ becomes slower for down_proj at M=256.

Do not collapse these into one “AWQ faster/slower” number.

Existing AWQ runtime path receipt:

- M1: `GEMM_QUANTIZED`
- M256: `GEMM_QUANTIZED`
- M2048: `DEQUANTIZE_PLUS_TORCH_MATMUL`

Thus shape can change the AWQ implementation path itself.

The first C16 E1 task is to **qualify and extend** this evidence, not repeat it.

---

# 3. Primary hypotheses

## H1 — shape/implementation interaction exists

The effect of AWQ relative to RAW is not a constant multiplicative factor; it changes with operator role and M.

Existing eight-point evidence already supports this descriptively.

## H2 — dtype alone does not explain the interaction

RAW historical points are BF16, while the AWQ path must be re-audited for actual input/output dtype.

A controlled RAW-FP16 bridge is needed before attributing the interaction to low-bit implementation rather than a BF16/FP16 deployment difference.

This bridge is **not** expected to make RAW and AWQ causally identical. It only quantifies dtype sensitivity.

## H3 — the interaction should survive an operator holdout if it is not specific to q_proj/down_proj only

Use `up_proj` as the operator holdout.

## H4 — input content should not materially change the implementation-level conclusion at a fixed semantic operator/shape

Use a CODE input holdout only if an exact paired input authority is already available or can be constructed without opening a new large capture campaign.

---

# 4. Stage 0 — authority re-audit, CPU-first

Before new GPU work, re-audit:

1. C16 V10 RAW/AWQ pair closure and its frozen claim boundary.
2. AWMA E1 V2 exact source/runtime/shape-specific activation authorities.
3. The eight existing timing points and their raw samples.
4. AWQ runtime source contract:
   - `gemm.py` SHA
   - `awq_ext` SHA
   - WQLinear path threshold.
5. Actual dtype at the input/output of every existing AWQ point.

Create a C16 review receipt that clearly states which existing points are reused as accepted upstream evidence.

If the eight points are fully auditable, do not rerun them.

---

# 5. Stage 1 — minimal RAW-FP16 dtype bridge

Run only four new points:

- `q_proj × M1 × RAW_FP16`
- `q_proj × M256 × RAW_FP16`
- `down_proj × M1 × RAW_FP16`
- `down_proj × M256 × RAW_FP16`

## Definition

For each point:

- use the same semantic module as the RAW baseline;
- use the same shape-specific activation values as the RAW authority, cast to FP16;
- use the same dense RAW weights, cast once to FP16;
- preserve layout/stride where possible;
- do not quantize the weights;
- execute the ordinary dense linear operation/backend appropriate to that module;
- validate against a direct FP16 module/function oracle with the same FP16 input and weights.

This is labeled:

`RAW_FP16_DTYPE_BRIDGE`

It is not a new deployment model.

## Timing protocol

Use:
- 2 warmups
- 5 measured iterations
- preserve all raw samples
- report median/min/max/CV

Use the same timing boundary as the existing eight-point matrix.

Also record:
- input dtype
- weight dtype
- output dtype
- input/output shape/stride
- actual runtime/kernel path identity at a lightweight level
- whether the backend changed relative to RAW_BF16

No NCU/NVBit/full trace in this stage.

---

# 6. Stage 2 — interaction analysis

Construct a unified table with:

- RAW_BF16
- RAW_FP16
- AWQ

for q_proj/down_proj × M1/M256.

Report for every point:
- median time
- CV
- relative ratio to RAW_BF16
- relative ratio to RAW_FP16 where meaningful
- path identity
- input/weight/output dtype

Required derived comparisons:

1. `RAW_FP16 / RAW_BF16`
   - estimates dtype/backend sensitivity of the dense path.

2. `AWQ / RAW_BF16`
   - deployment-level observed difference.

3. `AWQ / RAW_FP16`
   - only interpret as a closer deployment comparison if activation/output dtype and timing boundary are compatible.
   - otherwise label `NOT_FULLY_MATCHED`.

Do not use the bridge to claim “the remaining difference is caused only by quantization”.

---

# 7. Stage 3 — operator holdout: up_proj

If Stage 1 closes cleanly, run a minimal holdout:

- `up_proj × M1 × RAW`
- `up_proj × M1 × AWQ`
- `up_proj × M256 × RAW`
- `up_proj × M256 × AWQ`

Use the same Qwen2.5-7B layer/module family and shape-specific direct oracle policy.

No RAW_FP16 up_proj points are required in the first holdout.

Purpose:

> Test whether the observed shape × implementation interaction generalizes to another MLP projection role.

If `up_proj` cannot be bound to the same deployment/runtime contract without material engineering expansion, record `HOLDOUT_NOT_QUALIFIED` rather than opening a new campaign.

---

# 8. Stage 4 — input-content holdout: CODE

This is a validation-only stage.

Preferred representative point:

`down_proj × M1 × {RAW, AWQ}`

because the existing core matrix shows the largest sign/magnitude difference there.

Use a CODE activation only if:
- an exact paired semantic-module input authority is already available; or
- it can be obtained with a small, direct state replay under the same model/runtime without introducing a new capture problem.

Do not use unmatched RAW/AWQ natural states as if they were a causal CODE holdout.

If exact paired CODE authority is unavailable, record:

`CODE_HOLDOUT_NOT_RUN_NO_MATCHED_AUTHORITY`

and do not block the main E1 conclusion.

---

# 9. What this Goal does NOT do

Do not run by default:
- NVBit
- NCU deep profiling
- NSYS
- full address trace
- new model download
- Llama validation
- mechanism design

The existing V10 NCU evidence may be cited as historical deployment evidence, but not used to fill missing new measurements.

No claim of:
- low-bit universally faster/slower;
- pure quantization causality;
- cache/TLB causality;
- end-to-end model speedup.

---

# 10. Decision rule for a later deep memory stage

After RAW-FP16 bridge + up_proj holdout:

## Continue to a minimal deep diagnostic only if

all of the following are true:

1. the shape × implementation interaction remains materially visible after accounting for dense-path dtype sensitivity;
2. the interaction is not confined to one obviously pathological single point;
3. at least one holdout supports the same qualitative conclusion;
4. the runtime path identity suggests a plausible memory-organization difference worth measuring.

Then propose, but do not automatically execute, a minimal deep set selected by a deterministic rule:

- one point where AWQ is materially faster;
- one point at a different M for the same role where AWQ is materially slower/neutral;
- optionally one operator holdout point.

The first deep tool should normally be lightweight NCU traffic/kernel evidence before full address trace.

## Stop if

- RAW-FP16 explains most of the apparent difference;
- the interaction disappears under controlled dtype;
- holdout does not reproduce;
- differences are small relative to timing variability;
- path differences are purely implementation details with no clear memory research question.

A negative result is valid.

---

# 11. Required review pack

Suggested path:

`docs/vm_tlb/review_packs/C16_E1_QWEN25_SHAPE_LOWBIT_109_V1/`

At minimum:

- `UPSTREAM_C16_PAIR_AUTHORITY.json`
- `UPSTREAM_EIGHT_POINT_AUTHORITY.json`
- `EIGHT_POINT_REAUDIT.json`
- `DTYPE_AUDIT.json`
- `RAW_FP16_BRIDGE.tsv`
- `CORE_12_POINT_COMPARISON.tsv`
- `INTERACTION_ANALYSIS.json`
- `UP_PROJ_HOLDOUT.tsv`
- `CODE_HOLDOUT.json`
- `RUNTIME_PATH_RELATION.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Create/update a dedicated scientific log:

`docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

with:
- Question
- Evidence
- Result
- Interpretation
- Superseded
- Next question
- Stop condition

---

# 12. Efficiency rule

This stage must reuse prior accepted evidence aggressively.

Do not:
- rerun the eight existing core points if their authority closes;
- rebuild environments already hash-closed;
- re-profile unchanged historical points just to make a new table;
- create formal admission machinery for lightweight timing-only bridge points.

New GPU work should be limited to the four RAW-FP16 bridge points plus the small holdouts defined above.

---

# 13. Stop boundary

Stop after:
- authority re-audit;
- RAW-FP16 bridge;
- up_proj holdout or explicit not-qualified result;
- CODE holdout or explicit not-run result;
- unified analysis;
- scientific-log update;
- Git closure.

Do not automatically start a deep memory capture.
