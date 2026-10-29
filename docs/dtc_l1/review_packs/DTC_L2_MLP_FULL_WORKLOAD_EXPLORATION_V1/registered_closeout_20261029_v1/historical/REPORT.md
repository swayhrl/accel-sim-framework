# Historical long-tail status (read-only)

Observed UTC: 2026-10-29T01:30:15.518623+00:00

Current DTC-L2 full-35 and IR are separate and excluded. No simulator, controller, Goal, health model, Git or READY operation was performed.

Old downstream18 is CLOSED: all 18 results are strict performance accepted, archived and restored. All 18 native restore paths exist. MVT DH-PQ is naturally complete, not still running.

| Program | Lane | P0 cycles | PQ cycles / P0 | PS cycles / P0 |
|---|---|---:|---:|---:|
| ATAX | CH | 28428842 | 30737948 / 1.081224 | 20724681 / 0.729002 |
| ATAX | DH | 31880220 | 33774401 / 1.059416 | 19369013 / 0.607556 |
| MVT | CH | 26581175 | 23576996 / 0.886981 | 18407388 / 0.692497 |
| MVT | DH | 34687540 | 35470077 / 1.022560 | 21811979 / 0.628813 |
| BICG | CH | 26298698 | 24356422 / 0.926146 | 22474128 / 0.854572 |
| BICG | DH | 28685812 | 29194658 / 1.017739 | 18363200 / 0.640149 |

Each lane has its own P0=1; lower ratio is better. Core 9eedb3131937748f0492fa83aad37d3691118d70; Framework 02775fd795cde5aae1480d81cee6eb481d0a08f4; binary 02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d. Every run has 2 kernels / 145666048 instructions / 32 CTA. P0 clocks are 1410:1410:1410:850 MHz. PQ changes partition queues 64:64:64:64 to 64:256:64:64; clocks unchanged. PS changes only DRAM clock to1700 MHz relative to P0. Scope is NEW_DOWNSTREAM18_ONLY, never original288.

MVT DH-PQ takes2.26% more cycles than its P0; widening this queue did not improve that point. MVT DH-PS reduces cycles37.12%. Across these three DH points, PS improves substantially while PQ is adverse. This supports downstream service-rate sensitivity; it does not prove an exclusive DRAM-bandwidth bottleneck. In MVT DH, P0/PQ/PS L2 reservation-fail counts are161531923/177897694/75082505 and dramfull counts152064800/167782540/76748182. These are aggregate event counts, not stalled fractions. CH lower-cap and PIB-full counters are0 for all9points, with lower-outstanding peak1189?1358 below cap32768; the corresponding DH-specific counters are missing (not zero).

Original V100: registry RUNNING is not model liveness.284starts /281receipts /72 registered remaining; /proc shows0native simulator. Result states: {'PASS_STRICT_ARCHIVE_NATIVE_RESTORE': 251, 'ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS': 7, 'ENGINEERING_MODEL_GONE_RECEIPT_MISSING_PRESERVED': 1, 'FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY': 19, 'RESOLVING_ISSUE_NO_MODEL_RETRY': 6}. Three unrecepted outputs are stopped/unaccepted and preserved; they are not live or accepted cycles. Legacy R6 controller and final waiter remain sleeping; no intervention. Current registry admits71 inputs/284specs, so older72-input/288 plans cannot be certified complete from this snapshot.

Repair requests23+4+2+4+12 are CLOSED and have all execution receipts; these are correctness-validation results, excluded from accepted performance comparisons.

Historical EP simulator liveness is independently confirmed by stable PID/start generation and CPU-tick increases in two samples10seconds apart:

| Cohort | PID/start | Elapsed h | CPU tick delta | Last telemetry cycle |
|---|---|---:|---:|---:|
| EP_PERF_SYRK_90B0CC9D_S_REF_V1 | 2053685/989697704 | 25.67 | 997 | 8335000 |
| EP_PERF_SYRK_90B0CC9D_F_REF_V1 | 2194211/994648903 | 11.91 | 997 | 3595000 |
| EP_PERF_LAVAMD_51FAFFD2_F_REF_V1 | 2224914/995749284 | 8.86 | 999 | 3805252 |

EP raw streams are unfinished and the telemetry is provisional. No validated remaining-work total exists for an ETA. Snapshot windows and configuration/evidence identities are in STATUS.json. No scientific acceptance is inferred from a live process or a progress counter.

Evidence: STATUS.json contains two process snapshots, source SHA256 references, all18 strict rows, all284 old result identities,3receipt gaps and latest EP telemetry windows. MANIFEST.json hashes report and JSON.
