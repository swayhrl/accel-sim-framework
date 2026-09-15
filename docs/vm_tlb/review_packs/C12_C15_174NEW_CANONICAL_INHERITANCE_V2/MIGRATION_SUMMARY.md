# Migration summary

Created:

- `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/old174_c12_c15_simulation/`
- `/root/share/mnt164/huangrulin/c16_ai_workload/derived/datasets/historical_simulation/`

Copied shared payloads under `shared_archive/root_share/`:

- `workspace_migrated_20260905/m4_batch_20260906/m4c-formal-controls-20260903T220000Z`
- `workspace_migrated_20260905/m4_batch_20260906/m4bs-formal-replay-20260903T180000Z`
- `workspace_migrated_20260905/results/ep_l2_streaming_reuse`

The 10.17-GB M4A archive-source tree was not duplicated because the old174 authority explicitly marks it as already shared and formal trace archive source; its archive hashes remain referenced in Git and the source location is preserved. Current M4I staging was not duplicated because it is modern C16 provenance.

The old174 export (`PRIVATE_EXPORT_READY.json`, five private-only scientific assets) was copied to `private_export/` preserving export-relative paths. All operations were copy-only; source trees remain intact.
