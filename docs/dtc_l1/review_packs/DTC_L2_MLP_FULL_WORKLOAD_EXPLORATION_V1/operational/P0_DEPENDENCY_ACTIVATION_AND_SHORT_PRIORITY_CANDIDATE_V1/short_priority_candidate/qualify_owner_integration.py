from pathlib import Path as P
import json,time,copy,os,hashlib
from fixture_setup import setup,load,B,C,T,G,read,raw,sha,put
f=setup();m=load('qualified_one_shot_owner',B/'one_shot_owner.py');pin=f.root/'EXTRA_SOURCE_PIN.txt';pin.write_text('stable');f.scope['dependency_pins'][str(pin)]=sha(pin)
for role in['QA','readback']:
 p=P(f.scope[role+'_path']);v=read(p);v['dependency_pins']=f.scope['dependency_pins'];v.update({'QA_sha256':f.scope['QA_sha256']}if role=='readback'else{});put(p,v);f.scope[role+'_sha256']=sha(p)
put(f.cfgpath,f.scope);rec=f.q['additional_operational_overlays'][m.ID]
for key in['dependency_pins','QA_sha256','readback_sha256']:rec[key]=f.scope[key]
assessment=lambda frame:dict(modeled_30min_release_bytes=20*G,unknown_count=0,window_seconds=60,monotonic=time.monotonic(),modeled_not_deadline=True)
proof=m.install_on_frame(f.frame,f.cfgpath,assessment=assessment,fixture=True);adapter=getattr(f.main,m.MARKER)['adapter'];original_state=copy.deepcopy(f.aging.state.__dict__);original_sample=copy.deepcopy(f.sample);original_B=f.aging.original;original_gate=adapter.old_choose;cpu_wrapper=adapter.old_cpu;checks=[]
def ck(n,v):assert v,n;checks.append(n)
def reset():
 f.aging.state.__dict__.clear();f.aging.state.__dict__.update(copy.deepcopy(original_state));f.aging.calls=0;f.resource_state.update(calls=0,fail_from=None,pressure_from=None,on_call=None);f.sample.clear();f.sample.update(copy.deepcopy(original_sample));f.claims.clear();put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}});f.q['consumed'].pop(C,None);f.aging.original=original_B;adapter.assessment=assessment;adapter.last_hold=None;adapter.returned.clear()
 for path in P(f.scope['token_directory']).glob('*.json'):
  assert path.resolve().is_relative_to(f.root.resolve())and not path.is_symlink();path.unlink()
 db=f.root/'control/dispatch_bindings'/(C+'.json');put(db,dict(cohort=C,canonical_spec_sha256=f.q['admitted_specs'][C],host_cpu=16,resolved_spec_sha256=f.engine.jsonsha(dict(f.spec,host_cpu=16))))
def choose():return f.res.choose_dispatch(f.pending,f.sample,f.claims,f.history,None,f.policy,1)
# E's normal R fence blocks this point before the new adapter.
reset();ck('original_E_fence_blocks_same_P0_pool',adapter.old_choose(f.pending,f.sample,f.claims,f.history,None,f.policy,1)is None);reset()
f.resource_state['pressure_from']=3;ck('actual_B5_consistent_physical_HOLD_retained',choose()is None and not list(P(f.scope['token_directory']).glob('*.json')));reset()
f.resource_state['pressure_from']=1;ck('first_fresh_CPU_PSI_HOLD_retained',choose()is None);reset()
f.resource_state['pressure_from']=4;ck('second_fresh_CPU_PSI_HOLD_retained_no_token',choose()is None and not list(P(f.scope['token_directory']).glob('*.json')));reset()
f.resource_state['fail_from']=4;before=copy.deepcopy(f.aging.state.__dict__);ck('second_fresh_read_failure_uses_real_guard_state_rollback',choose()is None and f.aging.state.__dict__==before and getattr(f.main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1')['gate'].last_pass_status=='FAILCLOSED_FRAME_UNAVAILABLE');reset()
oldwriter=adapter.helper.atomic_exclusive
def failed_writer(*a,**k):raise OSError('CPU durable reservation fault')
adapter.helper.atomic_exclusive=failed_writer;ck('reservation_durable_failure_NONE_does_not_escape_owner',choose()is None and adapter.last_hold['stage']=='DURABLE_RESERVATION_FAILED');adapter.helper.atomic_exclusive=oldwriter;reset()
def dispatch_fault(path,obj):
 if str(path).endswith('.DISPATCH_RETURNED.json'):raise OSError('CPU durable final-return fault')
 return oldwriter(path,obj)
adapter.helper.atomic_exclusive=dispatch_fault;value=choose();ck('post_CPU_durable_failure_NONE_no_claim_no_refund',value is None and adapter.last_hold['stage']=='DURABLE_DISPATCH_RETURN_FAILED'and len(list(P(f.scope['token_directory']).glob('*.RESERVED.json')))==1 and f.claims=={});adapter.helper.atomic_exclusive=oldwriter;reset()
pin.write_text('drift');ck('source_drift_HOLD_before_E',choose()is None and adapter.last_hold['stage']=='OUTER_SOURCE_OR_ACTIVATION');pin.write_text('stable');reset()
def race(call):
 if call==4:f.q['consumed'][C]=dict(uuid='CPU_RACED_CONSUMER')
f.resource_state['on_call']=race;ck('second_fresh_consumed_identity_race_refused',choose()is None and not list(P(f.scope['token_directory']).glob('*.json')));reset()
# Generic future B wrapper: source is an ACTIVE registered operation, not a
# hard-coded raw-B identity, and it still delegates the unchanged complete B.
shim=f.root/'registered_B_wrapper.py';shim.write_text('def wrapped(*args,**kwargs):\n calls.append(1)\n return original(*args,**kwargs)\n');module=load('registered_future_B_shim',shim);module.original=original_B;module.calls=[];f.q['additional_operational_overlays']['CPU_GENERIC_B']=dict(status='ACTIVE_CPU_FIXTURE_ONLY',source_sha256=sha(shim));f.aging.original=module.wrapped;value=choose();ck('registered_generic_B_chain_CPU_rebind_and_two_durable_files',value is not None and module.calls and 'zero_start_cpu_rebind'in value and len(list(P(f.scope['token_directory']).glob('*.json')))==2);ck('R_and_actual_CPU_guard_closure_pool_claims_unchanged',f.aging.state.protected==55*G and getattr(f.main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1')['cell'].cell_contents is getattr(f.main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1')['gate'].wrapper and adapter.old_cpu is cpu_wrapper and id(f.frame.f_locals['pool'])==proof['pool_object_id']and f.claims=={})
again=choose();ck('durable_once_per_target_survives_repeated_calls',again is None);m.restore_in_owner();m.install_on_frame(f.frame,f.cfgpath,assessment=assessment,fixture=True);adapter=getattr(f.main,m.MARKER)['adapter'];ck('durable_once_per_target_survives_new_adapter_instance',choose()is None);reset()
# New unused bindings are frozen in original format before l2_ops refresh.
db=f.root/'control/dispatch_bindings'/(C+'.json');db.unlink();value=choose();receipt=read(value['one_shot_priority_dispatch']['path'])if value else{};ck('no_binding_created_under_attempt_lock_without_spec_change',value is not None and receipt['zero_start_binding_created']is True and f.engine.spec_for(C)['host_cpu']==read(db)['host_cpu']and sha(f.root/'control/specs'/(C+'.json'))==f.q['admitted_specs'][C]);reset()
# A now-funded real target wins through original E rather than the exception.
f.sample['host_MemAvailable_bytes']=260*G;f.sample['cgroup_effective_headroom_bytes']=260*G;value=choose();ck('funded_target_prioritized_no_exception_token',value is not None and value['cohort']==T and'one_shot_priority_token'not in value);reset()
m.restore_in_owner();ck('restore_preserves_original_CPU_and_Eguard_worker',f.res.choose_dispatch is cpu_wrapper and getattr(f.main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1')['gate'].original_choose==original_gate)
probe=m.ProgressAssessment(f.root,interval=60);probe_c='CPU_PROGRESS_ONLY';probe_u='CPU_PROGRESS_UUID';probe_p=f.root/'DTC/run/results'/probe_u/'progress.jsonl.gz';probe_p.parent.mkdir(parents=True);put(f.root/'control/specs'/(probe_c+'.json'),dict(expected=dict(instructions=1000)));import gzip
with gzip.open(probe_p,'wt')as h:h.write(json.dumps(dict(generation=probe_u,pid=99999902,start_ticks=2,completed=600))+'\n')
probe_frame=dict(own_live=[dict(cohort=probe_c,uuid=probe_u,pid=99999902,start_ticks=2,anon_PSS_bytes=G,effective_future_bytes=G)]);probe.previous=(time.monotonic()-61,{probe_c:dict(completed=100)});assessed=probe(probe_frame);ck('default_progress_observer_real_gzip_rate_and_cash_math',assessed['unknown_count']==0 and abs(assessed['modeled_30min_release_bytes']-1.88*G)<1)
probe.cached=None;probe.previous=(time.monotonic()-61,{probe_c:dict(completed=600)});assessed=probe(probe_frame);ck('default_progress_observer_no_progress_is_unknown_not_fake_ETA',assessed['unknown_count']==1)
report=dict(schema='ONE_SHOT_FULL_OWNER_INTEGRATION_CPU_QUALIFICATION_V1',status='PASS',checks=checks,passed=len(checks),source_sha256=sha(B/'one_shot_owner.py'),fixture_setup_sha256=sha(B/'fixture_setup.py'),driver_sha256=sha(P(__file__)),dependency_pins=f.scope['dependency_pins'],fixture=str(f.root),production_parent_attached=False,production_mutations=0,model_starts=0,model_signals=0,source_data_authority_and_positive_headroom_are_CPU_fixtures=True)
put(B/'OWNER_INTEGRATION_QUALIFICATION.json',report);put(B/'QUALIFIED_DEPENDENCIES.json',{k:v for k,v in f.scope['dependency_pins'].items()if str(f.root)not in k});print(json.dumps(report));f.pool.shutdown()
