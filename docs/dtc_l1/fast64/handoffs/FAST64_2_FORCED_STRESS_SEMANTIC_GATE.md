# FAST64.2 forced lower-create stress — semantic gate

Status: **RESEARCHER_DECISION_RESOLVED; POSITIVE COUPLED STRESS PREPARED**

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
the existing 80-SM NN/IO anchor has 2,673 lower requests, so it is the smallest
already provenance-resolved source-path candidate.  `cap=512` is deliberately
below the observed normal 80-SM lower concurrency scale while remaining far
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
