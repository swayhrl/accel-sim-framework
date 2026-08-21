# Phase-3 FRC execution record

## Branches and commits

- Core branch: `hrl/l2-frc-baseline-v1`.
- Experiment branch: `hrl/l2-frc-exp-v1`.
- The corrected conventional control includes core commit `5721256a`, which
  preserves dirty victim payload when a baseline read miss creates a lower
  writeback.
- FRC implementation commits are intentionally narrow: entry/configuration,
  delayed swap and partition-local sector fetch, statistics/timing, explicit write/atomic
  fallback, same-line ownership blocking, and primary-sector swap gating.

## Reproducible checks

With `LATEBIND_L2_GPGPUSIM_ROOT` set to the FRC core worktree and an SM7 QV100
configuration, run:

```bash
scripts/check_l2_frc_disabled.sh --trace <kernelslist.g> --config <gpgpusim.config> --trace-config <trace.config>
scripts/check_l2_frc_smoke.sh --trace <kernelslist.g> --config <gpgpusim.config> --trace-config <trace.config>
scripts/check_l2_frc_directed.sh --config <gpgpusim.config> --trace-config <trace.config>
scripts/check_l2_frc_atomic_fallback.sh --trace <atomic-kernelslist.g> --config <gpgpusim.config> --trace-config <trace.config>
scripts/run_l2_frc_sweep.sh --trace <kernelslist.g> --config <gpgpusim.config> --trace-config <trace.config>
```

The directed suite uses a 1-set/1-way L2 only to make replacement deterministic.
It checks: one partition-local fetching sector; FRC-set-full fallback; a same-sector
write stalled during `FETCHING`; dirty victim ownership
through lower writeback acceptance; partial-write fallback; and flush without
live FRC state.  It is not an equal-capacity performance configuration.

## Completed gates

| Gate | Result |
|---|---|
| FRC disabled equivalence | Same small-trace architectural metrics as the corrected control: 5,526 cycles, 256 instructions, 4 L2 accesses/misses. |
| Sector read smoke | One allocation sends one lower sector read and completes a clean swap. |
| Sector ownership | Directed two-warp case emits one FRC allocation and one lower read. |
| FRC-set-full fallback | Directed one-entry case reports `set_full_fallbacks=1`. |
| Same-line write ownership | Directed case reports `write_conflict_stalls=144`, then one baseline write fallback after swap. |
| Dirty victim path | Directed case reports `dirty_swaps=1`, `wb_lower_accepted=1`, and terminal `fetching=fetched=evicting=0`. |
| Atomic semantics | Atomic workload has identical control/FRC architectural metrics (204,016 cycles); nonzero `atomic_fallbacks` confirms the explicit baseline path. |
| Conservative timing | `management_cycles` is nonzero when configured; paper mode reports zero added management cycles. |

## Small pressure sweep

The pressure trace intentionally has no all-reserved victim benefit.  It is a
mechanism sanity point, not a performance claim:

| Variant | Cycles | L2 accesses/misses | FRC allocations | Lower sector reads | Management cycles |
|---|---:|---:|---:|---:|---:|
| control | 6,060 | 513 / 513 | 0 | 0 | 0 |
| frc32-paper | 6,065 | 513 / 513 | 257 | 1,028 | 0 |
| frc64-paper | 6,065 | 513 / 513 | 257 | 1,028 | 0 |
| frc32-conservative | 6,065 | 513 / 513 | 257 | 1,028 | 514 |

The +5-cycle result is expected for this trace: it exercises FRC allocation
but not the paper's reservation-conflict opportunity.  The historical result
used an invalid whole-line fetch path and is retained only as a superseded
development record; current experiments use one partition-local sector read.
Any research comparison must use the matched-capacity rule in
`phase3_contract.md`; `frc128`/`frc256` are not free storage.

## Real trace development check

The existing Accel-Sim ubench `l2_lat` trace was run unmodified under the same
QV100 configuration in control and `frc32-paper` modes.  It is a serial
store-heavy latency microbenchmark (47,221 instructions), so it is also a
useful check that the explicit non-FRC path remains exact:

| Variant | Cycles | L2 accesses/misses | FRC reads | Write fallbacks |
|---|---:|---:|---:|---:|
| control | 5,665,292 | 36,868 / 1,027 | 0 | 0 |
| frc32-paper | 5,665,292 | 36,868 / 1,027 | 0 | 4,099 |

The equal architectural metrics and cycles are expected: all L2-side traffic
that reaches this trace's FRC-enabled model is write traffic, and therefore
uses the explicit baseline fallback.  This is a semantic regression result,
not evidence for or against FRC performance on read-conflict workloads.
