# DTC FAST64 Acceptance Contract

Status: **HARD GATES ACTIVE**

This file defines the non-negotiable completion standard for every FAST64
stage. A stage may checkpoint/push and advance automatically only after all
HARD requirements are satisfied. SOFT items are desirable but may not block
progress when their absence does not affect correctness, fidelity, or the
scientific claim.

General meanings:

- `CORRECTNESS_HARD`: wrong behavior, broken accounting, trace corruption,
  assertion/fatal/unclassified deadlock, output mismatch, or incomplete drain
  blocks acceptance.
- `FIDELITY_HARD`: workload/input/platform/result identity drift blocks
  acceptance.
- `REPRODUCIBILITY_HARD`: required SHA/config/result provenance must exist.
- `EFFICIENCY_SOFT`: scheduling/runtime improvements should be pursued but may
  not alter scientific meaning.

## FAST64.0 — Pivot and evidence freeze

### HARD acceptance

- Framework branch descends from `a9cdb3328a346cbc9a76b7ffadae3725b4209ab5`.
- Core authority distinguishes the mechanism behavior anchor
  `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` from the formal instrumented Core
  `bbcbb5e7565417102087bc80b14c349b4e568c05`.
- Existing M5 evidence is classified into Tier A/B/C without deletion or
  relabelling.
- 2MM and SYR2K primary-path work is marked
  `DEFERRED_HEAVY_AUXILIARY`, not failed and not silently discarded.
- Existing large 80-SM ATAX is marked background auxiliary stress only.
- FAST12 membership is frozen before any FAST64 IO/OO performance is observed.
- Old M5 contracts remain historical authority for their own results; FAST64
  does not rewrite their identities.

### PASS artifact

`handoffs/FAST64_0_PIVOT.md`

PASS state: `FAST64_0_PIVOT_PASS`

## FAST64.1 — Platform and payload lock

### CORRECTNESS_HARD

- Base/IO/OO resolved configs build and launch successfully.
- `nn` and `bicg` smoke runs reach natural termination in all required modes or
  any workload-specific unsupported behavior is source-classified and repaired.
- No assertion, fatal, output mismatch, trace parse error, or unclassified
  deadlock.
- Terminal Base/IO/OO accounting drains to zero/balanced state.

### FIDELITY_HARD

- 64 x 1 endpoint shell is explicitly verified.
- DTC Base remains 16-KiB/4-way/128-B, PIB 8, MSHR 32.
- IO/OO retain 16-KiB logical tag capacity, 80-KiB/640-line physical pool,
  PIB 256/128, four tag banks, and DTC source semantics.
- C2P's 64-KiB/32-way L1 and peer-cache mechanisms are absent.
- One machine-readable resolved-config diff classifies every Base/IO/OO
  difference. Zero unrelated differences remain.
- FAST12 exact payload roots and ordered member hashes are frozen.
- No membership/input changes occur after observing DTC performance.

### Lower-cap HARD qualification

For candidate cap 8192 versus high non-binding cap on the required cases:

- identical final cycles;
- identical final instructions;
- identical strict-parser scientific fields;
- zero cap-full stalls at 8192;
- identical terminal lower/accounting state.

If 8192 fails, choose the smallest pre-performance common cap that passes the
same test. Record why. Do not optimize cap for speedup.

### REPRODUCIBILITY_HARD

Record:

- mechanism behavior-anchor SHA and formal instrumented-Core SHA;
- Framework SHA;
- runtime binary SHA;
- resolved Base/IO/OO config SHA-256;
- observer overlay SHA;
- each FAST12 payload identity.

### PASS artifact

`handoffs/FAST64_1_PLATFORM.md`

PASS state: `FAST64_1_PLATFORM_PASS`

## FAST64.2 — Repair qualification

### CORRECTNESS_HARD — normal triplet

A natural-terminal FAST64 Base/IO/OO triplet must satisfy:

- exit status zero;
- strict parser PASS;
- same expected trace payload consumed;
- no assertion/fatal/output mismatch/unclassified deadlock;
- Base PIB/lower state drains;
- IO/OO PIB/inflight/lower state drains;
- OO active-ref/reclaim state drains;
- lower create/issue/response conservation;
- dependency create/complete conservation.

### CORRECTNESS_HARD — forced queue-full stress

The diagnostic must deliberately observe:

`DTC_L1_io_lower_create_queue_full_stalls > 0`

and/or

`DTC_L1_oo_lower_create_queue_full_stalls > 0`.

Despite repeated queue-full events it must:

- never hit the old post-allocation assertion;
- make forward progress;
- naturally terminate;
- preserve lower create/issue/response conservation;
- preserve dependency conservation;
- finish with PIB/inflight/lower current state zero;
- finish OO active refs zero where applicable.

The queue-full stall must be classified as MissQueue/lower-capacity pressure in
paper-facing accounting; it must not be silently counted as Tag-bank conflict
merely because an internal retriable stall code is reused.

### FIDELITY_HARD

The forced-stress overlay is diagnostic only and is never included in FAST64
performance aggregates.  It may be physically acquired before FAST64.1 PASS
only as `PRECOMPUTED_FAST64_2_DIAGNOSTIC_PENDING_FAST64_1_ACCEPTANCE`; that
classification cannot be promoted or used to advance FAST64.2 before every
FAST64.1 HARD gate passes.

### PASS artifact

`handoffs/FAST64_2_REPAIR_QUALIFICATION.md`

PASS state: `FAST64_2_REPAIR_PASS`

After PASS, the existing large 80-SM ATAX natural triplet is optional
auxiliary confirmation and no longer blocks FAST64.

## FAST64.3 — Base-only characterization

### CORRECTNESS_HARD

All 12 frozen FAST12 Base rows must:

- naturally terminate;
- strict-parse;
- consume the frozen payload identity;
- have valid terminal accounting;
- have no unclassified correctness failure.

A source/workload incompatibility must be repaired or explicitly classified.
Substitution/removal requires a researcher decision because membership is
frozen.

### FIDELITY_HARD

- IO/OO physical acquisition may exist only with an explicit
  `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` classification.  It must not be
  consulted to alter FAST12 membership, inputs, or Base-characterization
  decisions before FAST64.3 PASS.  Main-matrix IO/OO precomputation begins only
  after FAST64.2 repair PASS.
- All 12 remain in the primary roster regardless of structural pressure.
- Same frozen Base platform/config identity is used except documented
  workload-independent trace-frontend necessities.

### REQUIRED METRIC COMPLETENESS

Every row must provide parser-valid values or an explicit unsupported-field
classification for:

- cycles/instructions;
- PIB pressure;
- Tag/cacheline allocation pressure;
- MSHR pressure;
- lower/downstream pressure;
- live-miss lifecycle;
- available cache/traffic fields;
- host wall/cpu/RSS planning data.

### PASS artifact

`handoffs/FAST64_3_BASE_CHARACTERIZATION.md`

PASS state: `FAST64_3_BASE_PASS`

## FAST64.4 — Primary Base/IO/OO matrix

### CORRECTNESS_HARD

All 36 primary rows must be valid, with Base rows reused from FAST64.3 when
identity matches exactly.

Each triplet requires:

- same payload identity across Base/IO/OO;
- same unrelated platform configuration;
- one common observer identity across the triplet;
- natural terminal exit zero;
- strict parser PASS;
- same dynamic instruction/source-domain operation identity where the model
  contract requires equality;
- no assertion/fatal/output mismatch/unclassified deadlock;
- exact terminal accounting/drain.

### FIDELITY_HARD

- No workload is removed for weak/negative performance.
- No per-workload DTC resource tuning.
- No input/trace replacement based on observed speedup.
- Only frozen mechanism-required Base/IO/OO parameters differ.

### REPRODUCIBILITY_HARD

Each row records a formal identity tuple and raw-log reference.

### PASS artifact

`handoffs/FAST64_4_PRIMARY_MATRIX.md`

PASS state: `FAST64_4_PRIMARY_PASS`

## FAST64.5 — Causal analysis

### CORRECTNESS_HARD

- Every FAST12 workload has one accepted Base/IO/OO triplet.
- Structural categories reconcile to source-backed events.
- Tag-bank arbitration remains separate from true Tag/cacheline allocation
  failure.
- live-miss create/complete conservation is valid.
- no unresolved implementation/modeling correctness issue is hidden as a
  scientific result.

### FIDELITY_HARD

Every workload receives a causal classification, including negative and
near-zero beneficiaries.

At minimum classify among:

- conventional-structure limited;
- low structural pressure;
- downstream/platform limited;
- compute/reuse dominated;
- traffic sensitive;
- IO-HOL sensitive;
- OO-reclaim sensitive;
- genuine mechanism non-beneficiary;
- implementation/modeling issue (must be resolved before PASS).

### REQUIRED OUTPUTS

- `fast12_summary.csv`
- `fast12_stalls.csv`
- `fast12_live_misses.csv`
- `fast12_traffic.csv`
- `fast12_io_oo.csv`
- paper-facing plots or plot-ready data;
- `GM-FAST12` with exact membership.

### PASS artifact

`handoffs/FAST64_5_CAUSAL_ANALYSIS.md`

PASS state: `FAST64_5_CAUSAL_PASS`

## FAST64.6 — Sensitivity

### FIDELITY_HARD

Sensitivity workload roster is frozen as:

- BICG;
- GESUMMV;
- Btree.

Do not replace based on FAST64.4 benefit.

### CORRECTNESS_HARD

Every retained sensitivity row must satisfy the same natural-terminal,
parser, payload, and accounting rules as FAST64.4.

Physical-capacity points must map to explicit whole-line counts. Any rounded
capacity label must state both requested KiB and actual modeled lines/bytes.

### INTERPRETATION_HARD

Sensitivity is one-dimensional:

- logical-cap sweep changes only logical capacity;
- physical-cap sweep changes only physical pool capacity;
- PIB sweep changes only PIB capacity plus unavoidable mechanism-consistent
  bookkeeping.

No multi-parameter tuning to improve the curve.

### PASS artifact

`handoffs/FAST64_6_SENSITIVITY.md`

PASS state: `FAST64_6_SENSITIVITY_PASS`

## FAST64.7 — Final synthesis

### HARD acceptance

- FAST64.0-FAST64.6 all PASS.
- All primary result identities and raw-log references are frozen.
- Tier A mechanism evidence index exists.
- Tier C heavy auxiliary evidence index exists.
- FAST64 limitations explicitly state platform/workload differences from the
  dissertation environment.
- No claim of exact +22%/+30% numerical reproduction unless independently
  supported, which is not the FAST64 target.
- Negative/zero results are retained.
- Branch is clean except explicitly ignored external raw artifacts.
- Final compact evidence is committed and pushed.

### PASS artifacts

- `handoffs/FAST64_7_FINAL.md`
- `review_packs/FAST64_FINAL/`

PASS state: `FAST64_COMPLETE_READY_FOR_REVIEW`
