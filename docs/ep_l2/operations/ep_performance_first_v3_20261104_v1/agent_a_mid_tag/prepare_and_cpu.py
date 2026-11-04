import json,pathlib,hashlib,os,resource,subprocess,time,re,copy
P=pathlib.Path
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1'); A=J/'research/performance_first_v3_20261104_v1/agent_a_mid_tag'; V=J/'research/performance_first_v2_20261103_v1'; OLD=J/'execution_system850_v2_20261104_v1/system'; O=P('/root/data/ep_l2_multiworkload_event_timeline_20261027_v1');CPU=V/'agent_c/cpu';G=1<<30;M=1<<20
for x in ['cpu','option_echo','spec_candidates','configs','evidence']: (A/x).mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p),bytes=P(p).stat().st_size)
def read(p):return json.loads(P(p).read_text())
def put(p,d):P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');return ref(p)
def run(argv,label,cap=G,wall=90,env=None):
 def limit():
  resource.setrlimit(resource.RLIMIT_AS,(cap,cap));resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(32*M,32*M));os.nice(10)
 start=time.monotonic();p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=wall,preexec_fn=limit,env=env)
 out=A/'cpu'/(label+'.stdout');err=A/'cpu'/(label+'.stderr');out.write_bytes(p.stdout);err.write_bytes(p.stderr)
 return dict(argv=list(map(str,argv)),returncode=p.returncode,seconds=time.monotonic()-start,stdout_ref=ref(out),stderr_ref=ref(err))
mem=int(next(x.split()[1]for x in P('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024
cg=P('/sys/fs/cgroup');mx=(cg/'memory.max').read_text().strip();cur=int((cg/'memory.current').read_text());free=os.statvfs(A).f_bavail*os.statvfs(A).f_frsize
admit=dict(MemAvailable_bytes=mem,cgroup_max=mx,cgroup_current=cur,disk_free=free,engineering_AS_limit=G,expected_incremental_disk=80*M)
admit['PASS']=mem>2*G and (mx=='max' or int(mx)-cur>G) and free>120*M
put(A/'evidence/CPU_RESOURCE_ADMISSION.json',admit);assert admit['PASS']
source=read(OLD/'cases/EP_PERF_PFV2_SYSTEM850_FWT_S_G64W16_V1/control/FROZEN_SPEC.json')['source_identity']
assert subprocess.check_output(['git','-C',str(O/'core'),'rev-parse','HEAD'],text=True).strip()==source['core_source_commit']
assert not subprocess.check_output(['git','-C',str(O/'core'),'status','--porcelain','--untracked-files=no'],text=True).strip()
for kind,p in [('binary_sha256',O/'build/accel-sim.out'),('archive_sha256',O/'build/gpgpu-sim/src/gpgpu-sim/libgpgpusim.a')]:assert sha(p)==source[kind]
# Reuse prior Source78 constructor S/F controls; execute only new geometry S/WV protocol+MS-only NI.
prior_ctor=J/'tools/qualified_geometry_queue_v1/evidence/SOURCE78_ACTUAL_CONSTRUCTOR_RESULT.json';ctor=read(prior_ctor)
assert ctor['source_identity']==source
reused=[]
for t in ctor['tests']:
 if t['case']in ['G32W16_S','G64W8_S']:
  assert t['PASS'];reused.append(dict(case=t['case'],evidence_ref=ref(prior_ctor),stdout_ref=t['stdout_ref']))
assert len(reused)==2
src=(CPU/'test_system850_protocol.cc').read_text();src=src.replace('assert(argc==9);','assert(argc==10);').replace('const unsigned sets=ways==16?64:32;','const unsigned sets=std::stoul(argv[9]);assert(sets==32||sets==64);')
(A/'cpu/test_midtag_protocol.cc').write_text(src)
cmd=read(CPU/'BUILD_RECEIPT.json')['argv'];cmd=[str(A/'cpu/test_midtag_protocol.cc')if x==str(CPU/'test_system850_protocol.cc') else str(A/'cpu/midtag.cpu')if x==str(CPU/'system850.cpu') else x for x in cmd]
env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',EPL2_LIFE_WIRE='SUMMARY_STAGE',EPL2_TAGPRESSURE_DIAG='0',EPL2_TAG_LIFETIME='0',EPL2_DETACH_DIAG='0',EP_L2_EVENT_TIMELINE='0')
compiled=run(cmd,'compile',wall=120,env=env);assert compiled['returncode']==0
runs=[];pairs=[]
for sets,ways in [(32,16),(64,8)]:
 for mode in ['S','WV_ZERO_RO']:
  sem=[]
  for bits in ['111','011']:
   txt=(CPU/('G64W16_'+mode+'.config')).read_text().replace('-gpgpu_ep_l2_ms_observer 1','-gpgpu_ep_l2_ms_observer '+bits[0]);cfg=A/'cpu'/('G'+str(sets)+'W'+str(ways)+'_'+mode+'_'+bits+'.config');cfg.write_text(txt)
   argv=[str(A/'cpu/midtag.cpu'),str(O/'cpu_fixture_inputs/base.config'),str(cfg),'1'if mode=='S'else'2','16','0','0','1',str(ways),str(sets)]
   rr=run(argv,cfg.stem,cap=G,env=env);assert rr['returncode']==0;rr.update(sets=sets,ways=ways,mode=mode,observer_bits=bits,config_ref=ref(cfg));runs.append(rr)
   marks=[x for x in P(rr['stdout_ref']['path']).read_text().splitlines()if x.startswith(('SYSTEM850_SEMANTIC|','SYSTEM_SOURCE78_REAL_REQUESTS|','SYSTEM_SOURCE78_CONSTRUCTOR|'))];assert len(marks)==3;sem.append(marks)
  assert sem[0]==sem[1];pairs.append(dict(sets=sets,ways=ways,mode=mode,MS011_111_semantics_equal=True,markers=sem[0],PASS=True))
put(A/'evidence/PRODUCTION_CPU_AND_MS_NI.json',dict(status='PASS_4_GEOMETRY_MODE_PROTOCOL_PAIRS_NOT_APPLICATION_NI',source_identity=source,compile=compiled,reused_S_constructors=reused,runs=runs,pairs=pairs,application_NI='NOT_MEASURED',B0_M0a_application_NI='NOT_PROVEN_HELD_ON',Trace_body_read=False,formal_model_starts=0,peak_child_RSS_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024))
# Exact eight candidate specs, each derived from accepted original mode REF282; no authority inheritance.
fields=['goal','source_identity','source_worktrees','binary_path','static_library_path','input_identity_sha256','input_binding_ref','eligibility_ref','trace_entry','all_unique_kernel_members','expected_CTA','expected_instructions','expected_kernel_launches','expected_kernel_scopes','command_count','observer_env','scientific_scope','original_capture_completeness','numeric_output','source_qualification_ref','modeled_resource_cost_ref','validation_contract_ref','helpers_ref','output_module_ref','compact_module_ref','limits','output_forecast']
points=[];echo=[]
echoexe=CPU/'option_echo_full_cpu';assert sha(echoexe)==read(V/'agent_c/ACTUAL_282_SYSTEM850_CPU_RECEIPT.json')['producer_binary_ref']['sha256']
for workload in ['FWT','GEMM']:
 for sets,ways in [(32,16),(64,8)]:
  for mode in ['S','WV_ZERO_RO']:
   prior=OLD/'cases'/('EP_PERF_PFV2_SYSTEM850_'+workload+'_'+mode+'_G64W16_V1')/'control/FROZEN_SPEC.json';s0=read(prior);base=read(s0['absolute_REF850_spec_ref']['path']);opts=dict(base['expected_effective_options']);assert len(opts)==282
   geom='S:'+str(sets)+':128:'+str(ways)+',L:B:m:L:P,A:128:1,128:0,32';before=opts['-gpgpu_cache:dl2'];opts['-gpgpu_cache:dl2']=geom
   case='EP_PERF_PFV3_MIDTAG_'+workload+'_'+mode+'_G'+str(sets)+'W'+str(ways)+'_V1';overlay=A/'configs'/(case+'.config');overlay.write_text('# V3 candidate only; no scientific launch authority\n-gpgpu_cache:dl2 '+geom+'\n')
   ordered=copy.deepcopy(base['ordered_configs'])+[ref(overlay)]
   for r in ordered:assert sha(r['path'])==r['sha256']
   argv=[str(echoexe)];[argv.extend(['-config',r['path']])for r in ordered];argv.extend(['-trace',s0['trace_entry']]);rr=run(argv,'echo_'+case,cap=G,env=env);assert rr['returncode']==0
   actual={}
   for line in P(rr['stdout_ref']['path']).read_text().splitlines():
    if line.startswith('-'):
     key,_,rest=line.partition(' ');value=rest.split('#',1)[0].strip();value='NULL'if value=='(null)'else value
     if key in actual:assert actual[key]==value
     actual[key]=value
   assert len(actual)==282 and actual==opts,(case,{k:(opts.get(k),actual.get(k))for k in set(opts)|set(actual)if opts.get(k)!=actual.get(k)})
   optfile=A/'option_echo'/(case+'.json');put(optfile,actual);rr.update(cohort=case,actual_option_count=len(actual),exact282_PASS=True,option_ref=ref(optfile));echo.append(rr)
   spec={k:copy.deepcopy(s0[k])for k in fields if k in s0};spec.update(schema='EP_PFV3_MIDTAG_PREPARATION_SPEC_V1',status='ENGINEERING_CANDIDATE_NOT_FROZEN_NOT_REGISTERED',science_request_id='EP_L2_MID_TAG_850MHZ_V1_20261104',cohort=case,workload=workload,mode=mode,profile='PFV3_MIDTAG_G'+str(sets)+'W'+str(ways),M=False,T=False,ro_qualification_ref=None,geometry=dict(slices=64,sets=sets,ways=ways,line_bytes=128),expected_effective_options=opts,ordered_configs=ordered,option_delta_from_exact_mode_REF={'-gpgpu_cache:dl2':dict(before=before,after=geom)},provenance_prior_spec_ref=ref(prior),absolute_REF850_spec_ref=s0['absolute_REF850_spec_ref'],absolute_REF850_S_anchor_qualification_ref=s0['absolute_REF850_S_anchor_qualification_ref'],absolute_REF850_EP_anchor_qualification_ref=s0['absolute_REF850_EP_anchor_qualification_ref'],same_background_peer_cohort=case.replace('_S_G','_WV_ZERO_RO_G')if mode=='S'else case.replace('_WV_ZERO_RO_G','_S_G'),source_keep=True,automatic_retry=False,refund=False,scientific_launch_permission=False,launch_budget_registered=0,estimated_peak_RAM_bytes=2*G,estimated_wall_seconds=7200 if workload=='FWT'else 10800,application_NI='NOT_MEASURED',B0_M0a_application_NI='NOT_PROVEN_HELD_ON',REF850_usage='ABSOLUTE_REFERENCE_ONLY_NOT_SAME_BACKGROUND_S')
   path=A/'spec_candidates'/(case+'.json');put(path,spec);points.append(dict(cohort=case,mode=mode,workload=workload,geometry=spec['geometry'],spec_ref=ref(path),priority=0 if workload=='FWT'else 1,stage='FWT_FOUR_BEFORE_GEMM_FOUR'))
put(A/'evidence/ACTUAL282_CPU_RECEIPT.json',dict(status='PASS_8_EXACT282_CANDIDATE_ECHO_NOT_APPLICATION',source_identity=source,producer_binary_ref=ref(echoexe),runs=echo))
put(A/'MID_TAG_FAMILY_SCOPE.json',dict(schema='EP_PFV3_MIDTAG_CANDIDATE_SCOPE_V1',request_id='EP_L2_MID_TAG_850MHZ_V1_20261104',source_identity=source,points=points,proposed_model_count=8,registered_model_count=0,formal_model_starts=0,physical_resources=dict(payload_line_slots_per_slice=1168,resident_nominal=1024,bypass=128,staticWB=16,banks=4,bank_ops_per_CORE_cycle=1,lineMSHR=128,descriptors=512,WAD=128),fixed_clock='1132.0:1132.0:1132.0:850.0',fixed_dram_latency=100,fixed_FRFCFS=128))
print(json.dumps(dict(status='CPU_AND282_PASS',point_count=len(points),root=str(A))))
