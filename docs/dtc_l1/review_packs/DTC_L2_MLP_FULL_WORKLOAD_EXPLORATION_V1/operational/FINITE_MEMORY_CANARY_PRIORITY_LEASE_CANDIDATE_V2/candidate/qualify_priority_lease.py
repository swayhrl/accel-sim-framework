"""Actual frozen E/B5/f3/CPU/FrameGuard/a650/memory348 private CPU fixture.
Authority/resources are synthetic; zero owner attach, model, signal or install.
"""
from fixture_setup import setup,load,R,C,T,G,P,read,sha,put
import copy,json,sys,threading,time
D=P(__file__).parent;f=setup();m=load('finite_canary_lease_qualification',D/'priority_lease.py');checks=[]
def ck(n,v):
 if not v:raise AssertionError(n+' '+repr(getattr(adapter,'last_hold',None)))
 checks.append(n)
def reject(n,fn):
 try:fn()
 except(AssertionError,RuntimeError,KeyError):checks.append(n);return
 raise AssertionError(n+' not refused')
# Install the exact actual a650 preference around captured B5/f3 before the
# published memory348 generic wrapper, mirroring current production lineage.
prefcfg=read(R/'control/operational_amendments/p0_dependency_preference_v1/INSTALL_CONFIG.json')
prefmod=load('canary_actual_a650',prefcfg['source_path']);prefpins={x['path']:x['sha256']for x in f.plan['source_pins']}
pref=prefmod.Preference(f.aging.original,f.engine,prefpins,f.root)
f.q['additional_operational_overlays'][prefmod.ID]=dict(status='ACTIVE',source_sha256=sha(prefcfg['source_path']))
pref.install(f.aging,lambda:None)
M=R/'control/operational_amendments/future_memory_admission_v1';memcfg=read(M/'ACTIVE_MEMORY.json');lib=load('canary_actual_memory_lib',memcfg['library_path']);owner=load('canary_actual_memory_owner',memcfg['owner_path'])
f.q['additional_operational_overlays'][lib.ID]=dict(lib.record(memcfg),status='ACTIVE')
owner.install_on_frame(f.frame,memcfg,f.aging,lambda:None)
f.sample.update(host_MemAvailable_bytes=149*G,cgroup_effective_headroom_bytes=149*G)
op=f.root/'control/operational_amendments/memory_canary_priority_lease_v1';op.mkdir(parents=True);tokens=op/'attempts';tokens.mkdir()
deps=copy.deepcopy(f.scope['dependency_pins']);deps.update({str(M/n):sha(M/n)for n in ['future_memory.py','memory_owner.py','memory_frontend.py','memory_extra_strict.py','joint_padding_strict.py','joint_io_strict.py']});deps[prefcfg['source_path']]=sha(prefcfg['source_path'])
extra=f.root/'SOURCE_PIN.txt';extra.write_text('stable');deps[str(extra)]=sha(extra)
cfg=dict(status='ACTIVE_FUTURE_ONLY',request=m.REQ,overlay_id=m.ID,root=str(f.root),source_path=str(D/'priority_lease.py'),source_sha256=sha(D/'priority_lease.py'),dependency_pins=deps,allowed_cohorts=[C],priority_only=True,token_directory=str(tokens),atomic_helper_path=str(R/'control/operational_amendments/shared_json_io_v1/shared_json_io.py'),memory_active_path=str(M/'ACTIVE_MEMORY.json'),memory_active_sha256=sha(M/'ACTIVE_MEMORY.json'))
private_memory_cfg=op/'ACTUAL_MEMORY_SCOPE_CPU_SNAPSHOT.json';put(private_memory_cfg,memcfg);cfg['memory_active_path']=str(private_memory_cfg);cfg['memory_active_sha256']=sha(private_memory_cfg)
join=dict(source_sha256=cfg['source_sha256'],dependency_pins=deps)
qa=op/'CPU_FIXTURE_QA.json';put(qa,dict(join,status='PASS',owner_integration_qualified=True,complete_memory_generic_B_exercised=True,CPU_FIXTURE_ONLY=True))
back=op/'CPU_FIXTURE_READBACK.json';put(back,dict(join,verified=True,QA_sha256=sha(qa),CPU_FIXTURE_ONLY=True))
cfg.update(QA_path=str(qa),QA_sha256=sha(qa),readback_path=str(back),readback_sha256=sha(back));cfgpath=op/'ACTIVE.json';put(cfgpath,cfg)
f.q['additional_operational_overlays'][m.ID]=m.record(cfg)
proof=m.install_on_frame(f.frame,cfgpath,scheduler_ident=threading.get_ident());adapter=getattr(f.main,m.MARKER)['adapter'];oldcpu=adapter.old_cpu;oldgate=adapter.old_choose;generic=f.aging.original;coupling=getattr(f.main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1');padding=adapter.padding
savedstate=copy.deepcopy(f.aging.state.__dict__);savedsample=copy.deepcopy(f.sample);originalresources=padding.resources;oldwriter=adapter.helper.atomic_exclusive
f.frame.f_locals['running']={}
def reset():
 f.aging.state.__dict__.clear();f.aging.state.__dict__.update(copy.deepcopy(savedstate));f.aging.calls=0
 f.resource_state.update(calls=0,fail_from=None,pressure_from=None,on_call=None);f.sample.clear();f.sample.update(copy.deepcopy(savedsample));f.claims.clear();put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={}))
 f.q['consumed'].pop(C,None);f.q['sealed']=[];f.frame.f_locals['running'].clear();padding.resources=originalresources;adapter.helper.atomic_exclusive=oldwriter;adapter.last_hold=None
 for suffix in ['.INTENT.json','.DONE.json']:
  p=f.root/'control/qualification_ledger'/(C+suffix)
  if p.exists():assert not p.is_symlink();p.unlink()
 for p in tokens.glob('*.json'):assert p.is_relative_to(f.root);p.unlink()
def choose(pending=None):return f.res.choose_dispatch(f.pending if pending is None else pending,f.sample,f.claims,f.history,None,f.policy,1)
reset();ck('actual_old_E_HOLD_while_exact_canary_in_pending',oldgate(f.pending,f.sample,f.claims,f.history,None,f.policy,1)is None);reset()
value=choose();ck('actual_new95_generic_B5_f3_a650_CPU_frameguard_complete_positive',value is not None and value['cohort']==C and 'finite_memory_canary_priority_dispatch'in value)
token=read(value['finite_memory_canary_priority_reservation']['path']);returned=read(value['finite_memory_canary_priority_dispatch']['path'])
ck('full_forecast_not_reduced_new95_budget_and_two_fullproofs',all(x['full_candidate_cost_bytes']>=value['forecast']['predicted_peak_RAM_bytes']and x['prospective_growth_bytes']<=x['memory_proof']['effective_decision']['admission_RAM_budget_bytes']and x['memory_proof']['memory_utilization_fraction']==.95 for x in [token['first'],token['second']]))
ck('durable_receipts_before_claim_INTENT_no_dispatch_binding_creation',len(list(tokens.glob('*.json')))==2 and not f.claims and not(f.root/'control/qualification_ledger'/(C+'.INTENT.json')).exists()and returned['stage']=='CPU_RETURNED_DURABLE_BEFORE_CLAIM_INTENT')
before=sorted((p.name,p.read_bytes())for p in tokens.glob('*.json'));again=choose();ck('zero_start_no_claim_no_INTENT_retry_uses_fresh_immutable_attempt',again is not None and again['finite_memory_canary_priority_reservation']['attempt']!=value['finite_memory_canary_priority_reservation']['attempt']and all((tokens/n).read_bytes()==raw for n,raw in before)and len(list(tokens.glob('*.json')))==4)
ck('R_credit_CPU_frameguard_pool_and_a650_memory_chain_preserved',f.aging.state.protected==savedstate['protected']and f.aging.state.pending_releases==savedstate['pending_releases']and coupling['cell'].cell_contents is coupling['gate'].wrapper and coupling['cpu']['original']is coupling['gate'].wrapper and f.aging.original is generic and getattr(f.main,owner.MARKER)['old_choose']==pref.wrapper and id(f.frame.f_locals['pool'])==proof['pool_object_id'])
reset();ck('finite_canary_outside_supplied_pool_never_added',choose([x for x in f.pending if x['cohort']!=C])is None and not list(tokens.glob('*.json')))
reset();f.q['consumed'][C]=dict(uuid='CPU_SPENT');ck('spent_never_borrowed',choose()is None)
reset();f.claims[C]=dict(host_cpu=16,predicted_peak_RAM_bytes=12*G);ck('claimed_never_borrowed',choose()is None)
reset();put(f.root/'control/qualification_ledger'/(C+'.INTENT.json'),dict(CPU_ONLY=True));ck('INTENT_never_borrowed',choose()is None)
reset();put(f.root/'control/qualification_ledger'/(C+'.DONE.json'),dict(CPU_ONLY=True));ck('DONE_hole_never_borrowed',choose()is None)
reset();f.q['sealed']=[C];ck('sealed_never_borrowed',choose()is None)
reset();f.frame.f_locals['running'][object()]=C;ck('existing_worker_never_reborrowed',choose()is None)
reset();put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={C:dict(CPU_ONLY=True)}));ck('persisted_claim_never_borrowed',choose()is None)
reset();extra.write_text('drift');ck('source_drift_failclosed_before_E',choose()is None and adapter.last_hold['stage']=='OUTER_ACTIVATION');extra.write_text('stable')
reset();active=getattr(f.main,owner.MARKER)['context']['cfg'];broad=dict(active,scope_mode='ALL_UNSPENT_FUTURE');getattr(f.main,owner.MARKER)['context']['cfg']=broad;ck('finite_to_broad_memory_scope_not_implicitly_activated',choose()is None);getattr(f.main,owner.MARKER)['context']['cfg']=active
reset();adapter.cfg['allowed_cohorts']=[T];ck('other_cohort_cannot_borrow_fixed_canary',choose()is None);adapter.cfg['allowed_cohorts']=[C]
reset();f.sample.update(host_MemAvailable_bytes=140*G,cgroup_effective_headroom_bytes=140*G);ck('new95_real_RAM_and_fullcandidate_HOLD_not_relaxed',choose()is None and not list(tokens.glob('*.json')))
reset();f.sample['cgroup_effective_headroom_bytes']=130*G;ck('cgroup_effective_headroom_gate_retained',choose()is None)
reset();f.resource_state['pressure_from']=1;ck('CPU_PSI_pressure_retained',choose()is None)
reset();f.sample['cpu_allowed']=[];ck('actual_CPU_capacity_gate_retained',choose()is None)
for field,bad,name in [('physical_disk_pass',False,'disk_gate'),('own_write_ceiling_pass',False,'own_write_gate'),('native_free_bytes',5*G,'candidate_write_margin_gate'),('free_inodes',99999,'inode_gate'),('own_remaining_write_and_restore_bytes',f.q['reserved_write_bytes'],'own_ceil_candidate_growth_gate')]:
 reset()
 def badresources(*a,_field=field,_bad=bad,**kw):return dict(originalresources(*a,**kw),**{_field:_bad})
 padding.resources=badresources;ck(name+'_retained',choose()is None and not list(tokens.glob('*.json')))
reset()
def writerfail(*a,**kw):raise OSError('CPU fsync/storage fault')
adapter.helper.atomic_exclusive=writerfail;ck('reservation_write_failure_no_return_no_claim',choose()is None and not f.claims)
reset()
def returnfail(p,obj):
 if str(p).endswith('.CPU_RETURNED.json'):raise OSError('CPU return fsync fault')
 return oldwriter(p,obj)
adapter.helper.atomic_exclusive=returnfail;ck('CPU_return_receipt_failure_no_dispatch',choose()is None and adapter.last_hold['stage']=='CPU_RETURN_RECEIPT_FAILCLOSED'and not f.claims)
adapter.helper.atomic_exclusive=oldwriter;ck('failed_return_attempt_does_not_starve_canary_retry',choose()is not None)
reset();f.resource_state['fail_from']=3;before=copy.deepcopy(f.aging.state.__dict__);ck('actual_FrameGuard_frame_failure_no_stale_resource_or_token',choose()is None and not list(tokens.glob('*.json')))
reset();f.sample.update(host_MemAvailable_bytes=300*G,cgroup_effective_headroom_bytes=300*G);value=choose();ck('normal_E_work_wins_unchanged_without_priority_token',value is not None and value['cohort']==T and 'finite_memory_canary_priority_reservation'not in value)
reset();before=copy.deepcopy(f.aging.state.__dict__);calls=f.aging.calls
def e_error(*a):
 f.aging.state.protected+=G;f.aging.calls+=1;raise RuntimeError('CPU old E engineering failure after mutation')
adapter.old_choose=e_error;ck('oldE_mutate_then_raise_contained_by_exact_Guard_rollback',choose()is None and f.aging.state.__dict__==before and f.aging.calls==calls and coupling['gate'].last_issue['status']=='UPSTREAM_E_CHOOSER_ENGINEERING_EXCEPTION');adapter.old_choose=oldgate
reset();before=copy.deepcopy(f.aging.state.__dict__);calls=f.aging.calls
def e_sentinel(*a):
 f.aging.state.protected+=G;f.aging.calls+=1;raise adapter.FrameUnavailable(dict(status='CPU_EXACT_SENTINEL_NOT_RELABELED'))
adapter.old_choose=e_sentinel;ck('oldE_exact_FrameUnavailable_preserved_and_rollback',choose()is None and f.aging.state.__dict__==before and f.aging.calls==calls and coupling['gate'].last_issue['status']=='CPU_EXACT_SENTINEL_NOT_RELABELED');adapter.old_choose=oldgate
reset();before=copy.deepcopy(f.aging.state.__dict__);calls=f.aging.calls;oldfresh=adapter.fresh;fresh_calls=[]
def fail_second_fresh(*a,**kw):
 fresh_calls.append(1)
 if len(fresh_calls)==2:f.resource_state['fail_from']=f.resource_state['calls']+1
 return oldfresh(*a,**kw)
adapter.fresh=fail_second_fresh;ck('fallback_second_fresh_three_failures_preserve_exact_sentinel_Guard_rollback',choose()is None and len(fresh_calls)==2 and f.aging.state.__dict__==before and f.aging.calls==calls and coupling['gate'].last_issue['attempts']==3 and not list(tokens.glob('*.json')));adapter.fresh=oldfresh
reset()
def cpu_error(*a):raise RuntimeError('CPU wrapper engineering fault')
adapter.old_cpu=cpu_error;ck('oldCPU_call_exception_returns_HOLD_not_scheduler_escape',choose()is None and adapter.last_hold['stage']=='UPSTREAM_CPU_CHOOSER_ENGINEERING_EXCEPTION');adapter.old_cpu=oldcpu
reset();broad=dict(memcfg,scope_mode='ALL_UNSPENT_FUTURE');put(private_memory_cfg,broad);getattr(f.main,owner.MARKER)['context']['cfg']=broad;f.q['additional_operational_overlays'][lib.ID]=dict(lib.record(broad),status='ACTIVE')
value=choose();ck('valid_broad_scope_E_HOLD_no_canary_priority_borrowing',value is None and not list(tokens.glob('*.json')))
f.sample.update(host_MemAvailable_bytes=300*G,cgroup_effective_headroom_bytes=300*G);value=choose();ck('valid_broad_scope_normal_oldE_decision_passes_through',value is not None and value['cohort']==T and 'finite_memory_canary_priority_reservation'not in value)
getattr(f.main,owner.MARKER)['context']['cfg']=memcfg;f.q['additional_operational_overlays'][lib.ID]=dict(lib.record(memcfg),status='ACTIVE');put(private_memory_cfg,memcfg)
reset();drift=lambda *a:None;old= f.res.choose_dispatch;f.res.choose_dispatch=drift;reject('restore_refuses_clobber_new_outer',lambda:m.restore_in_owner());f.res.choose_dispatch=old
restored=m.restore_in_owner();ck('restore_exact_prior_E_CPU_and_memory_a650',f.res.choose_dispatch is oldcpu and coupling['gate'].original_choose==oldgate and f.aging.original is generic and restored['immutable_attempt_receipts_retained'])
ck('all21_original_sourcepins_and_memory6_unchanged',all(sha(x['path'])==x['sha256']for x in f.plan['source_pins'])and all(sha(memcfg[r+'_path'])==memcfg[r+'_sha256']for r in lib.ROLES))
report=dict(schema='FINITE_CANARY_PRIORITY_OWNER_CPU_QUALIFICATION_V1',status='PASS',owner_integration_qualified=True,complete_memory_generic_B_exercised=True,checks=checks,passed=len(checks),source_sha256=sha(D/'priority_lease.py'),driver_sha256=sha(__file__),fixture_source_sha256=sha(D/'fixture_setup.py'),dependency_pins={p:h for p,h in deps.items()if not str(p).startswith(str(f.root))},fixture=str(f.root),CPU_fixture_authority_resources_and_thread_not_production=True,actual_frozen_layers=['B5','f3','E','a650','memory348','CPUrebinder','FrameGuard'],scientific_models_started=0,signals=0,production_mutations=0,production_owner_attached=False)
put(D/'CPU_QUALIFICATION.json',report);print(json.dumps(dict(status='PASS',checks=len(checks),source_sha256=report['source_sha256'],report=str(D/'CPU_QUALIFICATION.json'))));f.pool.shutdown()
