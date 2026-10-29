"""Actual native/observer/IO/CPU2 prefix, isolated authority/root, mocked fork."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,copy,types,tempfile,os,time,gzip,io,importlib.util
P=pathlib.Path;D=P(__file__).parent;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def build_fixture(root=None,extra_path=None,consumer_path=None,mode='BPF_REQUIRED',cohort=None,lineage=None,kind=None):
 root=P(root)if root else P(tempfile.mkdtemp(prefix='CPU_PREFIX_',dir=D));assert root.resolve().is_relative_to(A/'agents')and not root.resolve().is_relative_to(R);root.mkdir(parents=True,exist_ok=True)
 producer=load('CPU_BPF_producer_'+root.name,D/'strace_entry.py');front=load('CPU_BPF_front_'+root.name,D/'bpf_frontend.py')
 extra_path=P(extra_path or A/'agents/E/strace_bpf_future_strict_consumer_v3/bpf_extra_strict.py');consumer_path=P(consumer_path or A/'agents/E/strace_bpf_future_strict_consumer_v3/consumer_bridge.py');assert extra_path.exists()and consumer_path.exists()
 q=copy.deepcopy(read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][producer.REQ]);q['qualification_only']=True
 contract_path=A/'coordinator/bpf_canary_orchestration_v1/ENGINEERING_EXCLUSION_CONTRACT.json';ir_path=A/'agents/B/incident11_recovery_trials_plan_v1/DRAFT_PLAN.json';ir=read(ir_path);matrix=read(R/'control/MATRIX_CURRENT.json')
 if kind is None:kind='IR'if cohort in {r['new_cohort']for r in ir['rows']}else'ENGINEERING'if cohort in read(contract_path)['scope_cohorts']else'PRIMARY'
 assert kind in ['PRIMARY','IR','ENGINEERING']
 c=cohort or(next(r['new_cohort']for r in ir['rows'])if kind=='IR'else next(p['cohort']for p in matrix['points']if p['program']=='heartwall'and p['cell']=='DH'and p['profile']=='P0'))
 s=read(R/'control/specs'/(c+'.json'));assert s['host_cpu']is None
 if lineage is not None:assert kind=='IR';s['incident_recovery_trial_lineage']=lineage
 # Only the isolated copy can exercise a short already-completed primary.
 # The real consumed row and all production authority remain unchanged.
 q['consumed'].pop(c,None)
 rule=dict(reference_cycles=1234567 if kind=='IR'else 8552)
 history=read(R/'control/HISTORICAL_RSS.json');res=load('CPU_prefix_original_forecast',R/'tools/l2_resources.py');forecast=res.forecast(s,history,read(R/'control/RESOURCE_POLICY.json'));s['estimated_peak_model_RAM_bytes']=max(s['estimated_peak_model_RAM_bytes'],forecast['predicted_peak_RAM_bytes']);cpu=0;resolved=dict(s,host_cpu=cpu)
 for sub in['specs','dispatch_bindings','qualification_ledger']: (root/'control'/sub).mkdir(parents=True,exist_ok=True)
 (root/'DTC/run/results').mkdir(parents=True,exist_ok=True)
 put(root/'control/specs'/(c+'.json'),s);put(root/'control'/(c+'_SPEC.json'),s);db=dict(cohort=c,canonical_spec_sha256=sha(root/'control/specs'/(c+'.json')),host_cpu=cpu,resolved_spec_sha256=producer.objsha(resolved));put(root/'control/dispatch_bindings'/(c+'.json'),db);put(root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={c:dict(host_cpu=cpu)}))
 for name in['SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','BUILD_PROFILE.json','EXECUTION_PLAN.json','SCOPE.json','MATRIX_CURRENT.json']: (root/'control'/name).write_bytes((R/'control'/name).read_bytes())
 refs=sorted([p for p in read(root/'control/SCOPE.json')['points']if p['profile']=='P0'and p['input_digest']==s['input_digest']],key=lambda p:(p['cell']!='CH',p['cohort']));assert refs;ref=refs[0]['cohort'];rp=root/'control/specs'/(ref+'.json')
 if ref!=c:rp.write_bytes((R/'control/specs'/(ref+'.json')).read_bytes())
 if kind=='IR':
  old=s['incident_recovery_trial_lineage']['original_cohort'];(root/'analysis').mkdir(exist_ok=True)
  for source,target in [(R/'analysis'/(old+'.RESULT.json'),root/'analysis'/(old+'.RESULT.json')),(R/'control/qualification_ledger'/(old+'.DONE.json'),root/'control/qualification_ledger'/(old+'.DONE.json'))]:target.write_bytes(source.read_bytes())
 (root/'control/input_bindings').mkdir();(root/'control/input_bindings'/(s['input_digest']+'.json')).write_bytes(P(s['input_binding_path']).read_bytes())
 (root/'tools').mkdir(exist_ok=True);(root/'tools/l2_resources.py').symlink_to(R/'tools/l2_resources.py')
 req=root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json';put(root/'control/SCIENCE_AUTHORIZATION.json',dict(approval_request_sha256=sha(req),explicit_user_approval=True,owner_bindings_ratified=True,target_resource_policy_ratified=True,factor_family_grants_resolve_from_current_registry=True,budgets={c:1}))
 put(root/'control/DTC_NATIVE_GUARD_CONTROL_TESTS.json',dict(status='PASS',qualification_only=True));nativeRoot=root/'native';put(nativeRoot/'EP/control/SCIENCE_QUALIFICATION.json',dict(status='EP_SCIENCE_QUALIFIED',qualification_only=True))
 q['admitted_specs'][c]=sha(root/'control/specs'/(c+'.json'))
 if c not in q['admitted_inputs'][s['input_digest']]['specs']:q['admitted_inputs'][s['input_digest']]['specs'].append(c)
 q['budget']=len(q['admitted_specs']);q['remaining']=q['budget']-len(q['consumed']);q['state']='RUNNING';q['sealed']=[x for x in q.get('sealed',[])if x!=c]
 memcfg=copy.deepcopy(read(R/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json'))
 if c not in memcfg['allowed_cohorts']:memcfg['allowed_cohorts'].append(c)
 oldlib=load('CPU_prefix_old_CPU2_library',memcfg['library_path']);q['additional_operational_overlays'][oldlib.ID]=dict(oldlib.record(memcfg),status='ACTIVE');put(root/'CPU_MEMORY_CONFIG.json',memcfg)
 roles=dict(entry=str(D/'native-entry/bin/experiment'),frontend=str(D/'bpf_frontend.py'),producer=str(D/'strace_entry.py'),extra_strict=str(extra_path),consumer=str(consumer_path));pins=copy.deepcopy(memcfg['expected_pins']);pins[str(R/'tools/l2_native.py')]=sha(R/'tools/l2_native.py');pins[str(T/'tools/sweep_native_cap1m.py')]=sha(T/'tools/sweep_native_cap1m.py')
 policy_path=A/'agents/E/strace_bpf_future_policy_v3/future_policy.py';pins[str(policy_path)]=sha(policy_path);pins['/root/data/ep_l2_dtc_l1_native_v2/bin/native']=sha('/root/data/ep_l2_dtc_l1_native_v2/bin/native');sources={k:sha(p)for k,p in roles.items()};qa=root/'CPU_ONLY_QA.json';back=root/'CPU_ONLY_READBACK.json';put(qa,dict(schema='CPU_ONLY_STANDIN_NOT_RELEASE_AUTHORITY',qualification_only=True,status='PASS',native_prefix_qualified=True,extra_strict_qualified=True,consumer_archive_qualified=True,qualified_sources=sources,expected_pins=pins));put(back,dict(schema='CPU_ONLY_STANDIN_NOT_GITHUB',qualification_only=True,verified=True,qualified_sources=sources,expected_pins=pins,QA_sha256=sha(qa)))
 gate=root/'CPU_ONLY_CANARY4_PREREQUISITE.json';put(gate,dict(schema='DTC_BPF_FUTURE_V3_REAL_CANARY4_GATE_V1',kind='CPU_ONLY_PREREQUISITE_STANDIN_NOT_ACTUAL_CANARY',qualification_only=True,production_release_eligible=False))
 v2_entry=A/'agents/B/strace_bpf_future_entry_v2/native-entry/bin/experiment'
 cfg=dict(schema=producer.ID,request=producer.REQ,overlay_id=producer.ID,status='ACTIVE_FUTURE_SCOPED',root=str(root),qualification_only=True,future_primary_policy='MATRIX_REGISTERED_UNSPENT_BPF_REQUIRED',future_ir_policy='EXACT_REGISTERED_IR11_BPF_REQUIRED',source_paths=roles,qualified_sources=sources,expected_pins=pins,QA_path=str(qa),QA_sha256=sha(qa),readback_path=str(back),readback_sha256=sha(back),native_source_path=str(R/'tools/l2_native.py'),memory_frontend_path=str(R/'control/operational_amendments/future_memory_admission_v1/memory_frontend.py'),memory_frontend_sha256=sha(R/'control/operational_amendments/future_memory_admission_v1/memory_frontend.py'),memory_configuration_path=str(root/'CPU_MEMORY_CONFIG.json'),default_native_entry='/root/data/ep_l2_dtc_l1_native_v2/bin/native',v2_entry_path=str(v2_entry),v2_entry_sha256=sha(v2_entry),exclusion_contract_path=str(contract_path),exclusion_contract_sha256=sha(contract_path),policy_source_path=str(policy_path),policy_source_sha256=sha(policy_path),ir_plan_path=str(ir_path),ir_plan_sha256=sha(ir_path),canary4_prerequisite_path=str(gate),canary4_prerequisite_sha256=sha(gate));q['additional_operational_overlays'][producer.ID]=dict(producer.record(cfg),status='ACTIVE');put(root/'CONFIG.json',cfg)
 native=load('CPU_prefix_private_l2native_'+root.name,R/'tools/l2_native.py');native.R=root;native.registered=lambda:({'registered_future_requests':{producer.REQ:q}},{'epoch':2,'state':'NATIVE_SCIENCE_ACTIVE'},q,read(root/'control/EXECUTION_PLAN.json'));native.canonical=lambda cc:copy.deepcopy(read(root/'control/specs'/(cc+'.json')));native.spec_for=lambda cc:dict(native.canonical(cc),host_cpu=read(root/'control/dispatch_bindings'/(cc+'.json'))['host_cpu']);lease=dict(pid=999,start_ticks=100,qualification_only=True);native.assert_parent_lease=lambda:lease
 def authority(fn):fn({'registered_future_requests':{producer.REQ:q}});put(root/'CPU_ONLY_REGISTRY.json',q)
 native.update_authority=authority
 def prepared(cc):
  value=native.resources(native.spec_for(cc),True);assert value['physical_RAM_pass']and value['physical_disk_pass']
  return dict(status='CPU_PREFIX_OLD_PREPARE_STANDIN_NO_MODEL',operational_resource_profile=native.binding(),resources=value,CPU_FIXTURE=True)
 native.prepare=prepared
 def resource(spec,fresh_source=False):
  cost=s['estimated_peak_model_RAM_bytes'];return dict(boot_id=P('/proc/sys/kernel/random/boot_id').read_text().strip(),source_module_sha256=sha(R/'tools/l2_resources.py'),policy_sha256=sha(R/'control/RESOURCE_POLICY.json'),host_MemAvailable_bytes=1024*G,cgroup_effective_headroom_bytes=1024*G,native_free_bytes=100*G,required_free_bytes=5*G,free_inodes=1000000,monotonic=time.monotonic(),utc='CPU_ONLY_CONTROLLED_RESOURCE',physical_disk_pass=True,own_write_ceiling_pass=True,total_projected_additional_RAM_bytes=cost,RAM_reservation_entries=[],own_ram_forecasts=[dict(cohort=c,kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=cost)],admission_decision=dict(memory_utilization_fraction=.88,admission_RAM_budget_bytes=int(.88*1016*G),additional_reserved_RAM_bytes=cost,pressure_reasons=['cpu_pressure_full'],pressure_pause_new=True,pass_admission=False),physical_RAM_pass=not fresh_source)
 native.resources=resource
 ownpid=os.getpid();ownstat=P('/proc/self/stat').read_text();ticks=int(ownstat.rsplit(')',1)[1].split()[19]);tracerpid=ownpid+1000000
 def proc(pid):
  role='frontend'if pid==ownpid and not fixture.get('observing_model',False)else'model'if pid==ownpid else'tracer';fields=ownstat.rsplit(')',1)[1].split();fields[0]='R';fields[1]=str(tracerpid if role=='model'else ownpid if role=='tracer'else os.getppid());start=ticks if role!='tracer'else ticks-1;fields[19]=str(start);stat=str(pid)+' (CPU_FIXTURE) '+' '.join(fields)+'\n';sec=(2,1)if role=='model'and mode=='BPF_REQUIRED'else(0,0);tr=tracerpid if role=='model'else 0;status=f'Name:\tCPU_FIXTURE\nPid:\t{pid}\nPPid:\t{fields[1]}\nTracerPid:\t{tr}\nSeccomp:\t{sec[0]}\nSeccomp_filters:\t{sec[1]}\n';return dict(pid=pid,start_ticks=start,stat_before_utf8=stat,stat_after_utf8=stat,status_utf8=status,mnt_namespace='mnt:[4026535153]',observed_UTC='CPU_FIXTURE_NOT_ACTUAL_MODEL')
 fixture=dict(root=root,c=c,mode=mode,kind=kind,q=q,cfg=cfg,spec=s,resolved=resolved,memcfg=memcfg,native=native,producer=producer,front=front,calls=[],observing_model=False,root_native=nativeRoot,files_written_by_original_prefix=True,reference_cycles=rule['reference_cycles'])
 def memory_lib(lib):
  builder=load('CPU_old_evidence_fixture',A/'agents/A/cpu_spare_memory_v1/cpu_fixture.py');lib.sample_cpu_evidence=lambda selected_cpu=None:builder.evidence(lib,selected_cpu)
 class Raw:
  def __init__(self,p):self.f=P(p).open('wb');self.z=gzip.GzipFile(fileobj=self.f,mode='wb',mtime=0);self.hash=hashlib.sha256();self.bytes=0;self.error=None
  def start(self,stream):data=b'CPU MOCK NATIVE PREFIX ONLY\n';self.z.write(data);self.hash.update(data);self.bytes+=len(data)
  def flush(self):self.z.flush();self.f.flush()
  def fileno(self):return self.f.fileno()
  def close(self):self.z.close();self.f.close()
 class Adviser:
  def process(self,*a):pass
 class Guard:
  def __init__(self,*a):self.out=a[2];self.records=0
  def drain(self):return dict(records=[],terminal='NATURAL')
  def quick_stop(self):return None
  def sample(self,*a):return dict(decision=dict(decision='CONTINUE',CPU_FIXTURE=True))
 class Proc:
  pid=tracerpid
  def __init__(self):self.stdout=io.BytesIO(b'CPU');self.polls=0
  def poll(self):self.polls+=1;return None if self.polls==1 else 0
  def wait(self,*a,**kw):return 0
 def popen(argv,*args,**kwargs):fixture['calls'].append(dict(argv=list(argv),kwargs_keys=sorted(kwargs),list_id=id(argv)));return Proc()
 def engine_hook(n):
  n.NATIVE=nativeRoot;n.identity=lambda:dict(native_device=2128,CPU_FIXTURE=True);n.compressed_stream=lambda path:gzip.open(path,'wb');n.close_compressed=lambda h:h.close();n.child_info=lambda pid:dict(pid=pid,start_ticks=ticks,cmdline='CPU_FIXTURE',maps=s['native_simulator_argv'][0],mnt_namespace='mnt:[4026535153]',host_cpu_affinity_actual=[cpu],actual_process_limits_text=f'Max address space {s["limits"]["max_process_tree_vms_bytes"]} {s["limits"]["max_process_tree_vms_bytes"]} bytes\n');n._observer_race_children=lambda path:[str(ownpid)];sys.modules['sweep_read_cache']=types.SimpleNamespace(Adviser=Adviser);sys.modules['sweep_io']=types.SimpleNamespace(RawCapture=Raw);sys.modules['sweep_guard_cap1m']=types.SimpleNamespace(NativeDTCGuard=Guard);sys.modules['sweep_storage_guard']=types.SimpleNamespace(native_admission=lambda path:dict(status='PASS',CPU_FIXTURE=True))
  original_child=n.child_info
  def observed(pid):fixture['observing_model']=True;v=original_child(pid);return v
  n.child_info=observed
 fixture['hooks']=dict(proc_reader=proc,Popen=popen,engine=engine_hook,memory_lib=memory_lib);return types.SimpleNamespace(**fixture)
def run_prefix(fixture):
 f=fixture;f.producer.write_route_claim(f.native,f.cfg,f.c);result=f.front.main(['experiment','run-native',f.c,'--project','DTC_L1'],cfg=f.cfg,native_module=f.native,hooks=f.hooks,memory_cfg_override=f.memcfg);ip=f.root/'control/qualification_ledger'/(f.c+'.INTENT.json');i=read(ip);out=P(i['output']);proof=dict(performance_accepted=True,cycles=f.reference_cycles,cohort=f.c,uuid=i['uuid'],CPU_FIXTURE_NOT_ORIGINAL_PHYSICS_REPLAY=True,**{k:f.spec[k]for k in['input_digest','core_commit','framework_commit','binary_sha256','program','suite','cell','profile']});proof['effective_options']=f.spec['expected_options'];proof.update(CTA=f.spec['expected']['CTA'],instructions=f.spec['expected']['instructions'],kernel_count=f.spec['expected']['kernels']);return types.SimpleNamespace(fixture=f,root=f.root,c=f.c,q=f.q,cfg=f.cfg,out=out,intent=i,receipt=result,base_proof=proof)
def replay_old_additional(result):
 old=load('CPU_actual_old_CPU2_IO_extra',result.fixture.memcfg['extra_strict_path']);old.R=result.root
 return old.terminal(result.c,result.base_proof)
