# CODEX GOAL — AWMA post-negative problem pivot V1

## Mode

Enter Goal mode and execute continuously to the scientific STOP boundary.

This is designed for an unattended window. Do not request routine user decisions. Ordinary engineering problems are solve-and-continue. If a scientific identity/contract/claim boundary cannot be resolved without changing the registered question, fail closed, finalize the evidence already obtained, and STOP.

Repository: `swayhrl/accel-sim-framework`

Coordination branch:
`hrl/awma-post-negative-pivot-handoff-v1`

Stage:
`AWMA_POST_NEGATIVE_PROBLEM_PIVOT_V1`

## Accepted inputs — do not rerun

### Lane E / 109 UVM

Branch:
`hrl/awma-ai-uvm-model-derived-characterization-v1`

Accepted commit:
`f25312635dae33342d6540be92467c6ed67fdb0d`

Decision:
`MODEL_DERIVED_UVM_NO_DISTINCT_PROBLEM`

Review pack:
`docs/vm_tlb/review_packs/AWMA_AI_UVM_MODEL_DERIVED_CHARACTERIZATION_V1/`

Key boundary:
- 10/10 preregistered points complete.
- Llama KV has a reproducible oversubscription migration transition at 1.094x VRAM, but this is closest-work-covered UVM/KV/offload territory.
- OLMoE natural footprint is resident; no artificial expert oversubscription was introduced.
- PyTorch managed-tensor bridge is `NOT_READY`; this is an engineering gap, not a scientific positive result.
- fault/TLB/PPN/page-size claims remain unauthorized.

Do not repair the PyTorch bridge in this Goal.
Do not continue UVM mechanism search.
Do not add larger MoE only to manufacture oversubscription.

### Lane F / 174 resource map

Branch:
`hrl/awma-ai-gpu-resource-bottleneck-characterization-v1`

Accepted commit:
`d116e64b6c2d7faab1babc56c966ff4c1d628904`

Decision:
`AI_RESOURCE_MAP_COMPLETE_NO_ACTIONABLE_PROBLEM`

Review pack:
`docs/vm_tlb/review_packs/AWMA_AI_GPU_RESOURCE_BOTTLENECK_CHARACTERIZATION_V1/`

Key boundary:
- T0 L1-latency response is non-monotonic.
- T1 L2-capacity response is zero; tensor-unit scaling was source-coupled and unresolved.
- T2 has only finite L1-MSHR response with diminishing return.
- SPLITKV/L2 reservation-pressure reductions do not translate into material cycle gains.
- L1/M1 exact-function pair shows scale/context sensitivity, not model-family causality.
- generic MSHR/cache/backend-pressure scheduling has direct closest work.
- no architecture problem card and no prototype were authorized.

Do not repair tensor/SFU scaling merely to complete a matrix.
Do not parameter-scan generic cache/MSHR/DRAM resources.
Do not repackage scale sensitivity as an AI-specific mechanism problem.

## Frozen prior conclusions

Also preserve:
- `NO_NEW_AI_TRANSLATION_PROBLEM_IDENTIFIED_V1`
- classic intra-warp VPN dedup covers the previous PREL1 benefit
- access-path sensitivity is not a new TLB-hit-latency mechanism
- RTX4080/Ada simulator conclusions remain model-relative within their qualified scope

No new translation/TLB/PTW mechanism is authorized by this Goal.

---

# Scientific objective

The purpose of this Goal is not to find a positive result at all costs.

Build a rigorous **post-negative opportunity map** and answer:

> After resident translation, model-derived UVM, and generic modeled GPU-resource scaling have all failed to expose a differentiated actionable problem, is there a different AI-memory/execution problem already supported by accepted evidence that is specific enough to justify a new architecture study?

The discovery order is:

`accepted evidence -> exact phenomenon -> closest work -> falsifiable problem statement -> minimum diagnostic -> optional tiny prototype`

Never reverse this into:

`invent mechanism -> search workloads until it wins`.

---

# Candidate scope

Screen at most **three candidate families**, and advance at most **two problem hypotheses**.

These are candidate families, not assumed positives.

## Family A — semantic object / lifetime interaction

Ask whether accepted object-attributed evidence exposes a problem that generic cache/MSHR/DRAM scaling does not express, for example differences among:
- persistent weights,
- KV state,
- short-lived activations/intermediates,
- quantization metadata,

where lifetime/reuse/producer-consumer semantics create a concrete conflict or unnecessary movement.

Do not claim novelty from merely naming object classes.

## Family B — cross-kernel context / producer-consumer state

Ask whether isolated-kernel characterization materially misstates an AI kernel because its useful state or pressure is established by a real predecessor interval.

This may become:
- a simulation/sampling methodology problem, or
- an architecture problem only if a distinct realizable hardware limitation remains.

Do not rediscover ordinary kernel fusion or generic producer-consumer overlap.

## Family C — representation/runtime transformation

Use accepted evidence, if already present, to ask whether deployment transformations such as low-bit weight execution create a **specific hierarchy-level traffic amplification or residency conflict** that survives obvious software-kernel explanations.

Generic “dequantization is expensive” is already known and is not sufficient.

At minimum screen against:
- QServe / QoQ (W4A8KV4, dequantization/runtime overhead),
- StreamDQ (memory-side dequantization / on-chip traffic),
- existing AWQ software-kernel work.

If the phenomenon is already directly covered, reject it.

---

# Closest-work exclusions that must be respected

Do not reinvent or relabel the following broad spaces:

- HELM / generic UVM telemetry and policy selection
- FlexGen / LLM weight-KV offload
- ES-MoE / FloE-style expert offload/residency
- CCWS / cache-conscious warp scheduling
- adaptive GPU cache management / cache bypass / MSHR-pressure control
- generic DRAM/backend-pressure warp scheduling
- QServe-style dequantization/runtime-overhead optimization
- StreamDQ-style memory-side dequantization
- ClusterFusion / DeepFusion-style generic operator fusion and intermediate-HBM-traffic elimination

A candidate may still survive near this work only if the exact missing capability is explicit and testable.

---

# Phase 0 — independent audit and evidence index

Before new code or simulation:

1. Verify both accepted branches/commits/review packs above from the remote.
2. Build `POST_NEGATIVE_EVIDENCE_INDEX.tsv` containing:
   - evidence source / commit
   - workload / target
   - phenomenon
   - measurement layer: Native / NCU / NVBit / simulator / model-derived replay
   - accepted claim
   - forbidden extrapolation
   - reusable artifact path
3. Search accepted project assets for already-existing relevant C16 evidence. Reuse only if provenance and identity are accepted; do not silently import provisional data.
4. Produce `RULED_OUT_SPACE.md` summarizing what is closed and why.

Missing wrapper/index files follow the current deterministic-reconstruction policy; missing scientific payload does not.

---

# Phase 1 — problem cards before mechanisms

For each candidate family, produce a concise screening card with:

1. exact observed phenomenon;
2. at least one matched control or contrast already present in accepted evidence;
3. why Lane E/F did not already answer it;
4. nearest prior work and exact overlap;
5. the **missing capability/problem** not provided by prior work;
6. runtime-observable signal available to a real design;
7. minimum falsifying experiment;
8. independent validation sample not used to choose the hypothesis;
9. expected hardware/software cost class;
10. one of:

- `REJECT_ALREADY_COVERED`
- `REJECT_NO_MATERIAL_COST`
- `REJECT_NO_LOCALIZED_CAUSE`
- `REJECT_NO_REALIZABLE_SIGNAL`
- `CANDIDATE_DIAGNOSTIC_SUPPORTED`
- `CANDIDATE_PROTOTYPE_SUPPORTED`

Do not advance more than two candidates.

---

# Phase 2 — minimum diagnostics using existing assets

For each surviving candidate:

- Prefer existing accepted Native/NCU/NVBit/simulator artifacts.
- Do not request new 109 GPU capture in this Goal.
- Do not download models.
- Do not create a broad parameter sweep.
- Use the minimum diagnostic that distinguishes the candidate explanation from at least one alternative explanation.

Examples of allowed diagnostics:
- object-attributed bytes/pages/lines and reuse/lifetime comparison;
- same semantic operator under two accepted representation/shape conditions;
- isolated versus accepted real-prefix context if a matching context bundle already exists;
- one source-correct simulator intervention with a single changed variable.

If a diagnostic requires data that do not already exist, record an exact future capture request, but do not fabricate a proxy.

---

# Phase 3 — optional tiny prototype

Only a candidate labeled `CANDIDATE_PROTOTYPE_SUPPORTED` may enter this phase.

Maximum:
- one prototype total;
- one fixed design point;
- at most three discovery targets;
- one independent validation/holdout target;
- one necessary ablation.

Requirements:
- new simulator functionality opt-in and default OFF;
- diagnostics independently opt-in and timing-neutral;
- accepted baseline unchanged;
- exact input/target identity;
- no future-trace information;
- finite resources and explicit backpressure;
- instructions/CTA, unique UID/coverage, exactly-once, terminal and quiescence gates;
- matched control;
- preserve negative/regression results.

A positive speedup alone is not enough. The prototype must test the problem statement.

If source semantics are insufficient, stop that candidate instead of inventing simulator behavior.

---

# Phase 4 — final decision

Emit exactly one final state:

- `AWMA_POST_NEGATIVE_NO_NEW_PROBLEM_V1`
- `AWMA_NEXT_PROBLEM_IDENTIFIED_V1`
- `AWMA_NEXT_PROBLEM_PROTOTYPE_SUPPORTED_V1`
- `AWMA_NEXT_PROBLEM_REQUIRES_NEW_NATIVE_EVIDENCE_V1`

If no candidate survives, that is a valid success. Do not weaken gates to avoid a negative result.

If new Native evidence is required, emit a **single bounded capture manifest** for 109 containing only:
- exact scientific question,
- exact target/model/scenario,
- required tool,
- maximum number of runs/targets,
- expected observation,
- falsifier,
- why existing evidence is insufficient.

Do not execute that capture here.

---

# Execution / resource policy

- Work only on 174-new.
- Do not use the 109 GPU in this Goal.
- Before simulations, inspect CPU/RAM/I/O/storage and parallelize independent runs when safe.
- Independent runs may execute speculatively before scientific admission, but remain `SPECULATIVE_PRE_GATE` until their gate passes.
- Every run uses isolated output/config/log/tmp paths.
- node164 remains durable authority for large artifacts; do not fill 174 local disk.
- ordinary engineering issues: solve-and-continue.
- all new simulator features default OFF.
- no automatic merge.

Unattended envelope:
- continue through phases without waiting for routine approval;
- if the configured unattended wall-clock envelope is reached, finish the current coherent stage, finalize all valid evidence, and STOP rather than leaving ambiguous partial claims.

---

# Required deliverables

Create a review pack:

`docs/vm_tlb/review_packs/AWMA_POST_NEGATIVE_PROBLEM_PIVOT_V1/`

Minimum:
- `README.md`
- `POST_NEGATIVE_EVIDENCE_INDEX.tsv`
- `RULED_OUT_SPACE.md`
- `CANDIDATE_SCREEN.tsv`
- `CLOSEST_WORK_MAP.md`
- up to two `PROBLEM_CARD_*.md`
- diagnostic matrices/results if executed
- prototype/ablation/holdout results if authorized
- `NEW_NATIVE_EVIDENCE_REQUEST.md` only if required
- `FINAL_DECISION.md`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

Closure:
`science/engineering -> node164 when needed -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree verification -> clean worktree -> STOP`

Git transport failure is publication failure only. Preserve the exact local commit and use the configured HTTPS/HTTP1.1/SSH/gh fallback sequence; do not rerun science because a push transport fails.
