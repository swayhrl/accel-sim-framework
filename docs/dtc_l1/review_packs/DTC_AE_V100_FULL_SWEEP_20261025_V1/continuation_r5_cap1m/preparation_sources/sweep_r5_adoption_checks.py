import pathlib,json,hashlib,importlib.util,tempfile,copy,os,datetime,shutil
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1';ID='OBSERVABILITY_CAP1M_WALL90_V1';tests=[]
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+chr(10))
def test(name,v):assert v,name;tests.append({'test':name,'status':'PASS'})
controller=T/'tools/revision5/sweep_controller.py';s=importlib.util.spec_from_file_location('full_R5_isolated_adoption',controller);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
actual=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');q=actual['registered_future_requests'][REQ];candidate=read(T/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json');current_sha=sha(controller)
paths=[N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json',N/'control/CURRENT_SCIENCE_EPOCH.json',N/'bin/native'];before={str(p):sha(p) for p in paths}
class NativeFixture:
 def __init__(self):self.reg=copy.deepcopy(actual);self.updates=0
 def read_current_authority(self):return copy.deepcopy(self.reg),{'epoch':2}
 def update_authority(self,fn):fn(self.reg);self.updates+=1
with tempfile.TemporaryDirectory(prefix='R5-full-adoption-',dir=T/'analysis') as tmp:
 root=P(tmp);m.T=root;m.N=root/'native';(root/'tools').mkdir();(root/'analysis').mkdir();(root/'control').mkdir()
 for p in (T/'tools').glob('*.py'):(root/'tools'/p.name).symlink_to(p)
 write(root/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json',candidate)
 write(root/'control/CONTINUATION_R5_PUBLICATION_READBACK.json',{'verified':True,'controller_sha256':current_sha,'candidate_sha256':sha(root/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json'),'commit':'DECLARED_SYNTHETIC_ISOLATED_PUBLICATION_ONLY'})
 write(root/'control/CONTINUATION_R5_ZERO_MODEL_QUALIFICATION.json',{'status':'PASS','controller_sha256':current_sha,'candidate_sha256':sha(root/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json'),'fixture_only':True})
 write(root/'telemetry_v2/CPU_PROTOCOL_QUALIFICATION.json',read(T/'telemetry_v2/CPU_PROTOCOL_QUALIFICATION.json'));write(root/'control/CAP1M_FRAMEWORK_PUBLICATION_READBACK.json',{'verified':True,'commit':candidate['framework_commit'],'parent':candidate['framework_parent'],'fixture_only':True})
 write(root/'analysis/TELEMETRY_CAP8192_AUDIT_R4_METADATA_STOP.json',read(T/'analysis/TELEMETRY_CAP8192_AUDIT_R4_METADATA_STOP.json'));write(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 for n,revision in enumerate(['R2','R3','R4']):write(root/'control'/('CONTROLLER_LAUNCH_'+revision+'.json'),{'pid':999999990+n,'start_ticks':1})
 for cell,row in q['consumed'].items():
  write(root/'analysis'/(cell+'.RESULT.json'),read(T/'analysis'/(cell+'.RESULT.json')))
  link=root/'control/qualification_ledger'/(cell+'.INTENT.json');link.parent.mkdir(parents=True,exist_ok=True);link.symlink_to(T/'control/qualification_ledger'/(cell+'.INTENT.json'))
  receipt=T/'control'/(cell+'_ARCHIVE_RECEIPT.json')
  if receipt.exists():(root/'control'/receipt.name).symlink_to(receipt)
  original=T/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json')
  if original.exists():link=root/'DTC/control'/original.name;link.parent.mkdir(parents=True,exist_ok=True);link.symlink_to(original)
 entry=m.N/'bin/native';entry.parent.mkdir(parents=True);entry.write_text('ASSET_ROUTE_COPY_ONLY_UNCHANGED\nexec python '+str(root/'tools/sweep_frontend.py')+' "$@"\n');entry.chmod(0o755);oldentry=entry.read_bytes()
 # Exact source publication mismatch fails before reading/adopting old points.
 goodpub=read(root/'control/CAP1M_FRAMEWORK_PUBLICATION_READBACK.json');write(root/'control/CAP1M_FRAMEWORK_PUBLICATION_READBACK.json',dict(goodpub,commit='0'*40));native=NativeFixture()
 try:m.adopt(native,{'fixture':True})
 except AssertionError as e:test('wrong_Framework_publication_is_denied_before_authority_changes','exact Framework source publication missing' in str(e) and native.updates==0)
 else:raise AssertionError('wrong source publication accepted')
 write(root/'control/CAP1M_FRAMEWORK_PUBLICATION_READBACK.json',goodpub)
 pid=os.getpid();ticks=int((P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19]);write(root/'control/CONTROLLER_LAUNCH_R2.json',{'pid':pid,'start_ticks':ticks});native=NativeFixture()
 try:m.adopt(native,{'fixture':True})
 except AssertionError as e:test('live_prior_generation_is_denied_before_adoption','prior controller generation still live' in str(e) and native.updates==0)
 else:raise AssertionError('live prior generation accepted')
 write(root/'control/CONTROLLER_LAUNCH_R2.json',{'pid':999999990,'start_ticks':1});native=NativeFixture();del native.reg['registered_future_requests'][REQ]['consumed'][next(iter(q['consumed']))]['execution_receipt']
 try:m.adopt(native,{'fixture':True})
 except AssertionError as e:test('unclosed_spent_native_attempt_is_denied_before_mutation','unclosed spent native attempt' in str(e) and native.updates==0)
 else:raise AssertionError('unclosed old point accepted')
 native=NativeFixture();recovered=m.adopt(native,{'fixture_only_no_real_model':True});after=native.reg['registered_future_requests'][REQ]
 test('positive_full105_adoption_preserves_all_spent_UUID_DONE_and_credit',len(recovered)==105 and after['consumed']==q['consumed'] and after['remaining']==q['remaining']==251 and after['budget']==356 and native.updates==1)
 test('positive_full105_adoption_retains102PASS_and3explicit_failed_without_cycles',sum(r['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE' for r in recovered.values())==102 and sum(r['state']=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY' and r['accepted_cycles'] is None for r in recovered.values())==3)
 test('positive_adoption_keeps_original_authority_spec_and_peer_fields',all(after[k]==v for k,v in q.items() if k not in ['orchestrator_sha256','operational_continuations','operational_engine_profiles','effective_specs']) and all(native.reg['registered_future_requests'][k]==v for k,v in actual['registered_future_requests'].items() if k!=REQ))
 test('positive_profile_is_exact_candidate_with_correct_source_and_activation_prefix',after['operational_engine_profiles'][ID]['candidate_sha256']==sha(root/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json') and after['operational_engine_profiles'][ID]['activation_prior_consumed']==105 and after['operational_engine_profiles'][ID]['framework_commit']==candidate['framework_commit'] and not after['effective_specs'])
 test('positive_frontend_change_only_rebinds_exact_original_matrix_route',entry.read_bytes()==oldentry.replace(str(root/'tools/sweep_frontend.py').encode(),str(root/'tools/sweep_frontend_cap1m.py').encode()))
 test('all_three_issue_preimages_preserved_and_no_new_INTENT_or_START',len(list((root/'analysis/issue_preimages').glob('*.R2.json')))==3 and len(list((root/'control/qualification_ledger').glob('*.INTENT.json')))==105 and not (root/'control/CONTROLLER_START_R5.json').exists())
test('real_science_authority_epoch_and_native_entry_never_changed',before=={str(p):sha(p) for p in paths})
component=read(T/'control/CONTINUATION_R5_COMPONENT_QUALIFICATION.json');assert component['candidate_sha256']==sha(T/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json') and component['engine_sha256']==candidate['engine_sha256'] and component['strict_sha256']==candidate['strict_sha256']
proof=dict(component,controller_sha256=current_sha,test_count=len(component['tests'])+len(tests),tests=component['tests']+tests,component_qualification_sha256=sha(T/'control/CONTINUATION_R5_COMPONENT_QUALIFICATION.json'),additional_adoption_tests=len(tests),fixture_provenance='20unchanged-runtime/spec/strict component checks plus fresh exact-source publication/live-generation/unclosed-point negatives and full105old-point isolated positive adoption. Publication/authority/entry fixture only;real old raw/archive/restore evidence read only. No simulator or live authority mutation.',new_simulator_executed=False,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
master=T/'control/CONTINUATION_R5_ZERO_MODEL_QUALIFICATION.json';pre=T/'control/draft_preimages/R5_ZERO_QUAL_BEFORE_FULL_ADOPTION.json';assert not pre.exists();shutil.copyfile(master,pre);temp=master.with_suffix('.writing');write(temp,proof);os.replace(temp,master)
print(json.dumps({k:v for k,v in proof.items() if k not in ['source_pins','tests']},indent=2))
