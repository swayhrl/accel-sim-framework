# Goal 174-new — AI GPU Resource/Bottleneck Characterization V1

Stage:
`AWMA_AI_GPU_RESOURCE_BOTTLENECK_CHARACTERIZATION_V1`

Execution branch:
`hrl/awma-ai-gpu-resource-bottleneck-characterization-v1`

Node:
174-new

## 0. Goal

Use the existing qualified simulator-native assets and Bottleneck Observatory to
answer a broader architecture question:

> Across representative AI kernel families, which modeled GPU resource/service
> is limiting performance, how does the limiting domain shift with kernel
> family and execution scale, and where does bounded resource scaling saturate?

This is characterization first.
Do not begin with a proposed mechanism.

## 1. Authorities

Use accepted:
- RTX4080/Ada Accel-Sim platform qualification;
- WARP_VPN_DEDUP_REFERENCE where translation is enabled;
- Bottleneck Observatory V1:
  `b85d388abe98e5da70b749b52075c33fad7cede4`;
- path-model result:
  `a3756e1f3896c2ab292e2576c6271849c22eaf61`;
- Native residual result:
  `3e29f234a971e2be68076eef22a05391cf9e4b67`.

Do not change accepted traces or baseline semantics.

## 2. Pre-register target suite before new scaling results

Use only already-qualified traces.

Target suite:

1. T0 — Qwen prefill Flash
2. T1 — Qwen prefill GEMM
3. T2 — Qwen decode GEMV
4. SPLITKV — Qwen decode attention split
5. L2 — Llama decode attention-like, deterministic grammar-qualified authority
6. L1 — Llama decode GEMV scale-8
7. M1 — OLMoE decode GEMV scale-1
8. M2 — OLMoE reduction, LOW_DEMAND_CONTROL

M2 is control-only by default and should not receive a large scaling matrix.

Freeze:
`TARGET_SUITE_PREREG.tsv`

For every target include:
- family
- model/scenario
- evidence role
- Native time share if legitimately available in its own scenario
- cross-model runtime comparability = NO.

Do not form one arithmetic average across these scenarios.

## 3. Resource-knob source audit

Before changing any simulator parameter, build:
`RESOURCE_DIAGNOSTIC_REGISTRY.tsv`

Audit source/config semantics for the following domains.

### D0 Scheduler/front-end
Possible observable quantities:
- no-active/no-eligible/dependency/structural/idle
- issue/eligible pressure
Only add an intervention if the simulator provides a clean finite
scheduler/issue-capacity knob whose semantics can be isolated.
Otherwise mark `OBSERVABLE_ONLY`.

### D1 Execution resources
Audit relevant configurable FU counts/throughput for:
- SP/INT
- tensor/GEMM path
- SFU
- load/store execution path where modeled.

Do not invent a per-FU classification the current simulator cannot support.

### D2 L1D
Separate:
- capacity/associativity,
- latency,
- bank/port/reservation service.
Do not call a capacity change a bandwidth change.

### D3 L2
Separate:
- capacity,
- bank/service throughput,
- latency.

### D4 ICNT
Audit a clean service/bandwidth knob if present.
Do not change topology and call it only "bandwidth" unless source semantics
support that statement.

### D5 DRAM
Audit a clean bandwidth/service intervention such as bus width or equivalent
source-supported knob.
Record whether timing/queue law also changes.

### D6 Translation
Do not rediscover a new translation mechanism.
Use the already accepted sequential-vs-B1 path result as the translation-domain
diagnostic where applicable.
Do not rerun if accepted result exists.

Every registry entry must state:
- exact config/source location;
- what physical/model quantity changes;
- what else changes;
- whether architectural work/instructions remain constant;
- validity: `ELIGIBLE_DIAGNOSTIC`, `OBSERVABLE_ONLY`, or `REJECTED_CONFOUNDED`.

## 4. Baseline Observatory matrix

Run or reuse Observatory Level 1 for all non-control targets.

For M2, use existing basic counters unless Level 1 is cheap and useful.

Record at least:
- cycles/instructions/CTA;
- scheduler stall classes;
- execution structural indicators available;
- LDST stall taxonomy;
- L1D reservation failures;
- L2/ICNT/DRAM queue/service;
- translation path service;
- progress/tail indicators.

Output:
`BASELINE_BOTTLENECK_MATRIX.tsv`

No ROOT_CAUSE label.
Classify each signal as:
- LOCATION
- MEDIATOR
- NOT_SUPPORTED
- UNRESOLVED.

## 5. Pre-register domain selection

Before running resource changes, choose at most TWO eligible domains per
non-control target.

Selection order:
1. direct Level-1 symptom at a finite resource/service;
2. family-appropriate execution path;
3. an existing accepted causal result.

Do not choose based on expected speedup.

Freeze:
`TARGET_DOMAIN_PREREG.tsv`

Where the same exact function is available at multiple scales (L1/M1 and
T2/A1/A2 historical data), explicitly include scale-comparison reasoning.

## 6. Fixed two-point resource scaling

For each selected target/domain, run exactly one bounded `2X` intervention
from the registry.

Examples only if source-audited:
- 2x relevant execution service units;
- 2x L1D capacity or bank/service resource;
- 2x L2 capacity/service resource;
- 2x ICNT service/bandwidth;
- 2x DRAM bandwidth/service.

Do NOT tune intermediate values.
Do NOT change more than one scientific resource dimension in one run.

For each run record:
- exact knob;
- cycles and cycle response;
- instruction/CTA conservation;
- Observatory Level1;
- target resource occupancy/stall/service;
- secondary pressure moved elsewhere.

Output:
`RESOURCE_2X_MATRIX.tsv`.

## 7. One upper-bound diagnostic per target

After all 2X results are known, select exactly ONE target/domain pair per
non-control target for a generous source-supported upper-bound diagnostic.

Selection rule:
- the domain with the largest causal cycle response among that target's
  preregistered 2X domains;
- tie-break by the stronger baseline bottleneck signal.

This is a deterministic post-2X rule, not manual cherry-picking.

The upper bound may be:
- a large-but-finite capacity,
- near-zero modeled latency,
- generous service width,
- or existing idealized diagnostic,
only if its semantics are cleanly documented.

Do not combine multiple ideal resources.

Output:
`RESOURCE_UPPER_BOUND_MATRIX.tsv`.

## 8. Resource-saturation interpretation

For each target/domain report:
- baseline -> 2X response;
- 2X -> upper-bound incremental response;
- whether pressure migrates to another domain;
- whether increasing the resource shows diminishing returns.

Do not impose an arbitrary "saturated at X%" gate.
Report raw values and classify descriptively:

- `LOW_RESPONSE`
- `FINITE_RESOURCE_SENSITIVE`
- `DIMINISHING_RETURN_OBSERVED`
- `BOTTLENECK_MIGRATION_OBSERVED`
- `INTERVENTION_NON_MONOTONIC`
- `UNRESOLVED`

Output:
`RESOURCE_SATURATION_MAP.tsv`.

## 9. Family and scale analysis

Build:
`AI_FAMILY_RESOURCE_MAP.md`

At minimum compare:
- prefill GEMM vs prefill Flash;
- decode GEMV vs attention;
- same-function Llama L1 vs OLMoE M1 8x scale pair;
- Qwen GEMV historical context sensitivity where accepted;
- M2 as low-demand control only.

Do not call model-family differences when the exact function and per-CTA
behavior are identical.

Questions:
- Which resource limitation is stable within a family?
- Which limitation shifts with scale/context?
- Which resource additions merely move the bottleneck?
- Are any AI families limited by a resource balance rather than one absolute
  capacity?

## 10. Closest-work / novelty gate

Only after the resource map is complete, identify at most TWO architecture
problem candidates.

A candidate problem must have:
1. repeated evidence across at least two independent targets/contexts OR one
   strong target plus an exact matched scale/context contrast;
2. a finite, localized resource interaction;
3. a nontrivial limitation of simply doubling one resource;
4. an online/source-available signal for a future mechanism;
5. closest-work differentiation.

Screen relevant work, including where applicable:
- GPU warp scheduling / resource-aware scheduling;
- Memento / register-resource policies;
- cache/bandwidth management;
- GPU memory scheduling;
- existing AI-specific GPU architecture work.

Do not rename a known generic "pressure-aware scheduler" as novelty.

Produce:
`ARCH_PROBLEM_CARD_1.md`
`ARCH_PROBLEM_CARD_2.md`
only if gates pass.

## 11. Optional ONE micro-prototype

Only if one problem card passes all gates and a small, bounded prototype can be
implemented without changing multiple domains at once.

Before running:
- preregister max 3 development targets;
- freeze policy/resources;
- specify one falsifying criterion.

Run at most:
- 3 candidate;
- 3 matched controls.

No parameter sweep and no V2/V3 repair loop.

If no candidate passes novelty gate, candidate runs = 0.

## 12. Run budget

Baseline Level1: reuse whenever possible.
New full simulations:
- at most 2 resource-2X runs × 7 non-control targets = 14;
- at most 1 upper-bound run × 7 = 7;
- optional prototype/control <= 6.

Do not fill the budget mechanically.
Skip a domain when source audit marks it ineligible.

## 13. Deliverables

At minimum:
- README.md
- TARGET_SUITE_PREREG.tsv
- RESOURCE_DIAGNOSTIC_REGISTRY.tsv
- BASELINE_BOTTLENECK_MATRIX.tsv
- TARGET_DOMAIN_PREREG.tsv
- RESOURCE_2X_MATRIX.tsv
- RESOURCE_UPPER_BOUND_MATRIX.tsv
- RESOURCE_SATURATION_MAP.tsv
- AI_FAMILY_RESOURCE_MAP.md
- CROSS_SCALE_ANALYSIS.md
- CLOSEST_WORK_SCREEN.md
- ARCH_PROBLEM_CARD_1.md / 2 if any
- PROTOTYPE_DECISION.md
- if prototype: candidate/control/correctness tables
- RAW_DATA_INDEX.tsv
- SHA256SUMS
- REPORT.md

Final status exactly one:
- `AI_RESOURCE_MAP_COMPLETE_NO_ACTIONABLE_PROBLEM`
- `AI_RESOURCE_REBALANCING_PROBLEM_IDENTIFIED`
- `AI_RESOURCE_PROTOTYPE_SUPPORTED_DEVELOPMENT`
- `AI_RESOURCE_PROTOTYPE_NOT_SUPPORTED`

Commit/push/fetch-back/remote HEAD+tree/hash/clean and STOP.

