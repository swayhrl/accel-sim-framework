from closure_local import *
import collections,io
def md(n,t):(R/n).write_text(t,encoding='utf8')
s=load(R/'CLOSURE_TOTALS_AND_NONADDITIVE_COUNTS.json');matrix=rows(R/'LARGE_TRACE_CLOSURE_MATRIX.csv');poly=rows(R/'POLYBENCH_FULL_COVERAGE.csv');raw=rows(R/'RAW_RESULTS_RESTORABILITY.csv');q=rows(R/'ARCHIVE_ACTION_QUEUE.csv')
g=lambda n:f'{n/1024**3:.3f} GiB ({n:,} B)'
six=load(R/'evidence/AWMA_SIX_MANIFEST_EXACT_DIGEST_AND_CURRENT_ARTIFACT_STAT_CLOSURE.json')['records']
sixrows='\n'.join('|'+r['run_id']+'|'+str(r['before']['size'])+'|'+r['actual_sha256']+'|'+str(r['artifact_count'])+'|0|' for r in six)
md('AWMA_C16_RECOVERY_GAP_CLOSURE.md',f'''# AWMA / C16 evidence gap closure

## Six alleged digest mismatches: resolved, no corrupt-data inference

All six exact `RUN_MANIFEST.json` files now hash to the catalog-expected SHA256. The previous audit's `catalog_crosscheck.py` tested only files at most131,072B; these six were134,010–1,780,506B and were **skipped**, not hash mismatches. Four were only slightly above the limit. The exact Root/namespace remains174-new `mnt:[4026535153]` → `admin-wcx@10.208.130.164:/home/shared` SSHFS. Original174's same-named MD127 shadow was never used.

|Run|Manifest bytes|Current exact SHA256|Artifacts stat-checked|Missing/size mismatches|
|---|---:|---|---:|---:|
{sixrows}

Read {sum(r['before']['size'] for r in six):,} small metadata bytes at server side. All14,200 declared artifacts currently exist as regular files at the declared size; each manifest identity is stable before/after. The90 prior exact manifest proofs remain reused. This closes96/96 **manifest** digest bindings, not a fresh122,592,246,070B raw payload rehash or full independent native recovery. LOCAL_CLOSE_RECEIPT file counts/manifest SHA bind the same six runs. Prior TRANSFER_ACKED is historical transfer evidence; raw payload full-current integrity/recovery qualifiers remain explicit.

No checksum algorithm or scientific identity was changed. The old audit is preserved as history; the corrected reason is `PREVIOUS_READ_BOUND_EXCLUSION`, not a new digest convention, detected corruption or repair upload.

## Q05: separate two scientific identities

`SIM_EVIDENCE_c8b4175d33f8bed7def2984489eadbdbcdfaffbfcb6a7daef33c8beb18e80959` / `SIM_RUN_92a553b0d69a9f41c5e20a8650366c53f7fed31c29c7462947d3af03c6f136f1` is **FORMAL_FIXED_WINDOW10000**, per6415d3f1 owner `SIM_EVIDENCE_RECORD.json` and `SIM_RUN_RECORD.json`. It is not the885,681-cycle natural completion. The old storage catalog's natural-completion description mixed these scopes; no accepted scientific result is altered here.

Its exact replay1 raw is still present on174-new at:

`/root/workspace/accel-sim-framework-awma-first-current-model-replay-174new-v1/docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_BASELINE_SIM_174NEW_V1/raw/replay_1/run.log`

223,499B, current full SHA `06822c9fb9d2de0208eb51fb61c82f21150f509b8320662fd935efbac283843f` equals accepted owner evidence. Exact immutable Git recovery entry exists at6415d3f1's same review-pack path. Server direct public-Git DNS was unavailable; the already-local owner worktree resolved this ordinary read problem without new access or data upload. Its exact164 raw locator remains HOLD; don't substitute the separate natural log. Replay2 has its own run/normalization evidence and is not required to equal replay1 raw hash.

The **separate natural R0** has existing owner RAW_DATA_INDEX and RUN_RECEIPTS locator:

`/home/shared/huangrulin/awma_q05_full_kernel_translation_analysis_v1/r0_natural_completion_interrupted_transport/run.log`

166,223B, current full SHA `cc11bdb051ce3b8d4207bba8e9587adbd2dda65b13421f7699986652631d83af`. Existing885,681 cycles /368,696,302 instructions /224 CTA owner scope was checked. A new ABSENT174-new native ext4 sample directory contains an independently closed/reopened byte-identical copy: `/root/data/original174_trace_evidence_closure_20261024_v1/q05_natural_r0_sample/run.log`. Status is **NATIVE_TARGET_CONTENT_SAMPLE_RESTORE_VERIFIED**, not native164 restoration or a complete project recovery. Original native numeric metadata is unavailable in this locator chain; SSHFS projected owner/mode is not substituted. Resource gate7GiB+other current reservations+2MiB and MemAvailable≥64GiB passed. Actual own native write166,223B;0Share payload writes; no receiver/controller was installed or taken over. Sample remains for audit, no Source cleanup.

V4 matrix partial runs retain PARTIAL; producer canary/109 ACK gaps retain their original scope. No new109/GPU task was started.

## Previously unexpanded legacy raw authority: existing164 content located

Canonical root: `/home/shared/huangrulin/c16_ai_workload/provenance/historical_snapshots/old174_c12_c15_simulation/`.

Existing owner46de0c35e2c26fdabd9fc691370bedf0cc5974f5 supplies NODE164_ARCHIVE_MANIFEST/RECEIPTS, exact PRIVATE_EXPORT_READY and private tree/full-file SHA closure. Current immutable READY SHA `32dff6170ccf6172c0ebac2c8af0a0131c962d1dabe7349993f510742e046c0d` and export-manifest SHA `62564e06565be02ca63bf6fc3ce36c2df2a3adc2d23c619d73885c448bc1b6d4` match.494/494 regular-file stat/size locators match the historical complete destination SHA list. Five groups preserve C12 FORMAL, C13 DIAGNOSTIC, C14 microdiagnostic, C3 provenance and PRE_FIX status separately.

Actual regular-file bytes **5,330,959,289**, whereas old source/export tree logical count5,338,159,166B includes additional namespace/link/directory accounting. Do not call15,906 or14,286 trace-link entries raw files or count them as new independent payload. Configs, raw stdout and manifest identities are preserved, not just published performance numbers. No5GB blanket reread or complete native recovery was done.

C3/M4I input-trace symlinks and historical runtime qualifications remain dependencies; a regular raw-log archive does not establish whole scientific replay. The same owner's MIGRATION_SUMMARY explicitly left M4A's shared source archive unduplicated. M4A MD127 input in Top30 therefore cannot inherit a164 copy claim. Existing shared M4C/M4B/EP-streaming-reuse copy receipts are retained as diagnostic/UNKNOWN evidence, not promoted to complete C12 F0 raw.

## C16 six models

Historical true164 six full SHA proof `ab95e0aa46c73f6297315ecbbae09de10b09ce87` remains6/6; no model content reread. Current Source canonical six and true164 paths/sizes/mtime were checked metadata-only. RAW revision `a09a35458c702b33eeacc393d103063234e8bc28`, AWQ revision `b25037543e9394b818fdfca67ab2a00ecc7dd641`. Original canonical models remain ACTIVE_KEEP. Already-retired P2/P3 outbound paths are historical, not new reclaim.

SSHFS inode projection changes do not establish content changes. Source original metadata and exact two outbound layouts remain in baseline's SIX_ROW_TRUE164_AUTHORITY_PROOF.tsv / CURRENT_RESTORE_INDEX.tsv; native metadata cannot be read off SSHFS projections. Full large native model restore was not performed. No retirement, model transfer,109 operation, supervisor edit or C16 scientific qualification change occurred.

## TLS

P9 original txid remains `574747b05622a2a0f3ef1a58c11044ee724e5e585d0edd5f0fc32937eda12e6b`; latest Target branch09a6b4e4d closes B0028/130ranges/2,505,862,788B.391,334,023B remain formally missing and full141-file/4-directory restoration is unclosed. All25 planned group COMMIT locators were read without mutation; no complete group COMMIT was found at the frozen proposed transaction roots. Planned paths and reservations are not archives. Old B0010/B0029 requests, locks, payloads and controllers were not resumed or cleaned.
''')
native_ids=[r['asset_id'] for r in load(R/'evidence/TWENTY_SELECTORS_VS_CURRENT_WHOLE_SOURCE_DIRECTORY_DIFFERENCE.json') if r['native_restore_status']=='RESTORE_VERIFIED_NATIVE_TARGET']
md('RECOVERY_ENTRY_GUIDE.md',f'''# Exact recovery entries; do not execute unqualified bulk recovery

All20 trace reference entry scripts were read back from real164. Existing script interface is:

```sh
bash /root/share/mnt164/.../FINAL_INDEX/REFERENCES/SELECTOR_ID/RESTORE.sh /chosen/ABSENT_NATIVE_RECOVERY_DIRECTORY
```

Use the complete exact path in SOURCE_TO_TRUE164_RECOVERY_MAP.json; the ellipsis here is explanatory only. RESTORE.sh resolves its own directory and invokes the existing `restore_reference.py`. It requires a new ABSENT task-native destination. Do not use current Source, compatibility paths, SSHFS or an existing destination. Resource, permission and full expected-size admission precedes future execution; this Goal did not invoke any of these20 scripts again.

Complete prior native restore5/20: {', '.join(native_ids)}. Their current Source frozen-member identities and current164 COMMIT hash bindings match. The other15 have full raw content SHA archives/direct-readable trees and valid entries; status is CONTENT_ARCHIVED_RESTORE_NOT_FULLY_TESTED, not content missing.

These entries restore only frozen members.18 roots also contain14,040 unselected Source files /277,152,797B. In particular, CFD includes14,005 extra originally named `.trace`/control files; this is not classified as disposable mapper cache or equivalent to processed `.traceg`. Original `kernelslist` and processed `kernelslist.g` order are preserved separately. A processed single-kernel selector cannot silently cover the entire raw capture.

R13 polybench.tgz: use baseline POLYBENCH_RECOVERY_MAP_R13.json and numeric sidecars at the existing R13 persistent recovery root. Whole compressed SHA `9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca`; known recovery11 selected decoded data members+2markers/14directory records.66.33GB expanded historical stages already released are not current Source occupancy and were not recreated. Do not infer every fraction/trim variant from this package.

E057 and AD_GEMM: use their exact existing RECOVERY_POINTER and RESTORE.sh in the map. Full native Target restoration, Source KEEP validation and Source/config/binary/reader references already passed in c02fbf9f; no new test was needed.

Legacy C12/C15: use `PRIVATE_EXPORT_MANIFEST.tsv` to map the five original roots to canonical164 `private_export/`, and `receipts/PRIVATE_DESTINATION_FILE_HASHES.tsv` for all494 regular-file expected SHA/size rows. Restore into an ABSENT native directory only, checking each full byte hash after close/reopen. Symlink targets, raw-input dependency closure, original numeric metadata and old runtime remain separate gates. A raw-log-byte restore must not be advertised as a qualified native full scientific replay.

C16: use existing SIX_ROW_TRUE164_AUTHORITY_PROOF and CURRENT_RESTORE_INDEX; canonical Source originals stay ACTIVE_KEEP, two already-retired outbound layouts are distinct metadata specifications. This Goal neither writes a large restore nor authorizes retirement.

Q05 natural-log sample actual native path/SHA is in the map and audit JSON. The fixed10000 SIM_EVIDENCE_c8 raw is a different223,499B object with an exact local/Git entry; its164 locator remains unresolved. No substitution is allowed.
''')
counter=collections.Counter(r['status'] for r in matrix);pc=collections.Counter(r['status'] for r in poly)
md('FINAL_STATUS_AND_RECEIPT.md',f'''# ORIGINAL174_LARGE_TRACE_AND_RESEARCH_EVIDENCE_CLOSURE_V1

Status: FINITE_EVIDENCE_CLOSURE_COMPLETE_WITH_EXPLICIT_COPY_AUTHORIZATION_AND_RECOVERY_HOLDS. Baseline6a1a86ce3626bcd89274af071c4f4c5064ad607d, previous exact trace migrationb93fc0dbac79d6f9c5ca027baa2d2e1cf371455b. Independent branch `hrl/ops-original174-large-trace-evidence-closure-20261024-v1`.

## Mandatory completion and scope

Processed all30 Top30 and all28 PolyBench variants,51 unique required root representations. Together with existing exact20 scopes,65 exact roots were investigated. No new whole-disk/NAS scan: exact member traversal25,088entries; targeted catalog/provenance metadata only. Required roots' unique dev/inode regular-file representations:10,378 files /{g(s['mandatory_representation_disjoint_regular_file_bytes'])}; this is not content-unique bytes across compressed and expanded representations and not reclaimable space.

All65 rows have separate content, restoration and scientific-acceptance fields. Combined matrix status counts: `{dict(counter)}`; mandatory PolyBench28: `{dict(pc)}`. COMPLETE_METADATA means traversal/file presence, never body semantics, capture completeness or new runtime scientific qualification. Five input roots have empty/missing processed members, and non-R13 packages lack trusted current member/integrity bindings; precise HOLDs are retained.

## What can be reused and recovered now

-20 exact frozen selectors,683 files /{g(s['exact20_reused_content_bytes'])}, reuse full prior Source/164 SHA plus current Source exact identity and164 COMMIT hashes.20 recovery entries still exist and were read back.5 full native Target restore scopes ({s['exact20_complete_native_restore_bytes']:,}B) remain PASS;15 are CONTENT_ARCHIVED_RESTORE_NOT_FULLY_TESTED. No raw tree was falsely labeled missing because a large native restore was not repeated.
-Whole R13 polybench.tgz17,943,970,556B already archived; Source exact identity still binds prior full hash. Known recovered range is11 decoded data members+2markers, not every independent PolyBench variant.
-E057 and AD_GEMM preserve8,423 complete result files /513,220,893B with full native Target restore and owner-bounded accepted evidence. No9-sidecar retransmission or repeated application validation.
-Legacy C12/C13/C14/C3/PRE_FIX canonical164 raw/control5groups contain494 regular files /5,330,959,289B under existing historical all-file SHA receipts;494 current file sizes/presence match. Full native and external trace/runtime dependencies remain untested/HOLD. Formal/diagnostic/PRE_FIX status retained.
-AWMA six supposed mismatches are a prior128KiB metadata read-cap exclusion, resolved6/6 exact digests and14,200 artifact stat matches.96/96 manifest bindings now close; this is not a fresh114.173GiB raw checksum/recovery claim.
-Q05 natural R0's166,223B164 raw log has one new qualified native Target byte restore, full current SHA and stable Source identity. Fixed10000 `SIM_EVIDENCE_c8` is different; its223,499B local original matches accepted SHA, Git entry is exact,164 locator remains HOLD. Numeric original metadata for the new natural sample is not proven.
-C16 historical6/6 true164 content proof preserved; current canonical Source/authority metadata checked,0model bytes copied/rehashed, original canonical ACTIVE_KEEP. Old outbound retirement not repeated or counted.

## What still needs data or authorization

Existing selector scope leaves14,040 Source files /277,152,797B uncovered, including CFD original capture-like files. No `.trace` to `.traceg` or raw/full/fraction/trim equivalence is inferred. Top30/P1 objects without corresponding complete164 content proof are REQUIRES_COPY_AUTHORIZATION/REQUIRES_ARCHIVE_ACTION; no percentage was forced upward.

`ARCHIVE_ACTION_QUEUE.csv` plus51 exact metadata action manifests covers24,378 unique file identities /{g(s['copy_plan_representation_disjoint_file_bytes'])} of representation-disjoint new-copy candidates, including supplemental directory differences. This excludes already archived exact member bytes and does not add a parent and child twice. It is a future **metadata-ready plan**, not a data freeze or transfer admission: source full SHA/writer/current+planned reader checks, scientific identity qualifiers, independent copy authorization and fresh resource gates remain mandatory. The separate package/input HOLD rows are not silently included in this ready total. Source bytes compressed-vs-expanded semantic overlap is unknown and not advertised as deduplicated original content.

Planned raw range chunks≤128MiB, staging≤256MiB, single sender/receiver and total≤30MiB/s. No compression savings assumed. Remote peak budgets explicitly reserve raw tree+retained raw chunks, per-file metadata/control and staging; a tar carrier needs padded/PAX accounting. Current Share is below40GiB; this audit's zeroShare-write reads/small native sample do not authorize a future transfer waiver. New proposed164 namespace is confirmed ABSENT and was not created. Native full restores that exceed qualified scratch remain HOLD.

TLS P9 remains formal partial130ranges/2,505,862,788B, missing391,334,023B, no full141-file/4-dir restore;25 group COMMIT locators were checked, no new whole group accepted. Old transaction/txid/locks/controllers/payload cleanup were not resumed.

P2 Source original44 preserves41 executed raw roots plus3 no-raw admission HOLD;22 SG3 roots are separate independent scientific cohorts.63 exact roots currently total222,915,898 regular-file bytes. They have no trusted complete164 result join in reviewed indexes; input preservation does not imply output archival. This is a proof gap, not a global NAS-absence assertion. Other AG/AE/FAST64 containers have explicit mixed-container/owner scope gaps, not invented accepted raw counts.

## Operations and publication

New archival transfer0B; Source deleted/moved/overwritten/cleared0; Source release0B; scientific starts/stops/retries/budget/controller/accepted edits0. Old originals, models, traces and histories KEEP. Only own audit reports and the allowed166,223B ABSENT native recovery sample were written. No second receiver/daemon, no109 task, no old Goal restart.

Current server identity/IO/RAM/disk/pid-start_ticks snapshots, receiver-free read boundaries and tiny restore resource admission are in RESOURCE_AND_ACTIVE_SCIENCE_AUDIT.json. IO briefly exceeded10 before an early metadata phase; no large content pass was launched or forced through contention. Native AEFAIR model PID observations are live snapshots, not reused old IDs or a claim of owner acceptance. Old EP57, each separate DTC cohort budget, T0 and all adverse evidence retain their original meaning.

All eight requested deliverables and per-project deduplicated views are included. Exact content commit, report SHA and GitHub readback receipt are separate publication artifacts to avoid self-referential hashes. No automatic migration, cleanup or Source release follows this Goal.
''')
print('closure documentation written')
