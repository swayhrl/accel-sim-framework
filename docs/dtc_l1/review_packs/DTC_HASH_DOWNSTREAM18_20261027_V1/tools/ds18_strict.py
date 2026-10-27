"""Independent whole-trace terminal acceptance, scoped only to new18 contract."""
import pathlib,json,gzip,hashlib,importlib.util,re
P=pathlib.Path;R=P('/root/data/dtc_hash_downstream18_20261027_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def terminal(c):
 e=load('ds18_strict_engine',R/'tools/ds18_native.py');reg,ep,q,plan=e.registered();assert q['strict_sha256']==sha(__file__);s=e.spec_for(c);ip=R/'control/qualification_ledger'/(c+'.INTENT.json');i=read(ip);d=read(ip.with_name(c+'.DONE.json'));row=q['consumed'][c];out=P(i['output']);assert out==R/'DTC/run/results'/row['uuid']and row['uuid']==i['uuid']==d['uuid']and row['intent_sha256']==sha(ip)and d==row['execution_receipt']==read(out/'NATIVE_EXIT.json')and d['stop_reason']is None and d['launcher_wait_returncode']==0 and d['native_simulator_observed']
 assert sha(out/'raw.log.gz')==d['raw_sha256'];rawb=gzip.decompress((out/'raw.log.gz').read_bytes());assert hashlib.sha256(rawb).hexdigest()==d['raw_uncompressed_sha256']and len(rawb)==d['raw_uncompressed_bytes'];raw=rawb.decode();trace=(out/'actual_file_process_network.log').read_text();assert 'connect('not in trace and'"/usr/bin/ssh"'not in trace and'"/bin/ssh"'not in trace
 bp=P(s['input_binding_path']);assert sha(bp)==s['input_binding_sha256'];domain=read(bp)['qualification'];e.check_input(s);assert all(v['path']in trace for v in domain['rows'])and s['framework_commit']in raw and s['core_commit'][:7]in raw
 launch=read(out/'NATIVE_LAUNCH.json');pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');assert launch['argv'][-len(s['native_simulator_argv']):]==s['native_simulator_argv']and s['native_simulator_argv'][0]in pid['maps']and pid['mnt_namespace']==s['execution_mnt_namespace']and launch['host']['native_device']==2128 and pid['host_cpu_affinity_actual']==[s['host_cpu']]
 for b in [i,launch,pid]:assert b['downstream_execution_binding']==e.binding()and b['observer_exit_race_binding']==i['observer_exit_race_binding']
 obs=plan['observer_overlay'];observer=load('ds18_strict_observer',obs['path']);code,counts=observer.transformed((T/'tools/sweep_native_cap1m.py').read_text());bind=i['observer_exit_race_binding'];assert bind['adapter_sha256']==obs['sha256']==sha(obs['path'])and bind['transformed_run_native_source_sha256']==hashlib.sha256(code.encode()).hexdigest()and bind['transformation_counts']==counts and not bind['identity_snapshots_synthesized']
 for name,src in [('DOWNSTREAM_FROZEN_SPEC.json',R/'control/specs'/(c+'.json')),('DOWNSTREAM_INTENT.json',ip),('DOWNSTREAM_PLAN.json',R/'control/EXECUTION_PLAN.json'),('DOWNSTREAM_REQUEST.json',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),('DOWNSTREAM_PROFILE.json',R/'control/BUILD_PROFILE.json')]:assert sha(out/name)==sha(src)
 for x in s['runtime_files']:assert sha(x['actual_realpath'])==x['sha256']
 old=load('ds18_existing_population_comparator',T/'tools/sweep_strict_cap1m.py');result=old.population(raw,s,domain,old.legacy());seq=0;last=None
 with gzip.open(out/'progress.jsonl.gz','rt')as h:
  for line in h:
   v=json.loads(line);seq+=1;assert v['seq']==seq and(v['pid'],v['start_ticks'],v['generation'])==(pid['pid'],pid['start_ticks'],d['uuid'])and v['input']==s['original_environment']['DTC_AG7_INPUT_SHA']and v['roi']==s['original_environment']['DTC_AG7_ROI_SHA']
   if last is not None:assert v['mono_ns']>last['mono_ns']and v['completed']>=last['completed']
   last=v
 assert last and last['end']=='NATURAL'and last['completed']==s['expected']['instructions'];ba=rs=0
 with gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt')as h:
  for line in h:
   v=json.loads(line)
   if 'DTC_exact_original_policy'in v:assert v['DTC_exact_original_policy']['decision']['decision']!='STOP';ba+=1
   if 'physical_RAM_pass'in v:assert v['physical_RAM_pass']and v['physical_disk_pass']and v['process_tree_observed_rss_bytes']<=s['limits']['max_process_tree_rss_bytes'];rs+=1
 assert ba and rs;extra={}
 for key,value in re.findall(r'^\s*(avg_mrq_latency|averagemflatency|avg_icnt2mem_latency|avg_icnt2sh_latency)\s*=\s*(\d+)\s*$',raw,re.M):extra[key]=int(value)
 return dict(result,schema='DTC_HASH_DOWNSTREAM18_STRICT_V1',status='DOWNSTREAM18_NATIVE_TRACE_PERFORMANCE_QUALIFIED',cohort=c,uuid=d['uuid'],input_digest=s['input_digest'],program=s['program'],cell=s['cell'],downstream_profile=s['downstream_profile'],performance_accepted=True,performance_scope='NEW_DOWNSTREAM18_ONLY',never_merge_original288=True,core_commit=s['core_commit'],framework_commit=s['framework_commit'],binary_sha256=s['binary_sha256'],effective_options=s['expected_options'],latency_counters=extra,progress_records=seq,BA_decisions=ba,resource_samples=rs,raw_gzip_sha256=d['raw_sha256'],raw_uncompressed_sha256=d['raw_uncompressed_sha256'],full_application_numerical_values='UNPROVEN',SOURCE_KEEP=True)
