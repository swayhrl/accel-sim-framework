# AWMA Next Wave Plan

This plan is **not** the current executable GPU instruction. It defines the intended sequence after `AWMA_UNIFIED_FOUNDATION_174NEW_V1` is reviewed and accepted.

The project should proceed without deviating from the AWMA architecture:

```text
Unified identity/catalog foundation
            |
            +------------------------------+
            |                              |
      109 / RTX4080                  174-new / CPU
 SIM_COMPAT_CAPTURE_V1          NEW_SIM_BASELINE_V1
 implementation + canary        build + qualification
            |                              |
            +---------------+--------------+
                            |
                    bounded integration
                            |
                   Cross-view calibration
```

## Wave 2A — 109 simulator-compatible capture

Primary objective:

> produce one small, fully validated, simulator-eligible trace from the same workload identity used by Native evidence.

Do not immediately recapture the whole model matrix.

Recommended progression:

1. synthetic/unit validation of tool format;
2. CUDA/vector-add or tiny known kernel canary;
3. one Qwen0 S2 representative target already characterized by Native evidence;
4. complete hash/provenance/terminal closure;
5. Pipeline-V1 transfer/ACK;
6. stop before larger capture expansion.

Preferred target selection:

- use an already well-understood Qwen0 workload/target where exact model/input/backend identity is frozen;
- prefer a representative target with manageable trace size;
- do not choose an “easy” target solely because it is small if it cannot validate the required semantics.

The capture should emit or losslessly generate:

```text
kernelslist.g
*.traceg.xz
```

or a formally specified intermediate format whose converter is itself hash-bound and validated against the traceg parser.

It must preserve all fields required by `SIM_COMPAT_CAPTURE_V1`.

## Wave 2B — 174-new new simulator baseline

Primary objective:

> establish a maintainable current simulator runtime independent of the unrecoverable exact historical C12 binary.

The baseline should bind:

```text
framework commit
core commit
binary SHA
toolchain
base config
trace config
VM/TLB/cache baseline config
telemetry schema
```

Qualification sequence:

1. build/runtime smoke;
2. traceg parser smoke;
3. one bounded historical trace anchor;
4. telemetry extraction smoke;
5. historical-reference comparison where meaningful;
6. freeze `NEW_SIM_BASELINE_V1` only after tests pass.

Do not require exact C12 numeric reproduction if source/runtime identity differs. Instead classify differences explicitly.

## Wave 2C — First integrated Qwen simulation

Only after 2A and 2B pass:

```text
Qwen SIM_INPUT
   + NEW_SIM_BASELINE_V1
   -> baseline SIM_RUN
```

Then run a **small** controlled arm set sufficient to prove the pipeline, for example:

```text
baseline
ideal translation control
one TLB/Segment candidate
```

The exact arms should be chosen from the then-current research question, not hard-coded now.

## Wave 2D — Native/Simulation calibration

Create the first real `EXACT_WORKLOAD_TARGET` Cross-view row.

Compare only aligned quantities, for example:

- address/page/cache-line footprint sanity;
- modeled vs native traffic where definitions can be aligned;
- qualitative operator/object composition;
- baseline timing/traffic fidelity where supported.

Do not force incomparable hardware counters and simulator counters into the same metric.

## Wave 3 — Scale to representative workloads

Only after the first integrated pipeline passes:

1. use Native evidence to select representative workloads/targets;
2. capture simulator-compatible traces for that subset;
3. run TLB/PTW/cache mechanism experiments;
4. construct cross-model Cross-view datasets.

Native coverage should remain broader than Simulation coverage.

## Deferred work that must not derail this path

Examples:

- AWQ fused backend recovery;
- raw 7B OOM recovery;
- unrelated Decouple-L1/L2 work on old174;
- cosmetic renaming of legacy C16 paths;
- exact resurrection of historical C12 binary if it no longer serves the current baseline.

These may proceed independently but must not redefine AWMA identity/evidence contracts.

## Efficiency rule

Each Wave should combine implementation, tests, bounded execution, evidence packaging, and handoff when they are tightly coupled. Minor obvious non-scientific defects should be fixed inline and reported, not spun into one-off Codex rounds.