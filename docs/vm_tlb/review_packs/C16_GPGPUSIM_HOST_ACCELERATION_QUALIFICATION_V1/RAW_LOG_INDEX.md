# Raw log index

Root: `/root/share/mnt164/huangrulin/c16_ai_workload/host_acceleration_v1/qualification_runs`

- `runs16/CURRENT_0271_CONFIG1_rep{1..3}` — current authority, pinned CPU300.
- `runs16/PRISTINE_SAMEBUILD_CONFIG1_rep{1..3}` — pristine 0271, same remote build tree.
- `runs16/COMMITTED_GUARD_CONFIG1_rep{1..5}` — rejected commit with default config=1.
- `runs16/COMMITTED_HOST_FAST_V1_rep{1..5}` — rejected commit with PTX stats config=0.
- `runs16/AFFINITY_ALL_CPUS_rep{1..3}` — affinity screen.
- `runs16/TMPFS_COMPRESSED_rep{1..3}` — byte-exact tmpfs compressed-trace screen.
- `PREFIX59_ABORTED_CURRENT_BASELINE_rep1` — intentionally terminated shortness audit; not used for performance/equivalence claims.
- `raw/live_primary_proc_20260927T0250Z.txt` — committed 30-second `/proc` live sample.

Every admitted run directory contains `RUN_RECEIPT.json`, `OUTPUT_SHA256SUMS`, `host_time.txt`, `simulator.stdout`, and empty `simulator.stderr`. Receipt hashes are enumerated in `QUALIFICATION.json`.
