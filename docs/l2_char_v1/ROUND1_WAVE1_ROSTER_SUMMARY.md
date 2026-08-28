# Round-1 Wave-1 Roster Reconciliation

This is the workload-level correction to the physical-asset preflight
inventory.  The authoritative historical candidate pool is **52 workloads**,
not “about 53” and not the 159 physical trace roots.

The full table is [`ROUND1_WAVE1_COST_ROSTER.tsv`](ROUND1_WAVE1_COST_ROSTER.tsv).
It was reconciled from
`accel-sim-decoupled-l2/docs/decoupled_l2_workload_roster_under_5h.md` against
the current physical inventory by suite, workload, declared input, absolute
`kernelslist.g` path, asset family, and list SHA256.

## Reconciliation result

| Item | Count | Meaning |
|---|---:|---|
| Historical workload entries | **52** | Exact total in the authoritative under-five-hour roster. |
| Current physical roots | 159 | Asset copies/variants, not workload count. |
| Current path mapped for roster | **52/52** | Every workload has one directly runnable local trace asset. |
| Trace-body identity manifest | **52/52** | 2,610 referenced trace files, 62,138,865,619 bytes (57.87 GiB). |
| Historical result with body-SHA proof | 0 | Legacy records did not preserve body SHA, so historical equivalence is not asserted. |

There is no 53rd entry to reconcile: “about 53” was a loose historical
description.  This report uses the documented 52-row roster as the sole
Wave-1 source of truth.

## Cohorts and proposed decisions

| Cohort / decision | Count | Treatment |
|---|---:|---|
| `PRIMARY_FULL` / `RUN` | 34 | Complete public/archive workload assets; campaign candidates after the final multi-kernel gate. |
| `PRIMARY_FULL` / `NEEDS_REVIEW` | 1 | Rodinia BFS: runnable current input, but legacy completion evidence does not prove the exact historical graph input. |
| `MICROBENCH` / `UBENCH_ONLY` | 6 | Run as resource/instrumentation sanity cases; exclude from workload-heterogeneity aggregates. |
| `DERIVED_TRIMMED` / `SECONDARY_TRIMMED` | 1 | SRAD 1/40: useful diagnostic but never a full-input proxy. |
| `V100_BOUNDED` / `SECONDARY_BOUNDED` | 5 | Mars/SHOC traces previously exercised only in bounded replay; natural-drain qualification is required. |
| `V100_SPECIAL` / `NEEDS_REVIEW` | 5 | ISPASS/Pannotia V100 assets; retained, but need current-runner natural-drain gate. |

So the formal main-workload candidate set is **35 full entries** before the
post-run qualification; it is not yet a claim that all 35 will appear in a
paper result.  `RUN` means eligible to enter the current-baseline campaign,
not “already scientifically accepted.”

## Cost and memory evidence

Historical time is a scheduler prior only, never a current performance datum.

| Runtime class | Count | Note |
|---|---:|---|
| `<1h` | 32 | Includes short CUDA SDK, many Parboil/PolyBench items, and known ubench cases. |
| `1–4h` | 8 | Includes scan, L2 bandwidth, cutcp/histo/3mm, and bounded Mars ss. |
| `4–8h` | 0 | No authoritative roster entry falls here. |
| Unknown or bounded-only | 12 | Must obtain a current natural-drain cost before production scheduling. |
| `>8h` | 0 in Wave-1 | Deferred outside the 52-row roster. |

Deferred-known-long cases are PolyBench `syrk` (~17–19h), PolyBench `fdtd2d`
(~44.5h), and TLS SHOC `st2d` screen (~8h13m).  They remain available as
secondary assets and were not discarded.

Peak RSS evidence is sparse but explicit: 3 direct current-tree measurements
(`atax`, `bicg`, `mvt`), 10 cross-project priors, and 39 unknowns.  The largest
known priors are Parboil `sgemm` 7.8 GiB and PolyBench `gemm` 6.45 GiB.

At this snapshot the host has 377 GiB RAM, approximately 169 GiB
`MemAvailable`, 512 logical CPUs, and fully used 2 GiB swap.  With a 30%
headroom policy, the instantaneous simulation budget is about 118 GiB.  There
is intentionally **no fixed application-count concurrency** for the 39
unknown-RSS rows.  The safe first-wave rule is:

1. profile unknown-RSS assets before a paired experiment;
2. cap first profiling launches at 10 only while a launcher checks
   `MemAvailable` and stops before 96 GiB;
3. after profiling, pack 1.25 × observed RSS below the 118 GiB budget;
4. run the 10 GiB-reserved `sgemm` and 8 GiB-reserved `gemm` in isolated or
   low-concurrency slots; paired arms reserve twice the single-arm amount.

## Selected trace identity

The user explicitly authorized selected-roster hashing but not a 159-root
bulk scan.  [`ROUND1_WAVE1_TRACE_MANIFEST.json`](ROUND1_WAVE1_TRACE_MANIFEST.json)
therefore records every referenced `.traceg` or `.traceg.xz` file’s SHA256 and
each workload’s canonical aggregate `trace_tree_sha256`.  It covers the 52
mapped assets only.  The roster TSV references the aggregate hash and file
count on every row.

This proves the identity of the **current** selected assets.  It does not
retroactively prove legacy-run identity, because those historical directories
did not preserve trace-body SHA256.

## Multi-kernel output gate — completed

The short multi-kernel production replay is retained at
[`round1_pilots/fastWalshTransform_11_19/`](round1_pilots/fastWalshTransform_11_19/).
It naturally drained 16 launches: 12 `fwtBatch2`, 3 `fwtBatch1`, and 1
`modulate`, for 180,944,896 instructions and 171,722 simulation cycles
(506.38 host seconds, 642 MiB peak RSS).  The parser emitted one `summary.csv`
row, 64 slice rows, and 2,624 window rows; all invariants passed.

This proves the important current semantic: **L2CHARV1 is application
aggregate, not kernel-decomposed.**  The manifest correctly says
`kernel=all,kernel_id=all`; it does not invent per-kernel L2 shares from 16
launches.  The cumulative simulator log can identify launches, but its
end-of-kernel counters are not a stable kernel-level resource schema.

Wave-1 can therefore begin only as an application-level qualification campaign.
If later work requires dominant-kernel resource results, it must add a
deliberate per-kernel collector/runner contract before claiming such shares.
No broad characterization workload was launched while establishing this gate.
