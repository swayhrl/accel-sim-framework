"""Private V5 A2 mapping. No registry/Native writes or science grants."""
from pathlib import Path
import hashlib,importlib.util,json,copy,os,fcntl
P=Path;HERE=P(__file__).resolve().parent
BASE=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/activation_20261104_v1/agent_c_resources/resources_v3.py')
BASE_SHA='ebaacc5efecf4e2162532b0722822763df55fb5cab05dbec0e0eaa161e6465bd'
REQUEST='EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1'
ROOT=HERE/'three_mm/execution'
PIN=HERE/'FOUR_FOREIGN_EXACT_MAPPING_PINS.json'
PIN_SHA='67d01d185fd1dbdecde76b8e21ecaf02bc1712552a4a9c95f78821caa1b65b4c'
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def load(path,name,pin):
 need(sha(path)==pin,'resource dependency drift '+str(path));s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def map_owner(req,q,d,m,existing):
 root=P(d['root']);need(q['request']==req and q['schema']==d['registry_schema'] and q['budget']==d['budget']==len(q['admitted_specs']) and q['remaining']==q['budget']-len(q['consumed']),'foreign exact budget/schema')
 need(q['controller_path']==d['controller_ref']['path'] and q['controller_sha256']==d['controller_ref']['sha256'] and sha(q['controller_path'])==q['controller_sha256'],'foreign controller drift')
 pref=d['policy_ref'];need(sha(pref['path'])==pref['sha256'],'foreign policy drift');policy=read(pref['path'])
 cp=root/'control/POOL_DISPATCH_RESERVATIONS.json';cp_sha=sha(cp);claims=read(cp)['claims'];need(set(claims)<=set(q['admitted_specs']),'unknown claim')
 rows=[];models=[];cpus=[];pins=[];pending_cpu_claims=[]
 for c in sorted(set(q['consumed'])|set(claims)):
  sf=root/'control/specs'/(c+'.json');need(sha(sf)==q['admitted_specs'][c],'foreign spec pin');s=read(sf);need(s['cohort']==c and s['request']==req,'foreign spec scope');hard=s['limits']['max_process_tree_rss_bytes'];estimate=s['estimated_peak_model_RAM_bytes'];need(type(hard)is int and type(estimate)is int and 0<estimate<=hard,'foreign RAM bounds')
  claim=claims.get(c,{});pred=claim.get('predicted_peak_RAM_bytes',estimate);need(type(pred)is int and 0<pred<=hard,'claim RAM bounds')
  if claim:
   need(claim.get('RAM_cap_bytes',hard)==hard and claim.get('result_cap_bytes')==s['limits']['max_result_directory_bytes'],'claim cap mismatch')
   need(type(claim.get('host_cpu'))is int,'claim CPU missing');cpus.append(claim['host_cpu'])
   if c not in q['consumed']:pending_cpu_claims.append(dict(cohort=c,cpu=claim['host_cpu']))
  row=q['consumed'].get(c);pr=dict(live=False,RSS_bytes=0,PSS_bytes=0);done=False
  if row:
   ip=P(row['intent']);need(sha(ip)==row['intent_sha256'],'foreign intent drift');iv=read(ip);need(iv['uuid']==row['uuid'] and iv['cohort']==c,'foreign intent scope')
   out=root/'DTC/run/results'/row['uuid'];mp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
   never_started=(not mp.exists() and row.get('execution_receipt') and read(out/'NATIVE_EXIT.json')==row['execution_receipt'] and row['execution_receipt'].get('native_simulator_observed')is False and row['execution_receipt'].get('launcher_wait_returncode')==127 and row['execution_receipt'].get('automatic_retry')is False and q.get('model_automatic_retries')==0)
   need(mp.exists() or never_started,'consumed missing actual model identity')
   if mp.exists():iv=read(mp);pr=m.process(iv['pid'],iv['start_ticks'])
   if pr['live']:
    proc=P('/proc')/str(pr['pid']);argv=[x.decode()for x in (proc/'cmdline').read_bytes().split(bytes([0]))if x];expected=s['native_simulator_argv'];need(argv[-len(expected):]==expected,'foreign actual argv mismatch')
    need(any(x.split()[-1]==expected[0]for x in (proc/'maps').read_text().splitlines()if x.split()),'foreign ELF map mismatch');need(sha(expected[0])==s['binary_sha256'],'foreign loaded ELF bytes')
    models.append(dict(request=req,cohort=c,uuid=row['uuid'],pid=pr['pid'],start_ticks=pr['start_ticks'],CPU_affinity=pr['affinity']));cpus+=pr['affinity']
   done=bool(row.get('execution_receipt'));need(not(done and pr['live']),'execution receipt with live generation')
  # Existing RSS is already excluded from MemAvailable. Reserve only possible growth.
  growth=0 if done else max(0,min(hard,max(pred,pr['RSS_bytes']))-pr['RSS_bytes'])
  rows.append(dict(request=req,cohort=c,kind='EXACT_DTC_DONE_ZERO_MODEL_RAM'if done else'EXACT_DTC_REMAINING_MODEL_GROWTH',additional_RAM_bytes=growth,estimate_bytes=pred,hard_bytes=hard,**pr))
  pins.append(dict(path=str(sf),sha256=q['admitted_specs'][c]))
 owner=m.process(q['owner_pid'],q['owner_start_ticks']);need(not owner['live'] or any(x.get('pid')==owner['pid'] and x.get('start_ticks')==owner['start_ticks'] for x in existing),'unmapped live owner margin requires explicit review')
 rr=d['owner_resource_ref'];owner_math=load(rr['path'],'v5_d_owner_'+str(d['budget'])+'_'+root.name,rr['sha256'])
 projected=owner_math._dynamic(owner_math._peer(),root,q,claims,policy['metadata_reserve_bytes'])
 need(projected['projection_within_registered_ceiling'],'foreign derived write bound exceeds carrier')
 need(sha(cp)==cp_sha,'foreign claims transitioned;resample')
 return dict(pending_cpu_claims=pending_cpu_claims,protected_cpu_exclusions=policy.get('protected_cpu_exclusions',[]),projected_remaining_write_bytes=projected['projected_write_bytes'],projected_write_entries=projected['writes'],exact_archived_nonlive_count=projected['exact_archived_nonlive_count'],published_lifetime_ceiling_bytes=q['reserved_write_bytes'],owner_resource_ref=rr,ram=rows,models=models,reserved_cpus=sorted(set(cpus)),pin=dict(path=str(cp),sha256=cp_sha),policy_ref=pref,owner=owner,admitted_spec_pins=pins,
 confirmed_foreign_host_floor_bytes=policy['min_host_headroom_bytes'],confirmed_foreign_cgroup_floor_bytes=policy['min_cgroup_headroom_bytes'],confirmed_foreign_native_floor_bytes=policy['native_safety_floor_bytes'])
def shared():
 b=load(BASE,'v5_d_qualified_v3',BASE_SHA);b.SCOPES[REQUEST]=ROOT
 v4=HERE.parent.parent/'performance_first_v4_20261104_v1'
 b.SCOPES.update({'EP_L2_PFV4_A1_STENCIL_SOURCE78_850_L100_V1':v4/'track_a/resource_admission_followup_v2/A1/execution','EP_L2_PFV4_A3_TRANSPOSE_SOURCE78_850_L100_V1':v4/'track_a/resource_admission_followup_v2/A3/execution','EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104':v4/'track_b/private_execution/vector1700'})
 original_classify=b.classify
 def classify(argv):
  # A literal build target is not an executed ELF. All unknown executable wrappers remain HOLD.
  if argv and Path(argv[0]).name in ['cmake','ninja','gmake','make'] and 'accel-sim.out' in argv and all('/' not in x for x in argv if Path(x).name=='accel-sim.out'):return 'NOT_MODEL'
  return original_classify(argv)
 b.classify=classify
 runtime=b.runtime
 def wrapped_runtime():
  v=runtime();factory=v.qualified_math
  def qualified():
   h=factory();base=h.base
   def mappedbase():
    m=base();foreign=m.foreign_commitments
    def mapped(reg):
     f=foreign(reg);f['V5_DTC_exact_accounting']={}
     need(sha(PIN)==PIN_SHA,'foreign mapper contract drift')
     for req,d in read(PIN).items():
      q=reg['registered_future_requests'].get(req)
      if q is None:continue
      try:
       x=map_owner(req,q,d,m,f['foreign_RAM_entries'])
       carriers=[z for z in f['foreign_write_entries']if z['request']==req]
       need(len(carriers)==1 and carriers[0]['kind']=='ADVERTISED_UNKNOWN_WRITER' and carriers[0]['bytes']==q['reserved_write_bytes'],'unexpected foreign write carrier')
       carriers[0].update(bytes=x['projected_remaining_write_bytes'],kind='V5_EXACT_DTC_REMAINING_WRITES_WITH_OWN_RESTORE_BOUND',published_lifetime_ceiling_bytes=q['reserved_write_bytes'])
       f['foreign_RAM_entries']+=x['ram'];f['V5_DTC_exact_accounting'][req]=x
       # Remove only this exact unresolved mapping error after full identity join.
       err='unmapped active foreign RAM owner '+req
       f['foreign_metadata_errors']=[e for e in f['foreign_metadata_errors']if e!=err]
       for k in ['confirmed_foreign_host_floor_bytes','confirmed_foreign_cgroup_floor_bytes','confirmed_foreign_native_floor_bytes']:f[k]=max(f.get(k,0),x[k])
      except Exception as exc:f['foreign_metadata_errors'].append('V5_DTC_MAPPING_HOLD '+req+' '+repr(exc))
     f['foreign_additional_RAM_bytes']=sum(x['additional_RAM_bytes']for x in f['foreign_RAM_entries'])
     f['foreign_remaining_write_bytes']=sum(x['bytes']for x in f['foreign_write_entries'])
     # One same-owner live/remaining output and restore projection replaces each exact carrier, preserving the original registry ceiling as evidence.
     return f
    m.foreign_commitments=mapped;return m
   h.base=mappedbase;return h
  v.qualified_math=qualified;return v
 b.runtime=wrapped_runtime;return b
def snapshot():
 b=shared();s=b.snapshot(REQUEST)
 for req,x in s.get('V5_DTC_exact_accounting',{}).items():
  s['EP_CPU_claims'] += [dict(request=req,cohort='FOREIGN_RESERVED_CPU',cpu=c,state='FOREIGN_RESERVED')for c in sorted(set(x['reserved_cpus'])|set(x['protected_cpu_exclusions']))]
  s['EP_CPU_claims'] += [dict(request=req,cohort=z['cohort'],cpu=z['cpu'],state='CLAIMED')for z in x['pending_cpu_claims']]
 s['occupied_model_or_claim_cpus']=sorted(set(s['occupied_model_or_claim_cpus'])|{z['cpu']for z in s['EP_CPU_claims']})
 s['V5_foreign_write_carriers_replaced_once_by_owner_exact_remaining_projection']=True
 s['resource_admission_is_not_science_permission']=True
 return s
def admit(s,a,w,policy=None):
 need(s.get('current_request')==REQUEST,'cross-request snapshot')
 need(s.get('current_scope_registered')is True,'V5_A2_REQUEST_NOT_REGISTERED')
 p=dict(policy or {});p['max_global_EP_models']=p.get('max_global_EP_models',10);p['native_safety_floor_bytes']=max(p.get('native_safety_floor_bytes',0),5*(1<<30))
 need(p['max_global_EP_models']in[2,10],'cap not authorized');return shared().admit(s,a,w,p)
def forecast(input_id,history,policy=None):return shared().forecast(input_id,history,policy)
