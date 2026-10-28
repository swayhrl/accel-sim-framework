"""Actual old348/Scope22f/Tinybeec + new A library CPU integration. No models."""
import copy,datetime,hashlib,importlib.util,json,pathlib,sys,threading,types,os
P=pathlib.Path;H=P(__file__).resolve().parent;sys.path.insert(0,str(H));import cpu_owner as owner
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sys.modules[n]=m;sp.loader.exec_module(m);return m
libpath=A/'agents/A/cpu_spare_memory_v1/cpu_memory.py';lib=load('actual_new_cpu_memory',libpath)
oldcfg=read(R/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json')
assert oldcfg['library_sha256']=='d4398a355240e81714c771f3c547e16f079570fc72498a158bf7908eb1e0d3f9'
oldowner=load('actual_old348',oldcfg['owner_path']);assert sha(oldowner.__file__)=='348650a77f4f9d88b2525ac3e8298b9c51df7e8ce0582c9bbb261ea73338098c'
scope_mod=load('actual_scope22f',R/'control/operational_amendments/future_memory_scope_sync_v1/scope_sync.py')
tiny_mod=load('actual_tinybeec',R/'control/operational_amendments/future_memory_aging_facade_v1/facade_memory.py')
frames_mod=load('actual_RuntimeFrames',A/'agents/E/large_job_aging_v1/aging_runtime_frames.py')
aging_mod=load('actual_AgingChooser',A/'agents/E/large_job_aging_v1/large_job_aging.py')
guard_mod=load('actual_FrameGuard',A/'agents/E/frame_read_guard_v1/frame_read_guard.py')
resources_mod=load('actual_full_forecast',R/'tools/l2_resources.py')
q=copy.deepcopy(read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][lib.REQ])
assert owner.C not in q['consumed'];history=read(R/'control/HISTORICAL_RSS.json')
root=H/('cpu_fixture_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));root.mkdir();owner.R=root
matrix=read(R/'control/MATRIX_CURRENT.json');put(root/'control/MATRIX_CURRENT.json',matrix)
put(root/'control/ACTUAL_CANARY_QUALIFICATION.json',read(R/'control/ACTUAL_CANARY_QUALIFICATION.json'))
reference=next(iter(q['consumed']));specs={c:read(R/'control/specs'/(c+'.json'))for c in(owner.C,reference)}
f=resources_mod.forecast(specs[owner.C],history);specs[owner.C]['estimated_peak_model_RAM_bytes']=max(f['predicted_peak_RAM_bytes'],specs[owner.C]['estimated_peak_model_RAM_bytes'])
for c,s in specs.items():put(root/'control/specs'/(c+'.json'),s);q['admitted_specs'][c]=sha(root/'control/specs'/(c+'.json'))
engine=types.SimpleNamespace(registered=lambda:({}, {},q,{}),canonical=lambda c:copy.deepcopy(specs[c]),assert_parent_lease=lambda:None)
calls=[];claims={};pressure=['cpu_pressure_full']
def raw_resource(s,fresh_source=False):
 candidate=s['cohort']==owner.C
 own=[dict(cohort=reference,RSS_bytes=G,additional_reserved_bytes=G,kind='SPENT_UNRESOLVED_GENERATION')]
 if candidate:own.append(dict(cohort=owner.C,RSS_bytes=0,additional_reserved_bytes=specs[owner.C]['estimated_peak_model_RAM_bytes'],kind='CLAIM_OR_CANDIDATE'))
 total=sum(x['additional_reserved_bytes']for x in own);budget=int((96*G-8*G)*.88)
 return dict(schema='L2_MLP_DYNAMIC_WORKINGSET_RESOURCE_V1',source_module_sha256=sha(R/'tools/l2_resources.py'),policy_sha256=sha(R/'control/RESOURCE_POLICY.json'),
  own_ram_forecasts=own,RAM_reservation_entries=[],total_projected_additional_RAM_bytes=total,boot_id=P('/proc/sys/kernel/random/boot_id').read_text().strip(),
  host_MemAvailable_bytes=128*G,cgroup_effective_headroom_bytes=96*G,cgroup_memory_max=str(256*G),cgroup_memory_current=160*G,
  cgroup_reclaimable_clean_inactive_file_credit_bytes=0,native_free_bytes=100*G,required_free_bytes=5*G,free_inodes=1000000,
  physical_disk_pass=True,own_write_ceiling_pass=True,physical_RAM_pass=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),monotonic=__import__('time').monotonic(),
  admission_decision=dict(pressure_reasons=list(pressure),pass_admission=not pressure and total<=budget,memory_utilization_fraction=.88,
   admission_RAM_budget_bytes=budget,additional_reserved_RAM_bytes=total,effective_usable_bytes=88*G,pressure_pause_new=bool(pressure)))
res=types.SimpleNamespace(resources=raw_resource,forecast=resources_mod.forecast,cpu_candidates=resources_mod.cpu_candidates)
def generic_B(pending,sample,cl,hist,previous=None,policy=None,dispatch_index=0):
 calls.append(('NORMAL_B',tuple(s['cohort']for s in pending)))
 if pending and not res.resources(pending[0],True)['admission_decision']['pressure_reasons']:return dict(cohort=pending[0]['cohort'],host_cpu=0)
 return None
def loader(n,f):return types.SimpleNamespace(terminal=lambda c:dict(performance_accepted=False,CPU_FIXTURE_HISTORICAL=True))
consumer=types.SimpleNamespace(load=loader,accepted=lambda v:False)
facade=types.SimpleNamespace(resources=raw_resource,forecast=res.forecast)
frames=frames_mod.RuntimeFrames(root,engine,facade,consumer,lambda v:v['own_ram_forecasts'],observe=lambda*c:None,generation=lambda*c:None)
aging=aging_mod.AgingChooser(generic_B,frames);res.DTC_LARGE_JOB_AGING_INSTALLED=aging
guard=guard_mod.FrameReadGuard(aging)
def CPU_outer(*args,**kw):return guard.wrapper(*args,**kw)
res.choose_dispatch=CPU_outer
def nopadding_worker(c):calls.append(('NO_PADDING_WORKER',c));return dict(state='CPU_ONLY_NO_MODEL',cohort=c)
def padding_worker(c):calls.append(('PADDING_WORKER',c));return dict(state='CPU_ONLY_NO_MODEL',cohort=c)
frame=types.SimpleNamespace(f_locals=dict(engine=engine,res=res,consumer=consumer,registry=types.SimpleNamespace(),claims=claims,pool=object(),max_workers=384),f_globals=dict(worker=padding_worker))
main=sys.modules['__main__'];setattr(main,owner.PADDING,dict(worker=nopadding_worker))
oldowner.install_on_frame(frame,oldcfg,aging,lambda:None);memory=getattr(main,owner.MEMORY)
setattr(main,'DTC_L2_MLP_INSTALLED_AGING_V1',dict(frames=frames,chooser=aging))
cell=(lambda x:lambda:x)(guard.wrapper).__closure__[0]
setattr(main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1',dict(gate=guard,aging=aging,cpu=dict(wrapper=CPU_outer,original=guard.wrapper),cell=cell))
# Actual frozen Tiny and Scope objects; only their fixture metadata paths differ.
tcfg=read(R/'control/operational_amendments/future_memory_aging_facade_v1/INSTALL.json');tcfg['memory_active_path']=str(root/'ACTIVE_MEMORY.json');put(root/'tiny.json',tcfg);put(root/'ACTIVE_MEMORY.json',oldcfg)
tiny=tiny_mod.FacadeMemory(main,root/'tiny.json');facade.resources=tiny.wrapper;setattr(main,owner.TINY,tiny)
scfg=read(R/'control/operational_amendments/future_memory_scope_sync_v1/INSTALL.json');scfg.update(root=str(root),directory=str(root/'sync'),memory_active_path=str(root/'ACTIVE_MEMORY.json'));put(root/'sync.json',scfg)
journal=types.SimpleNamespace(check=lambda:({}, {},q,{}),extend=lambda p:[],registry=frame.f_locals['registry'])
frame.f_locals['registry'].extend=journal.extend
sync=scope_mod.ScopeSync(frame,root/'sync.json',journal,memory,lambda p:None);setattr(main,owner.SYNC,sync)
# New operational config/receipts are explicitly synthetic metadata for CPU only.
cfg=copy.deepcopy(oldcfg);cfg.update(overlay_id=lib.ID,cpu_exception_scope=dict(mode='SINGLETON',allowed_cohorts=[owner.C]),cpu_spare_policy=lib.POLICY,fallback_v2_config=copy.deepcopy(oldcfg))
for role,p in [('library',libpath),('owner',H/'cpu_owner.py'),('extra_strict',H/'cpu_extra_strict.py')]:cfg[role+'_path']=str(p);cfg[role+'_sha256']=sha(p)
cfg['QA_path']=str(root/'CPU_ONLY_QA.json');cfg['readback_path']=str(root/'CPU_ONLY_READBACK.json')
qualified={r:cfg[r+'_sha256']for r in lib.ROLES}
qa=dict(status='PASS',cpu_spare_library_qualified=True,native_binding_qualified=True,native_prefix_qualified=True,joint_strict_qualified=True,qualified_sources=qualified,expected_pins=cfg['expected_pins'],CPU_ONLY_NOT_PUBLICATION=True)
joint_path=P(sys.argv[1])if len(sys.argv)>1 else None
if joint_path:
 qa=read(joint_path);assert qa['status']=='PASS'and qa['qualified_sources']==qualified
 P(cfg['QA_path']).write_bytes(joint_path.read_bytes())
else:put(cfg['QA_path'],qa)
cfg['QA_sha256']=sha(cfg['QA_path']);put(cfg['readback_path'],dict(verified=True,qualified_sources=qualified,expected_pins=cfg['expected_pins'],QA_sha256=cfg['QA_sha256'],CPU_ONLY_NOT_PUBLICATION=True));cfg['readback_sha256']=sha(cfg['readback_path'])
q['additional_operational_overlays'][lib.ID]=dict(lib.record(cfg),status='ACTIVE');lib.validate(cfg,q)
checks=[]
def ck(n,x):assert x,n;checks.append(n)
ck('actual old348 created complete saved dictionary before upgrade',memory['lib'].ID==owner.OLD_ID and memory['new_resources']is res.resources)
oldkeys=set(memory);oldctx=memory['context'];oldhistory=q['additional_operational_overlays'][owner.OLD_ID];oldq=copy.deepcopy(q)
put(root/'ACTIVE_MEMORY.json',cfg);receipt=owner.install_on_frame(frame,cfg,aging,lambda:None)
ck('same memory dictionary retained by actual Scope22f and Tinybeec',getattr(main,owner.MEMORY)is memory is sync.memory is tiny.memory)
ck('old entire saved-key provenance retained not just three callback fields',set(memory['generation_history'][-1]['saved'])==oldkeys and memory['generation_history'][-1]['saved']['context']is oldctx)
ck('new function closures replace old348 captured lib instead of metadata only',res.resources is memory['new_resources']and aging.original is memory['new_choose']and consumer.load is memory['new_load'])
ck('actual old q95 row and all budget consumed UUID fields unchanged',q==oldq and q['additional_operational_overlays'][owner.OLD_ID]==oldhistory)
ck('actual frozen Scope and Tiny guards accept new same-dict generation',sync.stable_memory()[1]==cfg and tiny.guard()==cfg)
sample=resources_mod.sample_system();pending=[engine.canonical(owner.C)]
value=aging.original(pending,sample,claims,history,None,None,0)
ck('real A CPU sampler and memory math can select only singleton after true old gate HOLD',value is not None and value['cohort']==owner.C and value['old_B5_PASS_claimed']is False)
frameval=frames(pending,sample,claims,history,None,{},0)
ck('actual RuntimeFrames gets scoped frame exception without changing provider identity',not frameval['pressure_reasons']and aging.frame_provider is frames and guard.original_provider is frames)
empty=frames([],sample,claims,history,None,{},0)
ck('frame without singleton pending retains original full PSI HOLD',empty['pressure_reasons']==['cpu_pressure_full'])
worker=frame.f_globals['worker'];worker(owner.C);worker(reference)
ck('canary uses saved exact NO_PADDING worker while others retain exact current worker',calls[-2:]==[('NO_PADDING_WORKER',owner.C),('PADDING_WORKER',reference)])
q['consumed'][owner.C]=dict(uuid='CPU_ONLY_SPENT_NO_MODEL')
ck('consumed singleton closes frame exception and prevents any worker retry',frames(pending,sample,claims,history,None,{},0)['pressure_reasons']==['cpu_pressure_full']and worker(owner.C)['state']=='SPENT_ENGINEERING_PRESERVE')
q['consumed'].pop(owner.C)
future=owner.C.replace('-M8-','-E768_M8-');q['admitted_specs'][future]='CPU_ONLY_REGISTERED_FUTURE_SPEC';q['budget']+=1;q['remaining']+=1
expanded=copy.deepcopy(cfg);expanded['allowed_cohorts'].append(future);q['additional_operational_overlays'][lib.ID]=dict(lib.record(expanded),status='ACTIVE');put(root/'ACTIVE_MEMORY.json',expanded)
sync.owner_module.update_scope_in_owner(expanded,lambda:None)
ck('actual Scope22f supports append through new generic owner API without changing CPU scope or old95 record',sync.stable_memory()[1]==expanded and tiny.guard()==expanded and expanded['cpu_exception_scope']==cfg['cpu_exception_scope']and q['additional_operational_overlays'][owner.OLD_ID]==oldhistory)
protected=aging.state.protected;tokens=copy.deepcopy(aging.state.pending_releases);owner.restore_in_owner(lambda:None)
ck('restore reverses private frame helper before Tiny and preserves aging reserve tokens',facade.resources is tiny.wrapper and aging.state.protected==protected and aging.state.pending_releases==tokens)
ck('new historical consumer retained after dispatch restore',consumer.load is memory['retained_cpu_generation_consumer'])
put(root/'ACTIVE_MEMORY.json',oldcfg)
ck('actual Scope22f and Tinybeec old generation valid again after restore',sync.stable_memory()[1]==oldcfg and tiny.guard()==oldcfg)
# Failure after actual old348 restore must recover the full private preimage.
put(root/'ACTIVE_MEMORY.json',expanded);before=dict(memory);oldraw=raw_resource
def failed_raw(*args,**kwargs):raise OSError('CPU_ONLY_INJECTED_REFERENCE_READ_RACE')
original_old=memory['old_resources'];memory['old_resources']=failed_raw
before=dict(memory);prior=(res.resources,aging.original,consumer.load,frame.f_globals['worker'],tiny.facade.resources,tiny.lib,sync.owner_module)
try:owner.install_on_frame(frame,expanded,aging,lambda:None)
except OSError:failed=True
else:failed=False
ck('post-restore reference failure rolls back all exact callbacks and full dictionary',failed and all(memory[k]is v for k,v in before.items())and prior==(res.resources,aging.original,consumer.load,frame.f_globals['worker'],tiny.facade.resources,tiny.lib,sync.owner_module))
memory['old_resources']=original_old
put(root/'ACTIVE_MEMORY.json',oldcfg)
bad=copy.deepcopy(expanded);bad['owner_sha256']='0'*64;prior=dict(memory)
try:owner.install_on_frame(frame,bad,aging,lambda:None)
except Exception:failed=True
else:failed=False
ck('source drift before upgrade leaves full original dictionary unchanged',failed and all(memory[k]is v for k,v in prior.items()))
historical=R/'control/qualification_ledger/E2-DTCL2MLP-2b93f70cd0666c51-DH-Q64-V1.INTENT.json'
intent=read(historical);extra=owner.historical_extra(intent,intent['output'])
ck('actual historical scalar95 INTENT selects old78 not current CPU config',sha(extra.__file__)=='78abb1c386e684ab250fb8e78398c79f564796cebc3f486c1e6ecff77a6236cd')
out=dict(status='PASS',count=len(checks),checks=checks,fixture_root=str(root),models_started=0,new_grants=0,production_changes=0,
 actual_candidate_joint_QA=dict(path=str(joint_path),sha256=sha(joint_path))if joint_path else None,
 actual_source_pins={str(p):sha(p)for p in [libpath,H/'cpu_owner.py',H/'cpu_extra_strict.py',P(oldowner.__file__),P(scope_mod.__file__),P(tiny_mod.__file__),P(frames_mod.__file__),P(guard_mod.__file__)]},
 caveat='Real source APIs and real CPU sampler, controlled RAM/authority/worker fixtures; fixture QA/readback are NOT publication or production qualification')
put(H/('OWNER_CANDIDATE_JOINT_QA_INTEGRATION.json'if joint_path else'OWNER_CPU_QUALIFICATION.json'),out);print(json.dumps(out))
