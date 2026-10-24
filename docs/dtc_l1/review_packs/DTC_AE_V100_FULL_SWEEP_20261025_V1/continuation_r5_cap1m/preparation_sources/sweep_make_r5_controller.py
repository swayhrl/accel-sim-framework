import pathlib,ast,json,hashlib
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');s=(T/'tools/revision4/sweep_controller.py').read_text();start=s.index('def adopt(');end=s.index('def main():',start)
adopt='''def adopt(native,lease):
 pub=read(T/'control/CONTINUATION_R5_PUBLICATION_READBACK.json');qual=read(T/'control/CONTINUATION_R5_ZERO_MODEL_QUALIFICATION.json');candidate=read(T/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json')
 assert pub['verified'] and pub['controller_sha256']==sha(__file__) and qual['status']=='PASS' and pub['candidate_sha256']==sha(T/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json')
 assert read(T/'telemetry_v2/CPU_PROTOCOL_QUALIFICATION.json')['status']=='PASS_OBSERVATIONAL_CAP1M_CPU_PROTOCOL_NOT_SCIENTIFIC_MODEL'
 assert read(T/'control/CAP1M_FRAMEWORK_PUBLICATION_READBACK.json')['verified']
 for row in candidate['source_pins']:assert sha(row['path'])==row['sha256']
 for revision in ['R2','R3','R4']:
  old=read(T/'control'/('CONTROLLER_LAUNCH_'+revision+'.json'));proc=P('/proc')/str(old['pid'])
  if proc.exists():
   stat=(proc/'stat').read_text().rsplit(')',1)[1].split();assert int(stat[19])!=old['start_ticks'] or stat[0]=='Z','prior controller generation still live'
 assert not (T/'control/CONTROLLER_START_R3.json').exists() and not (T/'control/CONTROLLER_START_R4.json').exists()
 assert read(T/'analysis/TELEMETRY_CAP8192_AUDIT_R4_METADATA_STOP.json')['new_scientific_starts']==0
 reg,epoch=native.read_current_authority();q=reg['registered_future_requests'][REQ];assert q['state']=='RUNNING' and q['budget']==356 and len(q['consumed'])==105
 assert not read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 failure=module('cap1m_closed_failure_adoption','sweep_failure_review_cap1m.py');outbox=module('unchanged_closed_archive_adoption','sweep_outbox.py');recovered={};issue_preimages=[]
 for cell,row in q['consumed'].items():
  assert 'execution_receipt' in row,'unclosed spent native attempt'
  resultfile=T/'analysis'/(cell+'.RESULT.json');result=read(resultfile);assert result.get('uuid',result.get('native_done',{}).get('uuid'))==row['uuid']
  if result['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE':
   intent=read(T/'control/qualification_ledger'/(cell+'.INTENT.json'));out=P(intent['output']);qualification=read(T/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json'));assert qualification['strict_sha256']==sha(out/'AEFAIR_STRICT.json') and qualification['uuid']==row['uuid'];recovered[cell]=result;continue
  proof=failure.classify(cell);receipt=read(T/'control'/(cell+'_ARCHIVE_RECEIPT.json'));assert receipt['scientific_status']=='STOP_UNACCEPTED' and receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
  bundle=P(receipt['target_mount_path']);f,v=outbox.libraries(bundle);manifest=read(bundle/'SOURCE_MANIFEST.json');idx=f.verify_archive(bundle,manifest);assert idx['archive_sha256']==receipt['archive_sha256'];f.check_native(P(receipt['native_restore']),manifest)
  issue_preimages.append((resultfile,resultfile.read_bytes()))
  recovered[cell]={'state':'FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY','cohort':cell,'uuid':row['uuid'],'failure_classification':proof,'archive':receipt,'accepted_cycles':None,'partial_cycles_accepted':False}
 assert sum(r['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE' for r in recovered.values())==102 and len(issue_preimages)==3
 before=json.loads(json.dumps(q));write(T/'control/REQUEST_BEFORE_CONTINUATION_R5.json',before)
 def amend(registry):
  actual=registry['registered_future_requests'][REQ];assert actual==before
  actual['operational_continuations']=actual.get('operational_continuations',[])+[{'revision':'R5','prior_orchestrator_sha256':actual['orchestrator_sha256'],'new_orchestrator_sha256':sha(__file__),'publication_commit':pub['commit'],'qualification_sha256':sha(T/'control/CONTINUATION_R5_ZERO_MODEL_QUALIFICATION.json'),'prior_consumed':105,'same_finite_budget':356,'model_retries':0}]
  actual['orchestrator_sha256']=sha(__file__);assert not actual.get('effective_specs')
  profile=dict(candidate,status='REGISTERED_FOR_ORIGINAL_UNUSED_CELLS',candidate_sha256=sha(T/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json'),publication_commit=pub['commit'],qualification_sha256=sha(T/'control/CONTINUATION_R5_ZERO_MODEL_QUALIFICATION.json'),framework_publication_sha256=sha(T/'control/CAP1M_FRAMEWORK_PUBLICATION_READBACK.json'),activation_prior_consumed=105)
  actual['operational_engine_profiles']=dict(actual.get('operational_engine_profiles',{}),OBSERVABILITY_CAP1M_WALL90_V1=profile);actual['effective_specs']={}
 native.update_authority(amend)
 after=native.read_current_authority()[0]['registered_future_requests'][REQ];assert all(after[k]==v for k,v in before.items() if k not in ['orchestrator_sha256','operational_continuations','operational_engine_profiles','effective_specs'])
 for file,original_bytes in issue_preimages:
  pre=T/'analysis/issue_preimages';pre.mkdir(exist_ok=True);saved=pre/(file.stem+'.R2.json')
  if saved.exists():assert saved.read_bytes()==original_bytes
  else:
   with saved.open('xb') as f:f.write(original_bytes)
  write(file,recovered[file.name.removesuffix('.RESULT.json')])
 prior=(N/'bin/native').read_bytes();needle=str(T/'tools/sweep_frontend.py').encode();assert prior.count(needle)==1
 with (T/'control/NATIVE_ENTRY_BEFORE_CAP1M.sh').open('xb') as f:f.write(prior)
 replacement=prior.replace(needle,str(T/'tools/sweep_frontend_cap1m.py').encode());tmp=N/'bin/.native.DTC_SWEEP_CAP1M.writing'
 with tmp.open('xb') as f:f.write(replacement);f.flush();os.fsync(f.fileno())
 tmp.chmod((N/'bin/native').stat().st_mode&0o777);assert (N/'bin/native').read_bytes()==prior;os.replace(tmp,N/'bin/native')
 write(T/'control/CONTINUATION_R5_ADOPTED.json',{'state':'ALL_105_SPENT_ADOPTED_NO_RERUN','consumed':105,'remaining':before['remaining'],'accepted':102,'closed_unaccepted':3,'old_request_fields_unchanged':True,'original_specs_and_runtime_unchanged':True,'prior_entry_sha256':hashlib.sha256(prior).hexdigest(),'new_entry_sha256':sha(N/'bin/native'),'lease':lease})
 return recovered

'''
s=s[:start]+adopt+s[end:];s=s.replace('CONTROLLER_START_R4','CONTROLLER_START_R5')
# Restore the explicit R4 cancellation guard inside the new adoption function.
s=s.replace("assert not (T/'control/CONTROLLER_START_R3.json').exists() and not (T/'control/CONTROLLER_START_R5.json').exists()","assert not (T/'control/CONTROLLER_START_R3.json').exists() and not (T/'control/CONTROLLER_START_R4.json').exists()")
s=s.replace("'sweep_native_wall90_v1.py'","'sweep_native_cap1m.py'").replace("'sweep_strict.py'","'sweep_strict_cap1m.py'").replace("'sweep_admission.py'","'sweep_admission_cap1m.py'").replace("'sweep_failure_review.py'","'sweep_failure_review_cap1m.py'").replace('FAIL_CLOSED_NATIVE_DEADLOCK_ARCHIVED_NO_RETRY','FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY')
ast.parse(s);dest=T/'tools/revision5/sweep_controller.py';dest.parent.mkdir(exist_ok=True)
with dest.open('x') as f:f.write(s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((T/'telemetry_v2/BUILD_RESULT.json').read_bytes());sources=[T/'tools'/name for name in ['sweep_native_cap1m.py','sweep_strict_cap1m.py','sweep_guard_cap1m.py','sweep_cap1m_specs.py','sweep_admission_cap1m.py','sweep_failure_review_cap1m.py','sweep_frontend_cap1m.py','runtime_policy_wall90_v1.py']]+[T/'telemetry_v2/telemetry_receiver_cap1m.py',T/'telemetry_v2/framework/gpu-simulator/ag7_policyb_progress.h']
candidate={'status':'PREPARED_NOT_REGISTERED','profile_id':'OBSERVABILITY_CAP1M_WALL90_V1','max_records':1048576,'per_drain_records':8193,'wall_seconds':7776000,'finite_budget':356,'model_retries':0,'framework_parent':b['framework_parent'],'framework_commit':b['framework_commit'],'Core_commit':b['core_commit'],'framework_binary':b['framework_binary'],'source_worktrees':{'core':str((T/'core').resolve()),'framework':str(T/'telemetry_v2/framework')},'engine_sha256':sha(T/'tools/sweep_native_cap1m.py'),'strict_sha256':sha(T/'tools/sweep_strict_cap1m.py'),'runtime_spec_producer_sha256':sha(T/'tools/sweep_cap1m_specs.py'),'source_pins':[{'path':str(p),'sha256':sha(p)} for p in sources],'observational_source_delta':'Framework exactly one header record-limit constant;receiver total-limit plus unchanged original drain budget;Core/cache/performance options/input/config unchanged','build_receipt_sha256':sha(T/'telemetry_v2/BUILD_RESULT.json'),'CPU_protocol_qualification_sha256':sha(T/'telemetry_v2/CPU_PROTOCOL_QUALIFICATION.json'),'old_authority_and_original_specs_preserved':True}
with (T/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json').open('x') as f:json.dump(candidate,f,indent=2);f.write(chr(10))
proof={'status':'PREPARED_NOT_LAUNCHED','controller_sha256':sha(dest),'candidate_sha256':sha(T/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json'),'engine_sha256':candidate['engine_sha256'],'strict_sha256':candidate['strict_sha256'],'source_pins':candidate['source_pins']}
with (T/'control/CONTINUATION_R5_PREPARATION.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
print(json.dumps({k:v for k,v in proof.items() if k!='source_pins'},indent=2))
