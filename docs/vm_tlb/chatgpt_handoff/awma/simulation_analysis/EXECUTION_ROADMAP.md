# Simulation Analysis Execution Roadmap

## Scheduling principle

This roadmap is designed to progress in relatively large rounds. Do not create a separate round for every small cleanup. Small, obviously safe, non-scientific issues should be fixed inline, regression-tested, documented in the review pack, and the stage should continue.

## Stage S0 — Simulation foundation on 174-new

Primary node: 174-new.

GPU: none.

Goal: build as much of the complete Simulation Analysis foundation as possible before touching the 4080.

One round should attempt all of the following:

1. establish AWMA simulation identities/catalog schemas;
2. implement simulation input admission/validation;
3. normalize inherited historical simulation records;
4. establish simulation telemetry normalization;
5. audit/build `NEW_SIM_BASELINE_V1` candidate;
6. perform bounded historical parser/replay calibration if runtime becomes available;
7. generate the exact producer-side requirements for `SIM_COMPAT_CAPTURE_V1`.

Expected outcome:

```text
AWMA_SIMULATION_FOUNDATION_PASS
```

or, if runtime build is blocked but all non-runtime work is complete:

```text
AWMA_SIMULATION_FOUNDATION_PASS_RUNTIME_BLOCKED
```

Runtime blockage must be exact and documented, not a generic excuse.

## Stage S1 — Simulator-compatible capture qualification

Primary nodes: 109 producer + 174-new consumer.

Start only when 109 can spare bounded GPU time without disrupting Native Characterization.

Prefer requalification of the existing Accel-Sim NVBit tracer on RTX4080/SM89.

One round should include:

```text
vector/synthetic canary
small Qwen target canary
trace closure + transfer
174 admission/parser validation
NEW_SIM_BASELINE bounded smoke
```

Do not yet capture all current-model targets.

Acceptance:

```text
SIM_COMPAT_CAPTURE_V1_QUALIFIED
```

with at least one formally admitted `SIM_INPUT_ID` and one bounded simulator smoke.

## Stage S2 — First current-model baseline simulation

Primary current workload:

```text
Qwen2.5-0.5B S2_TEXT
```

Initial target set should follow accepted Native semantic coverage:

```text
Prefill Attention
Prefill heavy GEMM
Decode early Attention/KV-memory
Decode late Attention/KV-memory
```

Do not require a separate simulation target for every Native target if implementation/shape is proven equivalent for the scientific question.

For every target run at least the qualified real-PTW baseline. Useful controls, if qualified and supported by the baseline, include:

```text
VM disabled / translation-free control
ideal-translation control
real PTW generic baseline
```

Purpose:

- characterize baseline TLB/PTW/cache behavior;
- determine which operators/phases actually have simulation-visible translation/cache exposure;
- measure early-vs-late Decode changes;
- compare model behavior to Native page/line/object evidence where identity aligns.

Do **not** start a wide mechanism parameter sweep in this stage.

## Stage S3 — Baseline fidelity and Cross-view qualification

Use Native evidence and Simulation evidence together, while retaining distinct origins.

Questions:

```text
Does simulated address/page footprint agree with admitted input/native reference?
Which NCU vs simulator traffic metrics are meaningfully comparable?
Where does the simulator over/under-estimate L2/DRAM behavior?
Do Prefill/Decode relative trends agree?
Are mechanism conclusions likely robust to known baseline fidelity gaps?
```

Produce a calibration matrix rather than forcing exact equality where the models differ.

Acceptance should define, per metric family:

```text
CALIBRATED_FOR_TREND
CALIBRATED_FOR_ABSOLUTE_COMPARISON
STRUCTURAL_ONLY
NOT_CALIBRATED
```

## Stage S4 — TLB/PTW opportunity study

Only after S2/S3.

Analyze, by target and phase:

```text
TLB reach/working-set relation
miss concentration
PTW request concentration
walker/PWC pressure
translation stall exposure
Weight vs KV translation composition
context growth sensitivity
```

This stage chooses mechanism questions; it is not yet a final paper mechanism sweep.

Historical Segment/Selective/Subentry ideas may be used as comparison baselines, not assumed winners.

## Stage S5 — Cache opportunity study

In parallel with or after TLB opportunity work, depending on runtime instrumentation maturity.

Analyze:

```text
L1/L2 hit/miss and traffic
capacity sensitivity
replacement/fill behavior
Weight vs KV/activation behavior
context/batch sensitivity
quantization metadata when applicable
```

Keep TLB and Cache mechanisms separable so one does not hide the other's effect.

## Stage S6 — Mechanism experiments

Only mechanisms supported by current-model evidence advance here.

Minimum experimental discipline:

```text
frozen SIM_BASELINE_ID
frozen SIM_INPUT_IDs
explicit baseline arm
mechanism/config SHA
bounded parameter matrix
per-target and aggregate reporting
no silent exclusion of regressions
```

For each mechanism report:

```text
performance
translation/cache counters
cost/model assumptions
which workload classes benefit
which workloads regress or are unaffected
```

## Stage S7 — Multi-model expansion

Do not simulate every model by default.

Use Native Characterization to select representative workloads.

Potential expansion dimensions:

```text
Qwen same-family scale
AWQ quantized deployment
Qwen3 Dense
MoE / DeepSeek structure
context and batch scaling
```

Simulation trace cost is treated as a budget. A new model joins Simulation Analysis only if it covers a new behavior class or tests a claimed generalization.

## Stage S8 — Research closeout

Simulation line should eventually produce:

```text
qualified simulation runtime
formal simulation input library
baseline characterization library
TLB/PTW opportunity dataset
Cache opportunity dataset
mechanism evaluation datasets
Cross-view calibration dataset
cost/fidelity statement
```

The paper/research narrative then separates:

```text
Native observation/motivation
Simulation counterfactual/mechanism evaluation
Cross-view validation/generalization
```
