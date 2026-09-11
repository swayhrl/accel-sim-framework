# Latest Codex Report

## FAST64.6 GESUMMV 16.5-KiB IO/OO diagnostic acquisition active (2026-09-11)

The committed V2 observational dispatcher was dry-run verified and, after a
fresh two-worker resource admission, launched once in each new namespace:
IO UUID `5a6b4eeb-1563-49f5-8af0-a20ded38fc3c` on CPU 0 and OO UUID
`ac6c1a27-7980-4cdc-85c1-64974a536b76` on CPU 7.  Both have atomic START
receipts and bind only observational Core `f2836ea1...`, binary `361aada1...`,
the original 16.5-KiB configs/payload, A1 and immutable runner `bf9a84c8...`.
They are `NONFORMAL_DIAGNOSTIC_NOT_RESULT`: the terminal analyzer may establish
source state, but cannot relabel either preserved formal failure or advance a
FAST64 stage.

Their future-only collector is syntax-tested and presently reports only
`WAIT_TERMINAL`; it will accept solely exit `1` plus the corresponding
mode-specific deadlock print before materializing a nonformal JSON.  It wrote
no evidence during this live-row check and cannot publish a formal result.
The f283 source print and analyzer were also checked field-for-field with an
IO and an OO synthetic contract record, preventing cross-mode state inference.

## FAST64.6 GESUMMV 16.5-KiB diagnostic path repaired fail-closed (2026-09-11)

The historical GESUMMV/physical-16.5-KiB IO and OO failures remain preserved
non-results.  Their source-state classification needs the already-authorized
observational f283 diagnostic, but the V1 dispatcher correctly refused to run
after the active Core worktree advanced to Core-41.  A future-only V2 keeps
the exact f283 binary/config/trace/immutable-runner contract and validates its
source SHA in a clean detached f283 worktree instead.  Both V2 dry runs and a
fresh two-worker resource admission pass; V2 still requires an explicit CPU
and a fresh namespace.  It is only a `NONFORMAL_DIAGNOSTIC_NOT_RESULT` path
and cannot change any formal Core, sensitivity result, or stage state.

## FAST64.6 BICG 40-KiB IO strict precompute retained (2026-09-11)

The previously terminal BICG/physical-40-KiB/IO namespace was strictly
collected through its existing future-only V5 collector, without changing any
live process.  Immutable UUID `2c49d8fe-5b05-4814-84a5-0d588996b90b` exited
zero and binds Core `95ccdb7a...`, runtime `462d105c...cc4dbc9`, A1,
scientific Framework `037f008b...`, the frozen 320-line physical-pool IO
config and exact payload.  The compact record reports 61,017,789 cycles /
145,666,048 instructions; balanced lower credit and IO
create/issue/response `17,823,522/17,823,522`; dependencies
`18,350,080/18,350,080`; final lower/inflight/PIB `0/0/0`; and lower-cap-full
plus lower-create-queue-full `0`.  It remains solely
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; no logical FAST64 stage or
primary result is advanced.

## FAST64.4 primary IO/OO coverage closed for the currently dispatchable cells (2026-09-11)

The exact 24-cell primary IO/OO audit explicitly excludes all `FAST64_SENS_*`
rows.  It found 18 strict-terminal reuse candidates, GESUMMV/IO+OO live under
the formal Core-95 identity, 2DConvolution/IO+OO blocked on the eventual
common Core-41 triplet identity, and NN/IO+OO as the only genuinely missing
cells.  Following a fresh resource admission, those two NN rows were launched
once through immutable runner `bf9a84c8...` with Core `95ccdb7a...`, runtime
`462d105c...cc4dbc9`, A1 and scientific Framework `037f008b...`; no live
simulator was changed.

Both NN rows naturally exited zero at `2026-09-11T02:20:34Z` and strict
collection passed.  IO records 6,095 cycles / 1,284,872 instructions, balanced
lower credit and IO create/issue/response `2673/2673`, dependencies
`5346/5346`, final lower/inflight/PIB `0/0/0`, and lower-cap-full `0`.  OO
records 6,105 cycles / the same instructions, balanced lower credit and OO
create/issue/response `2673/2673`, dependencies `5346/5346`, final
lower/inflight/PIB/active-refs `0/0/0/0`, and lower-cap-full `0`.  Compact
evidence is `fast64_4_primary_core95_v1/*nn_{io,oo}*.json`.  The 20/2/2
coverage split is nonpromoting: all retained rows remain
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`, FAST64.3 remains ACTIVE, and neither
FAST64.4 nor any GM claim is advanced.

## FAST64.4 2DConvolution OO terminal recovered without promotion (2026-09-11)

The old-Core 2DConvolution/OO physical precompute had a natural exit-zero
receipt but no compact evidence because its original monitor remained at its
initial wait state. A one-shot future-only v3 monitor strictly collected the
unchanged namespace into
`fast64_4_2DConvolution_oo_cap8192_a1_v3_recovered_v3.json`: UUID
`7e6c31bb-6887-4117-850c-6a3b2bc2764e`, 593,208 cycles and 620,347,492
instructions, lower create/issue/response `3,305,954/3,305,954/3,305,954`,
dependencies `7,835,916/7,835,916`, and final OO inflight/PIB/active-ref/lower
state all zero. It preserves literal bbcbb/runtime/A1 identity and remains
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`; it is not a FAST64.4 matrix result
or a replacement for the live Core-41 2D Base repair.

## FAST64.6 physical coverage reconciled against terminal evidence (2026-09-11)

A row-by-row read-only reconciliation found six physical-pool rows whose
ledger state was stale: BICG 32-KiB IO/OO, 40-KiB OO, and 48-KiB OO; plus
GESUMMV 24-KiB IO/OO. Each has a natural terminal receipt and its already
published strict compact JSON with immutable identity, lifecycle closure and
terminal drain. The coverage ledger now marks these six as
`STRICT_TERMINAL_PRECOMPUTE` and pins their existing evidence paths. They
remain `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; this is state reconciliation
only, not FAST64.4 primary acceptance or a result promotion.

## FAST64.6 GESUMMV 48-KiB pair safely dispatched (2026-09-11)

A fresh two-window admission audit found roughly 127--129 GiB MemAvailable,
about 60 GiB cgroup use of 256 GiB, zero sampled memory PSI and swap I/O, and
about 98 GiB output headroom. The exact frozen GESUMMV/physical-48-KiB IO and
OO points were therefore dry-run verified and dispatched once on otherwise
idle CPUs 5 and 6. They are respectively V15 UUID
`d7fe42d6-1422-46b8-8d13-7824cff471b9` and V16 UUID
`d0615a70-d91f-4ae1-a070-28b62944e8c6`; each has the same immutable
Core-95/runtime/A1/scientific-Framework/payload identity and an atomic START
receipt. Future-only V11 closeout monitor PID `1269576` observes only those
two namespaces. Both remain `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; no
FAST64.3/.4/.5/.6 result or stage is promoted.

## FAST64 preliminary inventory reconciled; GESUMMV 40-KiB OO dispatched (2026-09-11)

The nonpromoting Stage3/4 generator was rerun over the current compact
evidence. It now includes repaired-Core ATAX and BICG as complete,
common-identity preliminary triplet candidates. Independent
`--require-immutable` validation confirmed their immutable receipts, exact
identity, equal instruction domains, accounting and terminal drain. Their
observed Base/IO/OO cycles are respectively
`87,750,512/88,363,340/48,078,114` and
`88,495,620/93,942,704/47,231,655`. Both remain
`PRELIMINARY_CANDIDATE` only: no FAST64.3/.4/.5/FAST12 claim changes.

A fresh two-window resource audit passed (about 107--110 GiB MemAvailable,
zero sampled swap I/O and memory PSI, and about 99 GiB output headroom), so
the previously missing nonduplicate GESUMMV/physical-40-KiB/OO row was
launched once in `fast64_sens_v14_gesummv_physical40_oo`, UUID
`301770a0-2ef4-4b1e-b51c-500624ab2dd6`, CPU 3. It uses the frozen
Core-95/runtime/A1/scientific-Framework/payload/config identity and immutable
runner, has an atomic START receipt, and remains
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`. The existing V10 collector
continues to cover only the V13/V14 pair. No live row was changed.

## FAST64.6 physical-pool terminal evidence retained without promotion (2026-09-11)

Four already natural-terminal, strict-collected physical-pool rows are now
retained as compact evidence: GESUMMV/24-KiB IO and OO, BICG/32-KiB IO, and
BICG/40-KiB OO.  Each carries a unique immutable attempt UUID, exact
Core-95/runtime/A1/scientific Framework/payload/config provenance, a single
perf stream, natural exit zero and the collector's terminal accounting/drain
checks.  They remain solely
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; this does not advance FAST64.3,
FAST64.4, FAST64.5, or FAST64.6.

## Four repaired-Core ramp rows revalidated and retained as compact evidence (2026-09-11)

The previously untracked compact records for BICG/Base, BICG/IO, ATAX/Base,
and ATAX/IO were regenerated independently from immutable terminal receipts
and compared byte-for-byte with the stored records.  All four pass the same
strict validator, bind Core `95ccdb7a...`, runtime `462d105c...`, A1,
scientific Framework `037f008b...`, their exact payload/config identity and
single-epoch immutable runner receipts.  Their lower/dependency accounting,
terminal drain, and lower-cap-full checks remain closed.

They are committed only as
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` evidence.  They do not promote
FAST64.3 or FAST64.4, and do not alter the separate Core-41 2DConvolution
replacement now running.

## 2DConvolution/Base diagnostic closed; source-correct repair in validation (2026-09-11)

The preserved historical formal Base attempt remains invalid: it naturally
terminated exit `1` with a simulator deadlock and is not relabeled or promoted.
The separate observational diagnostic UUID
`a970b692-22d5-441d-ad6a-faa500d9d573` also naturally terminated exit `1`.
The one-shot fail-closed collector published
`fast64/generated/fast64_3_diagnostics_v1/fast64_3_2d_base_coref283_diag_v1.json`
as `NONFORMAL_DIAGNOSTIC_NOT_RESULT`.

It observes reserved L1D tags with no fill owner, empty conventional
MSHR/miss-queue state, and no sector-child `pending_read`; the 129 latency
queue fetches are stranded behind that state.  Source tracing localizes the
cause to an L1 invalidation executed before a conventional miss lifecycle
drains: a later MSHR merge can reserve a replacement tag while the surviving
fill owner still points to the original index.  Completion removes the owner
but leaves the replacement tag reserved.  `BK_CONF` is only the resulting
retry behavior.  A minimal Core repair now defers the existing invalidation
until conventional miss/owner/MSHR state drains; it has built and passed the
existing focused tests, but no new formal result is claimed until its directed
regression and fresh immutable 2DConvolution/Base replacement pass.  Stage
FAST64.3 remains ACTIVE; the registry now explicitly records
`INVALID_HISTORICAL_BASE_PENDING_REPAIR` and has no nonexistent evidence path.

The separately committed Core repair is `41d740e862a6ad89ab0fc32b7b927ec787752862`
(`fix(l1): defer invalidation until miss lifecycle drains`).  A clean isolated
Release trace runtime built from it hashes to
`6e72d36665cde18e2845914ee9c2a9f2e65b37b7b3c216edf4b676ad17e2c21c`.
After a two-window read-only resource audit, the fresh formal replacement was
launched once on CPU 34 in
`/workspace/fast64-stage3-repair/fast64_3_2DConvolution_base_core41d740e8_a1_v1`:
UUID `7ba2205a-e205-4793-a3c0-8bce1a56d2f1`, immutable runner
`bf9a84c8...`, exact frozen Base config/trace and A1 observer.  Its first
50-second sample was CPU-active with growing stdout and no fatal signature.
It is `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`, not a result; an isolated
atomic strict collector will publish nothing unless it naturally exits zero
and clears all identity, parser, failure-scan and accounting gates.

After that strict collector publishes, the separately committed future-only
structural companion collector (`29e9bf19...`) reads the immutable summary and
the one terminal perf CSV, then atomically publishes the Base structural
companion. Its detached monitor is live as PID `1265331`; it currently records
only `WAIT_TERMINAL`. It has no authority to write the run, strict summary,
registry, or stage state.

## Stage3 PIB structural mapping completed for preliminary review (2026-09-11)

The fixed Base summaries all contained `DTC_L1_pib_full_events`; an early
structural-companion omission made the provisional table display `NA`.  The
future extractor now preserves the field and the provisional generator safely
recovers it from the already pinned summary for older companions.  DWT2D
regression passes and all 13 current structural rows now have source-backed
PIB-full values.  The updated preliminary handoff records Btree, Hotspot1,
Gaussian and LUD contrasts as hypotheses only.  It expressly retains the
historical-Core boundary for Gaussian/LUD and makes no causal, primary-stage,
or GM claim.

## Preliminary Stage3/4 analysis boundary repaired (2026-09-11)

The provisional Stage3/4 generator was audited against newly published
FAST64.6 records and found to be too broad: a `FAST64_SENS_*` physical
precompute could otherwise add duplicate IO/OO candidates to the primary
matrix.  The future analysis utility now excludes that exact config-ID family
only.  It does not modify simulators, experimental configurations, compact
results, or frozen collectors.  Regeneration and an explicit assertion prove
that Btree remains the single 1/1/1 repaired-Core preliminary candidate and
that the BICG physical-24-KiB pair is excluded from Stage4 aggregation.

The refreshed table also exposes repaired-Core ATAX/OO and BICG/OO only as
incomplete primary groups; neither row has the required matching triplet.  All
tables remain `PRELIMINARY_NONPROMOTING`, with no FAST64.3/.4/.5 PASS or
FAST12-GM claim.

## BICG 24-KiB pair strictly closed; GESUMMV 40-KiB IO safely precomputed (2026-09-11)

BICG/physical-24-KiB/PAPER_IO naturally exited zero and the unchanged V1
collector atomically published its strict compact record.  It binds formal
Core `95ccdb7a...`, runtime `462d105c...`, A1, scientific Framework
`037f008b...`, exact IO config `6d8ab5fa...`, and frozen payload; it records
42,351,523 cycles / 145,666,048 instructions, balanced lower
create/issue/response and credit lifecycles of 17,647,559, closed IO
dependencies 18,350,080/18,350,080, final lower/PIB/partial/inflight drain,
and lower-cap-full zero.  Together with the already strict OO companion, it
is a complete **precomputed only** pair, still
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`.

A fresh two-window target-20 replacement audit passed: zero sampled swap-out,
OOM, memory PSI and CFS throttling; 133.75 GiB `MemAvailable`; 187.86 GiB
cgroup headroom; and 104.16 GiB output headroom.  The exact nonduplicate
GESUMMV/physical-40-KiB/PAPER_IO row was dry-run verified then launched once
on CPU 30 (UUID `146b0390-2592-436d-bf4c-fad1e96148c6`, supervisor 948487,
simulator 948512).  Its immutable START receipt and short CPU-progress/no-real
fatal scan are clean.  New future-only V10 collection watches only this new
V13/V14 pair and does not modify existing collectors or simulators.  The OO
companion is not yet launched.  No FAST64.3/.4/.5/.6 promotion or FAST12
aggregation is claimed.

## FAST64 stage-gate ledger reconciled (2026-09-11)

`fast64/generated/FAST64_STAGE_GATE_LEDGER_V1.tsv` records the current
nonpromoting state machine from the acceptance contract: FAST64.0/.1/.2 are
PASS; FAST64.3 is ACTIVE pending the 2DConvolution/Base closure and full Base
promotion audit; FAST64.4 is PREPARED; FAST64.5 is preliminary analysis only;
FAST64.6 is physical precomputation only; and FAST64.7 is not entered.  The
ledger names the exact evidence or still-missing HARD boundary for every
stage, so no precompute or provisional aggregate can advance a stage by
renaming.

## GESUMMV 48-KiB future-only closeout prepared (2026-09-11)

The final unlaunched physical pair, GESUMMV 48 KiB IO/OO, now has passing
immutable-v2 dry-runs and an isolated V11 strict collector.  Its config delta
from 40 KiB is only 320 to 384 physical 128-B lines.  No namespace was
created and no live simulation/controller was changed; dispatch remains
strictly gated on a naturally released target-20 slot.

## 2DConvolution/Base terminal-classification map frozen (2026-09-11)

The active nonformal 2DConvolution/Base diagnostic was left untouched and is
CPU-active with growing stdout.  Its failure record now maps the observed
reserved-line/fill-owner state to the frozen conventional Base source path:
lower-credit and ownership creation, miss-queue injection, sector aggregation
and final fill/release, plus the frontend `BK_CONF` retry behavior.  The map
explicitly prevents a snapshot from being mistaken for a root cause or a
license to alter tag allocation or assertions.  It is observation-only
preparation for the diagnostic's natural terminal state.

## GESUMMV 40-KiB future-only closeout prepared (2026-09-11)

The fresh immutable-v2 dispatcher dry-runs for GESUMMV physical-40 KiB
PAPER_IO/OO pass without creating either namespace.  The config diff from the
physical-32 reference changes only the 128-B-line pool from 256 to 320 lines.
Future-only `collect_fast64_6_precompute_v10.sh` validates only V13/V14,
publishes atomically after a natural terminal receipt, and leaves all live
V1--V9 collectors untouched.  No work was launched because the approved
target-20 pool remains full; this is preparation only, never a result or
promotion.

## FAST64.6 physical coverage ledger refreshed without changing live work (2026-09-11)

`fast64/generated/FAST64_6_PHYSICAL_COVERAGE_V1.tsv` reconciles the frozen
30-row physical IO/OO roster before further dispatch.  It separates eleven
strict-terminal precomputes, eleven live formal rows, one live nonformal
BICG/16.5-KiB observation, four preserved 16.5-KiB failures, and four
not-yet-launched GESUMMV points.  This is preliminary operational coverage:
terminal rows remain `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; failures
remain excluded; and no FAST64.3/4/5/6 or FAST12-GM result is asserted.  The
live target-20 worker set and all collectors were read only.

## ATAX historical IO strict-revalidated as a literal candidate (2026-09-11)

The previously untracked ATAX/PAPER_IO compact row was verified from its
immutable START/TERMINAL receipts, exact historical Core `bbcbb5e...`/
runtime `6a8743b4...`, A1, config and payload.  A fresh isolated strict
validation produced byte-identical JSON.  It is now tracked as a literal
historical IO reuse candidate in the provisional table; it is not relabeled as
Core-95, has no common-identity triplet, and creates no stage/result promotion.

## BICG physical-32 OO future-only closeout restored (2026-09-11)

The original v4 controller is no longer a live process, while its one
remaining BICG/physical-32/PAPER_OO row is still CPU-active with a valid
immutable START receipt.  New `collect_fast64_6_precompute_v9.sh` therefore
strictly targets only that namespace and publishes to a distinct v9 evidence
directory after natural terminal.  It preserves the exact Core-95/runtime/A1/
Framework/payload/config identity, scans fatal signatures, verifies receipt
and config hashes, and atomically writes a compact result only on strict PASS.
The controller is live and currently waits; no existing collector file or
simulator was modified.

## GESUMMV 16.5-KiB source-state diagnostic prepared without dispatch (2026-09-11)

The GESUMMV physical-16.5 KiB failure now has a source-backed, future-only
diagnostic path.  Existing observational Core `f2836ea1...` already prints
post-deadlock IO FIFO/physical-pool state and distinct OO PIB/refcount state,
after the pre-existing deadlock decision only.  Its Core behavior is not in
the formal Core-95 identity and no formal binary or live process changed.

`dispatch_fast64_6_gesummv_physical16p5_diagnostic_v1.sh` dry-run passes for
both exact frozen IO and OO configs.  It verifies Core/binary/runner/config
hashes, refuses an existing namespace, and needs an explicit `--dispatch` plus
safe CPU; it consequently did not consume a target-20 slot.  The paired
parser consumes only those source diagnostic lines and preserves the semantic
boundary that IO partial-allocation evidence cannot be used to assign an OO
root cause.  The old formal failures remain failed evidence only.

## Btree/32-KiB strict pair closed; BICG/48-KiB and GESUMMV/32-KiB pairs in acquisition (2026-09-11)

The formerly inactive v4 supervisor was not altered; its unchanged collector
was invoked once as a read-only, atomic closeout step after both of its Btree
physical-32 rows had naturally terminated.  It strictly published the pair:
Btree/IO UUID `cb54525c-c634-4bbc-96e7-b8a43570c55f` at 244,231 cycles and
Btree/OO UUID `55755348-52c5-4c96-858c-638814aa0570` at 172,795 cycles, both
at 444,467,849 instructions.  The IO lower lifecycle is
`507,779/507,779/507,779`; OO is `502,450/502,450/502,450`; both dependency
lifecycles close `2,388,513/2,388,513`, all terminal lower/PIB/inflight (and
OO active-ref) state drains, and lower-cap-full is zero.  Both retain formal
Core/runtime/A1/scientific/payload identity and only
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` classification.

GESUMMV/physical-16.5/IO naturally exited 1 at its deadlock detector, matching
the already preserved OO failure; it has no PASS record and is held apart from
the eleven strict-terminal precomputes pending resource-state source
classification.  It does not alter the frozen matrix or constitute a stage
gate.  With the newly free capacity and a fresh healthy resource audit, four
exactly-once rows were dry-run verified then launched with atomic START
receipts: BICG/48-KiB IO `4a5a9737-1928-48b6-8ae9-f017f465466d` on CPU 31,
BICG/48-KiB OO `7e733ecb-f9b2-46e6-9899-4c5dd1e7213f` on CPU 37,
GESUMMV/32-KiB IO `cfed0564-14df-4e0f-b650-ae5460b88e25` on CPU 26, and
GESUMMV/32-KiB OO `00a173e5-8402-4345-9f4f-b5121b89957a` on CPU 35.
Future-only v7/v8 collectors isolate these new namespaces; no active
collector or simulator was changed.  All four are physical acquisitions only,
not FAST64.4/5/6 logical results.

## BICG / 24-KiB / OO strict-terminal physical precompute (2026-09-11)

The existing independent collector has now atomically published the compact
record for BICG / physical 24 KiB / PAPER_OO, immutable attempt
`e33abcc8-c43f-4599-a55b-4e895fe2fe32`.  Its START/TERMINAL receipts show
natural exit zero; strict validation binds formal Core `95ccdb7a...`, runtime
`462d105c...`, A1 observer, scientific Framework `037f008b...`, exact OO
config SHA `e7161643...`, and the frozen BICG payload.  It records 37,846,112
cycles and 145,666,048 instructions; lower create/issue/response and credit
acquire/release are all `17,639,701`, OO dependencies close
`18,350,080/18,350,080`, final lower/PIB/inflight/active-ref state is zero,
and lower-cap-full is zero.  The compact evidence is
`fast64/generated/fast64_6_precomputed_v1/fast64_sens_v1_bicg_physical24_oo.json`.

This is the ninth strict-terminal FAST64.6 physical acquisition only:
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`.  The paired BICG / 24-KiB / IO
row remains live, so no pair comparison, primary result, stage acceptance, or
FAST12 aggregation is asserted.

## Stage3/4 preliminary review refreshed; FAST64.6 BICG 40-KiB OO precompute dispatched (2026-09-11)

Goal mode remains active.  The already checked-in preliminary Stage3/4 tables
were reread against their compact strict records and the zero-access transition
map.  They remain explicitly nonpromoting: the only complete, same
repaired-Core/runtime triplet candidates are Btree, Hotspot1, and MRI-Q;
historical `bbcbb5e...` rows retain their literal identity and only the
source-inert/reuse status recorded in
`fast64/handoffs/FAST64_ZERO_ACCESS_CORE_REPAIR_IDENTITY_MAP.md`.  No
FAST64.3, FAST64.4, FAST64.5, or FAST12-GM claim is made.  The preliminary
structural/speedup tables continue to be hypotheses for the later causal
review, not a correlation-to-causation conversion.

The frozen FAST64.6 authority resolves the execution policy without an
experiment-design choice: logical, physical-pool, and PIB families use
PAPER_IO and PAPER_OO; physical points normalize to 32-KiB IO; and the
physical mapping remains exact whole lines (including 40 KiB = 320 lines).
After a fresh resource audit found 19 FAST64 simulator leaves, 129.5 GiB
`MemAvailable`, 64.3 GiB of the 256-GiB cgroup currently used, zero current
memory/I/O PSI, no CFS throttling, and about 106 GiB output headroom, one
unshared physical core was safely available.  The exact missing paired point
BICG / physical 40 KiB / PAPER_OO was dry-run verified and atomically
dispatched on CPU 41 as UUID `11383078-382d-4f18-9eb3-975bce4fb434`.

It uses formal Core `95ccdb7a...`, runtime `462d105c...`, A1 observer,
scientific Framework `037f008b...`, materialization `180e81c...`, the
read-only immutable-v2 runner `bf9a84c8...`, and fresh namespace
`fast64_sens_v8_bicg_physical40_oo`.  Its START receipt is present and a new
future-only v6 collector watches only that namespace.  Existing V3/V4/V5
collectors and every live Stage3/4 or sensitivity simulator were not changed.
This is solely `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`, never a primary
FAST64.4 result or FAST64.6 logical acceptance.

## Prepared exact 2DConvolution/Base diagnostic replay; no live work disturbed (2026-09-11)

The preserved 2DConvolution/Base failure now has a hash-pinned, future-only
diagnostic dispatcher at
`util/dtc_l1/dispatch_fast64_3_2d_base_diagnostic_v1.sh`. Its read-only
default dry-run passed against clean observational Core `f2836ea1...`, its
Release binary `361aada1...`, immutable runner `bf9a84c8...`, the frozen Base
config `1a016e3c...`, and the exact frozen trace list `23bcc08b...`. It
cannot dispatch without an explicit CPU and refuses an existing namespace.
Any eventual run is `NONFORMAL_DIAGNOSTIC_NOT_RESULT`, is not a replacement
for the failed historical attempt, and is deferred until a resource-safe slot
is available. No simulator, live controller, scientific config, or formal
result was changed by this preparation.

The paired read-only analyzer
`util/dtc_l1/analyze_fast64_3_2d_base_diagnostic_v1.py` is now ready for that
future terminal stdout. It mechanically joins each reserved L1D block to its
observed fill owner and `pending_read` count, rejects the old dump because it
lacks this required instrumentation, and labels all output observation-only.
It was tested with a synthetic owner/absence mapping and cannot create a
formal result or select a repair.

One permitted target-20 slot subsequently became free when Btree / physical
24-KiB / OO naturally exited zero. The frozen v3 collector strict-validated
and atomically recorded its `172,795` cycles / `444,467,849` instructions,
balanced lower `502,450/502,450` and dependency `2,388,513/2,388,513`
lifecycles, complete drain and lower-cap-full zero in
`fast64/generated/fast64_6_precomputed_v3/fast64_sens_v5_btree_physical24_oo.json`.
It remains `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` only.

The released CPU 34 was safely used for the exact, fresh 2DConvolution/Base
observational diagnostic UUID `a970b692-22d5-441d-ad6a-faa500d9d573`, not a
formal rerun. Its immutable START receipt binds diagnostic Core `f2836ea1...`,
the hash-pinned observational binary and the frozen Base trace/config. The
row is live as `NONFORMAL_DIAGNOSTIC_NOT_RESULT`; all other FAST64 work was
left running naturally.

Three additional Btree sensitivity rows (physical 40-KiB IO/OO and 48-KiB OO)
then naturally exit 0 and strict-validate, bringing retained physical
precomputes to seven. Their compact records retain exact identities, balanced
lower/dependency accounting, terminal drains and zero lower-cap-full, but all
remain `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`. The freed capacity safely
admitted fresh, nonduplicate physical-32 Btree IO/OO and BICG OO rows under
the detached formal Core-95 identity and immutable START receipts. A separate
future-only v4 collector covers just this v6 wave, leaving the live v3
collector byte-for-byte unchanged.

Btree/48-KiB/IO also naturally completed with exact formal identity, 244,231
cycles at 444,467,849 instructions, closed lower/dependency accounting and
full terminal drain. It is the eighth retained precompute only. Its released
slot now runs fresh BICG/40-KiB/IO under immutable UUID
`2c49d8fe-5b05-4814-84a5-0d588996b90b`; a future-only v5 collector is isolated
to that row so existing live collectors remain unchanged.

## FAST64.6 BICG/16.5-KiB capacity boundary preserved; Btree IO precomputes added (2026-09-10)

Two Btree physical-pool IO rows naturally exit 0 and strict-validate as
precomputes only: 16.5 KiB (`548,243` cycles) and 24 KiB (`244,231` cycles),
both at the exact `444,467,849` instructions with balanced lower and
dependency accounting, complete drain and lower-cap-full zero.  Their compact
identity/result records are in `fast64/generated/fast64_6_precomputed_v1/`.
Together with the prior Btree/16.5-KiB/OO record, these are strictly
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`, never FAST64.4 or FAST64.6
logical results.

BICG at 16.5 KiB naturally reaches the simulator deadlock detector in both
IO and OO; both exit-1 receipts and raw namespaces are preserved and the
collector correctly produces no PASS record.  IO has source-backed
classification: the frozen no-rollback partial-allocation model reaches its
explicitly allowed undersized-pool circular resource deadlock (132/132
physical lines allocated, FIFO head incomplete, no outstanding lower work).
This must not be repaired by weakening the mechanism.  OO remains excluded
with a telemetry-only fatal-dump observation follow-up because its current
formal dump lacks equivalent resource detail.  The full evidence and
nonpromotion disposition are in
`fast64/handoffs/FAST64_6_BICG_PHYSICAL16P5_FAILURE.md`.  Active 24-KiB BICG,
all other sensitivity rows and every Stage3/4 simulator remain untouched.

The fresh capacity audit subsequently admitted only the target-16 refill:
Btree physical-24-KiB/OO and physical-40-KiB/IO are live, exact formal
Core-`95ccdb7a` immutable precomputes with START receipts, fresh namespaces
and topology-separated cores.  The new dispatcher binds a detached clean
Core-95 worktree so the current diagnostic-only Core descendant cannot bleed
into formal provenance.  Separately, one BICG/16.5-KiB/OO reproduction runs
under Core `f2836ea1...` solely to print previously unavailable OO deadlock
resource state; it is explicitly `NONFORMAL_DIAGNOSTIC_NOT_RESULT`.  No
formal stage or result promotion is implied.

After a healthy target-16 observation, four further nonduplicate frozen rows
were admitted to the authorized target-20 total: Btree physical 40-KiB/OO,
48-KiB/IO, 48-KiB/OO, and BICG physical 32-KiB/IO.  Each uses the detached
formal Core-95 identity, immutable runner, atomically published START receipt
and an unshared physical CPU.  The fresh post-launch audit remains free of
memory PSI, CFS throttling and forbidden simulator signatures.  These live
rows remain `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; no performance result
or stage conclusion has been accepted.

The newly terminal repaired-Core ATAX/OO row was also independently reconciled
from its immutable START/TERMINAL receipts and strict compact record: exit 0,
the exact `145,666,048` instructions, lower create/issue/response
`17,814,804/17,814,804/17,814,804`, lower credit acquire/release balance,
dependency `18,350,336/18,350,336`, and final PIB/inflight/lower/OO-ref drain.
It is recorded as `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` only in
`fast64/generated/fast64_repaired_ramp_v1/fast64_atax_oo_core95ccdb7a_a1_r1.json`.
The corresponding repaired ATAX Base/IO rows are still nonterminal, so this
does not create an ATAX triplet, a FAST64.3 result, or any stage promotion.

Repaired-Core BICG/OO is likewise terminal and strict-preserved only:
`145,666,048` instructions, `47,231,655` cycles, balanced lower
create/issue/response and credit lifecycle (`17,814,913` each), balanced OO
dependencies (`18,350,080`), and all final lower/PIB/inflight/OO-ref counters
drained.  Its immutable receipts bind Core `95ccdb7a...`, runtime `462d105c...`
and the A1/scientific identities.  The compact record
`fast64/generated/fast64_repaired_ramp2_v1/fast64_bicg_oo_core95ccdb7a_a1_r1.json`
remains `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`; BICG Base and IO remain
live, so no triplet or stage claim is made.

## FAST64.3/4 preliminary strict review; FAST64.6 held at current safe concurrency (2026-09-10)

The current strict parser was rerun against every discovered terminal
Base/IO/OO compact record using the original config and trace receipt.  Of 50
records, 44 passed parser, receipt, config/trace/stdout-hash and forbidden-log
checks.  The other six are deliberately receipt-less early NN smoke/telemetry
anchors: they parse and hash-check cleanly but remain supporting-only rather
than formal candidates.  This is recorded without stage promotion in
`fast64/handoffs/FAST64_3_4_PRELIMINARY_REVIEW.md`; the checked-in provisional
structural/triplet/speedup tables remain explicitly nonpromoting and contain
no FAST12 GM.

The source review of the preserved 2DConvolution/Base failure now excludes
both a lower-cap-full interpretation and the obsolete dirty-victim condition.
Its three blocked SMs have stage-zero conventional-L1 reservation retries,
four `RESERVED` ways, and no displayed MSHR/miss-queue/response/lower owner.
This proves a reservation-completion ownership incident but not its root
cause.  No speculative functional Core change or blind re-run was made.  A
diagnostic-only Core commit `1c69f97a...` now makes the unprinted baseline
fill-owner map visible in a fatal dump; an isolated build passed.  Its future
directed run is nonformal, preserves the exact frozen 2D Base payload/config,
and waits for a resource-safe free slot rather than displacing current Stage3/4
or FAST64.6 simulators.

The first FAST64.6 terminal is Btree / 16.5-KiB physical / PAPER_OO: it
naturally exited 0 at `2026-09-10T14:06:03Z` and strict-validated with the
formal repaired Core/runtime, scientific Framework and A1 identities.  Its
lower lifecycle is `501958/501958`, its OO dependencies are
`2388513/2388513`, final lower/PIB/inflight/OO-ref state is drained, and
lower-cap-full is zero.  The compact record is
`fast64/generated/fast64_6_precomputed_v1/fast64_sens_v1_btree_physical16p5_oo.json`.
It remains only `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`, not a stage
result.  The other nine physical-sensitivity rows remain immutable,
repaired-Core/A1 precomputes only; at the latest read-only snapshot they were
CPU-active and clean of assertion/fatal/deadlock signatures.  `MemAvailable`
is about 52 GiB, while swap is nearly allocated but has no sampled swap-out or
memory-PSI.  Existing concurrency is retained; no new worker is admitted
pending a fresh healthy observation.  The subsequent three-window refill
audit passed one new worker for a 20-worker total, so the next frozen,
nonduplicate Btree / 24-KiB / IO physical row began with UUID
`c0902c8e-e9b8-4783-a021-933494c8b558`; it is likewise only
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`.

## FAST64.6 first physical-precompute wave active (2026-09-10)

The authorized frozen FAST64.6 matrix is now in physical acquisition, without
advancing FAST64.6 logically.  V3 resource admission for target 20 passed with
15 live FAST64 leaves, p95 RSS 2.96 GiB, 103.2 GiB `MemAvailable`, 208.7 GiB
cgroup headroom, 110.2 GiB output free, and zero sampled swap-out, OOM,
memory PSI, CFS throttling and pathological I/O.  Ten immutable-v2,
repaired-Core/A1 rows then started in fresh namespaces: 16.5-KiB physical
IO/OO for BICG, GESUMMV and Btree, plus 24-KiB IO/OO for BICG and GESUMMV.
Each has an atomic START receipt and a distinct read-only terminal monitor;
the compact identity index is
`fast64/generated/FAST64_6_PRECOMPUTE_DISPATCH_V1.tsv`.

All ten are strictly classified
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`.  They are neither FAST64.4
primary results nor a FAST64.6 PASS.  Existing Stage3/4 simulators and their
controllers were not modified.  The 2DConvolution/Base historical failure
remains an active source-diagnosis item: its deadlock snapshot shows reserved
conventional L1 lines with no live L1 MSHR/miss-queue owner; this is evidence,
not yet a root-cause conclusion or a repair.

The historical GEMM/OO row naturally reached exit 0 and strict validation:
its old-Core lower lifecycle is `4,113,199/4,113,199`, dependencies
`8,396,800/8,396,800`, and final lower/PIB/inflight/OO-ref state is drained.
It is retained as `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` only.  Because the
zero-access repair map authorizes historical reuse only for source-inert Base,
the preliminary analyzer now labels the otherwise-complete old-Core GEMM
Base/IO/OO set `HISTORICAL_CORE_NONPROMOTING`; it cannot become a repaired-Core
FAST64.4 triplet or candidate speedup.

## FAST64.3 failure preservation / FAST64.6 pre-dispatch freeze (2026-09-10)

The historical bbcbb 2DConvolution/Base acquisition is no longer live: its
immutable terminal receipt records exit `1` at `2026-09-10T12:50:39Z` after a
source-recorded simulator deadlock, not a timeout.  The raw diagnostic has
129 `MEM_FETCH_INITIALIZED` L1D latency-queue fetches and conventional-L1
reserved-line/retry state; the failed attempt is isolated in
`fast64/handoffs/FAST64_3_2DCONVOLUTION_BASE_FAILURE.md` and cannot enter
FAST64.3.  The zero-access repair is source-inert for PAPER_BASE, so a blind
repaired-Core rerun is not claimed as a remedy; root-cause work continues.

FAST64.6 physical acquisition is independently authorized after FAST64.2.  A
new, versioned pre-dispatch handoff and 78-row IO/OO matrix freeze BICG,
GESUMMV and Btree along the logical/physical/PIB axes; the M5 authority makes
logical Base a supplemental-only control, with physical and PIB both IO/OO.
The dispatcher separately binds the scientific snapshot `037f008b...` and
config-materialization commit `180e81c6...`, then launches only the immutable
repaired Core/runtime/A1 identity.  This remains physical precomputation under
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`, not a FAST64.6 stage advance.

The fresh three-window target-16 audit at
`/tmp/fast64-resource-audit-v3-20260910T1325Z-target16.tsv` found 11 live
FAST64 leaves, p50/p95/max RSS 2.37/4.87/4.87 GiB, zero sampled swap-out,
memory PSI, OOM, major faults and CFS throttling.  It admits five additional
workers with projected 71.8 GiB `MemAvailable`, 213.5 GiB cgroup headroom and
110.2 GiB output free.  Provisional nonpromoting triplet/speedup/structural
tables are now generated; only Btree, Hotspot1 and MRI-Q have complete common
repaired-Core candidate triplets, so no GM-FAST12 is computed or claimed.

## FAST64.6 frozen sensitivity configuration materialization (2026-09-10)

Following the already-passed `FAST64_2_REPAIR_PASS` gate, the future-only
materializer has produced 29 resolved sensitivity configurations in
`configs/dtc_l1/fast64/sensitivity_frozen_v2`: logical 16/32/64 KiB
Base/IO/OO (9), physical 16.5/24/32/40/48 KiB IO/OO (10), and PIB
32/64/128/192/256 IO/OO (10).  The compact checked-in manifest is
`fast64/generated/FAST64_SENSITIVITY_CONFIG_MANIFEST_V1.tsv`.

Each configuration was checked to retain global lower cap `8192`, and a
resolved-config normalization test proved it identical to the appropriate
primary Base/IO/OO file except for the declared sensitivity field(s).  The
fixed materializer now checks the actual canonical FAST64.2 PASS header and
tolerates the existing Base geometry whitespace; its aborted v1 attempt had
written no config file.  This is configuration precomputation only: no
sensitivity simulation, result, promotion, or scientific claim has begun.

## FAST64 safe-parallelism recalibration / Hotspot repair reconciliation (2026-09-10)

The latest review's requested Hotspot1/PAPER_OO isolated minimal-guard check
was already complete in the live repository state, so no duplicate simulator
was launched.  The common repaired-Core Hotspot1 Base/IO/OO immutable triplet
has terminal receipts with exit `0`, strict validator status
`FAST64_TRIPLET_STRICT_VALID_PENDING_STAGE_ACCEPTANCE`, and common repaired
Core/runtime `95ccdb7a...` / `462d105c...cc4dbc9`.  IO/OO record `85,206` /
`83,439` cycles at common `377,291,004` instructions; the repair and its
identity/reuse boundary are already committed and documented in
`fast64/handoffs/FAST64_ZERO_ACCESS_CORE_REPAIR_IDENTITY_MAP.md`.  Thus it is
not permissible to relaunch either qualification merely to satisfy a stale
dispatch instruction.

A new future-only, read-only v3 admission wrapper,
`util/dtc_l1/audit_fast64_future_precompute_resources_v3.sh`, retains the
existing multi-window V2 samples but adds FAST64-only RSS p50/p95/max,
projected total workers, a fixed 16-GiB `MemAvailable` reserve, and explicit
CFS-throttle rejection.  It changes neither simulator semantics nor any live
controller/collector.  Its source syntax and a two-window live dry run pass.

At the 2026-09-10T12:18:47Z three-window snapshot, exactly 13 FAST64
`accel-sim.out` leaves were live: old-Core 2DConvolution/Base (PID `57531`),
ATAX/IO (`67664`), GEMM/IO (`101725`), GEMM/OO (`101766`); repaired-Core
ATAX/OO (`219903`), GESUMMV/OO (`219910`), BICG/Base/IO/OO
(`232965`/`232978`/`232988`), GESUMMV/Base/IO (`232992`/`269155`), and
ATAX/Base/IO (`269186`/`289484`).  Every leaf was CPU-active at 99.4--99.5%
on a distinct CPU.  Aggregate FAST64 RSS was 31.1 GiB; p50/p95/max were
2.31/4.80/4.80 GiB.  The cgroup quota is 384 CPUs with 0 throttle events,
about 208 GiB cgroup-memory headroom, 39.2 GiB `MemAvailable`, zero memory
PSI/OOM/major faults, 111 GiB output free, and low cgroup I/O.

The paired audit artifacts are retained outside the repository at
`/tmp/fast64-resource-audit-v3-20260910T121815Z-target{16,20}.tsv`.  Both
observed one 65-page swap-out window followed by two zero windows, therefore
`TRANSIENT_SWAP_ACTIVITY`, not sustained memory pressure.  Target 16
(three additional p95-RSS workers) passes: projected `MemAvailable` remains
25.7 GiB after the new workers and above the 16-GiB reserve.  Target 20
(seven new workers) is rejected because it would leave only 6.5 GiB, below
that reserve.  The current resource-safe target is consequently
`N_safe = 16`, with no more than three new workers before another fresh audit.

Those three slots were deliberately not filled with duplicate simulations:
the sole pending FAST64.3 Base acquisition is the already-live
2DConvolution/Base; Btree and MRI-Q already have repaired-Core terminal
evidence awaiting promotion reconciliation; all other Base requirements are
accepted, strict-valid, or already active.  Existing FAST64.4 precompute rows
also retain their individual immutable namespaces/closeout paths.  Filling a
slot with an already-running or identity-incompatible row would violate
exactly-once and the zero-access reuse map.  FAST64.3 remains ACTIVE and
FAST64.4 remains physical precomputation only.

## FAST64 old-Core continuation deauthorized before successor dispatch (2026-09-10)

The old `continue_fast64_4_precompute_v1.sh` controller (PID `72912`) remains
live and unchanged while its bbcbb ATAX/IO predecessor continues naturally.
Because that controller would otherwise dispatch a new long old-Core row after
its prerequisite closes, an empty, otherwise-unused first legacy namespace
`/workspace/fast64-runs/fast64_4_atax_oo_cap8192_a1_v3` was atomically reserved
before the prerequisite exists.  The controller will therefore take its own
existing `REFUSE_NAMESPACE` exit path before it can launch a successor.

No simulator, controller, runner, config, payload, raw evidence, or compact
result was modified; the reservation contains no files and is not a result.
This enforces the existing authority that new long FAST64 acquisition uses
repaired Core `95ccdb7a...` / runtime `462d105c...cc4dbc9`, while preserving
the still-live bbcbb ATAX/IO row as literal historical precompute evidence.
Any later replacement must use a fresh repaired-Core namespace.

## FAST64 precomputed closeout recovery and repaired ATAX/IO dispatch (2026-09-10)

FAST64.1 and FAST64.2 remain PASS; FAST64.3 remains ACTIVE and FAST64.4
remains physical precomputation.  Seven terminal bbcbb rows whose original
monitor had written only an early `WAIT_TERMINAL` marker were strict-collected
with a future-only v2 collector into distinct `*_recovered_v2.json` files:
2DConvolution/IO, DWT2D/IO+OO, Gaussian/IO+OO, and LUD/IO+OO.  All retain their
literal original identity and are only
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`; none is a FAST64.4 result or a
mixed-identity triplet.  The original locks, monitors, raw outputs, and the
known Hotspot1 bbcbb IO/OO failures were preserved.  Details are in
`fast64/handoffs/FAST64_PRECOMPUTED_CLOSEOUT_RECOVERY_V2.md`.

A new three-window V2 resource audit authorized two workers with no sampled
swap-out/OOM/PSI/throttling.  One nonduplicative repaired-Core row was ready:
ATAX/IO started under Core `95ccdb7a...`, runtime `462d105c...cc4dbc9`, A1,
and immutable attempt `9c740af2-0d06-4f8a-b2b1-439128a39fa5` on CPU 6.  It is
CPU-active with its separate read-only v2 terminal collector.  The other
admission slot remains intentionally unused: all remaining FAST64.3 Base
requirements are already accepted, active, or have source-authorized literal
reuse, so a duplicate scientific row would add no valid evidence.

Btree/Base subsequently reached natural exit `0` and completed its common
repaired-Core Base/IO/OO strict triplet at 369,977 / 244,231 / 172,795 cycles
and common 444,467,849 instructions.  Its Base structural companion records
balanced lower lifecycle, cap-full zero, 590 cacheline-reservation events,
1,622,927 MSHR-entry-full events, and no MSHR-merge or downstream-full event.
It is still `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`, not a stage promotion.

## FAST64 repaired-Core eight-row ramp (2026-09-10)

After the repaired-Core identity transition, the three-window audit
`/tmp/fast64-repaired-ramp-audit-20260910T100407Z.tsv` authorized eight new
workers: zero swap-out, major faults, OOM, PSI and CFS-throttling deltas;
218,369,044,480 bytes cgroup memory headroom; 98,321,244,160 bytes
`MemAvailable`; and 123,047,563,264 bytes output free.  It used only
8.40--8.72 cgroup CPU-core equivalents of the 384-core quota.

Eight fresh immutable-v2 repaired-Core rows are active under exact
`95ccdb7a...` / `462d105c...cc4dbc9` / A1 / frozen Framework and payload
identities: Btree Base/IO/OO (`f4c5dbe9...`, `002abb01...`, `49062c94...`),
MRI-Q Base/IO/OO (`53d3653f...`, `add9ada3...`, `e32fff64...`), ATAX/OO
(`e05083ea...`) and GESUMMV/OO (`023b0b17...`).  They use isolated
`/workspace/fast64-repaired-ramp/fast64_*_core95ccdb7a_a1_r1` namespaces and
physical CPUs 5/6/7/8/9/10/13/18. Initial true leaf inspection finds all eight
CPU-active (96--99%), RSS 0.56--4.20 GiB, and no assertion/fatal/deadlock/
output-mismatch signature.  They are physical precomputes only under
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`; no FAST64.3/4 promotion is claimed.
Existing old-Core processes/controllers were neither modified nor relabelled.
Future-only `collect_fast64_repaired_ramp_v1.sh` provides terminal-only strict
closeout for exactly this wave. Its default dry run returned
`WAIT_TERMINAL` for all eight and created no compact result; `--collect` is
required before it invokes the repaired-Core v2 validator after a natural
immutable terminal receipt.

## FAST64 current parallelism / Gaussian closeout reconciliation (2026-09-10)

FAST64.1 and FAST64.2 remain PASS; FAST64.3 remains ACTIVE and FAST64.4
remains physical precomputation only.  A fresh three-window, read-only V2
admission audit is retained at
`/tmp/fast64-review-parallelism-20260910T094045Z.tsv`.  It observed `0`
swap-out pages, `0` major faults, `0` OOM kills, `0` memory PSI and `0` CFS
throttling across all windows; the cgroup used 11.47--11.71 CPU-core
equivalents out of 384, with 230,305,792,000 bytes cgroup headroom,
75,037,433,856 bytes `MemAvailable`, and 124,287,619,072 bytes output free.
It therefore authorizes up to eight *future* additional workers.  This is a
scheduling authorization only; no live process/controller was changed and
new old-Core FAST64.4 dispatch remains deferred until the repaired-Core
identity boundary closes.

Gaussian/IO and Gaussian/OO both naturally exited `0` under their immutable
bbcbb/A1/formal-runtime identities and wrote canonical strict JSON records:
`generated/fast64_4_precomputed_rows_v1/fast64_4_gaussian_{io,oo}_cap8192_a1_v3.json`.
They record respectively `3,815,204` / `3,818,467` cycles at common
`283,685,120` instructions, with clean required simulator log scans.  The
initial v2 collector successfully wrote and validated both JSON files, then
exited before its final PASS line because it treated the absent optional
`simulator.launcher.log` as a required `rg` input.  This is a host-only
closeout-marker defect, not a simulator failure.  Frozen v2 remains untouched
for its live GEMM users.  Future-only
`monitor_fast64_precomputed_row_v3.sh` scans the required stdout/stderr and
the launcher log only if present; syntax and a Gaussian/IO replay pass, whose
output SHA-256 exactly matches the canonical IO JSON
`0774d66aa058762a58bd4461e243d93030d631633f68c8cd1a79a6aa1798747f`.
Both Gaussian rows are strictly
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`, never accepted FAST64.4 evidence.

The common repaired-Core Hotspot1 triplet is now strict-valid under Core
`95ccdb7a...` and runtime `462d105c...cc4dbc9`: Base/IO/OO naturally exit `0`,
have common immutable payload/trace/A1/Framework identity, and pass the
immutable triplet validator. They record `160,486` / `85,206` / `83,439`
cycles at common `377,291,004` instructions. The repaired Base is exact against
the historical bbcbb Base on cycles, instructions, PIB/lower lifecycle,
terminal state and lower-cap-full. The finalized explicit reuse/invalidation
authority is `fast64/handoffs/FAST64_ZERO_ACCESS_CORE_REPAIR_IDENTITY_MAP.md`:
new formal rows use repaired Core/runtime, while historical bbcbb rows retain
their literal identity and can be reused only under that map. Stage promotion
remains separately gated.

## FAST64.3 Gaussian/Base and MRI-Q/Base strict terminals (2026-09-10)

Fresh immutable Gaussian/Base (`3ec79940-ae70-444a-8991-816d6f570223`) and
MRI-Q/Base (`4549f146-690a-4c32-be7f-ac8a8b363d3d`) both naturally exited `0`
and passed the future-only strict v2 collector with the frozen bbcbb/runtime/
A1/framework/Base-config identities. Gaussian records `4,229,815` cycles and
`283,685,120` instructions, lower acquire/release `1,951,815/1,951,815`, PIB
admit/retire `743,656/743,656`, terminal lower/PIB `0/0`, and cap-full `0`.
MRI-Q records `366,667` cycles and `1,411,757,056` instructions, lower
acquire/release `62,208/62,208`, PIB admit/retire `21,792/21,792`, terminal
lower/PIB `0/0`, and cap-full `0`. Both error scans are empty and their compact
strict/dynamic/structural evidence is retained under
`fast64/generated/fast64_3_dynamic_base_v1/` as
`STRICT_VALID_PENDING_STAGE_ACCEPTANCE`.

FAST64.3 is still active: 2DConvolution/Base remains live and Btree/Base is
queued behind its existing read-only continuation; no stage PASS is claimed.

## FAST64.4 Hotspot1 IO/OO source-reachable failure (2026-09-10)

Hotspot1 IO and OO physical precomputes remain preserved but are
non-authoritative failed attempts: their immutable-v2 attempts
`de96e9b8-eea8-4f2f-a179-b0d4b4a7f472` (IO) and
`0fdfa2a2-e9fb-427f-a8dd-97c412172ef8` (OO) each terminated `1` in seconds at
the same bbcbb `shader.cc:4279` `n_accesses > 0` assertion. They use the
frozen Hotspot1 payload, Core/runtime/A1/framework identities and distinct
correct IO/OO configs; they are not parser/accounting/results and will never
enter FAST64.4 aggregates. Hotspot1/Base with the same payload/identity is
strict-valid, isolating a mode-specific source-reachable empty-access issue.

The source-backed classification and isolated repair boundary are recorded in
`fast64/handoffs/FAST64_4_HOTSPOT1_ZERO_ACCESS_FAILURE.md`. Existing live
bbcbb rows and their frozen controllers are untouched. FAST64.1 and FAST64.2
remain closed (`FAST64_1_PLATFORM_PASS`, `FAST64_2_REPAIR_PASS`); FAST64.3 is
active and FAST64.4 is physical precomputation only.

The isolated minimal Core guard has now completed the exact Hotspot1 IO trace
naturally (`85,206` cycles; `377,291,004` instructions) with zero stderr,
closed lower/dependency accounting, and final IO PIB/inflight/lower `0/0/0`.
It is a repair qualification only, built from uncommitted isolated source and
therefore cannot be promoted or mixed with bbcbb formal evidence. A later
60-second one-worker audit passed (`swap_so_delta=0`, no OOM/PSI/throttle,
about 212 GiB cgroup headroom and 124 GiB output free), so the matching exact
Hotspot1/OO qualification is active in the fresh isolated namespace
`/workspace/fast64-repair-qual/hotspot1_oo_zero_access_guard_r0` on CPU 29.
It is likewise not a formal FAST64 row and has no result claim before natural
terminal lifecycle validation.

## FAST64.4 LUD IO/OO physical-precompute strict terminals (2026-09-10)

LUD/IO (`ad50c217-c4cc-4cf4-a514-91a368509f03`) and LUD/OO
(`ce6a4a2b-8986-4d3d-b8e0-c40f8141f76e`) naturally exited `0` and passed the
future-only v2 strict collector. Both preserve the frozen bbcbb/runtime/A1/
scientific-Framework/payload identities, one immutable execution epoch, empty
failure scans, lower create/issue/response conservation, dependency
create/complete conservation, and final PIB/inflight/lower state zero; OO also
ends with active refs zero. IO records `1,089,813` cycles and OO `1,086,338`,
each with `184,963,840` instructions. Their compact records are
`generated/fast64_4_precomputed_rows_v1/fast64_4_lud_{io,oo}_cap8192_a1_v3.json`.
They are strictly `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`: FAST64.4 has not
opened logically and no performance/triplet promotion is claimed.

## FAST64 future-wave parallelism recalibration (2026-09-10)

A read-only live inventory records 9 current FAST64 workers: 8 formal bbcbb
rows and the isolated Hotspot1/OO repair qualification. The formal-worker RSS
p50/p95/max is `644 MiB` / `4.79 GiB` / `4.79 GiB`; total live simulator RSS,
including two unrelated VM-TLB simulations, is about `18.0 GiB`. The cgroup
has a `384`-core quota, about `209 GiB` memory headroom, `~81 GiB`
MemAvailable, `~116 GiB` output capacity, zero CFS throttling and zero memory
PSI; iowait was `0.38%`. A 20-worker total FAST64 target is resource-safe by
the measured p95 planning model, subject to staged post-expansion evidence.

Future-only `util/dtc_l1/audit_fast64_future_precompute_resources_v2.sh`
supersedes v1 for new admission decisions. It retains every sampled
swap/major-fault/cgroup-I/O/PSI/OOM/CPU observation and classifies one positive
swap window as `TRANSIENT_SWAP_ACTIVITY`; only repeated positive windows are
`SUSTAINED_SWAP_ACTIVITY` and a pressure rejection. Its initial two-window
audit observed zero swap-out, major faults, PSI, OOM, and throttling. No live
controller or frozen closeout dependency was changed. To avoid avoidable Core
identity migration, unused capacity remains reserved for the Hotspot repair,
remaining Base work, and repaired-Core regression preparation rather than a
large old-bbcbb FAST64.4 wave before the repair is qualified.

## FAST64 Hotspot1 zero-access repair adopted / common triplet active (2026-09-10)

The isolated exact Hotspot1 repair qualifications now pass in both DTC modes.
PAPER_IO records `85,206` cycles and PAPER_OO `83,439`, each at
`377,291,004` instructions with clean stderr/failure scans, balanced lower and
dependency lifecycles, and zero terminal state. The minimal, source-local guard
is committed on the active Core branch as `95ccdb7a…`; a fresh trace-enabled
Release formal runtime is SHA-256 `462d105c…cc4dbc9`.

Fresh immutable Hotspot1 Base/IO/OO rows are active under that one common
Core/runtime on CPUs 5/6/8. They retain the frozen trace/config/A1/scientific
Framework identities and are classified
`REPAIRED_CORE_FORMAL_QUALIFICATION_PENDING_IDENTITY_MAP_FINALIZATION` until
all strict collectors and the explicit reuse/differential map close. Existing
bbcbb raw/results remain preserved and are neither relabelled nor mixed.

## FAST64.3 active Base promotion / acquisition state (2026-09-10)

The exact-identity Base promotion audit accepts ATAX, BICG, GESUMMV, GEMM and
DWT2D (5/12), including BICG's separately extracted canonical-perf structural
companion. Historical NN Base was deliberately not reused because it lacks the
current frozen Framework execution identity. Its fresh immutable replacement
`fast64_3_NN_base_cap8192_a1_v2` naturally exited `0` and is strictly collected
with cycles/instructions `6,985/1,284,872`, lower `10,691/10,691`, PIB
`4,011/4,011`, final lower/PIB `0/0`, and lower-cap-full `0`; compact strict
and structural evidence is under `generated/fast64_3_dynamic_base_v1/`.
NN is `STRICT_VALID_PENDING_STAGE_ACCEPTANCE`, not a FAST64.3 PASS claim.

LUD/Base is now a second fresh strict-valid row, not yet a stage PASS claim:
immutable attempt `3a5f2814-bfb6-4f77-84c0-8c860d93b6e4` naturally exited `0`
and records `1,113,878/184,963,840` cycles/instructions, lower
`1,048,098/1,048,098`, PIB `373,488/373,488`, terminal lower/PIB `0/0`, and
lower-cap-full `0`.  Its compact strict, dynamic, and structural evidence is
`generated/fast64_3_dynamic_base_v1/fast64_3_LUD_base_cap8192_a1_v2.json`,
`FAST64_3_LUD_BASE_DYNAMIC_V1.tsv`, and
`FAST64_3_LUD_BASE_STRUCTURAL_METRICS_V1.json`.  The formal identity is the
frozen Core/runtime/A1/framework tuple and frozen LUD payload; its status is
`STRICT_VALID_PENDING_STAGE_ACCEPTANCE`.

Hotspot1/Base is a third fresh strict-valid row, also pending the full-stage
acceptance: immutable attempt `409dbf6b-9a36-41c8-8c34-4aad51e6154a` naturally
exited `0` with `160,486/377,291,004` cycles/instructions, lower
`701,725/701,725`, PIB `161,336/161,336`, terminal lower/PIB `0/0`, and
lower-cap-full `0`. Its compact evidence is the Hotspot1 triple under
`generated/fast64_3_dynamic_base_v1/`.  This is the frozen formal
Core/runtime/A1/framework identity and source payload, with status
`STRICT_VALID_PENDING_STAGE_ACCEPTANCE`.

2DConvolution/Base plus fresh Gaussian/Base and MRI-Q/Base are immutable and
CPU-active. Btree/Base remains reserved for the existing single-slot
continuation after 2DConvolution naturally terminates. No active row has an
assertion/fatal/actual-deadlock/output-mismatch signature.

The four-worker admission audit
`/tmp/fast64-future-wave4-audit-20260910T0807Z.tsv` passed: sampled swap-out,
OOM, memory-PSI and CFS throttling are zero; cgroup headroom is about 194 GiB
and output free space about 117 GiB. It admitted Gaussian (CPU 5), Hotspot1
(CPU 6), LUD (CPU 7), and NN (CPU 8) under distinct immutable attempt UUIDs.
This replaces the earlier arbitrary one-worker operational limit with a
measured-safe wave; it changes no scientific identity.

The generic v1 closeout monitor invokes the non-executable Python validator as
an executable and therefore cannot close a terminal row. It remains untouched
while live. Future-only `monitor_fast64_precomputed_row_v2.sh` invokes the
same frozen validator through `python3`; its static regression and NN
integration strict collection pass. This is a host-only controller repair, not
a parser/configuration/mechanism change.

The seven-row pool and every canonical workload dry-run pass using the
future-only alias-v3 validator, which keeps frozen validator/manifest bytes
unchanged and fixes lookup casing only. Two 60-second resource audits correctly
refused launch due to swap-out (`2289` for seven workers; `222` for one); no
FAST64 simulation was started and the shared VM-TLB jobs were not disturbed.

A subsequent one-worker audit passed with zero sampled swap-out and admitted
only the first missing Base row: 2DConvolution/Base in immutable namespace
`fast64_3_2DConvolution_base_cap8192_a1_v2`, attempt
`844f1ba7-58a9-4208-98e5-71e01b1a6885`, CPU 0. Its one-worker dynamic pool
exited after dispatch because it read the headered `supervisor_pid` field as
column one. The live immutable runner was not touched. Future-only
`continue_fast64_dynamic_pool_v3.sh` (SHA-256
`9fe78b45e048e97534cd4179b71d12b789a86d3c52cdabc91c6cdc678c6418c1`) now
adopts that live row read-only, corrects the header-aware receipt parse, and
will strict-validate its natural terminal before it refills Btree. No formal
result is claimed while the row is live. Separate future-only observer
`monitor_fast64_3_dynamic_base_evidence_v1.py` (SHA-256
`3d437ff5b8470ab0eee0ec1de576b6a7e6b601320e986d59c64df32a52ef7dd5`) waits
for that strict summary before materializing compact JSON/TSV evidence and its
source-defined Base structural companion; it never writes live run state.

The LUD natural terminal freed CPU 7.  A fresh measured admission audit
`/tmp/fast64-future-lud-terminal-refill-audit-20260910T082614Z.tsv` authorized
exactly one worker (zero sampled swap-out/OOM/PSI/throttle, about 190 GiB
cgroup headroom, and about 117 GiB output free).  It dispatched only
`fast64_4_lud_io_cap8192_a1_v3`, immutable attempt
`ad50c217-c4cc-4cf4-a514-91a368509f03`, on CPU 7 with a separate v2 collector.
This is physical precomputation under
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`; it is neither a FAST64.4 logical
opening nor an accepted performance row.

A second post-LUD/IO audit
`/tmp/fast64-future-post-lud-io-refill-audit-20260910T083209Z.tsv` again
admitted exactly one worker with zero sampled swap-out/OOM/PSI/throttle.
`fast64_4_2DConvolution_io_cap8192_a1_v3` is therefore active on CPU 16 under
immutable attempt `7ae2c41b-a4f1-444c-bade-ae93dbc6293e` and its independent
v2 collector.  It carries the same physical-precompute classification and is
not an accepted FAST64.4 row while live.

The next two-worker audit
`/tmp/fast64-future-two-worker-refill-audit-20260910T083444Z.tsv` also passed
with zero sampled swap-out/OOM/PSI/throttle.  It dispatched
`fast64_4_2DConvolution_oo_cap8192_a1_v3` on CPU 17 (attempt
`7e6c31bb-6887-4117-850c-6a3b2bc2764e`) and
`fast64_4_gaussian_io_cap8192_a1_v3` on CPU 18 (attempt
`5251ab7f-13b1-43dc-9b7d-0434ef498817`), each with a separate v2 collector.

The active FAST64.4 physical-only wave is ATAX/IO; GEMM/IO and GEMM/OO;
DWT2D/IO and DWT2D/OO; LUD/IO; 2DConvolution/IO and 2DConvolution/OO; and
Gaussian/IO.  Every member is an isolated immutable-v2 attempt under
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`; none is a logical FAST64.4 result
until the FAST64.3 gate and later primary-matrix acceptance both pass.

DWT2D/IO and DWT2D/OO have since naturally exited `0` and passed their
independent v2 strict collectors. Their immutable attempts are respectively
`257ccf84-1651-4116-a36d-b8227a4e1548` and
`8d866b57-202e-4386-b221-b1b418d68735`; both retain the frozen formal identity,
one execution epoch, clean failure scan, `148,684,429` dynamic instructions,
final lower `0`, and lower-cap-full `0`.  The IO row records `241,380` cycles
and zero IO lower-create-queue-full stalls; the OO row records `234,651`
cycles, zero OO lower-create-queue-full stalls, and final OO active refs `0`.
Their compact JSON evidence is retained under
`generated/fast64_4_precomputed_rows_v1/` as
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`, not as an accepted FAST64.4 triplet.

After those DWT2D terminals, the four-worker audit
`/tmp/fast64-future-four-worker-refill-audit-20260910T083734Z.tsv` admitted a
new isolated wave: Gaussian/OO on CPU 22 (attempt `40293c57…`), Hotspot1/IO
on CPU 23 (attempt `de96e9b8…`), Hotspot1/OO on CPU 24 (attempt `0fdfa2a2…`),
and LUD/OO on CPU 25 (attempt `ce6a4a2b…`).  All four retain exact frozen
identity and independent immutable-v2 collectors, and all remain physical
precomputes pending FAST64.3 acceptance.

## FAST64.4 physical precompute — ATAX/IO active (2026-09-10)

A fresh 60-second `FAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_V1` admitted one
additional isolated worker (`swap_so_delta=0`, OOM/PSI/throttle deltas zero,
about 126 GB output free). The first ATAX/IO dispatch
`fast64_4_atax_io_cap8192_a1_v2` is retained as a non-authoritative
pre-simulation launch failure: it used a relative config path, so the
immutable runner changed to its run directory and the simulator immediately
exited `1` before an execution epoch. It produced no scientific result.

Its fresh repair `fast64_4_atax_io_cap8192_a1_v3` uses the same frozen,
absolute FAST64_IO config (SHA-256 `d4a2d9d0...`), payload, Core/runtime/A1
and framework identities; immutable attempt
`105ec7d4-8330-4493-b09a-0f3c2b6d402d` runs on CPU 3 under
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`. It is physically acquired only:
FAST64.4 is not logically open and no result is claimed while live.

## FAST64.2 repair qualification PASS (2026-09-10)

FAST64.2 is `FAST64_2_REPAIR_PASS`. The source-reachable diagnostic
`fast64_2_nn_io_coupled_cap1_pib1_a1_v1` naturally exited `0` under the
immutable-v2 receipt chain and strict validation. Its diagnostic-only cap-1,
IO-entries-1 overlay records `31,399,562` global lower-cap-full events and
`31,105,381` IO lower-create-queue-full stalls, while closing lower
create/issue/response at `2,673/2,673/2,673`, dependencies at `5,346/5,346`,
and final inflight/PIB/lower state at `0/0/0`. It has `564,234` cycles and
`1,284,872` instructions, with an empty assertion/fatal/actual-deadlock/output
mismatch scan.

The cap-1 row is a source-backed diagnostic only: it does not alter the
formal 8192-cap platform or enter performance aggregates. The retained
high-cap BICG negative control and immutable R2 BICG Base/IO/OO normal-triplet
reuse complete the FAST64.2 acceptance set. Compact evidence and the full
checklist are in `fast64/handoffs/FAST64_2_REPAIR_QUALIFICATION.md` and
`fast64/generated/fast64_2_coupled_stress_cap1_v1/`.

## FAST64.1 immutable R2 full-wave PASS (2026-09-10)

FAST64.1 is `FAST64_1_PLATFORM_PASS`. All seven immutable-v2 R2 rows naturally
exited `0`, have one atomic START/TERMINAL attempt UUID and one natural-exit
epoch, and strict-validate with formal Core `bbcbb5e...`, runtime
`6a8743b4...`, A1 observer `2c2a6a27...`, scientific Framework snapshot
`037f008b...`, the frozen payload, and resolved config identity. Required
terminal lower/dependency/drain state is closed and error scans are clean.

R2-vs-R2 BICG/IO, BICG/OO, and GESUMMV/IO 8192-vs-high comparisons are each
`EXACT_METRIC_MATCH`; every required 8192 candidate records
`DTC_L1_lower_cap_full_events = 0`. This freezes the unchanged 64x1 platform,
payload, DTC configuration, and cap-8192 non-binding conclusion.

The frozen full-wave reader was preserved unchanged and fail-closed on its
known alias defect: it counts the normal `perf_counter.csv.gz` symlink as a
second perf stream. Its final retained log SHA-256 is
`f3c1cd810d4d86d6a62274655b855967e6994abb84b850d1f84e65f7ba545ea2`.
Future-only alias-v2 verifies that each optional alias resolves to the one
canonical timestamped stream, preserving—not weakening—single-epoch proof.
The compact row JSONs, comparison TSVs, PASS marker, and SHA manifest are in
`fast64/generated/qualification_r2_full_wave_alias_v2/`.

FAST64.2 is now active. The existing coupled stress remains strict-negative
pressure evidence; no FAST64.2 PASS is claimed. Disk headroom is about 45 GiB
at 99% use, so storage inventory/retention proof is the immediate operational
task before any large later-stage wave.

## FAST64.3 ATAX/Base natural terminal — strict-valid precompute (2026-09-09)

The future-only immutable-v2 ATAX/Base precompute
`fast64_3_precomputed_atax_base_cap8192_a1_r2` naturally exited `0` at
`2026-09-09T01:26:57Z`.  Its separate alias-aware v3 collector records one
immutable attempt (`2e51d286-4483-45fd-8795-dd19fcd413c4`), normal simulator
exit, an empty precise assertion/fatal/deadlock/output-mismatch scan, and one
canonical perf epoch (with the normal alias normalized).  The bound identity
is Core `bbcbb5e...`, runtime `6a8743b4...`, A1 observer `2c2a6a27...`,
execution snapshot `037f008b...`, Base config `1a016e3c...`, and frozen ATAX
trace-list `b6dcd0e3...`.

Compact evidence under `fast64/generated/fast64_3_atax_base_alias_v3/` closes
lower acquired/released at `19,215,755/19,215,755`, PIB admits/retires at
`3,145,984/3,145,984`, and terminal lower/PIB at `0/0`; it records
`87,750,512` cycles and `145,666,048` instructions.  The structural companion
keeps cacheline allocation (`1,349,272,650`), MSHR-entry (`0`), miss-queue
(`1,070`), and Tag-bank (`20,972,288`) categories distinct.  Its sole status
is `FAST64_3_BASE_PRECOMPUTED_STRICT_VALID_PENDING_FAST64_1_2_ACCEPTANCE`:
this neither promotes FAST64.3 nor authorizes IO/OO work.

The FAST64.1 R2 closure is unchanged: it remains **5/7** terminal, with both
GESUMMV IO rows CPU-active and the frozen closeout controller waiting.  A
fresh resource audit is fail-closed for another worker (swap essentially full,
load above the 512 logical CPUs, and only about 56 GiB output free), so neither
the optional FAST64.2 stress nor another FAST64.3 row is launched.

## FAST64.2 BICG coupled stress and FAST64.3 GEMM/Base terminals (2026-09-08)

The immutable BICG/PAPER_IO coupled-stress fallback (`cap=512`, source-coupled
IO PIB entries `1`) naturally exited `0` at `2026-09-08T21:51:34Z`. Its
future-only alias-aware collector proves one immutable epoch, exact frozen
identity, clean failure scan, lower create/issue/response conservation
(`17,607,590` each), dependency conservation (`18,350,080` each), and final
IO inflight/PIB/lower `0/0/0`. Both required pressure observations remain zero:
`DTC_L1_lower_cap_full_events=0` and
`DTC_L1_io_lower_create_queue_full_stalls=0`. It is therefore
`FAST64_2_BICG_COUPLED_STRESS_STRICT_NEGATIVE_PRESSURE_ABSENT`, not a
FAST64.2 PASS; compact evidence is
`fast64/generated/fast64_2_coupled_stress_bicg_alias_v2/`.

GEMM/Base also naturally exited `0` at `2026-09-08T23:15:14Z` and is strictly
valid only as FAST64.3 physical precomputation: cycles/instructions
`2,662,394/739,246,080`, lower acquired/released
`16,813,388/16,813,388`, PIB admits/retires `12,599,296/12,599,296`, final
lower/PIB `0/0`, and lower-cap-full `0`. Its independent future-only v4
collector and structural companion are compact evidence under
`fast64/generated/fast64_3_gemm_base_alias_v4/`; this does not promote
FAST64.3 or authorize an expanded batch.

The fresh resource audit is fail-closed for additional work: swap is fully
used, load is about `569` on `512` logical CPUs, and output free space is
about `55 GiB`. No new worker is launched. The frozen FAST64.1 R2 closure
bytes retain their recorded hashes; R2 remains **5/7** natural terminals with
the two GESUMMV IO rows live and the unmodified frozen controller waiting.

## FAST64.1 fifth immutable-R2 natural terminal (2026-09-08)

`fast64_1r2_bicg_io_cap1048576_a1` (BICG / PAPER_IO / cap 1048576)
naturally exited `0` at `2026-09-08T22:48:52Z`. Its atomic immutable-v2
START/TERMINAL receipts agree on attempt
`661b4953-6045-4bc6-8943-9a0f6d90c35b` and runner `bf9a84c8...`; the
manifest binds Core `bbcbb5e...`, runtime `6a8743b4...`, A1 observer
`2c2a6a27...`, execution snapshot `037f008b...`, frozen IO-high-cap config
`c0d169b8...`, and canonical BICG trace-list `388740a7...`. The simulator
emitted its normal exit sequence, and the precise assertion/fatal/deadlock/
output-mismatch scan is clean.

R2 receipt state is now **5/7 natural terminals**, with GESUMMV
IO@8192/@1048576 remaining live. The frozen R2 controller remains untouched
and is the sole authoritative full-wave collector after 7/7. This is a
pending natural-terminal observation only, not individual strict validation,
cap-comparison acceptance, or FAST64.1 PASS.

## FAST64.1 fourth immutable-R2 natural terminal (2026-09-08)

`fast64_1r2_bicg_oo_cap8192_a1` (BICG / PAPER_OO / cap 8192) naturally
exited `0` at `2026-09-08T18:43:49Z`.  Its atomic immutable-v2 terminal
receipt identifies attempt `89d2c798-e66c-4e8d-8dfd-df26d01ff9f7`, runner
`bf9a84c8...`, Core `bbcbb5e...`, runtime `6a8743b4...`, A1 observer
`2c2a6a27...`, execution snapshot `037f008b...`, frozen OO config
`546c68f9...`, and canonical BICG trace-list `388740a7...`.  The direct
simulator emitted the normal exit sequence, and the precise assertion/fatal/
deadlock/output-mismatch scan is clean.

R2 receipt state is now **4/7 natural terminals**, with BICG IO@1048576 and
GESUMMV IO@8192/@1048576 remaining live.  The frozen R2 controller is still
the sole authoritative full-wave collector after 7/7; this is only a pending
terminal observation, not individual strict validation, a comparison result,
or FAST64.1 PASS.

## FAST64.1 third immutable-R2 natural terminal (2026-09-08)

`fast64_1r2_bicg_oo_cap1048576_a1` (BICG / PAPER_OO / cap 1048576)
naturally exited `0` at `2026-09-08T18:19:06Z`.  Its atomic immutable-v2
terminal receipt is chained to attempt
`26b9fab6-0138-4750-923d-3d79a4b7f9df`, runner `bf9a84c8...`, Core
`bbcbb5e...`, runtime `6a8743b4...`, A1 observer `2c2a6a27...`, execution
snapshot `037f008b...`, its frozen OO-high-cap config, and the canonical BICG
trace-list SHA-256 `388740a7...`.  The direct simulator emitted its normal
exit sequence, stderr is empty, and the precise assertion/fatal/deadlock/
output-mismatch scan is clean.

This changes the R2 receipt state to **3/7 natural terminals**, with the four
remaining R2 rows still live.  The frozen R2 closeout controller remains
untouched and will perform the only authoritative strict collection after all
seven terminal receipts exist.  Consequently this record is a pending
natural-terminal observation, not individual strict validation, cap-comparison
acceptance, or a FAST64.1 PASS claim.

## FAST64 review-time safe-parallelism audit (2026-09-08)

The requested post-seven-row-R2, 60-second read-only admission audit is
`/tmp/fast64-post-r2-fullwave-safeparallel-audit-20260908T181439Z.tsv`.
It authorizes exactly one additional worker: zero sampled swap-out, cgroup
OOM, memory PSI, and CFS throttling; 245 available distinct physical-core
candidates; 197,735,043,072 bytes cgroup memory headroom; and
61,653,282,816 bytes output free space.  The five live R2 simulators remained
near one CPU core each during this observation.  This is an operational
capacity result, not a FAST64.1 acceptance result.

No duplicate NN coupled-stress process was launched.  The specifically named
NN/PAPER_IO, cap-512, PIB-1 immutable-v2 row already naturally exited `0` with
the exact frozen Core/runtime/A1-observer/config identity and was strictly
collected as `FAST64_2_COUPLED_STRESS_STRICT_NEGATIVE_PRESSURE_ABSENT`: both
required pressure counters were zero.  Repeating the identical NN row would
not add evidence.  Its authorized BICG/PAPER_IO fallback under the same
cap-512/PIB-1 source-coupled configuration was then live in an isolated
immutable-v2 namespace.  This is a historical launch snapshot: the BICG
terminal strict-negative result and GEMM/Base terminal are recorded at the top
of this report; only ATAX/GESUMMV Base remain live.  Nothing in the frozen R2
closeout dependency closure, any R2 process, or any active monitor was
changed.

## FAST64.3 DWT2D/Base strict-valid precompute (2026-09-08)

The isolated DWT2D/Base immutable-v2 row naturally exited `0` at
`2026-09-08T17:40:19Z`.  Its future-only v3 collector produced only compact
evidence under `fast64/generated/fast64_3_dwt2d_base_alias_v3/`: one canonical
perf epoch (with the normal alias normalized), exact frozen identity, positive
progress (`344,119` cycles; `148,684,429` instructions), lower
acquired/released `757,359/757,359`, PIB admits/retires `437,886/437,886`, and
terminal lower/PIB state `0/0`.  The precise failure scan is clean.  Its sole
status is `FAST64_3_BASE_PRECOMPUTED_STRICT_VALID_PENDING_FAST64_1_2_ACCEPTANCE`;
it is not a FAST64.3 PASS and it authorizes neither later-stage IO/OO rows nor
a performance claim.

A separate future-only structural-metric extractor now reads only the
canonical terminal perf row, leaving the frozen R2 parser unchanged.  Its DWT2D
regression resolves the relevant category semantics from Core source:
`LINE_ALLOC_FAIL` means conventional L1D cache lines are all reserved and is
not interchangeable with the diagnostic Tag-bank conflict counter.  The
compact companion records line-allocation `1,417,779`, MSHR-entry-full
`346,268` (exactly cross-checked with the terminal summary), MSHR-merge-full
`0`, downstream miss-queue-full `18,367`, and the already closed Base
lower-request lifecycle.  This improves future FAST64.3 metric completeness
only; it does not promote DWT2D or alter any live row.

The future-only structural-companion monitor is now prepared for ATAX,
GESUMMV, DWT2D and GEMM.  It requires a natural terminal receipt plus the
existing strict Base JSON before it extracts a companion exactly once; it
cannot create Base validity evidence or alter any active Base/R2 monitor.  Its
static/once regression confirms that live rows remain waiting-only and have no
premature companion output.

The current 60-second, read-only post-review admission audit was fail-closed:
although swap-out/OOM/throttling were zero and cgroup/output headroom remained
ample, `memory_psi_avg10=0.01`, so `safe_to_launch=NO`.  No replacement worker
was launched.  The seven R2 closeout bytes and live simulators remain
untouched.

## FAST64.3 GEMM/Base controlled replacement admission (2026-09-08)

After DWT2D naturally freed its worker, a new 60-second read-only resource
audit passed exactly one replacement: zero sampled swap-out/OOM/memory PSI/CFS
throttling, 246 candidate physical cores, 207.4 GiB cgroup headroom and 62.6
GiB output space.  The immutable-v2 dispatcher admitted only
`fast64_3_precomputed_gemm_base_cap8192_a1_r2`, GEMM/Base, at
`2026-09-08T17:45:33Z` on CPU 11 with UUID
`4b62ba62-9ee3-41ed-8a67-402172e594fa`.  This is a historical admission
snapshot; GEMM subsequently reached its terminal strict-valid precompute
state, recorded at the top of this report.

The existing live v3 monitor is left untouched.  A separate future-only GEMM
v4 collector/monitor pair passed static regression and waits only for GEMM's
atomic terminal receipt.  It cannot affect R2 or any active v3 row.  GEMM is
strictly `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE`, not a formal result or
stage advancement.

The first GEMM v4 monitor exited after its inherited caller stdout closed; its
simulator stayed CPU-active and untouched.  A bounded read-only reproduction
proved the monitor loop itself correct.  The same committed monitor was
relaunched in an independent session with stdout/stderr redirected to
`/dev/null`, retaining only its explicit log channel.  It survived a full
120-second poll and recorded the next wait state.  This is solely a monitor
lifecycle recovery, with no collection/promotion claim and no R2 dependency
change.

## Future-only FAST64.4 triplet consistency preflight (2026-09-08)

`validate_fast64_triplet_v1.py` now provides a fail-closed compact-JSON
validator for a later Base/IO/OO triplet.  It validates common payload and
trace-list identity, dynamic instruction-domain equality, per-mode drain and
conservation, and—in formal mode—immutable receipts plus common runtime/A1
observer identity.  Its synthetic immutable-fixture regression passes and its
deliberate instruction-mismatch fixture fails.  It is not connected to a live
controller and cannot promote any current precompute or stage.

## FAST64 controlled third Base admission and Base closeout recovery (2026-09-08)

A new 60-second post-small-batch audit at
`/tmp/fast64-post-smallbatch-resource-audit-20260908T172527Z.tsv` authorized
exactly one worker: it recorded zero swap-out/OOM/memory PSI/CFS throttling,
205.8 GiB cgroup memory headroom, and 62.7 GiB output space.  The immutable-v2
Base dispatcher therefore admitted DWT2D/Base only, on CPU 11, into
`fast64_3_precomputed_dwt2d_base_cap8192_a1_r2` at
`2026-09-08T17:26:51Z` with UUID
`adc75323-a985-4222-bc28-804e4a9dedad`.  Its START receipt and frozen identity
chain are present; it is CPU-active and classified solely as
`PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE`.

Read-only source/log inspection found that the active v2 ATAX/GESUMMV Base
collectors' broad `deadlock` pattern matches the normal
`-gpgpu_deadlock_detect` configuration-help echo.  The active monitor was not
edited.  Separate v3 collector/monitor files now use precise diagnostic
patterns and independently wait for atomic terminal receipts for ATAX,
GESUMMV, and DWT2D.  Their pre-terminal regression passed.  No Base result is
promoted and no R2 closeout byte or live simulator was changed.

## FAST64 frozen R2 alias defect and F2 negative evidence (2026-09-08)

The frozen R2 validator's single-epoch glob counts a normal simulator symlink
alias (`perf_counter.csv.gz`) in addition to its sole timestamped perf stream.
Read-only inode/initialization evidence proves this is one epoch, but the
frozen validator rejects it as two streams. The frozen R2 collector also asks
the parser for lower-cap configuration, although the cap is source/config
identity rather than a terminal metric. Neither frozen byte was changed. A
versioned alias-aware reader is prepared and documented in
`fast64/handoffs/FAST64_1_R2_PERF_ALIAS_VALIDATOR_RESOLUTION.md`; it may only
become relevant after the existing frozen controller has fail-closed at 7/7.

The newly acquired immutable FAST64.2 NN/IO coupled stress has now been
strictly collected with a future-only alias-aware reader. It naturally exited
0, has one immutable epoch, exact identity, lower create/issue/response
conservation (`2673`), dependency conservation (`5346`), and drained final
state. Its required pressure events are both zero
(`lower_cap_full_events=0`, `io_lower_create_queue_full_stalls=0`), so it is
`FAST64_2_COUPLED_STRESS_STRICT_NEGATIVE_PRESSURE_ABSENT`, not FAST64.2 PASS.
The compact evidence is
`fast64/generated/fast64_2_coupled_stress_alias_v2/`; this ordinary
source/configuration-pressure diagnosis does not alter R2 semantics or any
frozen closeout dependency.

A later fresh 60-second admission at
`/tmp/fast64-future-precompute-audit-20260908T164959Z-for-f2-recheck.tsv`
returned `safe_to_launch=YES` for exactly one worker: sampled swap-out,
cgroup OOM and memory PSI were zero, with 191.8 GiB cgroup headroom and 58.5
GiB output space.  The researcher-authorized BICG fallback is therefore now
physically acquired, not inferred: `fast64_2_precomputed_bicg_io_coupled_cap512_pib1_a1_r2`
started at `2026-09-08T16:51:44Z` on CPU 9 with immutable attempt UUID
`24e4fff0-e2c5-4832-b8d6-fec5ae911249`.  This is a historical launch snapshot:
the row subsequently naturally terminated and was strictly collected as the
negative-pressure result recorded at the top of this report.  It has no
FAST64.2 PASS or R2-dependent stage transition claim.

The BICG row also has a dedicated future-only closeout monitor.  It observes
only the immutable terminal receipt, then invokes the existing BICG strict
collector once and checks for its compact evidence; it cannot launch, signal,
restart or promote a row.  Its once-mode pre-terminal regression confirms that
it only records a wait state before a terminal receipt exists.

## FAST64.3 controlled two-row Base precompute, pending (2026-09-08)

`prepare_fast64_3_base_precompute_v2.sh` is a future-only immutable-v2,
topology-aware one-row Base dispatcher. It permits only the ten nonredundant
FAST12 candidates while preserving potential BICG/NN evidence reuse. Its ATAX
dry-run passed. The earlier rejected audit is retained as evidence; a later
60-second audit at
`/tmp/fast64-future-precompute-audit-20260908T153334Z.tsv` observed zero
swap-out/OOM/memory-PSI/throttling, 249 distinct physical-core candidates, and
adequate memory/output headroom, returning `safe_to_launch=YES` for exactly
one worker. It admitted only `fast64_3_precomputed_atax_base_cap8192_a1_r2`
on CPU 0, with immutable runner UUID
`2e51d286-4483-45fd-8795-dd19fcd413c4` and classification
`PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE`. The START receipt exists and the
initial failure scan is empty. This live row remains nonformal pending work and
cannot advance FAST64.3 or interfere with FAST64.1 R2 closeout.

The final frozen A1 `runtime_stat=500000` has flag zero: it suppresses
human-readable runtime-stat output but emits a perf-counter stream only after
each 500,000 simulated-cycle boundary. Before that first boundary, host
CPU-time progress was the available liveness evidence.

ATAX has since crossed two perf boundaries (500,000 and 1,000,000 simulated
cycles; 386,656 and 675,008 instructions).  Its provisional launch-to-second-
point lower-bound rate is about 1,299 cycles/s and 877 instructions/s, while
all five R2 workers retained about 99.4--99.5% CPU.  The required fresh expansion audit
nevertheless failed solely on `swap_so_delta=103`, so no second Base worker
was launched.

A subsequent independent 60-second admission audit at
`/tmp/fast64-future-precompute-audit-20260908T155148Z-after-atax15m.tsv`
returned `safe_to_launch=YES` for exactly one additional worker: zero sampled
swap-out/OOM/memory-PSI/throttling, 181 GiB cgroup memory headroom and 57.5
GiB output space.  It was taken only after ATAX had crossed its 1,500,000-cycle
perf boundary and the five live R2 simulators remained CPU-active.  The
future-only dispatcher then admitted exactly one nonredundant row,
`fast64_3_precomputed_gesummv_base_cap8192_a1_r2`, on CPU 3 at
`2026-09-08T15:53:37Z`; its immutable attempt UUID is
`c4d6d35e-23ad-4466-b578-ed1f00eb2ee9`.  Its START receipt and source identity
chain are present, its simulator is CPU-active, and its initial
assertion/fatal/deadlock/error scan is clean (apart from configuration help
text mentioning the deadlock flag).  This is the only expansion: it remains
`PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE`, has no formal performance claim,
and does not alter any frozen R2 byte or controller.

The new GESUMMV row now has its own future-only strict collector,
`collect_fast64_3_gesummv_base_alias_v2.sh`.  It is deliberately separate from
all R2 closeout bytes and rejects before creating output unless a natural
terminal receipt exists.  Static syntax validation and a live-row
pre-terminal invocation both passed this fail-closed check; no run-directory
file or result artifact was created.  At natural terminal it will require the
immutable identity tuple, Base/cap identity, lower-credit and PIB
conservation, zero final lower/PIB state, positive cycle/instruction progress,
and an assertion/fatal/deadlock/output-mismatch scan before it can record only
the still-pending precompute classification.

A separate future-only Base closeout monitor is now prepared for the active
ATAX and GESUMMV namespaces.  It treats only an atomic `RUN_TERMINAL.tsv` as a
trigger, then invokes the corresponding strict pending collector once; it has
no launch, signal, restart or R2-closeout capability.  Its once-mode regression
proves pre-terminal rows are only observed, not collected.  It remains a
pending-evidence convenience and cannot promote FAST64.3.

For later post-FAST64.2 formal waves, the legacy mutable dynamic pool is now
explicitly superseded for future use by separate
`dispatch_fast64_precomputed_row_v2.sh` and `run_fast64_dynamic_pool_v2.sh`
files.  They verify the read-only SHA-addressed runner, runtime/Core/observer
and scientific-config identities, atomic immutable-v2 receipts and the R2
trace-config identity; they neither reference nor change the frozen R2
closeout bytes.  Their dry-run regression proves that a pending Base wave can
be planned without creating a namespace and that IO is refused before
FAST64.2 PASS.  No formal row was launched and no stage authority changed.

## FAST64.1 R2 closeout freeze and first natural terminals (2026-09-08)

The seven-row R2 closeout dependency closure is now frozen, byte-addressed in
`fast64/handoffs/FAST64_1_R2_CLOSEOUT_DEPENDENCY_FREEZE.md`, and must remain
unchanged until the existing closeout controller publishes
`FAST64_1_R2_FULL_WAVE_COLLECTOR_PASS`. This includes the controller,
collector, parser/validator/cap comparator, payload manifest, all R2 configs,
and R2 `trace.config`. Future work must use versioned controllers and only
read these bytes.

Two cohort-1 rows have naturally reached immutable terminal exit 0: BICG
Base@8192 at `2026-09-08T12:56:42Z` and BICG IO@8192 at
`2026-09-08T13:08:48Z`. Their receipt UUID/immutable-runner chain is intact;
the error scan found only configuration text and zero-valued invariant prints.
The five continuation R2 rows remain CPU-active. The untouched closeout
controller has observed `2/7` terminal receipts and remains the only route to
strict collection or FAST64.1 promotion.

## FAST64.1 five-row immutable-R2 continuation authorized (2026-09-08)

The researcher superseded the bootstrap two-worker ramp and authorized an
immediate five-row continuation wave, while preserving the two live cohort-1
R2 process trees and all existing SHA-pinned controllers unchanged. A new,
future-only one-shot dispatcher has a separate continuation lock and a fixed
five-row scope; it cannot touch the two existing namespaces. It verifies the
same immutable-v2 runner, Core/runtime/A1 observer/scientific-config identity
tuple, frozen config bytes, fresh namespace absence, unique UUID, atomic
receipts, and topology-aware explicit CPU placement.

The fresh 60-second cgroup audit at
`/tmp/fast64-r2-continuation-resource-audit-20260908T123617Z.tsv` passed full
five-worker admission: 12.822 useful core equivalents under a 384-core quota,
zero throttling/swap-out/OOM/memory-PSI, 252 distinct physical-core candidates,
18,647,875,584-byte 5+1 RSS requirement versus 203,603,755,008-byte cgroup
headroom, and 67,846,701,056 output-free bytes. Host loadavg is supplemental,
not a mixed-scope cgroup rejection. See
`fast64/handoffs/FAST64_1_R2_FULL_WAVE_CONTINUATION.md`. Admission is
authorized; dispatch receipts determine the next execution-state update.

The dispatch succeeded at `2026-09-08T12:41:22Z`: all five fixed future-only
rows received fresh immutable START receipts, so the complete R2 wave is now
**7/7 LIVE**. The rows are BICG OO@8192, BICG IO@1048576, BICG OO@1048576,
GESUMMV IO@8192, and GESUMMV IO@1048576, pinned to topology-selected CPUs
5/6/7/8/10. Their runner/Core/runtime/A1/scientific-config tuple exactly
matches cohort 1. The original Base@8192 and IO@8192 rows were neither opened
nor altered. A short follow-up found all seven direct simulator children in
state `R` at about 99% CPU, no growth in swap-out or OOM totals, zero memory
PSI and zero cgroup throttling. The two cohort-1 perf streams had progressed
to 82.0M and 88.0M cycles; new rows are live, not yet terminal results.

The existing autorefiller observed seven namespaces and recorded
`FAST64_R2_AUTOREFILL_DISPATCH_COMPLETE` at `2026-09-08T12:42:26Z`; it did not
create duplicates. The untouched strict closeout controller remains waiting
for 7/7 terminal receipts. FAST64.1 is still stage-gated pending natural
terminal/strict collector/comparison evidence. Compact per-row UUID/PID and
follow-up evidence is in `fast64/handoffs/FAST64_1_R2_FULL_WAVE_CONTINUATION.md`.

## FAST64.1 R2 dispatch-lock inheritance recovery (2026-09-08)

The first two immutable R2 supervisors inherited the dispatcher's advisory
lock descriptor.  Read-only `fuser` and `/proc/<pid>/fd/9` evidence ties the
lock to both live supervisor/process trees; this is an execution-controller
lifetime defect, not a simulator, DTC, configuration, or scientific-identity
defect.  The live rows are preserved untouched: there is no safe in-place FD
closure that does not perturb production processes, so the current lock will
release only when those rows naturally reach their terminal state.

The future-only dispatcher now closes FD 9 before `setsid` creates a detached
supervisor.  A disposable lock/sleep topology regression proves that the child
remains live while a second dispatcher can acquire the advisory lock; the
existing namespace mkdir, immutable SHA binding, UUID, receipts, and
single-epoch validator are unchanged.  This removes the issue for all rows
launched after the two live rows.  Status is
`FAST64_1_R2_RESOURCE_ADMISSION_PENDING` solely for this bounded lock lifetime;
FAST64 Goal execution remains active.  On either natural terminal event, take
a fresh resource audit and admit the next frozen-priority missing R2 row.
A low-frequency host-only `monitor_fast64_1_r2_autorefiller.sh` is active in
the `fast64-r2-autorefiller` persistent tmux controller: it holds a separate monitor lock, pins the reviewed
dispatcher SHA, waits for the live dispatch lock to disappear, performs the
same 60-second read-only audit, and invokes the dispatcher only for a fresh
`YES` admission.  It exits fail-closed on dispatcher-source drift and does not
inspect, signal, alter, or collect an existing R2 namespace.

A separate `fast64-r2-closeout` persistent tmux controller now waits only for
all seven fixed R2 terminal receipts.  It is SHA-pinned to the existing
fail-closed R2 collector, invokes that collector only after all seven rows are
terminal, and atomically publishes an external collector-pass marker only on
strict success.  It never launches or alters a simulator, and a collector
failure remains a retryable evidence failure rather than a stage promotion.

## FAST64.1 topology-aware R2 admission is ready (2026-09-08)

The remote review supersedes the former fixed/exclusive `74-80` pool rule:
host CPU placement is scheduling metadata, never a FAST64 scientific identity.
The dispatcher now uses `lscpu -p=CPU,CORE,SOCKET,NODE` and live affinity data,
prefers distinct physical cores, excludes only singleton/narrow pinned
simulator affinity, and ranks remaining candidates by current scheduler
occupancy.  A broad `Cpus_allowed_list=0-511` is soft host contention, not
exclusive ownership of every CPU.  R2 remains explicitly `taskset` pinned;
all immutable-v2, SHA, UUID, namespace, receipt and strict-validator guarantees
are unchanged.

`audit_fast64_r2_resources.sh` remains read-only but now publishes the
required `FAST64_R2_RESOURCE_AUDIT_V1`, including topology candidates, realistic
live p95 RSS and historical-R1 output footprint, cgroup/swap/OOM/PSI/I/O
deltas, and autonomous `safe_to_launch` / `authorized_workers` N_safe decision.
It never launches a process.  A passing audit authorizes the dispatcher to
admit the frozen-priority missing R2 rows without waiting for historical R1
termination; a conservative one-to-two worker ramp remains the policy.

The first formal immutable R2 ramp was admitted at `2026-09-08T04:06:56Z`
from `/tmp/fast64-r2-resource-audit-launch-v2.tsv`: `safe_to_launch=YES`,
`authorized_workers=2`, 384 cgroup quota cores, 249 available distinct
physical-core candidates, 9 pre-launch simulators, p95 RSS 8,925,478,912
bytes, 139,714,740,224 bytes MemAvailable, zero swap-out/OOM/throttling/PSI/iowait and
45,600,477,184 bytes output free.  The sample's 30-page swap-in without swap-out or PSI
is recorded but is not active pressure.  The new live rows are BICG
Base@8192 (`fast64_1r2_bicg_base_cap8192_a1`, CPU 0, UUID
`0c84f039-346e-4d28-9d0f-b7a4e04ee8b0`) and BICG IO@8192
(`fast64_1r2_bicg_io_cap8192_a1`, CPU 3, UUID
`81a1e97c-af78-417d-a38a-440a0a43ccd7`).  Both have immutable runner SHA
`bf9a84…`, exact Core/runtime/A1/scientific-config provenance and published
`RUN_START.tsv`; neither is terminal or promotable yet.

## FAST64.2 forced lower-create stress decision resolved (2026-09-08)

The one high-cap BICG/PAPER_IO diagnostic has naturally terminated with a
clean single execution epoch, exit 0, exact lower create/issue/response
conservation, and drained final state.  It is **not** FAST64.2 PASS: its
source-coupled entries-one overlay recorded
`DTC_L1_io_lower_create_queue_full_stalls = 0`.

Frozen-Core source sequencing explains why the former high-cap positive retry
was invalid:
PAPER_IO produces at most one candidate per SM cycle, and the following
cycle's pre-memory-stage issue routine removes it whenever the high global cap
has credit.  The NoC-full path only retains a separate unbounded issue queue.
Hence the former high/non-binding-cap plus natural queue-full requirement was
incompatible with this PAPER_IO path.  Researcher-authorized Option 2 now
classifies the completed row as `FAST64_2_HIGH_CAP_NEGATIVE_CONTROL` and
prepares an immutable NN/IO `cap=512, PIB=1` source-reachable coupled positive
stress.  The run remains resource-gated; no Core change or new simulator run
was made.  See `fast64/handoffs/FAST64_2_FORCED_STRESS_SEMANTIC_GATE.md`.
The FAST64 Goal is active again; FAST64.1 immutable R2 remains the first
formal-closeout priority whenever a fresh resource audit is safe.

## FAST64.1 immutable R2 recovery preparation (2026-09-08)

At this recovery checkpoint FAST64.1 was stage-gated by an execution-path
failure; no stage promotion and no R2 simulator launch had occurred.  Current
authority is `GOAL ACTIVE; FAST64.1 STAGE_GATE_PENDING`, rather than a global
Goal-blocked state.  Read-only `/proc` evidence resolves the
historical controller issue as
`ROOT_CAUSE_PROBABLE_ACTIVE_SCRIPT_MUTATION`: all live r1 Bash wrappers still
read fd `255` from the mutable worktree runner, whose SHA changed from the
launch snapshot's `6f078314…` to `14635253…`; the contaminated BICG OO parent
survived both observed epochs.  A second BICG OO@1048576 row has independently
produced the same two-epoch footprint and `line 74: d: command not found`.
The exact malformed continuation cannot be
reconstructed, so this is deliberately not labeled confirmed.

Future-only recovery is now prepared as a complete seven-row R2 wave, not a
one-row patch.  The v2 runner requires an SHA-verified, non-writable
`/tmp/fast64-runners/<sha>/` copy, one UUID, atomic namespace creation, and
immutable START/TERMINAL receipts.  Its validator requires the receipt chain
and a single-epoch proof calibrated on the clean NN rows.  A harmless
`/bin/true` test passed immutable binding, receipts, and duplicate namespace
rejection; it is not a scientific result.  The guarded dispatcher dynamically
admits only the fresh audited number of R2 workers; old r1 diagnostics are not
a scientific wait barrier.  The whole r1 qualification wave is
`SUPERSEDED_NONFORMAL_EXECUTION_PATH_AT_RISK`; all r1 collector output is
nonformal.  See
`fast64/handoffs/FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md`.

The earlier R2 resource snapshot was `FAST64_1_R2_RESOURCE_WAIT_ACTIVE`, not
Goal blocked.  It has since been superseded by the fresh CPU-slot-wait
observation above; the dispatcher/collector/config/identity preparation and
independent FAST64.2 diagnostic work remain authorized.  Whenever a historical
job naturally exits, take a new resource audit and admit the highest-priority
safe R2 row without a wait-for-all barrier.

## FAST64.1 r1 execution-path contamination (2026-09-07)

This historical R1 checkpoint is nonpromotable; it does not describe the
current R2 execution state.  The
BICG OO@8192 r1 namespace has two observed simulator epochs in a single
exactly-once output directory, no `simulator_exit_status`, and a controller
anomaly (`line 74: d: command not found`).  Its prior epoch reached
47,231,655 cycles, but neither epoch is formal evidence.  The cgroup's
`oom_kill=12` is retained as host-pressure evidence only; causal attribution
has not been established.  All remaining live r1 and FAST64.2 processes are
preserved untouched.  A future-only atomic-namespace runner has passed a
harmless controller test; no formal recovery row has been launched.  See
`fast64/handoffs/FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md`.

## FAST64 throughput-update checkpoint (2026-09-07)

FAST64 logical state remains **FAST64.1 ACTIVE**; no FAST64.1, FAST64.2, or
FAST64.3 PASS is claimed.  The seven formal-instrumented-Core r1 qualification
rows continue naturally and untouched.  The researcher-authorized scheduling
policy now separates strict `LOGICAL_STAGE_ACCEPTANCE` from provenance-bound
`PHYSICAL_PRECOMPUTED_ACQUISITION` (Framework `4144983b...`).

One high-cap BICG/IO lower-create stress diagnostic is live as
`PRECOMPUTED_FAST64_2_DIAGNOSTIC_PENDING_FAST64_1_ACCEPTANCE`; it uses the
formal `bbcbb5e...` Core and a source-coupled candidate-queue/PIB bound of one,
not a performance configuration.  NN/Base@8192 has naturally terminated and
strict-validated as `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE` (6,985 cycles,
1,284,872 instructions, zero lower-cap-full and drained accounting).  It is
not yet an accepted FAST64.3 result.  Shared-host swap is exhausted and output
headroom is about 62 GiB, so the first controlled ramp stops pending a fresh
resource/throughput audit.  See
`fast64/handoffs/FAST64_PRECOMPUTED_ACQUISITION.md`.

Stage: M5.0BT exact trace capture and qualification — **RESOLVING_ISSUE
M5-0BT-011 (2MM SIM_HOST immutable-receipt capacity)**.

## C2P trace versus M5 ATAX host-throughput review (2026-09-07)

The requested non-invasive audit is recorded in
`m5/handoffs/M5_0BT_C2P_TRACE_HOST_THROUGHPUT_AUDIT.md`.  It establishes that
the historical C2P ATAX trace and the exact M5 NVBit trace are not the same
payload: kernel-1 ABI differs, C2P has `(16,1,1) x (256,1,1)` while M5 has
`(128,1,1) x (32,8,1)`, M5 kernel-1 has 8.95x C2P's dynamic instructions, and
the two-kernel M5 traceg set is 10.26x the C2P byte size.  C2P therefore
cannot be used as a formal M5 trace substitute, although it may later be an
explicitly nonformal host-diagnostic control.

The apparent 2,466-versus-about-280 simulated-cycles/s gap does not show a
nine-fold per-instruction host regression.  The available evidence decomposes
it into about 6.58x higher M5 simulated IPC/work per cycle and only about
1.34x lower host simulated-instruction throughput.  The live M5 process was
CPU-active with no sampled I/O wait or swap pressure; the shared legacy
observer settings and the independently equivalent A1 observer experiment
cannot explain the gap.  No active process, config, Core behavior, formal
result identity, or stage has changed.

## 2MM copyback storage admission (2026-09-06)

2MM has reached remote `ARCHIVE_PASS` with archive SHA-256
`59e918821bc54a772434acc70d2d439abefd8ccf696c055be2564b53d520863e`; this is
not yet a SIM_HOST receipt or formal result.  The fail-closed copyback gate
stopped before rsync because 36,313,600,000 local free bytes are below its
58,013,565,949-byte exact requirement (archive 3,416,630,277 + complete
bundle 50,301,968,376 + 4 GiB margin).  No payload was deleted, recaptured,
or unpacked.  Researcher-authorized archive-only rsync is now preserving the
compressed `.tar.zst` locally, but it is deliberately not a receipt: no
archive SHA, internal bundle validation, or `LOCAL_IMMUTABLE_PASS` is claimed.
`m5/handoffs/M5_0BT_2MM_STORAGE_ADMISSION_STOP.md` binds the evidence and
requires capacity provision followed by full transfer-only receipt resume;
M5.0BT remains ACTIVE.

### Background hold and rented-host disposition

At researcher direction, the live archive-only 2MM rsync and the repaired
ATAX Base/IO/OO replays continue naturally in the background while no new M5
stage work is started.  The compact handoff is
`m5/handoffs/M5_0BT_2MM_STORAGE_ADMISSION_STOP.md`.  The rented capture host
is **not yet safe to release** while this archive-only transfer is partial.
After its natural completion, a SHA-256 comparison of the compressed archive
to the recorded remote archive SHA is sufficient no-unpack proof that permits
capture-host release, while still leaving 2MM outside formal
`COPYBACK_SHA_PASS`/`LOCAL_IMMUTABLE_PASS`.  Its later formal receipt remains
gated on capacity plus internal-bundle and immutable-store validation.  This
is a provenance constraint; it does not imply an active GPU workload.

The archive-only transfer has now naturally completed.  Its local compressed
archive is exactly 3,416,630,277 bytes and direct SHA-256 matches the recorded
remote archive SHA:
`59e918821bc54a772434acc70d2d439abefd8ccf696c055be2564b53d520863e`.
`ARCHIVE_ONLY_COPYBACK_SHA_PASS` makes the rented V100 capture host safe to
release for storage purposes.  This no-unpack retention proof deliberately
does not promote 2MM to a formal immutable receipt or authorize a new M5
stage.

The researcher has authorized the interim eight-workload repaired-Core replay
batch (Paper-10 excluding `2mm` and `syrk`). Its exact scope, non-bypass ATAX
qualification gate, and dispatch order are frozen in
`m5/handoffs/M5_0BT_EIGHT_WORKLOAD_REPLAY_PLAN.md`. BICG and SpMV are retained
instead of duplicated; no new replay may bypass the live ATAX natural-terminal
parser/accounting gate.

A source audit has also confirmed a native `.traceg.xz` frontend route.  It is
an isolated `TEXT_TRACEG_XZ_DERIVED` storage candidate only, not an accepted
trace representation: byte-decompression, ordered-list, and same-bundle
Base/IO/OO differential proofs remain mandatory before formal use.  See
`m5/handoffs/M5_0BT_COMPRESSED_TRACE_STORAGE_CANDIDATE.md`.  Its first
no-write SpMV trace byte-round-trip PASS is evidence only, not a formal replay
or receipt claim.

## E1 local `sm_70` build preflight (2026-09-06)

BlackScholes has a reproducible, isolated CUDA-11.8 `sm_70` source/build/PTX
preflight with all legacy helper inputs hash-bound.  SIM_HOST has no visible
GPU, so it did not execute the source-defined `QA_PASSED` checker and has not
promoted the row beyond `SOURCE_READY`; `BUILD_READY` and
`TRACE_CAPTURE_READY` counts remain zero.  The exact candidate identities and
the mandatory real-V100 follow-up gates are recorded in
`m5/extended20/CUDA_SDK_E1_SOURCE_AUDIT.md` and
`m5/handoffs/M5_E1_V100_CAPTURE_READINESS.md`.  This is E1 preparation only;
it neither consumes V100 capture capacity nor changes the Paper-10 priority.
The canonical post-link artifact is an independently double-built,
byte-identical stripped ELF; the resolved nvcc local-symbol metadata issue is
recorded as `M5-E1-003`.

FastWalshTransform now has the same local two-build `sm_70` preflight under
its exact `-logK 11 -logD 19` source contract.  It remains `SOURCE_READY`
because no V100 output smoke or dynamic trace audit has run; E1 readiness
counts and the Paper-10 capture priority are unchanged.

VectorAdd and scalarProd have now passed the same two-build local `sm_70`
preflight with normalized ELF/PTX identities.  Neither has run a V100
source-defined output smoke or dynamic trace audit, so both remain
`SOURCE_READY`; the E1 readiness ledger remains unchanged.

Transpose, scan, and sortingNetworks have also completed their independent
two-build local `sm_70` preflights under their exact SDK 4.2 tree identities.
They remain `SOURCE_READY` pending V100 output smokes and dynamic trace audits;
the physical-capture queue and E1 readiness ledger remain unchanged.

convolutionSeparable has now completed the same isolated two-build CUDA-11.8
`sm_70` preflight from the frozen SDK 4.2 object.  Its normalized ELF and PTX
are byte-identical across both builds, but SIM_HOST did not run the real-V100
`--size 3072` L2-norm `QA_PASSED` checker or dynamic trace audit.  Its
constant-memory transfer path remains a runtime semantic gate, so it remains
`SOURCE_READY`; no readiness count, capture priority, or active V100 work is
changed.

Rodinia hotspot1 has independently passed an equivalent local CUDA-11.8
`sm_70` build/PTX reproducibility preflight from the clean 3.1 source tree.
It remains `INPUT_READY`, not `BUILD_READY`: no V100 source-defined checker,
input/runtime/launch freeze, or dynamic trace audit has run. The Paper-10
capture queue and all E1 exclusive readiness counts are unchanged.

Rodinia btree has also passed a two-build local CUDA-11.8 `sm_70` preflight,
including its two selected GPU-kernel PTX artifacts. A CUDA-11.8-compatible
compiler-driver wrapper replaces only the historical invalid quoted gencode
expansion; it changes no source, launch, or runtime semantics. btree remains
`INPUT_READY`, not `BUILD_READY`, pending its V100 checker and dynamic trace
audit; Paper-10 capture priority and readiness counts are unchanged.

Rodinia lud likewise has a two-build local CUDA-11.8 `sm_70` preflight,
preserving its source-defined `-O3 -use_fast_math` build mode and three kernel
PTX entries. It remains `INPUT_READY`, not `BUILD_READY`: the V100 verifier,
runtime/input/launch freeze, and dynamic trace audit have not run. Paper-10
capture priority and readiness counts remain unchanged.

Rodinia dwt2d has also completed a two-build local CUDA-11.8 `sm_70` preflight
with a reproducible eight-unit PTX manifest. It remains `INPUT_READY`, not
`BUILD_READY`, pending source-defined output/reference checking and dynamic
trace audit; Paper-10 capture priority and readiness counts are unchanged.

Rodinia gaussian has likewise completed a two-build local CUDA-11.8 `sm_70`
preflight while preserving its source-defined workgroup constants. It remains
`SOURCE_READY`, not `BUILD_READY`, pending a selected input/checker, V100
smoke, and dynamic trace audit; Paper-10 capture priority is unchanged.

Rodinia cfd_097k has completed an independently repeated local CUDA-11.8
`sm_70` build/PTX preflight using only the exact frozen tree's legacy
host-timer helper headers.  This source-bound dependency recovery changes no
workload source or runtime semantics.  Because CFD uses constant-memory setup,
it remains `INPUT_READY/RUNTIME_AUDIT_CONSTANT`, not `BUILD_READY`: a real
V100 checker, frozen launch/input contract, and dynamic trace-ordering audit
are still required.  Paper-10 capture priority and all readiness counts are
unchanged.

## Live audit update (2026-09-06)

The natural-terminal BICG stats-light A0/A1 comparisons and the required
independent same-placement IO confirmation are complete. Base, repaired
PAPER_IO, and repaired PAPER_OO strict-parse and match exactly in every
parser-visible scientific field, including final cycles/instructions,
DTC lifecycle/accounting, and parser-visible traffic. The same-placement
confirmation again found zero differing metrics and natural zero drain.
A1 (`gpgpu_runtime_stat=500000`, observer-overlay SHA
`2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`) is now
adopted for **future, not-yet-launched** formal triplets only. Existing valid
A0 rows are neither rerun nor relabelled, and no future triplet may mix A0/A1.
See `m5/handoffs/M5_STATS_LIGHT_A1_TERMINAL_EQUIVALENCE.md`.

The repaired BICG Base replay has now naturally terminated (exit zero), strict
parsed, and reclosed the same-bundle repaired-Core T2 triplet with IO/OO.
`review_packs/M5_0BT_T2_BICG/` is now bound to Core `15cfa76e...`; the
pre-repair T2 remains diagnostic only.  The ATAX Base/IO/OO recovery triplet
remains live, so the lower-create repair gate is not yet PASS; repaired MVT
replacement and repaired GESUMMV T3 remain correctly gated by its required
natural-terminal/parser/drain closure.

The source-script capture route has been recovered and read non-invasively.
SpMV is `ARCHIVE_PASS`, has copyback SHA and local immutable validation PASS,
and is bound to exact source/input/tracer identity in
`m5/handoffs/M5_0BT_SPMV_CAPTURE_CLOSEOUT.md`.  2MM has completed its
capture/postprocess phase and is currently controller `ARCHIVE_PENDING`; it
has no archive/transfer/result claim yet. No production capture was restarted
or duplicated during the reachability recovery.

The newly immutable SpMV bundle has entered the repaired-Core SIM_HOST pool as
three isolated `PRECOMPUTED_PENDING_STAGE_ACCEPTANCE` Base/IO/OO rows.  All
three have loaded the first immutable `.traceg` through the trace frontend,
with empty stderr; no formal-result claim is made before their own natural
terminal/parser/accounting closure.

## Current capture-storage authority (2026-09-06)

SYR2K has reached remote ARCHIVE_PASS with an exact 57,694,970,930-byte
working bundle, exceeding the old 55,353,177,980-byte 2DConv-based aggregate
projection. Future capture uses the researcher-authorized serial-streaming
admission floor of 61,516,599,357 bytes: the maximum measured complete SYR2K
bundle + archive + measurable scratch footprint. The old ten-bundle/twofold
multiplier is superseded because proof-bound streaming offload is now required.
SYR2K now has copyback SHA and local immutable validation PASS: its remote
archive SHA, local resumed archive SHA, unpacked internal sums and capture
bundle have closed under receipt
`6a6b590dc7d05a10d85ab30b37c6350092aba981c65be82249c6374e3e825513`.
The proof-bound remote working-bundle eviction and fresh live gate have since
passed; only the redundant remote SYR2K working bundle was eligible, while its
archive/provenance remain retained. The ordered SpMV -> 2MM queue has been
restarted, but no SpMV capture/archive/transfer/result is claimed yet. 2MM is
HEAVY_SIZE_UNKNOWN and may start only under the recalibrated gate. See
docs/dtc_l1/m5/handoffs/M5_0BT_SYR2K_HEAVY_STORAGE_RECALIBRATION.md.

Status: M5.0BT T1, BICG/2DConv storage admission, immutable-store copybacks,
and T2 BICG same-bundle Base/IO/OO replay qualification PASS.  T3 GESUMMV
same-bundle Base/IO/OO formal replay is ACTIVE; `CAPTURE_AND_REPLAY_PIPELINED`.
**New Core recovery active:** four precomputed ATAX/MVT IO/OO rows aborted
at the bounded lower-create queue assertion.  Core
`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` replaces that post-allocation
abort with pre-allocation retriable backpressure and retains all correctness
assertions.  Exact-bundle ATAX IO/OO recovery replays are active under the
new runtime; neither they nor any old-Core row is a formal result yet.
The existing BICG T2 and live GESUMMV T3 replays use pre-repair Core
`12097864...`; preserve them to natural termination, but treat them as
diagnostic/mechanism anchors.  Same-bundle triplets under `15cfa76e...` are
required before a repaired-identity T2/T3 formal acceptance claim.

## Live scheduling update

### Concurrent three-track checkpoint

- **Track A — T3 (pre-repair diagnostic):** GESUMMV Base/IO/OO run as
  independent sessions on the
  immutable `d8cf9b57...` bundle under the frozen 80-SM/cap-10240/ratio-zero
  identities.  The latest non-invasive counter sample was Base
  `2,446,000` cycles / `5,539,040` instructions, IO `1,809,000` /
  `24,494,688`, and OO `1,864,000` / `22,761,472`; all three processes were
  CPU-active with no fatal/assert/deadlock signature (the only `deadlock`
  text is the printed enabled-config option).  They must naturally terminate.
  Because their Core predates the lower-create-queue repair, they cannot close
  repaired-identity T3 and a new-Core same-bundle replacement triplet remains
  required.
- **Track B — V100 capture:** ATAX is `ARCHIVE_PASS` remotely and locally
  transfer-verified: archive SHA-256
  `4db328affd8a81d444bca1bc034110e1e51458fbce6ab901078a101c6beadff3`,
  internal sums PASS, controller `valid_bundle()` PASS, and checker PASS with
  zero mismatches.  It is a T4-eligible payload, not a formal performance
  result.  GEMVER has remote checker/archival PASS.  MVT has now completed
  checker/archive/copyback: archive SHA-256
  `6c537caf1e110c3804bdc943211078565580f88d9ed85ac8dfa12d685964f270`,
  bundle ID `8b96abe81eed02a614014401cb074ff9d57abd3dc6ba72260167050679ca4f3a`,
  internal sums PASS, and `valid_bundle()` PASS at preserved local root
  `/workspace/m5-trace-immutable/mvt/mvt/mvt`.  SYRK has since reached
  `ARCHIVE_PASS` with bundle
  `66957eacdb8435c12c097631460450923adf9ed39bf8bfe37464cdf868c9a09b` and
  archive SHA-256
  `b82e9ef0310778f8e3493ca555532a636a08f84e466d9e733ebea53a11b3b6a3`;
  SIM_HOST copyback is active but local immutable validation is not yet a
  claim.  The subsequent SYR2K launch was refused before capture by the
  controller's fail-closed heterogeneous-storage projection gate
  (`RuntimeError: unsafe projected heterogeneous trace storage`): no SYR2K
  state, trace, or capture process was created.  Researcher-authorized,
  provenance-preserving R1/R2 reclamation then removed only regenerable
  capture scratch and one checker-failed, non-candidate GESUMMV raw attempt;
  its compact logs/provenance were retained.  The unchanged gate subsequently
  passed (`55,478,362,112` free bytes versus `55,353,177,980` projected), and
  the single SYR2K controller resumed under the capture lock.  While SYR2K
  was actively capturing, the proof-bound R3 controller operation offloaded
  only the redundant remote ATAX working bundle (5,806,756,882 bytes); its
  remote archive and all verified SIM_HOST artifacts remain preserved.  The
  post-R3 unchanged gate passed with 59,432,751,104 free bytes.  See
  `m5/handoffs/M5_0BT_AUTODL_SPACE_RECLAMATION.md`.  None of these capture
  bundles is a formal result.  As SYR2K's live trace later consumed the
  start-gate margin, R4 used the same proof-bound controller action for MVT:
  only its redundant 5,777,441,032-byte remote working bundle was removed,
  after remote/local archive SHA and local immutable manifest validation
  matched.  Its remote archive and SIM_HOST immutable payload remain intact;
  the post-R4 unchanged gate passed with 59,907,649,536 free bytes.  SYR2K
  remained active throughout.  R5 then proof-bound-offloaded only GEMVER's
  redundant 2,647,569,402-byte remote working bundle after the same archive
  and local immutable checks; its archive and local payload remain preserved,
  and the unmodified gate passed with 59,551,346,688 free bytes.
- **Track C — SIM_HOST statistics-light A/B:** the initial BICG
  same-trace/same-binary/80-SM/cap-10240/PAPER_BASE cutoff round established
  that `gpgpu_max_cycle=2000000` is not a valid DTC observation boundary: it
  bypasses normal drain and correctly fails the terminal lifecycle assertion.
  Those outputs remain diagnostic-only.  A separately isolated natural-
  terminal A0--A3 round is active.  A0 is current observer
  settings; A1 sparse runtime CSV; A2 additionally suppresses the final PTX
  line report; A3 additionally disables generic memlatency observer stats.
  This does not alter a formal run or registry.  See
  `m5/handoffs/M5_SIM_HOST_STATS_LIGHT_AUDIT.md`; no candidate is adopted
  until terminal counter equivalence and a controlled confirmation pass.

- **Pipelined returned-trace acquisition:** researcher authorization permits
  independent replay acquisition before T3/M5.0BT logical PASS.  The fully
  validated ATAX, GEMVER and MVT immutable payloads each have a Base/IO/OO
  replay on the unchanged frozen formal configuration, recorded as
  `PRECOMPUTED_PENDING_STAGE_ACCEPTANCE` in
  `m5/handoffs/M5_0BT_PRECOMPUTED_REPLAY_QUEUE.md`.  These live rows are not
  a stage result and must close all terminal/parser/accounting gates before
  later exact-identity reuse.

- **Lower-create queue recovery:** the frozen 80-SM/cap-10240 pool exposed
  the same source-reachable IO/OO assertion for ATAX and MVT.  The failed
  evidence is preserved, excluded from the registry, and documented in
  `implementation/M5_PRECOMPUTED_LOWER_CREATE_QUEUE_FAILURE.md`.  The Core
  repair exports explicit queue-full stall counters, passes the three DTC
  CTests in an isolated Release build, and has an isolated trace frontend
  runtime.  ATAX IO (PID `1045897`) and OO (PID `1045896`) now replay the same
  immutable bundle/config in a separate recovery namespace.  At 101 s both
  exceeded their old 83.81 s / 84.96 s abort window with empty stderr and no
  assertion/fatal/deadlock/error signature.  They must still close natural-
  terminal/parser/accounting gates before any post-repair formal reuse; MVT
  remains queued behind that evidence.  This is a HARD recovery gate, not a
  stage advance.

- **Repaired-identity replay pool:** isolated runtimes built from Core
  `15cfa76e...` now run ATAX Base/IO/OO and BICG Base/IO/OO on their existing
  immutable bundles/configs.  ATAX uses Framework `2bb015a8...`; BICG uses
  Framework `dc7836c4...`; each triplet is internally source-identical.  The
  BICG triplet is the post-repair T2 replacement, not a duplicate formal result.  The
  dynamically calibrated pool has 18 live simulator workers, including the
  four stats-light diagnostics; MemAvailable remains about 101 GiB with zero
  swap I/O, so further dispatch is frozen pending a natural exit or fresh
  calibration.  See `m5/handoffs/M5_REPAIRED_CORE_REPLAY_POOL.md`.

- BICG Base remains a verified trace-driven replay, not a PTX/execution-driven
  payload: its live argv uses immutable BICG `kernelslist.g`, loads both
  ordered `.traceg` invocations through the trace frontend, and has no trace
  corruption/fatal/assert/deadlock/output-mismatch signature. Its immutable
  bundle ID is `ae7f9dbd07e2da471b6e218d160b7446c710872cd85797e54bd58b42708e8a33`.
- A 90-second read-only sample recorded `33,182,550 -> 33,316,550` current
  kernel cycles and `54,363,616 -> 54,570,624` instructions: about 1,489
  cycles/s and 2,300 instructions/s. Classification:
  `TRACE_REPLAY_HEALTHY_PROGRESSING`. Base subsequently naturally terminated
  and strict-parsed at `50,303,549` cycles / `158,601,216` instructions; the
  full same-bundle BICG Base/IO/OO qualification is now T2 PASS. Its review
  pack is `review_packs/M5_0BT_T2_BICG/`; T3 is the next logical replay gate.
- Physical V100 capture now pipelines independently. The first GESUMMV
  (`gesu`) attempt is preserved `RETRY_READY`: its checker found 1,964
  mismatches caused by the pinned CUDA source copying uninitialized host
  `tmp`/`y` into additive device accumulators. A source-copy-only repair is
  hash-constrained to those two zero initializations and records both source
  hashes/replacements in capture provenance; the frozen source and failed raw
  attempt are untouched. Its corrected replacement capture now has checker,
  immutable-bundle/archive, copyback-SHA and local bundle-revalidation PASS;
  it is a T3 payload, not yet a formal result. Framework
  `14be71c7968f0fb5bc1e021cf40eda41d8314171` corrects the controller's
  heavy-pilot admission formula and passes its no-GPU regressions. This is a
  capture-controller repair only; it changes no trace bundle, replay config,
  Core behavior, or formal result.
- See `m5/handoffs/M5_0BT_CAPTURE_REPLAY_PIPELINE.md`. Capture ahead of replay
  is a scheduling admission only; M5.0C remains prohibited until full M5.0BT
  acceptance.

## Current authoritative state

### Throughput checkpoint (2026-09-06)

- Researcher-authorized worker recovery preserved and then gracefully retired
  stats-light A2/A3 and the old-Core GESUMMV Base/IO/OO diagnostics.  The
  exact preserved namespaces, pre-signal evidence, classifications and PGIDs
  are recorded in `m5/handoffs/M5_SIM_HOST_STATS_LIGHT_AUDIT.md` and
  `m5/handoffs/M5_REPAIRED_CORE_REPLAY_POOL.md`.  No repaired-Core formal
  candidate was signaled, no raw evidence was deleted, and no `SIGKILL` was
  required.
- The real container CPU boundary is a 384-core cgroup quota with cpuset
  `0-511`, not an 18-core allocation.  Eighteen was a conservative shared-host
  scheduling limit.  After retirement, BICG repaired PAPER_IO/PAPER_OO A1
  natural-terminal observer-only confirmations started on dedicated CPUs 46
  and 47 (`1512229`, `1512240`); they retain the immutable BICG trace, Core
  `15cfa76e...`, 80-SM/cap10240/ratio-zero model and differ only by runtime
  statistics cadence.  They are not adoption/formal results pending full
  terminal equivalence.
- ATAX repaired Base/IO/OO remain live and have only exceeded the historical
  abort window; they have not completed the HARD terminal/parser/drain/lower
  accounting gate.  Consequently MVT IO/OO and repaired GESUMMV T3 are ready
  for priority dispatch but remain correctly gated, rather than being launched
  under an unqualified repaired runtime.

### Capture-storage recovery R6 (2026-09-06)

- SYRK reached archive/copyback/local-immutable PASS and was then reclaimed
  only through the proof-bound controller path.  `bundles/syrk` (27,998,390,213
  bytes) was removed; its remote archive, local immutable payload and evidence
  were preserved.  Free space increased from the last pre-controller observed
  54,673,100,800 bytes to 82,369,568,768 bytes while SYR2K continued capture.
  See `m5/handoffs/M5_0BT_AUTODL_SPACE_RECLAMATION.md` and remote
  `reclamation/R6_syrk_offload_evict.json`.
- The AutoDL control plane is again readable through the live capture-host
  route.  SYR2K is in its natural post-GPU trace-processing phase:
  application checker PASS (zero mismatches), raw trace present, and the
  controller remains live while its CPU postprocessor runs.  Its state is
  still `CAPTURING`, so neither `ARCHIVE_PASS` nor copyback is claimed.
- The next exact SpMV payload's canonical matrix/vector/reference identities
  and clean wrapper `de9cf429...` / tree `5b8b3a8...` remain verified.  Both
  SIM_HOST source bundles were copied to an isolated AutoDL staging area with
  SHA-256 and complete-history bundle verification; a clean detached
  `parboil@4e0fc548...` / tree `0bc8944...` checkout now occupies the source
  path consumed by the existing queue supervisor.  This replaces the
  prolonged non-candidate public clone without changing any capture artifact.
  The supervisor is now fail-closed only on SYR2K `ARCHIVE_PASS`, storage, and
  the capture lock before starting SpMV, then applies the same ordering to
  2MM.  See `m5/handoffs/M5_0BT_SPMV_SOURCE_TRANSFER_READY.md`.
- 2MM CPU-side preparation and isolated AutoDL source-tar transfer are both
  verified: clean `polybenchGpu@5584aaa7...` source/header hashes,
  deterministic tar identity, sm70 build, source checker and dimensions are
  frozen in `m5/handoffs/M5_0BT_2MM_CAPTURE_READY.md`.  It remains `PENDING`
  and may start only after SpMV reaches its safe archive state and the normal
  lock/storage gates pass.

### Live throughput checkpoint (2026-09-06T12:19+08:00)

- The repaired-Core BICG PAPER_OO A0 replay naturally ended with exit status
  zero and strict parser/drain/accounting PASS in its isolated output
  namespace.  It records 8,764,792 cycles / 158,601,216 instructions, lower
  create/issue/response `17,827,090/17,827,090/17,827,090`, dependencies
  `18,350,080/18,350,080`, and final OO PIB/inflight/active-ref/lower state
  all zero.  It is only a `POST_REPAIR_T2_REPLAY_CANDIDATE`: repaired BICG
  Base/IO and the required IO/OO A1 equivalence confirmations are still live,
  so no T2 re-close, stats-light adoption, or formal registry update occurs.
- The repaired-Core BICG PAPER_IO A0 member has now also naturally ended and
  strict-parsed: 9,324,397 cycles / 158,601,216 instructions, lower
  create/issue/response `17,823,985/17,823,985/17,823,985`, dependencies
  `18,350,080/18,350,080`, and final IO inflight/PIB/lower state all zero.
  No assertion, fatal, output mismatch, or non-config deadlock text was
  observed.  This leaves only repaired BICG Base A0 before same-bundle T2
  triplet reconciliation; the IO/OO A1 stats-light confirmations remain live.
- **Current-pool correction (2026-09-06T12:33+08:00):** after the BICG IO A0
  terminal transition, 13 (not 14) isolated M5 simulator processes remain
  live.  The repaired BICG IO/OO A0 rows are recorded in the replay-job
  manifest as `POST_REPAIR_T2_REPLAY_CANDIDATE`; they are not registered
  formal results and still await Base A0 plus same-mode A1 equivalence.
- At the 12:19 historical snapshot, fourteen isolated M5 simulator processes
  remained active and each continued
  to accrue near-one-core CPU time.  The dynamic limit remains `N_safe=18`;
  the unfilled capacity is intentionally protected until repaired ATAX
  Base/IO/OO close their natural-terminal/parser/drain gate, after which MVT
  IO/OO and repaired GESUMMV receive priority.  The container has cpuset
  `0-511` and a non-throttling 384-core `cpu.max` quota, but the shared host
  load is about 440 and does not support increasing concurrency from topology
  alone.
- Two non-invasive V100 SSH probes were refused during this checkpoint.  No
  remote process, queue, archive, or state file was touched, and this is not
  classified as a capture failure.  Continue local replays and resume the
  existing fail-closed `SYR2K -> SpMV -> 2MM` capture pipeline only after the
  host is reachable and its retained controller state can be read.

### Extended E1 offline provenance progress (2026-09-06)

- The six selected Parboil input sets were byte-hash and Git-blob revalidated
  in clean `parboil@4e0fc548...`; the six selected checker identities remain
  source-pinned.  The Python-3 source-predicate adapter recompiled and passed
  all six accepted/mismatch fixtures.  This closes local input/checker drift
  evidence only: CUDA builds, PTX, generated output references/smokes, payload
  eligibility and all Rodinia input recovery remain pending.  No Extended
  simulation, trace capture, result registration, or E2 launch occurred.
- The eight selected CUDA SDK 4.2 source files were independently rehashed
  straight from Git commit `b059fdae...`; all match the recorded E1 source
  identities.  This is source-only provenance confirmation: executable/PTX
  artifact revalidation, deterministic runtime I/O, source-defined smoke and
  M5.2 anchor recheck remain required.
- A conservative static source audit now classifies the six Parboil rows
  before any V100 work: BFS (atomics/textures/global barrier), CUTCP
  (stream/constant memory), Histo (atomics), MRI-Q (constant memory), and
  SAD (textures) require workload-local runtime semantic audits; Stencil is a
  static trace candidate only.  None is yet `TRACE_CAPTURE_READY`, no feature
  is presumed unsupported, and the per-row readiness table remains the
  capture scheduling authority.  See
  `m5/extended20/M5_E1_PARBOIL_STATIC_TRACE_FEATURE_AUDIT.md` and
  `m5/handoffs/M5_E1_V100_CAPTURE_READINESS.md`.
- The selected Rodinia 3.1 CUDA source scan likewise identifies CFD's
  constant-memory transfer path for a runtime audit; BTree, DWT2D, Gaussian,
  Hotspot1 and LUD are static candidates only.  Their missing deterministic
  inputs/checkers and all clean V100/sm70 builds still prohibit capture.  See
  `m5/extended20/M5_E1_RODINIA_STATIC_TRACE_FEATURE_AUDIT.md`.
- The CUDA SDK 4.2 static screen identifies convolutionSeparable's
  constant-memory transfer path; the other seven selected rows are static
  candidates only.  All eight already have recorded local CUDA-11.8/sm70
  build/PTX preflights, but no SDK row can capture before its own real-V100
  output smoke/checker, input/launch/runtime freeze and dynamic contract.  See
  `m5/extended20/M5_E1_CUDA_SDK_STATIC_TRACE_FEATURE_AUDIT.md`.
- The source-recorded Rodinia 3.1 data archive is now archive-hashed and only
  the approved input members have been materialized in an isolated local E1
  namespace.  CFD, BTree, DWT2D and Hotspot now have exact launcher-input
  hashes; LUD's source-generated `-s 256` contract is distinguished from a
  data file.  Gaussian has several source-recorded candidates and remains
  deliberately unfrozen.  No V100 capture, build, trace or formal result was
  started.  See `extended20/RODINIA_PARBOIL_E1_SOURCE_AUDIT.md`.

- One persistent Goal: docs/dtc_l1/m5/M5_TRACE_TO_FINAL_SINGLE_GOAL_CONTRACT.md.
- M5.0BT is active and gates M5.0C. No M5.0C, Extended E2, graphics work, or
  capture-host rental/start is authorized by this report.
- Formal platform is 80 SM, global lower cap 10240 (128 credits/SM), and
  ratio-zero. The 80-SM/cap-256 combination is historical diagnostic-only.
- M5.0BT has a workload-specific, source-pinned CUDA-11.8/sm70 capture
  controller, immutable bundle validation, external archive/transfer states,
  non-bypassable BICG-based storage admission, and SIM_HOST orchestrator.
- The two remote checkouts are non-interchangeable: current M5 control checkout
  runs the command; detached 0db04452ec1c47630e4b08002067d82c6811e243
  supplies tracer sources only.
- The provisioned capture host passed V100/CC7.0, CUDA 11.8, toolchain,
  writable-data-volume and pinned-source preflight. M5-0BT-001 was repaired
  before CUDA build; M5-0BT-002 then found an unrelated root-Makefile legacy
  tool after the required trace tool/postprocessor compiled. Its scoped-build
  repair and regression contract now pass. Retry-4 completed that build but
  exposed M5-0BT-003: the host identity probe used incorrect CUDA Runtime UUID
  APIs. The compact Driver-API UUID adapter passed isolated CUDA-11.8/V100
  revalidation (properties, Driver UUID and CC 7.0 agree with `nvidia-smi`).
  No application, raw trace, immutable bundle or formal result has been
  created. Retry-5 reached the BICG CUDA build and exposed M5-0BT-004: its
  selected-workload loop propagated a false final predicate as status 1 after
  a successful `nvcc` build. The explicit-success repair passed an exact V100
  BICG build retest. Frozen source, CUDA 11.8 and sm70 build contract are
  unchanged; each fresh build's executable SHA is captured as provenance.
  Retry-6 then loaded NVBit on V100 but found the installed CUDA-11.8
  `nvdisasm` absent from the application PATH (M5-0BT-005). Retry-7's PATH
  repair passed: the BICG checker passed and full raw traces were captured.
  Its postprocess exposed M5-0BT-006; retry-8 passed that legacy-layout
  adapter, application checker, raw capture and `.traceg` postprocess. It then
  exposed M5-0BT-007; its CSV repair passed on resume. Strict mapping then
  exposed M5-0BT-008; its line-preserving repair also passed. Finalization
  reached record construction and exposed M5-0BT-009: it had not materialized
  the validated manifest files before hashing them. Its write-before-hash
  repair passed: retry-8 is now an immutable, archived BICG T1 bundle. See
  `m5/handoffs/M5_0BT_BICG_T1_REVIEW.md`. The archive was SHA-verified after
  copyback, unpacked once into the immutable replay store, and internally
  revalidated against its bundle sums. The BICG admission projects
  47,591,571,552 bytes against 104,537,268,224 measured free bytes, but is
  provisional because BICG's two small-grid invocations do not bound 2DConv.
  The required exact 2DConv 65,536-CTA heavy pilot now passes its hardware
  checker, archive/copyback SHA chain and internal immutable-store sum check.
  Its conservative ten-workload/twofold-reserve projection is 55,353,177,980
  bytes below 101,566,291,968 measured free bytes, admitting the remaining
  sequential Paper queue. See `m5/handoffs/M5_0BT_BICG_ADMISSION_COPYBACK.md`
  and `m5/handoffs/M5_0BT_2DCONV_HEAVY_ADMISSION.md`.

## Required next action after a V100 host is supplied

Complete natural-terminal GESUMMV T3 qualification while the exact Paper
capture queue continues independently.  Then obtain/qualify the remaining
Paper trace bundles.  No M5.0C transition is authorized.

## HISTORICAL / SUPERSEDED — DO NOT EXECUTE

The prior execution-driven M5.0B cap-256 workload campaigns, their former
natural-terminal wait, and their five terminated recovery jobs are preserved
only as source/provenance and mechanism-validation evidence. They are not
formal performance inputs and impose no active transition condition.
