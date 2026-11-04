#!/usr/bin/env python3
"""Pure cap10 resource-only migration binder; Main installs under its locks. No model/native/ledger writes."""
import pathlib,json,hashlib,copy,argparse
P=pathlib.Path(__file__).resolve().parent
REG=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
RECOVERY=P.parents[1]
GROUPS=json.loads((RECOVERY/'agent_b_native/RECOVERY_GROUPS.json').read_text())['groups']
ALLOWED=frozenset(['resource_module_ref','resource_policy_ref','pinned_files'])
def read(p):return json.loads(pathlib.Path(p).read_text())
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(pathlib.Path(p).resolve()),sha256=sha(p))
def exact(r):
 assert isinstance(r,dict)and sha(r['path'])==r['sha256'],'immutable ref drift';return read(r['path'])
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def compute(registry,bindings,spec_reader):
 assert set(bindings['module_refs']) in ({'system','highclock'},{'system','highclock','shared'}),'only both exact resource wrappers and optional shared dependency allowed'
 assert bindings['scope']['global_EP_model_limit']==10 and bindings['scope']['scientific_budget_changed']is False,'exact cap10 Host contract required'
 for r in bindings['module_refs'].values():assert sha(r['path'])==r['sha256'],'resource module drift'
 exact(bindings['policy_ref'])
 if bindings.get('resource_review_ref'):
  review=exact(bindings['resource_review_ref']);assert review['global_EP_model_limit']==10 and review['module_refs']==bindings['module_refs']and review['policy_ref']==bindings['policy_ref'],'resource review scope/module drift'
 extras=bindings.get('additional_pinned_refs',[])
 for r in extras:assert sha(r['path'])==r['sha256'],'shared dependency drift'
 changes=[];protected=[];budgets={}
 for tag,g in GROUPS.items():
  q=registry['registered_future_requests'][g['goal']]
  assert q['budget']==len(q['admitted_specs'])and q['remaining']==q['budget']-len(q['consumed']),'budget arithmetic'
  assert set(q['admitted_specs'])==set(g['original_admitted_specs']),'exact approved cohort scope'
  budgets[g['goal']]=dict(budget=q['budget'],remaining=q['remaining'],consumed=copy.deepcopy(q['consumed']),native_entry_ref=q['native_entry_ref'],runtime_versions=q['runtime_versions'])
  for case,digest in q['admitted_specs'].items():
   original_ref,a=spec_reader(tag,g,case);assert original_ref['sha256']==digest,'registered current spec drift'
   if case in q['consumed']:
    protected.append(dict(group=tag,cohort=case,state=q['consumed'][case].get('state'),original_spec_ref=original_ref));continue
   b=copy.deepcopy(a);b['resource_module_ref']=bindings['module_refs'][tag];b['resource_policy_ref']=bindings['policy_ref']
   for r in [b['resource_module_ref'],b['resource_policy_ref']]+extras:b['pinned_files'][r['path']]=r['sha256']
   for r in bindings['module_refs'].values():b['pinned_files'][r['path']]=r['sha256']
   delta=[k for k in a if a[k]!=b[k]]
   assert set(a)==set(b)and set(delta)<=ALLOWED,'non-resource spec delta forbidden'
   changes.append(dict(group=tag,request_id=g['goal'],cohort=case,original_spec_ref=original_ref,changed_fields=delta,candidate=b))
 return changes,protected,budgets

def bind(bindings,out):
 out=pathlib.Path(out).resolve();assert out.is_relative_to(P),'private candidate directory only'
 before=ref(REG);registry=read(REG)
 def spec_reader(tag,g,case):
  f=pathlib.Path(g['data_ROOT'])/'cases'/case/'control/FROZEN_SPEC.json';return ref(f),read(f)
 changes,protected,budgets=compute(registry,bindings,spec_reader);rows=[]
 for row in changes:
  b=row.pop('candidate');f=out/'specs'/row['cohort']/'FROZEN_SPEC.json';write(f,b);row['successor_spec_ref']=ref(f);rows.append(row)
 assert ref(REG)==before,'registry advanced while binding; candidates not usable; rerun read-only binder'
 index=dict(schema='EP_MAIN_CAP10_RESOURCE_ONLY_DYNAMIC_SPEC_MIGRATION_V1',status='CANDIDATE_MAIN_ONLY_INSTALL',registry_snapshot_ref=before,rows=rows,protected_consumed=protected,request_snapshots=budgets,resource_bindings=bindings,allowed_changed_fields=sorted(ALLOWED),global_EP_model_limit=10,science_budget_changed=False,runtime_or_native_changed=False,scientific_starts=0,registry_writes=0)
 write(out/'SPEC_INDEX.json',index);return index

def verify(index):
 assert ref(REG)==index['registry_snapshot_ref'],'registry advanced: rebind before install'
 registry=read(REG)
 if index['resource_bindings'].get('resource_review_ref'):exact(index['resource_bindings']['resource_review_ref'])
 for row in index['rows']:
  q=registry['registered_future_requests'][row['request_id']]
  assert row['cohort']not in q['consumed'],'now consumed; never change running/accepted spec'
  a=exact(row['original_spec_ref']);b=exact(row['successor_spec_ref']);assert q['admitted_specs'][row['cohort']]==row['original_spec_ref']['sha256']
  assert set(a)==set(b)and set(k for k in a if a[k]!=b[k])<=ALLOWED
 for row in index['protected_consumed']:exact(row['original_spec_ref'])
 return dict(status='CURRENT_UNCONSUMED_ONLY_RESOURCE_DELTA_PASS',count=len(index['rows']),writes=0)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bindings');p.add_argument('--out');p.add_argument('--verify-index');a=p.parse_args()
 if a.verify_index:print(json.dumps(verify(read(a.verify_index))))
 else:
  assert a.bindings and a.out;x=bind(read(a.bindings),a.out);print(json.dumps(dict(status=x['status'],count=len(x['rows']),index_ref=ref(pathlib.Path(a.out)/'SPEC_INDEX.json'))))
