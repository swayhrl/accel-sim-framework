# V3 final finite-scope performance results

Execution complete at2026-11-04 06:34UTC (14:34China time). All10 authorized starts consumed exactly once:8 accepted MID_TAG results and2 consumed Vector Host technical failures. No models or dispatcher remain in this scope. The finite executor naturally finished and published final HEAD0bdf465f1b87620ade800ebd1a766aad77e7dbf4 with remote readback. Main separately closes the finished request metadata; old budgets/history remain unchanged.

## Accepted absolute performance and resource frontier

Source78/ELF78d4e96b only; DRAM850MHz,L100,FR-FCFS128,Core/L2/ICNT1132MHz, physicalPayload1168 and all other accepted resources/observer111 remain fixed.

| Workload | Geometry | S cycles | WV cycles | WV reduction vs ownREF | Matched S/WV |
|---|---|---:|---:|---:|---:|
| FWT | REF32x8 reused |181827|178951|reference|1.016071|
| FWT | G32x16 new |169934|170225|4.8762%|0.9982905|
| FWT | G64x8 new |170266|170105|4.9433%|1.0009465|
| FWT | G64x16 reused |170266|170105|4.9433%|1.0009465|
| GEMM | REF32x8 reused |558588|550642|reference|1.014430|
| GEMM | G32x16 new |548988|548988|0.3004%|1.000000|
| GEMM | G64x8 new |548988|548988|0.3004%|1.000000|
| GEMM | G64x16 reused |548988|548988|0.3004%|1.000000|

PROVEN: G64x8 reproduces the1024-entry G64x16 S andWV cycles on both exact workloads with512 Tags/slice. G32x16 also reproduces GEMM, but its FWT WV is120cycles slower thanG64x8 and291cycles slower than its matchedS. FWT's best measured new512-entry S point isG32x16; its best new512-entry WV point isG64x8. GEMM ties all tested512/1024 organizations. Per-mode/per-workload optima are separate from a common design choice.

Decision: retain G64x8 as the preferred next common geometry candidate for these EP/WV workloads; do not enlarge FR-FCFS or Tag capacity automatically. Test additional inputs only under a new exact request. Two workloads do not establish universal8-way sufficiency. The result is sufficient for these64-set configurations, not a claim that the original32x8 is equally good.

Resource boundary:512 Tags/slice is twice REF's256 and halfG64x16's1024; nominal Tag-addressable capacity is4MiB instead of2/8MiB. PhysicalPayload remains1168 slots/slice (9.125MiB across64slices). This is a Tag-organization sensitivity, not synchronized SRAM shrink or measured equal-area benefit. G64x8 has8 way comparisons versus16 forG64x16; decoder, comparison, wiring, timing and PPA are not measured. Ordinary cache capacity also helpsS; the entire4.94% FWT or0.30% GEMM absolute WV gain is not EP-exclusive gain. MatchedWV benefit is about0.095% onFWT and0% onGEMM.

## Completion, identity and archive

AllFWT points complete180944896instructions,7040CTA,16kernels and required full hardware drain. AllGEMM points complete739246080instructions,1024CTA,onekernel and required full drain. The fourFWT acceptances/fullSHA/two-independent-native-restores gate was met before the fourGEMM consumptions. Each of all10 terminal outputs, including failures, has an official true164 archiveSHA and FIRST/INDEPENDENT native-target recovery proof:20 restore receipts. Main checked immutable receipt identities, source/spec/count/drain contracts; Trace and bulk tar contents were not redundantly rescanned. Complete references are in ALL10_ARCHIVE_AND_RESTORE_REVIEW.json.

GlobalEP cap10 was qualified and active across the Main controller, Native and resource adapter. It was not a ten-model fill barrier. OneMain controlled all10 points; no second dispatcher or competing publisher was created. Automatic30-minute progress and final publication worked. SOURCE_KEEP, all old failures/accepted results and V2'sunreleased allowance remain unchanged.

## Vector failure boundary

The two Source862 Vector1700 W/WV attempts were consumed CLOSED_UNACCEPTED due to a missing native_boot_id in generated specs; the monitor raisedKeyError and safely terminated each attempt. A masked second schema/population loss removed22 native library/tool pins. This was a Host generation and Main qualification error, not a Core/ELF or EP performance result. No accepted W/WV cycles exist; high-frequency package attribution remainsUNKNOWN. The old two-point budget is exhausted, failures archived, no retry/refund/replacement occurred.

Independent uninstalled repair adds preconsume43-field/schema and dependency closure checks. It passed124 synthetic/monitor checks and a realprivateCPU-stub run through the actual Host eventloop/loader/strace/PID/maps/env/AS/RSS/pipe/syscall path. These are engineering assurances, not GPU application acceptance, drain or appNI. Additional shell/cat dependencies and historical identity limits are explicitly recorded. The futuretwo-point repair scope is UNAUTHORIZED/NOT_REGISTERED; actual launch requires independent fresh authorization and qualified sole-owner handoff. Active/frozen assets were not patched.

## Next decision

Prioritize completing the separately qualified Vector Host repair and a new exact two-point request if the user wishes to recover the missing decomposition. First pilotW_ONLY acceptance/archive/two-restores can gateWV to limit sharedHost risk. Preserve both old failures.

For wider real-workload geometry validation, exact Source78 Stencil S/WV and3MM S identities are prepared. Both are historical long-tail costs (roughly3.7-4.8hoursStencil,7.1hours3MMS), not assumedshort. A new3MM matchedS/WV pair is possible, while absoluteWV improvement remainsUNKNOWN without its missingWV_REF; oneoptional newanchor is separately listed, never replaced withF or silently added. No next-workload point or CLEANquota/NI/frequency/source/trace-collection experiment is approved by this closeout.

Observer111 remains fixed; new geometry/mode applicationNI is NOT_MEASURED andB0/M0a NOT_PROVEN. No combinedSource78/862GM, standaloneT effect, universalworkload or physicalGPU/PPA claim is made. Paper editing remainsinactive.
