"""Read-only V2 scopes. No actors, ledger writes, native entries or budget changes.
Explicit selftest writes only its own CPU receipt/private temporary fixture.
"""
import pathlib,hashlib,importlib.util,json,fcntl,time
P=pathlib.Path;J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');D=P(__file__).resolve().parent
FROZEN=J/'execution_stencil_wv_20261103_v1/tools/stage2_resources_stencil.py';FROZEN_SHA='4869dab32f58c99a6f9e41a53722f176d2965195f7a5636d56073cd64af1264a'
REQUESTS={'system':'EP_L2_SYSTEM_850MHZ_PARAMETER_FAMILY_V2_20261104_V1','highclock':'EP_L2_CC_CAM_REPAIRED_VECTOR4M_850_1275_1700_V1'}
NEW_SCOPES={REQUESTS['system']:J/'execution_system850_v2_20261104_v1/system',REQUESTS['highclock']:J/'execution_cc_cam_highclock_20261104_v1/highclock'}
def qualified_math():
 if hashlib.sha256(FROZEN.read_bytes()).hexdigest()!=FROZEN_SHA:raise ValueError('frozen H scientific resource math drift')
 s=importlib.util.spec_from_file_location('v2_pinned_H_readonly_math',FROZEN);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 X=J/'execution_performance_first_20261103_v1';m.SCOPES=dict(m.SCOPES,**{'EP_L2_PF_RETENTION_CLASS_FWT_GEMM_20261103_V1':X/'retention','EP_L2_PF_DRAM_SERVICE_FWT_GEMM_VECTOR4M_20261103_V1':X/'service'},**NEW_SCOPES)
 return m
DEFAULT_POLICY=dict(qualified_math().DEFAULT_POLICY)
def snapshot(current_request):
 if current_request not in NEW_SCOPES:raise ValueError('unrecognized current V2 family')
 h=qualified_math();s=h.snapshot(current_request);b=h.base()
 with b.LOCK.open('rb')as f:
  fcntl.flock(f,fcntl.LOCK_SH);raw=b.REG.read_bytes();reg=json.loads(raw);fingerprint=hashlib.sha256(raw).hexdigest();fcntl.flock(f,fcntl.LOCK_UN)
 if fingerprint!=s.get('registry_sha256'):s['foreign_metadata_errors'].append('registry changed while sampling globalEP cap; resample')
 entries=[]
 for req,q in reg['registered_future_requests'].items():
  if not req.startswith('EP_'):continue
  rows=q.get('consumed',{})
  if not isinstance(rows,dict):
   if q.get('state')=='RUNNING'and rows:s['foreign_metadata_errors'].append('untyped activeEP consumed ledger '+req)
   continue
  for c,row in rows.items():
   if row.get('state')in ['CONSUMED_BEFORE_FORK','RUNNING']:entries.append(dict(request=req,cohort=c,state=row['state']))
 s.update(schema='EP_MAIN_V2_SCOPED_READONLY_RESOURCE_SNAPSHOT_V1',current_request=current_request,current_scope_registered=current_request in reg['registered_future_requests'],new_scope_registration={q:('REGISTERED'if q in reg['registered_future_requests']else'ABSENT_INACTIVE_NOT_SCIENCE_AUTHORIZED')for q in NEW_SCOPES},all_covered_EP_scope_roots={q:str(p)for q,p in h.SCOPES.items()},global_EP_consumed_active_entries=entries,global_EP_consumed_active_count=len(entries),max_global_EP_models=2,cap_is_prospective_preconsume=True,resource_admission_is_not_native_or_budget_permission=True,shared_restore_mutex_proven=False,one_scope_restore_bound_bytes=128*(1<<20),two_new_scope_restore_window_upper_bound_bytes=256*(1<<20),restore_math='FROZEN_SCOPE_LOCAL_MAX_RESULT_WINDOW; TWO_ACTIVE_FAMILIES_EACH128MiB_SUM256MiB_UPPERBOUND; NOT_CLAIMED_CROSS_SCOPE_DEDUP',dispatcher_created=False)
 return s
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 if s.get('current_request')not in NEW_SCOPES:raise ValueError('unknown/cross-scope current resource request')
 d=qualified_math().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
 if type(s.get('global_EP_consumed_active_count'))is not int:d['hold_reasons'].append('GLOBAL_EP_CAP_SAMPLE_UNKNOWN')
 elif s['global_EP_consumed_active_count']>=2:d['hold_reasons'].append('GLOBAL_EP_ACTIVE_MODEL_CAP_2')
 d['pass_admission']=not d['hold_reasons'];d['global_EP_active_count']=s.get('global_EP_consumed_active_count');d['new_science_permission']=False;d['global_restore_mutex_proven']=False;return d
def forecast(input_id,history,policy=None):return qualified_math().forecast(input_id,history,policy=policy)

def selftest():
 import copy,tempfile,datetime
 G=1<<30;M=1<<20;checks=[]
 def check(label,fn,reject=False):
  try:v=fn();ok=not reject and v is not False;detail=str(v)[:300]
  except Exception as e:ok=reject;detail=repr(e)
  checks.append(dict(label=label,passed=ok,detail=detail));assert ok,(label,detail)
 check('seven_scopes_preserve_E_H_X_plus_new2',lambda:len(qualified_math().SCOPES)==7)
 check('unknown_current_scope_reject',lambda:snapshot('UNKNOWN'),True)
 s=snapshot(REQUESTS['system']);check('actual_snapshot_no_metadata_error',lambda:not s['foreign_metadata_errors']);check('two_new_unregistered_are_inactive_not_error',lambda:all(z=='ABSENT_INACTIVE_NOT_SCIENCE_AUTHORIZED'for z in s['new_scope_registration'].values()))
 check('actual512MiB_growth256MiB_write_probe_PASS_no_launch',lambda:admit(s,512*M,256*M)['pass_admission'])
 for label,mut in [('disk',lambda z:z.update(native_free_bytes=0)),('hostRAM',lambda z:z.update(host_MemAvailable_bytes=0)),('cgroup',lambda z:z.update(cgroup_effective_headroom_bytes=0)),('inodes',lambda z:z.update(free_inodes=0)),('stale',lambda z:z.update(monotonic=time.monotonic()-100)),('foreignunknown',lambda z:z['foreign_metadata_errors'].append('UNKNOWN_ACTIVE_OWNER'))]:
  z=copy.deepcopy(s);mut(z);check(label+'_HOLD',lambda z=z:not admit(z,512*M,256*M)['pass_admission'])
 z=copy.deepcopy(s);z['global_EP_consumed_active_count']=1;check('one_globalEP_accepts_second_preconsume',lambda:admit(z,512*M,256*M)['pass_admission']);z['global_EP_consumed_active_count']=2;check('two_globalEP_blocks_third_preconsume',lambda:not admit(z,512*M,256*M)['pass_admission'])
 for group in REQUESTS:
  p=D/('resources_'+group+'.py');sp=importlib.util.spec_from_file_location('wrapper_'+group,p);w=importlib.util.module_from_spec(sp);sp.loader.exec_module(w);other=next(q for q in NEW_SCOPES if q!=REQUESTS[group]);check(group+'_strict_current_wrapper',lambda w=w,other=other:w.admit(dict(s,current_request=other),M,M),True)
 h=qualified_math();b=h.base()
 with tempfile.TemporaryDirectory(prefix='OWNED_CPU_SCOPE_',dir=D)as temp:
  for n,(qid,root)in enumerate(NEW_SCOPES.items()):
   fake=P(temp)/str(n);h.SCOPES[qid]=fake;c='TEST_ONLY_'+str(n);sp=fake/'cases'/c/'control/FROZEN_SPEC.json';sp.parent.mkdir(parents=True);sp.write_text(json.dumps(dict(science_request_id=qid,cohort=c,limits=dict(result_bytes=128*M,RSS_bytes=4*G))));ds=hashlib.sha256(sp.read_bytes()).hexdigest();cp=fake/'control/DISPATCH_CLAIMS.json';cp.parent.mkdir(parents=True);cp.write_text(json.dumps(dict(claims={c:dict(state='RUNNING',spec_sha256=ds,estimated_peak_RAM_bytes=2*G,remaining_write_bytes=200*M,model_pid=100+n,model_start_ticks=1)})))
  class Fake:
   def foreign_commitments(self,legacy):
    assert not any(q in legacy['registered_future_requests']for q in h.SCOPES)
    return dict(foreign_RAM_entries=[dict(additional_RAM_bytes=2*G)],foreign_write_entries=[dict(bytes=100*M)],foreign_metadata_errors=[],foreign_claims_pins={})
   def process(self,pid,ticks):return dict(live=True,RSS_bytes=3*G//4,PSS_bytes=3*G//4)
   def owner_growth(self,q,estimate,hard,rss):return max(0,min(hard,max(estimate,rss))-rss)
  fake=Fake();reg={'registered_future_requests':{'FOREIGN_LEGAL_OWNER':{}}}
  for qid,root in [(q,h.SCOPES[q])for q in NEW_SCOPES]:
   claim=json.loads((root/'control/DISPATCH_CLAIMS.json').read_bytes())['claims'];c=next(iter(claim));reg['registered_future_requests'][qid]=dict(consumed={c:dict(state='RUNNING')},admitted_specs={c:claim[c]['spec_sha256']},reserved_write_bytes=330*M)
  f=h.commitments(reg,REQUESTS['system'],fake);check('other_new_family_RAM_growth_minus_actualRSS_once',lambda:f['foreign_additional_RAM_bytes']==2*G+5*G//4);check('other_family_remainingwrites_and_one128MiBwindow',lambda:f['foreign_remaining_write_bytes']==430*M)
  both=h.commitments(reg,'EP_L2_WV_DECOMPOSITION_V2',fake);check('both_new_families_RAM_preserved',lambda:both['foreign_additional_RAM_bytes']==2*G+2*(5*G//4));check('two_local128windows_sum256_upperbound_not_dedup',lambda:both['foreign_remaining_write_bytes']==100*M+2*(200*M+128*M+2*M))
  reg['registered_future_requests'][REQUESTS['highclock']]['reserved_write_bytes']=1;check('underadvertised_other_write_carrier_HOLD',lambda:bool(h.commitments(reg,REQUESTS['system'],fake)['foreign_metadata_errors']));reg['registered_future_requests'][REQUESTS['highclock']]['reserved_write_bytes']=330*M
  root=h.SCOPES[REQUESTS['highclock']];(root/'control/DISPATCH_CLAIMS.json').write_text(json.dumps(dict(claims={})));check('consumed_without_resource_claim_HOLD',lambda:bool(h.commitments(reg,REQUESTS['system'],fake)['foreign_metadata_errors']))
  unknown={'registered_future_requests':{'EP_UNMAPPED_ACTIVE':dict(state='RUNNING',consumed={'x':dict(state='RUNNING')},reserved_write_bytes=M)}};check('real_frozen_mapper_unknownactive_failclosed',lambda:bool(b.foreign_commitments(unknown)['foreign_metadata_errors']))
 receipt=dict(schema='EP_MAIN_V2_RESOURCE_CANDIDATE_CPU_QUALIFICATION_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PASS',passed=len(checks),total=len(checks),checks=checks,actual_readonly_snapshot=s,old_X_scope_archival_not_changed=True,model_starts=0,dispatcher_starts=0,future_budget_or_native_or_registry_writes=0,runtime_writes=0,global_restore_mutex_proven=False)
 (D/'CPU_QUALIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(status='PASS',passed=len(checks),total=len(checks))))
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--selftest',action='store_true');z=a.parse_args()
 if z.selftest:selftest()
 else:print(json.dumps(dict(status='READ_ONLY_ADAPTER_DEFINITIONS_NO_SCIENCE_PERMISSION',models_started=0)))
