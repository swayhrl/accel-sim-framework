# FAST64.2 forced lower-create stress — semantic gate

Status: **RESEARCHER_DECISION_RESOLVED; POSITIVE COUPLED STRESS STRICTLY COLLECTED — PRESSURE ABSENT**

This record preserves a naturally terminated diagnostic and the source proof
that prevents choosing a replacement experiment by intuition.  It does not
change Core behavior, the formal platform, the active FAST64.1 R2 recovery, or
any live simulator.

## Observed diagnostic

| item | value |
| --- | --- |
| row | `fast64_2_precomputed_bicg_io_stress_cap1048576_pib1_a1` |
| mode / trace | PAPER_IO / exact BICG trace payload |
| Core | `bbcbb5e7565417102087bc80b14c349b4e568c05` |
| runtime SHA-256 | `6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041` |
| observer SHA-256 | `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e` |
| config SHA-256 | `f2de27d772e667f475c0e01a41c77c6ce66084cdcb76122ce2f58266b28b3015` |
| only diagnostic change | IO candidate-queue/PIB bound `256 -> 1`; global lower cap remains `1048576` |
| terminal | natural exit `0`, `2026-09-07T16:42:35Z` |
| execution-path check | one perf stream, one init marker, one natural-exit marker, empty launcher log; no assertion/fatal/deadlock record |

The final aggregate counters in `simulator.stdout` are:

| counter | value |
| --- | ---: |
| `DTC_L1_io_lower_created` | 17,607,590 |
| `DTC_L1_io_lower_issued` | 17,607,590 |
| `DTC_L1_io_lower_responses` | 17,607,590 |
| `DTC_L1_io_lower_create_queue_full_stalls` | **0** |
| final IO inflight / PIB occupancy / lower outstanding | `0 / 0 / 0` |
| `DTC_L1_lower_cap_full_events` | `0` |

Thus the execution path and drain/conservation evidence are valid supporting
diagnostic evidence, but the explicit FAST64.2 forced-stress HARD condition
(`queue_full_stalls > 0`) fails.  It is neither a performance result nor an
execution-path-contamination result.

## Source proof of the incompatibility

In the frozen Core, `ldst_unit::cycle()` calls
`dtc_l1_io_issue_lower_requests()` before `memory_cycle()` (`shader.cc`
4937--4948).  PAPER_IO accepts at most one grouped line reference for the
dispatching instruction per cycle (`dtc_l1_io_memory_cycle`, 2953--2997).
For a new miss it adds one candidate only after checking the bound
(`shader.cc` 2965--2991).

At the beginning of the next cycle, the issue function pops one nonempty
candidate whenever `gpgpu_sim::dtc_l1_try_acquire_lower_request()` succeeds
(`shader.cc` 3014--3040).  That acquisition fails only when the global lower
outstanding count has reached the configured cap (`gpu-sim.cc` 1328--1344).
The subsequent NoC test controls only the separate, unbounded lower-*issue*
queue (`shader.cc` 3047--3056); it cannot retain an item in the bounded
lower-*create* queue.

Consequently, with the required high/non-binding cap and one PAPER_IO
candidate generated per SM cycle, the create queue is emptied before the next
candidate can be admitted.  With an entries-one bound, its observed maximum is
one and the `>= entries` admission predicate cannot become true.  The zero
global-cap-full count in the completed run independently confirms the only
source path which could have prevented that pop was not active.

PAPER_OO does not supply an unexamined escape hatch: its ordinary paper path
also creates one line candidate per call and has the same early-cycle pop.
The sector mode can reserve several sector requests, but at entries one a
multi-sector reservation is rejected before allocation and may not make
forward progress; it is not PAPER_OO formal behavior.

## Researcher decision — source-correct Option 2

The researcher authorizes Option 2.  The completed row is now
`FAST64_2_HIGH_CAP_NEGATIVE_CONTROL`: it proves natural termination, clean
single epoch, conservation/drain, and zero lower-cap-full plus zero
create-queue-full events when global credit is non-binding.  It is never the
positive forced-stress PASS.

The positive diagnostic is
`SOURCE_REACHABLE_COUPLED_LOWER_CAP_CREATE_QUEUE_STRESS`.  Its prepared
isolated row is `fast64_2_precomputed_nn_io_coupled_cap512_pib1_a1_r2`, using
the frozen NN trace, PAPER_IO, global lower cap `512`, and source-coupled IO
candidate/PIB entries `1`.  NN is chosen before any performance observation:
the existing frozen FAST64 64-SM NN/IO anchor has 2,673 lower requests, so it is the smallest
already provenance-resolved source-path candidate.  `cap=512` is deliberately
below the intended normal FAST64 lower concurrency scale while remaining far
above a one-credit global serialization; this is a diagnostic construction,
not performance tuning.

`materialize_fast64_coupled_lower_cap_stress_config.sh` writes the exact
overlay and provenance.  `prepare_fast64_2_coupled_stress.sh` uses the
immutable v2 runner and refuses launch without a complete fresh safe resource
audit.  Newly admitted capacity dispatches the highest-priority missing R2 row
first; the positive diagnostic remains independently launchable only through
its explicit audited command.  The collector requires nonzero lower-cap-full and IO
create-queue-full events, natural exit 0, exact immutable receipts, no
failure signature, lower/dependency conservation, and zero final state.

No Core semantic change is authorized.  The queue-full condition remains
MissQueue/lower-capacity pressure, never a Tag-bank conflict because of an
internal `BK_CONF` retry.

## Immutable-v2 NN/IO `cap=512, PIB=1` collection

The authorized positive construction subsequently ran in its own immutable-v2
namespace and naturally exited `0`.  Its strict collection is a success as an
execution/provenance/conservation check, but it is a **negative pressure
result**, not a FAST64.2 acceptance result.

| item | value |
| --- | --- |
| row | `fast64_2_precomputed_nn_io_coupled_cap512_pib1_a1_r2` |
| resolved platform | `64 x 1` SM shell (the frozen FAST64 platform, not a legacy 80-SM M5 anchor) |
| mode / trace | PAPER_IO / frozen NN payload |
| global cap / coupled bound | `512` / `-gpgpu_dtc_l1_io_pib_entries=1` |
| natural terminal | exit `0`; one immutable attempt UUID and START/TERMINAL receipts |
| strict execution result | single perf epoch; exact Core/runtime/observer/config/payload identity; no failure signature |
| lower conservation | create = issue = response = `2673` |
| dependency conservation | created = closed = `5346` |
| final state | IO inflight = PIB occupancy = lower outstanding = `0` |
| `DTC_L1_lower_cap_full_events` | `0` |
| `DTC_L1_io_lower_create_queue_full_stalls` | `0` |
| compact evidence | `generated/fast64_2_coupled_stress_alias_v2/` |

The finalized source path still requires a failed global-credit acquisition to
retain a candidate into the next cycle.  This run shows that `cap=512` did not
cause that condition at an attempted candidate pop; therefore entries-one
alone cannot produce the requested queue-full event.  The terminal reporter
does not expose the global lower peak, so the result does not justify deriving
or silently choosing a replacement cap from total requests.  The next
source-correct action is bounded diagnosis of a pressure-producing diagnostic
construction under existing authority; no performance configuration, Core
mechanism, R2 frozen dependency, or live job is changed by this record.

The frozen experiment matrix already names BICG as the first fallback payload
when NN does not reach the event.  A separate immutable-v2 BICG launcher is
therefore prepared with the same `cap=512, PIB=1` diagnostic overlay and a
fresh-audit requirement.  It has **not** been launched: the later one-worker
safe-admission slot was deliberately assigned to the small FAST64.3 ATAX Base
ramp, so BICG remains ready without competing with the critical R2 wave.

Its independent strict collector is also prepared.  It requires a natural
terminal receipt, exact immutable provenance, strict trace/parser/accounting
validation, and a separate machine-readable outcome for pressure-present
versus pressure-absent.  It is future-only and does not alter the NN evidence
or the frozen R2 closeout chain.

## BICG fallback acquisition (active; no result claim)

The fresh 60-second resource admission at
`/tmp/fast64-future-precompute-audit-20260908T164959Z-for-f2-recheck.tsv`
passed exactly one additional worker: swap-out/OOM/memory-PSI and throttling
were zero, cgroup headroom was 205,898,829,824 bytes, and output free space was
62,861,844,480 bytes.  The exact separate BICG immutable-v2 launcher was then
admitted without changing the R2 wave or its closeout closure.

| item | value |
| --- | --- |
| namespace | `fast64_2_precomputed_bicg_io_coupled_cap512_pib1_a1_r2` |
| mode / source-coupled controls | PAPER_IO / global cap `512`, IO PIB entries `1` |
| class | `PRECOMPUTED_FAST64_2_COUPLED_STRESS_PENDING_FAST64_1_ACCEPTANCE` |
| launch UTC / CPU | `2026-09-08T16:51:44Z` / `9` |
| immutable attempt UUID | `24e4fff0-e2c5-4832-b8d6-fec5ae911249` |
| Core / runtime / observer | `bbcbb5e...` / `6a8743b4...` / `2c2a6a27...` |
| formal Framework source | `037f008b330eb230353b60edf126d6be9f45afdc` |
| lifecycle | START receipt published; simulator CPU-active; initial failure scan clean |

This is physical precomputation only.  It cannot promote FAST64.2 before the
full immutable FAST64.1 R2 wave passes, and it cannot claim the forced-stress
gate until its own natural terminal, strict alias-aware collection, pressure
event observation and accounting checks complete.
