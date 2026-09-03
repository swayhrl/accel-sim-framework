# M4B — paper paging baseline and Segmentation reproduction

Status: **FUTURE CONTRACT / DRAFT ONLY — NOT YET AUTHORIZED**.

Parents:

- `M4_INTEGRATION_TO_SEGMENTATION_MASTER.md`
- `M4I_AB_INTEGRATION_AND_REPLAY.md`
- `M4C_LLM_BASELINE_CHARACTERIZATION.md`

Entry condition: M4I/M4R/M4C PASS.  No Segmentation code may be used to produce
M4C baseline characterization.

This goal reproduces the paper mechanism on the real self-captured prefill and
first-decode traces.  It stops before long-context synthetic-KV injection (M5).

---

# Part A — M4B-P: paging-baseline preparation

## P0 — paper/reference implementation audit

Before implementing L2-TLB sub-entries, inspect all locally available evidence:

- `docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md`;
- the paper/reference ledger;
- any locally retained target-paper PDF/reference list if accessible;
- Accel-Sim/GPGPU-Sim source for an existing sub-entry implementation;
- any source/artifact identified by Track-B M4A research;
- the target paper's reference [4] if its identity/source can be resolved.

Record an evidence table with:

```text
property
value
source
status = PAPER_SPEC / TARGET_REFERENCE / REFERENCE_OTHER_PAPER /
         MODELING_DECISION / UNKNOWN
```

Required properties:

- number of L2 sub-entries per entry;
- base-region alignment/coverage;
- 64KB mapping semantics;
- set/tag/index semantics;
- fill semantics;
- replacement granularity;
- LRU update semantics;
- partial-valid behavior;
- lookup latency/throughput overhead;
- interaction with 2MB pages.

### Authorized fallback if target detail remains unavailable

If the target paper/reference implementation still does not expose exact
sub-entry details, this contract pre-authorizes a clearly labeled
`REFERENCE_APPROX_SUBENTRY_16` model for the **64KB paper baseline only**:

- one L2-TLB set/way entry is a replacement unit containing **16 sub-entries**;
- each sub-entry maps one 64KB page;
- the 16 sub-entries share one base tag corresponding to one **1MB-aligned**
  virtual region;
- sub-entry selector = low 4 bits of the 64KB VPN;
- base-region VPN = `VPN >> 4`;
- if the base tag matches but the selected sub-entry is invalid, count a
  `BASE_TAG_HIT_SUBENTRY_MISS` and execute the normal miss/PTW path;
- fill into an existing matching base tag only validates/updates the selected
  sub-entry and does not evict the other sub-entries;
- if no base tag matches, choose a way using the accepted L2 replacement policy,
  replace the whole group, clear all old sub-entry valids, install the new base
  tag and selected sub-entry;
- replacement/LRU state is maintained at the group/way level and any selected
  sub-entry hit updates that way's recency;
- eviction of a group evicts all valid sub-entry translations in that group;
- L1 TLB remains conventional one-page entries;
- the accepted 768-entry / 16-way L2 organization counts **768 group entries**,
  not 768 individual sub-translations;
- current L2 lookup service latency/port semantics remain unchanged unless
  stronger target evidence requires a different cost.

This fallback is motivated by published Ampere-family GPU TLB reverse
engineering and later GPU sub-entry work, but is **not** target-paper exact.
Any result using it must be labeled:

`PAPER_PAGING_BASELINE_APPROX`.

If P0 finds target/reference evidence that conflicts with this fallback, use the
stronger evidence and update the parameter ledger; do not force the fallback.

Acceptance P0:

- either exact/reference-backed target semantics are frozen, or
  `REFERENCE_APPROX_SUBENTRY_16` is explicitly selected and labeled;
- no UNKNOWN detail is silently converted to paper fact.

---

## P1 — L2 sub-entry implementation

Implement sub-entry behavior as a separable L2-TLB mode.  The accepted generic
M1-M3 conventional L2 mode must remain available and regression-identical.

Suggested modes:

```text
L2_TLB_STANDARD
L2_TLB_SUBENTRY16
```

Do not retrofit sub-entry semantics into L1.

### Required sub-entry statistics

- lookups;
- full sub-entry hits;
- base-tag hit / selected-subentry miss;
- base-tag miss;
- fills into existing group;
- new-group fills;
- group evictions;
- valid subentries evicted total;
- occupancy in group entries;
- occupancy in valid subentries;
- per-object valid-subentry occupancy if C1 attribution is enabled.

Global paper-facing L2 hit/miss must count a lookup as hit only if the requested
sub-entry translation is valid.

### Directed tests

At minimum:

1. 16 consecutive 64KB VPNs in one aligned 1MB region occupy one group and can
   all hit after fill;
2. VPN 16 crosses into a new group;
3. base-tag hit with missing selected sub-entry is a miss, not a false hit;
4. filling one sub-entry does not invalidate siblings;
5. group replacement invalidates all old subentries;
6. LRU update on any subentry hit protects the group as specified;
7. set/way capacity remains 768/16 in the paper config;
8. ASID/page-size class remain part of identity;
9. standard L2 mode remains bit-for-bit/counter regression compatible on
   existing directed tests;
10. no lookup polling/repeated port consumption is introduced.

Acceptance P1:

- all tests PASS;
- M1-M3 standard mode PASS;
- no change to data SimPA semantics;
- sub-entry stats conserve fills/evictions.

---

## P2 — paper paging baseline config

Starting from the M4C paper platform shell, enable the accepted P0/P1 sub-entry
mode and freeze the paper-facing config.

Required paper-known values remain:

- 35 SM;
- 1500MHz;
- 128KB L1/SM;
- 3MB 16-way L2;
- 12 memory channels;
- 32-entry fully-associative L1 TLB;
- 768-entry/16-way L2 TLB;
- 16 walkers;
- 64KB pages.

If I4 proved all formal addresses fit 49 bits, use 49-bit paper-facing VA mode.
If not, do not call this a paper-specific baseline; follow the hard-stop rule in
the parent contract.

Unknown generic parameters such as MSHR/PWQ/PWC/lookup timing remain explicitly
labeled modeling/reference values.

Result label:

- `PAPER_PAGING_BASELINE` only if sub-entry semantics are supported by target
  paper/reference evidence;
- otherwise `PAPER_PAGING_BASELINE_APPROX`.

---

## P3 — paging baseline real-trace validation

Run the same formal prefill/decode1 trace policy selected by M4R.

Compare:

- generic standard L2 TLB;
- paper sub-entry baseline;
- ideal-no-miss diagnostic if implemented.

Record total and Weight/KV/UNKNOWN:

- L1/L2 hit/miss;
- sub-entry group/subentry statistics;
- fills/evictions/replacement matrix;
- MSHR/walker/PWC/PTE traffic;
- requester latency;
- cycles/IPC.

The paper reports a 95.9% short-context weight L2-TLB hit rate at sequence length
64.  Treat it as a reference point, not a pass/fail equality target.  If the
self-captured trace differs materially, investigate trace policy/config/address
coverage before changing parameters.

Acceptance P3:

- formal paging baseline is stable/reproducible;
- no source/config tuning from the desired paper number;
- sub-entry reach effect is measurable or truthfully reported as small;
- all VM conservation invariants PASS.

---

# Part B — M4B-S: Segmentation mechanism

## S0 — segment descriptor contract

The evaluated mechanism segments **model weights only**.  Do not segment KV in
M4B.

Formal descriptor source is the accepted M4A contiguous rank0 Weight allocation
for each ROI.

The formal M3 resident map is identity-like (`SimPA == SimVA`), so a contiguous
Weight SimVA range is also physically contiguous in this simulation model.  This
is a deliberate resident-memory assumption matching the paper's requirement for
virtual+physical contiguity; do not claim it models GPU OS allocation
fragmentation.

### Descriptor fields

Represent at least:

- valid;
- virtual base page;
- virtual limit page, inclusive;
- physical-page offset or equivalent physical base relation;
- optional descriptor/model ID for statistics.

For 49-bit VA and 64KB pages, paper-facing virtual page fields must fit 33 bits.

Recommended arithmetic contract:

```text
VA_page = VA >> 16
segment hit iff base_page <= VA_page <= limit_page
PA_page = VA_page + signed_or_checked_page_offset
PA      = (PA_page << 16) | (VA & 0xffff)
```

The implementation may store wider host integers internally but must assert the
paper-facing field/range contract.

The formal identity-like mapping has page offset 0.  Directed tests must include
at least one non-zero safe mapping offset so descriptor arithmetic is not only
exercised by identity.

If negative offset representation is not specified by the paper and formal runs
do not need it, do not invent a claimed 33-bit signed encoding.  Test positive
or zero offset and document the limitation.

### Segment-table capacity

Make capacity configurable.  Formal workload uses exactly one Weight descriptor.
A default physical table capacity of 8 entries may be used as a
`MODELING_DECISION` because the paper discusses a small number of co-located
models (roughly 2-8) but does not provide a mandatory table size.

Unused capacity must not affect one-segment results.

Reject overlapping valid descriptors as a configuration error.

---

## S1 — parallel Segment + L1 lookup state machine

The paper states the segment lookup can occur in parallel with L1-TLB lookup and
that the L1 result is masked/discarded on a segment hit.

Implement an explicit one-shot state machine; do not bolt a serial segment probe
in front of the accepted TLB path.

### Frozen planned timing model

Until stronger paper evidence is found:

- segment lookup launches in the same cycle as L1 TLB lookup;
- segment lookup has its own logical lookup resource;
- formal default segment service latency = accepted L1 TLB service latency;
- therefore it adds **no serial delay** relative to an L1 hit/miss decision;
- segment throughput must be sufficient to accept the same request launch rate
  as the L1 translation frontend so an invented segment-port bottleneck is not
  introduced in the first reproduction.

This is a `MODELING_DECISION` that implements the paper's stated parallelism
without granting an unexplained extra speedup from a faster segment table.

A later sensitivity may use 1-cycle segment service, but it is not the default
paper-facing result unless evidence supports it.

### Parallel result semantics

At lookup completion:

#### Segment hit

- discard/mask the conventional L1 translation result;
- form SimPA from segment descriptor;
- **do not launch L2 TLB lookup**;
- **do not allocate/merge translation MSHR**;
- **do not start PWQ/walker/PWC/PTE traffic**;
- **do not fill L1/L2 TLB with the Weight translation**;
- allow the data access to proceed exactly once.

The L1 lookup resource may have been consumed in parallel, as described by the
paper.  Keep separate raw parallel-L1 statistics so this activity is not
confused with conventional paging traffic.

#### Segment miss

- reuse the already-completed parallel L1 result;
- if L1 hit, translate normally without extra serial segment latency;
- if L1 miss, continue into the accepted L2 lookup exactly once;
- all existing MSHR/PTW semantics remain unchanged.

Do not restart L1 after segment miss.

### Important counters

Separate:

- segment accesses/hits/misses;
- segment service cycles;
- raw parallel L1 probes on segment hits;
- effective conventional paging L1 accesses after segment filtering, if a
  paper-facing statistic uses that definition;
- suppressed L2 launches;
- suppressed MSHR allocations;
- suppressed walk starts;
- suppressed PTE requests;
- bytes translated by segment;
- hits/misses by object class;
- descriptor ID hits.

Do not report raw parallel L1 misses as conventional L2-TLB misses when the
segment hit prevents the conventional path from proceeding.

---

## S2 — segment registration / object binding

Create an immutable run-specific segment-map input derived from the accepted
Weight sidecar/merge-prep integration manifest.

Per formal ROI record:

- archive SHA;
- sidecar SHA;
- Weight SimVA base;
- Weight size;
- aligned base/limit pages;
- physical base / page offset;
- descriptor-table capacity;
- descriptor count;
- config SHA.

Registration occurs before the first traced inference kernel, modeling the
serving framework/OS setup performed after weight allocation.

Do not use pattern inference from trace accesses to decide the segment range.

A request receives a segment hit only if its full byte interval is contained in
the registered Weight segment.  Boundary-crossing/ambiguous accesses fall back
to paging and are counted explicitly; unexpected formal occurrences require
investigation.

---

## S3 — directed correctness tests

Required tests include:

1. first byte/page of segment hits;
2. last valid byte/page hits;
3. byte/page immediately below base misses;
4. byte/page immediately above limit misses;
5. lower 16-bit offset preserved;
6. non-zero descriptor offset produces expected PA;
7. segment hit does not launch L2/MSHR/PWQ/walker/PTE;
8. segment hit does not fill L1/L2 TLB;
9. segment miss uses the already-completed parallel L1 result and does not
   relaunch/reprobe L1;
10. segment miss + L1 miss launches L2 exactly once;
11. pending/in-flight retries consume neither segment nor TLB resources again;
12. new waiter UID receives its own normal parallel Segment+L1 lookup;
13. two valid non-overlapping descriptors match correctly;
14. overlapping descriptors rejected;
15. segment table persists across ordinary kernels;
16. store/atomic/data side effects exact-once;
17. segmentation disabled is regression-identical to selected paging baseline;
18. non-weight-only synthetic directed trace is cycle/counter equivalent to
   paging baseline apart from explicit segment-miss observability.

Hard STOP if Segmentation changes non-weight translation behavior directly.

---

## S4 — object-causal assertions on real LLM traces

Before performance claims, prove on bounded prefill/decode1:

- formal Weight references have near/all expected segment hits according to the
  frozen Weight range;
- `WEIGHT` conventional L2 launches after a segment hit = 0;
- `WEIGHT` MSHR allocations/walk starts/PTE requests after a segment hit = 0;
- Weight segment physical result equals resident identity-like SimPA for formal
  runs;
- KV/UNKNOWN remain on paging;
- non-weight PTE response association/conservation remains PASS;
- final VM/segment state is quiescent/valid.

Any Weight address outside the registered contiguous range is evidence to
investigate; do not silently grow the descriptor to catch it.

---

## S5 — formal Segmentation real-trace runs

For each formal ROI use the exact same:

- trace policy/list;
- simulator platform config;
- page size;
- sub-entry mode;
- MSHR/PWQ/walker/PWC parameters;
- source baseline;

and change only Segmentation enable/configuration.

Required rows:

1. selected paging baseline;
2. Segmentation enabled;
3. ideal-no-miss diagnostic if available.

For both prefill and decode1 report:

### Performance

- cycles;
- IPC;
- speedup over paging baseline;
- remaining gap to ideal diagnostic.

### Translation

- segment access/hit/miss;
- raw parallel L1 activity;
- effective conventional L1/L2 traffic;
- L2 sub-entry hit/miss/group stats;
- Weight/KV/UNKNOWN L2 misses;
- MSHR allocations/merges;
- walker starts;
- PWC accesses;
- PTE requests and DRAM fraction;
- requester translation latency;
- translation stall/backpressure.

### Capacity/interference

- L2 TLB occupancy/fills/evictions by class;
- replacement matrix before/after Segmentation;
- non-weight L2 hit-rate change after Weight translations stop occupying/filling
  conventional TLB state.

The desired causal chain is:

```text
Weight segment hits
 -> Weight L2/MSHR/PTW traffic disappears
 -> conventional TLB capacity is left for KV/UNKNOWN
 -> translation wait/stall falls
 -> IPC improves
```

Do not force every arrow to be large on B8/S64.  Short-context self-capture may
naturally have less KV pressure than the paper's synthetic 12K experiment.

---

## S6 — paper-reference comparison

Create a comparison table containing target-paper reported reference values:

- short-context Weight L2-TLB hit rate at S=64: 95.9%;
- long-context reported IPC loss up to 62.9%;
- Segmentation IPC 2.51x paging baseline;
- ideal no-TLB-miss IPC 2.69x baseline;
- reported baseline L2-TLB miss rate 91.5%;
- remaining conventional TLB miss rate after Segmentation 17.0%.

For each row mark:

- `DIRECTLY_COMPARABLE_REAL_TRACE`;
- `NOT_COMPARABLE_WITHOUT_SYNTHETIC_KV`;
- `CONFIG/MODEL_APPROXIMATION`;
- measured value;
- delta;
- explanation/evidence.

Do not use the 91.5%, 17.0%, 62.9%, or 2.51x values as tuning targets for
M4B real-trace code/config.

---

# M4B closeout

Create:

- `docs/vm_tlb/review_packs/M4B_PAGING_BASELINE/`
- `docs/vm_tlb/review_packs/M4B_SEGMENTATION_REAL_TRACE/`
- `docs/vm_tlb/review_packs/M4B_CLOSEOUT/`

Stage-specific structured artifacts should include at least:

- `PAGING_CONFIG.tsv`
- `SUBENTRY_VALIDATION.tsv`
- `PAGING_FORMAL_RESULTS.tsv`
- `SEGMENT_DESCRIPTOR_LOCK.tsv`
- `SEGMENTATION_FORMAL_RESULTS.tsv`
- `OBJECT_TRANSLATION_BEFORE_AFTER.tsv`
- `TLB_REPLACEMENT_BEFORE_AFTER.tsv`
- `PAPER_REFERENCE_COMPARISON.tsv`
- `CAUSAL_CHAIN.md`

M4B PASS means:

- selected paging baseline is reproducible and correctly labeled;
- Segmentation semantics are correct and isolated to registered Weight range;
- real prefill/decode1 causal effect is measured;
- no M1-M3 regression;
- no trace/source/provenance mutation;
- paper comparisons distinguish directly comparable real-trace results from
  long-context results requiring M5.

After M4B PASS, commit/push Core + Framework and STOP for ChatGPT review.

Do **not** start in this goal:

- synthetic KV request injection;
- equivalent 12K context pressure;
- segmenting KV;
- new object/phase-aware translation mechanism;
- page faults/migration/UVM;
- MCM/chiplet work.

Those belong to M5 or later.
