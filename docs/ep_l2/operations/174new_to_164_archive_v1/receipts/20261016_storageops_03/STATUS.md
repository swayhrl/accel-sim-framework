# Legacy pack backups retained — superseded by V5

V5 authority: `011b827c6b686ff4cff0387cafc23977376698de`. Active continuation: `../20261016_storageops_04/STATUS.md`.

All 36 pack copies (12415140272 B, 11.563 GiB) finished their sequential source/stage/SSHFS hashes and source identity checks. Their archived bytes are retained without recopying. Every original pack remains **SOURCE_KEEP**; no deletion is requested or allowed by this status. **Actual Lane5 bytes released: 0**.

The old container-workspaces staging route is **not V4 compliant**. Prior hash matches do not retrospectively authorize that route or source release. The non-cooperative automatic queue advanced during the V5 switch; its last batch completed normally. No transfer is running now, and a local V5 stop gate prevents new pack scheduling. No rsync was force-killed and no transmission was restarted.

Follow only revision 04 for bridge handshake and S01/S02 priority. Git pack backup and object-recovery work are deferred. Full Git fsck timed out and partial-copy index checks reported early EOF; source-object recoverability is unknown.
