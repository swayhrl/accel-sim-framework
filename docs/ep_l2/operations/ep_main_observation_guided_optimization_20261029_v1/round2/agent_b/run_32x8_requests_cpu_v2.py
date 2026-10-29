import os,sys,json,hashlib,subprocess,time,resource,pathlib,signal,shutil,datetime
P=pathlib.Path;B=P(__file__).resolve().parent;p=json.loads((B/'SOURCE78_EXACT3_PLAN_REFERENCE.json').read_bytes());O=B/'cpu_32x8_actual_v2';O.mkdir(exist_ok=False)
def sha(f):return hashlib.sha256(P(f).read_bytes()).hexdigest()
def ref(f):return dict(path=str(f),sha256=sha(f),bytes=P(f).stat().st_size)
def save(f,x):P(f).write_text(json.dumps(x,indent=2)+'\n')
def gate(phase):
 m={k:int(v.split()[0])*1024 for k,v in (l.split(':',1) for l in P('/proc/meminfo').read_text().splitlines())};cg=P('/sys/fs/cgroup');cur=int((cg/'memory.current').read_text());lim=(cg/'memory.max').read_text().strip();head=int(lim)-cur if lim!='max' else m['MemAvailable'];disk=shutil.disk_usage(B).free
 r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase=phase,MemAvailable=m['MemAvailable'],cgroup_remaining=head,disk_available=disk,self_compile_forecast_bytes=805306368,self_fixture_forecast_bytes=201326592,remaining_write_cap_bytes=134217728,emergency_disk_bytes=1073741824)
 if min(m['MemAvailable'],head)<2*1073741824 or disk<1073741824+134217728:raise RuntimeError('actual light CPU HOLD:'+str(r))
 return r
refs=[]
for r in p['sameSource_libraries']+p['source_refs']+p['generated_headers']+[p['base_config_ref'],p['overlay_ref'],p['compiler_ref']]:
 assert sha(r['path'])==r['sha256'],r;refs.append(r)
for r in p['source_repository_roots']:
 assert subprocess.check_output(['/usr/bin/git','-C',r['path'],'rev-parse','HEAD'],text=True).strip()==r['HEAD']
 assert subprocess.run(['/usr/bin/git','-C',r['path'],'diff','--quiet','HEAD']).returncode==0
# Reuse source dependencies read-only. Only fixture binaries are constructed.
env=dict(os.environ);env.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',EPL2_DETACH_DIAG='0',EPL2_TAGPRESSURE_DIAG='0',EPL2_TAG_LIFETIME='0',EP_L2_EVENT_TIMELINE='0',PYTHONDONTWRITEBYTECODE='1')
steps=[];cpu=8;assert cpu in os.sched_getaffinity(0)
def pre(asmax):
 os.setsid();os.sched_setaffinity(0,{cpu});os.setpriority(os.PRIO_PROCESS,0,10);resource.setrlimit(resource.RLIMIT_AS,(asmax,asmax));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def rss_tree(pid):
 ids={pid};todo=[pid]
 while todo:
  n=todo.pop()
  try:a=list(map(int,(P('/proc')/str(n)/'task'/str(n)/'children').read_text().split()))
  except FileNotFoundError:continue
  for v in a:
   if v not in ids:ids.add(v);todo.append(v)
 total=0
 for n in ids:
  try:
   for l in (P('/proc')/str(n)/'status').read_text().splitlines():
    if l.startswith('VmRSS:'):total+=int(l.split()[1])*1024
  except FileNotFoundError:pass
 return total
p['exact3']=[dict(name='requests32x8',source=str(B/'test_w_only_32x8_requests_v2.cc'),arguments=[p['base_config_ref']['path'],str(B/'W_ONLY_PRIVATE_CPU_V2.config'),'2','16','0','0','1'],expected_marker='W_ONLY_SOURCE78_32X8_REAL_REQUESTS|requests=9|pending_peak=7|dirtyWB=1|reverse_returns=7|bankP1=1|drain=1|PASS')]
for case in p['exact3']:
 case=dict(case);case['arguments']=[str(B/'W_ONLY_PRIVATE_CPU_V2.config') if x==p['overlay_ref']['path'] else x for x in case['arguments']]
 exe=(B/'cpu_actual_attempt3'/(case['name']+'.cpu')) if case['name'] in ['constructor32x8','partition_WAD128'] else O/(case['name']+'.cpu')
 for phase,argv in [('COMPILE',p['compile_prefix']+[case['source']]+p['link_suffix']+['-o',str(exe),'-UNDEBUG']),('CPU_FIXTURE',[str(exe)]+case['arguments'])]:
  
  if phase=='COMPILE' and case['name'] in ['constructor32x8','partition_WAD128']:
   prior=json.loads((B/'cpu_actual_attempt3/STEPS_CURRENT.json').read_bytes());steps.append(dict(next(x for x in prior if x['label']==case['name']+'_compile'),reused_exact_executable=True));continue
  label=case['name']+('_compile' if phase=='COMPILE' else '_run');g=gate(phase);save(O/(label+'.ADMISSION.json'),g);beg=time.monotonic();peak=0
  with (O/(label+'.stdout')).open('xb') as a,(O/(label+'.stderr')).open('xb') as e:
   child=subprocess.Popen(argv,cwd=O,env=env,stdout=a,stderr=e,preexec_fn=lambda:pre(1073741824 if phase=='COMPILE' else 268435456))
   hard=1207959552 if phase=='COMPILE' else 402653184
   while child.poll() is None:
    peak=max(peak,rss_tree(child.pid))
    if peak>hard or time.monotonic()-beg>(180 if phase=='COMPILE' else 60):
     os.killpg(child.pid,signal.SIGKILL);child.wait();raise RuntimeError('own CPU limit '+label)
    time.sleep(.05)
   rc=child.wait()
  try:os.killpg(child.pid,0);closed=False
  except ProcessLookupError:closed=True
  r=dict(label=label,phase=phase,argv=argv,returncode=rc,process_group_closed=closed,wall_seconds=time.monotonic()-beg,peak_child_tree_RSS_bytes=peak,stdout_ref=ref(O/(label+'.stdout')),stderr_ref=ref(O/(label+'.stderr')))
  if phase=='CPU_FIXTURE':r['expected_marker']=case['expected_marker'];r['expected_marker_present']=case['expected_marker'] in P(r['stdout_ref']['path']).read_text();r['binary_ref']=ref(exe)
  steps.append(r);save(O/'STEPS_CURRENT.json',steps);print(label,rc,peak,round(r['wall_seconds'],3),flush=True)
  assert rc==0 and closed,r
  if phase=='CPU_FIXTURE':assert r['expected_marker_present'],r
result=dict(schema='EP_ROUND2_SOURCE78_W_ONLY_EXACT3_CPU_EXECUTION_V1',status='SOURCE78_W_ONLY_32X8_REAL_REQUEST_COMPONENT_PASS_NOT_APPLICATION_ACCEPTANCE',source_identity=p['source_identity'],steps=steps,dependencies_verified=refs,constructed_exec_gpgpu_sim=True,constructor_success_RC_and_marker_observed=True,model_starts=0,registry_writes=0,Trace_read_count=0,production_source_mutations=0,scientific_qualification_granted=False,native_or_Host_qualification_granted=False,CPU_affinity=cpu,old_HOLD_untouched=True,authorization_ref=ref(B/'START_SCOPE.json'))
save(B/'CPU_32X8_REQUESTS_EXECUTION_FINAL.json',result);print('PASS_RESULT',ref(B/'CPU_32X8_REQUESTS_EXECUTION_FINAL.json'),flush=True)
