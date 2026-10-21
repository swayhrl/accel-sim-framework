# EP-L2 named-root storage: read-only metadata snapshot

Measured at **2026-10-21T17:03:05.828414+08:00** on actual hosthuangrulin-174. Allocated bytes come from `st_blocks*512`, not logical file length; per-root hardlinked inodes are deduplicated and symlinks are not followed. No raw/trace body is read. Scan scope is named EP-L2 roots only, not the entire disk or other projects. No file is removed or moved.

| Category | Path / group | Physical allocation |
|---|---|---:|
| Current mechanism application/native results | `/workspace/ep_l2_ms20261019_e_results` | **5,159,886,848B = 4.806GiB** |
| Current mechanism builds,9 directories | `/workspace/build/ep-l2-ms20261019*`, `ep-l2-ms20261020*` | **3,730,259,968B = 3.474GiB** |
| Current A/B/C preparation/shared handoffs | `/workspace/ep_l2_ms20261019_{a_common_v1,b_victim,c_ro_v1,shared}` | 0.013GiB |
| Shared coordination | `/workspace/ep_l2_ft20261016_shared` | 0.030GiB |
| **Above current local named roots** | Excludes worktrees/Git/trace inputs | **8,936,009,728B = 8.322GiB** |
| Historical potential results | `/workspace/ep_l2_potential20261017_lane5_results` | 6.382GiB |
| Historical fast-track results | `/workspace/results/ep_l2_ft20261016` | 6.614GiB, **on Share** |

The current mechanism raw/result root is genuinely on the workspace filesystem (device156), not a Share alias. **Not every path spelled /workspace is local:** historical `/workspace/results/ep_l2_ft20261016` resolves to `/root/share/workspace_migrated_20260905/results/ep_l2_ft20261016` on device2431. It has no files modified in the last48h in this snapshot. The historical potential root is local, also with zero last48h modified files. Backups or Git copies outside these roots are not inventoried and are not claimed absent.

Window48h begins2026-10-19T17:03:05.828414+08:00. Current result files modified in that window occupy4.804GiB now. For calendar10/20–10/21 beginning2026-10-20T00:00:00+08:00, they occupy4.691GiB. **mtime selects recently modified files; it does not measure exact newly allocated bytes or net two-day growth.** E's new-generation accounting includes failed/native/debug evidence as well as successful applications; result storage should not be reported as successful raw logs alone.

Filesystem availability: workspace **25.657GiB**, Share **41.171GiB**. These are different filesystems and their free space cannot be added for one build/output path. No sole cause of overall disk occupancy is inferred from EP-L2's named-root sizes. Existing central workspace policy is the explicit2026-10-20 user5GiB floor plus2GiB monitor margin, not an automatic reversion to the older48GiB condition; it remains subject to planned writes, other leases, RAM/Share and role-specific checks. D grants no build/run admission from this snapshot.

Machine-readable per-root allocated/logical sizes, filesystem device identities, modified-window totals and result-subdirectory breakdown are in `STORAGE_METADATA.json` and `STORAGE_ROOTS.csv`. Errors: 0. No historical evidence is designated deletable.
