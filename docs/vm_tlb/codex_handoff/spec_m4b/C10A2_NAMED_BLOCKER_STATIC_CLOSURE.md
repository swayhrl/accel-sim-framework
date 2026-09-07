# C10-A2: named blocker static closure

Goal: `C10A2_NAMED_BLOCKER_STATIC_CLOSURE`

Status: `READY_TO_EXECUTE / IMPLEMENTATION_ALLOWED / NO_BUILD_NO_REPLAY`.

## 1. Purpose

C10-A delivered the C9 architectural spine into Core, but ended correctly as
`C10A_IMPLEMENTATION_PARTIAL_WITH_NAMED_BLOCKERS` because the host had only ~76 kB SwapFree and the final Core was never compiled or run.

C10-A2 uses the remaining low-resource window before Window A terminal to close the blockers that can be solved by source/static work without pretending the uncompiled tree is validated.

C10-A2 is not C10-B. It must not build the full simulator, run workloads, start C5, or claim runtime correctness.

## 2. Authoritative inputs

Framework:
- branch: `hrl/vm-m4b-speculative-v0`
- C10-A evidence HEAD: `47840049d6c0ea41748674d4284e7d51d11aad56`

Core:
- branch: `hrl/vm-m4b-speculative-v0`
- C10-A Core HEAD: `c27bf0e2fc5e24c54966426840bd56748ef92028`
- original functional parent: `c21137bcb86010215c008292f272aacefac175d3`

Read first:
- C10-A `FINAL_REPORT.md`
- C10-A `KNOWN_DEFERRED_C10B.md`
- C9 `ARCHITECTURE_DECISION_RECORD.md`
- C9 `WEIGHT_SEGMENT_ARCHITECTURE_SPEC.md`
- C9 `SUBENTRY_EQUAL_BIT_BUDGET.md`
- C9 `FAIR_BASELINE_POLICY.md`
- C9 `C10_IMPLEMENTATION_REQUIREMENTS.md`

External A evidence remains read-only and motivation-only:
- progress-review branch `hrl/vm-llm-m4b-c3-progress-review-20260907`
- early C4 SHA `2e491abec2afb0c745ca26aae0d86f8f35ad096b`

Do not access Window A private worktree/scratch/process and do not calibrate C parameters to A numbers.

## 3. Resource boundary

Window A remains the only simulator-heavy workload.

C10-A2 forbids:
- full or partial simulator build/link;
- Accel-Sim/GPGPU-Sim workload execution;
- C5;
- trace generation/decompression/full scan;
- high-concurrency compilation;
- large file copies/hashes;
- Window A/B process/worktree/scratch changes;
- KV segmentation, 12K, M5.

Allowed:
- source edits;
- grep/source-callgraph audit;
- Python/static validators;
- syntax-only checks that do not invoke a heavy toolchain;
- tiny generated metadata/config checks.

If SwapFree remains near zero or swap-in/out persists, do source/static work only. Do not run even a focused compile.

## 4. Mandatory blocker closure scope

C10-A2 should close B2-B7 from `KNOWN_DEFERRED_C10B.md` as far as possible without runtime execution. B1 and B9 remain runtime validation blockers by definition. B8/F5 may be implemented only after B2-B7 are coherent and only if it can be done without destabilizing the candidate spine.

### A2-0 Admission and source audit

Before edits:
- record Framework/Core HEADs and worktree status;
- enumerate every production call to the translation API and every defaulted `translation_access` path;
- enumerate all parse/install paths for `M4B_WEIGHT_SEGMENT_REGISTRATION_V2`;
- enumerate all sub-entry fill/invalidate/shootdown sites;
- record exact files planned for modification.

No functional edits until this source map is documented.

### A2-1 B2: atomic registration failure must fall back, not abort

Current C10-A parser uses assertions for semantic registration failures. Replace this with a transactional registration admission model.

Required behavior:
- parse into staging state/vector first;
- semantic failures such as >N=8 extents, overlap, ASID/epoch mismatch, non-read-only mapping, invalid mapping class, partial/invalid extent metadata, duplicate or unsorted extent must NOT leave a partially live table;
- on semantic registration failure, candidate registration outcome becomes explicit failure and the entire registration remains inactive; all requests use conventional paging;
- report a machine-readable install failure reason in stats/manifest/review evidence;
- malformed/unreadable configuration file may remain a configuration error if that is consistent with existing project policy, but distinguish infrastructure/schema corruption from a valid driver registration transaction that is rejected by architecture policy;
- no prefix subset of descriptors may become valid.

Prefer a clear `registration_result/status` object or equivalent over scattered bools.

Static tests/validators must cover 9th extent, overlap, bad rights, bad mapping class, ASID mismatch, zero/invalid epoch and no-partial-live-image invariants.

### A2-2 B3+B6: install/revoke lifecycle and per-replica acknowledgements

Implement the C9 pinned-epoch lifecycle as explicit model state rather than immutable constructor copies.

Required conceptual states:
- inactive;
- staging/installing;
- active;
- revoking/quiescing as needed.

Required behavior:
- descriptors become architecturally active only after all local replicas acknowledge the same ASID/epoch/image;
- failed/partial replica installation cannot expose a Segment hit;
- revoke removes eligibility from all replicas before remap/free/context reuse is allowed;
- active ASID/epoch is explicit;
- epoch wrap requires explicit quiesce/global invalidate before reuse;
- install/revoke counters and ack counts are observable;
- local replicas are independent modeled state with identical committed image, not merely copies whose existence is inferred from constructor vector size;
- no silent replacement of a live provisioned ASID; unsupported second ASID falls back conventional according to C9 v1.

This is a functional model lifecycle API/state machine. C10-A2 need not invent a full external GPU driver; a deterministic privileged registration/install/revoke control model is sufficient if its contract is explicit and future runtime plumbing can call it.

### A2-3 B4: production access-class integration

This blocker is mandatory before any replay.

Audit every production translation caller. Do not rely on the READ default for normal simulator execution.

Required behavior:
- real load/read path passes READ;
- store path passes WRITE;
- atomic path passes ATOMIC;
- instruction/PTE/internal translation calls are classified explicitly according to their actual semantic role, not accidentally inherited from a default;
- Segment eligibility remains read-only; write/atomic candidate requests conservatively use conventional paging;
- historical/standard mode behavior must not change merely because the access enum is now explicit.

If a caller lacks enough information at the current API boundary, thread the access class from the nearest authoritative memory instruction/request structure instead of guessing.

Create a source-level callsite ledger showing caller, request class, passed enum and justification.

### A2-4 B5: make fair arms runtime-selectable in configuration/manifest plumbing

C10-A produced the static F0-F9 contract but not execution-ready parser/profile selection.

Without running them, make the configuration path able to represent and validate the official arms:
- F0 baseline exact;
- F1 G96 sub-entry;
- F2 exact bit-matched F1;
- F3 charged exact sweep;
- F4 leaf-capacity diagnostic;
- F5 equal-budget PWC only if model implemented;
- F6 2MiB diagnostic;
- F7 charged Segment+exact;
- F8 Segment+G32;
- F9 exact bit-matched F8.

Requirements:
- manifest exposes actual selected arm ID and realized geometry;
- G96 means 6 sets, G32 means 2 sets;
- Segment profiles expose N=8, replica count, ASID/epoch registration schema, Lseg point and accept-rate contract;
- H0/legacy 768-group can never be selected through the official fair-arm selector;
- F5 must remain hard-invalid/unselectable as an official executable arm until the physical PWC model is actually implemented; static metadata alone is insufficient.

Add validators that reject inconsistent arm/geometry/bit-budget combinations.

### A2-5 B7: sub-entry generation capture / stale-fill protection

Current leaf/group invalidation exists, but fill transactions do not yet bind a translation generation.

Implement an explicit ASID translation generation mechanism sufficient to enforce:
- a miss/walk/fill transaction captures the ASID generation when translation work is admitted/allocated;
- ASID/global shootdown increments/changes generation before stale in-flight fill can commit;
- fill commit compares captured generation against current generation;
- mismatch discards stale fill and cannot resurrect a leaf/group;
- ordinary no-race fill behavior remains unchanged;
- group replacement/leaf fill still use G96/G32 geometry correctly.

Do not fake this by checking only the current group ASID at fill time. The in-flight transaction must carry or otherwise bind the admission generation.

Document how this composes with Segment epoch. They are related invalidation concepts but must not be silently conflated if one is page-translation generation and the other is driver Segment registration epoch.

### A2-6 B8/F5 optional source implementation

Only after A2-1 through A2-5 are coherent, evaluate whether C9 F5 can be implemented safely in source-only mode.

F5 requires a physically interpretable PWC model, not the historical generic 128-entry logical prefix cache:
- three non-leaf levels with 40 entries/level;
- tag/prefix + ASID + next-table PPN/pointer payload + attributes;
- 4-way banks and PLRU accounting;
- explicit port/queue/timing contract;
- manifest budget = 8,370 bits plus 656 exact entries = 64,745 bits.

If completing this would require broad risky surgery without compile feedback, leave B8 explicitly deferred. That is acceptable and must not block completion of A2-1..A2-5.

## 5. Preserve C10-A architecture spine

Do not regress:
- non-identity capable `PA_base + (VPN-VA_base)` mapping;
- registration-based eligibility, not `OBJECT_WEIGHT`;
- local N=8 architecture;
- `HIT_FIRST / MISS_JOIN`;
- only-both-miss lower L2 launch;
- no retry re-probe / no duplicate completion;
- 5/10/20 Lseg plumbing;
- G96 standalone and G32 combined fair sub-entry;
- H0 historical-unfair exclusion;
- cross-layer telemetry continuity.

Source-level changes that would alter C9 decisions require STOP as `C10A2_ARCHITECTURE_CONTRADICTION_REQUIRES_DECISION`; ordinary implementation complexity does not.

## 6. Observability contract

Preserve and extend aggregate telemetry so future C10-B/C5 can explain not only TLB misses but pressure transfer.

At minimum keep:
- Segment attempted/accepted/denied/hit/miss/fallback reason;
- install/revoke attempt/result/ack/epoch;
- L1-first/Segment-first/both-miss/miss-join wait/late discard/mismatch;
- L1/L2 service;
- MSHR alloc/merge/full/wait;
- PWQ/walker/PWC;
- PTE request/response/DRAM/memory wait;
- cross-layer L1D/L2/ICNT/DRAM queue/outcome compatibility.

A early C4 showed that lower TLB misses/MSHR-full can coexist with higher PTE-memory wait and queue pressure. Do not remove or aggregate away the fields needed to detect this in future candidate runs.

## 7. Static verification

No runtime PASS is possible in C10-A2. Still require best-effort static evidence:
- parse/registration transaction validator;
- all production translation callsites classified explicitly;
- lifecycle transition/invariant table or lightweight pure model test if possible without compile;
- F0-F9/H0 selector validation;
- generation-race state-transition validator;
- grep/source assertions that `OBJECT_WEIGHT` is not a functional Segment eligibility gate;
- grep/source assertions that production caller use of default READ is eliminated or limited only to explicitly documented compatibility/test APIs;
- no official selector path to H0.

Do not call source inspection equivalent to compiled correctness.

## 8. Review pack

Create/update:
`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C10A2_NAMED_BLOCKER_STATIC_CLOSURE/`

At least:
- `README.md`
- `INPUT_PROVENANCE.tsv`
- `SOURCE_CALLSITE_LEDGER.tsv`
- `REGISTRATION_TRANSACTION_MODEL.md`
- `SEGMENT_LIFECYCLE_MODEL.md`
- `ACCESS_CLASS_INTEGRATION.tsv`
- `SUBENTRY_GENERATION_RACE_MODEL.md`
- `FAIR_ARM_RUNTIME_PLUMBING.tsv`
- `STATIC_VALIDATION.tsv`
- `REMAINING_C10B_BLOCKERS.md`
- `FINAL_REPORT.md`

## 9. Completion status

Use exactly one:
- `C10A2_STATIC_BLOCKERS_CLOSED_COMPILE_AND_RUNTIME_DEFERRED`
- `C10A2_PARTIAL_WITH_NAMED_STATIC_BLOCKERS`
- `C10A2_ARCHITECTURE_CONTRADICTION_REQUIRES_DECISION`

Even the first status does NOT mean the candidate is runnable or validated. Full build/link, focused runtime regression, cross-layer output inspection and C5 remain forbidden until separately authorized C10-B after resource recovery/A terminal.

Commit coherent changes with explicit paths only. Never use `git add .` or `git add -A`. Push Framework and Core normally; no force push. Then STOP.