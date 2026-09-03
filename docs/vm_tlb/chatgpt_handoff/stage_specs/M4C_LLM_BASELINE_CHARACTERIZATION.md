# M4C — LLM baseline translation characterization

Status: **FUTURE CONTRACT / DRAFT ONLY — NOT YET AUTHORIZED**.

Parent:

- `M4_INTEGRATION_TO_SEGMENTATION_MASTER.md`
- `M4I_AB_INTEGRATION_AND_REPLAY.md`

Entry condition: M4I/M4R PASS on the final integrated Track-A Core lineage and
accepted Track-B formal artifacts.

M4C intentionally contains **no Segmentation** and **no synthetic KV pressure**.
Its job is to establish the actual translation behavior of the captured Llama
prefill/decode1 traces before any optimization is introduced.

---

## C0 — freeze baseline configurations

Create an exact simulator config family with immutable SHA/provenance.

### C0.1 Generic M3-on-LLM baseline

Start from accepted M1-M3 defaults:

- VM enabled;
- real PTE L2/DRAM path;
- 64KB pages;
- L1 TLB 32-entry fully associative per SM;
- L2 TLB 768-entry, 16-way shared;
- 32 translation MSHR entries;
- 32 PWQ entries;
- 16 walkers;
- FINITE-128 intermediate-only PWC;
- L1/L2 TLB service timing 10/80 cycles;
- 56-bit generic VA unless M4I proves 49-bit-safe and an explicitly separate
  49-bit run is selected.

Label:

`GENERIC_M3_LLM_BASELINE`.

### C0.2 Paper-Table-I platform shell

Create a separate config shell matching paper-known platform values where the
simulator exposes corresponding controls:

- 35 SMs;
- 1500 MHz;
- 128KB L1 per SM;
- 3MB L2, 16-way;
- GDDR6 / 12 channels;
- L1 TLB 32-entry fully associative;
- L2 TLB 768-entry, 16-way;
- 16 walkers;
- 64KB page size.

Do not silently replace unknown RTX3070 memory/timing parameters with invented
numbers.  Begin from the retained SM86/RTX3070-compatible config used by M4A
parser smoke, then document every field changed to match Table I and every
remaining field inherited from the simulator/reference config.

Until M4B-P resolves L2-TLB sub-entry support, label this shell:

`PAPER_PLATFORM_SHELL_NO_SUBENTRY`

not `PAPER_PAGING_BASELINE`.

### C0.3 Controls

Retain:

- `CONTROL_VM_DISABLED`;
- `CONTROL_VM_IDEAL_IDENTITY`;
- zero-lookup/fixed-PTW only as `DIAGNOSTIC`, never baseline.

Acceptance C0:

- every config file committed/hashed;
- parameter ledger distinguishes `PAPER_SPEC`, `MODELING_DECISION`,
  `REFERENCE_OTHER_PAPER`, `INHERITED_SIM_CONFIG`, and `DIAGNOSTIC`;
- no parameter tuning from outcome metrics.

---

## C1 — object-aware VM observability only

M4C needs to prove the paper's proposed causal chain, not merely total miss
rate.  Add **observability**, not behavior, for object classes.

### C1.1 Object classes

Required classes:

- `WEIGHT`;
- `KV_CACHE`;
- `UNKNOWN`.

Do not infer `ACTIVATION` or `WORKSPACE` from access patterns unless the formal
capture metadata explicitly identifies a range.  Unidentified traffic remains
`UNKNOWN`.

### C1.2 Metadata input

Create a versioned read-only object-range file derived from the accepted
Track-B merge-prep integration manifest/coverage data.

Per ROI, bind:

- Weight contiguous SimVA range;
- allowed KV ranges for that ROI's temporal snapshot;
- object-map source SHA;
- archive/sidecar SHA that produced it.

The simulator must not parse mutable ad-hoc JSON differently on each run.  Use a
small frozen schema and validator.

### C1.3 Request classification

Classify the actual coalesced memory transaction entering VM translation.

Use the request byte interval, not only its starting address.

Rules:

- whole interval inside Weight range -> `WEIGHT`;
- whole interval inside an allowed KV range -> `KV_CACHE`;
- otherwise -> `UNKNOWN`;
- any ambiguous overlap -> correctness STOP.

Object classification must not affect translation result, lookup order,
replacement, timing, or arbitration during M4C.

### C1.4 Required object-specific counters

At minimum, for each object class record:

#### Requests / pages

- translation requesters;
- unique translation keys encountered;
- L1 lookup launches;
- L1 hits/misses;
- L2 lookup launches;
- L2 hits/misses;
- MSHR joins/merges;
- unique MSHR allocations/walk starts attributable to the object's missing
  translation;
- completed translations;
- requester total latency total/max;
- requester MSHR-wait total/max.

#### Paging work

- PWC accesses/hits/misses associated with walks for that object;
- PTE requests;
- PTE L2-only responses;
- PTE DRAM responses;
- PTE memory-wait total/max.

#### TLB residency/replacement

To establish interference, add non-invasive replacement attribution for L2 TLB
(and optionally L1 if cheap):

- fill count by incoming object class;
- eviction count by victim object class;
- replacement matrix `incoming_class -> victim_class`;
- occupancy snapshots/high-water by class if implementable without changing
  replacement semantics.

A TLB entry's observational object tag must be assigned from the translation
key/range at fill time.  It is metadata only and cannot affect tag match,
replacement victim selection, or timing.

The most important matrix element for the target motivation is:

`KV_CACHE/UNKNOWN incoming -> WEIGHT victim`.

### C1.5 Counter conservation

Add machine-checkable conservation tests.  Examples:

- object-class requester sum equals global classified requester count;
- object-class L2 accesses/hits/misses sum equals the classified subset of
  global counters;
- replacement matrix sum equals observed evictions with known incoming/victim
  classes;
- no walk/PTE work is multiplied by merged waiter count.

Acceptance C1:

- behavior-neutral differential test shows identical cycles/IPC/global VM
  counters with object attribution enabled vs disabled on a fixed trace;
- only new observational statistics differ;
- M1-M3 directed tests remain PASS.

---

## C2 — bounded LLM characterization pilot

Use the primary trace policy selected at M4R, plus `FULL_RANK0` sensitivity when
NCCL exists.

Run bounded representative sections of prefill and decode1 on:

- VM disabled;
- VM ideal identity;
- generic M3 baseline;
- paper platform shell without sub-entry.

The same list/config/provenance must be used within each comparison family.

### Required outputs

For each run record:

- cycles;
- IPC;
- simulated instructions;
- kernels completed;
- wall time;
- memory-reference progress;
- total/object-specific L1/L2 TLB stats;
- MSHR/PWQ/walker pressure;
- PWC/PTE traffic;
- requester latency;
- translation-related backpressure/stall counters available from the M3 path;
- L2 replacement matrix.

Purpose:

- catch integration errors;
- verify object attribution is nonzero and plausible;
- estimate full replay time;
- verify prefill vs decode1 already exhibit distinguishable translation
  behavior if the trace supports it.

Do not tune mechanisms at C2.

---

## C3 — formal real-trace baseline runs

When runtime feasibility is acceptable, execute formal prefill and decode1.

### Primary formal matrix

For each ROI:

1. `CONTROL_VM_DISABLED`;
2. `CONTROL_VM_IDEAL_IDENTITY`;
3. `GENERIC_M3_LLM_BASELINE`;
4. `PAPER_PLATFORM_SHELL_NO_SUBENTRY`.

The first three establish simulator/control causality.  The fourth positions the
workload for M4B-P; it is not yet the paper paging baseline.

If the primary trace policy is compute-only and semantic NCCL exists, also run a
bounded or full `FULL_RANK0` sensitivity according to the M4R feasibility
result.  Never mix its metrics into the compute-only primary row.

### Formal completion definition

A run is formal only if:

- exact archive/list/config/source SHAs recorded;
- normal simulator exit;
- all intended kernels consumed;
- final translation lookup/MSHR/PWQ/walker state quiescent;
- PTE request/response conservation PASS;
- zero response misassociation;
- no duplicate store/atomic/data side effect assertion;
- object-counter conservation PASS.

If a full prefill is too slow but making progress, do not substitute a sampled
result silently.  Follow the master runtime policy and stop with measured ETA if
operationally necessary.

---

## C4 — baseline characterization tables

Create machine-readable CSV/TSV with separate rows for prefill and decode1.

At minimum report:

### Performance

- cycles;
- IPC;
- slowdown vs `CONTROL_VM_IDEAL_IDENTITY`;
- slowdown vs VM disabled where meaningful.

### Translation totals

- L1 hit rate;
- L2 hit rate;
- L2 misses;
- MSHR allocations/merges/full events/high-water;
- PWQ full events/wait;
- walker active high-water / starts;
- PWC hit rate;
- PTE requests;
- PTE DRAM fraction;
- requester translation latency average/max;
- requester MSHR wait average/max.

### Object breakdown

For Weight/KV/UNKNOWN:

- request share;
- requested byte share;
- unique 64KB page footprint from merge-prep/offline analysis;
- simulator L1/L2 access/hit/miss;
- L2 miss rate;
- walk count;
- PTE traffic;
- requester translation latency;
- fill/eviction counts.

### Interference

Report L2-TLB eviction matrix, especially:

```text
incoming KV_CACHE -> victim WEIGHT
incoming UNKNOWN  -> victim WEIGHT
incoming WEIGHT   -> victim KV_CACHE
```

Do not state "KV evicts weights" unless this evidence is actually nonzero or
another direct residency mechanism proves it.

---

## C5 — minimum causality/sensitivity needed before Segmentation

Do not perform a huge design-space sweep.  Run only enough controls to determine
whether observed behavior is translation-capacity related.

Required, on at least one bounded/full ROI with meaningful TLB pressure:

- L2 TLB entries: 256 / 768 / 1536;
- PWC OFF / FINITE-128 / IDEAL;
- walker 4 / 16 if runtime permits;
- 64KB vs 2MB diagnostic if both are valid for the trace/config;
- ideal translation/no-miss control.

This is characterization, not parameter tuning.

Expected questions to answer:

1. Are LLM TLB misses materially larger/different than LUD/BFS?
2. Does prefill differ from decode1?
3. What fraction of paging pressure comes from Weight vs KV vs UNKNOWN?
4. Are weight translations being evicted by non-weight traffic?
5. Are MSHR/walker/PTE resources on the critical path or is TLB capacity alone
   dominant?
6. Does increased TLB reach reduce the same stalls that Segmentation is meant to
   remove?

If the real B8/S64/G3 traces show little/no KV pressure, state that directly.
Do not manufacture long-context pressure in M4C.

---

## C6 — characterization closeout gate

Create:

`docs/vm_tlb/review_packs/M4C_LLM_TRANSLATION_CHARACTERIZATION/`

Required stage-specific artifacts include:

- `BASELINE_CONFIG_MATRIX.tsv`
- `FORMAL_RUN_MATRIX.tsv`
- `OBJECT_VM_STATS.tsv`
- `L2_TLB_REPLACEMENT_MATRIX.tsv`
- `LATENCY_SUMMARY.tsv`
- `CAUSALITY_SWEEP.tsv`
- `TRACE_POLICY_COMPARISON.tsv` when NCCL exists
- `CHARACTERIZATION_FINDINGS.md`

`CHARACTERIZATION_FINDINGS.md` must separate:

- measured fact;
- inference supported by counters;
- paper comparison;
- unresolved unknown.

M4C PASS does **not** require matching the paper's 91.5% long-context L2 miss
rate or 62.9% IPC loss, because those reported pressure points use synthetic
long-context KV injection that is intentionally outside M4C.

M4C PASS means the real prefill/decode1 baseline is trustworthy enough to begin
M4B paper-baseline/Segmentation work.

On PASS, continue automatically to M4B-P under the parent goal unless a hard
STOP condition was triggered.
