"""Focused real RuntimeFrames/FrameGuard/AgingChooser interface qualification.
Authority, physical resource samples and model observations are private fixtures.
"""
import pathlib as P,json,hashlib,copy,types,importlib.util,time,threading,traceback
D=P.Path(__file__).parent;R=P.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1');S=types.SimpleNamespace
def read(p):return json.loads(P.Path(p).read_bytes())
def sha(p):return hashlib.sha256(P.Path(p).read_bytes()).hexdigest()
def put(p,v):p=P.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
fx=load('broad_frame_fixture',D/'cpu_fixture.py');f=fx.fixture();lib=f.lib;helper=load('broad_frame_adapter',D/'owner_frame.py');cfg=f.cfg;q=f.q
cfg['expected_pins'][str(D/'owner_frame.py')]=sha(D/'owner_frame.py')
for role,p in [('QA',cfg['QA_path']),('readback',cfg['readback_path'])]:
 v=read(p);v['expected_pins']=cfg['expected_pins']
 if role=='readback':v['QA_sha256']=sha(cfg['QA_path'])
 put(p,v);cfg[role+'_sha256']=sha(p)
q['additional_operational_overlays'][lib.ID]=dict(lib.record(cfg),status='ACTIVE');lib.validate(cfg,q)
frpath=R/'control/operational_amendments/large_job_aging_v1/aging_runtime_frames.py';apath=frpath.with_name('large_job_aging.py');gpath=R/'control/operational_amendments/frame_read_guard_v1/frame_read_guard.py'
fr=load('real_broad_RuntimeFrames',frpath);am=load('real_broad_AgingChooser',apath);gm=load('real_broad_FrameGuard',gpath);resmod=load('real_broad_forecast',R/'tools/l2_resources.py')
matrix=read(R/'control/MATRIX_CURRENT.json');put(f.root/'control/MATRIX_CURRENT.json',matrix);put(f.root/'control/ACTUAL_CANARY_QUALIFICATION.json',{'qualification_only':True})
engine=S(registered=lambda:(None,None,q,{}),assert_parent_lease=lambda:None)
oldcalls=[];base_factory=[lambda:f.base()]
def leaf(spec,fresh=False):
 oldcalls.append(('TINY_LEAF',spec['cohort'],fresh));b=base_factory[0]();b['utc']='CPU_ONLY_RUNTIME_FRAME';return lib.project(b)
def oldfacade(spec,fresh=False):oldcalls.append(('CURRENT_CPU2_HELPER',spec['cohort'],fresh));return leaf(spec,fresh)
facade=S(resources=oldfacade,forecast=resmod.forecast)
frames=fr.RuntimeFrames(f.root,engine,facade,consumer=S(accepted=lambda v:False),effective_rows=lambda x:x['own_ram_forecasts'],observe=lambda c,u:None,generation=lambda c,u:None)
frames.assert_owner=lambda:None;frames.first_eligible=time.monotonic()-4000
leaf_calls=[]
def choose_leaf(pending,*a,**kw):
 leaf_calls.append([s['cohort']for s in pending]);return None if not pending else dict(cohort=pending[0]['cohort'],host_cpu=0)
aging=am.AgingChooser(choose_leaf,frames);gate=gm.FrameReadGuard(aging,sleeper=lambda seconds:None)
cpu_wrapper=object();cpu_original=object();memory={'aging':aging,'context':{'cfg':{'FROZEN_CPU2_ALLOWED43':'UNCHANGED'}},'res':object()}
tiny=S(frames=frames,facade=facade,aging=aging,engine=engine,memory=memory,wrapper=leaf,coupling={'gate':gate,'cpu':{'wrapper':cpu_wrapper,'original':cpu_original}})
main=S(DTC_FUTURE_MEMORY_AGING_FACADE_095_V1=tiny,DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1=memory)
sched=S(f_locals={'engine':engine,'res':S(DTC_LARGE_JOB_AGING_INSTALLED=aging)})
sampled_threads=[]
def sampler(selected_cpu=None,sample_seconds=.5,prospective_cpu_threads=1):
 sampled_threads.append(prospective_cpu_threads);return f.cpu(selected_cpu,prospective_cpu_threads)
lib.sample_cpu_evidence=sampler;lib.capture_legal_cpu_evidence=f.legal
beforememory=copy.deepcopy(memory['context']);beforeglobal=sha(R/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json');protected=21*lib.G;aging.state.protected=protected;aging.state.pending_releases={('CPU_ONLY','UUID'):{'realized_credit_bytes':17}}
state=helper.install_on_frame(sched,cfg,lib,lambda:None,main=main);assert memory['context']==beforememory and aging.state.protected==protected and aging.state.pending_releases=={('CPU_ONLY','UUID'):{'realized_credit_bytes':17}}
checks=[]
def check(name,fn):
 try:details=fn();checks.append(dict(name=name,status='PASS',details=details))
 except BaseException as e:checks.append(dict(name=name,status='FAIL',error=repr(e),traceback=traceback.format_exc()))
hist=read(R/'control/HISTORICAL_RSS.json');policy=read(R/'control/RESOURCE_POLICY.json');contract=read(cfg['scope_contract_path']);IR=next(r['cohort']for r in contract['rows']if r['role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL');IRspec=read(f.root/'control/specs'/(IR+'.json'))
def real_IR():
 snapshot=frames([IRspec],{},f.claims,hist,None,policy,0)
 assert snapshot['pending'][0]['cohort']==IR and snapshot['memory_utilization_fraction']==.95 and snapshot['pressure_reasons']==[]
 assert state['eligible_pending_witnesses']==[IR]and sampled_threads[-1]==2
 assert frames is tiny.frames and frames.res is facade and gate.original_provider is frames and aging.frame_provider is frames
 return dict(real_RuntimeFrames_IR_not_in_old43=True,CPU_full_removed_only_under_new_proof=True,old_objects_and_global_context_preserved=True,explicit_otherclaim_plus_candidate_CPU_sample_threads=sampled_threads[-1])
check('real_RuntimeFrames_IR11_pending_dynamic_frame_scope',real_IR)
def guarded_E():
 # Existing E does one advance and hands the exact target/backfill subpool to
 # the replacement leaf; old leaf is a stand-in, not a dispatch/Popen.
 lav=next(c for c in cfg['allowed_cohorts']if c.startswith('E2-DTCL2MLP-ddb6806316876a85')and'-IR1-'not in c)
 sp=read(f.root/'control/specs'/(lav+'.json'));pending=[sp,IRspec]
 targetcost=max(sp['estimated_peak_model_RAM_bytes'],resmod.forecast(sp,hist,policy)['predicted_peak_RAM_bytes'])
 aging.state.target=dict(cohort=lav,cost_bytes=targetcost,program=sp['program'],first_eligible_monotonic=frames.first_eligible)
 aging.state.protected=20*lib.G;aging.state.pending_releases={};before=aging.calls
 value=gate.choose(pending,{},f.claims,hist,None,policy,1)
 assert value is not None and value['cohort']==lav and aging.calls==before+1
 assert leaf_calls[-1]==[lav]and value['large_job_aging']['offer_target_first']==lav
 assert aging.state.policy['protect_fraction']==.75 and value['large_job_aging']['candidate_costs_unmodified']is True
 assert gate.last_pass_status=='VALID_FRESH_FRAMES'and aging.frame_provider is frames
 return dict(one_advance=True,large_Lava_offered_first=True,fresh_FrameGuard_second_frame_valid=True,protect_fraction=.75,candidate_cost_not_discounted=True)
check('real_FrameGuard_E75_target_first_IR_fullpending_one_advance',guarded_E)
def failclosed():
 old=copy.deepcopy(aging.state.__dict__);calls=aging.calls
 # Config drift must raise the existing exact FrameUnavailable caught by guard,
 # with no stale frame/release token/call count retained.
 cfg['host_floor_bytes']-=1
 try:value=gate.choose([IRspec],{},f.claims,hist,None,policy,2)
 finally:cfg['host_floor_bytes']+=1
 assert value is None and gate.last_pass_status=='FAILCLOSED_FRAME_UNAVAILABLE'and aging.calls==calls and aging.state.__dict__==old
 assert state['last_issue']['status']=='BROAD_SHARED_FRAME_SOURCE_OR_RESOURCE_HOLD'
 return dict(exact_FrameUnavailable_class=True,aging_state_calls_rollback=True,healthy_models_untouched=True)
check('actual_FrameGuard_source_config_drift_rolls_back',failclosed)
def delegates():
 count=len(oldcalls);result=facade.resources({'cohort':'NON_RUNTIME_CALL'},True);assert oldcalls[count][0]=='CURRENT_CPU2_HELPER'and lib.PROOF not in result
 count=len(oldcalls);facade.resources({'cohort':'RUNTIME_FALSE'},False);assert oldcalls[count]==('CURRENT_CPU2_HELPER','RUNTIME_FALSE',False)
 # No new identities in pending: actual RuntimeFrames follows exact current facade.
 primary=next(p for p in matrix['points']if p['cohort']not in cfg['allowed_cohorts']);p=read(R/'control/specs'/(primary['cohort']+'.json'))
 count=len(oldcalls);frames([p],{},f.claims,hist,None,policy,0);assert any(row[0]=='CURRENT_CPU2_HELPER'for row in oldcalls[count:])
 original=state['original'];restored=helper.restore_owner_frame(state,lambda:None);assert facade.resources is original and not state['enabled']
 assert memory['context']==beforememory and sha(R/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json')==beforeglobal
 assert tiny.coupling['cpu']['wrapper']is cpu_wrapper and tiny.coupling['cpu']['original']is cpu_original and gate.original_provider is frames
 return dict(nonruntime_freshFalse_nonnew_exact_delegate=True,exact_restore=True,global_CPU2_ACTIVE_and_context_unchanged=True,FrameGuard_CPU_refs_unchanged=True)
check('exact_nonnew_false_delegation_restore_and_global_generation_unchanged',delegates)
result=dict(schema='BROAD_SHARED_OWNER_FRAME_REAL_INTERFACE_CPU_QUALIFICATION_V1',status='PASS'if all(c['status']=='PASS'for c in checks)else'FAIL',source_path=str(D/'owner_frame.py'),source_sha256=sha(D/'owner_frame.py'),library_source_sha256=sha(D/'cpu_shared.py'),checks=checks,count=len(checks),driver_sha256=sha(__file__),fixture_root=str(f.root),real_source_pins={str(p):sha(p)for p in[frpath,apath,gpath]},physical_resource_CPU_authority_model_observation='PRIVATE_FIXTURES_NOT_ACTUAL_OWNER',old_global_memory_unchanged=True,actual_models_started=0,production_mutations=0,new_grants=0,signals=0)
put(D/'OWNER_FRAME_CPU_QUALIFICATION.json',result);print(json.dumps(dict(status=result['status'],source_sha256=result['source_sha256'],QA_sha256=sha(D/'OWNER_FRAME_CPU_QUALIFICATION.json'),cases=[(c['name'],c['status'],c.get('error'))for c in checks]),indent=2))
