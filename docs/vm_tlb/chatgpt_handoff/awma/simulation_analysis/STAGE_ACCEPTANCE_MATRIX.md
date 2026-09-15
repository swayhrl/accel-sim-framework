# AWMA Simulation Analysis — Stage Acceptance Matrix

This matrix defines what each major Simulation Analysis stage must prove before the next stage can use its outputs as authority.

The stages are intentionally substantial. Recoverable engineering problems should be solved inside the active Goal rather than split into extra coordination rounds.

## S0 — Simulation Foundation

Goal: establish identities, input admission, telemetry normalization, catalog/provenance, consumer contract, and a maintainable runtime candidate.

Required PASS evidence:

```text
versioned simulation schemas and deterministic IDs
fail-closed SIM_INPUT admission
historical C12/C13/C14 status-preserving adapters
normalized telemetry layer + regression tests
immutable/idempotent simulation catalog
SIM_COMPAT_CAPTURE_V1 consumer validator + positive/negative fixtures
node164 simulation metadata/hash closure
parallel-worktree/process isolation evidence
inline recovery log
```

Runtime result:

```text
preferred: NEW_SIM_BASELINE_V1 qualified
allowed: runtime subphase BLOCKED_ENVIRONMENT after autonomous recovery is exhausted
```

Accepted stage states:

```text
AWMA_SIMULATION_FOUNDATION_PASS
AWMA_SIMULATION_FOUNDATION_PASS_RUNTIME_BLOCKED
```

The second state must still satisfy every non-runtime mandatory gate.

## S1 — `SIM_COMPAT_CAPTURE_V1` Producer Qualification

Goal: make 109/RTX4080 produce simulator-consumable trace without inventing semantics.

Required PASS evidence:

```text
exact workload/target binding
producer source/binary SHA
kernel launch and instruction/warp/CTA ordering required by consumer
opcode/access kind/memory space/byte width
active mask/lane addresses
required sync/control markers
address/object context sidecars
zero drop/overflow + complete terminal/list closure
payload/list/sidecar SHA closure
174-new consumer validator PASS
stable SIM_INPUT_ID
decoder record/instruction/address sanity
repeatability/deterministic re-read checks
bounded baseline replay smoke
```

Do not qualify a capture if missing fields are reconstructed from C16WARP1.

Accepted state:

```text
SIM_COMPAT_CAPTURE_V1_QUALIFIED
```

## S2 — First Current-model Baseline Simulation

Goal: run the first current Qwen target(s) on the qualified baseline without mechanism changes.

Each target must close:

```text
WORKLOAD_ID
TARGET_ID
SIM_INPUT_ID
SIM_BASELINE_ID
SIM_RUN_ID
```

Required outputs:

```text
exact input/config/binary/command hashes
complete raw simulator log
normalized TLB/PTW/cache/DRAM/performance telemetry
completion/timeout status
repeat run or deterministic consistency evidence
claim scope
```

Recommended initial target coverage:

```text
Qwen0 Prefill Attention
Qwen0 Prefill heavy GEMM
Qwen0 Decode early memory/attention
Qwen0 Decode late memory/attention
```

Use only targets with qualified sim-compatible traces.

Accepted state:

```text
CURRENT_MODEL_BASELINE_SIMULATION_PASS
```

## S3 — Native ↔ Simulation Calibration

Goal: quantify how the qualified simulation baseline relates to real-GPU Native evidence.

Required aligned metrics when available:

```text
page/cache-line/address footprint
memory-operation composition
L1/L2/DRAM traffic or comparable counters
kernel/target identity and workload binding
```

Required analysis:

```text
identity relation for every comparison
native and simulator values both retained
absolute/relative deltas
known modeling differences
unexplained mismatch list
metric-by-metric calibration qualification
```

Do not require exact equality where hardware counter semantics and modeled counters differ; document the semantic relation.

Accepted states may be metric-specific, for example:

```text
CALIBRATED_FOR_FOOTPRINT
CALIBRATED_FOR_TRAFFIC_DIRECTIONALLY
NOT_CALIBRATED_FOR_ABSOLUTE_CACHE_RATE
```

No mechanism-speedup claim is allowed before the baseline itself is sufficiently understood.

## S4 — TLB/PTW Opportunity Study

Goal: characterize translation pressure before proposing/finalizing mechanisms.

Required baseline sweeps are bounded and hypothesis-driven, covering as applicable:

```text
TLB reach/capacity/associativity sensitivity
page size sensitivity
PTW latency/walker count/PWC sensitivity
translation exposure/stall sensitivity
Weight vs KV vs other object translation pressure
Prefill vs Decode
early vs late Decode/context-growth effects
```

Required conclusion form:

```text
what resource is limiting
where it is limiting
which workloads/targets show it
which do not
upper-bound opportunity
native evidence that motivates the simulated phenomenon
```

Accepted state:

```text
TLB_PTW_OPPORTUNITY_QUALIFIED
```

Mechanism work should be deferred if opportunity is weak or not reproducible.

## S5 — Cache Opportunity Study

Goal: characterize modeled L1/L2/cache/memory-hierarchy opportunity before mechanism implementation.

Required studies as appropriate:

```text
capacity/associativity sensitivity
replacement/bypass sensitivity
Weight/KV/metadata working-set composition
L1/L2/DRAM traffic shifts
sector/line utilization where model supports it
Prefill/Decode and context-growth differences
interaction with translation changes
```

Required conclusion form mirrors S4: bottleneck, target scope, upper bound, negative cases and Native motivation.

Accepted state:

```text
CACHE_OPPORTUNITY_QUALIFIED
```

## S6 — Mechanism Experiments

Goal: evaluate specific TLB/PTW/cache mechanisms under controlled deltas.

Every mechanism comparison requires:

```text
same admitted SIM_INPUT_ID
same qualified baseline runtime
explicit baseline run
explicit mechanism run
only intended config/code semantic delta
mechanism-relevant counters
performance metrics
negative/regression targets
source/config diff and rationale
```

For code changes affecting architectural semantics, produce an explicit design record and directed tests before formal experiments.

Accepted mechanism result classes:

```text
FORMAL_TARGET_SPECIFIC
FORMAL_MULTI_TARGET
DIAGNOSTIC
NO_BENEFIT
REGRESSION
```

Do not generalize across models from one target.

## S7 — Multi-model Expansion

Goal: use Native Characterization to choose representative simulation targets rather than simulating every model indiscriminately.

Required selection evidence:

```text
Native feature/fingerprint basis
model/scenario/phase coverage
selection rule
certainty/rare targets retained
why selected models represent distinct behavior classes
```

For each new model, S1/S2 admission and baseline rules still apply.

Cross-model common-pattern claims require predefined support, e.g. consistent direction across multiple independent model lineages rather than simple family duplication.

Accepted state:

```text
MULTIMODEL_SIMULATION_LIBRARY_QUALIFIED
```

## S8 — Research Closeout

Goal: produce a durable Simulation Evidence Library and cross-view research dataset suitable for paper/design decisions.

Required closure:

```text
all formal runs cataloged
raw logs and simulator inputs hash-bound outside Git
normalized datasets reproducible from cataloged authority
Native/Simulation origin preserved
formal/diagnostic boundaries explicit
mechanism claims tied to exact inputs/baselines/configs
open unsupported claims listed
cost/runtime model documented
review packs independently auditable
```

Final outputs should support both:

```text
scientific conclusions
future re-analysis without rerunning every experiment
```

## Stage progression rule

A later stage may consume a prior stage as formal authority only after its acceptance state is closed.

However, implementation preparation may proceed in parallel when it cannot contaminate the scientific authority. Example:

```text
S0 consumer contract can be built while Native capture continues.
S1 producer tooling can be prepared before S0 runtime calibration closes.
S4 analysis scripts can be written before S2 data exists.
```

What must not happen is using an unqualified artifact as if the previous stage had passed.
