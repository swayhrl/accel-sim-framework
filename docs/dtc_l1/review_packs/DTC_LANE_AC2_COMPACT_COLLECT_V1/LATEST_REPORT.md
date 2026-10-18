# Lane AC2 compact raw-sector research — SCIENTIFIC STOP

Original huangrulin-174/root,2026-10-18. **SCIENTIFIC_STOP_RAW_RETENTION_CAPACITY;
COMPACT_NOT_IMPLEMENTED; CPU_PARENT_REGRESSION_AND_CAPACITY_WITNESSES_PASS.**
There is no compact integration, ISA/value, independent AG, application-performance
or hardware/PPA PASS. Full/canary/trace/native/GPU starts, performance UUIDs/new
attempts and old-lock acquisitions: **0**.

## Finding and resulting behavior

Parent AC requires every collected raw sector to remain until successful WB;
original serial service also waits for all collection and cycle>collect_done_cycle.
Serialization removes overlap, not the single instruction's storage requirement.
A real production coalescer/issue/LDST CPU source-API input produces512 required
sectors and256 fully admitted references:16384B raw retention. This exceeds the
proposed two4KiB banks' total8192B even after both old stages drain. At a full
256-sector retained image with sectors_left>0, neither collection nor WB can
advance legally. Finite backpressure alone has no releasing transition.

The witness supports the source/API timing domain, not executed scalar ISA or
real-trace legality. The accepted AC contract conservatively covers the full
640-line source-structural pool; manual640-reference production-LDST stress also
fully admits and drains2560 sectors using parent resources. We do not silently
narrow that domain or infer a smaller, unproved warp-output byte assembly.
A changed source-format bound/output extraction contract is an independent
scientific gate. Under the current accepted raw-retention domain,8KiB plus a
finite-progress fallback is not closed, so implementation stops as authorized.

Compact flag, payload arrays, fallback and compact counters are absent. Only a
CPU test and CMake test wiring were added. Every production file is byte-identical
to parent AC; no source K1/ordinary invalidate, Ref/physical/generation/PIB/waiter/
inflight/return, sidecar, finite quota, cache/statistic, clock or timing comparison
changed. Requesting the unimplemented compact option fails as Unknown Option.
No half-working opt-in or hidden serial80KiB buffer is shipped.

## Immutable identities

Fixed parent Core83aca449135703c176cfab29ae43e1245d00a557 and Framework
134a77798a2502a308c7f1e439a8f39dbc3ee043 were fetched exactly and audited in own
worktrees. AC descends from X2e32afdcf44be3374ff36d22568ed01a075459b6f, whose
direct parent is c0a5e2c31e407c57e3a4af3ce529c921e8059a05.

Published AC2 test-only Core: **835417b37627e46eaaf215f3ff697263c94a18cc**,
branch hrl/iscas2027-dtc-lane-ac2-compact-collect-core-174-v1.
Framework branch hrl/iscas2027-dtc-lane-ac2-compact-collect-174-v1;
executed tools source2a08aee8a5290603c83a0b4f805569762e5ab191; final documentation
publication is separately bound in PUBLICATION_RECEIPT.json/final external audit.
No moving AG integration, AD or AE source is consumed.

All three Core versions have independent builds with assertions enabled, O3,
CUDA11.8 and concurrency<=2. The final AC2 ELF embedded source is835417b3,
modified0.0. New libcudart SHA256:
`e5f035f6e44d6f49aae0fabca064727d421367c4e5120b0508fb1f0881171627`.
New capacity-probe SHA256:
`7daefdee1eea5d78a6d5b273c7a910b0974a13d4202978d958ba977bfe90e119`.
SHA_BINDING binds actual executable/library/loading/linker identities and1939
source files across the three own Core worktrees, before/after unchanged.
No Framework trace binary was built or loaded.

## CPU results and limits

Final CTests:AC2 **9/9** (original7+AC resource+AC2 capacity bound), fresh AC8/8,
fresh X2 7/7. Existing production-LDST matrix reruns80 processes (75 positive,
5 expected unsupported ON aborts).17 OFF/X2 typed-state triples and51 normal
boundaries match;17 paired AC ON cases and51 normal boundaries match parent.
New4/8/16/128/129/256/257/512-sector and manual2560-sector cases add45 positive
production CPU processes with9 additional OFF/X2 and ON/parent state/public
comparisons. All counted Ref/credit/PIB/physical/traffic/ledger and finite service
conservation checks pass. Three LDST microsteps cannot replenish quotas.

The test-local capacity object admits128 exactly, holds both full banks under
WB denial and drains later;129/257/512 over-bound claims reject. These are resource
boundary tests, not a production8KiB fallback PASS. The real normal gpu_print_stat
path retains existing AC/K1 contracts, complete64-SM snapshots/sentinels and16
strict parser negatives. It prints parent160KiB resource capacity, not compact
statistics. Existing sidecar/fence/partial/waiter/K1/old-generation/RFU cases remain
bounded component witnesses. CPU_TEST_MATRIX documents controlled setup/packets,
explicit unused DRAM n_ref initialization, failed engineering receipts and
unimplemented compact cases. No real values/full ISA/coherence/RTL/PPA are proved.

## Cost and next gate

Actual production banks stay2x80KiB =160KiB/SM,10MiB at64SM; **AC2 adds0 bank
bytes relative to parent**, and never claims8KiB production. Proposed compact data
budget is2x4096B =8192B/SM,512KiB at64SM, plus separately unproved control/routing.
The source-API512-sector owner alone needs16KiB raw retention under current rules.
A separate general80KiB serial fallback plus two4KiB banks would cost88KiB/SM;
reusing small banks in an80KiB total fallback still needs another72KiB and reviewed
routing/control. None is implemented or approved. A true compact-output design
requires independently proved extraction/assembly/byte-size and ownership rules;
no free PIB/physical buffer or port is assumed.

AG discovery remains1/8 actually started,0 complete PASS and STOP. AC2 cannot
revive it or replace its AC cells. Future AC2 performance needs a feasible
independently reviewed resource contract, implementation/CPU qualification,
AG2 executor qualification, independent scientific preregistration and new run
authorization. AG_INDEPENDENT_HANDOFF is a public Git negative-evidence handoff,
not private delivery or independent acceptance.

Both repositories' publication receipts verify pushed/fetched HEAD/tree/blobs and
clean worktrees. Earlier Lane sources/raw/worktrees/locks/evidence remain untouched;
raw evidence and all binaries stay only in own paths. The review pack contains all
requested contracts/equivalence/matrix/export/cost/source/SHA/handoff artifacts and
negative receipts. Publication does not authorize any subsequent simulation.
