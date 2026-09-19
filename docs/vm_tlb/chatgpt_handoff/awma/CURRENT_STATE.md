# AWMA Current State

Date: 2026-09-19

## Coordination stage

`AWMA_VM_PER_ACCESS_COVERAGE_REPAIR_174NEW_V1`

Node174-new remains the active scientific mainline.

Node109 V2.1 campaign is complete and released.

## Latest accepted 174 result

Execution:

```text
hrl/awma-q05-global-access-determinism-174new-v1
be82faf264e93396b4b7d4fd72078c7e4491e3e4
```

Status:

`AWMA_Q05_GLOBAL_ACCESS_DETERMINISM_CLOSURE_174NEW_V1_COMPLETE_WITH_SCOPE`

Accepted conclusion:

`PREVIOUS_STREAM_TELEMETRY_ARTIFACT`

Canonical generation-time comparison:

```text
140672 GLOBAL trace instructions
10/80 vs 0/80:
INPUT_SAME_OUTPUT_SAME for every canonical instruction
generation-time GLOBAL access delta = 0
```

Thus the formal trace/coalescing stream is deterministic.

## New correctness issue exposed by the same stage

Generation-to-VM conservation fails:

```text
generation-time GLOBAL accesses = 2182656

legacy VM unique/READY:
P34 10/80 = 776666
P34 0/80  = 864728
```

Approximate legacy GLOBAL coverage relative to generation:

```text
10/80 ~= 35.6%
0/80  ~= 39.6%
```

This is not yet the full GLOBAL+LOCAL eligible-coverage denominator.

Source audit identifies a concrete path:

`ldst_unit::memory_cycle()`

translates only current `accessq_back()`, after which positive-latency L1D and bypass-L1D paths may pop multiple further access-queue entries without independently checking/applying VM translation.

Therefore prior Q05 translation timing may under-cover coalesced accesses.

The current identity-like mapping can hide functional-address error while still skipping TLB/PTW timing/state.

## Scientific status of prior translation results

Do not delete historical evidence.

Until repair qualification:

`LEGACY_VM_UNDERCOVERAGE_BASELINE_PENDING_REQUALIFICATION`

applies to Q05 results dependent on modeled VM timing.

Producer traces, native census, structural footprint and Decode Flash capture evidence remain independent of this issue.

## node109 V2.1 final

Execution:

```text
hrl/awma-109-ten-hour-capture-native-recon-v2
8a9d96ceb00e36ebdfa3d56cc277f965fffa649c
```

Status:

`AWMA_109_TEN_HOUR_CAPTURE_AND_NATIVE_RECON_V2_COMPLETE_WITH_SCOPE`

Accepted side-lane observations:

- Decode Flash Primary-1/2 temporal and requested 2D capture coverage complete;
- Primary-1 memory traffic/footprint changes only modestly through Decode32 and is highly stable across within-step occurrence;
- Primary-2 is structurally tiny and highly invariant;
- native default pointer-chase knees are strongly data-cache-policy confounded;
- targeted `cg` surface is largely flat across location count at each tested stride;
- no clean pure-TLB latency calibration was obtained;
- simulator 10/80 remain generic model assumptions.

Node109 is released.

## Active mainline

Execute:

`CODEX_NEXT_STAGE_174NEW_VM_PER_ACCESS_COVERAGE_REPAIR_V1.md`

Goals:

1. directly prove untranslated downstream L1D/ICNT admissions in the legacy runtime;
2. build a surgical per-access VM coverage repair;
3. require every VM-eligible access to translate exactly once before downstream admission;
4. run unit/synthetic qualification;
5. run minimal real P34 legacy vs repaired comparison;
6. stop for scientific review before any broad rebaseline.

## Baseline policy

No architecture mechanism is authorized.

Do not silently replace accepted historical result packs.

If repair qualifies and changes the P34 scientific result, emit:

`STOP_FOR_SCIENTIFIC_REVIEW`

and return a minimal requalification plan.

## STOP boundary

Finish repair qualification, push/verify/clean, then STOP.
