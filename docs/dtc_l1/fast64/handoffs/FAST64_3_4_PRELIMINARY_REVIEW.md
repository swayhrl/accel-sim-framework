# FAST64.3/4 preliminary terminal-evidence review

Status: **PRELIMINARY, NONPROMOTING — FAST64.3 ACTIVE; FAST64.4 PHYSICAL
PRECOMPUTATION ONLY**

This record is a review-time audit of already terminal evidence.  It neither
creates a stage PASS nor turns a physical precompute into a primary result.
In particular, it does not compute a FAST12 geometric mean.

## Strict re-audit

At `2026-09-10` the current strict parser was rerun over every discovered
terminal `PAPER_BASE`, `PAPER_IO`, and `PAPER_OO` compact record, using the
exact config and trace-list paths recorded in that attempt's
`RUN_MANIFEST.tsv`.  The audit also checked the START/TERMINAL receipt,
current config/trace/stdout SHA-256 against the manifest/compact record, and
the standard assertion/fatal/deadlock/checker-mismatch scan.

| record class | count | parser/config/trace/stdout | immutable terminal receipt | disposition |
| --- | ---: | --- | --- | --- |
| formal/precomputed terminal rows | 44 | PASS | PRESENT | available only under their recorded pending/reuse authority |
| early NN smoke/telemetry anchors | 6 | PASS | absent by design | supporting instrumentation only; excluded from formal candidates |

The audit is retained outside the repository as
`/tmp/fast64-terminal-preaudit-v2-oXUg35/summary.tsv`; it contains no raw
simulator output.  A passed row still requires its identity/reuse and stage
acceptance gates.  In particular, historical `bbcbb5e...` IO/OO evidence is
not silently promoted to repaired-Core evidence.

### FAST64.6 exclusion regression (2026-09-11)

The provisional generator originally discovered every terminal compact JSON.
That scope was too broad once FAST64.6 physical precomputation began: a
`FAST64_SENS_*` record shares workload/mode provenance with the primary
matrix, but is explicitly not a Stage4 primary candidate.  The generator now
excludes only `provenance.config_id` values with the `FAST64_SENS_` prefix.
This is an analysis-boundary repair, not a simulator/config/result change.

The regenerated review contains 47 non-sensitivity terminal rows in 16
identity groups.  A regression assertion confirms that Btree remains exactly
one repaired-Core Base/IO/OO candidate with common instruction identity and
drain, while BICG's physical-24-KiB IO/OO pair cannot create a primary
candidate.  The independently terminal repaired-Core ATAX/OO and BICG/OO
records now appear only as incomplete Stage3/4 groups because their matching
primary-mode triplets are still absent.  No status is promoted.

### ATAX historical IO reconciliation (2026-09-11)

`fast64_4_atax_io_cap8192_a1_v3` is a natural-exit-zero historical-Core IO
attempt, not an unobserved placeholder.  The strict validator was rerun in an
isolated output namespace using its exact immutable receipt, config, payload,
Core `bbcbb5e...`, runtime `6a8743b4...`, A1 and Framework identity; its
compact result was byte-identical to
`generated/fast64_4_precomputed_rows_v1/fast64_4_atax_io_cap8192_a1_v3.json`.
The zero-access transition map permits this successful literal IO observation
only under its recorded historical provenance.  The provisional triplet table
now records one IO candidate, but it has no matching same-identity Base/OO
triple and is therefore explicitly incomplete and nonpromoting.

### Repaired-Core ATAX and BICG common-triplet audit (2026-09-11)

Regeneration from the current compact-record set exposed two previously
unlisted common-Core-95 candidate triplets. They were independently passed
through `validate_fast64_triplet_v1.py --require-immutable` in an isolated
audit namespace. The validator confirmed matching Core/runtime/A1/Framework
and frozen trace identity, a single immutable terminal receipt per member,
equal dynamic instruction domains, lifecycle conservation, and terminal
drain. The observations are retained only as preliminary candidates:

| workload | Base / IO / OO cycles | common instructions | provisional disposition |
| --- | ---: | ---: | --- |
| ATAX | 87,750,512 / 88,363,340 / 48,078,114 | 145,666,048 | `PRELIMINARY_CANDIDATE` |
| BICG | 88,495,620 / 93,942,704 / 47,231,655 | 145,666,048 | `PRELIMINARY_CANDIDATE` |

This audit does not make either triplet a FAST64.4 primary result and does
not advance FAST64.3, FAST64.4, FAST64.5, or any FAST12 aggregate. It merely
corrects the nonpromoting inventory so later acceptance cannot overlook the
already strict-collected common-identity candidates.

## Current provisional aggregates

The mechanically regenerated, checked-in, nonpromoting tables are:

- `generated/provisional_stage3_structural.tsv`
- `generated/provisional_stage4_triplets.tsv`
- `generated/provisional_stage4_speedup.tsv`
- `generated/FAST64_STAGE_GATE_LEDGER_V1.tsv` (cross-stage HARD-gate state;
  not an acceptance artifact)

The common repaired-Core triplet candidates presently represented are ATAX,
BICG, Btree, Hotspot1, MRI-Q, and NN. Their preliminary cycle observations
are:

### Inventory reconciliation: incomplete NN and historical 2D cells (2026-09-11)

The literal bbcbb NN Base record was correctly retained as historical evidence
but could not join the Core95 NN IO/OO pair. The fresh immutable Core95 NN
Base replacement has now naturally exited, strict-validated, and acquired its
structural companion. The regenerated aggregate therefore has one common
Core95 NN Base/IO/OO candidate with matching instruction identity and drained
terminal state. Separately, the literal bbcbb 2DConvolution OO compact record
appears beside the existing literal IO record, still with zero accepted Base
candidates. It remains historical precompute only: it is neither paired with
nor a substitute for the live Core-41 Base repair and its future Core-41
IO/OO successors.

This is an inventory correction only.  It does not promote a row, alter the
24-cell primary coverage audit, add a GM member, or change the Core-41
common-identity gate.

| workload | Base | IO | OO | Base/IO | Base/OO |
| --- | ---: | ---: | ---: | ---: | ---: |
| ATAX | 87,750,512 | 88,363,340 | 48,078,114 | 0.993065 | 1.825165 |
| BICG | 88,495,620 | 93,942,704 | 47,231,655 | 0.942017 | 1.873651 |
| Btree | 369,977 | 244,231 | 172,795 | 1.514865 | 2.141133 |
| Hotspot1 | 160,486 | 85,206 | 83,439 | 1.883506 | 1.923393 |
| MRI-Q | 366,667 | 360,536 | 361,415 | 1.017005 | 1.014532 |
| NN | 6,985 | 6,095 | 6,105 | 1.146021 | 1.144144 |

These observations are hypotheses for FAST64.5, not causal claims: Btree
combines substantial baseline PIB and traditional-MSHR pressure with the
largest currently observed incremental OO change; Hotspot1 has high PIB
pressure but little IO-to-OO incremental change; MRI-Q is near neutral.  The
future causal review must cross-check those observations with its explicit
HOL, merge, retirement/reclaim, traffic, and live-miss evidence.

### Structural-counter completeness and preliminary contrasts (2026-09-11)

Every terminal Base compact summary already carries the source-defined
`DTC_L1_pib_full_events` field.  Early V1 structural companions did not copy
that field, which made the provisional structural table display `NA` despite
the pinned source evidence.  Future companions now preserve it; the
provisional generator reads the cited compact Base summary for older immutable
companions.  The DWT2D extractor regression passes with the new field, and
all 13 current structural rows now have a concrete PIB-full value.  Existing
companion/result bytes were not rewritten.

The resulting source-backed *hypotheses*, not classifications, include:

| Base evidence | PIB-full | MSHR-entry-full | cacheline-all-reserved | downstream-full | permitted preliminary reading |
| --- | ---: | ---: | ---: | ---: | --- |
| Btree (repaired Core) | 18,175,485 | 1,622,927 | 590 | 0 | strong PIB and conventional-MSHR pressure; compare with IO HOL and OO retirement/reclaim only after its Stage4 authority is complete |
| Hotspot1 (repaired Core) | 5,037,171 | 866,624 | 24,303,354 | 15,056 | substantial Base structural pressure, but the small current IO-to-OO cycle change rules out a premature OO-reclaim conclusion |
| Gaussian (historical Core) | 3,706,501 | 2,025,717 | 29,611,524 | 78,330 | useful source contrast only; historical identity prevents repaired-Core causal use |
| LUD (historical Core) | 5,720,827 | 0 | 6,288,688 | 1,372 | useful near-neutral/low-MSHR contrast only; historical identity prevents repaired-Core causal use |

These fields establish neither stall attribution nor speedup causation.
FAST64.5 still requires accepted common-identity triplets and its complete
HOL/merge/live-miss/traffic/retire/reclaim reconciliation.

## 2DConvolution/Base remains an implementation incident

`fast64_3_2DConvolution_base_cap8192_a1_v2` is a preserved failed attempt,
not a terminal evidence row.  The deadlock dump has all of the following on
SMs 3, 29, and 51:

- `L1_latency_queue` stage zero repeatedly returns `RESERVATION_FAIL`;
- the relevant four conventional-L1 ways are `RESERVED`;
- the displayed MSHR, miss queue, response FIFO, and immediate lower-level
  queue are empty; and
- 129 latency-queue `MEM_FETCH_INITIALIZED` objects remain in the dump.

The configuration fixes `-gpgpu_dtc_l1_lower_outstanding_cap 8192`; this
incident is therefore not evidence that the cap is binding.  It is also not
the earlier dirty-only-victim condition: the frozen config has
`-gpgpu_l1_cache_write_ratio 0`, while this dump shows actual reservation
ownership rather than an unreplaceable dirty victim.

The completed diagnostic and source audit now identify the violating
transition. With `gpgpu_flush_l1_cache=1`, `gpgpu_sim::cycle()` could request
`baseline_cache::invalidate()` when an SM had no runnable threads although an
accepted conventional miss was still live. `tag_array::invalidate()` removed
the tag reservation but retained the MSHR/fill-owner state. A subsequent MSHR
merge could reserve a replacement tag; final fill still used the original
owner index, then erased that owner/MSHR and released its lower credit while
leaving the replacement tag reserved and ownerless. This is the observed
terminal state; `BK_CONF` remains only its frontend retry symptom.

Core commit `41d740e862a6ad89ab0fc32b7b927ec787752862` preserves the existing
invalidate request but defers physical tag invalidation until the conventional
miss queue, fill-owner map, and MSHR/ready-response state are quiescent. It
does not change DTC admission/arbitration, pending-write, scoreboard,
lower-credit, or assertion semantics. Its focused regression and an isolated
Release trace runtime passed; the fresh immutable Core-41 Base replacement is
now live. The historical failed attempt remains invalid and neither the repair
nor this preliminary review promotes FAST64.3 until that replacement naturally
terminates, strictly parses, drains and yields its structural companion.
