# SSD reclaim opportunities — non-ImageLab only

Current verified **READY** set: **0 GiB**. No unlink is authorized in this Goal. The numbers below are disjoint, conditional **physical block estimates**, not realized `df` gains. They exclude ImageLab, already retired OLMoE/Llama/LTX, parent/child double counting, R27 B0 raw tensors and E1 original Trace. Source root was 94% used with 54.08 GiB available at the scoped V2 snapshot. All candidate files are on the same ext4 device; no separate `/data` capacity pool exists.

| Option | Incremental literal assets | Incremental estimate | Cumulative estimate | Main remaining gates |
| --- | --- | ---: | ---: | --- |
| **A — fast low-risk** | StageA 24 exact files (8.27 GiB) + three AWMA pip HTTP cache trees (8.49 GiB) | 16.76 GiB | 16.76 GiB | StageA owner must resolve partial qualification; cache rebuild/offline dependency and reader checks |
| **B — medium** | A plus three R27 `COMMON_POST_BOOTSTRAP.pt` duplicate local inodes, restoring from R26 canonical checkpoint | 7.34 GiB | 24.10 GiB | Current source/true164 SHA, parent mapping restore and AWMA owner lineage approval |
| **C — largest reasonable** | B plus Qwen3-30B 26-file revision (56.89 GiB), R26 ten canonical checkpoint files (24.46 GiB), and R27r2 `B1_C1_K2.pt` (2.45 GiB) | 83.80 GiB | 107.90 GiB | Independent C16/AWMA owner approval, current archive/readback and restore proof; preserve scientific result lineage |

The options are nested, and every source object appears in only one increment. A contains 8881737728 B StageA unique file blocks plus 9119387648 B cache `du` blocks (directory blocks included); the cache's regular single-link files alone account for 9112039424 B. StageA planned amount is file blocks, not its overlapping parent directory `du`. B adds 7880097792 B from three independent nlink=1 inodes. C adds 89977974784 B. Actual `df` increase may differ because of directory metadata, ongoing writes, or open-deleted files.

**Current decision:** StageA archive proof is closed, but its reader/owner gate is not. Cache rebuild proof is open. AWMA and Qwen scientific gates remain open. A/B/C are review plans, not cleanup approvals. If the gates cannot be closed, the realized eligible amount remains zero. The exact 24 StageA file identities and proposed directory cache scopes are in `NEXT_EXACT_RETIREMENT_WHITELIST.csv`; every row is HOLD and requires a new explicit approval and pre-delete recheck. The C16 raw Trace, accepted results, R27 B0 raw tensors, ImageLab and active RTX suite do not enter any option.
