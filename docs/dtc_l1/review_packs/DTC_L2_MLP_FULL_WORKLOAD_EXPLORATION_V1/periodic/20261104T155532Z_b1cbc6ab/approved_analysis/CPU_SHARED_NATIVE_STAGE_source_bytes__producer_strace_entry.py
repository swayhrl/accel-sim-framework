"""Future private native-entry producer. Import never installs, forks or registers."""
import copy,datetime,hashlib,importlib.util,json,os,pathlib,sys,types,inspect,threading
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';ID='DTC_STRACE_SHARED_CPU_OBSERVATION_V1'
ROLES=['entry','frontend','producer','extra_strict','consumer'];MODES={'BPF_REQUIRED','DEFAULT_CONTROL'}
FLAG='--seccomp-bpf';FILTER='trace=%file,process,network';FIELD='additional_strace_bpf_observation_binding'
OLD_NATIVE_SHA='fb246ce610a76a21ae86b36730283fa9fdd9f5d21e35fd76e2db17847f2b247d'
INITIAL='E2-DTCL2MLP-731af5428c4b8155-DH-P0-OBSCTRL-V1'
DESIGN_SHA='02e9050b76f695c21d72a73bff636a415f8fe45c6a7f543874108241ae22905d'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def objsha(v):return hashlib.sha256(js(v)).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def atomic_exclusive(path,obj):
 p=P(path);data=js(obj);tmp=p.with_name('.'+p.name+'.bpf-'+os.urandom(8).hex())
 try:
  with tmp.open('xb')as h:h.write(data);h.flush();os.fsync(h.fileno())
  os.link(tmp,p);tmp.unlink();fd=os.open(p.parent,os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if tmp.exists():tmp.unlink()
def record(cfg):return dict(request=REQ,overlay_id=ID,configuration_sha256=objsha(cfg),qualified_sources=cfg['qualified_sources'],expected_pins=cfg['expected_pins'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],modes=cfg['modes'],future_primary_policy=cfg['future_primary_policy'],resource_configuration_sha256=cfg['resource_configuration_sha256'],design_contract_sha256=cfg['design_contract_sha256'])
def validate(cfg,q):
 assert cfg['schema']==cfg['overlay_id']==ID and cfg['request']==REQ and cfg['status']=='ACTIVE_FUTURE_ONLY'
 assert cfg['future_primary_policy']=='NONE'and cfg['modes']=={INITIAL:'DEFAULT_CONTROL'},'EXACT_ONE_SHARED_CONTROL_ONLY'
 if cfg['qualification_only']:
  assert q.get('qualification_only')is True and P(cfg['root']).resolve()!=R
 else:assert not q.get('qualification_only',False)and P(cfg['root']).resolve()==R
 assert set(cfg['qualified_sources'])==set(cfg['source_paths'])==set(ROLES)
 for role in ROLES:assert sha(cfg['source_paths'][role])==cfg['qualified_sources'][role]
 assert sha(__file__)==cfg['qualified_sources']['producer']
 for p,h in cfg['expected_pins'].items():assert sha(p)==h
 assert sha(cfg['memory_frontend_path'])==cfg['memory_frontend_sha256']
 assert sha(cfg['design_contract_path'])==cfg['design_contract_sha256']==DESIGN_SHA
 assert sha(cfg['resource_configuration_path'])==cfg['resource_configuration_sha256'];resource=read(cfg['resource_configuration_path'])
 assert resource['allowed_cohorts']==[INITIAL]and resource['max_shared_running']==1 and resource['qualification_stage']=='INITIAL_EXACT_ONE'
 assert resource['root']==cfg['root']and resource['source_paths']['owner']==cfg['source_paths']['producer']and resource['source_paths']['frontend']==cfg['source_paths']['frontend']and resource['source_paths']['consumer']==cfg['source_paths']['consumer']
 assert resource['source_paths']['extra_strict']!=cfg['source_paths']['extra_strict'],'RESOURCE_AND_OBSERVATION_STRICT_ARE_DISTINCT'
 lib=load('shared_independent_resource_contract',resource['library_path']);assert sha(lib.__file__)==resource['qualified_sources']['library'];lib.validate(resource,q)
 assert cfg['default_native_entry']=='/root/data/ep_l2_dtc_l1_native_v2/bin/native'and cfg['expected_pins'][cfg['default_native_entry']]=='46c69a74154e0690afd82324a348da236baf90189d9a7e474b4b14eb01ab4f0e'
 assert sha(cfg['exclusion_contract_path'])==cfg['exclusion_contract_sha256'];contract=read(cfg['exclusion_contract_path']);assert contract['schema']=='DTC_ENGINEERING_OBSERVATION_EXCLUSION_CONTRACT_V1'and contract['status']=='EXCLUSION_RULES_ONLY_NOT_ADMISSION_AUTHORITY'
 if contract.get('qualification_only'):assert cfg['qualification_only']and q.get('qualification_only')is True
 assert sha(cfg['QA_path'])==cfg['QA_sha256']and sha(cfg['readback_path'])==cfg['readback_sha256']
 qa=read(cfg['QA_path']);back=read(cfg['readback_path'])
 assert qa['status']=='PASS'and all(qa[k]is True for k in ['native_prefix_qualified','extra_strict_qualified','consumer_archive_qualified'])and back['verified']is True
 assert qa['qualified_sources']==back['qualified_sources']==cfg['qualified_sources']and qa['expected_pins']==back['expected_pins']==cfg['expected_pins']and back['QA_sha256']==cfg['QA_sha256']
 rec=q['additional_operational_overlays'][ID];assert rec['status']=='ACTIVE'and all(rec.get(k)==v for k,v in record(cfg).items())
 return rec
def select_mode(cfg,c,q):
 if c in cfg['modes']:return cfg['modes'][c]
 return None
def unused(q,c):return c in q['admitted_specs']and c not in q['consumed']and c not in q.get('sealed',[])and q['remaining']>0
def verify_engineering_spec(cfg,c,mode,spec):
 contract=read(cfg['exclusion_contract_path']);rule=contract['scope_cohorts'][c]
 assert rule['mode']==mode and rule['scientific_role']==spec['scientific_role']=='ENGINEERING_OBSERVATION_CANARY'and rule['primary_statistics_excluded']is True and rule['validated_union_authorized']is False
 projection={k:spec[k]for k in contract['science_keys']};digest=hashlib.sha256(json.dumps(projection,sort_keys=True,separators=(',',':')).encode()).hexdigest();assert digest==rule['science_projection_sha256']
 lineage=spec['engineering_observation_canary_lineage'];assert lineage['mode']==mode and lineage['pair_id']==rule['pair_id']and lineage['reference_result_sha256']==rule['reference_result_sha256']and lineage['science_projection_sha256']==digest
 assert lineage['reference_cohort']==rule['reference_cohort']and lineage['reference_cycles']==rule['reference_cycles']and lineage['primary_statistics_excluded']is True and lineage['validated_union_authorized']is False
 return rule
def scientific_identity(s):return dict(input_digest=s['input_digest'],input_binding_sha256=s['input_binding_sha256'],core_commit=s['core_commit'],framework_commit=s['framework_commit'],binary_sha256=s['binary_sha256'],expected_options_sha256=objsha(s['expected_options']),native_simulator_argv_sha256=objsha(s['native_simulator_argv']),cell=s['cell'],profile=s['profile'])
def expected_argv(root,out,s):
 root=P(root);loader=str(root/'common-lib/ld-linux-x86-64.so.2')
 return[loader,'--library-path',str(root/'tools/lib')+':'+str(root/'common-lib'),str(root/'tools/bin/strace'),'-f','-e',FILTER,'-o',str(P(out)/'actual_file_process_network.log'),'--',loader,'--inhibit-cache','--library-path',str(root/'DTC/env/lib'),*s['native_simulator_argv']]
def mode_argv(old,mode):
 assert mode in MODES and FLAG not in old and old[4:7]==['-f','-e',FILTER]
 return old[:4]+[FLAG]+old[4:]if mode=='BPF_REQUIRED'else list(old)
def capture_proc(pid):
 proc=P('/proc')/str(pid);before=(proc/'stat').read_text();status=(proc/'status').read_text();mnt=os.readlink(proc/'ns/mnt');after=(proc/'stat').read_text();a=before.rsplit(')',1)[1].split();b=after.rsplit(')',1)[1].split();assert a[19]==b[19]and a[0]not in ['Z','X']and b[0]not in ['Z','X']
 return dict(pid=pid,start_ticks=int(b[19]),stat_before_utf8=before,stat_after_utf8=after,status_utf8=status,mnt_namespace=mnt,observed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
def proc_fields(p):
 a=p['stat_before_utf8'].rsplit(')',1)[1].split();b=p['stat_after_utf8'].rsplit(')',1)[1].split();status={line.split(':',1)[0]:line.split(':',1)[1].strip()for line in p['status_utf8'].splitlines()if':'in line}
 assert type(p['pid'])is int and type(p['start_ticks'])is int and int(p['stat_before_utf8'].split('(',1)[0])==int(p['stat_after_utf8'].split('(',1)[0])==p['pid'];assert int(a[19])==int(b[19])==p['start_ticks']and a[0]not in ['Z','X']and b[0]not in ['Z','X'];assert int(status['Pid'])==p['pid']and int(status['PPid'])==int(a[1])==int(b[1])
 return dict(pid=p['pid'],start_ticks=p['start_ticks'],PPid=int(status['PPid']),TracerPid=int(status['TracerPid']),Seccomp=int(status['Seccomp']),Seccomp_filters=int(status['Seccomp_filters']))
def baseline(p):
 v=proc_fields(p);assert(v['TracerPid'],v['Seccomp'],v['Seccomp_filters'])==(0,0,0),'UNQUALIFIED_NESTED_OR_INHERITED_SECCOMP_BASELINE';return v
def activation_verdict(mode,model,tracer,preintent,prepop,launcher_pid,expected_pid,expected_ticks):
 reasons=[]
 try:
  a=baseline(preintent);b=baseline(prepop);assert(a['pid'],a['start_ticks'])==(b['pid'],b['start_ticks'])
  x=proc_fields(model);t=proc_fields(tracer);assert x['pid']==expected_pid and x['start_ticks']==expected_ticks and t['pid']==launcher_pid and x['TracerPid']==x['PPid']==t['pid']and(t['TracerPid'],t['Seccomp'],t['Seccomp_filters'])==(0,0,0)and t['PPid']==b['pid']
  assert model['mnt_namespace']==tracer['mnt_namespace']==preintent['mnt_namespace']==prepop['mnt_namespace']
  expected=(2,1)if mode=='BPF_REQUIRED'else(0,0);assert mode in MODES and(x['Seccomp'],x['Seccomp_filters'])==expected
 except Exception as error:reasons.append(repr(error))
 return dict(status=('PASS_CPU_SHARED_BPF_REQUIRED_ACTIVE'if mode=='BPF_REQUIRED'else'PASS_CPU_SHARED_DEFAULT_CONTROL_NO_BPF')if not reasons else'HOLD_CPU_SHARED_ACTIVATION_UNPROVEN',mode=mode,activation_verified=not reasons,BPF_claimed=mode=='BPF_REQUIRED'and not reasons,explicit_default_control=mode=='DEFAULT_CONTROL',reasons=reasons,automatic_retry_or_fallback=False)

class PrivateSubprocessProxy:
 def __init__(self,original,birth,cohort,mode,native,cfg,proc_reader,popen_override=None):self.original=original;self.birth=birth;self.cohort=cohort;self.mode=mode;self.native=native;self.cfg=cfg;self.proc_reader=proc_reader;self.popen_override=popen_override;self.attempted=False;self.launcher_pid=None
 def __getattr__(self,k):return getattr(self.original,k)
 def Popen(self,argv,*args,**kwargs):
  assert not self.attempted,'ONE_BIRTH_ONE_FORK_NO_FALLBACK';b=self.birth;assert b['snapshot_sha256']and b['uuid']
  q=self.native.registered()[2];row=q['consumed'][self.cohort];root=P(self.cfg['root']);ip=root/'control/qualification_ledger'/(self.cohort+'.INTENT.json');intent=read(ip)
  assert row['uuid']==intent['uuid']==b['uuid']and row['intent_sha256']==sha(ip)and row['charged']==1 and intent[FIELD]==b['binding']
  assert q['admitted_specs'][self.cohort]==b['canonical_spec_sha256']and self.native.assert_parent_lease()==self.birth['parent_lease']
  assert type(argv)is list and argv==b['expected_before'];prepop=self.proc_reader(os.getpid());baseline(prepop);assert proc_fields(prepop)['start_ticks']==proc_fields(b['baseline_preINTENT'])['start_ticks']
  argv[:]=b['expected_after'];plan=dict(schema=ID,cohort=self.cohort,uuid=b['uuid'],mode=self.mode,snapshot_sha256=b['snapshot_sha256'],intent_sha256=sha(ip),baseline_prePopen=prepop,argv_before=b['expected_before'],argv_after=list(argv),argv_list_mutated_in_place=True,scientific_identity=b['scientific_identity'])
  atomic_exclusive(P(b['output'])/'STRACE_BPF_FORK_PLAN.json',plan);b['fork_plan']=plan;self.attempted=True
  p=(self.popen_override or self.original.Popen)(argv,*args,**kwargs);self.launcher_pid=p.pid;return p

def configure_native(native,cfg,cohort,mode,hooks=None):
 """Compose after old IO/CPU2, restricted to one freshly loaded frontend module."""
 q=native.registered()[2];validate(cfg,q);assert select_mode(cfg,cohort,q)==mode and unused(q,cohort);assert not hasattr(native,'_STRACE_SHARED_CPU_ENTRY_V1')
 verify_engineering_spec(cfg,cohort,mode,native.canonical(cohort))
 assert all(p['cohort']!=cohort for p in read(P(cfg['root'])/'control/MATRIX_CURRENT.json')['points'])
 if hooks is not None:assert cfg['qualification_only']and q.get('qualification_only')is True
 hooks=hooks or{};proc_reader=hooks.get('proc_reader',capture_proc);old_prepare=native.prepare;old_engine=native.engine
 def prepare(c):
  assert c==cohort;validate(cfg,native.registered()[2]);assert unused(native.registered()[2],c);native.assert_parent_lease();baseline(proc_reader(os.getpid()));return old_prepare(c)
 native.prepare=prepare
 def engine():
  n=old_engine();assert sha(n.__file__)==OLD_NATIVE_SHA and n.run_native.__globals__ is n.__dict__
  if hooks.get('engine'):hooks['engine'](n)
  old=n.exclusive;old_child=n.child_info;birth={};binding={}
  proxy=PrivateSubprocessProxy(n.subprocess,birth,cohort,mode,native,cfg,proc_reader,hooks.get('Popen'));n.subprocess=proxy
  def child(pid):
   value=old_child(pid)
   if native.spec_for(cohort)['native_simulator_argv'][0]in value['maps']:
    assert proxy.launcher_pid is not None;model=proc_reader(pid);tracer=proc_reader(proxy.launcher_pid);assert model['start_ticks']==value['start_ticks']
    value=dict(value,strace_observation_proc_capture=dict(model=model,tracer=tracer))
   return value
  n.child_info=child
  def exclusive(path,obj):
   path=P(path)
   if path.name.endswith('.INTENT.json'):
    assert obj['cohort']==cohort and unused(native.registered()[2],cohort);rec=validate(cfg,native.registered()[2]);s=native.spec_for(cohort);root=P(cfg['root']);sp=root/'control/specs'/(cohort+'.json');db=root/'control/dispatch_bindings'/(cohort+'.json');raw=sp.read_bytes();dbr=db.read_bytes();canonical=json.loads(raw);dispatch=json.loads(dbr);assert sha(sp)==native.registered()[2]['admitted_specs'][cohort]==dispatch['canonical_spec_sha256'];assert objsha(s)==dispatch['resolved_spec_sha256']
    out=P(obj['output']);before=expected_argv(root,out,s);after=mode_argv(before,mode);preintent=proc_reader(os.getpid());baseline(preintent);lease=copy.deepcopy(native.assert_parent_lease());science=scientific_identity(s)
    verify_engineering_spec(cfg,cohort,mode,canonical)
    snap=dict(schema=ID,request=REQ,cohort=cohort,uuid=obj['uuid'],mode=mode,config=copy.deepcopy(cfg),overlay_record=copy.deepcopy(rec),source_snapshots={r:dict(path=cfg['source_paths'][r],sha256=cfg['qualified_sources'][r],utf8=P(cfg['source_paths'][r]).read_bytes().decode('utf-8'))for r in ROLES},QA_utf8=P(cfg['QA_path']).read_bytes().decode('utf-8'),readback_utf8=P(cfg['readback_path']).read_bytes().decode('utf-8'),canonical_spec_utf8=raw.decode(),canonical_spec_sha256=sha(sp),resolved_spec=s,resolved_spec_sha256=objsha(s),dispatch_binding_utf8=dbr.decode(),dispatch_binding_sha256=sha(db),scientific_identity=science,baseline_preINTENT=preintent,expected_argv_before=before,expected_argv_after=after,parent_lease=lease,exclusion_contract_utf8=P(cfg['exclusion_contract_path']).read_bytes().decode('utf-8'))
    snap.update(resource_configuration_utf8=P(cfg['resource_configuration_path']).read_bytes().decode(),design_contract_utf8=P(cfg['design_contract_path']).read_bytes().decode())
    atomic_exclusive(out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json',snap)
    binding.update(schema=ID,request=REQ,overlay_id=ID,cohort=cohort,uuid=obj['uuid'],mode=mode,snapshot_sha256=sha(out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json'),config_sha256=objsha(cfg),qualified_sources=cfg['qualified_sources'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],canonical_spec_sha256=sha(sp),resolved_spec_sha256=objsha(s),dispatch_binding_sha256=sha(db),expected_argv_before_sha256=objsha(before),expected_argv_after_sha256=objsha(after),scientific_identity=science)
    birth.update(binding,output=str(out),expected_before=before,expected_after=after,baseline_preINTENT=preintent,parent_lease=lease,binding=copy.deepcopy(binding))
   if path.name=='NATIVE_LAUNCH.json':
    assert obj['argv']==birth['expected_after']and proxy.launcher_pid==obj['launcher_pid'];obj=dict(obj,strace_fork_plan_sha256=sha(path.parent/'STRACE_BPF_FORK_PLAN.json'))
   if path.name=='NATIVE_SIMULATOR_PID_AND_MAPS.json':
    captured=obj['strace_observation_proc_capture'];plan=birth['fork_plan'];verdict=activation_verdict(mode,captured['model'],captured['tracer'],birth['baseline_preINTENT'],plan['baseline_prePopen'],proxy.launcher_pid,obj['pid'],obj['start_ticks'])
    activation=dict(schema=ID,cohort=cohort,uuid=birth['uuid'],mode=mode,snapshot_sha256=binding['snapshot_sha256'],fork_plan_sha256=sha(path.parent/'STRACE_BPF_FORK_PLAN.json'),model=captured['model'],tracer=captured['tracer'],baseline_preINTENT=birth['baseline_preINTENT'],baseline_prePopen=plan['baseline_prePopen'],verdict=verdict)
    atomic_exclusive(path.parent/'STRACE_BPF_ACTIVATION.json',activation);obj=dict(obj,strace_observation_activation_sha256=sha(path.parent/'STRACE_BPF_ACTIVATION.json'))
   if path.name.endswith('.INTENT.json')or path.name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:
    assert binding;obj=dict(obj,**{FIELD:copy.deepcopy(binding)})
   return old(path,obj)
  n.exclusive=exclusive;n._STRACE_SHARED_CPU_PRIVATE_V1=dict(proxy=proxy,old_child=old_child,old_exclusive=old,birth=birth,binding=binding);return n
 native.engine=engine;native._STRACE_SHARED_CPU_ENTRY_V1=dict(old_engine=old_engine,old_prepare=old_prepare,cohort=cohort,mode=mode);return native

def restore_private(native):
 v=native._STRACE_SHARED_CPU_ENTRY_V1;native.engine=v['old_engine'];native.prepare=v['old_prepare'];del native._STRACE_SHARED_CPU_ENTRY_V1

OWNER_MARKER='DTC_STRACE_CPU_SHARED_DISPATCH_V1'
def make_worker_clone(raw_worker,entry_root):
 assert sha(inspect.getsourcefile(raw_worker))=='a53f4933d2f0a7479a15d0e6dd8aa0501c4762d6b2161363b9467472a43fc1dc'
 namespace=dict(raw_worker.__globals__);namespace['N']=P(entry_root)
 clone=types.FunctionType(raw_worker.__code__,namespace,raw_worker.__name__,raw_worker.__defaults__,raw_worker.__closure__)
 assert clone.__code__ is raw_worker.__code__ and all(clone.__globals__[k] is raw_worker.__globals__[k] for k in raw_worker.__globals__ if k!='N')
 return clone
def install_owner_dispatch(frame,cfg_path,consumer_check,main=None,armed=False,hooks=None):
 """Main-only reversible future routing; never called by qualification runner."""
 assert threading.current_thread()is threading.main_thread();main=main or sys.modules['__main__'];assert not hasattr(main,OWNER_MARKER)
 engine=frame.f_locals['engine'];engine.assert_parent_lease();q=engine.registered()[2];cfg=read(cfg_path);validate(cfg,q)
 if hooks is not None:assert cfg['qualification_only']and q.get('qualification_only')is True and P(cfg['root']).resolve()!=R
 hooks=hooks or{}
 assert not any(c not in q['consumed']for c in frame.f_locals['claims']),'DRAIN_PREEXEC_CLAIMS_FIRST'
 assert P(inspect.getsourcefile(consumer_check))==P(cfg['source_paths']['consumer'])and sha(inspect.getsourcefile(consumer_check))==cfg['qualified_sources']['consumer']
 assert consumer_check(frame,cfg) is True,'NEW_STRICT_CONSUMER_NOT_INSTALLED'
 assert armed is False,'INSTALL_CLOSED_THEN_EXPLICIT_ARM'
 assert INITIAL not in frame.f_locals['claims']and INITIAL not in read(P(cfg['root'])/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']and not(P(cfg['root'])/'control/qualification_ledger'/(INITIAL+'.INTENT.json')).exists()and unused(q,INITIAL)
 old=frame.f_globals['worker'];raw=getattr(main,'DTC_L2_MLP_PADDING_ONLY_OWNER_V1')['worker'];clone=make_worker_clone(raw,P(cfg['source_paths']['entry']).parents[1]);res=frame.f_locals['res'];aging=res.DTC_LARGE_JOB_AGING_INSTALLED;oldchoose=res.choose_dispatch
 state=dict(frame=frame,previous=old,clone=clone,aging=aging,res=res,cfg_path=str(cfg_path),armed=False,ever_armed=False,previous_choose=oldchoose,last_hold=None,last_proof=None,consumer_check=consumer_check)
 def worker(c):
  if c!=INITIAL:return old(c)
  try:
   currentq=engine.registered()[2]
   if not unused(currentq,c):return dict(state='SPENT_ENGINEERING_PRESERVE',cohort=c,model_retries=0,error='SHARED_IDENTITY_NOT_UNUSED')
   if not state['armed']:return dict(state='ZERO_START_DEFERRED',cohort=c,model_starts=0,error='RESOURCE_HOLD_SHARED_EXACT1_NOT_ARMED')
   current=read(cfg_path);currentq=engine.registered()[2];validate(current,currentq);mode=select_mode(current,c,currentq)
   if mode is None:return old(c)
   if not unused(currentq,c):return dict(state='SPENT_ENGINEERING_PRESERVE',cohort=c,model_retries=0,error='BPF_IDENTITY_NOT_UNUSED')
   assert consumer_check(frame,current)is True
   return clone(c)
  except Exception as error:
   try:
    spent=c in engine.registered()[2]['consumed']or(P(cfg['root'])/'control/qualification_ledger'/(c+'.INTENT.json')).exists()
    if spent:return dict(state='SPENT_ENGINEERING_PRESERVE',cohort=c,model_retries=0,error='STRACE_ENTRY_SPENT_PRESERVE '+repr(error))
    return dict(state='ZERO_START_ENGINEERING',cohort=c,model_starts=0,error='STRACE_ENTRY_HOLD '+repr(error))
   except Exception:return dict(state='ENGINEERING_PRESERVE',cohort=c,model_retries=0,error='STRACE_ENTRY_IDENTITY_UNKNOWN '+repr(error))
 def choose(pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  ordinary=oldchoose(pending,sample,claims,history,previous,policy,dispatch_index)
  if ordinary is not None or not state['armed']:return ordinary
  try:
   with aging.lock:
    current=read(cfg_path);q=engine.registered()[2];validate(current,q);spec=next((s for s in pending if s['cohort']==INITIAL),None)
    if spec is None or not unused(q,INITIAL)or INITIAL in claims:return None
    rcfg=read(current['resource_configuration_path']);lib=load('shared_owner_exact1_resource',rcfg['library_path']);lib.validate(rcfg,q)
    if hooks.get('memory_lib'):hooks['memory_lib'](lib)
    canonical=engine.canonical(INITIAL);forecast=res.forecast(canonical,history,policy or read(P(current['root'])/'control/RESOURCE_POLICY.json'))
    assert forecast['predicted_peak_RAM_bytes']<=canonical['estimated_peak_model_RAM_bytes'],'OFFICIAL_FORECAST_REFRESH_REQUIRED'
    legal=lib.capture_legal_cpu_evidence(rcfg,claims,INITIAL);cpus=legal['legal_cpu_candidates'];assert cpus,'NO_ORIGINAL_LEGAL_CPU'
    db=P(current['root'])/'control/dispatch_bindings'/(INITIAL+'.json');selected=read(db)['host_cpu']if db.exists()and read(db)['host_cpu']in cpus else cpus[0]
    legal=lib.capture_legal_cpu_evidence(rcfg,claims,INITIAL,selected);cpu=lib.sample_cpu_evidence(selected);slot=lib.capture_slot_evidence(rcfg,q,INITIAL,selected,root=engine.R)
    base=res.resources(dict(canonical,host_cpu=selected),True);projected=lib.project_for_candidate(base,rcfg,INITIAL,selected,cpu,slot,{'kind':'OWNER_CHOOSE'},legal)
    reserve=max(0,int(aging.state.protected));slack=lib.budget(projected)-projected['total_projected_additional_RAM_bytes'];assert slack>=reserve,'PROTECTED_R_NOT_AVAILABLE'
    assert projected['physical_RAM_pass']and projected['physical_disk_pass']and projected['own_write_ceiling_pass']
    result=dict(cohort=INITIAL,host_cpu=selected,forecast=forecast,admission=projected['admission_decision'],cpu_shared_timeslice_overlay_id=lib.ID)
    # Reuse the already-qualified zero-start CPU-binding repair, never alter
    # a consumed/claimed identity or a scientific spec.
    helper=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/zero_start_cpu_rebind_v1/zero_start_cpu_rebind.py');assert sha(helper)=='b0db8a54400bd456aa404aa9b033badefc59231f8dd04534bc34bcf56937bcf8'
    rebound=load('shared_existing_zero_start_cpu_rebind',helper).maybe_rebind(engine.R,engine,res,result,legal['sample'],claims,None)
    assert rebound is not None,'ZERO_START_BINDING_HOLD';state['last_proof']=projected[lib.PROOF];state['last_hold']=None;return rebound
  except Exception as error:state['last_hold']=repr(error);return None
 with aging.lock:
  assert frame.f_globals['worker']is old and res.choose_dispatch is oldchoose
  state.update(wrapper=worker,chooser=choose,ever_exposed=True);setattr(main,OWNER_MARKER,state);frame.f_globals['worker']=worker;res.choose_dispatch=choose
 return dict(status='SHARED_EXACT1_CLOSED_DISPATCH_INSTALLED',armed=False,new_grants=0,model_starts=0)

def arm_owner_dispatch(main=None):
 assert threading.current_thread()is threading.main_thread();main=main or sys.modules['__main__'];v=getattr(main,OWNER_MARKER);frame=v['frame'];engine=frame.f_locals['engine'];engine.assert_parent_lease()
 with v['aging'].lock:
  cfg=read(v['cfg_path']);q=engine.registered()[2];validate(cfg,q);assert frame.f_globals['worker']is v['wrapper']and v['res'].choose_dispatch is v['chooser']and v['consumer_check'](frame,cfg)is True
  assert unused(q,INITIAL)and INITIAL not in frame.f_locals['claims']and INITIAL not in read(P(cfg['root'])/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']and not(P(cfg['root'])/'control/qualification_ledger'/(INITIAL+'.INTENT.json')).exists()
  v['armed']=True;v['ever_armed']=True
 return dict(status='SHARED_EXACT1_DISPATCH_ARMED',cohort=INITIAL,new_grants=0,model_starts=0)
def restore_owner_dispatch(main=None):
 assert threading.current_thread()is threading.main_thread();main=main or sys.modules['__main__'];v=getattr(main,OWNER_MARKER);v['frame'].f_locals['engine'].assert_parent_lease()
 with v['aging'].lock:
  frame=v['frame'];engine=frame.f_locals['engine'];q=engine.registered()[2];root=P(engine.R)
  if v['ever_armed']:
   value=read(root/'analysis'/(INITIAL+'.RESULT.json'));proof=value['proof'];resource=proof['additional_cpu_shared_timeslice_strict'];obs=proof['additional_strace_bpf_observation_strict']
   assert value['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and proof['performance_accepted']is True and value['uuid']==proof['uuid']==q['consumed'][INITIAL]['uuid']and value['archive']
   assert resource['status']=='PASS_CPU_SHARED_TIMESLICE_IO_AND_ORIGINAL_PERFORMANCE'and obs['schema']==ID
   for p in [resource,obs]:assert sha(p['sidecar_path'])==p['sidecar_sha256']
  else:assert INITIAL not in frame.f_locals['claims']and INITIAL not in q['consumed']and not(root/'control/qualification_ledger'/(INITIAL+'.INTENT.json')).exists()
  assert frame.f_globals['worker']is v['wrapper']and v['res'].choose_dispatch is v['chooser'];frame.f_globals['worker']=v['previous'];v['res'].choose_dispatch=v['previous_choose'];delattr(main,OWNER_MARKER)
 return dict(status='EXACT_PREVIOUS_FUTURE_WORKER_RESTORED',retained_new_generation_consumer_required=True,new_grants=0,model_starts=0)
