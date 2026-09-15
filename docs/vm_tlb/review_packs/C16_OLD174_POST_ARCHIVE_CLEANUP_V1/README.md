# C16 old174 post-archive cleanup V1

Final status: `OLD174_MODEL_PAYLOAD_CLEANUP_PASS`.

This pack records the narrowly scoped cleanup following accepted archive authority `hrl/c16-old174-recovery-archive-to-164-v1` at `0012b7c7a44899d303a1bc7919eb8cd3566e083d`. The accepted model archive status table is unchanged and hashes to `d494823b53e16d8307946011384cf52fd4ff1f5d442bf1242ae875d836f27832`.

Before removal, all six canonical node164 model archives passed the fail-closed gate: six prior `PASS` entries, readable canonical directories, receipt SHA equality, no canonical `.partial`, exact current payload inventory/SHA equality with `DESTINATION_INVENTORY.tsv`, and intact old174 non-model snapshot. After removal, the same independent full SHA256 recheck again passed for all six archives.

Only the six authorized old174 revision directories under `/root/share/c16_recovery_v3/models` were deleted. The cleanup freed 72,404,849,236 regular-file bytes. The remaining `/root/share/c16_recovery_v3` tree measures 2,414,448,587 bytes (`du -sb` after deletion).

The small node109-transfer receipt snapshot was copied, not moved, through a `.partial` destination. Its 15 regular files / 35,619 bytes have exact source/destination set, size, and SHA256 equality. It is explicitly `HISTORICAL_SNAPSHOT_ONLY_NOT_PIPELINE_RUN`, not a Pipeline scientific run.

Node109 inspection was read-only. Its results are redundancy/provisioning information only; node164 canonical archive revalidation was the sole deletion authority. No GPU workload, retokenization, raw-evidence modification, or cross-model conclusion was made.

See `FINAL_CLEANUP_STATUS.tsv` for the required per-model result, `POST_DELETE_VERIFICATION.json` for gate evidence, and `SHA256SUMS` for review-pack integrity.
