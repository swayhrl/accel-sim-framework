# V2: display-only program fallback, real closed cycles restored

The v1 program field lookup incorrectly treated an optional display label as qualification data. V2 changes only:

    program=s.get('program',s.get('workload',UNKNOWN))

A missing label now remains UNKNOWN without rejecting a fully qualified result. Every Source/input/Spec/mode/drain/population/full-SHA/two-distinct-restores gate is byte-for-byte unchanged. Original v1 seven sealed files and its manifest are preserved.

One real read-only --once was explicitly authorized and executed. The saved JSON includes the exact coherent authority token; the MD is extracted from that same JSON, not a second live run.

Qualified A3 cycles: S200330 and WV200972. Both are unchanged versus their final FAMILY_SCOPE same-mode REF: signed delta0, reduction0%.

Qualified original V3 cells:

| Workload/mode | G32W16 | G64W8 |
|---|---:|---:|
| FWT S | 169934 | 170266 |
| FWT WV | 170225 | 170105 |
| GEMM S | 548988 | 548988 |
| GEMM WV | 548988 | 548988 |

At this snapshot A1 remains UNKNOWN because its registry state is CONSUMED_BEFORE_FORK. B W remains UNKNOWN with PARSE_HOLD; B WV has no consumed registry cohort. No cycles are inferred for them. The reporter has no dispatch, retry, repair, publication or background behavior.

Main may run the standalone reporter again when desired:

    python3 -B /root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/activation_20261104_v1/closed_result_report_candidate_v2/closed_result_report.py --once

The default is foreground read-only stdout JSON with same-snapshot Markdown embedded; --format md prints Markdown. No raw logs, Trace or archive bodies were read. No registry/controller/source/runtime edits or model starts occurred. See PATCH_PROVENANCE.json and PATCH_VALIDATION_RECEIPT.json for the exact change and verification.
