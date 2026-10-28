"""Focused actual CPU1→CPU2 replacement/selection CPU fixture. No models."""
import copy,datetime,hashlib,importlib.util,json,pathlib,sys,types
P=pathlib.Path;H=P(__file__).resolve().parent;sys.path.insert(0,str(H));import cpu_owner as owner
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sys.modules[n]=m;sp.loader.exec_module(m);return m
af=load('actual_A_cpu2_fixture',A/'agents/A/cpu_spare_memory_v2/cpu_fixture_v2.py');f=af.fixture(owner_path=H/'cpu_owner.py',extra_path=H/'cpu_extra_strict.py')
root=f.root;lib=f.lib;cfg=f.cfg;q=f.q;previous=f.previous;CANARY=f.canary;BIG,SMALL=f.points;owner.R=root
cpu1=load('actual_cpu1_owner332',previous['owner_path']);cpu1.R=root
oldowner=load('actual_old348',f.old['owner_path']);frames_mod=load('actual_frames98d5',A/'agents/E/large_job_aging_v1/aging_runtime_frames.py');aging_mod=load('actual_aging',A/'agents/E/large_job_aging_v1/large_job_aging.py');guard_mod=load('actual_guard',A/'agents/E/frame_read_guard_v1/frame_read_guard.py')
scope_mod=load('actual_scope22f',R/'control/operational_amendments/future_memory_scope_sync_v1/scope_sync.py');tiny_mod=load('actual_tinybeec',R/'control/operational_amendments/future_memory_aging_facade_v1/facade_memory.py');resmod=load('actual_res',R/'tools/l2_resources.py')
canaryrow=q['consumed'].pop(CANARY);q['remaining']+=1
reference=next(iter(q['consumed']));specs={c:read(R/'control/specs'/(c+'.json'))for c in(CANARY,reference)}
for c,cost in[(BIG,100*G),(SMALL,20*G)]:specs[c]=dict(copy.deepcopy(specs[CANARY]),cohort=c,estimated_peak_model_RAM_bytes=cost)
for c,s in specs.items():put(root/'control/specs'/(c+'.json'),s);q['admitted_specs'][c]=sha(root/'control/specs'/(c+'.json'))
engine=types.SimpleNamespace(registered=lambda:({}, {},q,{}),canonical=lambda c:copy.deepcopy(specs[c]),assert_parent_lease=lambda:None)
matrix=read(R/'control/MATRIX_CURRENT.json');template=next(p for p in matrix['points']if p['cohort']==CANARY)
matrix['points']+=[dict(template,cohort=c)for c in(BIG,SMALL)];put(root/'control/MATRIX_CURRENT.json',matrix);put(root/'control/ACTUAL_CANARY_QUALIFICATION.json',read(R/'control/ACTUAL_CANARY_QUALIFICATION.json'))
calls=[];claims={}
def raw(s,fresh_source=False):
 own=[dict(cohort=reference,RSS_bytes=G,additional_reserved_bytes=G,kind='SPENT_UNRESOLVED_GENERATION')]
 if s['cohort']in(BIG,SMALL):own.append(dict(cohort=s['cohort'],RSS_bytes=0,additional_reserved_bytes=specs[s['cohort']]['estimated_peak_model_RAM_bytes'],kind='CLAIM_OR_CANDIDATE'))
 v=copy.deepcopy(f.base);v['own_ram_forecasts']=own;v['RAM_reservation_entries']=[];total=sum(r['additional_reserved_bytes']for r in own);v['total_projected_additional_RAM_bytes']=total
 v.update(cgroup_effective_headroom_bytes=96*G,host_MemAvailable_bytes=128*G,monotonic=__import__('time').monotonic());v['admission_decision'].update(additional_reserved_RAM_bytes=total,admission_RAM_budget_bytes=int(.88*88*G));return v
def forecast(s,h,policy=None):return dict(predicted_peak_RAM_bytes=s['estimated_peak_model_RAM_bytes'],historical_elapsed_seconds=10000 if s['cohort']==BIG else 100)
res=types.SimpleNamespace(resources=raw,forecast=forecast,cpu_candidates=resmod.cpu_candidates)
def oldchoose(pending,*args,**kw):calls.append(('OLD_GENERIC',tuple(s['cohort']for s in pending)));return None
consumer=types.SimpleNamespace(load=lambda n,f:types.SimpleNamespace(terminal=lambda c:dict(performance_accepted=False)),accepted=lambda v:False)
facade=types.SimpleNamespace(resources=raw,forecast=forecast);frames=frames_mod.RuntimeFrames(root,engine,facade,consumer,lambda v:v['own_ram_forecasts'],observe=lambda*c:None,generation=lambda*c:None)
aging=aging_mod.AgingChooser(oldchoose,frames);guard=guard_mod.FrameReadGuard(aging)
def outer(*args,**kw):return guard.wrapper(*args,**kw)
res.choose_dispatch=outer;res.DTC_LARGE_JOB_AGING_INSTALLED=aging
def plain(c):calls.append(('NO_PADDING',c));return dict(state='CPU_ONLY_NO_MODEL')
def padding(c):calls.append(('PADDING',c));return dict(state='CPU_ONLY_NO_MODEL')
frame=types.SimpleNamespace(f_locals=dict(engine=engine,res=res,consumer=consumer,registry=types.SimpleNamespace(),claims=claims,pool=object(),max_workers=384),f_globals=dict(worker=padding))
main=sys.modules['__main__'];setattr(main,owner.PADDING,dict(worker=plain));oldowner.install_on_frame(frame,f.old,aging,lambda:None);memory=getattr(main,owner.MEMORY)
setattr(main,'DTC_L2_MLP_INSTALLED_AGING_V1',dict(frames=frames,chooser=aging));cell=(lambda x:lambda:x)(guard.wrapper).__closure__[0];setattr(main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1',dict(gate=guard,aging=aging,cpu=dict(wrapper=outer,original=guard.wrapper),cell=cell))
tcfg=read(R/'control/operational_amendments/future_memory_aging_facade_v1/INSTALL.json');tcfg['memory_active_path']=str(root/'ACTIVE.json');put(root/'tiny.json',tcfg);put(root/'ACTIVE.json',f.old)
tiny=tiny_mod.FacadeMemory(main,root/'tiny.json');facade.resources=tiny.wrapper;setattr(main,owner.TINY,tiny)
scfg=read(R/'control/operational_amendments/future_memory_scope_sync_v1/INSTALL.json');scfg.update(root=str(root),directory=str(root/'sync'),memory_active_path=str(root/'ACTIVE.json'));put(root/'sync.json',scfg)
journal=types.SimpleNamespace(check=lambda:({}, {},q,{}),extend=lambda p:[],registry=frame.f_locals['registry']);journal.registry.extend=journal.extend
sync=scope_mod.ScopeSync(frame,root/'sync.json',journal,memory,lambda p:None);setattr(main,owner.SYNC,sync)
put(root/'ACTIVE.json',previous);cpu1.install_on_frame(frame,previous,aging,lambda:None)
q['consumed'][CANARY]=canaryrow;q['remaining']-=1 # private chronology only, not real refund/retry
before=dict(memory);refs=(res.resources,aging.original,consumer.load,frame.f_globals['worker'],facade.resources,tiny.lib,sync.owner_module)
put(root/'ACTIVE.json',cfg);owner.install_on_frame(frame,cfg,aging,lambda:None)
checks=[]
def ck(n,b):assert b,n;checks.append(n)
ck('actual332 CPU1 generation replaced directly without blind348 restore',memory['generation_history'][-1]['saved']['context']is before['context'])
ck('actual Scope22f/Tinybeec accept same dictionary CPU2 generation',sync.stable_memory()[1]==cfg and tiny.guard()==cfg and sync.memory is memory is tiny.memory)
sample=resmod.sample_system();pending=[engine.canonical(BIG),engine.canonical(SMALL)]
decision=aging.original(pending,sample,claims,{},None,None,0)
ck('larger first candidate full RAM HOLD does not block later fitting pending point',decision is not None and decision['cohort']==SMALL and decision['cpu_spare_priority']['earlier_resource_holds'][0]['cohort']==BIG)
ck('new mode is per cohort and not singleton',decision['cpu_spare_owner_proof']['mode']=='CPU_SPARE_PER_COHORT')
ck('actual frames preserve provider but allow eligible supplied pool witness',not frames(pending,sample,claims,{},None,{},0)['pressure_reasons']and aging.frame_provider is frames)
ck('no eligible supplied pending leaves original CPU pressure unchanged',frames([],sample,claims,{},None,{},0)['pressure_reasons']==['cpu_pressure_full'])
frame.f_globals['worker'](SMALL);ck('all eligible new points use stable NO_PADDING leaf not previous CPU1 wrapper',calls[-1]==('NO_PADDING',SMALL))
q['consumed'][SMALL]=dict(uuid='CPU2_PRIVATE_SPENT');ck('consumed point cannot reenter exception',not lib.eligible_cohort(cfg,q,SMALL,'OWNER_CHOOSE',claims));q['consumed'].pop(SMALL)
ck('new private qualification receipt cannot validate actual unmarked Main q',bool(cfg['qualification_only'])and q['qualification_only'])
badq=copy.deepcopy(q);badq.pop('qualification_only')
try:lib.validate(cfg,badq)
except Exception:failed=True
else:failed=False
ck('private canary standin rejected when live-q qualification flag absent',failed)
future='CPU2_PRIMARY_THIRD';expanded=copy.deepcopy(cfg);expanded['allowed_cohorts'].append(future);q['admitted_specs'][future]='CPU2_FIXTURE_ONLY_SPEC'
q['additional_operational_overlays'][lib.ID]=dict(lib.record(expanded),status='ACTIVE');put(root/'ACTIVE.json',expanded)
sync.owner_module.update_scope_in_owner(expanded,lambda:None)
ck('existing Scope22f append extends the only allowlist with same CPU policy and approval',sync.stable_memory()[1]==expanded and lib.eligible_cohort(expanded,q,future,'OWNER_CHOOSE',claims))
tampered=copy.deepcopy(expanded);alternate=root/'ALTERNATE_CANARY_RECEIPT.json';alternate.write_bytes(P(cfg['canary_qualification_path']).read_bytes());tampered['canary_qualification_path']=str(alternate)
q['additional_operational_overlays'][lib.ID]=dict(lib.record(tampered),status='ACTIVE')
try:sync.owner_module.update_scope_in_owner(tampered,lambda:None)
except AssertionError:failed=True
else:failed=False
ck('scope append cannot change approval path even when bytes and qrecord match',failed and memory['context']['cfg']==expanded)
q['additional_operational_overlays'][lib.ID]=dict(lib.record(expanded),status='ACTIVE')
owner.restore_in_owner(lambda:None);put(root/'ACTIVE.json',previous)
ck('exact CPU1 dispatch and facade refs restored except retained multi-generation consumer',refs[:2]==(res.resources,aging.original)and refs[3:]==(frame.f_globals['worker'],facade.resources,tiny.lib,sync.owner_module))
ck('CPU1 and CPU2 receipts remain consumable by retained snapshot dispatcher',consumer.load is memory['retained_cpu_generation_consumer'])
ck('restored actual Scope/Tiny guard CPU1 again',sync.stable_memory()[1]==previous and tiny.guard()==previous)
out=dict(status='PASS',count=len(checks),checks=checks,fixture_root=str(root),models_started=0,new_grants=0,production_changes=0,
 sources={str(p):sha(p)for p in(P(lib.__file__),H/'cpu_owner.py',H/'cpu_extra_strict.py',P(cpu1.__file__),P(scope_mod.__file__),P(tiny_mod.__file__))},
 qualification_only=True,live_canary_acceptance_claimed=False,real_host_CPU_sampler_used=True,
 caveat='Actual unchanged CPU1/Scope/Tiny/RuntimeFrames and new CPU2 library, controlled RAM/authority chronology and explicit canary stand-in; no deployment or GPU result')
put(H/'OWNER_CPU_QUALIFICATION.json',out);print(json.dumps(out))
