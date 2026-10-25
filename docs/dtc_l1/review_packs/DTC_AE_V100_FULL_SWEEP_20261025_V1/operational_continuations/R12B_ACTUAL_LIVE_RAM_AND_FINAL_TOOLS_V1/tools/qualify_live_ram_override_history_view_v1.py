import pathlib,json,hashlib,importlib.util,io,gzip,types,copy
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
n=load('R12_history_fixture_native','sweep_native_cap1m.py');v=load('R12_history_fixture_override','sweep_live_ram_override_provenance_v1.py');root=load('R12_history_fixture_hostV3','sweep_host_provenance_v3.py');q=n.read_current_authority()[0]['registered_future_requests'][n.REQUEST];binding=root.bind(q);cell='E2-AEV100-f9edab43938e7bf4-CH';row=q['consumed'][cell];out=T/'DTC/run/results'/row['uuid'];assert json.loads((T/'analysis'/(cell+'.RESULT.json')).read_bytes())['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE'
with gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt') as stream:original=stream.read()
expected={'cohort':cell,'uuid':row['uuid'],'frontend_pid':123,'frontend_start_ticks':456,'patch_monotonic_ns':10};certificate={'patch_source_sha256':v.sha(T/'tools/sweep_live_ram_override_v1.py'),'plan_sha256':'synthetic_fixture_plan_only'};changed=[];seq=0
for line in original.splitlines():
 r=json.loads(line)
 if 'physical_RAM_pass' in r:
  seq+=1;prior=r['physical_RAM_pass'];fresh={'sample_begin_monotonic_ns':1000+seq,'sample_end_monotonic_ns':1000+seq,'utc':'synthetic_fixture','frontend_pid':123,'frontend_start_ticks':456,'host_MemAvailable_bytes':63*G,'cgroup_memory_max':str(256*G),'cgroup_memory_current':64*G,'cgroup_memory_stat_for_credit':{k:0 for k in ['file','inactive_file','shmem','file_mapped','file_dirty','file_writeback']},'cgroup_reclaimable_clean_inactive_file_credit_bytes':0,'cgroup_effective_headroom_bytes':192*G};r['physical_RAM_pass']=False;r['live_RAM_guard_override']={'schema':v.SCHEMA,'profile':v.PROFILE,'scope':'RUNTIME_ACTUAL_HEADROOM_ONLY','patch_source_sha256':certificate['patch_source_sha256'],'plan_sha256':certificate['plan_sha256'],'cohort':cell,'uuid':row['uuid'],'frontend_pid':123,'frontend_start_ticks':456,'prior_physical_RAM_pass':prior,'effective_physical_RAM_pass':False,'override_resource_sample':fresh}
 changed.append(json.dumps(r)+'\n')
data=''.join(changed);resource=out/'RESOURCE_SAMPLES.jsonl.gz';global_open=gzip.open;real=types.SimpleNamespace(open=lambda path,*a,**kw:io.StringIO(data) if P(path)==resource else global_open(path,*a,**kw));modules=list(v.historical_modules(root,binding));saved=[(m,m.gzip) for m in modules if hasattr(m,'gzip')];proofs=[]
try:
 for m,_ in saved:m.gzip=real
 try:root.verify(cell,binding,n)
 except AssertionError:pass
 else:raise AssertionError('Historical verifier accepted un-restored false boolean fixture')
 for m,_ in saved:m.gzip=v.PrivateGzipProxy(real,out,expected,certificate,proofs)
 result=root.verify(cell,binding,n);assert result['profile']=='HOST_CPU_CACHE_AWARE_V1' and result['outer_RAM_sample_arithmetic_replayed']==seq and len(proofs)==seq
finally:
 for m,old in saved:m.gzip=old
assert gzip.open is global_open
with gzip.open(resource,'rt') as stream:assert stream.read()==original
checks=['actual_preserved_V1_arithmetic_rejects_raw_synthetic_override_then_passes_private_prior_boolean_view','all_original_archived_stream_bytes_and_global_gzip_open_unchanged']
print(json.dumps({'status':'PASS','checks':checks,'resource_rows_replayed':seq,'fixture_only_not_scientific_evidence':True,'models_started':0,'consumer_starts':0},indent=2))
