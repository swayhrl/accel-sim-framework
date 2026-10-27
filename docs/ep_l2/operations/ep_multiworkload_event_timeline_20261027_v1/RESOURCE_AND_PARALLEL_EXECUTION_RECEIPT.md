# Execution, concurrency, resources and retained failures

The cohort consumed11 single scientific starts;FWT was sealed unused1. All exact rows areCLOSED/SEALED, all remaining budgets0, own model claims and shared restore windows empty. No model retry/refund or extra scan was performed.

|Case|Final status|Host elapsed min|Sampled process-tree peak GiB|rc / stop|
|---|---|---:|---:|---|
|EP_MULTI_VECTOR_F_ET0_20261027_V1|ACCEPTED_TRACE_DEFINED|9.33|0.523|0 / None|
|EP_MULTI_VECTOR_F_ET1_20261027_V1|ACCEPTED_TRACE_DEFINED|9.43|0.531|0 / None|
|EP_MULTI_CONV_S_ET1_20261027_V1|ACCEPTED_TRACE_DEFINED|40.35|0.957|0 / None|
|EP_MULTI_FWT_S_ET1_20261027_V1|NOT_STARTED_SEALED|NOT_APPLICABLE|NOT_APPLICABLE|NOT_APPLICABLE|
|EP_MULTI_CFD_S_ET1_20261027_V1|ACCEPTED_TRACE_DEFINED|5.68|1.023|0 / None|
|EP_MULTI_DWT_S_ET1_20261027_V1|INVALIDATED_AFTER_C3_RESOURCE_CAP|7.78|0.719|0 / None|
|EP_MULTI_GAUSSIAN_S_ET1_20261027_V1|ACCEPTED_TRACE_DEFINED|0.56|0.363|0 / None|
|EP_MULTI_SAD_S_ET1_20261027_V1|ACCEPTED_TRACE_DEFINED|5.47|0.887|0 / None|
|EP_MULTI_SGEMM_S_ET1_20261027_V1|ACCEPTED_TRACE_DEFINED|27.92|7.855|0 / None|
|EP_MULTI_ATAX_S_ET1_20261027_V1|ACCEPTED_TRACE_DEFINED|80.75|1.559|0 / None|
|EP_MULTI_BICG_S_ET1_20261027_V1|UNACCEPTED_FORENSIC_CLOSED_NO_RETRY|14.13|0.949|-15 / RESOURCE_SNAPSHOT_UNSTABLE_30S|
|EP_MULTI_GESUMMV_S_ET1_20261027_V1|ACCEPTED_TRACE_DEFINED|107.29|1.953|0 / None|

Elapsed is the declared legacy PRE_SEAL_TO_DONE_AFTER_CLOSED_PROOFS boundary, not pure Popen model execution time. Current RSS after process exit is not peak RSS. All models had actual9GiB AS/RSS hard bounds; sampled peak is not a universal guaranteed maximum.

Observed model concurrency reached2: Conv/GES, GES/SGEMM, GES/CFD, GES/BICG and DWT/Gaussian were prepared/run in overlapping phases. Vector ET-OFF/ON formed the sequential observer NI pair, with T ON in both. The final ATAX was the sole remaining model. Engineering analysis, observer CPU controls and recovery preparation ran independently on other bounded CPU affinities. Models were launched only through the native sole-entry, using the exact frozen cohort, fresh scoped1 budget and qualified Source/input/config; no direct application ELF invocation.

Admission used measured free disk, RSS/cgroup and qualified foreign remaining commitments, shared restore pair once, no Trace local copy and no additional35GiB pool charge. Source/input/core clocks/services were not modified to accelerate completion. The actual Source/runtime pack was13,601,501 bytes before its small inventory; it and all application bulk archives live on genuine164.174 holds Source/build, hot output and bounded recovery checks.

BICG was terminated by a stale GES remaining-write estimate, not physical RAM/SSD exhaustion. GES remaining16MiB was reconciled to a source-backed160KiB upper bound after the accepted JSON had already been written; actual added capsule96KiB. Original resource module,96MiB hard result envelope,Source/spec/raw/ELF and other-owner guarantees stayed unchanged. BICG remains spent and unaccepted.

DWT actually used103,452,672B after formatted JSON; final formal acceptance is invalidated. Its raw/C3 point were retained, archived and independently recovered. Two original-file-tree engineering restores use a separately derived103,505,920B limit each,actual103,440,384B each, and do not requalify its original scientific96MiB envelope. FWT was not launched because existing diagnostic output lower bounds could not fit the frozen envelope.

Nonblocking archival metadata-lock conflicts were handled by explicitly resuming the same storage transaction, with original failures retained; no model was rerun. All accepted archives, BICG forensic closure, DWT technical-negative recovery, Source/runtime and final evidence/publication have exact SHA/restore references in RECOVERY_AND_SHA_INDEX.json and the genuine164 bundle metadata. No old Source or bulk data was deleted.
