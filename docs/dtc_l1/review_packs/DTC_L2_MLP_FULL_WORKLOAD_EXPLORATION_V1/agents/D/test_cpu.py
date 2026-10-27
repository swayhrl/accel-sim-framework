"""CPU-only acceptance wrappers, population exclusions and matched-GM fixtures."""
import pathlib,tempfile,json,gzip,hashlib,importlib.util,types,copy,math
HERE=pathlib.Path(__file__).resolve().parent
def load(n,p):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
strict=load('strict_fixture',HERE/'l2_strict.py');res=load('results_fixture',HERE/'l2_results.py');checks=0
def ck(v):
 global checks
 assert v;checks+=1
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def gz(p,rows):p.write_bytes(gzip.compress(''.join(json.dumps(x)+'\n'for x in rows).encode()))

with tempfile.TemporaryDirectory()as td:
 R=pathlib.Path(td)/'R';T=pathlib.Path(td)/'T';strict.R=R;strict.T=T;c='E2-DTCL2MLP-fixture-DH-E384-V1';uid='uuid-fixture';out=R/'DTC/run/results'/uid;out.mkdir(parents=True)
 (T/'tools').mkdir(parents=True);(T/'tools/sweep_native_cap1m.py').write_text('original source')
 bp=R/'input.json';write(bp,dict(qualification=dict(rows=[dict(path='/trace/kernel.trace')])))
 frozen=dict(cohort=c,host_cpu=None,native_simulator_argv=['/bin/model','-config','/config'],execution_mnt_namespace='mnt-test',input_binding_path=str(bp),input_binding_sha256=strict.sha(bp),core_commit='9eedb3131937748f0492fa83aad37d3691118d70',framework_commit='02775fd795cde5aae1480d81cee6eb481d0a08f4',runtime_files=[],original_environment=dict(DTC_AG7_INPUT_SHA='in',DTC_AG7_ROI_SHA='roi'),expected=dict(instructions=50),limits=dict(max_process_tree_rss_bytes=10000),input_digest='digest',program='TEST',suite='fixture',cell='DH',downstream_profile='E384',binary_sha256='binary',expected_options={'x':['y']})
 frozen['limits']['max_process_tree_vms_bytes']=20000
 canonical=R/'control/specs'/(c+'.json');write(canonical,frozen);s=dict(frozen,host_cpu=7)
 b=dict(cohort=c,canonical_spec_sha256=strict.sha(canonical),host_cpu=7,resolved_spec_sha256=strict.jsonsha(s));bd=R/'control/dispatch_bindings'/(c+'.json');write(bd,b);write(out/'DISPATCH_BINDING.json',b);write(out/'DOWNSTREAM_FROZEN_SPEC.json',frozen)
 observer=R/'observer.py';observer.write_text('observer');ob=dict(adapter_sha256=strict.sha(observer),transformed_run_native_source_sha256=hashlib.sha256(b'transformed').hexdigest(),transformation_counts={'exact':1},identity_snapshots_synthesized=False)
 basebind={'immutable':'contract'};common=dict(l2_mlp_execution_binding=basebind,observer_exit_race_binding=ob,dispatch_binding_sha256=strict.sha(bd))
 ip=R/'control/qualification_ledger'/(c+'.INTENT.json');i=dict(common,output=str(out),uuid=uid);write(ip,i)
 launch=dict(common,argv=s['native_simulator_argv'],host=dict(native_device=2128),effective_RLIMIT_AS_bytes=20000);write(out/'NATIVE_LAUNCH.json',launch)
 pid=dict(common,maps='/bin/model',mnt_namespace='mnt-test',host_cpu_affinity_actual=[7],pid=10,start_ticks=20,actual_process_limits_text='Limit                     Soft Limit           Hard Limit           Units\nMax address space         20000                20000                bytes\n');write(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',pid)
 raw=(s['framework_commit']+' '+s['core_commit']+'\navg_mrq_latency = 99\n').encode();(out/'raw.log.gz').write_bytes(gzip.compress(raw));(out/'actual_file_process_network.log').write_text('open /trace/kernel.trace')
 d=dict(uuid=uid,stop_reason=None,launcher_wait_returncode=0,native_simulator_observed=True,raw_sha256=strict.sha(out/'raw.log.gz'),raw_uncompressed_sha256=hashlib.sha256(raw).hexdigest(),raw_uncompressed_bytes=len(raw));write(ip.with_name(c+'.DONE.json'),d);write(out/'NATIVE_EXIT.json',d)
 p1=dict(seq=1,pid=10,start_ticks=20,generation=uid,input='in',roi='roi',mono_ns=1,completed=20,end=None);p2=dict(p1,seq=2,mono_ns=2,completed=50,end='NATURAL');gz(out/'progress.jsonl.gz',[p1,p2])
 resource=dict(DTC_exact_original_policy=dict(decision=dict(decision='RUN')),physical_RAM_pass=True,physical_disk_pass=True,process_tree_observed_rss_bytes=100);gz(out/'RESOURCE_SAMPLES.jsonl.gz',[resource])
 for name,src in [('DOWNSTREAM_INTENT.json',ip),('DOWNSTREAM_PLAN.json',R/'control/EXECUTION_PLAN.json'),('DOWNSTREAM_REQUEST.json',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),('DOWNSTREAM_PROFILE.json',R/'control/BUILD_PROFILE.json')]:
  if src!=ip:write(src,{'immutable':name})
  (out/name).write_bytes(src.read_bytes())
 q=dict(strict_sha256=strict.sha(strict.__file__),consumed={c:dict(uuid=uid,intent_sha256=strict.sha(ip),execution_receipt=d)});plan=dict(observer_overlay=dict(path=str(observer),sha256=strict.sha(observer)))
 engine=types.SimpleNamespace(registered=lambda:({}, {}, q, plan),spec_for=lambda cohort:s,check_input=lambda spec:None,binding=lambda:basebind)
 observed=[]
 def population(raw,spec,domain,legacy):
  observed.append((raw,spec,domain));assert spec['expected_options']=={'x':['y']};return dict(cycles=100,metrics={},traffic={})
 population_module=types.SimpleNamespace(population=population,legacy=lambda:None)
 def fake_load(name,path):
  if str(path).endswith('l2_native.py'):return engine
  if path==str(observer):return types.SimpleNamespace(transformed=lambda src:('transformed',{'exact':1}))
  if str(path).endswith('sweep_strict_cap1m.py'):return population_module
  raise AssertionError(path)
 strict.load=fake_load
 proof=strict.terminal(c);ck(proof['cycles']==100);ck(proof['performance_accepted']);ck(proof['latency_counters']['avg_mrq_latency']==99);ck(len(observed)==1)
 def reject(path,bad):
  before=path.read_bytes();path.write_bytes(bad)
  try:
   try:strict.terminal(c)
   except (AssertionError,ValueError,EOFError,KeyError):ck(True)
   else:raise AssertionError('accepted corrupt evidence '+str(path))
  finally:path.write_bytes(before)
 reject(out/'raw.log.gz',gzip.compress(b'corrupt'))
 reject(out/'actual_file_process_network.log',b'connect( socket ); /trace/kernel.trace')
 reject(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',json.dumps(dict(pid,host_cpu_affinity_actual=[8])).encode())
 reject(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',json.dumps(dict(pid,actual_process_limits_text='Max address space         unlimited            unlimited            bytes\n')).encode())
 reject(out/'NATIVE_LAUNCH.json',json.dumps(dict(launch,effective_RLIMIT_AS_bytes=10000)).encode())
 reject(out/'DISPATCH_BINDING.json',json.dumps(dict(b,host_cpu=9)).encode())
 reject(out/'DOWNSTREAM_FROZEN_SPEC.json',json.dumps(dict(frozen,host_cpu=7)).encode())
 reject(out/'DOWNSTREAM_PLAN.json',b'{}')
 reject(out/'progress.jsonl.gz',gzip.compress((json.dumps(dict(p2,end='TIMEOUT'))+'\n').encode()))
 reject(out/'progress.jsonl.gz',gzip.compress((json.dumps(p1)+'\n'+json.dumps(dict(p2,completed=49))+'\n').encode()))
 reject(out/'progress.jsonl.gz',gzip.compress((json.dumps(p1)+'\n'+json.dumps(dict(p2,mono_ns=1))+'\n').encode()))
 for bad in [dict(resource,physical_RAM_pass=False),dict(resource,physical_disk_pass=False),dict(resource,process_tree_observed_rss_bytes=10001),dict(resource,DTC_exact_original_policy=dict(decision=dict(decision='STOP')))]:
  reject(out/'RESOURCE_SAMPLES.jsonl.gz',gzip.compress((json.dumps(bad)+'\n').encode()))
 reject(out/'RESOURCE_SAMPLES.jsonl.gz',gzip.compress(b''))

# Three programs, two suites, two profiles, both cells; deliberate missing/fail.
points=[];records={}
for n in range(35):
 for profile in['P0','E384']:
  for cell in['CH','DH']:
   c=f'p{n}-{cell}-{profile}';points.append(dict(cohort=c,input_digest=str(n),program=f'program{n}',suite='S1'if n<20 else'S2',profile=profile,cell=cell));cyc=100 if profile=='P0'else(50 if cell=='DH'else 80)
   records[c]=dict(state=res.PASS,cycles=cyc,proof=dict(cycles=cyc,performance_accepted=True),archive={'verified':True})
scope={'points':points,'unresolved_programs':['u1','u2','u3','u4','u5','u6','u7']};v=res.summarize(scope,records)
ck(v['expected_input_count']==35);ck(v['aggregates']['E384']['ALL']['DH_speedup']['n']==35);ck(abs(v['aggregates']['E384']['ALL']['DH_speedup']['GM']-2)<1e-12);ck(abs(v['aggregates']['E384']['ALL']['relative_DTC_improvement']['GM']-1.6)<1e-12)
ck(v['aggregates']['E384']['S1']['CH_speedup']['n']==20);ck(v['aggregates']['E384']['S2']['CH_speedup']['n']==15)
records.pop('p0-CH-E384');records['p1-DH-E384']['state']='FAIL_L2MLP_ARCHIVED_NO_RETRY';records['p2-DH-E384']['proof']['performance_accepted']=False
v=res.summarize(scope,records);a=v['aggregates']['E384']['ALL'];ck(a['DH_speedup']['n']==33);ck(a['CH_speedup']['n']==34);ck(a['relative_DTC_improvement']['n']==32)
for metric in a['common_matched_quad'].values():ck(metric['n']==32);ck(metric['missing_n']==3)
ck(v['table']['0']['E384']['CH']['state']=='PENDING');ck(v['table']['1']['E384']['DH']['cycles']is None)
ref=dict(state=res.REUSE,cycles=100,proof=dict(performance_accepted=True),reuse_verification={k:True for k in['strict_verified','natural_done_verified','archive_native_restore_verified','complete_effective_options_equal','core_framework_binary_equal','input_scope_equal']})
ck(res.accepted(ref))
for k in list(ref['reuse_verification']):
 x=copy.deepcopy(ref);x['reuse_verification'][k]=False;ck(not res.accepted(x))
for n in range(35):ck(v['comparisons'][str(n)]['program']==f'program{n}')
cc=res.counters({});ck(cc['DRAM_issued_read_atoms']is None);ck(cc['L2_visible_MSHR_counters']is None);ck(cc['L2_accepted_read_miss_32B_sectors']is None)
cc=res.counters(dict(traffic=dict(L2_buckets={'GLOBAL_ACC_R:MISS':0,'GLOBAL_ACC_R:SECTOR_MISS':4,'GLOBAL_ACC_W:MISS':999,'GLOBAL_ACC_R:RESERVATION_FAIL':0})));ck(cc['L2_accepted_read_miss_32B_sectors']==4);ck(cc['L2_read_reservation_fail_attempts']==0)
with tempfile.TemporaryDirectory()as td:
 res.R=pathlib.Path(td);base=res.R/'control/SCOPE.json';write(base,scope)
 initial=res.summary();ck(initial['expected_input_count']==35)
 matrix=res.R/'control/MATRIX_CURRENT.json';extra=dict(cohort='future',input_digest='0',program='program0',suite='S1',profile='E1536',cell='DH')
 current=dict(points=points+[extra],base_scope_sha256=res.sha(base),revision=1);write(matrix,current)
 extended=res.summary();ck('E1536'in extended['profiles']);ck(extended['state_counts']['PENDING']==141)
 for bad in[dict(current,base_scope_sha256='wrong'),dict(current,points=current['points'][1:]),dict(current,revision=-1),dict(current,points=current['points']+[extra])]:
  write(matrix,bad)
  try:res.summary()
  except AssertionError:ck(True)
  else:raise AssertionError('accepted corrupt matrix revision')
print(json.dumps(dict(status='CPU_ONLY_PASS',checks=checks,actual_model_starts=0,population_comparator='unchanged original function mocked only for terminal wrapper fixtures',strict_negative_fixture_count=16,source_sha256={x.name:hashlib.sha256(x.read_bytes()).hexdigest()for x in[HERE/'l2_strict.py',HERE/'l2_results.py']}),indent=2))
