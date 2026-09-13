# Figure index and captions

All captions are English. Every plot is rebuilt from the compact Lane-E snapshots; observer evidence is diagnostic and is never part of the FAST12 GM.

## F01 — Primary performance: Base, IO, and OO

Base-normalized primary performance across the exact FAST12 membership. Bars are Base/IO and Base/OO speedups recomputed from accepted integer cycles; the final group is reported in the table, not mixed with workload bars.

Source mapping: `tables/E_PRIMARY_PERFORMANCE.tsv`. Assets: `figures/F01.svg; figures/F01.pdf; figures/F01.png`.

## F02 — Base structural pressure

Base-mode accumulated event counters normalized per million instructions. Categories are separate, nonexclusive counters and must not be added into a causal 100% breakdown.

Source mapping: `tables/E_BASE_PRESSURE.tsv, tables/E_BASE_PRESSURE_NORMALIZED.tsv`. Assets: `figures/F02.svg; figures/F02.pdf; figures/F02.png`.

## F03 — IO to OO mechanism evidence

Paired descriptive mechanism measures: IO HOL ready-younger active-SM-cycle exposure and OO out-of-order retirement fraction. They do not provide exclusive causal attribution.

Source mapping: `tables/E_IO_OO_MECHANISM.tsv, tables/E_PRIMARY_PERFORMANCE.tsv`. Assets: `figures/F03.svg; figures/F03.pdf; figures/F03.png`.

## F04 — Logical tag capacity sensitivity

Accepted Stage6 logical tag capacity sensitivity with same-mode normalization. Same-mode normalized speedup; accepted numeric points only. No universal optimum is inferred.

Source mapping: `tables/E_SENS_LOGICAL.tsv`. Assets: `figures/F04.svg; figures/F04.pdf; figures/F04.png`.

## F05 — Physical pool performance sensitivity

Accepted Stage6 physical pool performance sensitivity with same-mode normalization. 16.5-KiB BICG/GESUMMV markers are nonnumeric resource boundaries; Btree 16.5 stays numeric. No universal optimum is inferred.

Source mapping: `tables/E_SENS_PHYSICAL.tsv`. Assets: `figures/F05.svg; figures/F05.pdf; figures/F05.png`.

## F06 — PIB sensitivity

Accepted Stage6 pib sensitivity with same-mode normalization. Same-mode normalized speedup; accepted numeric points only. No universal optimum is inferred.

Source mapping: `tables/E_SENS_PIB.tsv`. Assets: `figures/F06.svg; figures/F06.pdf; figures/F06.png`.

## F07 — Physical-pool observer diagnosis

Diagnostic observer sweep at 24/32/48 KiB. The chart shows physical-full active-SM-cycle fraction; the linked table also retains occupancy lines/fraction, inflight, alloc-to-ready, L2 rates, cycles, and both IO no-free denominators.

Source mapping: `tables/E_PHYSICAL_OBSERVER_SYNTHESIS.tsv, tables/E_PRESSURE_DENOMINATOR_COMPARISON.tsv`. Assets: `figures/F07.svg; figures/F07.pdf; figures/F07.png`.

## F07 — Physical-pool observer diagnosis

Ten-panel diagnostic observer sweep at 24/32/48 KiB: cycles, allocated lines, occupancy fraction, pool-full active-SM-cycle fraction, inflight requests, alloc-to-ready average, L2 rates, and both IO no-free denominators. Capacity is controlled; internal mediators remain non-isolated.

Source mapping: `tables/E_PHYSICAL_OBSERVER_SYNTHESIS.tsv, tables/E_PRESSURE_DENOMINATOR_COMPARISON.tsv`. Assets: `figures/F07.svg; figures/F07.pdf; figures/F07.png`.

## F08 — IO/OO duplicate requests and payload ratio

Exact duplicate-share comparison for 12 workload pairs. IO comes from accepted Lane-C evidence; OO comes from qualified Lane-D observer telemetry. D×128 B is lower-request payload only, not DRAM or total-link traffic.

Source mapping: `tables/E_DUPLICATE_IO_OO.tsv, tables/E_DUPLICATE_PAYLOAD_RATIOS.tsv`. Assets: `figures/F08.svg; figures/F08.pdf; figures/F08.png`.

## F09 — Integrated evidence and boundary matrix

Evidence levels for the physical-pool mechanism chain. A controlled capacity intervention establishes workload-specific sensitivity, while the internal arrows remain non-isolated unless source-proven or explicitly bounded.

Source mapping: `tables/E_D6_ARROW_CLASSIFICATION.tsv, E_CLAIM_EVIDENCE_REGISTER.tsv`. Assets: `figures/F09.svg; figures/F09.pdf; figures/F09.png`.
