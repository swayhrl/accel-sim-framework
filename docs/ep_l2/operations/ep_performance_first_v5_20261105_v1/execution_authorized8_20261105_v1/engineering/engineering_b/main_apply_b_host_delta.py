#!/usr/bin/env python3
"""Exact Main B activation delta. Default dry-run; apply private graph only."""
from pathlib import Path
import argparse,ast,copy,fcntl,hashlib,json,os,stat,time
V=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1')
H=V/'track_b_fullf/host_private_candidate_v1';R=H/'runtime';E=H/'execution'
OUT=Path(__file__).parent
REQUEST='EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1'
CASES={'EP_PERF_PFV5_B1_VECTOR4M_F_BASELINE_1700_V1':'F_BASELINE','EP_PERF_PFV5_B1_VECTOR4M_F_PRESSURE_EPOCH_1700_V1':'F_PRESSURE_EPOCH'}
BASE_ENGINE_SHA='a9d3420fddad95bb261b590578aff9362a34b1496c24e529be4e3e0669e9171b'
SOURCE={'core_source_commit':'812fe1e029b4fb09afaf3d8d25d3f909464cc06c','framework_source_commit':'9dd1ee57a83d83b56b7874bc7c716185ab52c8f7','vendor_pybind11_commit':'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b','archive_sha256':'a7e9c8ce045710c8f3655aebb82a65628a5a18638036af17fa0ec8c755580d3e','binary_sha256':'a60600a418e6460e7aaf896b62469be0612046d0f4da34ac8c98da2eed3852e1'}
RESOURCE_PATH=str(V/'track_d_workloads/resource_scope_rebind_addendum_v1/resources_b_scoped_v5.py')
def need(x,m):
 if not x:raise ValueError(m)
def digest(b):return hashlib.sha256(b).hexdigest()
def read(p):
 def pairs(xs):
  d={}
  for k,v in xs:need(k not in d,'duplicate JSON key');d[k]=v
  return d
 return json.loads(Path(p).read_bytes(),object_pairs_hook=pairs)
def encoded(x):return (json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def ref(p,b=None):p=Path(p);b=p.read_bytes()if b is None else b;return dict(path=str(p),sha256=digest(b))
def exact(r):
 p=Path(r['path']);b=p.read_bytes();need(digest(b)==r['sha256'],'approval/ref drift:'+str(p));return read(p)
def validate_approval_object(a):
 need(a.get('schema')=='EP_MAIN_PFV5_HOST_RELEASE_DELTA_APPROVAL_V1','exact Main host-release approval schema')
 need(a.get('approved_by')=='EP-MAIN'and a.get('explicit_user_approval')is True,'Main explicit approval required')
 need(a.get('request_id')==REQUEST and a.get('Source5')==SOURCE,'exact B request/Source5')
 need(a.get('allowed_cohorts')==sorted(CASES),'exact sorted two B cohorts')
 need(type(a.get('approved_launches'))is int and a['approved_launches']==2,'exact2 launches')
 need(a.get('per_cohort_budget')=={c:1 for c in CASES},'one start per exact cohort')
 need(a.get('hard_wall_seconds')==7200 and a.get('soft_wall_reference_seconds')==900,'exact7200 hard/900 soft')
 need(a.get('independent_release')is True,'independent exact release')
 family=exact(a['fresh_user_authorization_ref'])
 need(family.get('schema')=='EP_MAIN_PFV5_FAMILY_USER_AUTHORIZATION_V1'and family.get('explicit_user_approval')is True and family.get('approved_by')=='EP-MAIN','real formal family science authorization')
 need(family.get('request_id')==family.get('goal')==REQUEST and family.get('Source5')==SOURCE,'family exact request/Source')
 for k in ['allowed_cohorts','approved_launches','per_cohort_budget','hard_wall_seconds','soft_wall_reference_seconds','independent_release']:need(family.get(k)==a[k],'family/host approval mismatch:'+k)
 need(family.get('automatic_retry')is False and family.get('source_keep')is True,'family no retry KEEP')
 need(family.get('user_request_ref')==ref(E/'control/USER_REQUEST.txt'),'formal authorization binds actual Main root summary')
 exact(a['parent_authorization_ref'])
 return family
def approval(path):
 r=read(path);a=exact(r);family=validate_approval_object(a);return r,a,family
def function_source(text,name):
 n=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name==name);return n,ast.get_source_segment(text,n)
def replace_function(text,name,body):
 n,_=function_source(text,name);lines=text.splitlines(keepends=True);return ''.join(lines[:n.lineno-1])+body+'\n'+''.join(lines[n.end_lineno:])
NEW_GATE="""def enforce_stage_gates(s,q,registry):
    need(SCOPED_MODES.get(s['cohort'])==s['mode'],'outside exact B two-point release')
    need(s['limits']['wall_seconds']==7200 and type(s.get('host_soft_warning_seconds'))is int and s['host_soft_warning_seconds']==900,'exact B hard/soft wall contract')
    need(s.get('independent_scientific_release')is True,'explicit independent release required')
    need(s.get('final_comparison_requirement')=='BOTH_SAME_SOURCE_CLOSED_ACCEPTED_ARCHIVED_TWO_NATIVE_RESTORES','qualified matching baseline retained for final comparison')
    return dict(status='EXACT_B_TWO_POINTS_INDEPENDENTLY_RELEASED',launch_completion_predecessor=None,
                same_source_final_comparison_required=True)
"""
COMPARISON="""def qualified_final_comparison():
    # Independent start/acceptance never requires a peer's completion. A final
    # performance comparison does require both exact same-Source accepted cells.
    registry,_=authority();q=registry['registered_future_requests'][GOAL]
    baseline_case='EP_PERF_PFV5_B1_VECTOR4M_F_BASELINE_1700_V1'
    optimized_case='EP_PERF_PFV5_B1_VECTOR4M_F_PRESSURE_EPOCH_1700_V1'
    baseline=read(spec_path(baseline_case));optimized=read(spec_path(optimized_case))
    module(baseline['mode_contract_ref'],'B_final_matched_pair').validate_fair_pair(baseline,optimized)
    b,br=accepted_cell(baseline_case,baseline,q)
    o,orr=accepted_cell(optimized_case,optimized,q)
    return dict(status='QUALIFIED_SAME_SOURCE_FINAL_F_POLICY_COMPARISON',
                source_identity=baseline['source_identity'],input_identity_sha256=baseline['input_identity_sha256'],
                baseline_cycles=b['cycles'],optimized_cycles=o['cycles'],
                saved_cycles=b['cycles']-o['cycles'],
                improvement_fraction=(b['cycles']-o['cycles'])/b['cycles'],
                baseline_accepted_point_ref=br['accepted_point_ref'],optimized_accepted_point_ref=orr['accepted_point_ref'],
                extra_scientific_starts=0)
"""
def replace_refs(x,mapping):
 if isinstance(x,dict):
  y={k:replace_refs(v,mapping)for k,v in x.items()}
  if isinstance(y.get('path'),str)and y['path']in mapping and 'sha256'in y:
   y['sha256']=digest(mapping[y['path']])
   if 'bytes'in y:y['bytes']=len(mapping[y['path']])
  if 'pinned_files'in y and isinstance(y['pinned_files'],dict):
   for p,b in mapping.items():
    if p in y['pinned_files']:y['pinned_files'][p]=digest(b)
  return y
 if isinstance(x,list):return [replace_refs(v,mapping)for v in x]
 return x
def build_plan(approval_file):
 approval_ref,a,family=approval(approval_file)
 mapping={};original={}
 def load(p):
  p=Path(p);need(p.is_file()and not p.is_symlink(),'regular existing private target');b=p.read_bytes();original[str(p)]=b;return b
 engine_path=R/'ep_perf_native_wv_modes_draft.py';text=load(engine_path).decode();need(digest(original[str(engine_path)])==BASE_ENGINE_SHA,'latest Main engine changed; rebase exact delta')
 _,old_gate=function_source(text,'enforce_stage_gates')
 need("accepted_cell('EP_PERF_PFV5_B1_VECTOR4M_F_BASELINE_1700_V1',s,q)"in old_gate,'expected sole old baseline stage gate')
 text=replace_function(text,'enforce_stage_gates',NEW_GATE+'\n'+COMPARISON)
 need(text.count('                eof = False\n')==1,'unique loop initializer')
 text=text.replace('                eof = False\n','                eof = False\n                soft_wall_warning_written = False\n',1)
 anchor='                    elapsed = time.monotonic() - began\n'
 soft="""                    if not soft_wall_warning_written and elapsed >= s['host_soft_warning_seconds']:
                        put(out/'HOST_SOFT_WALL_WARNING.json',dict(schema='EP_HOST_SOFT_WALL_WARNING_V1',
                            cohort=case,soft_wall_seconds=s['host_soft_warning_seconds'],
                            hard_wall_seconds=s['limits']['wall_seconds'],elapsed_seconds=elapsed,
                            action='WARNING_ONLY_NO_STOP',automatic_retry=False),True)
                        soft_wall_warning_written=True
"""
 need(text.count(anchor)==1,'unique elapsed monitor site');text=text.replace(anchor,anchor+soft,1)
 need("if elapsed > s['limits']['wall_seconds']:"in text,'original hard-stop guard retained')
 compile(text,str(engine_path),'exec');mapping[str(engine_path)]=text.encode()
 frontend=R/'ep_perf_frontend.py';fb=load(frontend);need(fb.count(BASE_ENGINE_SHA.encode())==1,'exact frontend engine pin');mapping[str(frontend)]=fb.replace(BASE_ENGINE_SHA.encode(),digest(mapping[str(engine_path)]).encode())
 # HostQ includes Main's current resource mapper; refresh only changed owned module pins.
 host=E/'control/HOST_QUALIFICATION_MAIN_RESOURCE_V5.json';hq=replace_refs(json.loads(load(host)),mapping)
 hq['Host_activation_delta']=dict(hard_wall_seconds=7200,soft_warning_seconds=900,independent_release=True,
     final_comparison_requires_qualified_matching_baseline=True,Main_host_delta_approval_ref=approval_ref,
     original_engine_preimage_sha256=BASE_ENGINE_SHA,old_CPU_qualification_not_repeated=True)
 mapping[str(host)]=encoded(hq)
 specs=[]
 for case,mode in sorted(CASES.items()):
  p=E/'cases'/case/'control/FROZEN_SPEC.json';s=json.loads(load(p))
  need(s['cohort']==case and s['mode']==mode and s['source_identity']==SOURCE,'exact current B private Spec')
  need(s['resource_module_ref']['path']==RESOURCE_PATH,'never revert Main latest resource mapper')
  need(digest(Path(RESOURCE_PATH).read_bytes())==s['resource_module_ref']['sha256'],'Main current resource mapper pin')
  need(s['limits']==dict(wall_seconds=900,RSS_bytes=2<<30,AS_bytes=10<<30,result_bytes=128<<20),'only current approved900 baseline limits expected')
  need(len(s['expected_effective_options'])==283,'strict283 preserved')
  s=replace_refs(s,mapping);s['limits']['wall_seconds']=7200;s['host_soft_warning_seconds']=900
  s['independent_scientific_release']=True
  s['final_comparison_requirement']='BOTH_SAME_SOURCE_CLOSED_ACCEPTED_ARCHIVED_TWO_NATIVE_RESTORES'
  s['Main_scientific_launch_authorization']=a['fresh_user_authorization_ref']
  s['Main_host_delta_approval_ref']=approval_ref
  mapping[str(p)]=encoded(s);specs.append(s)
 # Copy the canonical Main family authorization bytes to the original capsule
 # location; never alias the Host-delta approval as the formal science authority.
 auth=E/'control/USER_AUTHORIZATION.json';load(auth)
 mapping[str(auth)]=Path(a['fresh_user_authorization_ref']['path']).read_bytes()
 payload=E/'control/MAIN_ENGINEERING_INSTALL_PAYLOAD.json';pv=json.loads(load(payload));pv=replace_refs(pv,mapping)
 pv['spec_refs']=[ref(E/'cases'/s['cohort']/'control/FROZEN_SPEC.json',mapping[str(E/'cases'/s['cohort']/'control/FROZEN_SPEC.json')])for s in specs]
 pv['Main_host_delta_approval_ref']=approval_ref;pv['formal_family_authorization_ref']=a['fresh_user_authorization_ref']
 pv['independent_release']=True;pv['hard_wall_seconds']=7200;pv['soft_wall_reference_seconds']=900
 pv['registry_authorization_binding_required']=a['fresh_user_authorization_ref']
 mapping[str(payload)]=encoded(pv)
 for p,b in mapping.items():
  need(Path(p).is_relative_to(E)or Path(p).is_relative_to(R),'patch private B graph only')
 # Return content plan in memory; default invocation does not write a report.
 return dict(mapping=mapping,original=original,approval_ref=approval_ref,approval=a,specs=specs)
def preflight_unregistered():
 reg=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
 need(REQUEST not in reg['registered_future_requests'],'never mutate registered immutable B Specs')
 ledger=Path('/root/data/ep_l2_dtc_l1_native_v2/control/qualification_ledger')
 for case in CASES:
  need(not (ledger/(case+'.INTENT.json')).exists(),'B consumed intent exists')
  run=E/'cases'/case/'run'
  need(not run.exists()or not any(run.iterdir()),'B run directory already started')
def summary(plan):
 return dict(status='B_HOST_DELTA_DRY_RUN_PASS',approval_ref=plan['approval_ref'],
  changes=[dict(path=p,before_sha256=digest(plan['original'][p]),after_sha256=digest(b),bytes=len(b))for p,b in plan['mapping'].items()],
  hard_wall_seconds=7200,soft_wall_seconds=900,independent_release=True,
  final_comparison_requires_same_Source_qualified_baseline=True,formal_auth_not_aliased=True,
  registry_authorization_binding_required=plan['approval']['fresh_user_authorization_ref'],
  current_resource_mapping_retained=RESOURCE_PATH,budget_writes=0,shared_native_writes=0,models_started=0)
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--approval-ref-file',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args(argv)
 plan=build_plan(a.approval_ref_file);result=summary(plan)
 if not a.apply:return result
 preflight_unregistered()
 with (OUT/'APPLY.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  preflight_unregistered()
  for name,b in plan['original'].items():need(Path(name).read_bytes()==b,'private graph changed after planning')
  d=OUT/'preimages'/str(time.time_ns());d.mkdir(parents=True,exist_ok=False)
  pre=[]
  for name,b in plan['original'].items():
   dst=d/Path(name).relative_to(H);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(b)
   os.chmod(dst,stat.S_IMODE(Path(name).stat().st_mode));pre.append(dict(target=name,preimage_ref=ref(dst)))
  (d/'PREIMAGES.json').write_bytes(encoded(dict(approval_ref=plan['approval_ref'],preimages=pre)))
  staged=[]
  for name,b in plan['mapping'].items():
   target=Path(name);tmp=target.with_name('.'+target.name+'.B7200.'+str(time.time_ns()))
   with tmp.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
   os.chmod(tmp,stat.S_IMODE(target.stat().st_mode));staged.append((tmp,target))
  applied=[]
  try:
   for tmp,target in staged:os.replace(tmp,target);applied.append(str(target))
   for name,b in plan['mapping'].items():need(Path(name).read_bytes()==b,'applied byte readback')
   result.update(status='B_HOST_DELTA_APPLIED_PRIVATE_ONLY',preimage_directory=str(d),applied_paths=applied)
  except BaseException as e:
   result.update(status='PARTIAL_PRIVATE_APPLY_REQUIRES_MAIN_PREIMAGE_RECOVERY',preimage_directory=str(d),applied_paths=applied,error=str(e));(d/'APPLY_RECEIPT.json').write_bytes(encoded(result));raise
  (d/'APPLY_RECEIPT.json').write_bytes(encoded(result));return result
if __name__=='__main__':
 try:print(json.dumps(main(),sort_keys=True))
 except Exception as e:
  print(json.dumps(dict(status='HOLD',reason=str(e),automatic_retry=False,budget_writes=0,shared_native_writes=0,models_started=0)));raise SystemExit(2)
