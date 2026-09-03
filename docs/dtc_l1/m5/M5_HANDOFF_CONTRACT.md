# M5 Substage Handoff Contract

Status: **ACTIVE — M5 v3 PARALLEL TRACKS**

Primary scheduling authority:

- `M5_V3_PARALLEL_TRACKS_APPROVAL.md`

Paper compute authority remains `M5_V1_APPROVAL.md` + `M5_EXPERIMENT_MATRIX.md` + the ratio-zero policy resolution.

Extended authority:

- `M5_EXTENDED20_APPROVAL.md`
- `M5_EXTENDED20_FORMAL_MATRIX.md`
- `M5_EXTENDED20_HANDOFF_CONTRACT.md`

Graphics authority:

- `M5_GRAPHICS_INDEPENDENT_WINDOW_HANDOFF.md`
- `M5_GRAPHICS_POST_COMPUTE_PLAN.md`
- `M5_GRAPHICS_HANDOFF_CONTRACT.md`

M5 substages are quality/handoff boundaries, not ordinary approval pauses.

## 1. Standard handoff fields

Every compute/Extended handoff records:

1. status;
2. input Core/Framework SHAs;
3. previous handoff/authority anchors;
4. formal behavior anchor;
5. workload/provenance manifest;
6. config hashes;
7. parser/schema version;
8. completed experiment IDs;
9. acceptance checklist;
10. issue/resolution IDs;
11. invalidated/obsolete result IDs;
12. result artifacts/raw-log index;
13. mechanism finding;
14. exact next executable scope;
15. do-not-redo list.

Raw logs, binaries, traces, datasets and build trees remain outside Git.

## 2. Acceptance levels

- `CORRECTNESS_HARD`
- `FIDELITY_HARD`
- `MECHANISM_EXPECTATION`
- `DIAGNOSTIC`

Exact thesis speedups are references, not pass thresholds.

## 3. Paper compute sequence

### M5.0A Anchor

Branch ancestry, Release build/tests, LEGACY/Base/IO/OO sentinels, runtime/toolchain/config identities, resumable registry, safe host concurrency.

PASS -> M5.0B.

### M5.0B Workload recovery

Source-resolve all ten thesis compute workloads, deterministic inputs/output checks, explicit gemv/gemver, gesu/gesummv and conv2d mapping.

PASS -> M5.0C.

### M5.0C Platform fidelity

Actual option/source map, SM count/downstream caps, Tag-bank/coalescer comparability, ratio-zero identity and repaired mismatches.

PASS -> M5.0D.

### M5.0D Metrics

Freeze Figure-4.2 categories/diagnostics, Figure-4.7 live-miss lifecycle/denominator, parser schema and directed counter tests.

PASS -> M5.0E.

### M5.0E Fidelity lock

ATAX/SpMV/2MM/Conv2D triplets plus causal classification. Freeze first formal behavior anchor.

PASS -> M5.1.

### M5.1 Figure 4.2

Ten Base formal runs, paper-equivalent structural stalls plus diagnostics.

PASS -> M5.2.

### M5.2 Figure 4.5 + 4.7

Ten Base/IO/OO triplets, performance, common live misses, GM-CE/GM-PAPER10, weak-result causes, IO/OO evidence.

**M5.2 PASS is also the activation barrier for Extended M5.E2 primary runs.**

After M5.2, execute Paper M5.3-M5.6 while Extended M5.E2/E3 may run in parallel under the shared batch policy.

### M5.3 Figure 4.8

Logical-cache sensitivity 16/32/64 KiB.

PASS -> M5.4.

### M5.4 Figure 4.9

Physical-cache sensitivity 16.5/24/32/40/48 KiB; exact deadlock semantics.

PASS -> M5.5.

### M5.5 Figure 4.10

PIB 32/64/128/192 sensitivity, HOL/concurrency analysis.

PASS -> M5.6.

### M5.6 Paper-10 causal synthesis

Per-workload causal classification using all Paper-10 evidence.

M5.6 PASS is **not** by itself a compute freeze and does not authorize graphics Core integration.

State after Paper M5.6 if Extended is unfinished:

`M5_PAPER10_READY_WAITING_FOR_EXTENDED20`

## 4. Extended track

Use `M5_EXTENDED20_HANDOFF_CONTRACT.md`.

Sequence:

`M5.E0 selection (already approved) -> M5.E1 formalization -> M5.E2 60-run wave -> M5.E3 synthesis`

E1 can prepare source/build/input identities before M5.2.

E2 begins only after M5.2 PASS and uses the same common formal anchor/counters.

Extended simulations must use `M5_PARALLEL_BATCH_POLICY.md`; serial one-workload-at-a-time execution is not the default.

E3 PASS state:

`M5_EXTENDED20_READY_FOR_COMPUTE_FREEZE`

## 5. Compute-freeze join handoff

Create only when:

- Paper M5.6 PASS;
- Extended M5.E3 PASS;
- no unresolved correctness/fidelity issue;
- active compute Core/Framework branches pushed/clean.

Handoff:

`docs/dtc_l1/m5/handoffs/M5_COMPUTE_FREEZE.md`

Required fields:

- `COMPUTE_FREEZE_CORE_SHA`;
- `COMPUTE_FREEZE_FRAMEWORK_SHA`;
- Paper-10 review-pack path;
- Extended-20 review-pack path;
- formal config/parser/behavior anchors;
- 30-workload primary-result membership;
- graphics M5.7/M5.8 research state;
- explicit statement that later graphics integration cannot rewrite compute FORMAL evidence.

State:

`M5_COMPUTE30_FROZEN_READY_FOR_GRAPHICS_INTEGRATION`

## 6. Graphics research/integration handoffs

M5.7/M5.8 may run now in the independent Framework graphics-research branch under `M5_GRAPHICS_INDEPENDENT_WINDOW_HANDOFF.md`.

M5.9+ may run only after `M5.COMPUTE_FREEZE`, on fresh graphics branches created from the freeze SHAs.

Detailed M5.9-M5.12 acceptance remains in `M5_GRAPHICS_HANDOFF_CONTRACT.md` and `M5_GRAPHICS_POST_COMPUTE_PLAN.md`, with M5 v3 dependency overrides.

## 7. Transition rules

At each PASS:

1. finish correctness/fidelity checks;
2. parser/counter sanity;
3. explicit-path commit/push;
4. update the track-owned mutable report;
5. continue when dependencies permit.

A resolve-in-goal issue remains in its active stage: reproduce, classify, repair/reconstruct, regress, invalidate stale identities, continue.

Only a genuine researcher-decision boundary pauses the relevant track.

## 8. Final M5 review states

If source-backed graphics succeeds:

`M5_FULL_REPRO_READY_FOR_REVIEW`

If exhaustive graphics recovery proves formal source-backed graphics unavailable:

`M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

Figure 4.6 fresh area/synthesis remains a separate M6 authorization.
