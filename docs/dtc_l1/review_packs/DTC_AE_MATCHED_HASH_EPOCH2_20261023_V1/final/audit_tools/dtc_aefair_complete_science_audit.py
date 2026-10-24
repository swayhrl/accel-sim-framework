"""Completion-scope independent evidence join; no model launch or ledger writes."""
import pathlib,json,hashlib,importlib.util,datetime,subprocess,os
T=pathlib.Path('/root/data/dtc_main_20261023_v1/ae_fair_v1');N=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2');F=pathlib.Path('/root/data/dtc_main_20261023_v1/accel-sim-framework');P=F/'docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_EPOCH2_20261023_V1'
ORDER=['E2-AEFAIR-'+c for c in ['DM','DH','CM','CH']]
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def save(name,value):
 with (T/'analysis'/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
regfile=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';reg=read(regfile);epoch=read(N/'control/CURRENT_SCIENCE_EPOCH.json');q=reg['registered_future_requests']['DTC_AEFAIR_EPOCH2_V1']
assert epoch['native_registry_sha256']==sha(regfile) and epoch['epoch']==2 and epoch['state']=='NATIVE_SCIENCE_ACTIVE' and epoch['holder']==os.uname().nodename
assert q['budget']==4 and q['remaining']==0 and q['state']=='COMPLETE' and set(q['consumed'])==set(ORDER)
assert read(T/'control/CONTROLLER_STATE.json')['state']=='ALL_FOUR_SCIENCE_ARCHIVE_RESTORE_COMPLETE'
request=read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json');assert request['matrix_order']==ORDER and q['spec_request_sha256']==sha(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
assert sha(T/'aefair_analysis.py')==sha(P/'consumer/aefair_analysis.py'),'frozen consumer changed'
assert q['controller_sha256']==sha(T/'tools/aefair_native.py')
for pin in q['shared_tool_pins']:assert sha(pathlib.Path(pin['path']))==pin['sha256'],pin['path']
for name,head in [('core','2e3bef4364e578cddd0e881c0baace2e51c55930'),('framework','cfd3ff56d7ba6642dab6c7710ec4f6065168174e')]:
 assert subprocess.check_output(['git','-C',str(T/name),'rev-parse','HEAD'],text=True).strip()==head
 assert not subprocess.check_output(['git','-C',str(T/name),'status','--porcelain'],text=True).strip()
amend=read(T/'control/UNUSED_CPLUS_AMENDMENT_APPLIED.json');oldauth=pathlib.Path(amend['old_DM_authorization_preimage']['path']);assert sha(oldauth)==amend['old_DM_authorization_preimage']['sha256']
strict=load('completion_exact_full_strict',T/'tools/aefair_strict.py');cells=[];uuids=[];sequence=[]
for cohort in ORDER:
 intentfile=T/'control/qualification_ledger'/(cohort+'.INTENT.json');intent=read(intentfile);done=read(T/'control/qualification_ledger'/(cohort+'.DONE.json'));out=pathlib.Path(intent['output']);specfile=T/'control'/(cohort+'_SPEC.json');spec=read(specfile);row=q['consumed'][cohort]
 assert row['uuid']==intent['uuid']==done['uuid'] and row['intent_sha256']==sha(intentfile) and row['charged']==1
 assert intent['spec_sha256']==sha(specfile) and next(r for r in request['specs'] if r['cohort']==cohort)['sha256']==sha(specfile)
 assert intent['authorization_sha256']==sha(oldauth if cohort.endswith('DM') else T/'control/SCIENCE_AUTHORIZATION.json')
 assert done['new_attempt_consumed']==1 and done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed']
 assert done==read(out/'NATIVE_EXIT.json') and row['execution_receipt']==done
 assert read(out/'AEFAIR_STRICT.json')==strict.terminal(cohort),'independent full strict replay differs:'+cohort
 for runtime in spec['runtime_files']:assert sha(T/runtime['target'])==runtime['sha256'] and str((T/runtime['target']).resolve())==runtime['actual_realpath']
 pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=pathlib.Path('/proc')/str(pid['pid'])
 if proc.exists():assert int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=pid['start_ticks'],'old model generation still live'
 samples=[];warnings=[]
 for line in (out/'RESOURCE_SAMPLES.jsonl').read_text().splitlines():
  x=json.loads(line)
  if 'DTC_exact_original_policy' not in x:continue
  d=x['DTC_exact_original_policy'];assert d['decision']['decision']!='STOP';samples.append(d['sample']['monotonic_ns'])
  if d['decision']['warnings']:warnings.append(d['decision']['warnings'])
 gaps=[(b-a)/1e9 for a,b in zip(samples,samples[1:])];assert samples and (not gaps or max(gaps)<=30),'resource sample gap:'+cohort
 uuids.append(intent['uuid']);rec=T/'control'/(cohort+'_ARCHIVE_RECEIPT.json')
 cells.append({'cohort':cohort,'uuid':intent['uuid'],'intent_sha256':sha(intentfile),'spec_sha256':sha(specfile),'execution_authorization_sha256':intent['authorization_sha256'],'new_start_charged':row['charged'],'new_attempt_consumed':done['new_attempt_consumed'],'native_returncode':done['launcher_wait_returncode'],'strict_independently_replayed':True,'runtime_files_current_sha_and_realpath_checked':len(spec['runtime_files']),'model_generation_gone':True,'resource_samples':len(samples),'resource_warning_samples':len(warnings),'resource_stop_samples':0,'max_resource_gap_seconds':max(gaps) if gaps else 0,'archive_local_receipt_mtime_ns':rec.stat().st_mtime_ns,'intent_utc':intent['utc']})
assert len(set(uuids))==4
assert {p.name for p in (T/'DTC/run/results').iterdir() if p.is_dir()}==set(uuids),'extra own scientific output population'
assert {p.name for p in (T/'control/qualification_ledger').glob('E2-AEFAIR-*.INTENT.json')}=={c+'.INTENT.json' for c in ORDER}
for first,nextrow in zip(cells,cells[1:]):
 next_ns=int(datetime.datetime.fromisoformat(nextrow['intent_utc']).timestamp()*1e9);assert first['archive_local_receipt_mtime_ns']<next_ns
 sequence.append({'archived_cell':first['cohort'],'next_started_cell':nextrow['cohort'],'archive_receipt_precedes_next_intent':True,'minimum_elapsed_seconds':(next_ns-first['archive_local_receipt_mtime_ns'])/1e9})
install=read(T/'control/NATIVE_REQUEST_INSTALL_RECEIPT.json');oldsha=install['epoch']['request_revision']['prior_registry_sha256'];pre=N/'control/science_authority/request_history'/('NATIVE_SCIENCE_REGISTRY.'+oldsha+'.json');assert sha(pre)==oldsha;old=read(pre)
assert reg['old_source_history']==old['old_source_history'] and reg['qualification_history']==old['qualification_history']
peers={k:reg['registered_future_requests'].get(k)==v for k,v in old['registered_future_requests'].items()};assert all(peers.values()),'pre-existing foreign request changed during cohort; adjudicate before closure'
analysis=load('frozen_qualified_complete_population_consumer',T/'aefair_analysis.py');result,rows=analysis.collect_verified();save('COMPLETE_RESULT.json',result)
audit={'schema':'DTC_AEFAIR_COMPLETE_SCIENCE_REQUIREMENT_AUDIT_V1','status':'PASS_ALL_FOUR_SCIENTIFIC_EXECUTION_AND_ARCHIVE_REQUIREMENTS_DELIVERY_PENDING','science_matrix_order':ORDER,'starts_consumed':4,'remaining_budget':0,'four_unique_attempts':True,'own_output_directory_population_exactly_four':True,'all_four_full_strict_independently_replayed':True,'all_four_archives_and_restores_full_inventory_and_sha_rechecked':True,'restore_entries_total':sum(x['restore_entries'] for x in result['proofs']),'new_scientific_request_state':q['state'],'current_native_epoch':epoch,'current_registry_sha256':sha(regfile),'pre_request_registry_sha256':oldsha,'old_source_history_unchanged':True,'qualification_history_unchanged':True,'pre_existing_foreign_request_rows_unchanged':peers,'old_AG8R1_restarts':0,'no_extra_start_retry_refund_or_canary_in_own_population':True,'original_DM_authorization_preimage_preserved':str(oldauth),'cells':cells,'strict_archive_restore_before_next_start':sequence,'consumer_sha256':sha(T/'aefair_analysis.py'),'complete_result_sha256':sha(T/'analysis/COMPLETE_RESULT.json'),'scientific_claim_boundary':result['interpretation_boundary'],'remaining_delivery_work':['source/contract/historical-file audit','final report and complete evidence publication','final evidence/reproducibility bundle true164 archive and independent native restore','final publication readback and Goal completion accounting'],'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
save('FOUR_CELL_SCIENCE_REQUIREMENT_AUDIT.json',audit)
chproof=next(x for x in result['proofs'] if x['cell']=='CH');save('CH_CLOSED_INDEPENDENT_RECHECK.json',dict(chproof,status='PASS_COMPLETE_CH_STRICT_NATIVE_ARCHIVE_RESTORE',cycles=rows['CH']['cycles'],instructions=rows['CH']['instructions'],CTA=rows['CH']['CTA'],full_strict_independently_replayed=True,current_spec_and_revision2_authorization_verified=True,verified_utc=audit['verified_utc']))
print(json.dumps({'complete_scientific_result':result,'audit_status':audit['status'],'resource_scope':[{k:r[k] for k in ['cohort','resource_samples','resource_warning_samples','max_resource_gap_seconds']} for r in cells],'sequence':sequence,'old_history_and_peers_unchanged':True},indent=2))
