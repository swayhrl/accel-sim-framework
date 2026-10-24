# SSD duplicate retirement feasibility ? review only

The approach is feasible in principle. New copying alone cannot reclaim the shared /dev/sdf SSD; exact verified local-copy retirement and a positive measured df delta are required. No files were deleted, moved, or uploaded during this review.

Fresh SSD available 9,968,877,568B; inherited required 10,536,091,648B; shortage 567,214,080B (540.94MiB). Registry still reserves 805,306,368B for completed epoch2 and 1,073,741,824B for live SHORT3; T did not change either.

| Candidate | Measured regular-file allocation | Qualification |
|---|---:|---|
| T E057 and AD_GEMM native restore verification duplicates | 527,740,928B (503.29MiB) | 8,423 current file identities match full restore proofs; genuine164 COMMIT, manifest, archive index and restore proof hashes all match; no open candidate FDs. Originals retained. Insufficient alone. |
| Four old174 BICG/ATAX kernel trace files | 476,585,984B (454.51MiB) | Full historical Source/164 SHA and independent native restore; all current Source and remote object identities and COMMIT hashes match; 174-new compatibility paths already resolve to genuine164. Current Source FD scan empty; future Source-local use needs explicit disposition. SOURCE_KEEP still applies. |
| Combined plan A | 1,004,326,912B (957.80MiB) | About 416.86MiB projected margin over the snapshot deficit. Actual reclaim depends on filesystem allocation and intervening science growth. |
| Larger alternative: Source polybench.tgz | 17,944,014,848B (16.712GiB) | Existing genuine164 package and R13 selected recovery evidence found. Destination projected inode differs from prior proof; no fresh whole-file SHA in this review. NOT release-ready. |

Exact paths, SHA, identity, recovery references and preconditions: [EXACT_RELEASE_REVIEW.json](EXACT_RELEASE_REVIEW.json). No new data transfer is needed for plan A. The original 115-object copy queue remains RESOURCE_HOLD until all live resource gates actually pass.

The prior user Goal explicitly limits authorization to copying and recovery evidence and excludes Source release. It also prohibits deleting/moving/overwriting Source data. This user turn requests investigation, so no Source deletion authorization was inferred. Plan A needs an explicit four-file SOURCE_KEEP exception plus retirement of the two T-owned verification duplicates. No open FDs does not prove closure of future readers.

Only exact research and own task paths were inspected. No whole NAS scan, large body rehash, Source writes, model/controller/registry changes, or scientific starts. Remote evidence identifies genuine164 as admin-wcx@10.208.130.164:/home/shared at Target /root/share/mnt164; Source same-name MD127 shadow was not used. Native restored test bytes from the prior trace Goal were already cleaned, so their historical 805,928,503B were not counted again.
