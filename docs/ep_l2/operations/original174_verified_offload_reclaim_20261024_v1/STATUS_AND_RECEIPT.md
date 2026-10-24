# Verified offload and SSD reclaim ? recovery ready

Read-only recovery on 2026-10-25: 9 committed, 106 pending (106 historical HOLD), no live driver. Verified committed unique content is 95,297,328,530 bytes across 676 regular files. The original driver finished its pass at 2026-10-24 20:37:29 +08:00 after a registry parser exception affected the remaining assets.

`CURRENT_RECOVERY_STATUS.md` and `.json` record both endpoint namespaces, exact resources, ownership, retirement closure and the single resumable atomic_add_bw transaction. Its 1 GiB durable ranges and 79,691,776-byte owned partial remain intact. All 9 existing committed control hash chains and source EOF SHA proofs passed readback; no committed payload was retransmitted.

Both independent resource admissions PASS at this snapshot: shared SSD available 22,095,417,344 bytes, required 10,536,091,648 bytes; Share uses zero payload staging; genuine164 is accessed only through the 174-new SSHFS mount. All original reservations and floors remain unchanged.

Prior exact retirements remain complete and are not repeated: 8,423 T-owned recovery-test files, four Source BICG/ATAX files and the cold polybench package. Historical measured operation-interval pool gains remain 18,936,295,424 bytes; Source unlink interval gains remain 18,420,580,352 bytes. Archive volume and physical reclaim are counted separately. No new Source deletion or scientific action occurred during recovery.

Safe continuation uses the same frozen 115 scopes, original task IDs, manifests, range checkpoints and global locks. The parser will fail closed for unsupported RUNNING science schemas, and common admission failures will stop the pass without another cascade of per-asset holds. This is an active recovery snapshot, not a whole-Goal completion claim. Full native restore for large archived inputs remains NOT_PERFORMED_EXCEEDS_BOUND; original metadata and recovery scripts remain on genuine164.
