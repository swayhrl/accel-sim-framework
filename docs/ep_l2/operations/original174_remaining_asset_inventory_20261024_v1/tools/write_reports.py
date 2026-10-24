from audit_local import *
from build_inventory import load,batches
def md(n,s):(R/n).write_text(s,encoding='utf8')
s=load('CALCULATED_TOTALS_AND_NONADDITIVE_ESTIMATES.json')
g=lambda n:f'{n/2**30:.3f} GiB ({n:,} B)'
heads=(P/'REMOTE_HEADS.tsv').read_text().splitlines();wanted=['ep-l2-main-native-174new','dtc-main-native-onboarding','ops-174new-c16-model-authority','ops-c16-storage-audit','old174-global-cold-census','awma-174-local-storage','awma-174-node164']
save('evidence/FROZEN_GITHUB_RESEARCH_HEADS_AT_AUDIT_START.json',[dict(commit=l.split()[0],ref=l.split()[1]) for l in heads if any(k in l for k in wanted)])
endpoints=list(csv.DictReader((R/'ENDPOINT_SUMMARY.csv').open(encoding='utf8')))
table='\n'.join('|'+str(r['endpoint'])+'|'+r['roots']+'|'+r['files']+'|'+g(int(r['logical_bytes']))+'|'+g(int(r['allocated_bytes']))+'|' for r in endpoints)
dedup=sum(r.get('logical',0)-r.get('unique_inode_logical',0) for r in batches('SOURCE_METADATA_BATCH_*.json'))
md('STORAGE_SUMMARY.md',f'''# ORIGINAL174_REMAINING_ASSET_READONLY_INVENTORY_V1

Finite readonly audit of positively attributable research assets; baseline trace migration `b93fc0dbac79d6f9c5ca027baa2d2e1cf371455b`. No migration or cleanup follows this report.

## Current measured inventory

Original174 native scan: **{s['source_roots']} disjoint known research roots**, **{s['source_files']:,} regular-file entries**, logical **{g(s['source_logical'])}**, allocated regular-file blocks **{g(s['source_allocated'])}**. Two roots are incomplete; counts are observed lower bounds. These figures are not the entire SSD or all users' data. Whole-root Git/environment pruning and the explicit unscanned scopes below remain outside the denominator.

|Endpoint|Measured roots|Regular-file entries|Logical|Allocated regular files|
|---|---:|---:|---:|---:|
{table}

Source /workspace and /tmp are SSD-backed private overlay, not native ext4 mount points. 174-new AWMA worktrees are another private overlay; /root/data is shared ext4. Source and174-new share the host SSD pool. Namespace-reported blocks cannot be blindly summed as exclusive host upper-layer physical occupancy; shared lower layers and cross-root hardlinks are not fully observable here. Shared `/root/data` entries are counted once under SHARED_SSD_DATA, despite access through both containers. MD127 rows cover only specifically referenced research data. NAS catalog bytes are not included in these local rows. Snapshot measurements are sequential, not an atomic filesystem snapshot.

`PROJECT_ENDPOINT_SUMMARY.csv` is the project/endpoint view. `FILE_TYPE_SUMMARY.csv` is the root/project/type view. `RAW_EXPERIMENT_RECORDS.csv` separates extension candidates from exact owner-frozen accepted result trees. Extensions alone cannot establish that JSON is a scientific result, or that a log/venv fixture is irreplaceable evidence.

## Archive coverage and overlapping estimates

|Measure|Observed amount|Interpretation|
|---|---:|---|
|20 exact input selectors, complete archived content retained on Source|{g(s['source_archived_trace_allocated'])}|22,507,635,190 original logical bytes; all 683 Source identities still match prior complete SHA proof and 20 NAS COMMIT hashes still match. Only five selectors have complete native Target restore evidence.|
|E057 and AD_GEMM complete accepted result trees retained on Source|{g(s['source_archived_full_result_allocated'])}|22 + 8,401 files, 513,220,893 logical bytes; all current file/directory/link identities match; complete prior native Target restore PASS. Old nine sidecars reused, not added again.|
|R13 complete compressed polybench.tgz retained on Source|{g(s['source_archived_polybench_tgz_allocated'])}|Current dev/inode/size/mtime_ns/ctime_ns matches prior full Source SHA; prior complete 164 archive hash. Recovery closure covers 11 selected decoded data members and two markers, not a proof of every possible program in the package. Shared input KEEP.|
|C16 protected canonical six Source models with valid164 content references|{g(s['protected_canonical_models_allocated_bytes'])}|Current six canonical Source identities and immutable verified-receipt hashes match. Prior true164 full SHA6/6. ACTIVE_KEEP; these are not the already-retired outbound files.|
|Sum of the four **path-disjoint Source file selections** above|{g(s['known_source_path_disjoint_archived_content_allocated_lower_bound'])}|Lower bound on Source files with archived content, **not** guaranteed recoverable/freeable bytes; all protected/restore/reader restrictions remain. Compressed versus decoded content is not claimed logically deduplicated.|
|Confirmed incomplete formal TLS P9 transaction|{s['known_missing_formal_archive_bytes']:,} logical B missing|B0028 closed, 130 ranges / 2,505,862,788B verified; B0029–B0033 not complete, no full141-file restore. Formal transaction evidence only, not an assertion that no other NAS copy exists.|
|Potential reusable duplicate relation, exact20 input selectors|{s['potential_duplicate_trace_content_bytes']:,} logical B|Source→164 other-copy relation. This is a subset of the retained archived amount, not another additive quantity.|
|Build/postcheck/wheelhouse container review candidates|{g(s['retention_review_container_allocated_upper_bound'])}|Path-disjoint within this candidate list, mixed content, upper bound only. Can overlap archived rows and protected binaries/configs. No regenerability or deletion approval inferred.|
|Within-root repeated-inode logical entries observed on Source|{dedup:,} B|Only exact same dev/inode duplication; cross-root hardlinks/reflinks/compressed equivalence are not comprehensively proved. Aliases count0 duplicate payload bytes.|
|Authorized or actual source release in this audit|0 B|Readonly inventory only.|

Do **not** sum the archive, duplicate, candidate and UNKNOWN rows. The unjoined remainder is UNKNOWN, not automatically NOT_ARCHIVED. The only quantified confirmed missing amount is the formal incomplete P9 range coverage; there is no defensible global unique-unarchived physical total yet. Old C16 outbound, V3 postcheck and PolyBench closeout releases are historical, not new free space.

## Top trace assets and PolyBench

`LARGE_ASSETS_TOP30.csv` ranks30 path-disjoint trace directories/large trace packages by current regular-file allocated blocks, with project, endpoint and exact archive state. It excludes nested children already represented by a selected parent; it does not treat a NAS logical catalog size as local blocks. Top entries include shared Cutlass 1/40, native Rodinia srad/lavaMD, and the native PolyBench package.

`POLYBENCH_TRACE_INVENTORY.csv` records {s['polybench_rows']} discovered trace-directory/package variants with path-derived program/scale/version labels. Fraction/trim/full variants are distinct until trusted byte identities prove equivalence. `SOURCE_ALIAS_ENDPOINT_MAP.csv` preserves354 discovered aliases; many baseline/decoupled paths resolve to the same MD127 trace. The selected migration manifest covers only exact member subsets; extra capture files in the same directory do not inherit archive PASS.

The full17.94GB package member listing was not regenerated by reading the compressed payload. R13 recovery map explicitly covers correlation/covariance closeout11 data members +2 empty markers /14 directories. Both historical Source closeout stage directories were released previously; their66.33GB expanded bytes cannot be added to the compressed package or presented as current Source occupancy.

## Counting and trust rules

- `INVENTORY.csv` mixes disjoint measured roots, NONADDITIVE children/selectors and archive reference rows. Only rows with the same explicitly named additive group can be considered together; references with historical allocations cannot be used as current occupancy.
- `ARCHIVED_VERIFIED` denotes the stated frozen archive/restoration scope. C2P1, C2P2, M2D and R1/R1R/R2 retain historical complete content restoration evidence; native numeric metadata was verified only for subsets, and current whole-Source equivalence is not asserted.
- `NOT_ARCHIVED` is used for the known incomplete formal P9 object. `DUPLICATE_OR_REUSABLE` covers exact authority-copy relationships; aliases are relationships, not extra files. `RETENTION_REVIEW_CANDIDATE` is review only. Missing content/identity/restoration/ownership proofs remain `UNKNOWN/HOLD`.
- Allocated is `st_blocks*512` for regular files. Directory blocks, Git contents, unreadable/pruned areas and uncompleted subtrees are excluded. Sparse allocation is preserved as observed. File counts are namespace entries unless a specific exact-inode dedup field says otherwise. NAS SSHFS projected inode/owner/mode is not native164 metadata.
- No raw trace/model bytes were newly hashed. Small manifests/immutable receipts/COMMIT files were hashed where needed to bind reused evidence. Filename or size alone never proves equal content.
- Metadata reads can update access time under filesystem policy; no source data/control/probe files were written by this audit. No zero-filesystem-side-effect claim is made.
''')
md('AWMA_C16_ASSET_AUDIT.md',f'''# AWMA / C16 authority and unique-data audit

True164 is174-new namespace `mnt:[4026535153]`, existing SSHFS `admin-wcx@10.208.130.164:/home/shared`. Original174 namespace `mnt:[4026534768]` sees a local MD127 shadow at the same name; that path was not used for remote evidence. Native164 command access and underlying native164 block device remain unobserved. No new credentials or109 access were requested.

The official AWMA storage contract explicitly retains `/home/shared/huangrulin/c16_ai_workload` as canonical durable namespace. Logical AWMA data includes NVBit/C16WARP1, simulator-native input, PTW/TLB/cycle/raw evidence, provenance and derived datasets. AWMA is not classified absent merely because it lies outside EP/DTC migration directories.

Bounded catalog inspection read594 small metadata/index files (2,560,059 bytes of content), with explicit1200-entry/depth limit. It found **96 scoped scientific run catalog entries**, declared **{g(s['nas_declared_logical'])}**;96 referenced raw roots currently exist. Ninety small RUN_MANIFEST file hashes equal their catalog raw_manifest digest. Six do not have that exact file-digest match; the audit does not infer corruption because catalog digest conventions may differ. No raw payload was rehashed and no blanket independent restoration claim follows from TRANSFER_ACKED. Two test-fixture entries named `a`/`b` fail scoped identity qualification and are excluded from asset totals.

`references/AWMA_EXISTING_STORAGE_CATALOG.tsv` also establishes109 producer/working-copy references, a durable Q05 trace and NSYS census, plus a **Q05 accepted SIM_EVIDENCE logical identity whose durable path was not rediscovered by its prior bounded audit**. That is a specific recovery-locator HOLD. Existing snapshot SIM_RUNS/INPUTS/BASELINES/EVIDENCE documents are foundation S0 metadata, not current full closure. The V4 node164 mount recovery receipt records qualification-log completion but six matrix runs PARTIAL without terminal/coverage markers; these cannot be upgraded to complete results.

Current original174 `/workspace/c16_assets` still occupies32,267,386,880 regular-file allocated bytes and includes canonical models, software environments/wheels, receipts and partial-download evidence. Original C16/legacy VM worktrees also retain raw/result/build records. Unless joined by a trusted exact manifest, they remain UNKNOWN regarding complete archival, **not** proved Source-only or proved disposable. Suspected PTW/TLB, producer/consumer and capture records are recovery-priority owner review assets. Immutability/irreproducibility is not inferred from a suffix.

C16 six distinct RAW/AWQ contents are fully proved by `ab95e0aa46c73f6297315ecbbae09de10b09ce87`: RAW1–3 full-SHA reused, RAW4/AWQ1/AWQ2 full-SHA completed20 October, total6/6 matched historical hashes. Current164 paths/sizes/mtime still match, but all six SSHFS projected inode numbers changed since then. This is recorded as projected-identity continuity uncertainty; no new full hash and no fabricated native164 metadata PASS.

Current original **canonical** six models have exact dev/inode/size/mtime_ns/ctime_ns match to prior Source receipts; all six immutable verification-receipt SHA match. They occupy **{g(s['protected_canonical_models_allocated_bytes'])}** and remain ACTIVE_KEEP. Their exact SHA corresponds to true164 six-authority proof. Previously authorized **outbound P2/P3 six paths** are now absent; C16 retirement branch `735f8efe5df19017918fd5376357cb1e46e86190` closes their historical20,802,134,016B two-window df recovery. Never report that as new audit recovery or retire the original canonical files.

Both original outbound layouts and164 authority paths, revisions, SHA, original numeric restore metadata and recovery scripts are retained in `references/SIX_ROW_TRUE164_AUTHORITY_PROOF.tsv` and `references/CURRENT_RESTORE_INDEX.tsv`. RAW revision `a09a35458c702b33eeacc393d103063234e8bc28`, AWQ revision `b25037543e9394b818fdfca67ab2a00ecc7dd641`. Independent full model restoration was not performed.109/PC copies are provenance/catalog evidence only; live presence there was not independently probed.

No artifact is declared the only irreproducible Source copy without owner exclusivity/complete-copy evidence. Specific evidence gaps are listed in UNKNOWN_AND_HOLDS.md; no model/capture migration or deletion is authorized by this report.
''')
targetremain=load('evidence/TARGET_AWMA_SCAN_REMAINDER.json')
incomplete=[]
for pattern in ['SOURCE_METADATA_BATCH_*.json','TARGET_AWMA_METADATA_BATCH_*.json']:
 incomplete += [dict(path=r['path'],status=r['status'],entries=r.get('entries')) for r in batches(pattern) if r['status'].startswith('INCOMPLETE')]
save('evidence/EXACT_INCOMPLETE_AND_UNSCANNED_METADATA_SCOPES.json',dict(incomplete=incomplete,target_awma_not_scanned=targetremain,excluded_historical_tmp_roots=sum(r['project']=='Other_tmp_scratch' for r in __import__('build_inventory').historical)))
md('UNKNOWN_AND_HOLDS.md',f'''# Exact limits and remaining evidence

This finite audit is complete as a bounded, qualified inventory. It does not claim a globally complete or quiescent SSD/NAS census.

1. Source native partial metadata roots: `{s['source_partial'][0]}` and `{s['source_partial'][1]}`. Their observed blocks/counts are lower bounds. Target AWMA has additional partial roots and **{len(targetremain)} exact unvisited roots**: see `evidence/EXACT_INCOMPLETE_AND_UNSCANNED_METADATA_SCOPES.json`. Existing historical census is provenance only, not substituted as current occupancy. No repeated full-tree rescan was used to hide limits.
2. Git objects, private/environment pruning, unrelated accounts/system data and1532 historically unresolved tmp roots were not recursively audited. Deep alias discovery is bounded to35,000 entries/depth5/14s at the known EP/DTC hw_run root; actual8878 entries/354 aliases completed that frontier. No NAS-wide walk. New files outside discovered positively attributed scopes remain unknown.
3. LIVE/INCOMPLETE is conservative: current process cwd hits or changing root identities. Root mtime stability does not prove every descendant closed; metadata-only COMPLETE means traversal completed, not scientific terminal/quiescence. AEFAIR current registry is authoritative, not stale old cohort/PID snapshots.
4. Fifteen of20 trace inputs have no complete native Target restore evidence; full content archive and direct-readable tree are verified by prior SHA and current identity/COMMIT binding. Five do have complete native Target restore PASS. Extra files beside frozen selectors stay UNKNOWN. Original44 DTC cases remain41 accepted numeric scopes +3 admission HOLD per owner; model-conditioned derived Btree/Hotspot arms are distinct. Storage validation does not promote scientific status.
5. R13 polybench.tgz full archive SHA is trusted; known Source file identity still matches prior complete hash. Its11 selected decoded data members/two markers do not enumerate every possible program. Fraction/trim/full PolyBench variants and size-equivalent traces cannot inherit that package claim. No17.94GB reread was done just to produce a tar-member report.
6. TLS P9 latest original Target branch closes B0028/130ranges/2,505,862,788B;391,334,023B remain formally unarchived, no complete141-file/4-dir restore. Older B0010 metadata is historical and superseded. This audit does not resume P9, touch locks or payloads. Other24 groups can have Source-only frozen bindings/planned target paths: ONE_SHOT index flags them as planned, not archived.
7. Industrial L2 nineJSON full archive is verified, **native restoration explicitly not executed** under its final archive-only amendment. C2P1, C2P2, M2D are separate; historical all-file independent content restoration is not full native numeric metadata import. R1/R1R/R2 parent archived selectors must not be added to already-released VVP subsets.
8. AWMA96 raw roots are present and90 exact manifest digest matches; six require manifest-digest convention/receipt reconciliation. No fresh raw integrity or independent recovery proof for all96 was generated. The Q05 accepted logical SIM_EVIDENCE recovery locator is unresolved. V4 partial matrix results remain partial. Canonical164/109/PC provenance is explicitly considered, but other-node current existence is not assumed.
9. C16 existing six-authority full SHA is6/6 historically, current path/size/mtime matches; SSHFS projected inode changed6/6. Independent complete native model restore is absent. Original protected canonical Source models still exist with exact immutable receipt/identity matches; already-retired outbound six do not. No C16 workflow or retirement state is changed.
10. Source total unknown/unarchived physical bytes cannot be uniquely inferred from incomplete cross-index joins. Confirmed missing formal P9 bytes are logical ranges, not an allocated-space reclaim estimate. Potential duplicate/review candidate/archived totals overlap; no sum is a deletion or guaranteed df-gain proposal. Cross-root hardlink/reflink equality and compressed-versus-decoded equivalence outside explicit manifests remain unproved.

Next work, if separately requested: owner reconciliation of the named missing manifest/locator proofs, continued bounded metadata cursors for exact partial roots, then a distinct copy/recovery/release proposal. This audit performs none of those mutations or migrations.
''')
md('STATUS_AND_RECEIPT.md',f'''# Finite readonly inventory delivery

Goal: ORIGINAL174_REMAINING_ASSET_READONLY_INVENTORY_V1. Status: AUDIT_COMPLETE_WITH_EXPLICIT_COVERAGE_GAPS. Independent branch `hrl/ops-original174-remaining-assets-readonly-inventory-20261024-v1`; baseline `b93fc0dbac79d6f9c5ca027baa2d2e1cf371455b`.

Delivered all eight requested reports plus explicit project/type/endpoint summaries, PolyBench variants, alias map, nonadditive review-candidate table, immutable recovery references, bounded scanner and current metadata/activity evidence. {s['inventory_rows']} inventory rows, {s['archive_rows']} coverage records, top30 assets, {s['polybench_rows']} PolyBench trace/package variants. UNKNOWN/HOLD is preserved wherever complete identity, current closure, owner attribution or restoration proof is absent.

No Source/NAS asset copied, uploaded, deleted, moved, overwritten, truncated or cleaned. No probe writes, scientific starts/stops/restarts, budget changes, controller changes, NAS remount, receiver/lock mutations or native migration-tool calls. Only own local Windows audit worktree/scratch and Git metadata publication were written. Original files, archives and caches retain KEEP. New large-payload SHA bytes0; small manifest/receipt hashes only. Actual release0B; no automatic next migration/cleanup.

Current mount/activity start/end evidence and unchanged active PID/start_ticks checks are in evidence. Owner registry changes caused by independently running science are observations, never audited into older values. Native underlying164 device/pressure is unavailable; actual read route is verified SSHFS on174-new, not the old174 local shadow.

Reproducibility: scanners are finite nice19/ionice idle metadata-only SSH stdin programs; no remote files installed, no daemon, no whole filesystem/NAS recursion. Entry/time/root budgets and exact omissions are recorded. Report CSV references are read together with STORAGE_SUMMARY counting rules.

Publication: exact immutable Git content and SHA readback are recorded in GITHUB_REMOTE_READBACK.json; final remote HEAD is also confirmed separately at completion. Receipt commits never claim a circular hash of themselves.
''')
print('core reports written')
