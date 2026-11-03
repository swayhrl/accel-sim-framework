# Execution and resource status V2

As of **2026-11-04T00:30:18.686451+08:00 (Asia/Shanghai)**, the original approved24-point scope has naturally settled: **13 accepted,1 technical failure,10 unconsumed technicalHOLD**.14 INTENTs retain unique UUIDs, consume-before-fork and no retry. All14 outcomes, including the failure, have genuine164 archive and two independent restoresPASS. Both scope claim sets are empty. Retention8 has0remaining; service16 has10remaining, restricted to its original unqualified high-clock cells. That remaining authorization is not a newSource budget.

The successor controller3463972/start_ticks1046887334 is now gone after its recorded natural finish at00:14:46 onNov4. DIRTY_ON completed570129cycles; it was neither reforked nor stopped. Local technicalHOLD worked: safe retention proceeded while the10 high-clock cells remained held. Final remoteHEAD **839f0485d7ead3c2bd62e2734385c1d91688c0d6** was independently read with `ls-remote` and matches the final publisher receipt. No new dispatcher or Gitwriter was created byAgentD.

| Source78,850MHz mode | FWT cycles | GEMM cycles |
|---|---:|---:|
| S |181827|558588|
| W-only |181635|558957|
| CLEAN-only ON |181441|553632|
| DIRTY-only ON |179267|570129|
| CLEAN+DIRTY WV |178951|550642|

Four same-mode MS-only ON/OFF application pairsPASS. OFF rows are controls, not extra performance points. These tests do not validate B0/M0aOFF. FullWV remains the fastest of these850MHz mechanism modes for both inputs; no new structure has application results yet.

At1020MHz, FWT S/WV=178339/177738 and GEMM S/WV=565690/551783. FWTWV reduces its own850 cycles0.678%; GEMMWV increases0.207%. GEMM same-backgroundS/WV improves from1.01443 to1.02520 becauseS worsens more; this is not an absoluteEP improvement. VectorS1275=53910 is retained as a diagnostic singleton; failedVectorF1275 is not replaced or refunded and cannot form an acceptedS/F pair.

Current hostMemAvailable=224.92GiB;174free=12.66GiB; verified foreign futureRAM=1.392GiB and remaining writes=2.184GiB; foreign metadata errors=0. No old35GiB pool was added again. Source78claimRAM/write carrier is now0. ActualSource78X disk usage is about149MiB, so globalSSD free-space decrease cannot be attributed to these small runs. BigTrace/raw/archives remain true164; noTrace body was scanned, copied or rehashed.

B's independent-j4 build forecast2-4GiB RAM and<=2GiB hot writes fits current conditions: after verified foreign writes, that2GiB increment and1GiB emergency floor, approximately7.48GiB remains. Reported90MiB build and0.79GiB peak **single child** do not establish aggregate-j4 peakRSS. Preserve the4GiB bounded engineering forecast until aggregate measurement is available. This engineering advice does not reserve resources or alter active admissionpolicy. Future science still requires a fresh scoped resource snapshot before consumption.

NewSYSTEM850 profiles and repaired-Source high-clock models remain unregistered/unstarted. AgentD changed only its independentV2 evidence/derived data; acceptedCore/ELF, originalcontrols, failures, budgets and archives are intact.
