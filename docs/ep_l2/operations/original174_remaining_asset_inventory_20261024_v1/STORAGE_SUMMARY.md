# ORIGINAL174_REMAINING_ASSET_READONLY_INVENTORY_V1

Finite readonly audit of positively attributable research assets; baseline trace migration `b93fc0dbac79d6f9c5ca027baa2d2e1cf371455b`. No migration or cleanup follows this report.

## Current measured inventory

Original174 native scan: **937 disjoint known research roots**, **847,506 regular-file entries**, logical **463.879 GiB (498,085,781,279 B)**, allocated regular-file blocks **465.222 GiB (499,528,515,584 B)**. Two roots are incomplete; counts are observed lower bounds. These figures are not the entire SSD or all users' data. Whole-root Git/environment pruning and the explicit unscanned scopes below remain outside the denominator.

|Endpoint|Measured roots|Regular-file entries|Logical|Allocated regular files|
|---|---:|---:|---:|---:|
|ORIGINAL174_SSD_BACKED_OVERLAY|937|847506|463.879 GiB (498,085,781,279 B)|465.222 GiB (499,528,515,584 B)|
|SHARED_MD127|10|27226|156.165 GiB (167,681,390,123 B)|156.224 GiB (167,744,528,384 B)|
|174NEW_NATIVE_OVERLAY|172|359650|13.755 GiB (14,769,669,551 B)|14.631 GiB (15,709,847,552 B)|
|SHARED_SSD_DATA|12|221|0.488 GiB (524,244,698 B)|0.489 GiB (524,849,152 B)|

Source /workspace and /tmp are SSD-backed private overlay, not native ext4 mount points. 174-new AWMA worktrees are another private overlay; /root/data is shared ext4. Source and174-new share the host SSD pool. Namespace-reported blocks cannot be blindly summed as exclusive host upper-layer physical occupancy; shared lower layers and cross-root hardlinks are not fully observable here. Shared `/root/data` entries are counted once under SHARED_SSD_DATA, despite access through both containers. MD127 rows cover only specifically referenced research data. NAS catalog bytes are not included in these local rows. Snapshot measurements are sequential, not an atomic filesystem snapshot.

`PROJECT_ENDPOINT_SUMMARY.csv` is the project/endpoint view. `FILE_TYPE_SUMMARY.csv` is the root/project/type view. `RAW_EXPERIMENT_RECORDS.csv` separates extension candidates from exact owner-frozen accepted result trees. Extensions alone cannot establish that JSON is a scientific result, or that a log/venv fixture is irreplaceable evidence.

## Archive coverage and overlapping estimates

|Measure|Observed amount|Interpretation|
|---|---:|---|
|20 exact input selectors, complete archived content retained on Source|20.963 GiB (22,509,080,576 B)|22,507,635,190 original logical bytes; all 683 Source identities still match prior complete SHA proof and 20 NAS COMMIT hashes still match. Only five selectors have complete native Target restore evidence.|
|E057 and AD_GEMM complete accepted result trees retained on Source|0.492 GiB (527,777,792 B)|22 + 8,401 files, 513,220,893 logical bytes; all current file/directory/link identities match; complete prior native Target restore PASS. Old nine sidecars reused, not added again.|
|R13 complete compressed polybench.tgz retained on Source|16.712 GiB (17,944,014,848 B)|Current dev/inode/size/mtime_ns/ctime_ns matches prior full Source SHA; prior complete 164 archive hash. Recovery closure covers 11 selected decoded data members and two markers, not a proof of every possible program in the package. Shared input KEEP.|
|C16 protected canonical six Source models with valid164 content references|19.374 GiB (20,802,158,592 B)|Current six canonical Source identities and immutable verified-receipt hashes match. Prior true164 full SHA6/6. ACTIVE_KEEP; these are not the already-retired outbound files.|
|Sum of the four **path-disjoint Source file selections** above|57.540 GiB (61,783,031,808 B)|Lower bound on Source files with archived content, **not** guaranteed recoverable/freeable bytes; all protected/restore/reader restrictions remain. Compressed versus decoded content is not claimed logically deduplicated.|
|Confirmed incomplete formal TLS P9 transaction|391,334,023 logical B missing|B0028 closed, 130 ranges / 2,505,862,788B verified; B0029–B0033 not complete, no full141-file restore. Formal transaction evidence only, not an assertion that no other NAS copy exists.|
|Potential reusable duplicate relation, exact20 input selectors|22,507,635,190 logical B|Source→164 other-copy relation. This is a subset of the retained archived amount, not another additive quantity.|
|Build/postcheck/wheelhouse container review candidates|34.401 GiB (36,937,953,280 B)|Path-disjoint within this candidate list, mixed content, upper bound only. Can overlap archived rows and protected binaries/configs. No regenerability or deletion approval inferred.|
|Within-root repeated-inode logical entries observed on Source|159,970,675 B|Only exact same dev/inode duplication; cross-root hardlinks/reflinks/compressed equivalence are not comprehensively proved. Aliases count0 duplicate payload bytes.|
|Authorized or actual source release in this audit|0 B|Readonly inventory only.|

Do **not** sum the archive, duplicate, candidate and UNKNOWN rows. The unjoined remainder is UNKNOWN, not automatically NOT_ARCHIVED. The only quantified confirmed missing amount is the formal incomplete P9 range coverage; there is no defensible global unique-unarchived physical total yet. Old C16 outbound, V3 postcheck and PolyBench closeout releases are historical, not new free space.

## Top trace assets and PolyBench

`LARGE_ASSETS_TOP30.csv` ranks30 path-disjoint trace directories/large trace packages by current regular-file allocated blocks, with project, endpoint and exact archive state. It excludes nested children already represented by a selected parent; it does not treat a NAS logical catalog size as local blocks. Top entries include shared Cutlass 1/40, native Rodinia srad/lavaMD, and the native PolyBench package.

`POLYBENCH_TRACE_INVENTORY.csv` records 28 discovered trace-directory/package variants with path-derived program/scale/version labels. Fraction/trim/full variants are distinct until trusted byte identities prove equivalence. `SOURCE_ALIAS_ENDPOINT_MAP.csv` preserves354 discovered aliases; many baseline/decoupled paths resolve to the same MD127 trace. The selected migration manifest covers only exact member subsets; extra capture files in the same directory do not inherit archive PASS.

The full17.94GB package member listing was not regenerated by reading the compressed payload. R13 recovery map explicitly covers correlation/covariance closeout11 data members +2 empty markers /14 directories. Both historical Source closeout stage directories were released previously; their66.33GB expanded bytes cannot be added to the compressed package or presented as current Source occupancy.

## Counting and trust rules

- `INVENTORY.csv` mixes disjoint measured roots, NONADDITIVE children/selectors and archive reference rows. Only rows with the same explicitly named additive group can be considered together; references with historical allocations cannot be used as current occupancy.
- `ARCHIVED_VERIFIED` denotes the stated frozen archive/restoration scope. C2P1, C2P2, M2D and R1/R1R/R2 retain historical complete content restoration evidence; native numeric metadata was verified only for subsets, and current whole-Source equivalence is not asserted.
- `NOT_ARCHIVED` is used for the known incomplete formal P9 object. `DUPLICATE_OR_REUSABLE` covers exact authority-copy relationships; aliases are relationships, not extra files. `RETENTION_REVIEW_CANDIDATE` is review only. Missing content/identity/restoration/ownership proofs remain `UNKNOWN/HOLD`.
- Allocated is `st_blocks*512` for regular files. Directory blocks, Git contents, unreadable/pruned areas and uncompleted subtrees are excluded. Sparse allocation is preserved as observed. File counts are namespace entries unless a specific exact-inode dedup field says otherwise. NAS SSHFS projected inode/owner/mode is not native164 metadata.
- No raw trace/model bytes were newly hashed. Small manifests/immutable receipts/COMMIT files were hashed where needed to bind reused evidence. Filename or size alone never proves equal content.
- Metadata reads can update access time under filesystem policy; no source data/control/probe files were written by this audit. No zero-filesystem-side-effect claim is made.


## Current filesystem capacity (separate from asset totals)

|Observer/path|Filesystem source/type|Available bytes|Total bytes|
|---|---|---:|---:|
|SOURCE /workspace|overlay overlay|10188939264|3779302981632|
|SOURCE /root/data|/dev/sdf[/huangrulin] ext4|10188939264|3779302981632|
|SOURCE /root/share|/dev/md127 ext4|37738311680|7143083376640|
|SOURCE /root/share/mnt164|/dev/md127 ext4|37738311680|7143083376640|
|TARGET /workspace|overlay overlay|10188939264|3779302981632|
|TARGET /root/data|/dev/sdf[/huangrulin] ext4|10188939264|3779302981632|
|TARGET /root/share|/dev/md127 ext4|37738311680|7143083376640|
|TARGET /root/share/mnt164|admin-wcx@10.208.130.164:/home/shared fuse.sshfs|50547441516544|168306982981632|

These are filesystem-level counters, not the measured research subset. `/workspace` overlays and `/root/data` share the SSD backing pool; Source `/root/share/mnt164` is MD127 shadow, while Target is actual remote SSHFS. Do not add repeated mount counters. Native164 physical filesystem type/device cannot be inferred from FUSE. Share below40GiB does not authorize any new payload write; this task performed metadata reads only.
