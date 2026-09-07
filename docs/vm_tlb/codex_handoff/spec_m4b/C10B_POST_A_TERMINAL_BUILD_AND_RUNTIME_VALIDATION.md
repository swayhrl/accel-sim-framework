# Window C — C10-B post-A-terminal build/runtime validation

Goal: `C10B_POST_A_TERMINAL_BUILD_AND_RUNTIME_VALIDATION`

Status: `PREPARED / NOT_AUTHORIZED_UNTIL_A_TERMINAL_AND_RESOURCE_GATE`.

This document may be read now but must not trigger build, link, simulator, replay or C5 while Window A C3 is still running.

## Authoritative inputs

Framework:
- repo `swayhrl/accel-sim-framework`
- branch `hrl/vm-m4b-speculative-v0`
- C10-A2 static-closure HEAD `447ad52cf867e35a616fa16ab12e32b8914f50b9`

Core:
- repo `swayhrl/gpgpu-sim`
- branch `hrl/vm-m4b-speculative-v0`
- C10-A2 static-closure HEAD `12267bb7ed1dc0257d1d903f6baf7cbdc6ca550e`

Architecture authority remains C9. Retain labels `REFERENCE_APPROX_SUBENTRY_16` and `SPECULATIVE_CANDIDATE`.

## External gate A

Do not start C10-B until an A terminal attestation exists and begins with exactly:

`A_TERMINAL_CONFIRMED`

Expected shared path prepared by A:

`/workspace/m4c-c3-formal-20260905-v1/A_TERMINAL_ATTESTATION.txt`

The attestation means A C3 is terminal; it does not mean resources are healthy.

## External gate B — host resources

Before every compile/test/replay class:

- verify no Window A simulator-heavy process remains;
- sample `MemAvailable`, `SwapFree`, swap-in/out delta and iowait;
- if swap-in/out is persistent, memory is near exhaustion, or iowait is unhealthy, DEFER the heavy step;
- use conservative single-process / `-j1` first;
- do not change A/B process priority or cgroups.

## Ordering is mandatory

C10-B must proceed in this order. Do not jump to C5 or performance replay.

### C10B-0 — compile/link admission

1. Sync exact Framework/Core heads above.
2. Verify worktrees have no unexplained local changes.
3. Compile the current C10-A2 Core **before making any new functional change**.
4. Start with the smallest existing translation/unit target at `-j1`; then perform the required simulator/full link only after focused compile succeeds and resources remain healthy.
5. Ordinary compile/link errors must be debugged against the current delta until root-caused and repaired. Do not add new architecture features while fixing integration errors.

Gate: `C10B_COMPILE_LINK_PASS`.

### C10B-1 — standard-mode regression

Before any candidate runtime claim, prove that C10-A/A2 did not alter accepted modes when new profiles are off.

Run the existing focused M1-M4C/translation regression subset that covers:

- disabled / ideal controls;
- standard exact L1/L2 TLB path;
- MSHR/PWQ/walker/PWC/PTE conservation;
- existing telemetry exact-once invariants;
- historical candidate compatibility only where deliberately retained.

Compare against the accepted pre-C10 baseline evidence and binary/config provenance. Any standard-mode semantic regression blocks all later stages.

Gate: `C10B_STANDARD_REGRESSION_PASS`.

### C10B-2 — execute B2-B7 focused runtime tests

Run directed tests for the source/static closures that were unexecuted in C10-A2.

Registration / PA:
- accepted non-identity PA mapping;
- >8 extents -> atomic semantic rejection -> zero live descriptor -> conventional path;
- overlap/unsorted/rights/mapping-class/ASID/epoch rejection;
- no prefix replica image after rejection;
- conventional PTE translation equals Segment translation for active registered pages.

Lifecycle / replicas:
- `INACTIVE -> INSTALLING -> ACTIVE -> REVOKING -> INACTIVE`;
- no Segment hit before all replica install acks;
- all 35 replica acks required for ACTIVE in F7/F8;
- revoke removes all replicas before reuse;
- second ASID conservatively pages;
- epoch wrap requires quiesce rule.

Access class:
- production READ Weight may use Segment if descriptor matches;
- WRITE Weight is conventional;
- ATOMIC Weight is conventional;
- KV/UNKNOWN remains conventional unless an actually registered descriptor covers the address;
- no functional eligibility depends on `OBJECT_WEIGHT`.

Ordering:
- L1-first owner;
- Segment-first owner;
- L1 miss + Segment hit;
- Segment miss + L1 hit;
- both miss -> exactly one lower L2 launch;
- late result cannot duplicate completion;
- requester retry does not re-probe Segment;
- mapping mismatch triggers correctness failure.

Generation / shootdown:
- in-flight exact fill after generation advance is discarded;
- in-flight sub-entry fill after generation advance is discarded;
- stale waiter/ready outcome cannot resurrect translation;
- Segment epoch and conventional translation generation remain distinct.

Fair-arm runtime selector:
- F0/F1/F2/F3/F4/F6/F7/F8/F9 parse and realize expected geometry;
- F5 is hard blocked until physical PWC exists;
- H0 is permanently rejected by official selector;
- G96 has 6 sets, G32 has 2 sets;
- F7/F8 require 35 SMs, N=8 and Lseg in 5/10/20.

Gate: `C10B_FOCUSED_RUNTIME_PASS`.

### C10B-3 — post-delta telemetry continuity and conservation

Use a tiny/bounded real or directed runtime only; do not start full C5 yet.

Verify emitted runtime output contains and conserves:

Segment:
- attempts / accepts / port denials;
- launch / completion / hit / miss;
- fallback reasons;
- L1-first / Segment-first / both-miss;
- miss-join wait;
- late-result discard;
- mapping mismatch;
- install/revoke attempts and replica acks;
- configured N, replica count, lifecycle state, ASID/epoch and Lseg.

Conventional translation:
- L1/L2 H/M and service;
- MSHR allocation/merge/full/wait;
- PWQ/walker;
- PWC;
- PTE request/response/DRAM/wait;
- generation/stale-fill counters.

Cross-layer:
- keep the existing L1D/L2/queue/DRAM/cross-layer telemetry schema usable;
- explicitly check that a Segment improvement cannot be reported from miss rate alone;
- preserve enough output to detect pressure shifts into requester wait, PTE memory wait, ICNT/L2/DRAM queues as motivated by A early C4.

Gate: `C10B_TELEMETRY_CONSERVATION_PASS`.

### C10B-4 — F5 physical PWC implementation and validation

Only after C10B-0 through C10B-3 pass may F5 be implemented.

C9 F5 contract:
- 120 total entries = 40/40/40 over three non-leaf levels;
- 4-way organization;
- physical pointer payload / level / prefix / attributes as documented by C9 accounting;
- modeled port/queue/timing, not the old free logical 128-entry vector;
- charged total remains within the C9 66,000-bit budget with exact E=656.

If a faithful bounded implementation cannot be completed without reopening architecture, keep F5 blocked and report `F5_DEFERRED_ARCHITECTURE_OR_MODEL`. Do not relabel the old PWC.

Gate: either `C10B_F5_PASS` or explicitly approved `C10B_F5_REMAINS_BLOCKED` before later fair-performance claims involving F5.

### C10B-5 — fair-arm focused sanity

Before C5 full replay, run small/bounded sanity comparisons sufficient to prove each executable arm actually realizes the intended configuration and preserves exact-once frontend behavior.

Do not interpret these bounded results as performance conclusions.

Gate: `C10B_READY_FOR_C5_RESOURCE_GATED_REPLAY`.

## C5 is not automatic

Even if all gates pass, C10-B must STOP and submit a review pack before starting C5 full replay. C5 requires separate approval and a fresh resource gate.

## Required review pack

Create:

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C10B_BUILD_AND_RUNTIME_VALIDATION/`

Include at least:
- `INPUT_PROVENANCE.tsv`
- `RESOURCE_GATE.tsv`
- `COMPILE_LINK_RESULTS.tsv`
- `STANDARD_REGRESSION.tsv`
- `FOCUSED_RUNTIME_MATRIX.tsv`
- `REGISTRATION_LIFECYCLE_RESULTS.tsv`
- `ACCESS_CLASS_RESULTS.tsv`
- `GENERATION_RACE_RESULTS.tsv`
- `FAIR_ARM_RUNTIME_RESULTS.tsv`
- `TELEMETRY_CONSERVATION.tsv`
- `F5_STATUS.md`
- `KNOWN_REMAINING_BLOCKERS.md`
- `FINAL_REPORT.md`

## Final states

Use exactly one:

- `C10B_READY_FOR_C5_RESOURCE_GATED_REPLAY`
- `C10B_PARTIAL_WITH_NAMED_RUNTIME_BLOCKERS`
- `C10B_STANDARD_REGRESSION_FAILED`
- `C10B_ARCHITECTURE_CONTRADICTION_REQUIRES_DECISION`

Commit/push Framework/Core checkpoints with explicit-path staging. Never `git add .` or `git add -A`. STOP after C10-B review pack; do not start C5.