# AG4 — STOP_PRELAUNCH_CPU_QUALIFICATION_INCOMPLETE

Actual new starts2/5; new full strict observations1; completed optimization results0. Three remaining reservations were never started. No retry, replacement, patch-and-resume or old UUID reuse.

The prelaunch CPU gate was incomplete: the PID-reuse negative tested direct classification but missed the production retired-PID wait-dispatch path. Frozen owned/states retain retired IDs, allowing an unconfirmed reused-ID stop to reach resume before fresh parent-event proof. A source-level execution of the unchanged dispatch AST demonstrates this gap; actual PID reuse in either performance run is NOT_ESTABLISHED. See FINAL_CPU_QUALIFICATION_DECISION.json and ROOT_CAUSE_AND_FIX_TERMINAL_SUPPLEMENT.md.

|Point|Recorded outcome|Integer cycles|Comparison eligibility|
|---|---|---:|---|
|Imported prior AG3 GEMM|Original full strict;91 reuse identity checks|1071405|Recorded prior control only|
|New BASE_Gaussian|Full strict and all frozen T1-C common/traffic calibration|3278356|Recorded calibration only; executor gate incomplete|
|AE_GEMM|Stopped via verified own coordinator signal; strict failed|UNAVAILABLE|No performance result|
|AE_Gaussian|Never started|UNAVAILABLE|No performance result|
|AD_GEMM|Never started|UNAVAILABLE|No performance result|
|AD_Gaussian|Never started|UNAVAILABLE|No performance result|

Gaussian completed510kernels/513commands/65790CTA/283685120active-thread instructions,33778actual map snapshots and1020parent-event proofs. Its original strict receipt is preserved. No AE/AD speedup, native correctness or full discovery convergence is claimed. All ratios are withheld.

This STOP was a newly identified execution-authority qualification gap, not the earlier transient I/O window or isolated host swap pages. Runtime resources were CONTINUE at the own-signal decision; no actual mapping SHA mismatch or external DTC simulator was observed. The stopped AE_GEMM raw/strict/signal receipts remain unchanged.

CPU repair publication cbde7120c44976fe9eac678547eb2da4ade355f9 preceded new UUID generation. Preregistration9ece18f6fdb6de16ee95f35caa6fad1fec765fc9/tree57209f5898f2b7443e1a560ef64c470a8a429842,manifest65c8f58fcce618f0de5a80a89085386841e6050cc618fe58d7cbca40f8a6b79e was pushed/fetched and84blobs/clean verified before first start. All81 registered files remain unchanged; Core c8090115 and exact old actual ELF/library are untouched.

POST_TERMINAL_IDENTITY_AND_PROCESS_LOCK.json verifies1267current/historical AG4 CPU/model/helper/coordinator instances absent and own FLOCK0. HISTORY_FINAL_PRESERVATION.json verifies old AG3 2/6actual1full, old AG1/8actual0full, AA5 1/4actual0full and original failures unchanged; five new UUIDs are disjoint from347fixed-history UUIDs. No Englishv0.17/old44/GM12 edit or future automatic dispatch.

Large raw stays in /workspace/dtc-lane-ag4-authority-aead-174-v1/raw. Final GitHub HEAD/tree/allblob/clean receipt follows publication in raw/FINAL_PUBLICATION_READBACK.json. The Goal closes only after publication/index/process verification.
