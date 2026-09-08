# Window C — C11 C5 input/provenance closure

Goal: `C11_C5_PREFILL_PROVENANCE_CLOSURE`

Status: `GOAL_MODE / INPUT_AND_PROVENANCE_ONLY / NO_C5_REPLAY`.

## 1. Why C11 exists

C10B itself is complete and accepted through C10B-5. Current validated identities are:

- Framework evidence closeout: `28edd4e6c59691ea2b766f8221d0b0a1442ff167`
- Core: `5b4094931910cd3bb9b30df47a552eb0ae596983`
- validated binary SHA-256: `74307f3a9b975300e469a7768be1324444c927498e3b19d40d39dc326df31345`
- C9 architecture authority: `04be2899a19b1fe756956dbe5e459494ae1da8df`

C10B-0 through C10B-5 passed. The only C5 preflight blocker is missing full-ROI input/provenance, especially prefill:

1. no C-owned immutable full prefill trace-list;
2. no legal C10 V2 prefill driver registration with non-identity modeled PA;
3. existing `M4B_PREFILL_WEIGHT_SEGMENT_MAP.tsv` is V1 identity-like and may not be used as C10 Segment input.

C11 must close those inputs without changing the C9/C10 architecture and without running C5 performance replay.

## 2. Evidence boundary

C11 may:

- inspect A's frozen C3/C4 provenance and immutable input files read-only;
- import small trace-list/manifests into C while preserving byte-identical hashes;
- create explicit C5 driver-allocation / V2 registration artifacts under the already-approved C9 modeled-PA semantics;
- create validators, C5 arm configs/manifests, exact commands and acceptance rules;
- run tiny/direct validators or bounded mapping sanity tests needed to prove the new artifacts are legal;
- fix B/C-local scripts or config plumbing if the fix is behavior-neutral and does not alter C9 architecture.

C11 must not:

- run full C5;
- alter C9/C10 mechanisms, capacities, timing points or fair-arm budget;
- infer functional eligibility from `OBJECT_WEIGHT` at runtime;
- use V1 identity map as a V2 registration;
- copy decode1 V2 PA values onto prefill;
- guess/tune PA layout based on performance results;
- silently reorder/trim trace lists;
- run KV segmentation, 12K or M5.

Labels remain `SPECULATIVE_CANDIDATE` and `REFERENCE_APPROX_SUBENTRY_16` where applicable.

## 3. Authoritative A full-ROI trace identities

Use A publication checkpoint:

`14edbe200859f6ddf42bc3d459334f184a920a82`

and specifically:

`docs/vm_tlb/review_packs/M4C_C3_TERMINAL_PUBLICATION_CHECKPOINT/C3_FINAL_PROVENANCE.tsv`

A proves the frozen full-ROI trace-list hashes:

- prefill: `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`
- decode1: `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`

All four prefill arms use the same trace-list hash; all four decode1 arms use the same decode trace-list hash.

C11 must locate the actual immutable list files by provenance/hash, not by guessing a filename.

### Trace-list import rules

For both `prefill` and `decode1`:

1. locate the source file used by frozen A C3;
2. recompute SHA-256 and require exact match to the value above;
3. validate every listed trace exists under the frozen immutable trace source and reject path traversal/duplicates unless the original list itself contains them;
4. create a C-owned small trace-list copy or immutable manifest with **byte-identical content**;
5. recompute the C-owned copy hash and require exact equality;
6. record source path, destination path, source commit/checkpoint, trace-list hash, trace-root/archive provenance and kernel count;
7. do not copy huge trace archives unless required; a C-owned immutable list plus provenance-bound read-only trace-root reference is acceptable.

The C5 full-ROI lists must not be replaced by the three-kernel decode correctness list used in C10B.

## 4. Authoritative runtime Weight allocation provenance

A's exact runtime-range map for prefill is:

`configs/vm_tlb/object_maps/M4C_PREFILL_OBJECT_MAP.tsv`

At A checkpoint it records:

- source SHA-256: `08bd106f6597865e622465ee3bd13233f7d49fd1eef131965fd2692956091e7a`
- archive SHA-256: `f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181`
- sidecar SHA-256: `8b605b8b19034613106a61ab993dcab60b6eb34509293074b123b44ceeaa839a`
- runtime Weight VA range: `0x7fd99e000000 .. 0x7fd9da520fff`

The object map is telemetry metadata and **must not itself become the functional C10 registration**. Instead, C11 must locate and bind the underlying runtime allocation/source sidecar that produced this exact range. Verify its hashes and establish that the Weight VA extent is privileged runtime allocation knowledge rather than a post-hoc address classification guess.

Do the same provenance audit for decode1 rather than assuming its bounded C10 registration is automatically the final C5 full-ROI allocation artifact.

## 5. C9 PA semantics and the allowed C5 modeled-driver mapping

C9 explicitly defines a **modeled physical-address namespace**, not measured target-silicon PA. It requires real non-identity translation semantics and a privileged driver-owned pinned mapping; identity fallback is prohibited.

Therefore C11 may create a new C5-specific **MODELED_DRIVER_PA** allocation artifact when the frozen trace capture contains authoritative VA allocation provenance but no captured physical page map.

This is not a claim that the modeled PPNs were measured on hardware. It is a controlled simulation input and must be labeled exactly as such.

### Deterministic PA-layout policy

Use policy name:

`C5_MODELED_PA_HIGH_UNUSED_BIT_V1`

The policy must be performance-independent and reproducible:

1. audit the exact C5 memory-address decoder / partition / bank / channel mapping used by the frozen configs;
2. identify a PA/VPN high bit within the 49-bit modeled PA namespace that is above all address bits materially consumed by the simulated memory placement/hash for these runs, or otherwise prove that setting it leaves all lower placement bits unchanged;
3. require this chosen high bit to be zero across the admitted source VA extent;
4. map each admitted full 64 KiB page with a fixed nonzero high-bit offset so that `PPN != VPN` while page adjacency and lower placement bits are preserved;
5. reject overflow/wrap/overlap or inability to prove the placement property;
6. record the exact chosen bit/offset, decoder audit, policy version and proof in the allocation manifest.

The reason for this policy is to break illegal identity translation while minimizing a new DRAM-placement confound. Do not tune the chosen PA offset by observing performance.

If the simulator consumes additional high address bits not obvious from the config, audit source code and document them before selecting the offset.

## 6. Full-page admission and descriptor construction

Follow C9 exactly:

- base page = 64 KiB;
- admit only full pages wholly inside the privileged Weight allocation;
- leading/trailing partial pages remain conventional;
- read-only only;
- mapping class = pinned contiguous 64 KiB;
- one provisioned ASID;
- nonzero epoch;
- maximum `N=8` extents;
- registration is all-or-nothing.

For each ROI, derive maximal contiguous VPN->modeled-PPN runs from the **driver allocation artifact**, not from dynamic memory accesses.

Generate C5-specific V2 registration artifacts in a dedicated directory, for example:

`configs/vm_tlb/c5_registrations/`

with explicit names for prefill and decode1.

Every V2 registration must record/bind:

- ROI;
- allocation-source SHA;
- trace archive/source SHA where applicable;
- runtime allocation sidecar SHA;
- modeled-PA policy/version;
- ASID;
- epoch;
- descriptor extents;
- read-only/mapping class;
- its own SHA-256.

Do not overwrite C10B bounded correctness registrations.

## 7. Common-PA fairness across C5 arms

A C5 comparison is invalid if Segment arms and conventional arms silently see different physical mappings.

For each ROI, all C5 arms must use the same C5 driver PA allocation:

- F0
- F1
- F2
- F5
- F7
- F8
- F9
- F6 diagnostic if included

Segment-enabled arms may additionally use descriptors to bypass conventional translation, but the conventional page-table result for a registered Weight page must equal the same modeled PPN used by Segment.

C11 must audit current C10 plumbing and prove this property.

Required directed check:

For at least one admitted prefill Weight VA and one decode1 Weight VA:

- conventional-only arm mapping == C5 driver PPN;
- F7 Segment mapping == same PPN;
- F8 Segment mapping == same PPN;
- mappings are non-identity;
- no `OBJECT_WEIGHT` dependency is needed for functional lookup.

If existing configuration plumbing cannot bind the same driver PA map to non-Segment controls, do **not** hide the difference. Treat it as a C11 blocker unless a minimal behavior-neutral input-plumbing fix can be made without changing C9 architecture. Any such code change requires focused regression and a new binary identity before C5 preflight can close.

## 8. C5 arm/config matrix to freeze

Prepare an exact C5 preflight matrix for both `prefill` and `decode1`.

Primary fair matrix:

- F0 baseline exact
- F1 G96 Sub-entry
- F2 exact E688 comparator
- F5 physical PWC + exact E656
- F7 Segment + exact E320 at Lseg=5/10/20
- F8 Segment + G32 at Lseg=5/10/20
- F9 exact E656 no-Segment comparator

Diagnostic:

- F6 homogeneous 2 MiB exact may be included, but label it diagnostic/not equal-cost primary control.

Do not include:

- H0 historical unfair arm;
- historical 768-group C2/C4 data as a fair candidate.

For every ROI/arm point freeze:

- exact config file;
- config SHA-256;
- trace-list SHA-256;
- trace-root/archive provenance;
- driver-allocation SHA-256;
- V2 registration SHA-256 where applicable;
- Framework/Core SHA;
- simulator binary SHA-256;
- Lseg;
- charged bits / realized geometry;
- expected telemetry schema;
- exact command;
- output/resume directory;
- acceptance/conservation checks.

## 9. Preserve validated C10B binary unless code really changes

Preferred outcome: C11 is input/config/tooling only and retains:

- Core `5b4094931910cd3bb9b30df47a552eb0ae596983`
- binary SHA-256 `74307f3a9b975300e469a7768be1324444c927498e3b19d40d39dc326df31345`

If C11 needs a behavior-neutral plumbing code change to express the common driver PA map:

1. checkpoint the exact reason;
2. make the smallest change;
3. rerun affected focused C10B tests plus standard regression sufficient to prove no semantic regression;
4. full-link the new binary;
5. update all C5 preflight identities.

Do not carry the old binary hash forward after code changes.

## 10. Validators / no performance replay

C11 should create machine-readable validators for:

- trace-list exact hash and kernel count;
- trace existence/provenance;
- runtime allocation source hashes;
- modeled PA policy proof;
- V2 registration schema;
- non-identity mapping;
- <=8 extents / no overlap;
- full-page admission;
- conventional vs Segment mapping equality;
- arm config/bit budget correctness;
- command completeness;
- no H0/unfair selector path.

Tiny directed mapping tests are allowed.

Full C5 performance replay is forbidden in C11.

## 11. C11 review pack

Create:

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C11_C5_PREFILL_PROVENANCE_CLOSURE/`

At minimum:

- `INPUT_SOURCE_AUDIT.tsv`
- `A_TRACE_IMPORT_PROVENANCE.tsv`
- `PREFILL_RUNTIME_ALLOCATION_PROVENANCE.md`
- `DECODE_RUNTIME_ALLOCATION_PROVENANCE.md`
- `MODELED_DRIVER_PA_POLICY.md`
- `C5_DRIVER_ALLOCATIONS.tsv`
- `C5_V2_REGISTRATION_MANIFEST.tsv`
- `COMMON_PA_FAIRNESS_VALIDATION.tsv`
- `C5_ARM_MATRIX.tsv`
- `C5_COMMAND_MANIFEST.tsv`
- `C5_ACCEPTANCE_MATRIX.md`
- `VALIDATION_RESULTS.tsv`
- `KNOWN_GAPS.md`
- `FINAL_REPORT.md`

Do not commit large trace archives or raw simulator outputs.

## 12. Problem-solving policy

Goal mode: ordinary path/hash/script/config issues must be solved, not immediately escalated.

Use:

`locate -> hash verify -> root cause -> minimal repair -> revalidate -> continue`

Hard stop only if:

- A full-ROI trace-list hash cannot be reproduced from any immutable source;
- the runtime Weight VA allocation provenance cannot be traced to an authoritative source/sidecar;
- no legal modeled PA policy can be instantiated without changing C9 architecture;
- common PA mapping across fair arms cannot be expressed without architecture redesign;
- evidence is corrupt or internally contradictory.

Do not fabricate missing provenance to avoid a blocker.

## 13. Final states

Use exactly one:

- `C11_C5_INPUTS_CLOSED_READY_FOR_C5_REVIEW`
- `C11_HARD_BLOCKER_WITH_EVIDENCE`

The first state means C5 commands are fully specified and scientifically auditable, **not** that C5 has run.

Commit/push Framework (and Core only if a necessary minimal plumbing fix occurred), then STOP for review. Do not start C5.