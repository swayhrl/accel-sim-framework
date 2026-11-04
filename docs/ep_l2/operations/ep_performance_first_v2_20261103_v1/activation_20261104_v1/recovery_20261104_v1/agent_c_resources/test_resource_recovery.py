"""Bounded readonly actual-state and synthetic-counterfactual resource CPU controls."""
from pathlib import Path
import importlib.util,json,copy,time,hashlib,types
A=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('recover',A/'resources_recovery.py');r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
v=r.base_runtime();h=v.qualified_math();b=h.base();reg=json.loads(b.REG.read_text());q=reg['registered_future_requests'][r.DTC];checks=[]
def check(k,fn,reject=False):
 try:o=fn();ok=not reject and o is not False;err=None
 except Exception as e:o=None;ok=reject;err=repr(e)
 checks.append(dict(label=k,PASS=ok,error=err));assert ok,checks[-1];return o
actual=check('actual_owner_exact_mapping',lambda:r.owner_mapping(q,b,[]))
check('preserve_current2p5GiB_published_carrier_once',lambda:sum(z['bytes']for z in actual['writes'])==q['reserved_write_bytes']==2684354560)
check('actual16terminal_models_no_future_modelRAM',lambda:actual['batch_terminal']and all(z['additional_RAM_bytes']==0 for z in actual['ram']if z.get('cohort')))
check('actual_owner_still_live_not_released',lambda:actual['owner']['live']and not actual['owner_closed_released'])
pr=actual['owner'];added,margin=r.controller_margin(pr,{'minimum_prediction_bytes':4*r.G,'history_multiplier':1.2,'history_additive_bytes':256*r.M},[])
check('only_incremental_owner_growth_not_RSS',lambda:0<added<pr['RSS_bytes']and actual['current_controller_RSS_not_added_as_future_RAM'])
check('same_PID_generation_margin_deduplicated',lambda:r.controller_margin(pr,{'minimum_prediction_bytes':4*r.G,'history_multiplier':1.2,'history_additive_bytes':256*r.M},[dict(pid=pr['pid'],start_ticks=pr['start_ticks'],additional_RAM_bytes=margin)])[0]==0)
bad=copy.deepcopy(q);bad['execution_plan_sha256']='0'*64
check('plan_pin_drift_reject',lambda:r.owner_mapping(bad,b,[]),True)
bad=copy.deepcopy(q);bad['owner_start_ticks']+=1
check('owner_generation_mismatch_reject',lambda:r.owner_mapping(bad,b,[]),True)
bad=copy.deepcopy(q);bad['budget']=17
check('unapproved_owner_extension_reject',lambda:r.owner_mapping(bad,b,[]),True)
bad=copy.deepcopy(q);bad['remaining']=1
check('budget_remaining_not_proof_of_free_owner',lambda:r.owner_mapping(bad,b,[]),True)
# Preserve all original unknown-owner failclosed behavior through the mapped function.
legacy=copy.deepcopy(reg)
for key in h.SCOPES:legacy['registered_future_requests'].pop(key,None)
legacy['registered_future_requests']['UNMAPPED_FUTURE_CPU_WRITER']=dict(state='RUNNING',consumed={'X':{}},reserved_write_bytes=17)
f=b.foreign_commitments(legacy)
check('unknown_active_owner_failclosed',lambda:any('UNMAPPED_FUTURE_CPU_WRITER'in z for z in f['foreign_metadata_errors']))
check('unknown_owner_write_promise_not_erased',lambda:any(z.get('request')=='UNMAPPED_FUTURE_CPU_WRITER'and z['bytes']==17 for z in f['foreign_write_entries']))
s=r.snapshot(v.REQUESTS['system'])
check('actual_snapshot_no_metadata_errors',lambda:not s['foreign_metadata_errors'])
check('actual_restore_bound384_not256',lambda:s['two_new_scope_restore_window_upper_bound_bytes']==384*r.M)
d=r.admit(s,5*r.G,512*r.M);check('actual5GiB_RAM_512MiB_writes_probe_PASS_no_start',lambda:d['pass_admission'])
check('own_emergency1GiB_preserve_explicit_DTC5GiB_floor',lambda:d['own_emergency_floor_bytes']==r.G and d['confirmed_foreign_native_floor_bytes']==5*r.G)
for label,mut in [('disk_exhausted',lambda x:x.update(native_free_bytes=0)),('RAM_exhausted',lambda x:x.update(host_MemAvailable_bytes=0,cgroup_effective_headroom_bytes=0)),('global_EP_cap2',lambda x:x.update(global_EP_consumed_active_count=2)),('stale',lambda x:x.update(monotonic=time.monotonic()-60)),('unknown_metadata',lambda x:x.update(foreign_metadata_errors=['unknown peer']))]:
 x=copy.deepcopy(s);mut(x);check(label,lambda x=x:not r.admit(x,1,1)['pass_admission'])
# Family wrapper rejects cross-scope snapshots before any admission.
sp=importlib.util.spec_from_file_location('wrapper',A/'resources_system.py');w=importlib.util.module_from_spec(sp);sp.loader.exec_module(w)
x=copy.deepcopy(s);x['current_request']=v.REQUESTS['highclock'];check('system_wrapper_cross_scope_reject',lambda:w.admit(x,0,0),True)
(A/'CPU_RESOURCE_RECOVERY_CONTROLS.json').write_text(json.dumps(dict(schema='EP_READONLY_DTC16_RECOVERY_RESOURCE_CPU_V1',status='PASS_ACTUAL_AND_COUNTERFACTUAL_NO_ACTORS',checks=checks,total=len(checks),passed=sum(z['PASS']for z in checks),new_models=0,real_ledger_writes=0,DTC_processes_signaled=0),indent=2)+'\n')
(A/'ACTUAL_READONLY_SNAPSHOT.json').write_text(json.dumps(s,indent=2)+'\n');(A/'ACTUAL_PROBE_ADMISSION_NO_START.json').write_text(json.dumps(d,indent=2)+'\n')
print('PASS',len(checks),'resource controls')
