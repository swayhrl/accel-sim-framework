from exec_local import *
import collections
scope=load(R/'FROZEN_AUTHORIZED_EXECUTION_SCOPES.json');scopes=scope['scopes'];last_source=load(R/'resource/CHECK3_SOURCE.json');last_target=load(R/'resource/CHECK3_TARGET.json')
identity={}
for p in (R/'readonly').glob('*.json'):
 for a in load(p)['scopes']:identity[a['asset_id']]=a
free=last_target['filesystems']['/root/data']['available_bytes'];required=last_target['required_SSD_bytes'];deficit=last_target['SSD_deficit_bytes']
need=required-free;assert need==deficit>0
def csvout(name,rs,columns=None):
 columns=columns or list(dict.fromkeys(k for r in rs for k in r))
 with (R/name).open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,columns);w.writeheader();w.writerows(rs)
events=[];admit=[]
events.append(dict(event='GOAL_CREATED_INDEPENDENT_FINITE_EXECUTION',unix=time.time(),authority_base=BASE,new_data_copy_started=False,Source_disposition='KEEP'))
for n in ['CHECK1','CHECK2','CHECK3']:
 for end in ['SOURCE','TARGET']:
  x=load(R/f'resource/{n}_{end}.json');events.append(dict(event='RESOURCE_ADMISSION_FAIL_CLOSED',checkpoint=n,endpoint=end,unix=x['unix'],available_SSD=x['filesystems']['/root/data']['available_bytes'],required_SSD=x['required_SSD_bytes'],deficit=x['SSD_deficit_bytes'],reason='RESOURCE_HOLD_SSD_ALL_DECLARED_RESERVATIONS',sender_receiver_started=False))
for s in scopes:
 z=identity[s['asset_id']];a=dict(asset_id=s['asset_id'],kind=s['kind'],priority=s['priority'],source_root=s['source_root'],source_host=z.get('source_namespace',s['source_alias']),source_namespace=z['namespace'],source_realpath=z['source_realpath'],current_frozen_identity_state=z['status'],current_files=z['regular_files_checked'],current_identity_matching_files=z['matching_frozen_identity_files'],logical_original_bytes=s['expected_bytes'],Source_content_SHA='REUSE_AVAILABLE_PRIOR_FULL_SHA_CURRENT_IDENTITIES_MATCH' if s['kind']!='TRACE' else 'NOT_STARTED_RESOURCE_GATE_FAILED',old_frozen_manifest_reference=s['queue']['manifest_reference'] if s['queue'].get('manifest_reference') else 'Q05 accepted owner rawSHA06822c9f...',existing164_reuse_this_execution='NOT_EVALUATED_FOR_DATA_ADMISSION; NO_NEW_REUSE_RECEIPT',actual_new_payload_transferred_bytes=0,archived_content_state='NOT_ARCHIVED_IN_THIS_EXECUTION_RESOURCE_HOLD',whole_content_SHA_state='NO_NEW_DESTINATION_SHA_OR_COMMIT',recovery_entry_state='PREVIOUS_BASELINE_REFERENCES_PRESERVED; NO_NEW_ENTRY',native_restore_state='NOT_STARTED_RESOURCE_HOLD',scientific_qualification_state='FROZEN_OWNER_CONTEXT_UNCHANGED; FRESH_WRITER_READER_GATES_NOT_PASSED',Source_disposition='SOURCE_KEEP',status='RESOURCE_HOLD',hold_reason='Shared SSD does not protect all registered foreign write reservations + existing5GiB floor2GiB monitor1GiB outside-project headroom64MiB controls',SSD_available_bytes=free,SSD_required_bytes=required,SSD_deficit_bytes=deficit,planned_true164_target=s['queue']['proposed_true164_root'],target_created=False,transaction_id=None,sender_receiver_started=False,next_action='Free real backing-SSD capacity through a separately authorized owner action or obtain legitimate reservation release by its owner; then fresh complete gate/zeroShare qualification. Do not lower thresholds, clear reservations, clean Source or auto-start.')
 admit.append(a);events.append(dict(event='ASSET_FAIL_CLOSED_RESOURCE_HOLD',**a))
events.append(dict(event='FINITE_GOAL_NORMAL_END_ALL_AUTHORIZED_SCOPES_HELD',authorized_scope_count=len(scopes),archived_assets=0,new_archive_bytes=0,Source_release_bytes=0,no_auto_resume=True))
with (R/'ARCHIVE_EXECUTION_LEDGER.jsonl').open('w',encoding='utf8') as f:
 for r in events:f.write(json.dumps(r,ensure_ascii=False)+'\n')
csvout('ASSET_ADMISSION_LEDGER.csv',admit)
cols=['asset_id','source_root','original_bytes','actual_new_payload_bytes','reused_existing164_bytes','content_status','full_SHA_status','true164_bundle','recovery_entry','native_restore_status','scientific_status','Source_disposition']
csvout('FINAL_ARCHIVED_ASSETS.csv',[],cols)
csvout('REMAINING_HOLD_AND_COPY_QUEUE.csv',admit)
save('SOURCE_TO_TRUE164_RECOVERY_MAP.json',dict(schema='RESOURCE_HELD_EXECUTION_RECOVERY_MAP_V1',newly_archived_entries=[],new_transactions=[],previous_verified_recovery_map=dict(commit=BASE,path='docs/ep_l2/operations/original174_trace_evidence_closure_20261024_v1/SOURCE_TO_TRUE164_RECOVERY_MAP.json'),planned_routes_not_usable_archives=[dict(asset_id=a['asset_id'],source=a['source_root'],planned_true164=a['planned_true164_target'],target_created=False,status='RESOURCE_HOLD') for a in admit],Source_disposition='KEEP',warning='No new target/COMMIT exists. Existing historical archives are preserved; planned roots are never recovery entries.'))
save('FULL_SHA_AND_COMMIT_RECEIPTS.json',dict(new_archived_assets=0,new_complete_Source_SHA_passes=0,new_destination_SHA_passes=0,new_COMMITs=[],new_transactions=[],prior_closed_DTC_SHA_reusable_by_current_exact_identity=True,authorized_scope_current_identity_matches=sum(a['current_identity_matching_files'] for a in admit),gates_not_completed=['zeroShare current path resource qualification','fresh activity/writer/current+planned reader admission','new Source EOF SHA where absent','new receiver validation','new native restoration'],reason='RESOURCE_HOLD before source SHA/sender/receiver'))
save('NATIVE_RESTORE_VERIFICATION.json',dict(status='NOT_STARTED_RESOURCE_HOLD',actual_new_native_restored_files=0,actual_new_native_restore_bytes=0,pilot_source='smallest frozen DTC root reserved as first test after qualification',new_recovery_directories_created=False,scientific_runs_launched=0))
checks=[load(p) for p in sorted((R/'resource').glob('CHECK*.json'))]
live=load(R/'resource/CURRENT_NEW_SHORT3_ACTUAL_INTENT_PID_JOIN.json')
save('RESOURCE_AND_ACTIVE_SCIENCE_AUDIT.json',dict(schema='ARCHIVE_EXECUTION_GLOBAL_RESOURCE_FAIL_CLOSED_V1',snapshots=checks,initial_failure=load(R/'resource/INITIAL_ADMISSION_FAILURE_EXACT_VALUES.json'),current_short3_actual_PID_join=live,admission_outcome='GLOBAL_SSD_RESOURCE_HOLD',available_bytes=free,required_bytes=required,deficit_bytes=deficit,reservation_math=dict(existing_science_floor_bytes=5*1024**3,existing_monitor_reserve_bytes=2*1024**3,outside_registered_project_headroom_bytes=1024**3,own_controls_reserve_bytes=64*1024**2,COMPLETE_AEFAIR_still_registered_reserved_bytes=805306368,RUNNING_SHORT3_registered_reserved_bytes=1073741824,all_native_registered_reserved_bytes=1879048192),old_complete_reservation_not_unilaterally_ignored_or_released=True,zero_Share_path=dict(status='PREPARED_NOT_QUALIFIED_RESOURCE_GATE_FAILED',Share_new_payload_bytes=0,Source_full_temporary_copy_bytes=0,actual_probes_or_transfers=0,end_to_end_writing_probe_not_executed=True,global40GiB_Share_policy_changed=False,SSD_floor_or_headroom_changed=False,reason='Zero Share staging does not repair backing SSD capacity/reservation deficit'),actual_new_sender_count=0,actual_new_receiver_count=0,old_transaction_locks_taken_over=False,new_Source_data_writes_moves_deletes=0,source_payload_SHA_reads=0,new_scientific_starts_stops_budget_or_controller_edits=0,new_true164_target_created=False,independent_own_native_metadata_only='One inactive admission helper file under/root/data/research_asset_archive_exec_20261024_v1/tools; no Source scientific directory writes, no background receiver/daemon'))
save('ZERO_SHARE_ROUTE_QUALIFICATION.json',dict(status='NOT_QUALIFIED_RESOURCE_HOLD',preparation='Existing immutable V9 and multi-member framing reviewed; direct174-new toSource SSH host/namespace probe PASS. No old sender/receiver lock acquired.',source='huangrulin-174 mnt:[4026534768]',target='huangrulin-sshfs-174 mnt:[4026535153]',true164='admin-wcx@10.208.130.164:/home/shared fuse.sshfs',Source_same_named_mount='MD127_LOCAL_SHADOW_NOT_USED',payload_staging_design='Source read/socket ->174-new bounded memory -> genuine164 only;0MD127 payload. Requires independent real admission/test before use.',current_Share_available_bytes=last_target['filesystems']['/root/share']['available_bytes'],old40GiB_threshold_unchanged=True,Source_SSD_available_bytes=free,Source_SSD_required_bytes=required,Source_SSD_deficit_bytes=deficit,capacity_protection_failed=True,qualified=False))
summary=dict(status='NORMAL_FINITE_END_ALL_115_AUTHORIZED_ASSETS_RESOURCE_HOLD_NOT_ARCHIVE_COMPLETE',authorized_assets=115,authorized_files=25153,authorized_representation_file_bytes=199632736880,trace_roots_authorized=51,trace_file_identities=24378,trace_bytes=199409597483,DTC_roots_authorized=63,DTC_files=774,DTC_bytes=222915898,Q05_optional_bytes=223499,extra20_files=14040,extra20_bytes=277152797,extras_already_inside_trace_totals=True,new_archived_independent_assets=0,new_archived_bytes=0,new_trace_P0_P1_complete=0,trace_P0_P1_remaining=51,DTC_completed=0,DTC_remaining=63,Q05_completed=0,actual_reused_or_saved_transfer_bytes_this_execution=0,previous_known_archives_and_recovery_proofs_unchanged=True,actual_Source_release_bytes=0,available_SSD_bytes=free,required_SSD_bytes=required,SSD_deficit_bytes=deficit,current_exact_identity_matching_scopes=115,current_exact_identity_matching_files=25153)
save('FINAL_EXECUTION_COUNTS.json',summary)
poly=rows(B/'POLYBENCH_FULL_COVERAGE.csv');csvout('POLYBENCH_EXECUTION_COVERAGE.csv',[dict(source_root=r['source_root'],baseline_variant=r.get('baseline_variant'),prior_content_state=r['content_state'],prior_restore_state=r['restore_state'],new_archive_status='NO_NEW_COPY_RESOURCE_HOLD',new_transfer_bytes=0,existing_archive_unchanged=True,hold_reason='Global backing SSD admission fails; no promotion of prior selector/package scope') for r in poly])
text=f'''# ORIGINAL174_RESEARCH_ASSET_ARCHIVE_EXECUTION_V1

**Status: NORMAL_FINITE_END — ALL115 AUTHORIZED ASSETS RESOURCE_HOLD. Archiving did not start and is not complete.**

Independent branch `hrl/ops-original174-research-archive-exec-20261024-v1`. Full latest closure package9a34666c025474367b9176764d2ae67e03b22b49 was read and bound by SHA. No old Goal/transaction was restarted.

## Admission result, not an archive PASS

Required backing SSD capacity: **{required:,}B**. Last Source/Target available: **{free:,}B**. Deficit: **{deficit:,}B ({deficit/1024**2:.3f}MiB)**. Both private overlays and `/root/data` share this physical SSD pool, so changing container paths does not create space.

Calculation: existing5GiB disk floor +2GiB monitor reserve +1GiB headroom for outside registered projects +64MiB own controls +805,306,368B retained by completed DTC_AEFAIR_EPOCH2_V1 +1,073,741,824B retained by the active DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1 =10,536,091,648B. Source active old EP leases contribute0 additional bytes in the snapshots. The completed campaign's reservation is still in the authority registry; T did not ignore, clear, refund or edit it.

Three bounded Source/Target checks all fail this same capacity gate. There was no infinite polling/retry loop. A current SHORT3 actual model was joined through its new qualification ledger: cohort E2-AEF3-DWT2D-DH, PID920268/start_ticks956646449, live at its recorded timestamp. Old AEFAIR PIDs were not reused as current identity; original Source research processes remain untouched.

True164 is still174-new's `admin-wcx@10.208.130.164:/home/shared` SSHFS with about50.49TB available. Original174's same pathname is local MD127 shadow. New proposed164 archive root remains ABSENT, no NAS directory or transaction/COMMIT was created. Old archive locks were only observed through kernel metadata; no old lock or controller was taken over.

## zero-Share path

Direct174-new→old174 SSH namespace probe passes. Existing pinned V9/multi-member code and qualified small-result carrier were reviewed. An independent bounded source-read/socket→real164 route was prepared, but **is not qualified**: resource failure occurs before any payload write probe, Source checksum pass, pilot, sender or receiver.

Share payload writes0 is an actual no-transfer result, not evidence of a passed end-to-end transfer. zero-Share staging cannot offset insufficient SSD reserve protection. The old40GiB Share policy and frozen SSD/resource floors were not lowered; tmpfs or a different same-pool path was not used to pretend to create capacity.

## Finite queue processing

-115 authorized units:51 trace selections /24,378 identities /199,409,597,483B;63 DTC raw roots /774files /222,915,898B; optional Q05 fixed-window223,499B.14,040 extras /277,152,797B are already in the trace selections, never added twice.
-All115 scopes /25,153 currently selected regular-file identities match the frozen dev/inode/size/uid/gid/mode/mtime_ns/ctime_ns metadata. No Source data body read or full SHA was started. Prior DTC/Q05 full SHA remains available with exact current identity binding, but does not admit a copy without resource/writer/reader checks.
-P0/P1 new completed0, remaining51; DTC new completed0, remaining63; Q05 new completed0. All inherit the exact global resource HOLD.9 pre-existing input/package HOLD rows remain outside this execution's authorized copies.
-`FINAL_ARCHIVED_ASSETS.csv` is intentionally header-only. Per-asset fields, source identity, original size, zero wire bytes, unstarted content/SHA/native recovery, unchanged science and next action are in ASSET_ADMISSION_LEDGER.csv / REMAINING_HOLD_AND_COPY_QUEUE.csv and the append-only execution ledger.
-All earlier20 trace, R13, E057/AD_GEMM, legacy AWMA/C16 and other verified archives remain unchanged. No older proof was counted as a newly archived asset or actual saved transfer in this execution. PolyBench coverage remains its prior precise selector/package scope.

New true164 archived assets0 /bytes0. New transfers0. Native restores0. Actual Source release **0B**. Scientific starts/stops/retries/budget/T0/controller/accepted evidence changes0. No Source/model/cache/result deletion, move or overwrite. Only small own operation metadata was written; no Source scientific workspace probe or whole-disk scan.

## Smallest lawful unblock

At the last snapshot, restore at least{deficit:,}B actual backing-SSD capacity, with additional room for ongoing foreign growth, through a separately authorized action; **or** let the legitimate DTC resource owner decide under its own current contract whether the completed old campaign's805,306,368B reservation can actually be released. T does neither operation. The active SHORT31GiB remains protected. Source cleanup/deletion and reservation-field edits are not authorized by this Goal.

Even after space improves, a later continuation must freshly recheck all declared reservations, actual science PID/start_ticks and IO, exact Source identity/writers/current+planned readers, target ABSENT/same transaction, then independently qualify zero-Share via the smallest frozen DTC pilot. No assumption of automatic restart or a lower threshold follows from this report.

The Goal ends normally under the user's explicit condition that all remaining authorized objects have precise HOLD. It does **not** claim data archived or automatically start a next migration. All required reports are published in the independent branch and their exact GitHub bytes/critical receipts are read back in GITHUB_REMOTE_READBACK.json.
'''
(R/'FINAL_STATUS_AND_RECEIPT.md').write_text(text,encoding='utf8')
print(json.dumps(summary,indent=2))
