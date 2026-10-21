# Five accepted capacity/data-service diagnostic pairs — Lane D

Task: `D-CAPACITY-FIVE-INCREMENT`. E authority `1d30dc27d6f8da6e042b0ba08dedad2e069c46ff`. This is downstream offline analysis, not independent E qualification.

| Input | OFF cycles | ON cycles | ON−OFF | Speedup OFF/ON−1 | ON class |
|---|---:|---:|---:|---:|---|
| Conv | 292,932 | 268,117 | -24,815 | +9.2553% | UNKNOWN |
| CFD | 79,093 | 79,742 | +649 | -0.8139% | UNKNOWN |
| DWT | 166,519 | 157,034 | -9,485 | +6.0401% | UNKNOWN |
| SAD | 110,773 | 110,634 | -139 | +0.1256% | UNKNOWN |
| Vector | 73,696 | 42,788 | -30,908 | +72.2352% | UNKNOWN |

Fixed-five diagnostic GM: **1.1465847062× (+14.6585%)**. All five inputs, including adverse CFD, remain in the denominator. Speedup uses OFF/ON−1; cycle change uses ON/OFF−1 and is a different percentage. This GM does not enter main61 MAIN; the original-seven MAIN GM remains UNKNOWN.

Only Conv is newly decoded: eight hash-bound cached observations from the four-pair r2 snapshot are reused, and only E045/E046 completed accepted logs are observed once. No application/native/build/trace-body scan or active raw access; no controller, ledger, registry, budget, source, binary, or EN-v22 edits.

- [Scientific brief](SCIENCE_BRIEF.md) and [English paper candidates](PAPER_RESULTS_DISCUSSION_CANDIDATES.md).
- [Performance figure](CAPACITY_FIVE_PERFORMANCE.pdf), [Conv phases](CONV_CAPACITY_PHASES.pdf), [five-input phase deltas](CAPACITY_FIVE_STAGE_DELTAS.pdf), [lower-interface bytes](CAPACITY_FIVE_LOWER_TRAFFIC.pdf), [captions](FIGURE_CAPTIONS.md), [TeX table](CAPACITY_FIVE_TABLE.tex).
- [Exact ten endpoint identities](accepted_snapshot_05/EXACT_ACCEPTED_IDENTITIES.json), [E authority index](E_SOURCE_INDEX.json), [CONSUMED](CONSUMED.json).
- [Conv measured facts](CONV_MEASURED_FACTS.json), [complete terminal counters](accepted_snapshot_05/DIAGNOSTIC_TERMINAL_MECHANISMS.csv), [complete kernel input](accepted_snapshot_05/DIAGNOSTIC_KERNEL_AND_MECHANISM_DELTAS.csv).
- [Data checks](DATA_CHECKS.json), [receipt](RECEIPT.json), [file hashes](FILES_SHA256.json). `render.py` reproduces the four PDF/PNG figures using only frozen CSVs.

This diagnostic combines enlarged finite resources and bypassed L2 data service. It is not a hardware performance upper bound, an unlimited system, a V/RO measurement, or a new MAIN workload selection.
