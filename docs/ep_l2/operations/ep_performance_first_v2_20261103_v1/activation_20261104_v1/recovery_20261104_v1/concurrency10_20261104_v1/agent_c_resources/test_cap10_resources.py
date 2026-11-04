"""Pure admission tests and bounded actual metadata-only capacity probes; no starts."""
from pathlib import Path
import json,importlib.util,copy,time,itertools,hashlib
A=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('cap10',A/'resources_cap10.py');r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');G=1<<30;M=1<<20
s=r.snapshot('EP_L2_SYSTEM_850MHZ_PARAMETER_FAMILY_V2_20261104_V1')
checks=[]
def check(label,value):
 checks.append(dict(label=label,PASS=bool(value)));assert value,label
# Isolate concurrency in a healthy real resource view; do not fabricate new scientific rows.
x=copy.deepcopy(s);x['monotonic']=time.monotonic();x['global_EP_consumed_active_count']=9
check('nine_active_allows_tenth_prospective',r.admit(x,1,1)['pass_admission'])
x['global_EP_consumed_active_count']=10
check('ten_active_rejects_eleventh',not r.admit(x,1,1)['pass_admission'])
x['global_EP_consumed_active_count']=None
check('unknown_active_count_failclosed',not r.admit(x,1,1)['pass_admission'])
for k,mut in [('disk',lambda z:z.update(native_free_bytes=0)),('RAM',lambda z:z.update(host_MemAvailable_bytes=0,cgroup_effective_headroom_bytes=0)),('unknown_owner',lambda z:z.update(foreign_metadata_errors=['UNMAPPED_OWNER']))]:
 x=copy.deepcopy(s);x['monotonic']=time.monotonic();mut(x);check(k+'_unchanged_failclosed',not r.admit(x,1,1)['pass_admission'])
d=r.admit(dict(s,monotonic=time.monotonic()),1,1)
check('5GiB_foreign_floor_preserved_not_summed_with_own1GiB',d['confirmed_foreign_native_floor_bytes']==5*G and d['own_emergency_floor_bytes']==G)
check('384MiB_restore_upper_bound_preserved_not_doublecharged',d['restore_upper_bound_bytes']==384*M)
check('actual_mapping_still_clean',not s['foreign_metadata_errors'])
reg=json.loads(Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes())
v=r.prior().base_runtime();h=v.qualified_math();b=h.base()
roots={q:Path(p)for q,p in s['all_covered_EP_scope_roots'].items()if q in v.NEW_SCOPES}
pending=[];claims={}
for q,rt in roots.items():
 claims[q]=json.loads((rt/'control/DISPATCH_CLAIMS.json').read_bytes())['claims']
 row=reg['registered_future_requests'][q]
 for c,digest in row['admitted_specs'].items():
  spath=rt/'cases'/c/'control/FROZEN_SPEC.json';raw=spath.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
  z=json.loads(raw)
  if c not in row['consumed']:
   pending.append(dict(request=q,cohort=c,estimated_RAM_bytes=z['estimated_peak_RAM_bytes'],result_cap_bytes=z['limits']['result_bytes'],conditional='G64W16_FRFCFS256'in c))
ownq=s['current_request'];ownclaims=claims[ownq]
ownram=0;ownwrites=0;maxwindow=0
for c,z in ownclaims.items():
 rss=b.process(z['model_pid'],z['model_start_ticks'])['RSS_bytes']if z.get('model_pid')else 0
 ownram+=max(0,z['estimated_peak_RAM_bytes']-rss)
 ownwrites+=z['remaining_write_bytes'];maxwindow=max(maxwindow,json.loads((roots[ownq]/'cases'/c/'control/FROZEN_SPEC.json').read_bytes())['limits']['result_bytes'])
ownwrites+=maxwindow+2*M
def probe(chosen):
 x=copy.deepcopy(s);x['monotonic']=time.monotonic()
 ram=ownram;writes=ownwrites;ownwindow=maxwindow
 for z in chosen:
  if z['request']==ownq:
   ram+=z['estimated_RAM_bytes'];writes+=z['result_cap_bytes']+2*M;ownwindow=max(ownwindow,z['result_cap_bytes'])
  else:
   x['foreign_additional_RAM_bytes']+=z['estimated_RAM_bytes'];x['foreign_remaining_write_bytes']+=z['result_cap_bytes']+2*M
 writes+=ownwindow-maxwindow
 # A previously idle foreign scope needs its first restore window plus scope metadata.
 for peer in roots:
  if peer==ownq:continue
  selected=[z for z in chosen if z['request']==peer]
  if not selected:continue
  existing_caps=[json.loads((roots[peer]/'cases'/c/'control/FROZEN_SPEC.json').read_bytes())['limits']['result_bytes']for c in claims[peer]]
  old_window=max(existing_caps or[0]);new_window=max([z['result_cap_bytes']for z in selected]+[old_window])
  x['foreign_remaining_write_bytes']+=new_window-old_window+(0 if claims[peer]else 2*M)
 # prospective aggregate after adding selected candidates must itself stay <=10
 x['global_EP_consumed_active_count']=s['global_EP_consumed_active_count']+len(chosen)-1 if chosen else s['global_EP_consumed_active_count']
 d=r.admit(x,ram,writes)
 return dict(additional_count=len(chosen),total_active=s['global_EP_consumed_active_count']+len(chosen),cells=[z['cohort']for z in chosen],own_additional_RAM_bytes=ram,own_remaining_write_bytes=writes,admission=d)
sets={}
for name,rows in [('unconsumed_all_stage_boundaries_still_required',pending),('unconsumed_unconditional_only',[z for z in pending if not z['conditional']])]:
 out=[];slots=max(0,10-s['global_EP_consumed_active_count'])
 for n in range(1,min(slots,len(rows))+1):
  ps=[probe(sub)for sub in itertools.combinations(rows,n)]
  good=[z for z in ps if z['admission']['pass_admission']]
  out.append(dict(additional_count=n,total_active=s['global_EP_consumed_active_count']+n,combinations=len(ps),passing_combinations=len(good),best=good[0]if good else ps[0],worst= max(ps,key=lambda z:z['admission'].get('required_native_free_bytes',z['own_remaining_write_bytes']))))
 sets[name]=out
check('actual_mixed_capacity_probes_generated',bool(sets))
(A/'CPU_CAP10_CONTROLS.json').write_text(json.dumps(dict(schema='EP_MAIN_PROSPECTIVE_CAP10_CPU_V1',status='PASS',total=len(checks),passed=len(checks),checks=checks,prior22_controls_ref=dict(path=str(A.parent.parent/'agent_c_resources/CPU_RESOURCE_RECOVERY_CONTROLS.json'),sha256=hashlib.sha256((A.parent.parent/'agent_c_resources/CPU_RESOURCE_RECOVERY_CONTROLS.json').read_bytes()).hexdigest()),no_repeated_prior22_run=True,model_starts=0,registry_writes=0),indent=2)+'\n')
(A/'ACTUAL_READONLY_SNAPSHOT.json').write_text(json.dumps(s,indent=2)+'\n')
(A/'ACTUAL_MIXED_CAPACITY_PROBE.json').write_text(json.dumps(dict(schema='EP_MAIN_CAP10_ACTUAL_MIXED_CAPACITY_READONLY_V1',utc=s['utc'],actual_global_EP_active=s['global_EP_consumed_active_count'],unconsumed=len(pending),pending=pending,current_own_claims=list(ownclaims),baseline_own_additional_RAM_bytes=ownram,baseline_own_remaining_write_bytes=ownwrites,projection='Same sampled df/RSS; preserve all committed owners and per-scope restore windows. No scan or starts. Recheck before each real claim. Conditional stage gate unchanged.',sets=sets),indent=2)+'\n')
print('PASS',len(checks))
print('nativefree GiB',s['native_free_bytes']/G,'foreignwrites GiB',s['foreign_remaining_write_bytes']/G,'MemAvailable GiB',s['host_MemAvailable_bytes']/G)
for k,rows in sets.items():
 print(k,[(z['total_active'],z['passing_combinations'],z['combinations'])for z in rows])
