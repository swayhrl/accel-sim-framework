# Agent C: Physical × OO PIB co-design, CPU only

This package prepares two parameter combinations on all eight frozen inputs: Physical768 + OO PIB192 and Physical1024 + OO PIB192. The sixteen PLAN rows have no registered request, UUID, budget or model launch. V1, its 102 source pins, the production Core, owner and services are unchanged.

`C_RESOURCE_CODESIGN_MATRIX.json` contains the complete resource matrix: Physical640/768/1024 × OO PIB128/192, with eight inputs per cell. It retains P0, every V1 single-factor result or missing state, and the two unrun combinations. Each candidate contains its full input identity, four configuration SHAs, all 270 expected options, build and runtime library identities, deterministic proposed native name, legal CH/DH-P0 references, single-factor sources and advisory resource limits. Proposed native names are strings for future registration, not consumed identities. New cycles, speedups and J are all null.

Configuration and source facts
------------------------------

Only two effective DH-P0 options change: `-gpgpu_dtc_l1_physical_lines` becomes768 or1024, and `-gpgpu_dtc_l1_oo_pib_entries` becomes192. Configurations0–2 are byte-identical to the original DH-P0 files; configuration3 appends these two overrides. Complete expected options are derived from DH-P0, never from the included CH reference. Canonical P0 specification and four-file SHA receipts are recorded in `CONFIG_QUALIFICATION.json`.

PIB192 changes both active OO instruction slots and the lower-create candidate queue from128 to192. The512 lookup Tags do not grow with the physical pool. Physical768 and1024 add20% and60% nominal128B identity capacity; PIB and its coupled queue add50% depth. These quantities are declared model accounting, not evidence of a128B value array, RTL SRAM, area, frequency, power or free hardware cost.

Finite service remains fixed: create, inject, refill and retire quotas are one per SM tick; collection permits four32B sectors and the frontend notifies four waiters per tick. Shared operand writeback must still grant. Tag quotas remain four banks, one request per bank and four total. More pool or PIB capacity cannot guarantee more throughput, and V1 Tag2/8 observations are not combination results. Exact source anchors and Git/blob hashes appear in `SOURCE_AND_COMPLETION_SERVICE_EVIDENCE.json`.

CPU evidence and its limits
---------------------------

The actual checks comprise66 configuration/source checks,83 combination-shape checks,19 original-header positive cases and two expected original-assertion aborts. These are finite CPU checks, not170 scientific experiments. Header tests used one free CPU511 at nice10, with1GiB child address-space limit, and finished in about1.84seconds. They compiled the fixed production header without changing it.

Every resource shape exercises sequential replacement and generation reuse; full PIB sharing, deduplication, finite notification and slot generation; and full physical occupancy followed by real returns, eligible old-entry retirement and renewed admission. A separate case checks service quotas and collection edges. The single unallocated cacheable instruction is never incorrectly retired through the bare header's empty-entry readiness: explicit eligible old UIDs respect the production single-dispatch partial-allocation guard. Multiple-partial bare-API scenarios are not called production deadlocks. Lower responses, service advancement and eventual writeback fairness remain assumptions. PASS is not a universal liveness theorem or complete application/numerical correctness proof.

The new combination shape adapter checks the complete270-option contract, actual configuration bytes, input/ROI, binary and libcudart identities. The unchanged V1 single-factor shape validator rejects these combinations, as expected. A private legacy parser changes exactly one terminal physical-allocation bound and reverse substitution restores all original bytes. Every other population and lifecycle check remains intact. The pinned existing population comparator supplies the full270 echo comparison; the historical AG6 top-level scientific entrypoint, which fixes128/640 and AE/AD identities, is not called.

There is no accepted combination raw log, so actual native entry, runtime binding, guard, natural termination, complete strict acceptance and archive/native restoration remain future qualification. Configured192 is not a measured PIB or queue peak. Missing counters remain missing; terminal PIB, references, inflight requests and lower outstanding must still drain to zero.

Evidence and future statistics
------------------------------

V1 evidence is the immutable11-accepted snapshot20261104T155603_725e5ee5, provider ebf0e09… and manifest12313cd…. MVT's Physical768 improvement and BICG's accepted regression both remain in the matrix, alongside zero responses and missing factors. VectorAdd currently has both single-factor components for the two combinations, but even its J remains missing until a real combination result exists.

Future S_combo = DH0/newDH, R_combo = CH0/newDH and J = S_combo/(S_physical × S_PIB) require exact matched qualified sources. J needs DH0, both single factors and the combination; R additionally needs CH0. J greater than one means supra-multiplicative gain relative to those factors, not best absolute performance or cost. Uniform-profile, suite, common-input and coverage rules prohibit choosing a best variant per program or extrapolating this eight-program set to32/35 programs.

Next authority boundary
-----------------------

The main pending Goal is referenced by path/SHA in `ROOT_NEXT_CONTRACT_REFERENCE.json`; C's exact mapping and integration requirements are in `NEXT_EXECUTION_CONTRACT_REQUIREMENTS.md` and `FUTURE_RUNTIME_WRAPPER_REQUIREMENTS.json`. These fixed-Core combinations do not wait for or authorize a new Tag/reclamation mechanism. Root can defer a whole ineffective or unsafe family after V1 direction review while retaining every fixed row; individual speedup selection is forbidden.

This CPU-only work stops at scientific execution approval. Existing source/capture ELF, HtoD/coherence and native numerical validity limits remain unproven. Englishv0.23 is unchanged. Reproduce CPU checks in a new output namespace; do not rerun helpers into this frozen evidence directory.
