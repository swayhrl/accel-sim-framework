import pathlib,json,importlib.util,copy,io,gzip,types
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
v=load('R12_override_independent_fixture',T/'tools/sweep_live_ram_override_provenance_v1.py');p=load('R12_override_payload_fixture',T/'tools/sweep_live_ram_override_v1.py');checks=[]
expected={'cohort':'fixture','uuid':'fixtureUUID','frontend_pid':123,'frontend_start_ticks':456,'model_pid':789,'model_start_ticks':987,'patch_monotonic_ns':10}
certificate={'patch_source_sha256':v.sha(p.__file__),'plan_sha256':'fixturePlan'}
sample={'sample_begin_monotonic_ns':20,'sample_end_monotonic_ns':21,'utc':'fixture','frontend_pid':123,'frontend_start_ticks':456,'host_MemAvailable_bytes':64*G,'cgroup_memory_max':str(256*G),'cgroup_memory_current':240*G,'cgroup_memory_stat_for_credit':{'file':40*G,'inactive_file':40*G,'shmem':0,'file_mapped':0,'file_dirty':0,'file_writeback':0},'cgroup_reclaimable_clean_inactive_file_credit_bytes':32*G,'cgroup_effective_headroom_bytes':48*G}
profile={'profile_id':p.PROFILE,'plan_sha256':certificate['plan_sha256'],'patch_source_sha256':certificate['patch_source_sha256'],'targets':{'fixture':expected}}
authority=lambda:({'registered_future_requests':{'DTC_AE_V100_FULL_SWEEP_20261025_V1':{'live_RAM_guard_override_profile':profile}}},None)
original={'physical_RAM_pass':False,'physical_disk_pass':True,'old_counter':{'exact':'preserved'},'reserved_additional_live_and_candidate_RAM_bytes':300*G}
fn=p.make_wrapper(lambda *a:copy.deepcopy(original),authority,expected,certificate['plan_sha256'],certificate['patch_source_sha256'],sampler=lambda:copy.deepcopy(sample));row=fn({},False);proof=v.verify_override_sample(row,expected,certificate)
assert proof['effective_physical_RAM_pass'] is True and proof['prior_physical_RAM_pass'] is False and {k:val for k,val in row.items() if k!='live_RAM_guard_override' and k!='physical_RAM_pass'}=={k:val for k,val in original.items() if k!='physical_RAM_pass'};checks.append('payload_and_independent_actual64G48G_boundary_and_old_dictionary_preservation')
assert p.code_identity(fn)['code_sha256']==v.nested_resource_code_sha(p.__file__);checks.append('replacement_runtime_code_SHA_reconstructed_without_executing_compiled_source')
fingerprint=v.stable_code_sha(fn.__code__)
for _ in range(100):fn({},False)
assert fingerprint==v.stable_code_sha(fn.__code__)==p.code_fingerprint(fn.__code__);checks.append('structural_code_fingerprint_stable_across100_runtime_calls')
code=compile("def fixture(a=None):\n return (None, Ellipsis, True, 10, 1.5, 2+3j, b'x', 'unicode\\u03b1', frozenset({1,2}), (1,2))\n",'/fixture/typed_code.py','exec');assert v.stable_code_sha(code)==p.code_fingerprint(code);checks.append('independent_recursive_typed_code_canonical_form_matches_payload')
for name,mutator in [('wrong_fresh_credit',lambda x:x['live_RAM_guard_override']['override_resource_sample'].__setitem__('cgroup_reclaimable_clean_inactive_file_credit_bytes',0)),('wrong_effective_verdict',lambda x:x.__setitem__('physical_RAM_pass',False)),('wrong_UUID',lambda x:x['live_RAM_guard_override'].__setitem__('uuid','foreign')),('wrong_frontend',lambda x:x['live_RAM_guard_override']['override_resource_sample'].__setitem__('frontend_pid',999)),('sample_predates_patch',lambda x:x['live_RAM_guard_override']['override_resource_sample'].__setitem__('sample_begin_monotonic_ns',5)),('wrong_source',lambda x:x['live_RAM_guard_override'].__setitem__('patch_source_sha256','foreign'))]:
 r=copy.deepcopy(row);mutator(r)
 try:v.verify_override_sample(r,expected,certificate)
 except AssertionError:pass
 else:raise AssertionError(name+' accepted')
 checks.append(name+'_rejected')
source=json.dumps(row)+'\n';proofs=[];old_open=gzip.open;real=types.SimpleNamespace(open=lambda *a,**k:io.StringIO(source));proxy=v.PrivateGzipProxy(real,P('/fixture'),expected,certificate,proofs)
with proxy.open('/fixture/RESOURCE_SAMPLES.jsonl.gz','rt') as stream:view=json.loads(next(iter(stream)))
assert view==dict(row,physical_RAM_pass=False) and json.loads(source)==row and len(proofs)==1 and gzip.open is old_open;checks.append('private_proxy_changes_only_view_of_old_boolean_and_keeps_producer_bytes_global_gzip_unchanged')
raw=types.SimpleNamespace(open=lambda *a,**k:io.StringIO(source));proxy=v.PrivateGzipProxy(raw,P('/fixture'),expected,certificate,[])
with proxy.open('/foreign/RESOURCE_SAMPLES.jsonl.gz','rt') as stream:assert json.loads(next(iter(stream)))==row
checks.append('foreign_stream_not_transformed')
print(json.dumps({'status':'PASS','check_count':len(checks),'checks':checks,'scientific_models_started':0,'scientific_processes_attached_or_signaled':0,'consumer_started':False},indent=2))
