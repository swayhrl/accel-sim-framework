# M5 Conventional-L1 Dirty-Victim Policy Resolution

Status: **RESEARCHER-APPROVED M5 v1 REFINEMENT — RESUME M5.0B AFTER VALIDATION**

Decision date: 2026-09-03.

This file resolves `M5-T005`, the researcher-decision boundary caused by the inherited SM7 `-gpgpu_l1_cache_write_ratio 25` policy at the M5 paper-facing 16 KiB conventional L1 geometry.

It is an authoritative M5 v1 refinement for conventional-L1 dirty-victim policy. It does **not** change the frozen DTC architecture, the researcher-frozen 16 KiB Base geometry, Figure 4.7 metric, or Figure 4.2 category definitions.

## 1. Researcher decision

For all **paper-facing M5 formal configurations** that instantiate the conventional L1D policy surface — including LEGACY, PAPER_BASE, PAPER_IO, PAPER_OO, all cache-preference variants, and later Figure 4.x sensitivity configs unless a sensitivity explicitly studies this policy — set:

```text
-gpgpu_l1_cache_write_ratio 0
```

explicitly.

Keep the existing cache write policy and allocation semantics unchanged. In particular, do **not** change the configured `WRITE_THROUGH` policy, `LAZY_FETCH_ON_READ` policy, LRU replacement policy, line size, associativity, capacity, MSHR semantics, pending-write/scoreboard semantics, or DTC read backend merely to resolve this issue.

Do **not** modify `tag_array::probe` to add a new fallback replacement rule for the formal M5 baseline unless a later source-backed issue independently requires such a change. The approved resolution is a configuration-policy correction, not a new cache replacement implementation.

The inherited value `25` remains useful as a **DIAGNOSTIC_PLATFORM_POLICY** control only. Results produced with ratio 25 after the 16 KiB geometry correction are not paper-facing FORMAL data and must not substitute for ratio-0 runs.

## 2. Scientific/source basis

### 2.1 The 25% threshold is inherited platform calibration, not a frozen DTC mechanism

M5-T005 established that the 16 KiB four-way cache can have all four ways of one set in `MODIFIED` state before global dirty occupancy reaches 25%. Current `tag_array::probe` treats a modified line as replacement-eligible only when the global dirty percentage has reached `m_wr_percent`. Thus the inherited 25% threshold can leave a set with no eligible victim and make the request retry forever.

This behavior is reproduced in both PAPER_BASE and LEGACY, so it is not caused by DTC PIB/Tag/ref-count semantics.

### 2.2 Source default is zero

The GPGPU-Sim cache configuration object initializes `m_wr_percent` to zero, and the option parser registers `-gpgpu_l1_cache_write_ratio` with default `0`. Therefore ratio 25 is not required by the generic cache model; it is an explicit tested-GPU configuration choice inherited from the Volta/SM7 platform.

### 2.3 Write-through correctness does not require retaining MODIFIED lines until 25%

The formal inherited L1 configuration is write-through. In the source, a write-through hit marks the local line/sector `MODIFIED` for local cache state/readability bookkeeping **and sends the write request to the lower level immediately**. The lower level therefore does not depend on later eviction of that local MODIFIED line to receive the store.

The thesis background likewise describes GPU L1 data caches as normally using a write-through policy and does not specify a 25% global dirty-retention threshold for the Chapter-4 conventional 16 KiB baseline.

Consequently, using the source-supported ratio-0 policy is the least invasive paper-facing interpretation: it preserves write-through behavior and permits ordinary LRU replacement of modified local lines instead of importing an unrelated Volta dirty-retention heuristic that deadlocks at the paper geometry.

## 3. Formal-data disposition

After this decision:

- the frozen Base geometry remains **16 KiB, 128B line, 4-way**;
- PAPER_BASE PIB remains 8 and traditional L1 MSHR remains 32;
- PAPER_IO/PAPER_OO paper-mode defaults remain unchanged;
- all paper-facing modes use the same explicit conventional-L1 write ratio `0` wherever that source policy applies;
- the corrected ratio-0 config hashes become part of the M5 formal identity;
- any 16 KiB ratio-25 run is `DIAGNOSTIC_PLATFORM_POLICY` / non-formal for Figures 4.2-4.10;
- existing 32 KiB and 128 KiB ratio-25 jobs may finish and be retained as diagnostics, but they cannot replace the frozen 16 KiB formal run or define the paper-facing policy.

Do not terminate already-running diagnostic jobs solely because of this decision. Subject to the M5.0A calibrated host-concurrency limit, corrected ratio-0 work may start without waiting for those diagnostics to finish.

## 4. R5DV recovery/validation sequence

Codex must close this decision with source-backed validation before treating M5-T005 as resolved.

### R5DV.0 — Preserve and classify pre-decision evidence

- Preserve the exact ratio-25 SpMV LEGACY/PAPER_BASE deadlock evidence and config hashes.
- Preserve any still-running 16/32/128 KiB jobs and classify their eventual results by their actual config identity.
- Do not rewrite prior evidence as if it had used ratio 0.

Acceptance: M5-T005 retains a reproducible pre-decision causal record.

### R5DV.1 — Update the complete formal config family

Set `-gpgpu_l1_cache_write_ratio 0` explicitly in:

- LEGACY formal base config;
- PAPER_BASE formal base config;
- PAPER_IO formal base config;
- PAPER_OO formal base config;
- `PrefL1` / `PrefShared` source-reachable cache variants through the same global policy option;
- any generated Figure 4.x configs derived from the formal base.

Do not change other architecture/timing knobs in the same semantic change unless an independently documented fidelity issue requires it.

Acceptance: strict config-diff evidence proves dirty-victim ratio is the only intended policy change from the corrected 16 KiB config family.

### R5DV.2 — Directed dirty-set replacement regression

Create a deterministic source-level/runtime regression that exercises the real conventional L1 path:

1. populate all ways of one target set with locally `MODIFIED` lines under the write-through policy while global dirty occupancy is below 25%;
2. access another line mapping to the same set;
3. under ratio 0, require forward progress and a legal replacement rather than permanent `RESERVATION_FAIL`;
4. require application/data correctness;
5. require no pending-write/scoreboard/accounting leak;
6. verify that write-through stores were already sent to the lower level and that eviction does not fabricate an additional write-back requirement solely to compensate for this policy change.

A ratio-25 run may be retained as a negative diagnostic showing the inherited starvation condition; it is not required to be made to pass.

Acceptance: ratio-0 conventional L1 replacement is source-correct and forward-progressing with no weakened assertions.

### R5DV.3 — Canonical SpMV recovery

Rerun canonical Parboil JDS SpMV `medium` (`bcsstk18`) with the corrected 16 KiB ratio-0 configs.

At minimum first require:

- LEGACY completes without the dirty-set no-progress failure;
- PAPER_BASE completes without that failure;
- official/wrapper output check passes;
- no deadlock/assertion/pending-write/scoreboard failure;
- final L1/DTC/lower accounting drains as applicable;
- dynamic operation identity remains valid.

If another source-reachable issue appears, treat it through `M5_PROBLEM_RESOLUTION_POLICY.md`; do not restore ratio 25 or enlarge L1 as a shortcut.

PAPER_IO/PAPER_OO use the same ratio-0 platform policy and are exercised by the normal M5.0E/M5.2 triplets; Codex may run an earlier SpMV IO/OO smoke when efficient for regression.

### R5DV.4 — Regression and formal-anchor/config refresh

Run at least:

- release build;
- all DTC CTests;
- LEGACY/PAPER_BASE/PAPER_IO/PAPER_OO VecAdd sentinels using ratio-0 configs;
- the M4 mixed Store/Atomic/`.cg` bypass sentinel if the formal config change reaches those paths;
- `git diff --check`.

Update:

- formal config hashes;
- result registry identities;
- M5 workload/config manifests;
- `M5_CONFIG_KNOB_MAP.md` when M5.0C reaches its normal closeout;
- `implementation/M5_ISSUE_LOG.md` M5-T005 state and evidence.

Any ratio-25 candidate previously marked FORMAL must be invalidated. Diagnostic results remain preserved with explicit classification.

### R5DV.5 — Resume continuous M5

After R5DV.0-R5DV.4 pass, close M5-T005 and resume M5.0B from its prior checkpoint. Do not redo already source-verified workload provenance or completed valid work unnecessarily.

Then continue the already-authorized sequence automatically:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`.

No additional human authorization is required merely because a corrected ratio-0 workload exposes an ordinary resolvable implementation/workload/platform issue.

## 5. What still requires researcher review

Pause again only at the normal `RESEARCHER_DECISION_REQUIRED` boundaries in M5 policy, for example if:

- ratio 0 still cannot produce a source-correct conventional-L1 execution and the only proposed fix changes frozen architecture semantics;
- a second scientifically distinct dirty-victim policy must be chosen for the paper-facing baseline rather than diagnosed as supplemental sensitivity;
- or another issue reaches an irreducible researcher-decision boundary.

Do not pause merely because performance changes substantially after removing the inherited ratio-25 heuristic. That performance difference is itself part of the platform-fidelity evidence and should be analyzed, not tuned away.
