# AWMA CROSS-CALIBRATION V1R2 HANDOFF CONTEXT

Date: 2026-09-23

This handoff supersedes the scientific interpretation of Cross-Cal V1 while preserving all of its raw simulator results.

## 1. Accepted new Native authority

Branch/HEAD:

`hrl/awma-crosscal-exact-measured-trace-v1r1 @ 149af0566cc6720621fdfe88d3cd3ca9b32cba67`

Exact frozen CLI:

```text
M0 --stride 4096  --locations 16   --warps 1  --steps 512 --samples 50 --warmup-batches 2 --policy default --seed 102
M1 --stride 4096  --locations 4096 --warps 1  --steps 512 --samples 50 --warmup-batches 2 --policy default --seed 102
M2 --stride 4096  --locations 4096 --warps 16 --steps 512 --samples 50 --warmup-batches 2 --policy default --seed 102
M3 --stride 65536 --locations 1024 --warps 1  --steps 512 --samples 50 --warmup-batches 2 --policy default --seed 102
```

Three uninstrumented Native process repetitions per configuration.

Contemporaneous Native medians-of-medians:

```text
M0 = 52.0 cycles/load
M1 = 294.0 cycles/load
M2 = 280.0 cycles/load
M3 = 152.5 cycles/load
```

Exact Native M1→M2 change:

`-4.7619047619%`

The historical V1R2 value (-4.5840%) remains valid historical evidence, but V1R1 contemporaneous timing is the primary reference for the new cross-calibration.

Node164 immutable bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/crosscal_exact_v1r1_20260923T111500Z`

Status:

`NODE164_SHA256_VERIFY_PASS_58_MEMBERS`

Evidence classes:

- `NATIVE_UNINSTRUMENTED_TIMING_EXACT_V1R1`
- `SIMULATOR_NATIVE_CONTEXT_PAIR_EXACT_V1R1`

For every M0–M3 capture, the same process/context contains:

`chase occurrence0 warmup → chase occurrence1 measurement`

Bracket counts are closed:

```text
M0 warmup=2, measured=50
M1 warmup=2, measured=50
M2 warmup=32, measured=800
M3 warmup=2, measured=50
```

No Accel-Sim was run on node109.

## 2. Accepted 174 prep audit

Branch/HEAD:

`hrl/awma-174-crosscal-v1r1-prep @ a04085f73458c9d30537640c2f7daad4a3aa3dd7`

Frozen decisions:

```text
CURRENT_M0_M3_TRACE_PHASE = WARMUP_CHASE_OCCURRENCE0
MEASURED_OCCURRENCE1_TRACE_NOT_PRESENT_IN_ACCEPTED_BUNDLE
TRACE_PERMUTATION_SEED_UNRESOLVED
M0_M3_MECHANISM_INACTIVE_CONTROL_SUITE
```

The old Cross-Cal V1 evidence is reclassified as:

`CROSSCAL_V1_WARMUP_TRACE_SUPPORTING_ONLY`

Accessq-cardinality audit:

```text
M0: 1024 dependent LDG events, all cardinality=1
M1: 1024 dependent LDG events, all cardinality=1
M2: 16384 dependent LDG events, all cardinality=1
M3: 1024 dependent LDG events, all cardinality=1
```

Every active dependent LDG has one active lane and exactly one coalesced accessq entry.

Therefore Legacy/V1/V2R1 equality on M0–M3 is expected by construction and cannot validate/invalidate V1/V2R1.

Accessq telemetry neutrality PASS.

SM89 parser audit:

- 38 distinct trace opcodes;
- all admitted by the selected Ampere opcode map;
- parser compatibility only;
- no Ada fidelity claim.

## 3. Current simulator platform authority

The current cross-cal simulator hardware config is NOT an RTX4080/Ada config.

It uses:

`SM86_RTX3070/gpgpusim.config`

Key authority SHA:

`f6b480d66fb04a948c04e1a5b65527600f3959ac561dcfa2de0b6632e864fe9c`

Trace config SHA:

`a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b`

VM overlay 10/80 SHA:

`85cd687d95f712b1f6a734805a5429f8268e6fb2f173f014b73e9c3079fc9ba4`

VM overlay 0/80 SHA:

`a40fadd84a8bd64b684dfd9664a92fb6991bfa2c4c6e4c918ddcebd087002325`

Therefore all Native↔simulator conclusions must explicitly carry:

`PLATFORM_SCOPE = SM86_RTX3070_MODEL_VS_SM89_RTX4080_NATIVE`

Do not interpret a mismatch as proof of translation-model error without separating platform effects.

Do not silently create/tune an RTX4080 config in the next stage.

## 4. Frozen translation semantic authorities

V1:

`hrl/awma-174-translation-frontend-pipelining-v1 @ ad6f38878bc1e7c268b17e65fdb3793a3899a84d`

V2R1:

`hrl/awma-174-translation-frontend-ready-application-v2r1 @ dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`

V2R1 final classification:

`READY_APPLICATION_HOL_NOT_PRIMARY`

Do not reopen V1/V2R1 source semantics in either next Goal.

## 5. What the next two parallel Goals are for

### 174 goal

Use the new exact ordered warmup+measurement trace pairs to answer:

- Does the large old +86.5% M1→M2 simulator slowdown survive after exact seed/phase/context repair?
- Does exact warmup→measurement contextual replay preserve Native-like relative shape at all?
- Are the old V1/V2R1 equality observations still true for measured occurrence1 (expected because accessq cardinality remains structurally one)?

This is a control/base-model calibration stage.

It is NOT a V1/V2R1 mechanism-validation stage.

### 109 goal

Create a NEW calibration-only benchmark that deliberately causes:

`accessq_entries > 1`

within one warp memory instruction.

This benchmark is required to externally exercise the exact semantic axis changed by V1/V2R1.

It must not alter any accepted old benchmark.

## 6. Global engineering rule

All new simulator telemetry must be opt-in, default OFF, observational-only, and independently neutrality-qualified.

All new Native benchmark code must live in a new source family and must not modify accepted `native_tlb_probe_v1`.

