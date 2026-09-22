# DTC/ISCAS2027 Experimental Efficiency Policy — 2026-09-22

Status: `AUTHORITATIVE_FOR_RESUME_EXECUTION`

This policy supplements the resume handoff and Goal. It exists to minimize elapsed time and unnecessary simulator cost **without weakening scientific controls**.

## 1. General rule: answer questions, do not fill matrices for their own sake

Every new run must satisfy at least one predeclared evidence need.

Before launching a batch, create/update a compact run-necessity table:

`claim_or_question | required_contrast | existing_exact_evidence | reusable_evidence | genuinely_missing_rows | trigger_for_followup`

If an accepted row with exact scientific identity already answers the required contrast, reuse it. Do not rerun it only to obtain a new directory/stage label.

If a terminal row only lacks validation, validate it. Do not rerun it.

If a diagnostic row can legitimately populate multiple analysis tables under the same exact identity and evidence boundary, reference the same immutable attempt from all of those tables.

## 2. Batch complete independent work once a gate is open

Do not split an already-authorized fixed matrix into many small human-review rounds.

Use short smoke/equivalence runs only to qualify a runtime or observer. Once the qualification gate passes:

- launch the remaining independent rows of that **scientifically justified batch** together, subject to the common host/resource ceiling;
- use a rolling queue;
- validate rows as they terminate;
- do not wait for researcher confirmation between ordinary successful rows.

Human review is required only for the stop conditions already stated in the resume handoff.

## 3. Build once, reuse immutable runtime

For each frozen Core/config family:

- build once in an isolated build directory;
- hash the runtime;
- reuse that exact runtime for the whole authorized campaign;
- do not rebuild per workload;
- do not rebuild merely to create a new stage name.

Rebuild only when the scientific/source identity actually changes.

## 4. SG1 efficiency policy

SG1 canonical NORMAL FAST12 is primary fairness evidence and remains worth completing.

Efficiency rules:

- first strict-validate the terminal B16-N/BICG D2B smoke;
- reuse canonical BICG/Btree smoke rows into G6 only after exact-identity machine audit;
- run all genuinely missing G6 rows as one rolling batch;
- run the bounded same-Core B16-S/TC80-S G6 controls in the same overall execution window when worker slots allow;
- after G6 closes, reuse its exact cells into FAST12 and launch only genuinely missing FAST12 cells.

Do not rerun a G6 cell again for FAST12 if identity is exact.

## 5. SG5 efficiency policy

The canonical 36-row G6 observer campaign is a compact, fixed diagnostic matrix and may be executed as a single rolling campaign after C2 qualification.

Do not serialize by variant or workload unless required by resource pressure.

Where multiple variants use the same workload trace, scheduling them in the same execution window is allowed; do not create duplicate warmup/scientific rows merely for cache warming.

A single accepted immutable observer row may feed all lower-traffic tables that use the same metric semantics.

## 6. SG3 efficiency policy — replace exhaustive 96-row first pass with staged, deduplicated design

The original V1 plan enumerated 96 cells because each dimension repeated its own 1x/default baseline. The resume execution should create a **pre-result V2 deduplicated plan** before launching any observer-ON sensitivity rows.

Fixed G4:
- BICG
- GESUMMV
- Btree
- 2DConvolution

Modes:
- IO
- OO

One default observer-ON baseline cell per workload/mode serves all SG3 dimensions:

- L2 capacity = 1x
- L2 MSHR = 1x
- DTC global lower cap = 8192

This is 8 shared baseline rows total, not three repeated sets of 8.

### Phase A: decisive coarse screen

After the 8 shared baseline rows pass, run:

**L2 capacity**
- 0.5x
- 2x

=> 16 additional rows.

**L2 MSHR entries**
- 0.5x
- 4x

=> 16 additional rows.

**DTC global outstanding cap**
- 512
- 2048
- default 8192 is the shared baseline

=> 16 additional rows.

Phase-A total:
- 8 shared baseline
- 48 sensitivity rows
- **56 distinct observer-ON rows**

This is sufficient to determine whether there is strong evidence for capacity sensitivity, concurrency-resource sensitivity, or injection sensitivity without immediately paying for every intermediate point.

### Phase B: conditional refinement only when scientifically needed

Add MSHR 2x (8 rows) only if Phase A shows that:
- 4x materially improves the difficult workloads, or
- 0.5x degrades them and 4x leaves the saturation point unresolved.

Add DTC cap 1024 and/or 4096 only if Phase A shows:
- a non-monotonic or potentially interior optimum, or
- 2048 materially differs from both 512 and 8192 and the shape matters to the claim.

Do not add intermediate points just to make curves smoother.

If every Phase-B refinement is triggered, the deduplicated full design is at most 80 distinct rows, not 96, because the baseline is shared.

### Queue and service sweeps remain conditional

Run miss-queue sensitivity only if:
- source-defined MISS_QUEUE_FULL pressure is nontrivial, and
- capacity/MSHR/cap results do not already explain it.

Run SG3.5 service sensitivity only if capacity/MSHR/cap/conditional-queue evidence still fails to localize the bottleneck.

Stop when the scientific question is resolved; do not perform decorative sweeps.

## 7. SG4A efficiency policy — bounded characterization before FAST12 expansion

Do **not** automatically launch the full 72-cell logical-Tag missing-point matrix after R0.

First:

1. strict-validate the eight terminal exit-0 BICG/GESUMMV rows;
2. complete failure registry for the four logical80 failures;
3. complete the logical80 source-boundary audit;
4. use the fixed representative G4 set:
   - BICG
   - GESUMMV
   - Btree
   - 2DConvolution
   across IO/OO and logical 32/64 KiB;
5. include logical80 only if the source-boundary audit proves the point legal and numerically executable.

This G4 is predeclared independently of results and contains two difficult and two favorable DTC workloads.

Expand SG4A to full FAST12 only if at least one of the following predeclared triggers is met:

- logical-Tag capacity changes performance by >=5% on at least two G4 workload/mode cells with supporting Tag/pending/duplicate telemetry in a consistent direction;
- logical-Tag capacity changes a primary fairness interpretation (for example, whether DTC can recover a TC80-dominated workload without adding physical data SRAM);
- the final paper intends to make a workload-wide claim about logical-Tag capacity rather than a bounded mechanism diagnosis.

Otherwise close SG4A as a bounded G4 characterization and mark full-FAST12 expansion:

`NOT_TRIGGERED_NOT_REQUIRED_FOR_CLAIM`

Do not run 72 cells merely because a table was previously enumerated.

## 8. Validation efficiency

Validation may be batched after terminal completion, but acceptance remains per immutable attempt.

Use validators to consume existing terminal rows before scheduling any replacement.

A failed validator due solely to invocation/input identity may be reconciled under the existing immutable-revalidation rule; do not rerun the simulator.

## 9. Disk/time budgeting

Before every large launch batch:

- estimate median and high-percentile run-directory growth from comparable completed attempts;
- compute projected batch growth;
- retain at least the hard-stop free-space reserve from the resume handoff;
- size the batch to evidence priority and disk budget, not to CPU count alone.

The Git object store now resides on `/root/share`; this reduces overlay Git-pack pressure but does **not** make either filesystem unlimited.

Before Git pack-intensive work, verify both:
- overlay free space;
- `/root/share` free space.

## 10. Evidence hierarchy under time pressure

If elapsed time becomes the limiting resource, preserve this order:

1. SG1 canonical fairness controls and FAST12;
2. SG3 decisive downstream localization coarse screen;
3. SG5 canonical G6 lower-traffic diagnostics;
4. SG4A bounded G4 logical-Tag characterization;
5. conditional refinements only when required by an unresolved claim.

Do not spend time on a lower-priority dense sweep while a higher-priority scientific gate is still missing.

## 11. No efficiency shortcut may weaken science

Efficiency means:
- reuse exact evidence;
- deduplicate common baselines;
- batch independent rows;
- use predeclared conditional refinement;
- stop when the question is answered.

Efficiency does **not** mean:
- mixing Core/runtime identities;
- changing parameters after seeing favorable results without a predeclared trigger;
- dropping negative workloads;
- accepting terminal-only rows;
- interpreting failed/deadlocked rows numerically;
- replacing strict validation with spot checks.
