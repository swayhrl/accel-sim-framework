from audit_local import *
import collections,re,io
def load(n):return json.loads((R/n).read_text(encoding='utf8'))
def writecsv(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (R/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
def batches(pattern):
 out={}
 for p in sorted((R/'evidence').glob(pattern)):
  for r in json.loads(p.read_text(encoding='utf8'))['roots']:
   if r['status']!='BATCH_BUDGET_NOT_SCANNED':out[r['path']]=r
 return list(out.values())
historical=list(csv.DictReader((P/'SOURCE_COLD_CENSUS_ROOT_LEDGER.csv').open(encoding='utf-8-sig')))
old_by={r['source_path']:r for r in historical}
source=batches('SOURCE_METADATA_BATCH_*.json');shared=batches('SOURCE_SHARED_METADATA_BATCH_*.json')+batches('SOURCE_SHARED_TRACE_METADATA_BATCH_*.json')
target=batches('TARGET_AWMA_METADATA_BATCH_*.json');common=batches('SHARED_SSD_C16_METADATA_BATCH_*.json')
old=Path('D:/repo/ep-dtc-trace-migration-20261024-v1/docs/ep_l2/operations/174new_ep_dtc_trace_migration_20261024_v1')
traces=json.loads((old/'TRUE164_TRACE_RECOVERY_INDEX.json').read_text(encoding='utf8'))['records']
sourcechecks={r['asset_id']:r for r in load('evidence/TRACE_CURRENT_SOURCE_MEMBERS_VS_COMPLETED_SHA_IDENTITIES.json')}
naschecks={r['asset_id']:r for r in load('evidence/TRACE_TRUE164_SMALL_COMMIT_AND_MEMBER_STAT_READBACK.json')}
inv=[];coverage=[];raw=[];types=[]
def project(p,fallback='USER_RESEARCH_UNRESOLVED'):
 z=p.lower()
 if 'c16' in z:return 'C16_AI'
 if 'awma' in z or 'accel-sim-vm-' in z:return 'AWMA_VM_LEGACY'
 if any(s in z for s in ['dtc','decoupled-l1','fast64','m5-trace']):return 'DTC_L1'
 if any(s in z for s in ['ep_l2','ep-l2','gpu-l2']):return 'EP_L2'
 if 'accel-sim-decoupled-l2' in z or '/root/share/accel-sim/' in z:return 'SHARED_GPU_TRACE_EP_DTC_LEGACY'
 return fallback
proc=load('evidence/SOURCE_ENDPOINT_ACTIVITY_START.json')['processes']+load('evidence/TARGET_ENDPOINT_ACTIVITY_START.json')['processes']
def live(p):return any(r['cwd']==p or r['cwd'].startswith(p+'/') for r in proc)
root_rows=[]
for endpoint,sets in [('ORIGINAL174_SSD_BACKED_OVERLAY',source),('SHARED_MD127',shared),('174NEW_NATIVE_OVERLAY',target),('SHARED_SSD_DATA',common)]:
 for r in sets:
  p=r['path'];base=old_by.get(p,{});pr=project(p,base.get('project','USER_RESEARCH_UNRESOLVED'))
  state='LIVE/INCOMPLETE' if live(p) or r.get('root_identity_changed') else r['status']
  row=dict(asset_id=hashlib.sha256((endpoint+p).encode()).hexdigest()[:16],project=pr,endpoint=endpoint,source_path=p,scope='DISJOINT_SCAN_ROOT_REGULAR_FILES_ONLY',files=r.get('files',''),directories=r.get('dirs',''),symlinks=r.get('symlinks',''),logical_bytes=r.get('logical',''),allocated_bytes=r.get('allocated',''),inode_dedup_within_root_bytes=r.get('logical',0)-r.get('unique_inode_logical',0),measurement=state,classification='UNKNOWN/HOLD',archive_state='NOT_ESTABLISHED_FOR_WHOLE_CONTAINER',restore_state='NOT_ESTABLISHED_FOR_WHOLE_CONTAINER',overlap_parent='',additive_group=endpoint+'_ROOTS',evidence='evidence/*METADATA_BATCH*.json',scientific_role=base.get('role','PATH_ATTRIBUTED_CONTAINER'),retention='SOURCE_KEEP; NO_RELEASE_AUTHORITY',notes='No whole-tree hash; excluding Git/environment pruning; directory blocks omitted. Process cwd hit is a conservative reader/activity hint, not proof of writing. Historical project labels preserved where finer ownership unproven.')
  inv.append(row);root_rows.append(row)
  for ext,v in r.get('types',{}).items():
   t=dict(project=pr,endpoint=endpoint,source_root=p,file_type=ext,file_count=v['files'],logical_bytes=v['logical'],allocated_bytes=v['allocated'],measurement=state,necessity='OWNER_REVIEW_REQUIRED; extension alone cannot establish scientific necessity or regenerability')
   types.append(t)
   if any(k in ext for k in ['trace','log','json','csv','tsv','out','raw','ncu','nsys','parquet','ptw','tlb']):raw.append(dict(t,record_class='EXTENSION_CANDIDATE_NOT_SEMANTICALLY_CERTIFIED_RAW',additive_group='DISJOINT_ROOT_TYPE_CANDIDATES',evidence='metadata only; includes possible software test fixtures/control/config files; cannot claim all are scientific raw'))
selectors=[];filecoverage={};archived_source_alloc=0
for r in traces:
 chk=sourcechecks[r['asset_id']];nc=naschecks[r['asset_id']];m=json.loads((old/r['all_original_numeric_metadata_and_SHA']).read_text(encoding='utf8'))
 complete_restore=r['RESTORE_VERIFIED_NATIVE_TARGET']=='RESTORE_VERIFIED_NATIVE_TARGET'
 valid=chk['all_current_source_identities_match'] and nc['all_members_present_sizes_match'] and nc.get('commit_hash_matches',False)
 allocated=sum(f.get('allocated',0) for f in chk['files']);archived_source_alloc+=allocated if valid else 0
 c=dict(asset_id=r['asset_id'],project='+'.join(r['projects']),source_path=r['source_root'],scope='EXACT_FROZEN_MEMBERS_ONLY; NOT_WHOLE_DIRECTORY',logical_bytes=r['original_bytes'],allocated_bytes=allocated,files=len(m['members']),classification='ARCHIVED_VERIFIED' if valid and complete_restore else 'UNKNOWN/HOLD',archive_state='FULL_CONTENT_SHA_VERIFIED_REUSED_EXACT_SOURCE_IDENTITY' if valid else 'CURRENT_IDENTITY_HOLD',restore_state=r['RESTORE_VERIFIED_NATIVE_TARGET'],true164_path=r['true164_tree'],recovery_reference='b93fc0dbac79d6f9c5ca027baa2d2e1cf371455b:docs/ep_l2/operations/174new_ep_dtc_trace_migration_20261024_v1/'+r['all_original_numeric_metadata_and_SHA'],current_source_present=True,source_disposition='SOURCE_KEEP',overlap_relation='SUBSET_OF_NATIVE_ROOT; shared scientific aliases are one selector',proof_scope='Full prior Source/164 SHA + current full Source dev/inode/size/mtime/ctime; current NAS exact small COMMIT hash + member sizes. No new payload hash.',restore_evidence=r.get('native_restore_evidence'),additive_group='EXACT_TRACE_SELECTORS_ONLY')
 coverage.append(c);selectors.append(c)
 for f in m['members']:filecoverage[r['source_root']+'/'+f['relative_path']]=c
 inv.append(dict(c,endpoint='ORIGINAL174_SSD_BACKED_OVERLAY',measurement='CURRENT_STAT_BINDING_TO_PRIOR_FULL_SHA',retention='DUPLICATE_OR_REUSABLE_RELATION; SOURCE_KEEP; NO_DELETION',overlap_parent='CONTAINING_SCAN_ROOT',notes='Extra capture/header files in same directory are not silently included. Full native restore performed for only five of twenty selectors.'))
fullresults=[]
for s in load('evidence/EXISTING_FULL_RESULTS_CURRENT_SOURCE_IDENTITY_AUDIT.json'):
 a=s['asset'];receipt=load('references/'+a+'_RECEIPT.json');pointer=load('references/'+a+'_RECOVERY_POINTER.json')
 c=dict(asset_id=a,project='EP_L2' if a.startswith('EP') else 'DTC_L1',source_path=s['source'],scope='COMPLETE_OWNER_FROZEN_RESULT_TREE',logical_bytes=s['logical'],allocated_bytes=s['allocated'],files=s['files'],classification='ARCHIVED_VERIFIED' if s['all_identity_match'] else 'UNKNOWN/HOLD',archive_state='ARCHIVE_VERIFIED',restore_state='RESTORE_VERIFIED_NATIVE_TARGET',true164_path=receipt['true164_bundle'],recovery_reference='c02fbf9f554b6287151ae50666889ff3aac4eebc:docs/ep_l2/operations/full_result_offload_20261023_v1/results/'+a+'/RECOVERY_POINTER.json',current_source_present=True,source_disposition='SOURCE_KEEP',overlap_relation='SUBSET_OF_NATIVE_ROOT; prior nine sidecars REUSED not added',proof_scope='Prior whole-content/native restore; all current files/dirs/links exact stat binding PASS',additive_group='EXACT_RESULT_SELECTORS_ONLY')
 coverage.append(c);fullresults.append(c);inv.append(dict(c,endpoint='ORIGINAL174_SSD_BACKED_OVERLAY',measurement='CURRENT_ALL_ENTRY_STAT_MATCH',retention='SOURCE_KEEP; NO_RELEASE_AUTHORITY'))
 raw.append(dict(project=c['project'],endpoint='ORIGINAL174_SSD_BACKED_OVERLAY',source_root=s['source'],file_type='OWNER_ACCEPTED_COMPLETE_RESULT_TREE',file_count=s['files'],logical_bytes=s['logical'],allocated_bytes=s['allocated'],measurement='CURRENT_ALL_ENTRY_IDENTITIES_PASS',necessity='ACCEPTED_REPRODUCIBILITY_EVIDENCE_KEEP',record_class='OWNER_FROZEN_ACCEPTED_RESULTS',additive_group='NONADDITIVE_EXACT_OWNER_SELECTOR',evidence=c['recovery_reference']))
legacy=list(csv.DictReader((R/'references/OLD174_ALREADY_ARCHIVED_RECOVERY_OPPORTUNITIES.csv').open(encoding='utf-8-sig')))
current_legacy={r['asset_id']:r['stat'] for r in load('evidence/LEGACY_ARCHIVE_SOURCE_LOCATOR_CURRENT_STAT.json')}
poly_current=current_legacy['POLYBENCH_TGZ'];poly_proof=load('references/SOURCE_POLYBENCH_SOURCE_FINAL_HASH_R10.json');poly_frozen=poly_proof['source_identity_after_hash_ns']
poly_identity_match=all(poly_current.get(k)==int(poly_frozen[k if k!='size' else 'size_bytes']) for k in ['dev','inode','size','mtime_ns','ctime_ns'])
save('evidence/POLYBENCH_WHOLE_ARCHIVE_SOURCE_CURRENT_IDENTITY_REUSE.json',dict(current=poly_current,prior_full_SHA=poly_proof['observed_sha256'],all_identity_fields_match=poly_identity_match,new_payload_bytes_read=0,scope='whole compressed archive only; selected 11 decoded data members and two markers have R13 recovery proof, not all hypothetical package members'))
for r in legacy:
 if r['asset_id']=='P9_PUBLIC':continue
 verified_legacy=r['asset_id'] in ['C2P1','C2P2','M2D','R1','R1R','R2','M5_ARCHIVE','M5_CANONICAL_EXTRACT']
 coverage.append(dict(asset_id=r['asset_id'],project=r['project_class'],source_path=r['canonical_source_path'],logical_bytes=r['historical_logical_bytes'],allocated_bytes=r['historical_source_allocated_bytes'],files=r['historical_file_count'],classification='ARCHIVED_VERIFIED' if verified_legacy else 'UNKNOWN/HOLD',archive_state=r['content_restore_scope'],restore_state=r['numeric_native_metadata_scope'],true164_path=r['native164_archive_path'],recovery_reference=r['immutable_evidence'],current_source_present='error' not in current_legacy.get(r['asset_id'],{'error':1}),source_disposition=r['source_state'],scope='HISTORICAL_FROZEN_SELECTOR_NOT_FRESH_WHOLE_SOURCE',overlap_relation=r['overlap_parent_asset_id'],proof_scope='Historical exact all-file independent CONTENT restoration, native numeric metadata subset only; current locator only. Current Source content equivalence remains UNKNOWN. Do not equate remaining parent allocation with archived selector.',additive_group='NONADDITIVE_LEGACY_HISTORY'))
tls=load('references/TLS_P9_LATEST_EXACT_STATUS.json')['P9']
coverage.append(dict(asset_id='TLS_P9_PUBLIC_CURRENT_B0028',project='TLS',source_path='/workspace/worktrees/accel-sim-tls-cache/hw_run/tls-cache-p9-public-v1',logical_bytes=2897196811,files=141,classification='NOT_ARCHIVED',archive_state='FORMAL_TRANSACTION_INCOMPLETE_130_RANGES_2505862788B',restore_state='NO_FULL_141_FILE_4_DIR_RESTORE',true164_path='/home/shared/huangrulin/host174_storage_recovery/tls_v10/20261018_P9_PUBLIC_315c008ee1757637b4f68172f93e58c4916cda061936dc4d0125762e6aa9ba0a',missing_formal_archive_logical_bytes=tls['remaining_original_bytes'],proof_scope='Exact 09a6b4e4d current Target branch B0028 closed receipt supersedes stale B0010 review. No assertion that other unindexed NAS copies are absent.',source_disposition='SOURCE_KEEP',recovery_reference='references/TLS_P9_LATEST_EXACT_STATUS.json',additive_group='NONADDITIVE_PARTIAL_TRANSACTION'))
for r in load('references/V3_BOTH_BATCHES_RECOVERY_INDEX_20261020.json')['assets']:
 coverage.append(dict(asset_id=r['transaction'],project='EP_L2_V3',source_path=r['source_root'],logical_bytes=r['logical_bytes'],files=r['regular_files'],classification='ARCHIVED_VERIFIED',archive_state='ALL_MEMBER_CONTENT_METADATA_VERIFIED',restore_state='STREAM_FULL_CONTENT_AND_METADATA; NATIVE_SAMPLE_ONLY_3',true164_path=r['native164_root']+'/'+r['archive'],sha256=r['archive_sha256'],source_disposition='HISTORICALLY_SOURCE_RELEASED_BY_BA',current_source_present=False,proof_scope='Full stream member verification; small native samples; NOT a complete expanded native tree. Already released, zero new reclaim.',recovery_reference='09a6b4e4d329dfde43d8cf3cc1c6bd2f3e2d2b03:docs/ep_l2/operations/cold_fast_20261020_target/V3_BOTH_BATCHES_RECOVERY_INDEX_20261020.json',additive_group='NONADDITIVE_ALREADY_RELEASED'))
models=load('evidence/TRUE164_C16_AWMA_CATALOG_AND_SIX_MODEL_METADATA.json')['models']
proof=list(csv.DictReader((R/'references/SIX_ROW_TRUE164_AUTHORITY_PROOF.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
for r,s in zip(proof,models):
 coverage.append(dict(asset_id='C16_AUTHORITY_'+r['package']+'_'+r['pair_id'],project='C16_AI',source_path=r['original174_path'],logical_bytes=r['size_bytes'],files=1,classification='DUPLICATE_OR_REUSABLE',archive_state='SIX_COMPLETE_HISTORICAL_CONTENT_SHA_PASS',restore_state='EXACT_TWO_LAYOUT_RESTORE_MAP; NO_LARGE_NATIVE_RESTORE',true164_path=r['native164_path'],sha256=r['sha256_expected'],current_source_present=False,source_disposition='OUTBOUND_SIX_HISTORICALLY_RETIRED; canonical originals ACTIVE_KEEP',proof_scope='Current path/size/mtime match; SSHFS projected inode changed since prior full hashes. No new full hash and no native164 metadata claim.',recovery_reference='ab95e0aa46c73f6297315ecbbae09de10b09ce87:SIX_ROW_TRUE164_AUTHORITY_PROOF.tsv;735f8efe5df19017918fd5376357cb1e46e86190:conditional_retirement/CURRENT_RESTORE_INDEX.tsv',additive_group='NONADDITIVE_AUTHORITY_MODELS'))
canonical_models=load('evidence/C16_CANONICAL_SOURCE_MODELS_CURRENT_IDENTITY_AND_IMMUTABLE_RECEIPTS.json')
for i,s in enumerate(canonical_models):
 coverage.append(dict(asset_id='C16_PROTECTED_CANONICAL_SOURCE_'+str(i+1),project='C16_AI',source_path=s['path'],logical_bytes=s.get('size'),allocated_bytes=s.get('allocated'),files=1,classification='DUPLICATE_OR_REUSABLE',archive_state='EXISTING_TRUE164_SIX_CONTENT_SHA_PASS; SOURCE_CURRENT_EXACT_IDENTITY_AND_IMMUTABLE_FULL_SHA_RECEIPT_PASS',restore_state='NO_LARGE_NATIVE_RESTORE; ORIGINAL_CANONICAL_ACTIVE_KEEP',true164_path=proof[i]['native164_path'],sha256=s['historical_model_sha256'],current_source_present=True,source_disposition='ACTIVE_KEEP_NO_RETIREMENT_AUTHORITY',proof_scope='Source canonical originals differ from already-retired outbound copies. Six exact dev/inode/size/mtime/ctime + six immutable verification-receipt hashes match; genuine164 prior fullSHA6/6. Not a cleanup recommendation.',recovery_reference='evidence/C16_CANONICAL_SOURCE_MODELS_CURRENT_IDENTITY_AND_IMMUTABLE_RECEIPTS.json',additive_group='NONADDITIVE_PROTECTED_MODEL_SOURCE'))
industrial=json.loads((P/'ARCHIVE_COMPLETION_RECEIPT.json').read_text(encoding='utf8'))
coverage.append(dict(asset_id='INDUSTRIAL_L2_NINE_JSON',project='EP_L2_NETLIST',logical_bytes=industrial['original_bytes'],files=9,classification='UNKNOWN/HOLD',archive_state='ALL9_ARCHIVE_VERIFIED;503611418 compressed bytes',restore_state='NOT_EXECUTED_USER_ARCHIVE_ONLY',true164_path=industrial['native164_root'],source_disposition='SOURCE_KEEP',proof_scope='All120chunks+full original SHA coverage; no independent native restoration executed. No restoration PASS invented.',recovery_reference='1f0c30799012e4eb019d6c46d683a94da46f4eb8:docs/ep_l2/operations/industrial_l2_netlist_archive_20261022_v1/target_01/ARCHIVE_COMPLETION_RECEIPT.json',additive_group='NONADDITIVE_FORMAL_ARCHIVE'))
nasruns=load('evidence/AWMA_C16_IMMUTABLE_RUN_MANIFEST_METADATA_CROSSCHECK.json')
for r in nasruns:
 if r.get('status'):continue
 coverage.append(dict(asset_id=r['run_id'],project='AWMA_C16',source_path='PRODUCER_'+str(r.get('producer_host')),logical_bytes=r.get('raw_bytes'),files='',classification='UNKNOWN/HOLD',archive_state=r.get('transfer_status'),restore_state='RESTORATION_NOT_ESTABLISHED_BY_CATALOG_TRANSFER_ACK',true164_path=r['raw_path'],sha256=r.get('raw_manifest_sha256'),current_source_present='OTHER_NODE_NOT_PROBED',source_disposition='KEEP; NO_NODE109_OPERATIONS',proof_scope='Current genuine164 root; small RUN_MANIFEST digest equals catalog='+str(any(m['equals_catalog_raw_manifest'] for m in r['manifest_checks']))+'; no new raw payload SHA.',recovery_reference='evidence/AWMA_C16_IMMUTABLE_RUN_MANIFEST_METADATA_CROSSCHECK.json',additive_group='NAS_CATALOG_DECLARED_NONLOCAL_BYTES'))
# Fine-grained directories and large files are NONADDITIVE children of disjoint roots.
fine=[]
for endpoint,rs in [('ORIGINAL174_SSD_BACKED_OVERLAY',source),('SHARED_MD127',shared),('174NEW_NATIVE_OVERLAY',target)]:
 for r in rs:
  for a in r.get('assets',[]):
   if a['path']==r['path']:continue
   fine.append(dict(asset_id=hashlib.sha256((endpoint+a['path']).encode()).hexdigest()[:16],project=project(a['path'],project(r['path'],old_by.get(r['path'],{}).get('project','USER_RESEARCH_UNRESOLVED'))),endpoint=endpoint,source_path=a['path'],scope='NONADDITIVE_DIRECTORY_CHILD',logical_bytes=a['logical'],allocated_bytes=a['allocated'],files=a['files'],directories=a['dirs'],measurement=r['status'],classification='RETENTION_REVIEW_CANDIDATE' if Path(a['path']).name in ['build','postcheck','wheelhouse'] else 'UNKNOWN/HOLD',archive_state='NO_EXACT_WHOLE_DIRECTORY_ARCHIVE_JOIN',restore_state='NOT_ESTABLISHED',overlap_parent=r['path'],additive_group='NONADDITIVE_CHILD',retention='KEEP; mixed binaries/config/scientific evidence require exact owner review',evidence='evidence/*METADATA_BATCH*.json'))
  for a in r.get('large_files',[]):
   match=filecoverage.get(a['path'])
   fine.append(dict(asset_id=hashlib.sha256((endpoint+a['path']).encode()).hexdigest()[:16],project=project(a['path'],project(r['path'])),endpoint=endpoint,source_path=a['path'],scope='NONADDITIVE_LARGE_REGULAR_FILE',logical_bytes=a['size'],allocated_bytes=a['allocated'],files=1,measurement=r['status'],classification=match['classification'] if match else 'UNKNOWN/HOLD',archive_state=match['archive_state'] if match else 'NO_TRUSTED_EXACT_SHA_JOIN',restore_state=match['restore_state'] if match else 'NOT_ESTABLISHED',overlap_parent=r['path'],additive_group='NONADDITIVE_CHILD',retention='SOURCE_KEEP',evidence=match['recovery_reference'] if match else 'evidence/*METADATA_BATCH*.json'))
inv+=fine
for c in coverage:
 if c['asset_id'] not in {r['asset_id'] for r in inv}:
  inv.append(dict(c,endpoint='TRUE164_ARCHIVE_REFERENCE' if c.get('true164_path') else 'HISTORICAL_REFERENCE',measurement='HISTORICAL_OR_DECLARED_NOT_CURRENT_SOURCE_ALLOCATION',retention='SOURCE_KEEP_OR_HISTORICALLY_RELEASED; THIS_TASK_NO_RELEASE',notes='Reference row only; cannot add historical/source/NAS bytes to measured filesystem roots.'))
writecsv('INVENTORY.csv',inv);writecsv('ARCHIVE_COVERAGE.csv',coverage);writecsv('RAW_EXPERIMENT_RECORDS.csv',raw);writecsv('FILE_TYPE_SUMMARY.csv',types)
trace_candidates=[r for r in fine if any(t in r['source_path'].lower() for t in ['trace','polybench','rodinia','capture','nsys','ncu']) and r['allocated_bytes']>0 and r['endpoint']!='174NEW_NATIVE_OVERLAY' and (r['source_path'].endswith('/traces') or (r['scope']=='NONADDITIVE_LARGE_REGULAR_FILE' and any(r['source_path'].lower().endswith(s) for s in ['.traceg','.gz','.tgz','.zst','.nsys-rep','.ncu-rep','.c16warp1','.bin','.raw'])))]
top=[]
for r in sorted(trace_candidates,key=lambda r:-r['allocated_bytes']):
 p=r['source_path']
 if any(p==z['source_path'] or p.startswith(z['source_path']+'/') or z['source_path'].startswith(p+'/') for z in top):continue
 top.append(dict(rank=len(top)+1,**r))
 if len(top)>=30:break
writecsv('LARGE_ASSETS_TOP30.csv',top)
polys=[]
for r in fine:
 p=r['source_path']
 if 'polybench' not in p.lower() or not (p.endswith('/traces') or ('NONADDITIVE_LARGE_REGULAR_FILE'==r['scope'] and '.tg' in p)):continue
 comps=Path(p).parts;program=next((c for c in reversed(comps) if c.startswith('polybench-')),'PACKAGE_OR_UNRESOLVED');program=program.replace('polybench-','')
 polys.append(dict(**r,program_variant=program,input_scale='PATH_VARIANT_ONLY; NOT_SCIENTIFICALLY_INFERRED' if program=='PACKAGE_OR_UNRESOLVED' else program,version='11.0' if '/11.0/' in p else 'OWNER_OR_MEMBER_INDEX_REQUIRED',native_current_members='METADATA_ONLY',notes='Fraction/trim variants are distinct until exact byte manifest proves equality. Full tgz member inventory not regenerated by scanning payload.'))
writecsv('POLYBENCH_TRACE_INVENTORY.csv',polys)
alias=load('evidence/SOURCE_TRACE_ALIAS_AND_STORAGE_ENDPOINTS.json')['symlinks']
writecsv('SOURCE_ALIAS_ENDPOINT_MAP.csv',[dict(path=r['path'],target=r.get('link'),resolved_path=r['resolved_path'],classification='DUPLICATE_OR_REUSABLE',relation='SAME_PATH_ALIAS_ONLY_NOT_AN_EXTRA_COPY',native_storage_endpoint='SHARED_MD127' if r['resolved_path'].startswith('/root/share/') else 'SOURCE_NATIVE_OR_UNRESOLVED',counts_toward_duplicate_payload_bytes=0) for r in alias])
def aggregate(rows,keys):
 out={}
 for r in rows:
  k=tuple(r[z] for z in keys);a=out.setdefault(k,dict(zip(keys,k),roots=0,files=0,logical_bytes=0,allocated_bytes=0,partial_roots=0))
  a['roots']+=1;a['files']+=int(r.get('files') or 0);a['logical_bytes']+=int(r.get('logical_bytes') or 0);a['allocated_bytes']+=int(r.get('allocated_bytes') or 0);a['partial_roots']+=int(r['measurement']!='COMPLETE_METADATA_ONLY')
 return list(out.values())
writecsv('PROJECT_ENDPOINT_SUMMARY.csv',aggregate(root_rows,['project','endpoint']))
writecsv('ENDPOINT_SUMMARY.csv',aggregate(root_rows,['endpoint']))
retention=[r for r in fine if r['classification']=='RETENTION_REVIEW_CANDIDATE'];rr=[]
for r in sorted(retention,key=lambda r:len(r['source_path'])):
 if not any(r['source_path'].startswith(z['source_path']+'/') for z in rr):rr.append(r)
writecsv('RETENTION_REVIEW_ONLY.csv',rr)
stats=dict(inventory_rows=len(inv),archive_rows=len(coverage),source_roots=len(source),source_files=sum(r.get('files',0) for r in source),source_logical=sum(r.get('logical',0) for r in source),source_allocated=sum(r.get('allocated',0) for r in source),source_partial=[r['path'] for r in source if r['status'].startswith('INCOMPLETE')],share_logical=sum(r.get('logical',0) for r in shared),share_allocated=sum(r.get('allocated',0) for r in shared),target_awma_allocated=sum(r.get('allocated',0) for r in target),source_archived_trace_logical=sum(r['logical_bytes'] for r in selectors),source_archived_trace_allocated=archived_source_alloc,source_archived_polybench_tgz_allocated=poly_current.get('allocated',0) if poly_identity_match else 0,source_archived_full_result_allocated=sum(r['allocated_bytes'] for r in fullresults),source_archived_full_result_logical=sum(r['logical_bytes'] for r in fullresults),trace_complete_native_restores=sum(r['classification']=='ARCHIVED_VERIFIED' for r in selectors),known_missing_formal_archive_bytes=tls['remaining_original_bytes'],potential_duplicate_trace_content_bytes=sum(r['logical_bytes'] for r in selectors),retention_review_container_allocated_upper_bound=sum(r['allocated_bytes'] for r in rr),nas_catalog_runs=len([r for r in nasruns if not r.get('status')]),nas_declared_logical=sum(int(r.get('raw_bytes') or 0) for r in nasruns if not r.get('status')),nas_catalog_manifest_hash_matches=sum(any(m['equals_catalog_raw_manifest'] for m in r.get('manifest_checks',[])) for r in nasruns),polybench_rows=len(polys),top30=len(top),authorized_release_bytes=0,actual_release_bytes=0,large_payload_rehash_bytes=0,assets_transferred=0)
save('CALCULATED_TOTALS_AND_NONADDITIVE_ESTIMATES.json',stats)
stats['protected_canonical_models_allocated_bytes']=sum(s.get('allocated',0) for s in canonical_models if s.get('source_exact_identity_match') and s.get('immutable_receipt_matches_census'))
stats['known_source_path_disjoint_archived_content_allocated_lower_bound']=stats['source_archived_trace_allocated']+stats['source_archived_full_result_allocated']+stats['source_archived_polybench_tgz_allocated']+stats['protected_canonical_models_allocated_bytes']
save('CALCULATED_TOTALS_AND_NONADDITIVE_ESTIMATES.json',stats)
print(json.dumps(stats,indent=2))
