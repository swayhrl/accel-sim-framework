# EP-L2 ChatGPT Review — Lane B Descriptor-512 Interim

Status: **CONDITIONAL PASS / CONTINUE TARGET MODE.**

Do not interrupt the currently running `scan / B0-Banked` D256 backward-equivalence job.

This review covers the pushed Lane-B source state and the shared workboard status. It does not declare `D512_READY` because the mandatory longer D256 equivalence gate is still running and Lane-B has not yet published a complete review pack.

## 1. Reviewed source anchors

Formal C7e base used by Lane A:

```text
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
```

Current Lane-B calibration source:

```text
Framework branch hrl/ep-l2-d512-cal-v0
Framework tip    aae62b66685f15437cecf0193934f628e6fac6ae

Core branch      hrl/ep-l2-d512-cal-v0
Core tip         878f80869ce212e779df20b6421e4dc7f987825d
```

Both Lane-B branches are linear descendants of the exact formal C7e source pair.

## 2. Core semantic-delta audit — PASS

Core is exactly one commit ahead of formal C7e. The production change is limited to descriptor occupancy telemetry cardinality:

```text
old:
  descriptor occupancy histogram clamps all values >=256 into the final bin

new:
  descriptor histogram grows when a configured descriptor occupancy exceeds
  the current vector size, so D512 can represent 257..512 without clipping
```

The associated delta logic subtracts only bins that existed in the starting snapshot, preserving launch/window delta semantics when the current histogram grows.

No descriptor allocator/lifetime semantics are changed. No Line-MSHR, per-address cap, WAD, payload, bank, L1, queue, scheduler, or DRAM behavior is changed.

## 3. Descriptor allocator / boundary directed test — PASS with one follow-up

The added directed test correctly isolates global descriptor capacity from Line-MSHR capacity by using a test table with >512 line entries. It demonstrates:

```text
257 live descriptors are legal under D512
512 live descriptors are legal
513th/global-new allocation reports DESCRIPTOR_POOL_FULL
release reduces live count 512 -> 511
one new allocation restores 512
32/address remains independently enforced
```

This is good evidence that D512 changes the global capacity boundary rather than the per-address cap.

### Follow-up required before final D512_READY

The current directed test exercises allocator/cardinality boundaries but does not directly assert the **telemetry** result above 256 (for example p95/max/histogram bin 511/512).

Before `D512_READY`, satisfy one of the following:

```text
Preferred:
  add a small deterministic descriptor-telemetry test proving occupancy
  >256 is not clipped and p95/max are correct.

Acceptable:
  in D512 natural preflight, retain an explicit assertion/evidence row from a
  workload that exceeds 256 descriptors showing descriptor_max >256 and a
  non-clipped p95/histogram, together with parser success.
```

Do not add a new simulator behavior change merely to create this test.

## 4. Framework config-delta isolation — PASS

The D512 overlays retain the D256 configuration and change only:

```text
-gpgpu_ep_l2_descriptor_pool_size 256
->
-gpgpu_ep_l2_descriptor_pool_size 512
```

Lane B also added a fail-closed test comparing the D256/D512 overlays and requiring exactly that one option difference for both Legacy and Banked variants.

This is the correct isolation for the D512 experiment.

## 5. Runner/provenance changes — PASS for current stage

The runner now explicitly distinguishes:

```text
TARGET_BASELINE_D256
SPECULATIVE_CALIBRATION_D512
```

and records descriptor pool size in the run/campaign metadata while retaining source/config hash checks and separate result roots.

This avoids silently promoting D512 to formal baseline data.

## 6. D256 backward-equivalence — PARTIAL PASS / mandatory gate still open

Reported completed natural tests:

```text
vectorAdd_4M: COMPLETE_VALID
spmv:         COMPLETE_VALID
```

The user/Codex report states their parsed C7e CSV outputs are byte-identical to the formal C7e D256 references. This is directionally exactly what is required for the observation-only histogram generalization.

However, independent GitHub review currently has source and shared-workboard evidence, not the full equivalence artifacts/review pack. Preserve and publish at Lane-B closeout:

```text
cycles
instructions
selected successful DRAM transactions/bytes
selected L2 counts
bank logical/conflict/wait
terminal invariants
CSV/hash comparison result
source/config hashes
```

The mandatory longer case:

```text
scan / B0-Banked D256 equivalence
```

is still running. Do not skip, replace, or interrupt it solely because the two shorter cases pass.

## 7. D512_READY gate

Do **not** declare `D512_READY` yet.

It becomes eligible automatically, without another manual ChatGPT pause, when all Lane-B acceptance gates through the natural preflight are satisfied, including:

```text
scan D256 backward-equivalence PASS
D512 telemetry >256 non-clipping evidence PASS
Release/regression/config-delta gates retained PASS
D512 natural preflight COMPLETE_VALID
no variable other than descriptor capacity changes
```

Then update the shared workboard:

```text
D512-AUDIT     = DONE
D512-PREFLIGHT = DONE/PASS
```

with exact Framework/Core SHA, config hash, and result/review paths. This is the handshake that allows Lane C to consume the exact D512 definition.

## 8. Full D512 mirror

After `D512_READY`, Lane B is already authorized by its target-mode contract to launch the independent:

```text
13 workloads x {B0-Legacy, B0-Banked} @850 MHz
Descriptor = 512
= 26 SPECULATIVE_CALIBRATION runs
```

No manual ChatGPT checkpoint is required between a fully passing preflight and mirror launch.

The mirror remains calibration evidence until `BASELINE-DECISION`; never relabel it as the primary formal baseline on its own.

## 9. Lane-D provenance integration

Lane D's first analyzer revision was reviewed separately and requires an equivalence-aware provenance model before it can compare formal D256 against a different-SHA but backward-equivalent D512 implementation.

Lane B should therefore publish an explicit machine-readable equivalence identity at closeout, for example:

```text
semantic_base_core_sha      = ece1a3a77...
semantic_base_framework_sha = f08d2ce857...
candidate_core_sha          = 878f80869c...
candidate_framework_sha     = aae62b6668...
equivalence_gate            = PASS
equivalence_evidence_path   = ...
allowed_model_delta          = descriptor_pool_size:256->512
```

This gives Lane D a safe way to accept the intended source delta without weakening SHA provenance checks globally.

## 10. Current review conclusion

```text
Core D512 generalization semantics:       PASS
Descriptor allocator boundary behavior:   PASS
D512 config isolation:                    PASS
Runner/campaign labeling:                 PASS
Short D256 backward equivalence:           PASS as reported; retain evidence
Long D256 backward equivalence (scan):     RUNNING / REQUIRED
>256 telemetry non-clipping validation:   REQUIRED before D512_READY
D512 natural preflight:                    NOT STARTED / REQUIRED
D512_READY:                                NOT YET
D512 mirror:                               NOT YET
```

Continue Lane-B target mode. No source issue found that requires stopping Lane A/C or invalidating existing D256 formal data.
