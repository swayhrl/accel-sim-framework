# Raw and derived data boundary

Read-only accepted input (node164):

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_20260917T101100Z/`

V2 durable output (node164):

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_reclassification_v2_20260923/`

The durable output contains the full 34,677-row V2 inventory (about 18 MiB),
complete classification summary, delta, receipt, and `SHA256SUMS`. Git contains
only the compact review derivatives and their hashes. No raw NSYS report,
SQLite database, or full inventory is copied into Git.
