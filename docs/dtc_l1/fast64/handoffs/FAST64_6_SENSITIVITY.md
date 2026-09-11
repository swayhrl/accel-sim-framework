# FAST64.6 — Frozen sensitivity acquisition handoff

Status: **FROZEN; TWELVE PHYSICAL PRECOMPUTATION ROWS STRICT-TERMINAL, ELEVEN
FORMAL ROWS PLUS ONE NONFORMAL DIAGNOSTIC ACTIVE, AND FOUR PRESERVED
16.5-KIB FAILURES UNDER
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`**

Logical stage order remains unchanged: FAST64.3, FAST64.4 and FAST64.5 must
pass before FAST64.6 logical acceptance.  This handoff freezes only the
independent physical-acquisition contract authorized after FAST64.2 PASS.

## Authority and mode policy

The dissertation-derived M5 authority is unambiguous.  M5.3 specifies the
logical 16/32/64 KiB formal sweep as PAPER_IO and PAPER_OO, with Base only an
optional supplemental capacity control; M5.4 specifies physical 16.5/24/32/
40/48 KiB for IO and OO; and M5.5 specifies IO/OO PIB 32/64/128/192, with
FAST64 retaining its already-frozen 256-entry diagnostic saturation point.
The exact sources are `M5_EXPERIMENT_MATRIX.md` §§M5.3--M5.5 and
`FAST64_SENSITIVITY_CONFIG_PLAN.md`.  Thus no researcher decision is needed.

The formal roster is frozen pre-performance as BICG, GESUMMV and Btree.  The
machine-readable 78-row IO/OO matrix is
`generated/FAST64_6_SENSITIVITY_MATRIX_V1.tsv`.  It records each config SHA,
exact physical-line mapping, per-dimension reference point, and pending
classification.  The nine materialized Base logical controls are retained as
source-supported *supplemental* configurations and are not part of the formal
FAST64.6 bar/matrix roster.

The companion operational ledger is
`generated/FAST64_6_PHYSICAL_COVERAGE_V1.tsv`.  It records each physical
IO/OO point exactly once as a strict terminal precompute, active immutable
attempt, preserved failure, diagnostic, or not-yet-launched point.  It is
nonpromoting scheduling evidence: terminal rows remain
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`, and a complete pair in the ledger
does not promote FAST64.4, FAST64.5, or FAST64.6.

## Exact identities

- scientific Framework snapshot: `037f008b330eb230353b60edf126d6be9f45afdc`;
- config materialization source: `180e81c68816012165c26dab577e693b3b798292`;
- repaired Core/runtime: `95ccdb7a056f2d53f740d90869785cac6d4ee0f5` /
  `462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9`;
- A1 observer: `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`.

Every acquisition uses a fresh namespace, unique UUID, immutable runner and
atomic START/TERMINAL receipts.  Versioned dispatcher
`dispatch_fast64_sensitivity_row_v4.sh` separately validates the historical
scientific snapshot and the later config-materialization commit, then gives
the immutable runner only the scientific snapshot identity.  This avoids
silently claiming that a configuration-only commit changed scientific inputs.
Future dispatches use `dispatch_fast64_sensitivity_row_v5.sh`, which performs
the same checks against the detached clean Core-`95ccdb7a...` formal worktree.
The active Core worktree may advance only for diagnostic-only descendants; its
HEAD is never allowed to substitute for the frozen formal Core identity.

## One-dimensional controls and normalization

- Logical: only `logical_sets`, IO/OO, normalize to the same mode at 16 KiB.
- Physical: only `physical_lines`, IO/OO, normalize per source to IO at 32 KiB.
  The exact 128-B mappings are 132/16,896 B, 192/24,576 B, 256/32,768 B,
  320/40,960 B and 384/49,152 B.
- PIB: only the mode-local PIB/coupled candidate-queue capacity, IO/OO,
  normalize per source to IO at 128 entries.  The 256 point is explicitly
  retained as a diagnostic saturation point and never relabelled as a thesis
  Figure-4.10 primary bar.

No matching historical-Core row is treated as repaired-Core sensitivity by
renaming.  A baseline point can be reused only after repaired-Core terminal
identity, exact payload/config/observer/snapshot, parser and drain checks.
All new rows must naturally exit zero and strict-validate lower/dependency and
mode-specific drain before any later logical promotion.

## First physical-acquisition wave (2026-09-10)

The two fresh three-window V3 resource audits recorded
`PASS_FUTURE_PRECOMPUTE_ADMISSION_V3`: no sampled swap-out, OOM, memory PSI,
CFS throttling or pathological cgroup I/O.  The target-20 audit at
`/tmp/fast64-resource-audit-v3-20260910T1340Z-target20.tsv` observed 15 live
FAST64 leaves and admitted five more, projecting 20 total workers and about
88.4 GiB `MemAvailable` after the fixed 16-GiB reserve.  This was followed by
ten nonduplicate physical-pool rows, all with atomic START receipts and
separate read-only closeout monitors:

| Physical pool | Workloads/modes |
| --- | --- |
| 16.5 KiB (132 lines, 16,896 B) | BICG IO/OO; GESUMMV IO/OO; Btree IO/OO |
| 24 KiB (192 lines, 24,576 B) | BICG IO/OO; GESUMMV IO/OO |

After the Btree/16.5-KiB/OO terminal freed one of the admitted slots, a fresh
three-window target-20 refill audit at
`/tmp/fast64-resource-audit-v3-20260910T1422Z-target20-refill.tsv` passed for
one new worker (no sustained swap-out, PSI, OOM, CFS throttle or pathological
I/O; projected `MemAvailable` 57.6 GiB after the fixed reserve).  The next
frozen, nonduplicate point, Btree / 24 KiB / IO, launched with immutable START
receipt UUID `c0902c8e-e9b8-4783-a021-933494c8b558` on CPU 29.  Its collector
is versioned separately as `collect_fast64_6_precompute_v2.sh`, so the live
v1 closeout dependency was not modified.

`generated/FAST64_6_PRECOMPUTE_DISPATCH_V1.tsv` is the compact immutable
attempt index (namespace, CPU, supervisor/simulator PID, UUID and config
hash).  The Btree / 16.5-KiB / OO row (UUID
`3a34fc35-38d0-48f3-a0e0-399f72c348f1`) naturally terminated exit 0 at
`2026-09-10T14:06:03Z` and strict-validated into
`generated/fast64_6_precomputed_v1/fast64_sens_v1_btree_physical16p5_oo.json`.
Its exact repaired-Core/runtime/scientific/A1 identities, payload trace hash,
receipt hashes, lower acquire/release `501958/501958`, dependency
`2388513/2388513`, and final lower/PIB/inflight/OO-ref drains are recorded
there; lower-cap-full is zero.  This is a retained physical precompute only.
All rows, including that terminal row, remain
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`: no FAST64.6 logical promotion or
performance conclusion is claimed.

## Terminal and failure accounting update (2026-09-10)

Two further Btree IO rows naturally exited zero and passed immutable receipt,
strict-parser, payload/config/identity, lower/dependency-conservation and
terminal-drain checks.  They remain retained precomputes only:

| Workload / point / mode | UUID | terminal UTC | cycles / instructions | lower acquire/release | dependencies closed/count | terminal resource state |
| --- | --- | --- | --- | --- | --- | --- |
| Btree / 16.5 KiB / IO | `3936327b-fe50-4212-bb1d-b0e79b2c6e23` | `2026-09-10T14:36:40Z` | 548,243 / 444,467,849 | 507,647 / 507,647 | 2,388,513 / 2,388,513 | lower, PIB, inflight and partial entries/lines drain to zero; cap-full 0 |
| Btree / 24 KiB / IO | `c0902c8e-e9b8-4783-a021-933494c8b558` | `2026-09-10T15:39:55Z` | 244,231 / 444,467,849 | 507,779 / 507,779 | 2,388,513 / 2,388,513 | lower, PIB, inflight and partial entries/lines drain to zero; cap-full 0 |

Their compact records are `generated/fast64_6_precomputed_v1/fast64_sens_v1_btree_physical16p5_io.json` and `generated/fast64_6_precomputed_v1/fast64_sens_v1_btree_physical24_io.json`.  Both bind repaired Core `95ccdb7a...`, repaired runtime `462d105c...`, scientific Framework `037f008b...`, A1 observer and exact Btree trace payload.  Both remain only `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`.

The BICG / 16.5-KiB IO and OO attempts are preserved failures, never result
records.  Both use the frozen repaired-Core/runtime/A1 identity and immutable
runner, but their TERMINAL receipts record exit 1: IO UUID
`cf459ee2-7ac4-4caa-8649-26eeb31d1d4e` at `2026-09-10T17:34:54Z`; OO UUID
`a6061cae-52b5-4263-a7fd-04434386ffaa` at `2026-09-10T17:17:10Z`.  The IO
fatal dump is source-classified as the frozen valid undersized-pool IO circular
resource dependency: 132/132 physical lines allocated, zero free, one
non-ready FIFO head per affected SM and 28--31 partially held lines, with zero
lower-create/issue/inflight work.  `DTC_L1_SPEC.md` §§3.4 and 8 expressly
require retained partial allocations/no rollback and identify this
undersized-configuration deadlock as emergent behavior.  It must not be
"fixed" by changing allocation semantics.  The OO failure is also preserved
and excluded; its current fatal dump lacks a mode-equivalent DTC resource
snapshot, so it remains an observability follow-up rather than an inferred
root cause.  `FAST64_6_BICG_PHYSICAL16P5_FAILURE.md` holds the exact evidence
and disposition.

## Target-16 refill: two new formal rows; separate OO observation (2026-09-10)

A fresh read-only admission observation found 13 live FAST64 simulator leaves,
about 167 GiB `MemAvailable`, cgroup memory current/max 54.6/256 GiB, zero
memory-PSI and CFS throttling, and 108.8 GiB output free.  The two real
physical cores 34 and 35 were unoccupied by FAST64.  It was therefore safe to
raise the formal total only toward the authorized target 16, rather than jump
to 20.  `dispatch_fast64_sensitivity_row_v5.sh` was dry-run verified and then
launched these new nonduplicate formal rows:

| Row | core / simulator PID | immutable UUID | exact config | classification |
| --- | --- | --- | --- | --- |
| Btree / 24 KiB / OO | 34 / 802101 | `6d24efbd-473c-487e-b4d6-d93209a07d66` | `FAST64_SENS_PHYSICAL_24KB_OO`, SHA `e7161643...` | `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` |
| Btree / 40 KiB / IO | 35 / 802165 | `bef2beaf-5bbd-45b2-b449-89008a3afc87` | `FAST64_SENS_PHYSICAL_40KB_IO`, SHA `69a9c237...` | `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` |

`generated/FAST64_6_PRECOMPUTE_DISPATCH_V2.tsv` records their exact frozen
formal identities.  Both START receipts were atomically published; a brief
read-only observation showed the processes CPU-active with growing output and
no forbidden signature.  They are live precomputes, not PASS records.

The third target-16 slot is deliberately **not** a formal result.  It is the
one exact BICG / 16.5-KiB / OO reproduction needed to observe the preserved OO
failure, in fresh namespace
`/workspace/fast64-diagnostics/fast64_6_bicg_physical16p5_oo_coref283_diag_v1`.
It uses diagnostic-only Core `f2836ea1...` and binary SHA `361aada1...`, CPU
36, UUID `2ef7f749-cf0c-4d45-a9d0-4a73b35d9d21`, the exact frozen payload and
config, and `NONFORMAL_DIAGNOSTIC_NOT_RESULT`.  This binary prints only after
the existing deadlock decision; it cannot change normal simulation behavior or
replace formal Core `95ccdb7a...` for any retained row.

## Target-20 expansion (2026-09-10)

The target-16 workers sustained useful CPU progress without terminal or
forbidden-log signatures, while `MemAvailable` remained about 166 GiB, cgroup
memory was 57.9 GiB of 256 GiB, memory PSI and CFS throttling were zero, and
output free space remained 108.8 GiB.  The four next nonduplicate frozen
physical points were dry-run verified then launched onto unshared physical
cores 37--40.  Each has an atomic START receipt, formal Core-95/runtime/A1
identity, immutable runner and fresh namespace:

| Row | CPU / simulator PID | UUID | config |
| --- | --- | --- | --- |
| Btree / 40 KiB / OO | 37 / 807685 | `caed8185-190f-4c5d-9579-6f9ab35eccad` | `FAST64_SENS_PHYSICAL_40KB_OO` |
| Btree / 48 KiB / IO | 38 / 807749 | `e6d49d31-0c68-498a-b1ac-9a1c1bca4f5b` | `FAST64_SENS_PHYSICAL_48KB_IO` |
| Btree / 48 KiB / OO | 39 / 807807 | `826c71df-70b5-4157-bf4d-f5213111c361` | `FAST64_SENS_PHYSICAL_48KB_OO` |
| BICG / 32 KiB / IO | 40 / 807848 | `3e5e4a69-0884-44c1-9340-d83e20ced89f` | `FAST64_SENS_PHYSICAL_32KB_IO` |

These four and the target-16 formal rows are live
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` rows only.  The compact identity
index below is extended with their exact config hashes.  No 16.5-KiB failed
attempt was restarted, and no Stage3/4 work was modified.

## Btree / 24-KiB / OO terminal precompute (2026-09-10)

The target-16 Btree / 24-KiB / PAPER_OO row naturally terminated with exit
zero at `2026-09-10T19:09:27Z`. The frozen v3 collector then independently
validated its immutable START/TERMINAL receipt pair, exact formal
Core-`95ccdb7a...`/runtime-`462d105c...`/A1/scientific identities, config SHA
`e7161643...`, payload identity and strict parser/accounting contract before
atomically publishing
`generated/fast64_6_precomputed_v3/fast64_sens_v5_btree_physical24_oo.json`.

| point | UUID | cycles / instructions | lower acquire/release | dependencies closed/count | final drain |
| --- | --- | --- | --- | --- | --- |
| Btree / 24 KiB / OO | `6d24efbd-473c-487e-b4d6-d93209a07d66` | 172,795 / 444,467,849 | 502,450 / 502,450 | 2,388,513 / 2,388,513 | lower, PIB, OO inflight and active refs all zero; lower-cap-full 0 |

It is a physical acquisition only and remains
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; it is not a FAST64.4/FAST64.6
logical result or a performance conclusion.

## Btree / 40--48-KiB terminal precomputes and 32-KiB refill (2026-09-10)

Three more Btree physical-pool rows naturally exited zero and were independently
strict-validated by the frozen v3 collector. Each has exact repaired formal
Core/runtime/A1/scientific/payload provenance, balanced mode-specific lower
create/issue/response and dependency lifecycles, zero final PIB/inflight/lower
state and lower-cap-full zero:

| point | UUID | cycles / instructions | lower lifecycle | dependency lifecycle |
| --- | --- | --- | --- | --- |
| Btree / 40 KiB / IO | `bef2beaf-5bbd-45b2-b449-89008a3afc87` | 244,231 / 444,467,849 | 507,779 / 507,779 / 507,779 | 2,388,513 / 2,388,513 |
| Btree / 40 KiB / OO | `caed8185-190f-4c5d-9579-6f9ab35eccad` | 172,795 / 444,467,849 | 502,450 / 502,450 / 502,450 | 2,388,513 / 2,388,513 |
| Btree / 48 KiB / OO | `826c71df-70b5-4157-bf4d-f5213111c361` | 172,795 / 444,467,849 | 502,450 / 502,450 / 502,450 | 2,388,513 / 2,388,513 |

Their compact records reside in `generated/fast64_6_precomputed_v3/`. They
remain `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` only.

The three naturally released slots were re-audited with about 151 GiB
`MemAvailable`, zero sampled memory PSI and 115 GB output headroom. Three
fresh nonduplicate physical-32 rows were dry-run validated and atomically
started: Btree IO (CPU 35, UUID `cb54525c-c634-4bbc-96e7-b8a43570c55f`), Btree
OO (CPU 37, UUID `55755348-52c5-4c96-858c-638814aa0570`), and BICG OO (CPU
39, UUID `37a406ef-9111-4a18-a2d1-99f498893b9c`). They use the detached formal
Core-95 worktree and exact frozen physical-32 configs. New
`collect_fast64_6_precompute_v4.sh` is future-only for these v6 namespaces;
the active v3 collector remains untouched. All three are precomputes only.

## Btree / 48-KiB / IO terminal and BICG / 40-KiB / IO refill (2026-09-10)

Btree / 48 KiB / IO (UUID `e6d49d31-0c68-498a-b1ac-9a1c1bca4f5b`) naturally
exited zero and strict-validated into
`generated/fast64_6_precomputed_v3/fast64_sens_v5_btree_physical48_io.json`:
244,231 cycles, 444,467,849 instructions, lower
create/issue/response `507,779/507,779/507,779`, dependencies
`2,388,513/2,388,513`, final lower/PIB/inflight zero and lower-cap-full zero.
It is the eighth retained precompute only.

The released CPU 38 passed the same resource admission checks and now runs
fresh BICG / 40 KiB / IO in namespace
`fast64_sens_v7_bicg_physical40_io`, UUID
`2c49d8fe-5b05-4814-84a5-0d588996b90b`, exact physical-40 config and formal
Core-95/runtime/A1 identities. Future-only v5 collection is isolated to this
row. Neither fact advances FAST64.4 or FAST64.6 logical acceptance.

The row subsequently reached its immutable terminal receipt with exit `0` at
`2026-09-11T02:05:21Z`.  The unchanged V5 collector strictly published
`generated/fast64_6_precomputed_v5/fast64_sens_v7_bicg_physical40_io.json`:
61,017,789 cycles / 145,666,048 instructions; lower credit and IO
create/issue/response `17,823,522/17,823,522`; dependencies
`18,350,080/18,350,080`; final lower/inflight/PIB `0/0/0`; and lower-cap-full
plus lower-create-queue-full `0`.  It remains
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`, with no FAST64.4/.5/.6 promotion.

## BICG / 40-KiB / OO paired physical precompute (2026-09-11)

The source-backed mode policy is frozen before this dispatch: physical-pool
points run both PAPER_IO and PAPER_OO, keep the 16-KiB logical geometry and
mode-primary PIB value fixed, and normalize to the 32-KiB PAPER_IO point.
`40 KiB` is exactly `320` 128-B physical lines (`40,960 B`), as recorded in
`generated/FAST64_6_SENSITIVITY_MATRIX_V1.tsv` and the resolved config plan.
No config is rounded or jointly tuned.

At the fresh admission snapshot there were 19 FAST64 leaves; `MemAvailable`
was 129.5 GiB, cgroup use 64.3 GiB of 256 GiB, memory/I/O PSI and CFS
throttling were zero, and output headroom was about 106 GiB.  CPU 41 was an
unshared physical core.  The missing BICG/physical-40/PAPER_OO pair therefore
passed the immutable dispatcher dry run and was started exactly once:

| Row | CPU | UUID | config | collector | disposition |
| --- | ---: | --- | --- | --- | --- |
| BICG / 40 KiB / OO | 41 | `11383078-382d-4f18-9eb3-975bce4fb434` | `FAST64_SENS_PHYSICAL_40KB_OO`, SHA `6b1cf347...` | future-only `collect_fast64_6_precompute_v6.sh` | `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` |

The row binds formal repaired Core `95ccdb7a...`, runtime `462d105c...`, A1
observer, frozen scientific Framework `037f008b...`, materialization
`180e81c...`, and read-only immutable runner `bf9a84c8...`.  Its atomic START
receipt is present in fresh namespace `fast64_sens_v8_bicg_physical40_oo`.
The v6 collector is isolated to this one future row; no live V3/V4/V5
collector, Stage3/4 simulator, or diagnostic was edited or restarted.  This
is physical acquisition only and cannot promote FAST64.4, FAST64.5, or
FAST64.6.

## GESUMMV / 40-KiB IO dispatched after BICG-24K pair closure (2026-09-11)

The next nonduplicate GESUMMV physical point is 40 KiB, exactly 320 physical
128-B lines (40,960 B).  Immutable-v2 dispatcher dry-runs passed for fresh
namespaces `fast64_sens_v13_gesummv_physical40_io` and
`fast64_sens_v14_gesummv_physical40_oo`.  The physical-32-to-40 config diff is
only `-gpgpu_dtc_l1_physical_lines 256 -> 320` in each mode.

After BICG/24-KiB/IO naturally terminated, a fresh two-window resource audit
admitted one replacement: no sampled swap-out, OOM, memory PSI or CFS
throttling; p95 simulator RSS was 3.18 GiB; `MemAvailable` was 133.75 GiB;
cgroup headroom was 187.86 GiB; and output headroom was 104.16 GiB.  GESUMMV
/ 40 KiB / IO was atomically started once on CPU 30 as immutable attempt
`146b0390-2592-436d-bf4c-fad1e96148c6` in
`fast64_sens_v13_gesummv_physical40_io` (supervisor 948487, simulator 948512).
Its START receipt binds the formal Core/runtime/A1/scientific/payload and
physical-40 IO config SHA `69a9c237...`; a short read-only observation found
CPU progress and no actual assertion/fatal/deadlock/output-mismatch signature.

Future-only `util/dtc_l1/collect_fast64_6_precompute_v10.sh` (monitor PID
949578) targets only V13/V14, uses atomic temporary-result publication, and
does not read or modify active V1--V9 collection dependencies.  V14 remains
undispatched.  V13 is `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` only: it is
not a result, pair comparison, or stage promotion.

## GESUMMV / 48-KiB pair closeout prepared, not dispatched (2026-09-11)

The final currently unlaunched physical-pool pair is 48 KiB, exactly 384
128-B lines (49,152 B).  Immutable-v2 dry-runs for fresh V15/V16 namespaces
pass with no directory creation.  The only physical-40-to-48 config delta is
`-gpgpu_dtc_l1_physical_lines 320 -> 384` in both IO and OO.

Future-only `util/dtc_l1/collect_fast64_6_precompute_v11.sh` is isolated to
those names and preserves the exact formal identity plus atomic strict-result
publication.  It does not read or modify V1--V10 collector state.  As with
the 40-KiB pair, it will remain unlaunched until a fresh target-20 admission
audit accepts a naturally freed slot; no performance or stage conclusion is
claimed.

## BICG / 24-KiB / OO terminal physical precompute (2026-09-11)

BICG / physical 24 KiB / PAPER_OO naturally terminated with exit zero and was
strict-collected by the existing independent v1 collector into
`generated/fast64_6_precomputed_v1/fast64_sens_v1_bicg_physical24_oo.json`.
The atomic receipts and record bind formal Core `95ccdb7a...`, runtime
`462d105c...`, A1 observer, scientific Framework `037f008b...`, exact
physical-24 OO config SHA `e7161643...`, and the frozen BICG payload.

| point | UUID | cycles / instructions | lower create/issue/response and credit acquire/release | OO dependency closed/count | terminal state |
| --- | --- | --- | --- | --- | --- |
| BICG / 24 KiB / OO | `e33abcc8-c43f-4599-a55b-4e895fe2fe32` | 37,846,112 / 145,666,048 | 17,639,701 / 17,639,701 / 17,639,701 | 18,350,080 / 18,350,080 | lower, PIB, OO inflight, and active refs zero; lower-cap-full 0 |

This is the ninth strict-terminal physical precompute.  It remains
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; BICG / 24 KiB / IO is still live,
so this evidence does not create a mode-pair comparison, FAST64.4 primary
result, FAST64.5 causal claim, or FAST64.6 logical promotion.

## Btree / 32-KiB strict physical pair and next pairwise refills (2026-09-11)

Both Btree / physical 32-KiB modes naturally exited zero and the unchanged,
then-inactive v4 collector was invoked once to atomically strict-validate their
own terminal receipts.  It touched neither the remaining live v6 BICG row nor
any simulator.  The two compact records are
`generated/fast64_6_precomputed_v4/fast64_sens_v6_btree_physical32_io.json`
and `...physical32_oo.json`; each binds Core `95ccdb7a...`, runtime
`462d105c...`, A1, scientific Framework `037f008b...`, frozen Btree payload,
and its exact physical-32 config.

| point | UUID | terminal UTC | cycles / instructions | lower lifecycle | dependency closed/count | terminal state |
| --- | --- | --- | --- | --- | --- | --- |
| Btree / 32 KiB / IO | `cb54525c-c634-4bbc-96e7-b8a43570c55f` | `2026-09-10T19:48:48Z` | 244,231 / 444,467,849 | 507,779 / 507,779 / 507,779 | 2,388,513 / 2,388,513 | lower, PIB, IO inflight zero; lower-cap-full 0 |
| Btree / 32 KiB / OO | `55755348-52c5-4c96-858c-638814aa0570` | `2026-09-10T19:42:30Z` | 172,795 / 444,467,849 | 502,450 / 502,450 / 502,450 | 2,388,513 / 2,388,513 | lower, PIB, OO inflight and active refs zero; lower-cap-full 0 |

They raise the strict-terminal physical-precompute count to eleven and remain
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` only.  The BICG/physical-24 OO
and Btree/physical-32 pairwise results must not be used as FAST64.4 primary
comparisons or FAST64.6 logical acceptance.

GESUMMV/physical-16.5/IO has now naturally reached the same exit-1 deadlock
class as the preserved 16.5-OO attempt.  It is a terminal failure with no PASS
record, retained separately pending source-backed resource-state classification;
it is not silently relabeled as a valid sensitivity result and does not change
the frozen matrix.

Fresh capacity released by natural terminal rows admitted the following exact
nonduplicate physical acquisitions after dry-run verification.  All bind the
formal repaired Core/runtime/A1/scientific identities, immutable-v2 runner,
fresh namespace and atomic START receipt.  Future-only v7/v8 collectors cover
only these new rows.

| Row | CPU | UUID | collector | disposition |
| --- | ---: | --- | --- | --- |
| BICG / 48 KiB / IO | 31 | `4a5a9737-1928-48b6-8ae9-f017f465466d` | v7 | `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` |
| BICG / 48 KiB / OO | 37 | `7e733ecb-f9b2-46e6-9899-4c5dd1e7213f` | v7 | `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` |
| GESUMMV / 32 KiB / IO | 26 | `cfed0564-14df-4e0f-b650-ae5460b88e25` | v8 | `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` |
| GESUMMV / 32 KiB / OO | 35 | `00a173e5-8402-4345-9f4f-b5121b89957a` | v8 | `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` |

The original v4 controller is no longer live.  Its only remaining live input,
BICG / physical 32 KiB / OO, has been adopted by future-only v9 collector
`collect_fast64_6_precompute_v9.sh`.  The script does not alter v4, waits for
the existing immutable terminal receipt, and writes only a distinct v9 compact
record after strict validation.  This closes collection coverage without
touching the simulator or changing its experimental identity.

## BICG / 24-KiB / IO strict-terminal paired precompute (2026-09-11)

The BICG / physical 24 KiB / PAPER_IO companion naturally terminated with
exit zero at `2026-09-10T20:23:30Z` and was atomically strict-collected into
`generated/fast64_6_precomputed_v1/fast64_sens_v1_bicg_physical24_io.json`.
The immutable attempt is `15f1c709-7c73-439c-93f6-f64f2c7623f4`; receipts and
the compact record bind Core `95ccdb7a...`, runtime `462d105c...`, A1,
scientific Framework `037f008b...`, the exact IO config SHA `6d8ab5fa...`,
and the frozen BICG payload.

| point | cycles / instructions | lower create/issue/response and credit acquire/release | IO dependency closed/count | terminal state |
| --- | --- | --- | --- | --- |
| BICG / 24 KiB / IO | 42,351,523 / 145,666,048 | 17,647,559 / 17,647,559 / 17,647,559 | 18,350,080 / 18,350,080 | lower outstanding, PIB, partial-entry/line and IO-inflight state zero; lower-cap-full 0 |

This brings the retained physical-precompute count to twelve and makes the
BICG/24-KiB IO/OO pair terminal under the same formal identity.  Both rows
remain `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; no pair performance
interpretation, FAST64.4 primary result, FAST64.5 causal claim, FAST64.6
logical acceptance, or FAST12 aggregation is asserted.

## BICG / 48-KiB / OO terminal physical precompute (2026-09-11)

BICG / physical 48 KiB / PAPER_OO naturally terminated with exit zero at
`2026-09-11T01:14:18Z`.  The independent v7 collector strict-collected the
immutable receipts into
`generated/fast64_6_precomputed_v7/fast64_sens_v10_bicg_physical48_oo.json`.
The record binds formal Core `95ccdb7a...`, runtime `462d105c...`, A1
observer, scientific Framework `037f008b...`, the frozen BICG payload, and
exact physical-48 OO config SHA `361c9c98...`.

| point | UUID | cycles / instructions | lower create/issue/response and credit acquire/release | OO dependency closed/count | terminal state |
| --- | --- | --- | --- | --- | --- |
| BICG / 48 KiB / OO | `7e733ecb-f9b2-46e6-9899-4c5dd1e7213f` | 47,093,407 / 145,666,048 | 17,815,083 / 17,815,083 / 17,815,083 | 18,350,080 / 18,350,080 | lower, PIB, OO inflight, and active refs zero; lower-cap-full 0 |

This raises the retained strict-terminal physical-precompute count to thirteen.
It remains `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`: its BICG / 48-KiB /
IO peer is still live, so the record creates no mode-pair comparison, no
FAST64.4 primary result, no FAST64.5 causal claim, and no FAST64.6 logical
promotion.

## BICG / 32-KiB / OO terminal physical precompute (2026-09-11)

BICG / physical 32 KiB / PAPER_OO naturally terminated with exit zero at
`2026-09-11T00:55:06Z`.  The future-only v9 collector strict-collected the
immutable receipts into
`generated/fast64_6_precomputed_v9/fast64_sens_v6_bicg_physical32_oo.json`.
The record binds formal Core `95ccdb7a...`, runtime `462d105c...`, A1
observer, scientific Framework `037f008b...`, the frozen BICG payload, and
exact physical-32 OO config SHA `d6017773...`.

| point | UUID | cycles / instructions | lower create/issue/response and credit acquire/release | OO dependency closed/count | terminal state |
| --- | --- | --- | --- | --- | --- |
| BICG / 32 KiB / OO | `37a406ef-9111-4a18-a2d1-99f498893b9c` | 42,895,109 / 145,666,048 | 17,769,885 / 17,769,885 / 17,769,885 | 18,350,080 / 18,350,080 | lower, PIB, OO inflight, and active refs zero; lower-cap-full 0 |

This raises the retained strict-terminal physical-precompute count to fourteen.
The matching 32-KiB IO record was already retained under the same formal
identity, but this remains `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; no
pair performance interpretation, FAST64.4 primary result, FAST64.5 causal
claim, or FAST64.6 logical promotion is asserted.

## BICG / 48-KiB / IO and GESUMMV / 32-KiB / OO terminal precomputes (2026-09-11)

The existing strict collectors published two additional natural-exit-zero
records without changing any simulator or configuration.  Both bind Core
`95ccdb7a...`, runtime `462d105c...`, A1, scientific Framework `037f008b...`,
their frozen payloads, and atomically published immutable receipts.

| point | UUID | terminal UTC | cycles / instructions | conserved lower lifecycle | dependency closure | terminal state |
| --- | --- | --- | --- | --- | --- | --- |
| BICG / 48 KiB / IO | `4a5a9737-1928-48b6-8ae9-f017f465466d` | `2026-09-11T04:27:32Z` | 77,916,699 / 145,666,048 | credit and IO create/issue/response `17,822,880` | `18,350,080/18,350,080` | lower, PIB and IO inflight zero; cap-full 0 |
| GESUMMV / 32 KiB / OO | `00a173e5-8402-4345-9f4f-b5121b89957a` | `2026-09-11T04:37:24Z` | 78,961,728 / 190,918,656 | credit and OO create/issue/response `34,370,858` | `35,651,712/35,651,712` | lower, PIB, OO inflight and active refs zero; cap-full 0 |

These raise the retained strict-terminal physical-precompute count to sixteen.
BICG/48 now has both modes retained; GESUMMV/32 still awaits its live IO
companion.  All remain `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; no pair
interpretation, FAST64.4 primary result, FAST64.5 causal claim, or FAST64.6
logical promotion is asserted.

## Complete-matrix collection contract and logical-capacity precomputation (2026-09-11)

Future-only `util/dtc_l1/collect_fast64_6_sensitivity_v1.py` is the
fail-closed collector for the entire frozen 78-cell roster.  Its input
registry must name every BICG/GESUMMV/Btree × logical/physical/PIB × IO/OO
cell exactly once.  It validates the frozen config hash, trace/payload,
Core/runtime/A1/scientific identities, immutable receipts, natural-terminal
lower/dependency accounting and mode-specific drain.  It rejects duplicates,
conflicting rows, and missing reference cells.  It writes immutable candidate
tables only: cell and raw manifests plus plot-ready logical/physical/PIB
tables with the frozen reference normalization.  It cannot emit a PASS
marker, tune points, or alter a live dispatcher.  Its synthetic positive and
negative regressions pass.

A fresh three-window V3 audit
`/workspace/fast64-sensitivity-v2/fast64_6_resource_audit_v5_20260911T0457Z_workers9.tsv`
authorized nine new workers (projected 20 FAST64 workers): no sustained
swap-out, memory PSI, OOM, CFS throttling or pathological I/O; projected
post-admission `MemAvailable` is 115,163,357,184 B after the fixed reserve.
After v5 immutable-dispatch dry-runs, the following nonduplicate,
one-dimensional logical points started on distinct physical CPUs.  Existing
Stage3/4 and physical-sensitivity rows were not changed.

| Workload | logical capacity | mode | CPU | immutable UUID |
| --- | ---: | --- | ---: | --- |
| BICG | 16 KiB | OO | 8 | `a5c57367-b457-4d9a-a881-ac56676f9a36` |
| BICG | 32 KiB | IO | 10 | `d52c6d90-8c5d-4319-b84a-5261c9813b57` |
| BICG | 32 KiB | OO | 11 | `5d14827b-24cc-4f63-99f8-a62be31a605a` |
| BICG | 64 KiB | IO | 12 | `e62a6b65-37b0-4d7d-9b61-cd73e56749f1` |
| BICG | 64 KiB | OO | 13 | `9338a339-d81a-4eb4-8a47-2de9fee18595` |
| GESUMMV | 16 KiB | IO | 14 | `0819375e-30aa-4537-831e-61fe0103ace1` |
| GESUMMV | 16 KiB | OO | 17 | `5f5eade2-cafd-484b-b4d3-bf7fcff306d2` |
| GESUMMV | 32 KiB | IO | 18 | `54bbb3a1-2db5-4961-8d6b-4031c4449e4e` |
| GESUMMV | 32 KiB | OO | 19 | `dfa700e5-6ac2-4aa3-83b9-076aa8a8deb3` |

All nine are monitored through the pre-existing read-only strict validator and
remain `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; they are not results,
curves, or a FAST64.6 promotion.  The pre-existing BICG/16-KiB/IO immutable
row remains live in its separate namespace and completes that pair only after
its own natural terminal validation.

## Btree logical-capacity six-cell precompute strictly collected (2026-09-11)

The six Btree logical-capacity IO/OO rows all naturally exited zero and the
unchanged immutable-v2 monitors strict-collected each terminal receipt.  The
complete compact registry is
`generated/FAST64_6_BTREE_LOGICAL_TERMINAL_REGISTRY_V1.tsv`; it pins the six
JSON hashes, UUIDs, exact Core-95/runtime/A1/scientific Framework/payload
identity, terminal timestamps, cycles/instructions and lifecycle closure.

| logical capacity | IO cycles | OO cycles | instructions per mode | lower-cap-full |
| ---: | ---: | ---: | ---: | ---: |
| 16 KiB | 244,231 | 172,795 | 444,467,849 | 0 / 0 |
| 32 KiB | 235,454 | 152,508 | 444,467,849 | 0 / 0 |
| 64 KiB | 233,835 | 146,453 | 444,467,849 | 0 / 0 |

For every row, lower create/issue/response and dependency count/closed
conserve; terminal lower, PIB and inflight are zero, with OO active references
also zero.  These are strict terminal **precomputes only**, classified
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`.  They do not create a Stage6
curve or promotion, alter FAST64.4/5, or permit a causal interpretation before
the required logical gates.

## Frozen 78-cell reconciliation closed; GESUMMV logical-64 pair dispatched (2026-09-11)

A read-only reconciliation joins the frozen matrix by config SHA and payload
SHA (not by config filename) against strict compact records and live formal
processes.  At the dispatch boundary it found 35 strict-terminal candidates,
39 exact formal live cells, and four preserved 16.5-KiB source-diagnostic
cells; no matrix cell was unowned.  The physical-16.5 cells remain preserved
diagnostic failures, not formal results and not automatic rerun candidates.

The only previously unowned cells were GESUMMV logical 64 KiB IO/OO.  A fresh
three-window V3 admission for two workers passed: no sampled swap-out, memory
PSI, OOM or CFS throttling; projected `MemAvailable` after admission was
65,261,965,312 B with the fixed 16-GiB reserve.  Both fresh namespaces were
absent before atomic START publication and were launched once on distinct CPUs
20/21 through immutable runner `bf9a84c8...`; their unchanged read-only v2
strict monitors have separate sessions.

| point | mode | CPU | immutable UUID | config SHA |
| --- | --- | ---: | --- | --- |
| GESUMMV / logical 64 KiB | IO | 20 | `d44047eb-4d10-44fe-9a6b-61c51acdea09` | `35b84094...` |
| GESUMMV / logical 64 KiB | OO | 21 | `383691d1-9ae2-4eae-b997-e9de38add704` | `313ff909...` |

The pair has only atomic START receipts and a short healthy observation; it is
strictly `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` until natural terminal
and strict collection.  This coverage closure is physical acquisition only:
it does not create a FAST64.6 curve/PASS or change FAST64.3--5 acceptance.

## Btree PIB OO non-reuse wave strictly collected (2026-09-11)

The non-reuse Btree PIB 32/64/192/256-entry OO wave naturally exited zero and
was strict-collected by the unchanged per-row v2 monitors.  The compact batch
registry `generated/FAST64_6_BTREE_PIB_OO_TERMINAL_REGISTRY_V1.tsv` binds each
immutable UUID, JSON hash and full lifecycle/drain summary.  All records carry
Core-95/runtime/A1/scientific Framework/frozen-payload identity, 444,467,849
instructions, conserved lower create/issue/response and dependencies, final
lower/PIB/inflight/active-ref zero, and lower-cap-full zero.

The 128-entry OO reference remains an existing exact primary-reuse candidate;
it is not rerun.  The matching newly acquired IO points remain live, so this
OO-only batch is retained strictly as
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`.  It makes no pairwise sensitivity
claim and does not promote FAST64.4, FAST64.5 or FAST64.6.
