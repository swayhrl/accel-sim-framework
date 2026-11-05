"""Minimal A-private activation delta. Default dry-run; never Native/registry/start."""
from pathlib import Path
import argparse,ast,copy,fcntl,hashlib,json,os,sys,time
HERE=Path(__file__).resolve().parent
PLAN=json.loads((HERE/'ACTIVATION_CHANGE_PLAN.json').read_bytes())
ROOT=Path(PLAN['private_graph']);R=ROOT/'runtime';Q=ROOT/'execution/control'
def need(v,m):
 if not v:raise ValueError(m)
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):return sha_bytes(Path(p).read_bytes())
def read(p):return json.loads(Path(p).read_bytes())
def encode(d):return (json.dumps(d,sort_keys=True,indent=2)+'\n').encode()
def exact(r):need(type(r)is dict and sha(r['path'])==r['sha256'],'immutable approval ref drift');return read(r['path'])
def refbytes(p,b):return dict(path=str(p),sha256=sha_bytes(b))
def patch_function(text,name,replace):
 t=ast.parse(text);n=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name==name)
 return ''.join(text.splitlines(keepends=True)[:n.lineno-1])+replace+'\n'+''.join(text.splitlines(keepends=True)[n.end_lineno:])
def reviewed(approval,approval_ref):
 need(approval.get('approved_by')=='EP-MAIN'and approval.get('explicit_user_approval')is True,'Main exact scientific activation approval required')
 need(approval.get('request_id')==PLAN['request_id']and approval.get('Source5')==PLAN['Source5'],'approval request/Source5')
 need(approval.get('allowed_cohorts')==PLAN['exact_cohorts']and approval.get('approved_launches')==3 and approval.get('per_cohort_budget')=={c:1 for c in PLAN['exact_cohorts']},'approval exact independent3 budget')
 need(approval.get('hard_wall_seconds')==28800 and approval.get('soft_wall_reference_seconds')==3600 and approval.get('independent_release')is True,'approval wall/release contract')
 ur=approval.get('fresh_user_authorization_ref');need(type(ur)is dict and sha(ur['path'])==ur['sha256']and Path(ur['path']).stat().st_size>0,'fresh user scope transcript pin')
 family=exact(ur);need(family.get('explicit_user_approval')is True and family.get('Source5')==PLAN['Source5']and family.get('goal')==PLAN['request_id']and family.get('allowed_cohorts')==PLAN['exact_cohorts'],'Main family user authorization scope')
 u=family['user_request_ref'];need(sha(u['path'])==u['sha256'],'fresh private user request text pin')
 return approval
def build_payload(original,approval=None,approval_ref=None):
 writes={}
 engine=original[str(R/'ep_perf_native_wv_modes_draft.py')].decode()
 # Remove the D template's nonexistent accepted-peer branch; every new point
 # uses only its matched newSource peer SPEC, never completion/acceptance as gate.
 old="read(scope.family_row(s)['peer_accepted_spec_ref']['path'])if scope.family_row(s)['peer_accepted_spec_ref']else read(spec_path(s['same_background_peer_cohort']))"
 need(engine.count(old)==1,'Main engine changed, review new baseline before patch')
 engine=engine.replace(old,"read(spec_path(s['same_background_peer_cohort']))")
 # Existing execution, monitor and consume functions remain byte/AST unchanged.
 newfresh="""def fresh_science_authorization(s):
    a=exact(s['Main_scientific_launch_authorization'])
    need(a.get('explicit_user_approval')is True and a.get('approved_launches')==3 and a.get('allowed_cohorts')==sorted(ALLOWED_COHORTS)and a.get('goal')==GOAL and a.get('Source5')==s['source_identity'],'MISSING_FRESH_EXACT_REQUEST3_SCIENTIFIC_AUTHORIZATION')
    need(a.get('request_ref')==ref(ROOT/'control/EXACT_REQUEST.json'),'fresh request identity drift')
    need(a.get('independent_release')is True and a.get('per_cohort_budget')=={c:1 for c in ALLOWED_COHORTS},'exact independent3 release/budget')
    need(a.get('hard_wall_seconds')==s['limits']['wall_seconds']==28800 and s.get('soft_wall_reference_seconds')==a.get('soft_wall_reference_seconds')==3600,'new hard wall and soft reference binding')
    source=exact(a['Main_activation_approval_ref'])
    need(source.get('approved_by')=='EP-MAIN'and source.get('explicit_user_approval')is True and source.get('request_id')==GOAL and source.get('Source5')==s['source_identity'],'Main activation owner/source')
    need(source.get('allowed_cohorts')==a['allowed_cohorts']and source.get('per_cohort_budget')==a['per_cohort_budget']and source.get('hard_wall_seconds')==28800 and source.get('independent_release')is True,'Main activation exact scope')
    u=a['user_request_ref'];need(sha(u['path'])==u['sha256'],'fresh private user request text drift')
    return a"""
 engine=patch_function(engine,'fresh_science_authorization',newfresh)
 guard=original[str(R/'native_route_guard_v3.py')].decode()
 oldline=next(l for l in guard.splitlines()if 'c.need(all(x in 'in l)
 guard=guard.replace(oldline,' c.need(r["goal"]=='+repr(PLAN['request_id'])+' and sorted(r["exact_cohorts"])=='+repr(PLAN['exact_cohorts'])+',"outside exact A3 independent scope")')
 writes[str(R/'native_route_guard_v3.py')]=guard.encode()
 # The engine pins the corrected owned guard before HostQ is rebuilt.
 t=ast.parse(engine);n=next(n for n in t.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='NATIVE_ROUTE_GUARD_REF'for x in n.targets))
 lines=engine.splitlines();lines[n.lineno-1]='NATIVE_ROUTE_GUARD_REF='+repr(refbytes(R/'native_route_guard_v3.py',writes[str(R/'native_route_guard_v3.py')]));engine='\n'.join(lines)+'\n'
 writes[str(R/'ep_perf_native_wv_modes_draft.py')]=engine.encode()
 request=json.loads(original[str(Q/'EXACT_REQUEST.json')]);request.update(state='USER_APPROVED_PENDING_MAIN_NATIVE_REGISTRATION',scientific_authorization=True,independent_release=True,soft_wall_reference_seconds=3600)
 for c in request['cases']:
  need(c['limits']['wall_seconds']==3600,'unexpected old request wall');c['limits']['wall_seconds']=28800;c['soft_wall_reference_seconds']=3600;c['release_condition']='INDEPENDENT_OWN_QUALIFICATION_RESOURCE_AND_ONE_START_ONLY'
 writes[str(Q/'EXACT_REQUEST.json')]=encode(request)
 if approval is not None:
  reviewed(approval,approval_ref)
  auth=copy.deepcopy(exact(approval['fresh_user_authorization_ref']));auth.update(request_ref=refbytes(Q/'EXACT_REQUEST.json',writes[str(Q/'EXACT_REQUEST.json')]),Main_activation_approval_ref=approval_ref,fresh_user_authorization_ref=approval['fresh_user_authorization_ref'],status='MAIN_EXACT_APPROVED3_PENDING_NATIVE_REGISTRATION')
  writes[str(Q/'USER_AUTHORIZATION.json')]=encode(auth)
 else:
  writes[str(Q/'USER_AUTHORIZATION.json')]=original[str(Q/'USER_AUTHORIZATION.json')]
 def current_ref(p):
  p=str(p);return refbytes(p,writes[p]if p in writes else Path(p).read_bytes())
 hostPath=Q/'HOST_QUALIFICATION_MAIN_RESOURCE_V5.json';host=json.loads(original[str(hostPath)])
 host['modules']=[current_ref(x['path'])for x in host['modules']]
 host['Main_activation_delta_scope']='same Source5/283/resource binding; hard wall8h and independent exact3; corrected A guard/cohort/peer metadata'
 if approval_ref:host['Main_activation_approval_ref']=approval_ref
 writes[str(hostPath)]=encode(host)
 for path in original:
  if not path.endswith('/control/FROZEN_SPEC.json'):continue
  s=json.loads(original[path]);oldlimits=dict(s['limits'])
  need(s['source_identity']==PLAN['Source5']and s['resource_module_ref']==PLAN['expected_resource_module_ref']and len(s['expected_effective_options'])==283,'Source283/latest resource binding changed')
  need(oldlimits['wall_seconds']==3600,'unexpected old Spec wall');s['limits']['wall_seconds']=28800;s['soft_wall_reference_seconds']=3600
  s['Main_scientific_launch_authorization']=current_ref(Q/'USER_AUTHORIZATION.json');s['host_qualification_ref']=current_ref(hostPath);s['host_engine_ref']=current_ref(R/'ep_perf_native_wv_modes_draft.py');s['native_route_guard_ref']=current_ref(R/'native_route_guard_v3.py')
  if approval_ref:
   s['parent_scientific_authorization_ref']=approval['fresh_user_authorization_ref'];s['scientific_scope_approved']=True
  # Main alone later registers/activates. These proposal markers do not claim it.
  s['scientific_scope_activated']=False;s['launch_budget_registered']=False;s['scientific_launch_permission']=False
  s['qualification_status']='MAIN_APPROVED_EXACT3_HARD8H_PENDING_NATIVE_REGISTRATION'
  for p in list(s['pinned_files']):
   if p in writes:s['pinned_files'][p]=sha_bytes(writes[p])
  for p in [str(hostPath),str(R/'ep_perf_native_wv_modes_draft.py'),str(R/'native_route_guard_v3.py')]:s['pinned_files'][p]=sha_bytes(writes[p])
  if approval_ref:s['pinned_files'][approval_ref['path']]=approval_ref['sha256']
  need({k:v for k,v in s['limits'].items()if k!='wall_seconds'}=={k:v for k,v in oldlimits.items()if k!='wall_seconds'},'resource limits accidentally changed')
  writes[path]=encode(s)
 route=json.loads(original[str(Q/'NATIVE_ENTRY_ROUTE_V4.json')]);route.update(goal=PLAN['request_id'],entry_ref=current_ref(R/'native_request3'),frontend_ref=current_ref(R/'ep_perf_frontend.py'),guard_module_ref=current_ref(R/'native_route_guard_v3.py'),exact_cohorts=PLAN['exact_cohorts'],independent_release=True)
 # Retain resource latest dependencies; deduplicate exact paths, then include
 # every reviewed HostQ module. Shared route stays uninstalled until Main owns it.
 owned={x['path']:current_ref(x['path'])for x in route.get('owned_runtime_pins',[])}
 for x in host['modules']+[current_ref(hostPath)]:owned[x['path']]=x
 route['owned_runtime_pins']=[owned[p]for p in sorted(owned)];route['scientific_scope_activated']=False
 need(route['status']=='PRIVATE_NOT_INSTALLED_NOT_AUTHORIZED','already installed route must never be hot-patched')
 writes[str(Q/'NATIVE_ENTRY_ROUTE_V4.json')]=encode(route)
 return writes
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--approval-ref-file',type=Path);a=ap.parse_args()
 originals={}
 for r in PLAN['changed_files']:
  need(sha(r['path'])==r['sha256'],'private preimage changed; Main must review current version')
  originals[r['path']]=Path(r['path']).read_bytes()
 approval_ref=read(a.approval_ref_file)if a.approval_ref_file else None
 approval=exact(approval_ref)if approval_ref else None
 if a.apply:need(approval is not None,'--apply requires exact Main approval ref')
 writes=build_payload(originals,approval,approval_ref)
 info=dict(status='PRIVATE_APPLY_CANDIDATE'if a.apply else'DRY_RUN_NO_WRITES',new_start_budget_to_register=3,actual_budget_registered=0,independent_release=True,Source5=PLAN['Source5'],resource_module_preserved=PLAN['expected_resource_module_ref'],hard_wall=28800,soft_reference=3600,changes=[dict(path=p,before_sha256=sha_bytes(originals[p]),after_sha256=sha_bytes(b))for p,b in writes.items()],prospective_request_ref=refbytes(Q/'EXACT_REQUEST.json',writes[str(Q/'EXACT_REQUEST.json')]),Shared_Native_registry_writes=0,model_starts=0)
 if not a.apply:print(json.dumps(info,sort_keys=True));return 0
 # No authority has been installed or consumed; refuse any live/claimed graph.
 need(read(Q/'DISPATCH_CLAIMS.json').get('claims')=={},'existing A claims; no live patch')
 reg=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
 need(PLAN['request_id']not in reg['registered_future_requests'],'scope already registered; immutable scientific Specs cannot be patched')
 with (HERE/'A_PRIVATE_APPLY.lock').open('a+b')as f:
  fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  for p,b in originals.items():need(Path(p).read_bytes()==b,'private graph transitioned before apply')
  backup=HERE/('preimages_'+str(time.time_ns()));backup.mkdir()
  for p,b in originals.items():
   out=backup/Path(p).relative_to(ROOT);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b)
  (backup/'INTENT.json').write_bytes(encode(info))
  for p,b in writes.items():
   out=Path(p);temp=out.with_name('.'+out.name+'.A_activation_tmp');need(not temp.exists(),'retained previous partial patch must be diagnosed')
   with temp.open('xb')as stream:stream.write(b);stream.flush();os.fsync(stream.fileno())
   os.replace(temp,out)
  info.update(status='PRIVATE_APPLIED_AWAIT_MAIN_NATIVE_BUDGET_INSTALL',preimages=str(backup))
  (HERE/'PRIVATE_APPLY_RECEIPT.json').write_bytes(encode(info))
 print(json.dumps(info,sort_keys=True));return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as exc:print(json.dumps(dict(status='HOLD_NO_SHARED_WRITES_NO_MODELS',reason=str(exc))),file=sys.stderr);raise SystemExit(2)
