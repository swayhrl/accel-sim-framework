# Instrumentation v1.1 port-sampling closeout

## Scope and stop condition

This is a `STOP_AND_FIX` closeout, not a Round-1 characterization campaign.
It corrects only the observation point used for L2CHAR port-busy accounting.
The corrected-baseline cache admission, port replenishment, fill, tag, MSHR,
and DRAM behaviour are unchanged.  No broad workload sweep was launched.

All pre-fix campaign output is retained as `PRE_FIX_DIAGNOSTIC` in
`ROUND1_PRE_FIX_DIAGNOSTIC.md`; it is excluded from every formal heatmap.

## Revisions

| component | branch | revision | purpose |
|---|---|---|---|
| Core | `hrl/l2-resource-char-v1` | `32f9b8d52490044f487c14811121ed0368e48a48` | Latch native pre-replenish DataPort/FillPort busy state, exact invariants, and occupancy HIST records. |
| Framework | `hrl/l2-resource-char-exp-v1` | `abad633971f1622b9de80ede3423455a0c36d932` before this documentation commit | Parser/audit fixes and bounded closeout harnesses. |
| Frozen corrected Core | frozen worktree | `8830fc9683a9993a85e628a4f2a9a4c35f5dd5bc` | Unmodified reference. |
| Frozen corrected Framework | frozen worktree | `a65561df482213daec03125e03546eb414c90573` | Unmodified tracked reference; it has pre-existing untracked review artifacts only. |

The core change latches the exact booleans used immediately before native
`sample_cache_port_utility()` and before `replenish_port_bandwidth()`.  The
existing L2CHAR sampling location remains unchanged, but consumes these
latched values.  Therefore it cannot change port availability or admission.

## Exact port crosschecks

Every value below is an integer sum over the final 64-slice records.  The
`native_*` counters come from `cache_stats`; `char_*` are L2CHAR counters from
the same pre-replenish sample.  `port_samples` also matches exactly in every
case.

| case | native data | L2CHAR data | native fill | L2CHAR fill | port samples | result |
|---|---:|---:|---:|---:|---:|---|
| C4 DataPort directed | 992 | 992 | 0 | 0 | 6,907 | PASS |
| C8 FillPort directed | 0 | 0 | 64 | 64 | 800 | PASS |
| `fastWalshTransform` (`logK_11`, `logD_19`) | 2,031,616 | 2,031,616 | 131,072 | 131,072 | 10,990,208 | PASS |
| Parboil `spmv` (`Dubcova3_large`) | 50,849 | 50,849 | 375,334 | 375,334 | 1,544,576 | PASS |

The C4 directed fixture remains `eligible=1300`, `blocked=930`,
`requests=30`, and `episodes=30`, identical to its pre-fix fixture result.
The C8 fixture remains `fill_eligible=33` and `fill_blocked=31`; it now also
checks the native/L2CHAR busy integers explicitly.  Hence the observation
fix did not alter DataPort or FillPort blocking semantics.

## Timing neutrality and host cost

The bounded equivalence harness passed both required checks:

* **C1 PASS:** frozen corrected baseline versus fixed Core with L2CHAR off:
  terminal cycles, instructions, native L2/DRAM statistics, and filtered
  native output are identical.
* **C2 PASS:** fixed char-off versus char-on: the same simulated/native values
  are identical after removing L2CHAR records and configuration echo.

The same `fastWalshTransform` trace was also replayed once with L2CHAR off
only to quantify host cost.  Both arms finished at exactly 171,722 simulated
cycles and 180,944,896 instructions.  On this shared loaded host, char-off
was 237.72 s / 679,476 KiB and char-on was 551.06 s / 667,268 KiB, a 131.8%
wall-time increase.  This is a host-cost measurement, not a simulated-timing
change.  It is retained for review because it is higher than the earlier
20--25% estimate; no optimization was attempted in this closeout.

## Histogram and audit corrections

The parser now aggregates exact merged histograms (never averages per-slice
percentiles) for:

1. Reserved ways
2. MSHR entries
3. MSHR targets
4. Merge depth
5. MissQ occupancy
6. MissQ writeback occupancy
7. ICNT-to-L2 queue occupancy
8. L2-to-DRAM queue occupancy
9. DRAM-to-L2 queue occupancy
10. L2-to-ICNT queue occupancy
11. ROP occupancy

Each reports global AVG/P50/P95/MAX.  Finite resources use bounded dense
histograms; ROP uses the sparse encoding.  Parser unit tests cover weighted
two-slice merge and sparse ROP merge, including exact P50/P95/AVG/MAX.

Early-sanity causal semantics were also corrected:

* `RESPQ_FULL` supporting occupancy refers to **L2-to-ICNT**, not
  DRAM-to-L2.
* Event-time blocker records are authoritative.  A sampled queue not reaching
  capacity is a warning only, never evidence against a blocker.
* `eligible=0` has ratio `NA`.
* The performance-derived column is named
  `sim_instructions_per_cycle`, never ordinary `IPC`.

## Formal runner readiness

The next formal Round-1 runner is pinned to Core
`32f9b8d52490044f487c14811121ed0368e48a48` and the Framework revision
recorded in this closeout, with:

```text
L2CHAR enabled                 = 1
window                         = 5000 L2 cache cycles
set detail / windows           = 1 / 1
dram_issue_hold / returnq_hold = 0 / 0
all directed test hooks        = 0
QV100 corrected baseline       = unchanged
per-run timeout                = 8 h
```

It will not read or merge `PRE_FIX_DIAGNOSTIC` result directories.  No formal
Round-1 workload was started by this change.

## Evidence and review material

The archive described by
`review_packs/INSTRUMENTATION_V1_1_PORT_FIX_CONTENTS.md` contains the source
diffs, validation logs, natural sample CSV/JSON output, hashes, status, and
this document.  It intentionally keeps raw pre-fix campaign logs outside the
formal result set.

## Decision

**ROUND1_GO** for the corrected Instrumentation v1.1 functionality: port
sampling is exact, blocking semantics are preserved, parser/audit semantics
are fixed, and timing neutrality is demonstrated.  The elevated measured host
cost is recorded as a review item for campaign scheduling; it does not alter
the simulated model or invalidate the port/accounting GO criteria.
