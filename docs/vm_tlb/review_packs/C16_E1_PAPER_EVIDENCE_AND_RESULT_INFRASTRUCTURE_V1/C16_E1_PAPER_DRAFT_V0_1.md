# C16 E1 paper draft v0.1

Status: evidence-grounded story draft. The simulator result and system-case conclusion remain **PENDING_B16_TIMING_RESULT**. Native values cited below are generated in `PAPER_RESULTS_CURRENT.tsv/json` from committed independent consumer summaries; claim IDs resolve through `C16_E1_EVIDENCE_LEDGER`.

## Motivation

Low-bit decode changes the working-set geometry. In the accepted M1 semantic profile, packed AWQ storage fits within the measured RTX 4080 L2 capacity while the corresponding dense FP16 weight exceeds it [E1-002]. This opens a cache-residency opportunity; it does not show that cache is the sole reason for the shape-dependent traffic, nor that persisting weights benefits full decode. The problem is to preserve useful packed qweight reuse without transferring more cost to other work than the local saving is worth.

## Observation chain

The investigation began with the byte-identical-input operator-by-shape interaction [E1-001]. Semantic NCU showed a large AWQ/RAW traffic contrast and a capacity-consistent packed footprint [E1-002]. Pre-target memory-state intervention changed the local target materially, though the strict primary reversibility gate remained partial [E1-003]. Natural full-model execution destroyed the isolated warm behavior at tested layer-zero targets, with role-dependent timing response [E1-004]. Targeted CUDA L2 persistence restored local timing benefit [E1-005].

Rotating shared protection retained local benefit without a material whole-decode gain [E1-006]. Increasing coverage to all selected up projections produced a positive but subthreshold decode effect [E1-007]; expanding to gate/up/down operator families also failed the whole-decode gate [E1-008]. The native budget sweep then independently measured material local up-projection savings at every budget while run-aligned, non-overlapping top-level timing accounted for the offset in other semantic work [E1-009]. The measured offset motivates an elastic, cost-aware counterfactual. The unique cache, replacement, or self-attention kernel cause is still unestablished [E1-010, E1-015].

## Mechanism: `ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1`

An exact software interval sidecar identifies the selected qweight allocations at the address presented to L2. The oracle tag isolates replacement opportunity; it is not a proposed autonomous deployment classifier. Each L2 instance has a hard protected-line quota derived from the requested global byte budget. Ordinary lines borrow unused cache space. For target fills below quota, set-local eligible ordinary victims are preferred using baseline recency; ordinary fills likewise prefer ordinary victims. At quota, protected lines compete using baseline recency when an eligible protected victim exists. Baseline invalid priority and set-local fallback remain binding. When quota is full and a target has no eligible protected victim, the fill can be admitted unprotected with a recorded denial reason; it cannot overcommit, reach across sets, or stall the target. Hits retain baseline replacement-state updates, with no promotion. There is no demotion policy or timer. With the mechanism disabled by default, baseline behavior and timing remain neutral under the qualified synthetic tests [E1-012].

This is a bounded replacement model, not an assertion about NVIDIA's proprietary replacement policy. CPU-only implementation and address-namespace qualification are complete [E1-012, E1-013]; a performance benefit has not yet been shown.

## Methodology and authority layers

1. **Real RTX 4080 native execution:** paired RAW/AWQ timing, NCU semantics, controlled memory-state and CUDA persistence interventions, coverage and budget sweeps. The independent 174 consumers rederive the accepted observations from producer raw evidence. Results in the current tables are native CUDA-policy measurements.
2. **Bounded full-SASS trace:** the admitted D1-D3 decode trace is scoped to the qualified workload, kernel range and sidecar, with independent transfer/admission audit [E1-011]. Tensor bytes are not treated as byte-identical to the earlier native timing run, so we do not calibrate an absolute per-run cycle count to that run.
3. **RTX 4080/Ada-qualified Accel-Sim/GPGPU-Sim counterfactual:** the trace-to-L2 numeric address namespace and oracle target tagging are qualified [E1-013]. Opcode parser coverage is execution compatibility for this bundle; it is not complete Ada microarchitecture fidelity. The simulator will test counterfactual direction, mechanism activity, budget dependence and costs. It will not be presented as cycle-perfect native reproduction.

## Results available now

The native figures and machine-readable table show the packed footprint, local-versus-decode response, operator-family residual, and B8/B16/B24/BFULL native budget decomposition. The full budget analysis records 28 material local up-projection modules at each tested budget and qualifies each top-level decomposition; the representative self-attention NCU range does not reproduce the aggregate self-attention slowdown. Those facts support the local-benefit/system-offset problem statement and bound the causal interpretation.

The B16 **simulator** baseline/candidate timing, correctness comparison, activation, protection, denial and local/window effects are **PENDING_B16_TIMING_RESULT**. No speedup is inferred from native B16 or partial canary execution. Simulator B8, B24 and BFULL are **PENDING_FUTURE_BUDGET**. The system-case conclusion and final abstract claim remain open.

## Discussion boundary and next result

The present story is closed as an observation-to-mechanism rationale, not as a successful simulator system case. The next draft needs the independently accepted B16 primary review pack with terminal/correctness gates, baseline/candidate window and local timing, protection/denial counters, and committed source identities. Re-running the consumer and plot command will then populate only admitted B16 points. `B16_DECISION_TEMPLATE.md` determines whether expansion, mechanism revision or stopping the system case follows.
