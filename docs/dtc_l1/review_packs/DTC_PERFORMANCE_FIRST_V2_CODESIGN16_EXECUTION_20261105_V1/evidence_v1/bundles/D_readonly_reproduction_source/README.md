# Independent engineering-negative archive audit reproduction

This is the exact read-only D auditor used for the final16 review. It reads the existing closed INTENT/DONE/EXIT/raw files, frozen negative-only adapter source, the reviewed B archive-witness functions, every archive chunk/full stream, all native restored typed entries, and all retained original source entries. It writes only a new exclusive D output directory. It does not register, launch, restore, copy, retry or signal a simulator.

The successful original audit is `../final_engineering_negative_archive_audit_v1/MANIFEST.json`, SHA256 `36dbbca1231b4142f025cf01b823ce6fb6dde8268ace5be7add0d04182df7ffe`.

On174-new, a manual read-only reproduction may choose a new unused output name:

```sh
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1/agents/D_independent_review_v1/readonly_reproduction_source_v1/final_negative_archive_readonly_audit.py --negative-adapter-manifest-sha256 510990aa05321c7eff338137f2666631ae1a8dce2af15fb7bcebee2e1c22c3c8 --output-name MANUAL_REVIEW_UNIQUE_DIRECTORY
```

The existing original output must not be reused. A failure creates an explicit HOLD record and does not automatically retry. Required external receipts and source pins remain at their recorded174/true164 paths; no simulator raw logs or binary are copied into this source packet. The historical q.state label RUNNING is not changed by this audit and does not replace the separately verified actual result terminal.

This source packet does not approve another scientific attempt. All16 historical identities remain charged engineering negatives with performance missing.
