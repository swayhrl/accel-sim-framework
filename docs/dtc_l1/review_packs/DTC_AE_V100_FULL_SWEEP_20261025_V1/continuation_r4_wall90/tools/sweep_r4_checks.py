import pathlib,json,hashlib,importlib.util,tempfile,copy,types,ast,datetime,shutil
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1';cell='E2-AEV100-1df9d5479504d9c7-DM';tests=[]
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x)+chr(10))
def load(p):s=importlib.util.spec_from_file_location('isolated_r4_controller_qualification',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def test(name,fn):fn();tests.append({'test':name,'status':'PASS'})
def truth(v):assert v
controller=T/'tools/revision4/sweep_controller.py';m=load(controller);prep=read(T/'control/CONTINUATION_R4_PREPARATION.json');wall=read(T/'control/WALL90_PROFILE_CANDIDATE.json')
before={str(p):sha(p) for p in [N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json',N/'control/CURRENT_SCIENCE_EPOCH.json',N/'bin/native',T/'tools/sweep_native.py']}
test('all_wall_sources_still_match_21check_qualification',lambda:truth(all(sha(T/'tools'/r['name'])==r['sha256'] for r in wall['source_pins']) and read(T/'control/WALL90_ZERO_MODEL_QUALIFICATION.json')['status']=='PASS'))
test('R4_and_failure_classifier_precise_source_pins',lambda:truth(sha(controller)==prep['controller_sha256'] and sha(T/'tools/sweep_failure_review.py')==prep['failure_review_sha256']))
actual=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][REQ];q=copy.deepcopy(actual);q['consumed']={cell:q['consumed'][cell]};q['remaining']=355
class NativeFixture:
 def __init__(self):self.reg={'registered_future_requests':{REQ:copy.deepcopy(q)}};self.updates=0
 def read_current_authority(self):return copy.deepcopy(self.reg),{'epoch':2}
 def update_authority(self,fn):fn(self.reg);self.updates+=1
with tempfile.TemporaryDirectory(prefix='dtc-r4-adoption-zero-model-') as tmp:
 root=P(tmp);native=root/'native';m.T=root;m.N=native;(root/'tools').mkdir();(root/'analysis').mkdir()
 for p in (T/'tools').glob('*.py'):(root/'tools'/p.name).symlink_to(p)
 for rel in ['WALL90_PROFILE_CANDIDATE.json','WALL90_ZERO_MODEL_QUALIFICATION.json','CONTROLLER_LAUNCH_R3.json',cell+'_ARCHIVE_RECEIPT.json']:write(root/'control'/rel,read(T/'control'/rel))
 write(root/'analysis/WALL_DEADLINE_AUDIT_R3_METADATA_STOP.json',read(T/'analysis/WALL_DEADLINE_AUDIT_R3_METADATA_STOP.json'))
 write(root/'control/CONTINUATION_R4_PUBLICATION_READBACK.json',{'verified':True,'controller_sha256':sha(controller),'failure_review_sha256':prep['failure_review_sha256'],'commit':'DECLARED_SYNTHETIC_PUBLICATION_FOR_ISOLATED_TEST_ONLY'})
 write(root/'control/CONTINUATION_R4_ZERO_MODEL_QUALIFICATION.json',{'status':'PASS','fixture_only_no_live_authority':True});write(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 write(root/'analysis'/(cell+'.RESULT.json'),read(T/'analysis'/(cell+'.RESULT.json')))
 entry=native/'bin/native';entry.parent.mkdir(parents=True);entry.write_text('ASSET_ROUTE_COPY_ONLY\nexec python '+str(root/'tools/sweep_frontend.py')+' "$@"\n');entry.chmod(0o755);entry_before=entry.read_bytes()
 write(root/'control/CONTROLLER_LAUNCH_R2.json',read(T/'control/CONTROLLER_LAUNCH_R2.json'));fixture=NativeFixture()
 try:m.adopt(fixture,{'fixture':True})
 except AssertionError as e:assert 'old controller generation still live' in str(e)
 else:raise AssertionError('R4 stole live prior controller')
 test('live_prior_controller_is_denied_before_authority_or_frontend_changes',lambda:truth(fixture.updates==0 and entry.read_bytes()==entry_before))
 write(root/'control/CONTROLLER_LAUNCH_R2.json',{'pid':999999999,'start_ticks':1});fixture=NativeFixture();del fixture.reg['registered_future_requests'][REQ]['consumed'][cell]['execution_receipt']
 try:m.adopt(fixture,{'fixture':True})
 except AssertionError as e:assert 'active or unclosed prior model' in str(e)
 else:raise AssertionError('R4 adopted unclosed model')
 test('unclosed_spent_model_is_denied_before_update',lambda:truth(fixture.updates==0 and entry.read_bytes()==entry_before))
 fixture=NativeFixture();recovered=m.adopt(fixture,{'fixture':True});after=fixture.reg['registered_future_requests'][REQ]
 test('positive_isolated_closed_failure_adoption_preserves_budget_and_consumed',lambda:truth(after['consumed']==q['consumed'] and after['remaining']==355 and after['budget']==356 and fixture.updates==1))
 test('positive_adoption_preserves_original_controller_AUTH_specs_and_other_fields',lambda:truth(all(after[k]==v for k,v in q.items() if k not in ['orchestrator_sha256','operational_continuations','operational_engine_profiles'])))
 test('positive_adoption_only_registers_exact_wall90_profile',lambda:truth(after['operational_engine_profiles']['WALL90_V1']['engine_sha256']==wall['engine_sha256'] and after['operational_engine_profiles']['WALL90_V1']['source_pins']==wall['source_pins'] and after['operational_engine_profiles']['WALL90_V1']['activation_prior_consumed']==1))
 test('positive_frontend_rebind_preserves_all_other_bytes',lambda:truth(entry.read_bytes()==entry_before.replace(str(root/'tools/sweep_frontend.py').encode(),str(root/'tools/sweep_frontend_wall90_v1.py').encode())))
 test('positive_failed_result_remains_unaccepted_with_preimage',lambda:truth(recovered[cell]['state']=='FAIL_CLOSED_NATIVE_DEADLOCK_ARCHIVED_NO_RETRY' and recovered[cell]['accepted_cycles'] is None and (root/'analysis/issue_preimages'/(cell+'.RESULT_R2.json')).exists()))
 test('positive_adoption_writes_no_model_INTENT_or_start',lambda:truth(not (root/'control/qualification_ledger').exists() and not (root/'control/CONTROLLER_START_R4.json').exists()))
assert before=={str(P(p)):sha(P(p)) for p in before}
tests.append({'test':'live_authority_epoch_entry_and_old_launcher_bytes_unchanged','status':'PASS'})
proof={'status':'PASS','test_count':len(tests),'tests':tests,'controller_sha256':sha(controller),'failure_review_sha256':prep['failure_review_sha256'],'wall_engine_sha256':wall['engine_sha256'],'WALL90_qualification_sha256':sha(T/'control/WALL90_ZERO_MODEL_QUALIFICATION.json'),'fixture_provenance':'DECLARED_SYNTHETIC_AUTHORITY_PUBLICATION_AND_ENTRY_IN_ABSENT_TEMP_ROOT;real closed failure archive read only;no simulator or live authority mutation.','scientific_starts':0,'actual_existing_models_modified':False,'source_files_modified':False,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (T/'control/CONTINUATION_R4_ZERO_MODEL_QUALIFICATION.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
print(json.dumps(proof,indent=2))
