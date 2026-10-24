import pathlib,json,hashlib,importlib.util,tempfile,copy,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');KEY='af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8';REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1';tests=[]
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def test(name,v):assert v,name;tests.append({'test':name,'status':'PASS'})
candidate=read(T/'control/CUTCP_FORMAT_ADMISSION_CANDIDATE.json');origQ=T/'qualification'/KEY/'QUALIFICATION.json';oldsha=sha(origQ);actual=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');q=actual['registered_future_requests'][REQ];before={str(p):sha(p) for p in [N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json',N/'control/CURRENT_SCIENCE_EPOCH.json',N/'bin/native',origQ]}
s=importlib.util.spec_from_file_location('one_input_reviewed_source_producer',T/'tools/sweep_admission_cutcp_reviewed.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='cutcp-reviewed-admission-',dir=T/'analysis') as tmp:
 root=P(tmp);m.T=root;(root/'control').mkdir();(root/'control/input_bindings').mkdir();(root/'tools').mkdir();(root/'DTC').mkdir()
 for name in ['INTAKE_CANDIDATES.json','HOST_CALIBRATION.json','FOUR_ARM_GOLDEN_TEMPLATES.json']:(root/'control'/name).symlink_to(T/'control'/name)
 (root/'tools/body_audit_ratebound.py').symlink_to(T/'tools/body_audit_ratebound.py');(root/'DTC/env').symlink_to(T/'DTC/env');(root/'DTC/bin').symlink_to(T/'DTC/bin');(root/'common-lib').symlink_to(T/'common-lib');link=root/'qualification'/KEY/'QUALIFICATION.json';link.parent.mkdir(parents=True);link.symlink_to(origQ)
 fq=copy.deepcopy(q);fq['format_adjudications']={KEY:copy.deepcopy(candidate)}
 class NativeFixture:
  def read_current_authority(self):return {'registered_future_requests':{REQ:copy.deepcopy(fq)}},{'epoch':2}
  def update_authority(self,fn):fn({'registered_future_requests':{REQ:fq}})
 native=NativeFixture()
 try:m.admit('0'*64,native)
 except AssertionError:test('reviewed_producer_cannot_apply_to_another_input',True)
 else:raise AssertionError('unlisted input accepted')
 old=fq['format_adjudications'][KEY]['review_sha256'];fq['format_adjudications'][KEY]['review_sha256']='0'*64
 try:m.admit(KEY,native)
 except AssertionError:test('changed_review_SHA_is_denied_before_spec_creation',not list((root/'control').glob('*_SPEC.json')))
 else:raise AssertionError('changed review accepted')
 fq['format_adjudications'][KEY]['review_sha256']=old
 result=m.admit(KEY,native);test('explicit_review_produces_exact_four_original_cells',result['state']=='ADMITTED_FULL_INPUT' and set(result['cells'])==set(candidate['original_never_spent_cells']))
 test('original_spent_UUIDs_budget_and_credit_unchanged',fq['consumed']==q['consumed'] and fq['remaining']==q['remaining'] and fq['budget']==q['budget']==356)
 test('original_existing_spec_bindings_unchanged',all(fq['admitted_specs'][c]==h for c,h in q['admitted_specs'].items()))
 binding=read(root/'control/input_bindings'/(KEY+'.json'));test('new_binding_uses_separate_qualified_input_with_original_HOLD_provenance',binding['qualification_source_sha256']==candidate['qualified_input_sha256'] and binding['qualification']['explicit_current_source_format_adjudication']['original_qualification_sha256']==oldsha and binding['qualification']['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS')
 original=read(origQ)
 for cell in result['cells']:
  spec=read(root/'control'/(cell+'_SPEC.json'));arm=cell.rsplit('-',1)[1];golden=read(T/'control/FOUR_ARM_GOLDEN_TEMPLATES.json')[arm]
  test('original_'+arm+'_config_family_and_full_populations_preserved',spec['expected']=={'instructions':original['expected_instructions'],'CTA':original['expected_CTA'],'kernels':11} and [r['sha256'] for r in spec['configs']]==[sha(T/'DTC/env'/arm/('config-'+str(i)+'.config')) for i in range(4)] and spec['expected_options']['-trace']==[original['trace_entry']])
 test('metadata_only_no_new_INTENT_or_replay',not (root/'control/qualification_ledger').exists())
test('real_original_HOLD_authority_epoch_entry_unchanged',before=={str(P(p)):sha(P(p)) for p in before})
result={'status':'PASS_METADATA_ONLY_REVIEWED_CUTCP_PRODUCER','test_count':len(tests),'tests':tests,'producer_sha256':sha(T/'tools/sweep_admission_cutcp_reviewed.py'),'candidate_sha256':sha(T/'control/CUTCP_FORMAT_ADMISSION_CANDIDATE.json'),'explicit_adjudication_sha256':candidate['adjudication_sha256'],'new_model_starts':0,'old_model_retries':0,'production_authority_or_HOLD_mutated':False,'fixture_scope':'One-input admission/authority/spec files in absent isolated native temp root;no simulator or production registration.','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (T/'control/CUTCP_FORMAT_PRODUCER_ZERO_MODEL_QUALIFICATION.json').open('x') as f:json.dump(result,f,indent=2);f.write(chr(10))
print(json.dumps(result,indent=2))
