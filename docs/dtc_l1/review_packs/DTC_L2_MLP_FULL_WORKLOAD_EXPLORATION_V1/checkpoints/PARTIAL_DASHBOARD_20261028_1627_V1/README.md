# Partial L2 concurrency dashboard — 315 / 350 accepted

Snapshot: 2026-10-28T08:27:11.231043+00:00 (2026-10-28 16:27 CST). This is a frozen intermediate report, not the final 35-program result. The original matrix has 315 accepted cells (309 fresh + 6 exact references), 12 confirmed live cells, 22 pending cells and one original engineering-negative with no accepted cycles. The independent scan/M16-V2 trial remains outside all primary statistics.

[Open the self-contained dashboard](dashboard.html) after downloading, or inspect [the complete machine-readable report](report.json), [all 350 point identities](ALL_350_POINTS.json) and [the sensitivity figure](sensitivity.png). GitHub displays HTML source rather than executing the dashboard.

## Uniform DH sensitivity — partial coverage

Ratios are DH P0 cycles / DH variant cycles; >1 means faster. Every row is one uniform configuration. The available population changes by row; the common column uses exactly the same 30 inputs across all eight variants. Neither population is the final 35-input suite. Missing and failed values are excluded with explicit coverage, never filled with 0 or 1.

| Profile | Available n / 35 | Available GM | Faster / equal / slower | Common-30 GM |
| --- | ---: | ---: | ---: | ---: |
| E384 | 32 / 35 | 1.000874 | 5 / 21 / 6 | 1.000721 |
| E768 | 32 / 35 | 1.000874 | 5 / 21 / 6 | 1.000721 |
| M8 | 31 / 35 | 1.000289 | 5 / 19 / 7 | 1.000490 |
| M16 | 30 / 35 | 1.001027 | 5 / 20 / 5 | 1.001027 |
| Q64 | 31 / 35 | 0.997136 | 4 / 19 / 8 | 0.997180 |
| Q128 | 31 / 35 | 0.996752 | 4 / 19 / 8 | 0.996840 |
| F128 | 31 / 35 | 1.013004 | 7 / 18 / 6 | 1.008535 |
| F256 | 31 / 35 | 1.019762 | 7 / 18 / 6 | 1.011969 |

Non-P0 matched CH coverage is zero in this snapshot. CH self speedup, same-profile CH/DH and relative DTC improvement remain unavailable for the variants. The partial DH numbers cannot establish a DTC-versus-CH improvement, a final winning configuration or phase completion. Suite groups and individual input SHA/cycles/traffic are in report.json.

## Evidence and preservation

The immutable 314-result base is commit `9389c78bb1e858f8969eb220762459a6da9996ba`, checkpoint `EXISTING_RESULTS_20261028_V3_DELTA`. All its accepted RESULT SHA, UUID and cycles were rechecked unchanged. This package adds only the existing naturally completed sgemm DH-Q64 RESULT (`409417` cycles; UUID `dfe621a1-493e-4dd4-b423-b41387cfb623`; SHA `2668d4cb8086c5e700bcb903b5f6fcb614d44138d99dd7e4401f5afe99bd3720`) in a byte-reconstructible compressed document. All 315 accepted native RESULT hashes and cycles were rechecked during packaging. The Q64 observation and original result retain strict physics + CPU2 + IO and the 25-entry true164 archive/native-restore evidence. This publication does not replace that consumer with a new validator.

The report generator is the unchanged 74-check CPU-qualified source at commit `fce10d92eb09bc8f562b84a5a84b202bbf1ea385`, `agents/D/report_v1/build_report.py` under this review pack, SHA `9ad9cdf8db29eb062f8053b51b3396a1bac6ff9132f6ad0d89ac64aac58786d7`. The snapshot historical `UNCOMMITTED_GENERATOR_SHA_IS_CANONICAL` field is preserved verbatim; this post-generation lookup supplies the already-committed exact source identity. No generator changes or test reruns were needed. `REPORT_MANIFEST.json` verifies the original four generated artifacts; `MEMBER_MANIFEST.json` covers this package.

Runtime-label caveat: the copied batch field `dynamic_memory_budget_fraction: 0.88` is a historical controller label, not the active policy. CPU2 future admission is the separately published 95%-after-10GiB-floor policy (actual deployment commit `1194c64ac8bcca916ab63d80caf64fa0f8c32365`). Do not use that frozen batch label for current resource decisions.

Negative-state caveat: the unchanged generic report label `SPENT_LIVENESS_UNVERIFIED_AWAITING_TERMINAL` for scan/M16-V1 is not a new failure or an accepted performance result. The authoritative typed engineering-negative and final-disposition boundary are documented in `operational/SCIENCE_TRANSITION_REVIEW_CPU2_V1` (commit `59b2515641a4c7b186c892f108dbfe4478f655e2`). No original receipt, cycle value or ledger is replaced, and no automatic M16-V2 union is performed.

Core `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, binary `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`, DRAM850MHz and 10MiB L2 capacity remain fixed. FR-FCFS window changes also affect partition credits. Counts are structure limits, not physical area or occupancy. Missing counters remain missing; last-printed latency is not a weighted whole-application average. Trace acceptance does not prove whole-application numerical correctness.

No simulations, new controllers, registry grants or policy changes were made to publish this package. The seven unresolved identities, old experiments and English v0.23 remain unchanged. Single-factor completion, combinations, range extensions and matched full35 CH validation remain outstanding; Goal ACTIVE.
