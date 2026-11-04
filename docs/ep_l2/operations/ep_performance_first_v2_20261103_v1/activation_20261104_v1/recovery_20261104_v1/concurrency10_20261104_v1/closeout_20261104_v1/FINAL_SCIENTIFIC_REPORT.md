# Performance-First V2: final authorized-range results

Status: COMPLETED. Sixteen new models consumed and CLOSED_ACCEPTED; zero technical failures or unaccepted consumed points. Two conditional GEMM combination points were not released. The approved range is complete; no further model is required. The original single execution owner exited naturally at 2026-11-04 03:04:43 UTC (11:04:43 China time).

## Source78 system family

Core 78f4b59e865b136eede74df74c44c210f5b4ca04; ELF 78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a. Exact Source5, input identity, immutable specs and accepted-point references are preserved per row in FINAL_RESULTS.json. Four exact historical REF points were reused and did not consume this budget. DRAM 850 MHz, L100 and Core/L2/ICNT 1132 MHz are unchanged.

| Workload | Hardware background | S cycles | WV_ZERO_RO cycles | WV cycles reduction vs own REF | S/WV |
|---|---|---:|---:|---:|---:|
| FWT | REF32x8, FR-FCFS128 (reused) | 181827 | 178951 | reference | 1.016071 |
| FWT | G64x16 | 170266 | 170105 | 4.9433% | 1.000946 |
| FWT | FR-FCFS256 | 181800 | 178769 | 0.1017% | 1.016955 |
| FWT | G64x16 + FR-FCFS256 | 170266 | 170105 | 4.9433% | 1.000946 |
| GEMM | REF32x8, FR-FCFS128 (reused) | 558588 | 550642 | reference | 1.014430 |
| GEMM | G64x16 | 548988 | 548988 | 0.3004% | 1.000000 |
| GEMM | FR-FCFS256 | 558588 | 550642 | 0% | 1.014430 |
| GEMM | G64x16 + FR-FCFS256 | NOT_RUN | NOT_RUN | condition false | NOT_APPLICABLE |

PROVEN: Enlarging Tag geometry improves absolute FWT WV performance, but S also improves and the same-background WV advantage contracts. The FWT combination adds zero cycles improvement over geometry alone. GEMM queue enlargement changes neither S nor WV cycles; geometry provides only 0.3004% WV reduction and eliminates the measured WV/S difference. These results do not demonstrate a system-resource change that selectively releases substantial additional WV benefit.

The GEMM combination release criterion is false: WV reductions are 0.3003766513% and 0%, below both permitted alternatives. Both points remain unconsumed. Budget arithmetic remains system 12 authorized, 10 consumed, 2 unspent conditional; highclock 6 authorized, 6 consumed, 0 remaining. Unspent conditional allowance is not automatically reusable. See CONDITIONAL_RELEASE_FINAL_DECISION.json.

Resource boundary: G64x16 has four times the REF32x8 Tag entries; physical Payload remains fixed. FR-FCFS256 increases scheduler and derived shared-credit resources (319 to 447); private credits and WB-progress allowance are unchanged. These are resource sensitivity results, not equal-area gains. Physical timing and PPA remain UNKNOWN.

## Repaired-Source Vector4M family

Core 862376f62ab19f9a677abe31c6a422028b44fcd0; ELF 083aa0d72173e8f27b298a76b88898bf117f44d119379b3e3ef9edd1b7ffa52b. All comparisons below use this one new Source/ELF and the exact qualified Vector4M input. These results are independent of Source78 and its historical technical failure.

| DRAM MHz | S cycles | F cycles | F cycles change vs same-background S |
|---:|---:|---:|---:|
| 850 | 77184 | 77237 | +0.0687% |
| 1275 | 53910 | 56038 | +3.9473% |
| 1700 | 45974 | 55925 | +21.6448% |

PROVEN: All six runs complete the full 56M instructions, 15625 CTA, kernel and required drain under the repaired production path. Faster DRAM improves absolute F cycles, but S gains more; F nearly plateaus from 1275 to 1700 MHz. No high-frequency EP speedup relative to matched S is demonstrated. High-frequency points are diagnostic system-service sensitivity, not calibrated hardware claims. This matrix does not isolate T; no F-minus-T comparison was run. The exact limiting F resource is UNKNOWN from performance alone and warrants only targeted follow-up engineering before another experiment request.

## Acceptance, archive and observation boundaries

All sixteen official true164 result archives were reopened and SHA256 checked at final closeout. Every accepted model has its original archive receipt plus FIRST and INDEPENDENT complete native-target restore proof: 32 restore validations. All accepted points satisfy their mode-specific kernel, CTA, instruction and hardware-drain contract. See ALL16_TRUE164_SHA_AND_RESTORE_RECEIPTS.json for complete SHAs and recovery locations. Existing Source assets remain KEEP; large Trace assets remain on verified true164 and were not copied locally.

Application observer NI gaps remain explicit: the active observation profile does not by itself prove application OFF/ON noninterference for each new profile or Source; B0/M0a application NI is NOT_PROVEN, and relevant new-profile/new-Source application NI is NOT_MEASURED. CPU correctness or CPU/golden NI is not promoted to application NI. This range contains no extra NI experiment, and no missing measurement is filled with zero.

Four naturally completed GEMM models encountered a postrun global Native hash guard after another owner's insert-only route registration. Main reviewed that delta, left the shared entry and foreign work untouched, and closed only those exact four completed outputs through their original registered scoped Native accept command. Immutable Source, ELF, specs, raw and consumed history were unchanged. No model was rerun; no failure was refunded. The postrun qualification and four Native closure receipts are included alongside this report.

## Final decision

Close this authorized range with all positive, zero and negative results retained. Do not release the two GEMM combinations or extend a frequency/queue/geometry scan automatically. Preserve the FWT absolute geometry result and the repaired cross-clock completion result, while recording their limited or negative matched EP advantage. Future work should prioritize a bounded F-specific service-cost check and concrete W/V structural candidates; any new application launch requires its own exact authorization and qualification. Paper editing remains inactive.

Machine-readable deliverables: FINAL_RESULTS.json; FINAL_PERFORMANCE_RESULTS.csv; CONDITIONAL_RELEASE_FINAL_DECISION.json; FINAL_SCOPE_CLOSEOUT_RECEIPT.json; ALL16_TRUE164_SHA_AND_RESTORE_RECEIPTS.json. The final small package has its separate true164 SHA and two recovery checks in FINAL_CLOSEOUT_ARCHIVE_RECEIPT.json.
