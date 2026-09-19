# DRAFT — AWMA 20h Pipeline Acceptance Contract V1

Date: 2026-09-19

Status: `PRE_REPAIR_DRAFT_NOT_EXECUTABLE`

This document defines evidence and acceptance rules for the post-repair 20-hour unattended
campaign. It is not authorization to execute.

## 1. Global acceptance principles

A stage is accepted only if:

1. exact source / branch / commit authority is recorded;
2. exact scientific input identity is recorded;
3. tool/runtime identity is recorded;
4. intended target identity is proved, not inferred from a convenient name;
5. all required artifacts close size/hash/provenance;
6. node164 ACK exists for large durable outputs;
7. partial runs are not represented as complete;
8. unsupported measurements are explicitly marked unavailable;
9. claim scope matches the evidence level;
10. final report distinguishes reuse, new execution, partial, skipped, and failed.

Engineering success alone is not scientific acceptance.

## 2. Global prohibited acceptance shortcuts

The following are never sufficient by themselves:

- process exit code 0;
- profiler output file exists;
- rsync exit code 0;
- target kernel name string matches;
- a result is numerically close to a previous one;
- a page-footprint change is observed;
- an NCU counter exists;
- a state checkpoint restores model tensors;
- a model asset exists on disk;
- a detailed trace is large.

## 3. Accepted status vocabulary

Use exactly where applicable:

`ACCEPTED`

`ACCEPTED_WITH_SCOPE`

`PARTIAL_NOT_ADMITTED`

`SKIPPED_GATE`

`SKIPPED_BUDGET`

`COUNTER_UNAVAILABLE`

`IMPLEMENTATION_LEVEL_ONLY`

`STOP_SCIENTIFIC`

`FAILED_ENGINEERING_UNRESOLVED`

No ambiguous `PASS-ish` or equivalent status.

## 4. 174 repair authority gate

Before any post-repair simulation is accepted, the final handoff must bind:

- exact repair execution branch;
- exact repair commit;
- exact repair review pack;
- exact candidate/final binary SHA;
- defect decision;
- repair qualification decision;
- repaired invariants;
- exact accepted per-access semantics.

Required defect/repair properties for a qualified repaired runtime:

- legacy untranslated downstream admission directly observed;
- source path localized;
- every eligible downstream access translated before admission;
- zero untranslated downstream admissions;
- zero post-ready retranslation attempts;
- no architecture-semantic changes beyond the correctness repair;
- natural real-Q05 repaired control completes.

If the repair report does not support all of these, the final handoff must not authorize the
candidate requalification plan unchanged.

## 5. 174-M0 repaired Q05 acceptance

### 5.1 Identity

Every reused/new run must bind:

- source SHA;
- binary SHA;
- simulator config;
- SIM_INPUT/context bundle;
- exact target member;
- R0/I0 mode;
- telemetry schema.

### 5.2 Completion

A complete target run must naturally complete its target scope.

Fixed-window progress cannot substitute for full-target cycle comparison.

### 5.3 Coverage

Required:

- `vm_untranslated_downstream_admissions = 0`;
- `vm_post_ready_retranslation_attempts = 0`;
- accepted GLOBAL/LOCAL conservation;
- all admitted eligible accesses have an observed translation outcome.

### 5.4 Context

Same-source isolated/P8/P34 target identity must be proved.

Historical standalone isolated evidence remains historical unless exact pairing has been
established.

### 5.5 I0

For Q05-only I0:

- predecessors remain repaired natural R0;
- Q05 I0 is per-access clean;
- identity SimVA→SimPA preserved;
- no hidden bypass outside the approved I0 contract.

Otherwise status is `REPAIRED_TARGET_I0_DEFERRED`.

### 5.6 Required decision artifact

`LEGACY_CLAIM_REQUALIFICATION.md`

must classify each major old translation claim as:

- `RETAINED_WITH_NEW_VALUES`;
- `QUALITATIVELY_RETAINED`;
- `MATERIALLY_REVISED`;
- `RETIRED`;
- `NOT_YET_REQUALIFIED`.

## 6. 174-O1 cross-family analysis acceptance

The analysis is accepted only if:

- every row identifies its source evidence;
- compared metrics share the same unit/definition;
- census-to-trace joins use exact identity;
- family-internal variation and cross-family difference are separated;
- offline page footprint is not converted into simulator TLB behavior;
- no global chronology is invented from per-trace file ordering;
- limitations are reported next to derived claims.

Required outputs:

- `CROSS_FAMILY_EXISTING_EVIDENCE_MATRIX.tsv`;
- `CROSS_FAMILY_EVIDENCE_GAPS.md`;
- `NEXT_FAMILY_SELECTION_RATIONALE.md`.

## 7. 174-C1 non-Attention R0/I0 acceptance

This stage is accepted only if:

- final handoff explicitly enabled it;
- chosen target input is consumer-qualified;
- complete R0 and I0 targets finish;
- repaired coverage invariants close for both;
- target identity is exact;
- result is labeled isolated if no matched predecessor context exists;
- no mechanism parameter is changed between the pair except R0/I0 translation mode.

One incomplete side means the pair is `PARTIAL_NOT_ADMITTED`.

## 8. 109-M0 native resource closure acceptance

For each target:

- exact semantic/kernel/occurrence identity;
- uninstrumented timing authority or explicit absence;
- profiler/tool version;
- replay/cache-control mode;
- pass count;
- metric definitions;
- resource results or `COUNTER_UNAVAILABLE`;
- source receipt for reused evidence.

Targets:

- Q05 Prefill Flash;
- Prefill GEMM Primary;
- Decode GEMV Primary;
- Decode Flash Primary-1.

M0 is accepted when all four rows are scientifically closed even if some optional metrics are
unavailable.

Do not fail the stage merely because a hardware counter is unsupported.

## 9. 109-M1 E1 acceptance

### 9.1 Core matrix completeness

Required 8 core identities:

- down_proj/raw/M1;
- down_proj/AWQ/M1;
- down_proj/raw/M256;
- down_proj/AWQ/M256;
- q_proj/raw/M1;
- q_proj/AWQ/M1;
- q_proj/raw/M256;
- q_proj/AWQ/M256.

Each must have:

- exact model revision;
- operator/layer identity;
- weight/quantization asset identity;
- activation-pool/hash authority;
- tensor shape/rank/stride/dtype;
- implementation/kernel sequence;
- native timing samples;
- numeric status;
- provenance receipt.

### 9.2 Semantic comparability

Each raw/AWQ pair must be classified:

`SEMANTIC_PAIR_QUALIFIED`

or

`IMPLEMENTATION_LEVEL_ONLY`

If a required input transform / absorbed scale cannot be proved, do not claim same-function
raw/AWQ semantics.

### 9.3 Dtype bridges

If runtime dtype differs materially across a compared pair, bridge status must be:

`NOT_REQUIRED`

or

`REQUIRED_AND_COMPLETE`

or

`REQUIRED_BUT_SCIENTIFICALLY_BLOCKED`.

Do not silently compare BF16 raw against FP16 AWQ as pure quantization.

### 9.4 Timing quality

For each newly measured point:

- warmup count recorded;
- every measured sample retained;
- synchronization method recorded;
- median/dispersion reported;
- GPU background/clock/temperature sanity recorded where practical.

A point whose noise interval prevents the intended distinction remains valid data but cannot
trigger a detailed-capture claim.

### 9.5 Implementation fingerprint

Must include all kernels in the semantic region.

If AWQ path contains dequant/copy/matmul/postprocess kernels, record them all.

### 9.6 Resource diagnosis

At least the points used to support an explanation must have enough resource metrics to
distinguish the stated competing explanations.

Unsupported counters are not failure if explicitly marked.

### 9.7 E1 success decisions

Allowed:

`E1_CORE_QUALIFIED`

`E1_CORE_QUALIFIED_WITH_IMPLEMENTATION_ONLY_SUBSET`

`E1_PARTIAL_SCIENTIFIC_STOP`

No requirement exists for AWQ to be faster.

No-effect or opposite-effect results are accepted if measurement/identity contracts are closed.

## 10. 109-C1 E3 acceptance

### 10.1 Natural N

Required:

- exact Q30 state authority;
- exact router output;
- active expert set;
- assignment histogram;
- gate weights where needed by output semantics;
- execution-region identity.

### 10.2 P permutation

Required:

- documented joint permutation;
- documented inverse permutation;
- output-equivalence test;
- same backend/residency policy.

Failure of equivalence blocks P-based scientific interpretation.

### 10.3 U-active

Required:

- same naturally active expert set;
- same M/E/k and total assignments;
- explicit synthetic-routing label;
- deterministic construction receipt;
- same expert execution backend/residency policy.

### 10.4 E3 decision

Allowed:

`E3_LIGHT_DIAGNOSTIC_QUALIFIED`

`E3_NATURAL_ONLY_QUALIFIED`

`E3_SKIPPED_GATE`

`E3_STOP_SCIENTIFIC`

Do not infer natural routing bottleneck from an artificial hotspot not observed naturally.

## 11. Opportunity-task acceptance

### G1 scenario extension

Required:

- new scenario ID;
- exact token/input binding;
- model revision;
- native timing;
- complete lightweight census;
- target/family deltas;
- explicit statement that no detailed trace was required unless separately selected.

### G2 same-quantized-weight decomposition

Required:

- same quantized weight authority;
- trustworthy runtime reference path;
- timing boundary includes/excludes dequantization explicitly;
- numeric reference passes;
- B/C paths labeled diagnostic rather than deployed AWQ.

If a trustworthy reference path does not already exist, `SKIPPED_GATE`.

### G3 profiler protocol

Required:

- same target identity;
- same metric set;
- exact replay/cache-control settings;
- enough repeats to separate measurement noise where practical;
- claim limited to profiling-protocol sensitivity.

Do not label as TLB cold/hot.

### G4 Llama raw holdout

Required:

- exact Llama revision/binding;
- pre-frozen operator roles;
- M1/M256 shape definitions;
- native timing/fingerprint;
- claim limited to raw shape trend.

Do not use it as independent AWQ validation.

## 12. Detailed capture acceptance

Detailed capture is optional.

Before capture:

- selector rule frozen;
- selected pair identity frozen;
- native effect/noise recorded;
- scientific reason documented;
- budget check passes.

After capture:

- producer terminal complete;
- zero drop/overflow under accepted producer contract;
- validator passes;
- static/global-address path closure per the applicable producer contract;
- hashes close;
- node164 ACK;
- raw size within authorized budget.

If bounded partial:

`PARTIAL_NOT_ADMITTED`.

## 13. Holdout acceptance

A validation sample remains independent only if:

- it was not used to choose the selector;
- it was not used to tune thresholds;
- its result was not inspected before rules were frozen.

If rules are modified after seeing it, reclassify it as development evidence.

## 14. Storage acceptance

A large artifact is durable only after:

1. local manifest/size/hash closure;
2. transfer to node164 partial path;
3. destination size/hash verification;
4. no-overwrite admission;
5. durable receipt;
6. ACK.

`rsync exit 0` alone is not acceptance.

## 15. Time/budget acceptance

Campaign timing metadata must record:

- start;
- deadline;
- no-new-target cutoff;
- per-task start/end;
- finalization start.

No new scientific target starts in the final 2 hours.

Tasks exceeding budget become:

`PARTIAL_NOT_ADMITTED`

or

`SKIPPED_BUDGET`.

Do not extend the campaign automatically.

## 16. Final review-pack acceptance

109 and 174 each produce their own review pack.

Each final report must include:

- exact execution branch / SHA;
- exact parent;
- accepted/reused/new/partial/skipped task matrix;
- scientific stops;
- opportunity tasks actually run;
- raw/node164 index;
- SHA256SUMS;
- clean-worktree confirmation;
- lock-release confirmation where relevant;
- next-stage proposal only, not automatic execution.

Final success means the delivered evidence satisfies its scoped contracts.
It does not mean every queued opportunity task ran.
