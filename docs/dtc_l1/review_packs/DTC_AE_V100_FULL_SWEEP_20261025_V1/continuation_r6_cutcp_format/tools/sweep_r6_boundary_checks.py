import pathlib,json,hashlib,importlib.util,tempfile,copy,types,os,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1';KEY='af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8';tests=[]
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+chr(10))
def test(name,v):assert v,name;tests.append({'test':name,'status':'PASS'})
controller=T/'tools/revision6/sweep_controller.py';s=importlib.util.spec_from_file_location('isolated_R6_boundary_transition',controller);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
actual=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');originalq=actual['registered_future_requests'][REQ];candidate=read(T/'control/CUTCP_FORMAT_ADMISSION_CANDIDATE.json');paths=[N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json',N/'control/CURRENT_SCIENCE_EPOCH.json',N/'bin/native',T/'qualification'/KEY/'QUALIFICATION.json'];before={str(p):sha(p) for p in paths}
q=copy.deepcopy(originalq);allcells={c for row in q['admitted_inputs'].values() for c in row['specs']};assert len(allcells)==284
q['consumed']={c:{'uuid':'DECLARED_SYNTHETIC_PHASE_CLOSED_'+c,'execution_receipt':{'fixture_only':True}} for c in allcells};q['state']='ALL_STARTS_CLOSED_PENDING_COMPLETE_SCIENTIFIC_DELIVERY';q['remaining']=0;q['sealed']=sorted(set(q['candidate_cohorts'])-allcells);q['sealed_unused']=len(q['sealed']);q['input_holds']=copy.deepcopy(read(T/'analysis/BATCH_STATE.json')['input_holds']);assert len(q['sealed'])==72 and KEY in q['input_holds']
class NativeFixture:
 def __init__(self):self.reg={'registered_future_requests':{REQ:copy.deepcopy(q)}};self.updates=0
 def read_current_authority(self):return copy.deepcopy(self.reg),{'epoch':2}
 def update_authority(self,fn):fn(self.reg);self.updates+=1
with tempfile.TemporaryDirectory(prefix='R6-unspent-boundary-',dir=T/'analysis') as tmp:
 root=P(tmp);m.T=root;(root/'control').mkdir();(root/'analysis').mkdir()
 for name in ['CUTCP_FORMAT_ADMISSION_CANDIDATE.json','CUTCP_FORMAT_ADJUDICATION_PUBLICATION_READBACK.json','SCIENCE_AUTHORIZATION.json']:write(root/'control'/name,read(T/'control'/name))
 original=root/'qualification'/KEY/'QUALIFICATION.json';original.parent.mkdir(parents=True);original.symlink_to(T/'qualification'/KEY/'QUALIFICATION.json')
 write(root/'control/CONTINUATION_R6_PUBLICATION_READBACK.json',{'verified':True,'controller_sha256':sha(controller),'admission_candidate_sha256':sha(root/'control/CUTCP_FORMAT_ADMISSION_CANDIDATE.json'),'commit':'DECLARED_SYNTHETIC_R6_PUBLICATION_FOR_BOUNDARY_UNIT_ONLY'})
 write(root/'control/CONTINUATION_R6_ZERO_MODEL_QUALIFICATION.json',{'status':'PASS','controller_sha256':sha(controller),'fixture_only':True});write(root/'control/CONTROLLER_LAUNCH_R5.json',{'pid':999999999,'start_ticks':1});write(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 phase={'state':'ALL_APPLICABLE_NATIVE_ATTEMPTS_CLOSED_ARCHIVED_RESTORED_WITH_CLASSIFIED_FAILURES','closed_point_results':len(allcells),'input_holds':q['input_holds'],'fixture_provenance':'Declared synthetic complete-phase metadata;not native model results'};write(root/'analysis/BATCH_NATIVE_CLOSED.json',phase);write(root/'analysis/BODY_QUALIFICATION_PROGRESS.json',read(T/'analysis/BODY_QUALIFICATION_PROGRESS.json'))
 for c,row in q['consumed'].items():write(root/'analysis'/(c+'.RESULT.json'),{'cohort':c,'uuid':row['uuid'],'state':'PASS_STRICT_ARCHIVE_NATIVE_RESTORE','fixture_only':True})
 calls=[]
 def checked_module(name,file):
  if file=='sweep_admission_cutcp_reviewed.py':return types.SimpleNamespace(admit=lambda key,native:(calls.append(('reviewed_admit',key)) or {'state':'ADMITTED_FULL_INPUT','cells':list(m.CELLS)}))
  if file=='sweep_cap1m_specs.py':return types.SimpleNamespace(register_input=lambda result,native:calls.append(('unchanged_effective_spec_derivation',set(result['cells']))))
  raise AssertionError(file)
 m.module=checked_module
 pid=os.getpid();ticks=int((P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19]);write(root/'control/CONTROLLER_LAUNCH_R5.json',{'pid':pid,'start_ticks':ticks});native=NativeFixture()
 try:m.activate(native,{'fixture':True})
 except AssertionError as e:test('live_R5_generation_cannot_be_replaced','R5 generation still live' in str(e) and native.updates==0)
 else:raise AssertionError('live R5 accepted')
 write(root/'control/CONTROLLER_LAUNCH_R5.json',{'pid':999999999,'start_ticks':1});native=NativeFixture();del native.reg['registered_future_requests'][REQ]['consumed'][next(iter(allcells))]
 try:m.activate(native,{'fixture':True})
 except AssertionError as e:test('incomplete_prior_full_matrix_cannot_open_followup','prior phase matrix coverage incomplete' in str(e) and native.updates==0)
 else:raise AssertionError('incomplete phase accepted')
 native=NativeFixture();native.reg['registered_future_requests'][REQ]['consumed'][m.CELLS[0]]={'uuid':'FALSE_PREVIOUSLY_SPENT','execution_receipt':{}}
 try:m.activate(native,{'fixture':True})
 except AssertionError:test('any_previously_spent_Cutcp_cell_is_denied',native.updates==0)
 else:raise AssertionError('spent candidate accepted')
 native=NativeFixture();native.reg['registered_future_requests'][REQ]['budget']=357
 try:m.activate(native,{'fixture':True})
 except AssertionError:test('original_budget_cannot_expand',native.updates==0)
 else:raise AssertionError('expanded budget accepted')
 native=NativeFixture();prior,record=m.activate(native,{'fixture_only':True});after=native.reg['registered_future_requests'][REQ]
 test('positive_transition_releases_only_four_never_consumed_slots',after['remaining']==4 and set(after['sealed'])==set(q['sealed'])-set(m.CELLS) and len(after['sealed'])==68 and after['budget']==356)
 test('all_prior_spent_UUIDs_receipts_and_specs_unchanged',after['consumed']==q['consumed'] and after['admitted_specs']==q['admitted_specs'] and after['effective_specs']==q['effective_specs'])
 test('source_HOLD_and_sealing_snapshot_is_preserved',read(root/'control/phase_closures/R5_AUTHORITY_BEFORE_CUTCP.json')==q and read(root/'control/phase_closures/R5_NATIVE_CLOSED_BEFORE_CUTCP.json')==phase and record['old_input_holds']==q['input_holds'] and KEY not in after['input_holds'])
 test('same_total_original_budget_partition_retained',len(after['consumed'])+len(after['sealed'])+after['remaining']==356)
 test('exact_review_producer_and_existing_runtime_deriver_are_selected',calls==[('reviewed_admit',KEY),('unchanged_effective_spec_derivation',set(m.CELLS))])
 test('no_new_INTENT_or_model_fork_in_boundary_transition',not (root/'control/qualification_ledger').exists() and not (root/'control/CONTROLLER_START_R6.json').exists())
test('real_authority_epoch_entry_and_original_HOLD_unchanged',before=={str(P(p)):sha(P(p)) for p in before})
proof={'status':'PASS','test_count':len(tests),'tests':tests,'controller_sha256':sha(controller),'admission_candidate_sha256':sha(T/'control/CUTCP_FORMAT_ADMISSION_CANDIDATE.json'),'reviewed_producer_sha256':candidate['producer_sha256'],'producer_component_qualification_sha256':sha(T/'control/CUTCP_FORMAT_PRODUCER_ZERO_MODEL_QUALIFICATION.json'),'fixture_provenance':'Synthetic closed284point phase metadata and publication/authority in absent temp root;reviewed producer/effective derivation selection are stubs here and independently covered by12producer plus existing R5effective-spec checks. No synthetic point is a native result.','new_model_starts':0,'old_model_retries':0,'production_authority_or_HOLD_mutated':False,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (T/'control/CONTINUATION_R6_ZERO_MODEL_QUALIFICATION.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
print(json.dumps(proof,indent=2))
