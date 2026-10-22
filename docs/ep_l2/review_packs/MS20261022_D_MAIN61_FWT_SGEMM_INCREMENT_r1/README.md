# FWT restoration and SGEMM exploration — incremental Lane D analysis

E authority `8556058b9151ab44f580f49dd5139dad46b08566`; only published CURRENT_ACCEPTED pairs and exact endpoint summary counters are consumed. No simulator/native/build/raw/trace scan or E qualification is performed.

| Input | S cycles | F cycles | Saved cycles | Speedup | Cohort |
|---|---:|---:|---:|---:|---|
| FWT | 493,189 | 490,402 | 2,787 | +0.5683% | Original MAIN restoration, sixth pair |
| SGEMM | 343,730 | 343,442 | 288 | +0.08386% | Separate frozen-trace exploration |

Original MAIN accepted-six subset GM: **0.9990537501× (−0.094625%)**. Original-seven MAIN GM remains **UNKNOWN** (Btree HOLD). SGEMM does not replace Btree or enter that denominator. Previously delivered five-pair capacity diagnostic remains separate and unchanged.

- [Scientific brief](SCIENCE_BRIEF.md), [English paper candidates](PAPER_RESULTS_DISCUSSION_CANDIDATES.md), [captions](FIGURE_CAPTIONS.md).
- [Cohort performance figure](MAIN61_PERFORMANCE_BY_COHORT.pdf), [mechanism profile](FWT_SGEMM_MECHANISM_PROFILE.pdf), [nonexclusive waits](FWT_SGEMM_WAIT_OBSERVATIONS.pdf).
- [New pair performance](NEW_PAIR_PERFORMANCE.csv), [accepted-six MAIN data](MAIN61_SIX_ACCEPTED_PERFORMANCE.csv), [complete mechanism table](NEW_PAIR_TERMINAL_MECHANISMS.csv).
- [CONSUMED](CONSUMED.json), [exact identities](EXACT_ACCEPTED_IDENTITIES.json), [E source commits and hashes](INTAKE.json), [receipt](RECEIPT.json), [checks](DATA_CHECKS.json), [hashes](FILES_SHA256.json).
- [Kernel-timing coverage](KERNEL_TIMING_AVAILABILITY.json): no per-kernel elapsed timing was exported; preserve UNKNOWN and [request only existing metadata](MINIMAL_E_KERNEL_METADATA_REQUEST.json). This does not block whole-app delivery.

EN-v22 and all old outcomes, HOLD/INCOMPLETE and frozen analysis packs remain unchanged. `project.py` reuses existing `full_v2_analysis.mechanism_table` and `csvout`; it is a downstream projection, not another acceptor. `render.py` reads only frozen derived tables. Both run from the D worktree root.
