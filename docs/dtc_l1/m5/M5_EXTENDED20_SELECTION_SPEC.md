# M5 Extended-20 Workload Selection Specification

Status: **SELECTION-ONLY RESEARCH TRACK — NO FORMAL DTC EXPERIMENTS AUTHORIZED ON THIS BRANCH**

Purpose: select 20 additional, commonly used, source-backed GPU compute workloads from the user's local pool of 52 already-runnable workloads. These 20 are an **Extended Compute** set for generalization analysis after the paper-10 workflow is stable. They are not substitutes for the thesis Paper-10 set and must never be selected by observed DTC speedup.

This branch is intentionally isolated from the active compute Goal branch. Selection work must not disturb running M5.0B/R5DV jobs or modify the validated Core.

## 1. Scientific role of the Extended-20

The Paper-10 set answers: "Can the Chapter-4 DTC mechanism/trend be reproduced on the thesis workloads?"

The Extended-20 set answers: "Does the same already-validated DTC mechanism generalize to a broader, commonly used GPU-compute workload set, including both expected beneficiaries and non-beneficiaries?"

Required reporting groups later:

- `PAPER_10`: thesis compute workloads only;
- `EXTENDED_20`: selected workloads from this specification;
- `ALL_COMPUTE_30`: union of Paper-10 + Extended-20, only when all component runs are correctness/fidelity clean.

Do not mix Extended-20 results into paper Figure 4.x labels without explicit labeling as supplemental/generalization evidence.

## 2. Selection principles

Selection must be **pre-performance** with respect to DTC. Do not inspect, rank, filter, or choose candidates using PAPER_IO/PAPER_OO cycles, speedup, DTC live-miss gains, or any result that reveals DTC benefit.

Allowed selection evidence:

1. source provenance and benchmark-suite identity;
2. algorithm/domain identity;
3. deterministic canonical input and output checking;
4. prior "runnable/pass" evidence;
5. source/static memory-access structure;
6. existing **conventional/Base-only** characterization if already available;
7. historical wall-clock cost from prior runs;
8. launch geometry / work amount;
9. operation mix (load/store/atomic) from source or conventional-only evidence.

If an existing result file contains Base/IO/OO together, Codex must not use the IO/OO performance fields for selection. If necessary, redact/ignore those fields and use only Base/source metadata.

## 3. Candidate hard eligibility gates

A workload is eligible only if all applicable gates pass.

### E1 — Compute workload

- CUDA/GPU compute workload, not graphics scene or a graphics-memory proxy.
- No microbenchmark/unit-test-only workload unless it is a recognized benchmark application with a standard problem definition.

### E2 — Source/provenance

Must have a source-backed identity:

- benchmark suite/project;
- application/algorithm name;
- source version/commit/tag when recoverable;
- build/wrapper path;
- PTX/binary identity if already available.

### E3 — Deterministic input

- canonical/standard input or a deterministic locally frozen input;
- input hash/path recoverable;
- no input chosen because it improves DTC speedup.

### E4 — Correctness

- prior successful run exists, or a reliable output/self-check exists and is known to pass;
- output checking method is documented.

### E5 — Nontrivial workload

Reject trivially tiny smoke tests that fail to exercise a meaningful GPU working set. Prefer standard/canonical problem sizes that launch multiple CTA waves and use all available SMs where the source suite supports such inputs.

### E6 — No silent duplicate of Paper-10

Do not select the same algorithm as a Paper-10 workload under another wrapper/name/version unless there is a scientifically distinct access pattern that is explicitly justified.

Paper-10 algorithms to exclude as direct duplicates:

- bicg
- atax
- gemver/gemv mapping once resolved
- mvt
- syrk
- gesummv/gesu mapping once resolved
- syr2k
- spmv
- 2mm
- conv2d / 2DConvolution mapping once resolved

### E7 — No near-duplicate crowding

Do not fill the set with many variants of the same algorithm family. Examples: multiple nearly identical GEMM sizes, multiple BFS implementations, multiple stencil dimensions, or multiple wrappers for the same kernel. Keep the variant that is most canonical, best checked, and most representative unless two variants have clearly different memory behavior.

### E8 — Simulator feature fidelity

Exclude candidates whose "pass" depends on an unsupported/approximated feature that would materially change DTC interpretation, unless the feature is already source-backed and validated in M1-M4/M5. Examples to audit: unsupported UVM behavior, dynamic parallelism, unsupported graphics/texture semantics, or host-side behavior dominating the run.

## 4. Diversity axes to characterize for all 52 candidates

Every candidate must be tagged before selection.

### A. Application/domain class

Use one primary class and optional secondary classes:

- `DENSE_LINEAR_ALGEBRA`
- `STENCIL_STRUCTURED_GRID`
- `SPARSE_LINEAR_ALGEBRA`
- `GRAPH_TRAVERSAL`
- `SEARCH_SORT_SCAN_REDUCTION`
- `IMAGE_SIGNAL_PROCESSING`
- `DYNAMIC_PROGRAMMING`
- `PARTICLE_PHYSICS_NBODY`
- `MONTE_CARLO_STATISTICAL`
- `COMPRESSION_CRYPTO_OTHER`
- `OTHER_SOURCE_BACKED_COMPUTE`

### B. Memory-access pattern

Tag one or more:

- `REGULAR_COALESCED`
- `REGULAR_STRIDED`
- `STREAMING_LOW_REUSE`
- `HIGH_SPATIAL_REUSE`
- `HIGH_TEMPORAL_REUSE`
- `IRREGULAR_GATHER`
- `IRREGULAR_SCATTER`
- `POINTER_GRAPH_LIKE`
- `SPARSE_INDIRECT`
- `ATOMIC_UPDATE`
- `MIXED_READ_WRITE`

### C. Conventional/Base structural tendency

Use existing Base-only evidence when available; otherwise source-infer and mark confidence.

- `PIB_PRESSURE_HIGH/MED/LOW/UNKNOWN`
- `MSHR_PRESSURE_HIGH/MED/LOW/UNKNOWN`
- `TAG_LINE_ALLOC_PRESSURE_HIGH/MED/LOW/UNKNOWN`
- `DOWNSTREAM_PRESSURE_HIGH/MED/LOW/UNKNOWN`
- `COMPUTE_HEAVY_HIGH/MED/LOW/UNKNOWN`

Do not run DTC modes to fill these fields.

### D. Operation mix

- load-dominated;
- balanced load/store;
- store-heavy;
- atomic-present / atomic-heavy;
- read-only-ish.

### E. Runtime cost

Use prior wall-clock evidence from the already-runnable pool where possible.

Classify by the 52-workload empirical distribution rather than arbitrary absolute cutoffs:

- `COST_Q1` fastest quartile;
- `COST_Q2`;
- `COST_Q3`;
- `COST_Q4` slowest quartile.

The final set must not be dominated by Q4 workloads.

## 5. Hard portfolio constraints for the final 20

The selection is a portfolio, not simply the 20 highest scores.

### P1 — Benchmark-suite diversity

- prefer at least 3 independent benchmark suites/projects when the 52-candidate pool permits it;
- no single suite should exceed 50% of the final 20;
- if the local pool makes this impossible, document the exact inventory limitation rather than fabricating diversity.

### P2 — Domain diversity

Cover at least 6 primary domain classes if available in the pool.

No one primary domain class should occupy more than 5 of 20 unless the 52-candidate inventory is unusually narrow.

### P3 — Access-pattern diversity

The final set must include, when available:

- >=3 irregular/sparse/graph-like workloads;
- >=3 regular/streaming or structured-grid workloads;
- >=3 reuse-heavy workloads;
- >=2 write/atomic/update-heavy workloads;
- >=2 compute-heavy/low-memory-pressure controls;
- >=2 reduction/sort/scan/search-style workloads.

Categories may overlap, but Codex must show that the resulting set spans both likely DTC beneficiaries and likely non-beneficiaries.

### P4 — Base-pressure diversity

Using only Base/source evidence, aim for a balanced spread rather than selecting only highly memory-stalled applications:

- approximately 6-8 candidates with high conventional memory-structure pressure;
- approximately 6-8 medium/mixed candidates;
- approximately 4-6 low-pressure or compute-heavy controls.

This is a target distribution, not permission to use DTC performance.

### P5 — Runtime practicality

- no more than 5 of the final 20 should come from `COST_Q4` unless a coverage requirement cannot otherwise be met;
- prefer at least 10 from Q1/Q2 combined;
- if a uniquely valuable Q4 workload is selected, state what behavior/domain it uniquely covers.

### P6 — No speedup cherry-picking

The final selection report must explicitly attest that no IO/OO/DTC speedup was used in ranking or tie-breaking.

## 6. Ranking method

After hard eligibility filtering, score eligible candidates only to help choose among coverage-equivalent options.

Recommended 100-point score:

- 25: behavior/domain coverage novelty relative to already-selected candidates;
- 20: source/provenance/canonicality quality;
- 15: deterministic correctness/input quality;
- 15: Base-only structural-interest value (high, medium, or useful negative control; not DTC benefit);
- 10: operation-mix novelty (writes/atomics/irregularity where underrepresented);
- 10: runtime practicality;
- 5: benchmark-suite diversity contribution.

Important: the score is subordinate to portfolio constraints. Do not simply take the top 20 if that produces a narrow set.

## 7. Selection procedure

### S0 — Inventory all 52

Create a complete inventory before selecting anything.

Required fields:

`candidate_id | suite | workload | algorithm | source_version | source_path | wrapper | input | input_hash | output_check | prior_pass_evidence | launch/work_amount | primary_domain | access_tags | op_mix | Base_pressure_tags | evidence_confidence | wall_time | cost_quartile | Paper10_duplicate? | eligibility | notes`

### S1 — Exclude ineligible and duplicate candidates

Record a specific exclusion reason for every rejected candidate.

### S2 — Build behavior matrix

Produce a candidate-by-feature matrix for all eligible workloads. Use source and existing Base-only evidence. Do not inspect DTC performance.

### S3 — Draft candidate portfolio

Select 20 satisfying P1-P6. Also identify:

- 5 alternates (`ALT01-ALT05`) in priority order;
- why each alternate lost to a selected workload.

### S4 — Adversarial self-review

Before finalizing, test the 20 against these questions:

1. Did one suite dominate because it was easiest to inspect?
2. Are we selecting many variants of one algorithm family?
3. Did runtime convenience eliminate all difficult/irregular workloads?
4. Did we accidentally use DTC performance knowledge?
5. Are both likely beneficiaries and non-beneficiaries present?
6. Do load/store/atomic behaviors vary?
7. Are there obvious common benchmark workloads in the 52 pool that are missing without a good reason?
8. Could a reviewer reasonably accuse the set of being cherry-picked for DTC?

If yes, revise and document the revision.

### S5 — Freeze proposal, do not launch 60 formal runs

This selection branch stops at a selection proposal. Do not launch the Extended-20 Base/IO/OO formal wave here.

The later formal runner will use the compute M5 formal behavior/config/parser anchor after the Paper-10 path is stable.

## 8. Required outputs

Commit only compact metadata/evidence, not raw logs or binaries.

Required files:

1. `docs/dtc_l1/m5/extended20/EXTENDED52_INVENTORY.tsv`
2. `docs/dtc_l1/m5/extended20/EXTENDED52_BEHAVIOR_MATRIX.tsv`
3. `docs/dtc_l1/m5/extended20/EXTENDED20_SELECTED.tsv`
4. `docs/dtc_l1/m5/extended20/EXTENDED20_ALTERNATES.tsv`
5. `docs/dtc_l1/m5/extended20/EXTENDED20_NOT_SELECTED.tsv`
6. `docs/dtc_l1/m5/extended20/M5_EXTENDED20_SELECTION_REPORT.md`
7. `docs/dtc_l1/m5/handoffs/M5_E0_EXTENDED20_SELECTION.md`

`EXTENDED20_SELECTED.tsv` minimum columns:

`rank | workload | suite | algorithm | input | domain | access_tags | op_mix | Base_pressure | cost_quartile | score | unique_coverage_reason | provenance_status`

## 9. Handoff acceptance

M5_E0 selection is PASS only if:

- all 52 candidates are inventoried;
- every excluded/non-selected candidate has a reason;
- all 20 selected workloads pass E1-E8;
- portfolio P1-P6 is checked explicitly;
- 5 alternates are identified;
- no DTC performance field was used;
- source/input/output-check provenance is adequate for later reproduction;
- runtime cost distribution is recorded;
- selection can be reproduced by another researcher from the committed metadata.

Final status for this branch:

`M5_EXTENDED20_SELECTION_READY_FOR_REVIEW`

Do not merge into the active compute Goal automatically. The researcher/ChatGPT will review the 20-workload proposal first, then authorize the Extended-20 formal experiment track.
