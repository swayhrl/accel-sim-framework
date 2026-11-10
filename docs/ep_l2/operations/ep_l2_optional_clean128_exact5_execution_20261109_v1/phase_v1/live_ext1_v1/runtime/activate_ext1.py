#!/usr/bin/env python3
"""Install the exact additive EXT1 Native route, then register one scoped start."""
import fcntl,hashlib,importlib.util,json,os,sys,uuid
from pathlib import Path
P=Path
R=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
REQ='EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1'
CASE='EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1'
H=R/'runtime/host_stencil_ext1_bound_v1'
SPEC=R/'cases'/CASE/'control/FROZEN_SPEC.json'
ROUTE=R/'control/NATIVE_ENTRY_ROUTE_EXT1.json'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def need(x,m):
 if not x:raise RuntimeError(m)
def load(p,n):
 x=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(x);x.loader.exec_module(m);return m
def install():
 s=json.loads(SPEC.read_bytes());route=json.loads(ROUTE.read_bytes())
 need(s['cohort']==CASE and s['science_request_id']==REQ and s['native_entry_ref']==route['entry_refs'][REQ],'Spec/route mismatch')
 auth=json.loads(P(route['Main_user_authorization_ref']['path']).read_bytes())
 need(auth['explicit_user_approval'] and auth['approved_total_launches']==1 and auth['cohort']==CASE,'specific approval absent')
 old=P(route['old_global_ref']['path']).read_bytes();prefix=P(route['owned_prefix_ref']['path']).read_bytes()
 need(old.startswith(b'#!/bin/sh\nset -eu\n') and old.count(b'experiment:EP_PERF_CLEAN128_')==5,'old route changed')
 target=N/'bin/native';lock=N/'control/science_authority/NATIVE_ROUTE_UPDATE.lock'
 with lock.open('a+b') as f:
  fcntl.flock(f,fcntl.LOCK_EX)
  current=target.read_bytes()
  if current==prefix+old:
   status='EXISTING_EXACT_EXT1_ROUTE_REUSED'
  else:
   need(current==old,'shared Native changed; no install')
   tmp=target.with_name('.native.ext1.'+str(uuid.uuid4()))
   with tmp.open('xb') as g:g.write(prefix+old);g.flush();os.fsync(g.fileno())
   tmp.chmod(target.stat().st_mode&0o777)
   need(target.read_bytes()==old,'Native changed during lock')
   os.replace(tmp,target)
   status='EXT1_ROUTE_INSTALLED'
  check=load(R/'runtime/native_route_guard_ext1.py','ext1_guard').validate_current(ROUTE)
 print(json.dumps({'status':status,'route_ref':ref(ROUTE),'guard':check}))
def register():
 routecheck=load(R/'runtime/native_route_guard_ext1.py','ext1_guard_registration').validate_current(ROUTE)
 sys.path.insert(0,str(H))
 import ep_perf_common_v2 as c
 import ep_perf_native_wv_modes_draft as e
 s=json.loads(SPEC.read_bytes());need(c.GOAL==REQ and s['science_request_id']==REQ and s['cohort']==CASE,'Host identity')
 need(e.engineering_static(s)['status']=='EXT1_SOURCE5_EXACT_DELTA_PASS_NO_START','static qualification')
 snap=load(H/'resources_ext1_v2.py','ext1_resources_registration').snapshot()
 need(not snap['foreign_metadata_errors'] and not snap['actual_loader_aware_models'] and snap['true164_mount_verified'],'current resource metadata/model/mount')
 need(json.loads((R/'control/DISPATCH_CLAIMS.json').read_bytes())['claims']=={},'shared claim exists')
 authref=ref(R/'control/EXT1_USER_AUTHORIZATION.json')
 def fn(reg):
  rows=reg['registered_future_requests']
  if REQ in rows:
   q=rows[REQ]
   need(q['admitted_specs']=={CASE:sha(SPEC)} and q['authorization_ref']==authref and q['budget']==1 and q['automatic_retry'] is False and q['refund'] is False,'existing request identity differs')
   return {'status':'IDENTICAL_EXT1_REQUEST_REUSED','request':REQ}
  need(all(CASE not in (q.get('admitted_specs') if isinstance(q.get('admitted_specs'),dict) else {}) for q in rows.values()),'cohort registered elsewhere')
  eng=ref(H/'ep_perf_native_wv_modes_draft.py');common=ref(H/'ep_perf_common_v2.py')
  rows[REQ]={'request':REQ,'request_id':REQ,'resource_group_id':REQ,'owner':'EP-L2 Main','project':'EP_L2',
    'state':'REGISTERED_FRESH_SCOPE_NO_START','budget':1,'remaining':1,'consumed':{},
    'admitted_specs':{CASE:sha(SPEC)},'allowed_cohorts':[CASE],
    'authorization_ref':authref,'native_qualification_ref':ref(ROUTE),'native_entry_ref':ref(H/'native_b1'),
    'runtime_versions':{eng['sha256']:{'engine_ref':eng,'common_ref':common}},
    'source_identity':s['source_identity'],'source_keep':True,'independent_release':True,
    'automatic_retry':False,'refund':False,'global_model_concurrency_authorized':10,
    'global_model_concurrency_qualified':10,'reserved_write_bytes':(64+130)*1024*1024,
    'registered_utc':c.now()}
  return {'status':'EXT1_REGISTERED_ONE_START_NO_MODEL','request':REQ,'spec_ref':ref(SPEC)}
 result=c.transaction('REGISTER_EXT1_EXACT_ONE_SCOPED_BUDGET_NO_START',fn)
 print(json.dumps({'result':result,'route':routecheck}))
if __name__=='__main__':
 need(len(sys.argv)==2 and sys.argv[1] in ('install','register'),'install|register')
 (install if sys.argv[1]=='install' else register)()
