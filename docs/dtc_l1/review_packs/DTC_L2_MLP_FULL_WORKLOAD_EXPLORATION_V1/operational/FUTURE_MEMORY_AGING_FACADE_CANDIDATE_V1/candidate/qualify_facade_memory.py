"""Focused CPU qualification with real RuntimeFrames/AgingChooser/FrameGuard,
real qualified memory library and B5 effective_own_rows. No actual owner/model.
"""
from pathlib import Path as P
import json,copy,hashlib,types,tempfile,threading,sys,importlib.util,os,time
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');D=P(__file__).parent;M=R/'control/operational_amendments/future_memory_admission_v1';A=R/'control/operational_amendments/large_job_aging_v1';F=R/'control/operational_amendments/frame_read_guard_v1';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('tiny_facade_candidate',D/'facade_memory.py');rt=load('real_runtime_frames_for_tiny',A/'aging_runtime_frames.py');ag=load('real_aging_for_tiny',A/'large_job_aging.py');fg=load('real_guard_for_tiny',F/'frame_read_guard.py');lib=load('real_memory_for_tiny',M/'future_memory.py');padding=load('real_B5_effective_rows_for_tiny',R/'control/operational_amendments/padding_only_v1/padding_overlay.py')
root=P(tempfile.mkdtemp(prefix='CPU_AGING_FACADE_',dir=D));main=sys.modules['__main__'];checks=[]
def ck(n,v):assert v,n;checks.append(n)
def reject(n,fn):
 try:fn()
 except(AssertionError,fg.FrameUnavailable):checks.append(n);return
 raise AssertionError(n+' not refused')
active=read(M/'ACTIVE_MEMORY.json');active.update(scope_mode='ALL_UNSPENT_FUTURE');mempath=root/'ACTIVE_MEMORY.json';put(mempath,active)
q=dict(request=lib.REQ,admitted_specs={c:'CPU_ONLY_CANONICAL'for c in active['allowed_cohorts']},consumed={'LIVE':dict(uuid='CPU_LIVE_UUID')},additional_operational_overlays={lib.ID:dict(lib.record(active),status='ACTIVE',production_installation_pending=False,publication_commit='CPU_fixture_original_provenance')})
plan=dict(parent_pid=os.getpid(),parent_start_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]));engine=types.SimpleNamespace(registered=lambda:(None,None,q,plan),assert_parent_lease=lambda:dict(CPU_FIXTURE=True))
for c in ['LIVE','CLAIM','CANDIDATE']:q['admitted_specs'][c]='CPU_ONLY_CANONICAL'
put(root/'control/MATRIX_CURRENT.json',dict(points=[dict(cohort=c,input_digest=c+'_INPUT',program=c)for c in ['LIVE','CLAIM','CANDIDATE']]))
(root/'control/ACTUAL_CANARY_QUALIFICATION.json').write_bytes((R/'control/ACTUAL_CANARY_QUALIFICATION.json').read_bytes())
rows=[dict(cohort='LIVE',kind='LIVE_MODEL',RSS_bytes=G,additional_reserved_bytes=10*G),dict(cohort='CLAIM',kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=2*G)]
padproof=dict(base_own_growth_rows=rows,discount_rows=[dict(cohort='LIVE',discount_bytes=4*G)],claim_candidate_topups=[],effective_total_additional_RAM_bytes=11*G)
base=dict(host_MemAvailable_bytes=100*G,cgroup_effective_headroom_bytes=120*G,native_free_bytes=50*G,required_free_bytes=5*G,free_inodes=1000000,monotonic=1,utc='CPU_ONLY',source_module_sha256=sha(R/'tools/l2_resources.py'),policy_sha256=sha(R/'control/RESOURCE_POLICY.json'),physical_RAM_pass=True,physical_disk_pass=True,own_write_ceiling_pass=True,total_projected_additional_RAM_bytes=11*G,own_ram_forecasts=rows,RAM_reservation_entries=[dict(additional_reserved_bytes=3*G)],additional_padding_admission_proof=padproof,admission_decision=dict(memory_utilization_fraction=.88,admission_RAM_budget_bytes=int(.88*92*G),additional_reserved_RAM_bytes=11*G,pressure_reasons=[],pass_admission=True))
state=dict(mode='BASE',calls=0);runtime=dict(EXACT_OLD_RUNTIME=True)
def original(s,fresh_source=False):
 if not fresh_source:return runtime
 state['calls']+=1
 if state['mode']=='ERROR':raise json.JSONDecodeError('CPU read fault','',0)
 if state['mode']=='PROJECTED':return lib.project(base)
 return base
def forecast(s,h,p):return dict(predicted_peak_RAM_bytes=12*G)
facade=types.SimpleNamespace(resources=original,forecast=forecast)
consumer=types.SimpleNamespace(accepted=lambda result:False)
frames=rt.RuntimeFrames(root,engine,facade,consumer,padding.effective_own_rows,observe=lambda c,u:dict(pid=99999901,start_ticks=1,anon_PSS_bytes=G,PSS_sample_monotonic=time.monotonic()),generation=lambda c,u:dict(pid=99999901,start_ticks=1))
pending=[dict(cohort='CANDIDATE',input_digest='CANDIDATE_INPUT',program='CPU_PROGRAM',cell='DH',profile='Q64',estimated_peak_model_RAM_bytes=9*G)]
def generic(*args,**kw):return dict(cohort='CANDIDATE')
aging=ag.AgingChooser(generic,frames);aging.state.previous_C=base['admission_decision']['admission_RAM_budget_bytes']-base['total_projected_additional_RAM_bytes'];aging.state.protected=3*G;aging.state.pending_releases={('CPU_PENDING','CPU_UUID'):dict(raw_release_bytes=2*G,realized_credit_bytes=G)}
gate=fg.FrameReadGuard(aging,sleeper=lambda _:None);aging.wrapper=gate.wrapper
cell=(lambda original:(lambda:original))(gate.wrapper).__closure__[0];cpu=dict(wrapper=lambda *a:gate.wrapper(*a),original=gate.wrapper)
global_resource=lib.wrap_resources(original);global_choose=lambda *a:cpu['wrapper'](*a);globalres=types.SimpleNamespace(resources=global_resource,choose_dispatch=global_choose)
context=dict(cfg=active);memory=dict(lib=lib,context=context,res=globalres,aging=aging,new_resources=global_resource,new_choose=generic)
setattr(main,m.MEMORY,memory);setattr(main,'DTC_L2_MLP_INSTALLED_AGING_V1',dict(frames=frames,chooser=aging,res=globalres));setattr(main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1',dict(gate=gate,aging=aging,cpu=cpu,cell=cell))
# Explicit identities for already-installed SYNC and E guard are sentinels only;
# the candidate never reads/replaces either installed marker or callable.
sync_sentinel=object();E_guard=object();setattr(main,'DTC_FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_V1',sync_sentinel);setattr(main,'CPU_EXISTING_E_GUARD',E_guard)
deps={str(p):sha(p)for p in [A/'aging_runtime_frames.py',A/'large_job_aging.py',F/'frame_read_guard.py',F/'cpu_outer_coupling.py',R/'control/operational_amendments/padding_only_v1/padding_overlay.py',*[P(active[r+'_path'])for r in lib.ROLES]]};pin=root/'DRIFT_PIN';pin.write_text('stable');deps[str(pin)]=sha(pin)
qa=root/'CPU_FIXTURE_QA.json';back=root/'CPU_FIXTURE_READBACK.json';join=dict(source_sha256=sha(D/'facade_memory.py'),dependency_pins=deps);put(qa,dict(join,status='PASS',real_RuntimeFrames_FrameGuard_qualified=True,CPU_FIXTURE_ONLY=True));put(back,dict(join,verified=True,QA_sha256=sha(qa),CPU_FIXTURE_ONLY=True))
cfg=dict(status='ACTIVE_OPERATIONAL_ONLY',request=lib.REQ,overlay_id=m.ID,source_path=str(D/'facade_memory.py'),source_sha256=sha(D/'facade_memory.py'),QA_path=str(qa),QA_sha256=sha(qa),readback_path=str(back),readback_sha256=sha(back),dependency_pins=deps,memory_active_path=str(mempath));cfgpath=root/'INSTALL.json';put(cfgpath,cfg);q['additional_operational_overlays'][m.ID]=m.record(cfg)
args=(pending,{}, {'CLAIM':dict(CPU_ONLY=True)}, {}, None,{},0)
before=frames(*args);old_previous=aging.state.previous_C;R_before=aging.state.protected;tokens=copy.deepcopy(aging.state.pending_releases);proof=m.install_in_owner(cfgpath);obj=getattr(main,m.MARKER);after=frames(*args)
ck('real_existing_RuntimeFrames_fraction_changes_088_to_095',before['memory_utilization_fraction']==.88 and after['memory_utilization_fraction']==.95 and after['budget_bytes']==lib.budget(base))
ck('full_peer_own_claim_growth_discounts_and_candidate_forecast_unchanged',all(before[k]==after[k]for k in ['effective_total_growth_bytes','total_padding_discount_bytes','padding_discount_by_cohort','accounted_growth_by_cohort','claim_cohorts','pending'])and after['pending'][0]['cost_bytes']==12*G and after['effective_total_growth_bytes']==11*G)
ck('previousC_rebased_without_R_or_pending_release_credit',aging.state.previous_C==lib.budget(base)-11*G and proof['previous_C_before']==old_previous and proof['policy_change_release_credit_bytes']==0 and aging.state.protected==R_before and aging.state.pending_releases==tokens)
ck('exact_original_freshFalse_object_and_global_owner_resource_identity_preserved',facade.resources({},False)is runtime and globalres.resources is global_resource and globalres.choose_dispatch is global_choose)
ck('RuntimeFrames_provider_CPU_FrameGuard_SYNC_Eguard_objects_unchanged',aging.frame_provider is frames and gate.original_provider is frames and cpu['original']is gate.wrapper and cell.cell_contents is gate.wrapper and getattr(main,'DTC_FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_V1')is sync_sentinel and getattr(main,'CPU_EXISTING_E_GUARD')is E_guard)
ck('actual_FrameGuard_and_Echooser_use95_frame',gate.wrapper(*args)is not None and frames.last_frame['memory_utilization_fraction']==.95)
oldactive=context['cfg'];finite=copy.deepcopy(oldactive);finite.update(scope_mode='FINITE_CANARY',allowed_cohorts=[oldactive['allowed_cohorts'][0]]);context['cfg']=finite;put(mempath,finite);q['additional_operational_overlays'][lib.ID].update(lib.record(finite))
ck('FINITE_snapshot_is_exact_original_object_and_frame_088',facade.resources({},True)is base and frames(*args)['memory_utilization_fraction']==.88)
context['cfg']=oldactive;put(mempath,oldactive);q['additional_operational_overlays'][lib.ID].update(lib.record(oldactive));state['mode']='PROJECTED';projected=facade.resources({},True);ck('already95_snapshot_not_double_projected_or_nested',projected['admission_decision']['memory_utilization_fraction']==.95 and 'additional_future_memory_admission_proof'not in projected['additional_future_memory_admission_proof']['base_resource_snapshot']);state['mode']='BASE'
newcfg=copy.deepcopy(oldactive);newcfg['allowed_cohorts'].append('CPU_NEW_PROFILE');q['admitted_specs']['CPU_NEW_PROFILE']='CPU_ONLY';context['cfg']=newcfg;put(mempath,newcfg);q['additional_operational_overlays'][lib.ID].update(lib.record(newcfg));ck('legitimate_append_only_context_scope_update_remains_compatible',frames(*args)['memory_utilization_fraction']==.95)
before_state=copy.deepcopy(aging.state.__dict__);calls=aging.calls;pin.write_text('drift');result=gate.wrapper(*args);ck('source_drift_raises_exact_FrameUnavailable_and_original_Guard_rolls_back',result is None and gate.last_issue['status']=='AGING_FACADE_SOURCE_OR_MEMORY_CONFIG_INVALID'and aging.state.__dict__==before_state and aging.calls==calls);pin.write_text('stable')
q['additional_operational_overlays'][m.ID]['source_sha256']='wrong';ck('own_operational_record_mismatch_failclosed_through_real_Guard',gate.wrapper(*args)is None and gate.last_issue['status']=='AGING_FACADE_SOURCE_OR_MEMORY_CONFIG_INVALID');q['additional_operational_overlays'][m.ID]=m.record(cfg)
state['mode']='ERROR';calls=aging.calls;before_state=copy.deepcopy(aging.state.__dict__);ck('original_transient_three_read_retries_preserved_and_rollback',gate.wrapper(*args)is None and gate.last_issue['attempts']==3 and aging.calls==calls and aging.state.__dict__==before_state);state['mode']='BASE'
pressure=base['admission_decision']['pressure_reasons'];base['admission_decision']['pressure_reasons']=['CPU_PSI'];v=facade.resources({},True);ck('pressure_and_physical_HOLD_not_forged_away',v['physical_RAM_pass']is False and v['admission_decision']['pressure_reasons']==['CPU_PSI']and frames(*args)['pressure_reasons']==['CPU_PSI']);base['admission_decision']['pressure_reasons']=pressure
base['physical_disk_pass']=False;v=facade.resources({},True);ck('disk_guard_fields_preserved',v['physical_disk_pass']is False and v['required_free_bytes']==base['required_free_bytes']);base['physical_disk_pass']=True
oldfacade=facade.resources;facade.resources=lambda *a:None;reject('restore_refuses_newer_facade_wrapper',lambda:m.restore_in_owner());facade.resources=oldfacade
restored=m.restore_in_owner();ck('exact_restore_old_facade_and_rebase_without_R_or_token_changes',facade.resources is original and aging.state.previous_C==base['admission_decision']['admission_RAM_budget_bytes']-base['total_projected_additional_RAM_bytes']and restored['policy_change_release_credit_bytes']==0 and aging.frame_provider is frames and globalres.resources is global_resource)
ck('MEM6_and_native46_bytes_unchanged',all(sha(active[r+'_path'])==active[r+'_sha256']for r in lib.ROLES)and sha(P('/root/data/ep_l2_dtc_l1_native_v2/bin/native'))=='46c69a74154e0690afd82324a348da236baf90189d9a7e474b4b14eb01ab4f0e')
report=dict(status='PASS',schema='FUTURE_MEMORY_AGING_FACADE_FOCUSED_CPU_V1',real_RuntimeFrames_FrameGuard_qualified=True,checks=checks,passed=len(checks),source_sha256=sha(D/'facade_memory.py'),driver_sha256=sha(__file__),cpu_process_pid=os.getpid(),cpu_process_start_ticks=plan['parent_start_ticks'],dependency_pins={p:h for p,h in deps.items()if p!=str(pin)},fixture=str(root),real_frozen_interfaces=['RuntimeFrames','AgingChooser','FrameReadGuard','B5.effective_own_rows','MEM.library.project/validate'],authority_resources_CPU_and_existing_SYNC_Eguard_sentinels_are_explicit_fixtures=True,actual_owner_attached=False,production_mutations=0,model_starts=0,signals=0)
put(D/'CPU_QUALIFICATION.json',report);print(json.dumps(dict(status='PASS',checks=len(checks),source_sha256=report['source_sha256'],path=str(D/'CPU_QUALIFICATION.json'))))
