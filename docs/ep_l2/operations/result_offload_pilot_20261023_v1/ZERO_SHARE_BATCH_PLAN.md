# Zero-Share alternative using the capacity just recovered

Status: AWAIT_EXPLICIT_SCOPE_APPROVAL. No new native scratch or archive root was created. The original40GiB Share failure is not silently waived.

The user recovered capacity on the shared SSD backing original174 /workspace and174-new /root/data. Targeted cross-container statvfs now reports11,332,714,496B available on that pool; Share is a distinct md127 filesystem with40,930,123,776B available at the follow-up check. The existing genuine164 mount remains the persistent archive target.

Use a new native ext4 /root/data/result_offload_pilot_20261023_v1 for synthetic input, bounded stages, fault evidence, controls and ABSENT restore, capped16MiB. Real projects get separate new /root/data/result_offload_real_sidecars_20261023_v1/<project> roots, each capped2MiB. No task files are written on md127 Share; the old lock is opened read-only and flocked. Genuine164 writes cross into fuse.sshfs device39 and must never fall back to md127 if the mount disappears.

This keeps original synthetic4files1314816B3directories, NAS8MiB cap and exact9 owner-frozen sidecars199357B. Native Target ext4 restore remains fully independent with full byte/numeric metadata checks. Candidate real txids and NAS targets do not change. No old payload exists to retransmit. All Source originals remain KEEP. No new science scheduler/receiver or environment takeover is created.

Current data volume needs no smaller batch: execute the synthetic cases continuously, then EP and DTC serially under one existing storage slot. Later separately authorized large frozen results can use64-128MiB raw chunks under the original256MiB stage/30MiB/s ceilings; do not enlarge this pilot payload or budgets.

The draft minimal driver variant preserves V9 primitives and changes only the scratch location, exact original lock path and scoped zero-Share admission gate. A real bootstrap must verify a new explicit user approval for ZERO_SHARE_SCOPE_AMENDMENT.json before invoking it; the existing frozen Share-root approval alone is insufficient. Original data/metadata, other projects and their Share floors remain unchanged.
