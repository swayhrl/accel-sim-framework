# EP-L2 Lane E Line-MSHR Causality — ChatGPT Review

Date: 2026-08-30

Review status: **CONDITIONAL PASS — LOCAL CAUSALITY RESULT ACCEPTED, D512 PROMOTION PENDING**

Reviewed pack:

```text
docs/ep_l2/review_packs/LINE_MSHR_CAUSALITY_r1/
```

This review accepts the local implementation/correctness and causal-sensitivity result. It does not yet mark the D512-derived rows `PROMOTED_VALID_CALIBRATION`, because they remain dependent on Lane B `D512_PREFLIGHT_PASS` for the exact frozen D512 candidate.

## 1. Source / isolation / parameterization — PASS

Lane E derives from the frozen Lane-B D512 candidate and does not create an independent descriptor implementation.

The Core delta from Lane B Core `878f80869ce212e779df20b6421e4dc7f987825d` to Lane-E Core `d1f51667a0f2227bcef600c40e22821ac1334c42` changes only `tests/ep_l2/test_descriptor_mshr.cc`; simulator production code is unchanged. Framework changes add isolated MSHR256 config overlays, runner/packaging tooling, and config-diff tests.

The MSHR256 effective-config delta is exactly the L2 Line-MSHR entry field:

```text
A:128:1 -> A:256:1
```

Descriptor pool, per-address cap, L1, WAD, payload, bank, lower queues, scheduler, ReturnQ, frequency and traces remain frozen.

## 2. Line-MSHR256 correctness — PASS

The allocator is already capacity-parameterized. Directed tests cover 127/128/129 and 255/256 entries, exact `EP_L2_BLOCK_LINE_MSHR_FULL`, release/reuse, and terminal zero live state.

The existing occupancy histogram/parser path already represents values above 128, so no production telemetry rewrite was required.

## 3. MSHR128 backward equivalence — PASS

With the final Lane-E source/config infrastructure returned to MSHR128, both required D512 workloads reproduce Lane B byte-for-byte across all seven parsed artifacts:

```text
vectorAdd_4M
convolutionSeparable
```

This is stronger than timing-only equivalence and supports treating the Lane-E source/tooling delta as non-semantic at MSHR128.

## 4. Convolution Descriptor x MSHR 2x2 — PASS locally

The controlled matrix is:

```text
                    MSHR128          MSHR256
D256 descriptors     290,308          290,308 cycles
D512 descriptors     292,211          291,108 cycles
```

D256 has no Line-MSHR-full blocking and is exactly insensitive to 128->256, as expected.

Under D512:

```text
Line-MSHR-full block: 931,416 -> 0
cycles:               292,211 -> 291,108
improvement:          ~0.38%
```

Thus MSHR128 is a real admission ceiling after descriptor relief, but removing that ceiling produces only weak performance response.

## 5. Pressure movement — supports downstream-limited classification

D512 MSHR128 -> MSHR256 changes include:

```text
L2->DRAM full:      2,455,970 -> 2,144,141
scheduler pressure: remains high
L1 MissQ pressure:  1,723,839 -> 2,329,422
WAD full events:        3,407 ->    20,834
native DRAM bus use: ~0.647 -> ~0.649
```

Line-MSHR occupancy is allowed to grow beyond the old ceiling (p95/max 135/158) while traffic and downstream pressure redistribute. The system does not obtain material cycle gain.

Accepted local classification:

```text
MSHR_ADMISSION_THROTTLE_DOWNSTREAM_LIMITED
```

This is stronger than saying the MSHR-full counter is merely an artifact: it is a genuine admission limit. But it is not the dominant ultimate performance limit for convolution under this baseline.

## 6. spmv negative control — PASS

D512 spmv had Line-MSHR max 125 and exact Line-MSHR-full block 0 at MSHR128. Raising capacity to 256 changes neither cycles nor the reported counters:

```text
23,560 -> 23,560 cycles
```

This supports the exact-full-block interpretation and argues against a generic hidden benefit from simply increasing MSHR capacity.

## 7. Implication for RO no-MSHR — conservative

The result weakens a performance motivation framed primarily as "Line-MSHR capacity is scarce and bypassing MSHR allocation will improve performance." In the cleanest observed case, completely eliminating 931,416 MSHR-full blocks yields only ~0.38% improvement because pressure moves elsewhere.

RO no-MSHR can still be scientifically useful if it changes something beyond raw MSHR capacity, for example pending-tag lifetime/flexibility, metadata organization, or interaction with TVD/payload mechanisms. Those mechanisms must not claim expected speedup from the MSHR-full count alone.

Do not promote MSHR256 to the baseline from this result.

## 8. Promotion status

Local gates accepted:

```text
MSHR256-AUDIT:        PASS
D256/M256 control:    PASS
D512 convolution M256 local run: PASS
D512 spmv M256 local run:        PASS
causal interpretation:           PASS locally
```

But the D512 parent and its Lane-E descendants remain:

```text
SPECULATIVE_PENDING_GATE
promotion dependency: D512_PREFLIGHT_PASS
```

If Lane B publishes `D512_PREFLIGHT_PASS` for the exact candidate Core `878f80869ce212e779df20b6421e4dc7f987825d` / Framework `aae62b66685f15437cecf0193934f628e6fac6ae`, promote these exact Lane-E results without rerun and close Lane E as `LINE_MSHR_CAUSALITY_PROBE_COMPLETE` after documentation refresh.

If Lane B supersedes the candidate due a real producer/config/timing defect, invalidate only the D512-derived Lane-E rows and rerun against the superseding candidate.
