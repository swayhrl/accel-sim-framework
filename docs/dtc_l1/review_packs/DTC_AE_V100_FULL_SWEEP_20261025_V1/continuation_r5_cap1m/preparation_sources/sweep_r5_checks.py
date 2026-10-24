import pathlib,json,hashlib,importlib.util,tempfile,copy,ast,sys,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1';ID='OBSERVABILITY_CAP1M_WALL90_V1';tests=[]
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True,indent=2)+chr(10))
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def test(name,v):assert v,name;tests.append({'test':name,'status':'PASS'})
candidate=read(T/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json');prep=read(T/'control/CONTINUATION_R5_PREPARATION.json');engine=load('isolated_r5_engine_checks',T/'tools/sweep_native_cap1m.py');specs=load('isolated_r5_spec_checks',T/'tools/sweep_cap1m_specs.py')
realreg,epoch=engine.read_current_authority();q=realreg['registered_future_requests'][REQ];before_paths=[N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json',N/'control/CURRENT_SCIENCE_EPOCH.json',N/'bin/native',T/'tools/sweep_native.py',T/'tools/sweep_strict.py'];before={str(p):sha(p) for p in before_paths}
test('all_current105_spent_are_closed_no_old_model_can_be_restarted',len(q['consumed'])==105 and all('execution_receipt' in r for r in q['consumed'].values()))
test('new_runtime_sources_match_frozen_candidate',all(sha(r['path'])==r['sha256'] for r in candidate['source_pins']))
for p in [T/'tools/revision5/sweep_controller.py',*[P(r['path']) for r in candidate['source_pins'] if r['path'].endswith('.py')]]:ast.parse(p.read_text())
test('all_new_production_sources_syntax',True)
def function_ast(file,name):return ast.dump(next(n for n in ast.parse(P(file).read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
test('scientific_population_conservation_parser_is_exact_unchanged_source',function_ast(T/'tools/sweep_strict.py','population')==function_ast(T/'tools/sweep_strict_cap1m.py','population'))
key='b41cc74c66ca6ed4';cells=[c for c in q['admitted_specs'] if c.startswith('E2-AEV100-'+key+'-')];assert len(cells)==4
with tempfile.TemporaryDirectory(prefix='r5-isolated-spec-',dir=T/'analysis') as tmp:
 root=P(tmp);(root/'control').mkdir();(root/'tools').mkdir();(root/'tools/sweep_native.py').symlink_to(T/'tools/sweep_native.py');(root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json').symlink_to(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 for c in cells:(root/'control'/(c+'_SPEC.json')).symlink_to(T/'control'/(c+'_SPEC.json'))
 fake=copy.deepcopy(candidate);path=root/'telemetry_v2/framework-build/accel-sim.out';path.parent.mkdir(parents=True);path.symlink_to(P(candidate['framework_binary']['path']));fake['framework_binary']['path']=str(path)
 write(root/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json',fake);fq=copy.deepcopy(q);fq['operational_engine_profiles']={ID:dict(fake,status='DECLARED_ISOLATED_TEST_PROFILE',candidate_sha256=sha(root/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json'))};fq['effective_specs']={}
 class FixtureNative:
  def read_current_authority(self):return {'registered_future_requests':{REQ:copy.deepcopy(fq)}},copy.deepcopy(epoch)
  def update_authority(self,fn):reg={'registered_future_requests':{REQ:fq}};fn(reg)
  def registered_profile(self,row):return engine.registered_profile(row)
  def spec_for(self,c):return engine.spec_for(c)
 native=FixtureNative();engine.ROOT=root;engine.read_current_authority=native.read_current_authority;specs.T=root;sys.modules['sweep_cap1m_specs']=specs
 result={'state':'ADMITTED_FULL_INPUT','cells':cells,'input_digest':read(T/'control'/(cells[0]+'_SPEC.json'))['input_digest']};original_fq=copy.deepcopy(fq);specs.register_input(result,native)
 expected={c for c in cells if c not in q['consumed']};test('effective_spec_registration_skips_all_previously_spent_cells',set(fq['effective_specs'])==expected and len(expected)==2)
 test('effective_registration_preserves_original_admitted_specs_consumed_and_budget',fq['admitted_specs']==q['admitted_specs'] and fq['consumed']==q['consumed'] and fq['remaining']==q['remaining'] and fq['budget']==356)
 for c in expected:
  original=read(T/'control'/(c+'_SPEC.json'));effective=engine.spec_for(c);test('derived_'+c[-2:]+'_keeps_exact_whole_input_config_options_and_CPU',effective['expected']==original['expected'] and effective['configs']==original['configs'] and effective['expected_options']==original['expected_options'] and effective['input_binding_sha256']==original['input_binding_sha256'] and effective['host_cpu']==original['host_cpu'] and effective['limits']==original['limits'] and effective['core_commit']==original['core_commit'])
  test('derived_'+c[-2:]+'_changes_only_observational_binary_and_Framework_identity',effective['framework_commit']==candidate['framework_commit'] and effective['binary_sha256']==candidate['framework_binary']['sha256'] and effective['native_simulator_argv'][1:]==original['native_simulator_argv'][1:] and effective['operational_runtime_profile']==ID)
 cell=sorted(expected)[0];specfile=root/'control/effective_specs'/(cell+'.json');saved=specfile.read_bytes();entry=copy.deepcopy(fq['effective_specs'][cell]);tampered=read(specfile);tampered['host_cpu']+=1;write(specfile,tampered);fq['effective_specs'][cell]['sha256']=sha(specfile)
 try:engine.spec_for(cell)
 except RuntimeError as e:test('even_consistently_rehashed_performance_or_CPU_change_is_rejected','outside allowed observational runtime fields' in str(e))
 else:raise AssertionError('changed CPU accepted')
 specfile.write_bytes(saved);fq['effective_specs'][cell]=entry
 fq['effective_specs'][cell]['path']='/tmp/arbitrary.json'
 try:engine.spec_for(cell)
 except RuntimeError:test('effective_spec_cannot_select_unregistered_external_path',True)
 else:raise AssertionError('arbitrary spec path accepted')
 fq['effective_specs'][cell]=entry;oldhash=fq['admitted_specs'][cell];fq['admitted_specs'][cell]='0'*64
 try:engine.spec_for(cell)
 except RuntimeError:test('original_preregistered_spec_remains_a_required_binding',True)
 else:raise AssertionError('original spec binding bypassed')
 fq['admitted_specs'][cell]=oldhash
 oldprofile=copy.deepcopy(fq['operational_engine_profiles'][ID]);fq['operational_engine_profiles'][ID]['max_records']=1048577
 try:engine.registered_profile(fq)
 except RuntimeError:test('profile_record_bound_cannot_be_changed_after_candidate_binding',True)
 else:raise AssertionError('changed bound accepted')
 fq['operational_engine_profiles'][ID]=oldprofile
 # Restore imported helper globals before later read-only checks.
 specs.T=T
sys.modules.pop('sweep_cap1m_specs',None)
strict=load('new_scientific_dispatch_read_only_checks',T/'tools/sweep_strict_cap1m.py');nn=next(c for c,r in q['consumed'].items() if read(T/'control'/(c+'_SPEC.json'))['program']=='nn' and read(T/'analysis'/(c+'.RESULT.json'))['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE');intent=read(T/'control/qualification_ledger'/(nn+'.INTENT.json'));test('old_accepted_point_replays_through_unchanged_original_strict_dispatch',strict.terminal(nn)==read(P(intent['output'])/'AEFAIR_STRICT.json'))
guard=load('new_cap1m_guard_constructor_checks',T/'tools/sweep_guard_cap1m.py');test('all_nonconstructor_guard_methods_are_inherited_exactly',all(getattr(guard.NativeDTCGuard,k) is getattr(guard.original.NativeDTCGuard,k) for k in ['drain','sample','quick_stop']))
failure=load('new_closed_failure_classification_checks',T/'tools/sweep_failure_review_cap1m.py');failed=['E2-AEV100-1df9d5479504d9c7-DM','E2-AEV100-977e34578994c3d2-CH','E2-AEV100-977e34578994c3d2-DM'];classifications=[failure.classify(c) for c in failed];test('all_three_failed_spent_points_are_full_SHA_verified_without_cycles',len(classifications)==3 and all(r['scientific_acceptance'] is False and r['accepted_cycles'] is None and r['model_retries']==0 for r in classifications))
controller=(T/'tools/revision5/sweep_controller.py').read_text();test('first_new_Goal_point_gates_pool_ramp_without_extra_canary',"target=1;old_consumed=set(recovered)" in controller and "target=ceiling if new_passed>=1 else 1" in controller)
test('spent_cells_still_excluded_before_dispatch',"cell in results or cell in q['consumed']" in controller and 'spent cell cannot be restarted' in controller)
afterreg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');test('live_science_authority_epoch_entry_and_old_source_bytes_unchanged',before=={str(p):sha(p) for p in before_paths})
proof={'status':'PASS','test_count':len(tests),'tests':tests,'controller_sha256':sha(T/'tools/revision5/sweep_controller.py'),'candidate_sha256':sha(T/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json'),'engine_sha256':candidate['engine_sha256'],'strict_sha256':candidate['strict_sha256'],'source_pins':candidate['source_pins'],'fixture_provenance':'Effective-spec/authority fixtures in an absent native temp directory only;real old accepted/failed evidence read only. No new model or production authority mutation.','scientific_starts':0,'old_attempt_retries':0,'new_simulator_executed':False,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (T/'control/CONTINUATION_R5_ZERO_MODEL_QUALIFICATION.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
print(json.dumps({k:v for k,v in proof.items() if k!='source_pins'},indent=2))
