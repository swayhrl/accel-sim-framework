# V5: SOURCE_PROBE_PASS_TARGET_REMOVED_AWAIT_SOURCE_READY

Snapshot: 2026-10-16T13:34:02.134996+00:00. Authority `011b827c6b686ff4cff0387cafc23977376698de`, fully read together with V3/V4. Original Goal and execution branch continue; no Goal or transfer task was restarted.

The compliant bridge is `/root/share/host174_storage_recovery_bridge/20261016_storageops_02`. A unique 8-byte nonce was fsynced, closed and reopened by 174-new. Its READY marker was published atomically. Exact source-side verification inputs are in BRIDGE_PROBE_READY.json:

- Path: `/root/share/host174_storage_recovery_bridge/20261016_storageops_02/probe_b8a12d08e13eaca9.bin`
- SHA256: `1187c2af8eebc05b94a363c1f1d5fabf5d1775e6bb5eaf31264b031614ca08d3`
- Device/inode: `2431/103546883`; size `8` bytes.
- READY marker: `/root/share/host174_storage_recovery_bridge/20261016_storageops_02/probe_b8a12d08e13eaca9.READY.json`.
- Share free at creation: `47725842432` B, above the 40 GiB floor.

The independent old174 source Ops window must read/hash/stat this exact file and publish its own PASS receipt on `swayhrl/gpu-l2-cache-verilog`, branch `hrl/ops-174-source-audit-exec-v1`. Target Ops has not substituted its own old174 read for that independent acknowledgment. Probe remains available until PASS, then its creator cleans it and both sides confirm absence.

**Priorities:** S01 (52 .vvp, 418020580 B), then S02 (50 .vvp, 403579225 B), each only after source exact manifest/hash, conforming bridge READY and resource checks. Target publishes DEST_VERIFIED after complete SSHFS close/reopen hashing; source Ops alone assesses/executes exact eligible source release. No second source copier/deleter is started by this target window.

**Git packs:** 36 archived copies / 12415140272 B retained. All original packs **SOURCE_KEEP**. The prior staging path is acknowledged noncompliant with V4 and is forbidden for new data. The existing non-cooperative queue advanced during switch-over before its final batch ended; all transfers now ended normally and the V5 scheduling gate is installed. These backups are not retrospectively V4 compliant and are not proof of released space.

**Actual source bytes released: 0.** Last real source free measurement `40513581056` B remains below the 48 GiB floor plus 2 GiB growth. No scientific task was stopped or restarted. No build admission is implied by copying archives.

Update: independently published source nonce PASS at `a279d7d2ac23db0c59c39031736e6618e2787fe6` matches all fields. Creator removed the nonce and its READY marker at 2026-10-16T13:40:00.358900+00:00. Source must confirm its own absence and publish conforming S01/S02 READY. Exact frozen 102-file inventory is included as SOURCE_VVP_MANIFEST.csv with SHA256 d34a952f7dfa5fcd0a2a965fc82623a6ff5fb9666f007b7626269e295a8505d7. No source transfer/deletion is performed by this target window.
