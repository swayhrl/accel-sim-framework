# AWMA R101 Fixed NS Intermediate Lifecycle V1

Stage: `AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1` on node109 RTX4080/SM89. Execution branch: `hrl/awma-r101-fixed-ns-intermediate-lifecycle-v1`, based on exact handoff `4d6df5774f1a9a7e59a9e8eec034e7371d6eff7e`.

Final state: **`R101_INTERMEDIATE_RETENTION_READY_FOR_ARCH_REVIEW_V1`**. See `R101_DECISION.md` for evidence and limitations. This is not a hardware design, training-quality result, or cross-tile algorithm comparison.

The compact files here are the review authority. Large gradient/tile tensors, numerical outputs, NSYS/SQLite, NCU reports, source checkout, and excluded attempts live under the node164 durable root `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_fixed_ns_intermediate_lifecycle_20260927/`. `RAW_DATA_INDEX.tsv` and `SHA256SUMS` identify the published payloads. The isolated runtime and JIT caches remain local node109; their exact configuration/source hashes are in the receipts. No new model was downloaded.

Formal timing used one canary, two warmups and seven repetitions per arm, GPU events for primary medians, with profilers in separate runs. GPU operations held `/data/c16/locks/c16_gpu_campaign.lock`. The holdout was pre-registered before its gradient and timing. NCU was limited to K128 and L512 after the discovery gate. Only source- and contract-preserving engineering corrections were made; excluded attempts are listed in `R101_DECISION.md`.

Manifest interpretation: `LARGE_TILE_ACCOUNTING.tsv` separates logical/allocated/source-derived bytes from NCU-reported DRAM/L2. NCU metric units are decimal Mbyte. The author reuses intermediate buffers. `OPERATOR_TIMING.tsv` and `HOLDOUT_RESULTS.tsv` retain all formal observations, not only medians. Distinct tile sizes are distinct maps.
