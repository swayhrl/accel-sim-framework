import pathlib,json,hashlib,importlib.util,copy,types,ast,datetime,sys
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');tests=[]
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def test(name,fn):fn();tests.append({'test':name,'status':'PASS'})
def truth(x):assert x
candidate=read(T/'control/WALL90_PROFILE_CANDIDATE.json');old_path=P(candidate['original_policy_source']);old=load('untouched_policy_for_wall_contract',old_path);new=load('new_wall90_policy_contract',T/'tools/runtime_policy_wall90_v1.py')
test('exact_policy_source_difference_is_three_wall_tokens_only',lambda:truth(old_path.read_text().replace('21600','7776000')==(T/'tools/runtime_policy_wall90_v1.py').read_text() and old_path.read_text().count('21600')==3))
test('all_non_wall_profile_bounds_identical',lambda:truth({k:v for k,v in old.PROFILE.items() if k!='wall_deadline_s'}=={k:v for k,v in new.PROFILE.items() if k!='wall_deadline_s'} and new.PROFILE['wall_deadline_s']==7776000))
class Domain:
 def __init__(self):self.reason=None
 def observe(self,*args):return {'decision':'STOP' if self.reason else 'CONTINUE','stop_reasons':[self.reason] if self.reason else [],'warnings':[]}
class Runtime:
 def __init__(self,baseline,output):self.first=baseline;self.host=Domain();self.cgroup=Domain()
 def _project(self,sample):return sample
 def quick_stop(self):return None
resource=types.SimpleNamespace(Runtime=Runtime);start=10**9
baseline={'monotonic_ns':start,'disk_free_bytes':32*new.GIB,'output_filesystem_device':2128,'host_oom_kill':0,'pressure':{'io':{'full':{'avg10':0.0}}},'cgroup_pressure_parsed':{'io':{'full':{'avg10':0.0}}}}
safety={k:True for k in new.SAFETY_KEYS};impact={'known_scope':True,'harm_detected':False,'conservative_host_episode_profile_accepted':True}
def make(module):return module.RuntimePolicyB(copy.deepcopy(baseline),T,resource_module=resource,started_ns=start,opt_in=True)
def observe(r,seconds,completed=None,modify=None):
 sample=copy.deepcopy(baseline);sample['monotonic_ns']=start+seconds*10**9;progress={'mono_ns':sample['monotonic_ns'],'completed':seconds if completed is None else completed,'end':'NONE'};safe=dict(safety)
 if modify:modify(sample,progress,safe)
 return r.observe(sample,0,0,progress=progress,safety_checks=safe,io_impact=impact)
a=make(old);b=make(new);equal=True
for seconds in range(10,21600,10):
 x=observe(a,seconds);y=observe(b,seconds);x.pop('profile');y.pop('profile');equal=equal and x==y and y['decision']=='CONTINUE'
test('2159_synthetic_samples_before6h_have_identical_decisions',lambda:truth(equal))
at_old=observe(a,21600);at_new=observe(b,21600)
test('old6h_stop_preserved_and_new6h_continues_with_fresh_retirement',lambda:truth(at_old['stop_reasons']==['WALL_DEADLINE_21600S'] and at_new['decision']=='CONTINUE'))
test('new_continues_after6h_not_just_at_boundary',lambda:truth(observe(b,21610)['decision']=='CONTINUE'))
c=make(new);c.last_ns=start+(7776000-10)*10**9;c.last_retired_ns=c.last_ns;c.completed=7775990;c.last_producer_ns=c.last_ns
test('new90day_boundary_stops_not_unbounded',lambda:truth(observe(c,7776000)['stop_reasons']==['WALL_DEADLINE_7776000S']))
test('cadence_above30s_still_stops',lambda:truth('INVALID_OR_MISSING_RESOURCE_SAMPLE_CADENCE' in observe(make(new),31)['stop_reasons']))
test('stale_producer_still_stops',lambda:truth('STALE_OR_FUTURE_PRODUCER' in observe(make(new),10,modify=lambda s,p,g:p.update(mono_ns=s['monotonic_ns']-31*10**9))['stop_reasons']))
d=make(new)
for seconds in range(10,601,10):no_retire=observe(d,seconds,completed=0)
test('600s_without_semantic_retirement_still_stops',lambda:truth('NO_SEMANTIC_RETIREMENT_600S' in no_retire['stop_reasons']))
test('new_host_OOM_still_stops',lambda:truth('NEW_HOST_OOM_KILL' in observe(make(new),10,modify=lambda s,p,g:s.update(host_oom_kill=1))['stop_reasons']))
test('5GiB_floor_still_stops',lambda:truth('USER_OUTPUT_FILESYSTEM_AT_OR_BELOW_5GiB' in observe(make(new),10,modify=lambda s,p,g:s.update(disk_free_bytes=5*new.GIB))['stop_reasons']))
test('wrong_output_device_still_stops',lambda:truth('V2_OUTPUT_FILESYSTEM_CHANGED' in observe(make(new),10,modify=lambda s,p,g:s.update(output_filesystem_device=1))['stop_reasons']))
test('ownership_evidence_still_required',lambda:truth('CURRENT_GUARD:ownership' in observe(make(new),10,modify=lambda s,p,g:g.update(ownership=False))['stop_reasons']))
e=make(new);e.original.cgroup.reason='SYNTHETIC_UNCHANGED_CGROUP_MEMORY_STOP'
test('original_cgroup_stop_propagates',lambda:truth('cgroup:SYNTHETIC_UNCHANGED_CGROUP_MEMORY_STOP' in observe(e,10)['stop_reasons']))
sys.path.insert(0,str(T/'tools'));guard=load('qualified_wall90_guard_contract',T/'tools/sweep_storage_guard_wall90_v1.py');engine=load('qualified_wall90_engine_contract',T/'tools/sweep_native_wall90_v1.py')
test('receiver_drain_sample_quickstop_methods_inherited_exactly',lambda:truth(all(getattr(guard.NativeDTCGuard,k) is getattr(guard.original.NativeDTCGuard,k) for k in ['drain','sample','quick_stop'])))
test('engine_profile_validates_without_live_authority_mutation',lambda:truth(engine.operational_wall_profile({'operational_engine_profiles':{'WALL90_V1':candidate}})==candidate))
def reject_profile(name,modify):
 p=copy.deepcopy(candidate);modify(p)
 try:engine.operational_wall_profile({'operational_engine_profiles':{'WALL90_V1':p}})
 except RuntimeError:tests.append({'test':name,'status':'PASS'})
 else:raise AssertionError(name)
reject_profile('changed_engine_SHA_denied',lambda p:p.update(engine_sha256='0'*64));reject_profile('arbitrary_wall_bound_denied',lambda p:p.update(wall_deadline_seconds=0));reject_profile('extra_source_membership_denied',lambda p:p['source_pins'].append({'name':'arbitrary.py','sha256':'0'*64}));reject_profile('budget_expansion_denied',lambda p:p.update(finite_budget=357))
test('original_launcher_policy_and_guard_sources_preserved',lambda:truth(sha(T/'tools/sweep_native.py')==candidate['original_engine_sha256'] and sha(old_path)==candidate['original_policy_sha256']))
proof={'status':'PASS','test_count':len(tests),'tests':tests,'source_pins':candidate['source_pins'],'engine_sha256':candidate['engine_sha256'],'clock_provenance':'DECLARED_SYNTHETIC_RESOURCE_AND_MONOTONIC_TIME_FIXTURES;actual native guard always uses actual clocks. No altered runtime receipt is a scientific result.','scientific_starts':0,'actual_guard_process_starts':0,'live_authority_or_native_entry_changed':False,'existing_models_changed':False,'policy_delta':'three wall tokens only;all non-wall policy source identical','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (T/'control/WALL90_ZERO_MODEL_QUALIFICATION.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
print(json.dumps(proof,indent=2))
