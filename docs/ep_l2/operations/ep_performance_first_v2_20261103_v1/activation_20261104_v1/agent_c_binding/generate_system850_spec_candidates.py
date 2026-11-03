"""Final pure SYSTEM850 binding API; writes candidate files only under agentC."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,os,sys
A=Path(__file__).resolve().parent;R=A/'qualified_runtime';V=A.parents[1];J=V.parents[1]
sys.path.insert(0,str(R));sys.path.insert(0,str(A))
import mode_contract as mc
from bind_system850_specs import bind
Q=V/'activation_20261104_v1/main_qualification';OLDQ=V/'main/qualification_review'
def ref(p):p=Path(p);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def defaults():
 return dict(host_qualification_ref=ref(Q/'SYSTEM850_DERIVED_HOST_QUALIFICATION.json'),
             source_qualification_ref=ref(Q/'SYSTEM850_SOURCE_QUALIFICATION.json'),
             mode_cpu_qualification_ref=ref(OLDQ/'SYSTEM850_MODE_CPU_QUALIFICATION.json'),
             resource_module_ref=ref(V/'agent_d/resources_v2_candidate/resources_system.py'),
             resource_policy_ref=ref(OLDQ/'RESOURCE_POLICY_NUMERIC.json'),
             authorization_ref=ref(J/'execution_system850_v2_20261104_v1/system/control/USER_FAMILY_AUTHORIZATION.json'),
             native_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
             native_mount_namespace=os.readlink('/proc/self/ns/mnt'))
def bind_all(bindings=None):
 common=defaults();common.update(copy.deepcopy(bindings or {}));result={}
 auth=mc.exact(common['authorization_ref']);mc.need(auth['goal']==mc.SYSTEM_REQUEST_ID and auth['budget']==12 and auth.get('automatic_retry')is False and auth.get('refund')is False,'fresh exact12 userauthority contract')
 src=mc.exact(common['source_qualification_ref']);mc.need(src['status']=='EXACT_ACCEPTED_SOURCE_CPU_EVIDENCE_REUSED_NOT_NEW_APP_ACCEPTED'and src.get('approved_by')=='EP-MAIN','Main real Source wrapper required')
 for row in mc.family_scope()['points']:
  b=dict(common)
  b['eligibility_ref']=ref(Q/(row['program']+'_'+row['mode']+'_INPUT_ELIGIBILITY.json'))
  b['absolute_REF850_S_anchor_qualification_ref']=ref(OLDQ/(row['program']+'_S_ABSOLUTE850_ANCHOR_REVIEW.json'))
  b['absolute_REF850_EP_anchor_qualification_ref']=ref(OLDQ/(row['program']+'_WV_ZERO_RO_ABSOLUTE850_ANCHOR_REVIEW.json'))
  e=mc.exact(b['eligibility_ref']);mc.need(e.get('approved_by')=='EP-MAIN'and e['status']=='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE'and row['mode']in e['modes_qualified'],'Main real inputeligibility required')
  draft=mc.exact(row['candidate_spec_ref']);s=bind(draft,b);mc.validate_static(s)
  mc.need(s['source_identity']==src['source_identity']==auth['source_identity'],'Source qualification/authorization/spec mismatch')
  mc.need(e['ordered_kernel_identity']==mc.exact(s['input_binding_ref'])['ordered_kernel_identity'],'Main eligibility orderedkernel equality')
  result[s['cohort']]=s
 for s in result.values():
  if s['mode']=='S':mc.validate_fair_pair(s,result[s['same_background_peer_cohort']])
 return result
def write_candidates(bindings=None,output=None):
 target=Path(output)if output else A/'formal_spec_candidates'
 mc.need(target.resolve().is_relative_to(A.resolve()),'agent binder cannot install official runtime/native/registry directories')
 target.mkdir(parents=True,exist_ok=True);out=[]
 for case,s in bind_all(bindings).items():
  p=target/(case+'.json');p.write_text(json.dumps(s,sort_keys=True,indent=2)+'\n');out.append(ref(p))
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bindings');p.add_argument('--output');a=p.parse_args();b=json.loads(Path(a.bindings).read_text())if a.bindings else{}
 print(json.dumps(dict(schema='EP_SYSTEM850_FORMAL_SPEC_CANDIDATE_BINDING_V1',status='PASS_MAIN_SIGNED_FACTS_AND_STATIC12_NOT_NATIVE_INSTALL_OR_SCIENTIFIC_START',specs=write_candidates(b,a.output),models=0,registry_writes=0,native_installations=0)))
