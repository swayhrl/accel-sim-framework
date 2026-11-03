"""Read-only requirement audit. Writes reports only; never changes scientific evidence."""
from pathlib import Path
import json,hashlib,datetime,importlib.util,os,sys,gzip,traceback
sys.dont_write_bytecode=True
P=Path;R=P('/root/data/dtc_stage_iia_first16_20261104_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1');HERE=A/'root_completion_audit_v1';REQ='DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1';PASS='PASS_STAGEII_CH_STRICT_ARCHIVE_NATIVE_RESTORE';FAIL='FAIL_STAGEII_CH_ARCHIVED_NO_RETRY'
def rd(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def ref(p):return dict(path=str(p),sha256=sha(p))
def report():
 checks=[]
 def check(name,passed,evidence):checks.append(dict(requirement=name,status='PROVEN'if passed else'INCOMPLETE_OR_CONTRADICTED',evidence=evidence));return passed
 plan=rd(R/'control/EXECUTION_PLAN.json');reg=rd('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');q=reg['registered_future_requests'][REQ];matrix=rd(R/'control/MATRIX.json');expected={x['cohort']for x in matrix['points']};auth=rd(R/'control/SCIENCE_AUTHORIZATION.json')
 check('Fixed approved contract, exact8 frozen inputs and16 one-start CH-F128/F256 cohort identities',plan['approved_contract_commit']=='5001c3f35052f7f91f1ad41eeff83f2947a0878d'and len(expected)==16 and expected==set(q['admitted_specs'])==set(auth['budgets'])and set(auth['budgets'].values())=={1}and len({x['input_digest']for x in matrix['points']})==8 and all(x['cell']=='CH'and x['profile']in['F128','F256']for x in matrix['points']),[ref(R/'control/EXECUTION_PLAN.json'),ref(R/'control/MATRIX.json'),ref(R/'control/SCIENCE_AUTHORIZATION.json')])
 check('Finite budget accounting; consumed identities never refunded',q['budget']==16 and q['remaining']==16-len(q['consumed']),dict(budget=q['budget'],consumed=len(q['consumed']),remaining=q['remaining']))
 pins=[dict(path=x['path'],expected=x['sha256'],observed=sha(x['path']))for x in plan['source_pins']];check('All62 frozen runtime/build/input/config source pins still match',len(pins)==62 and all(x['expected']==x['observed']for x in pins),pins)
 uid=[x['uuid']for x in q['consumed'].values()];other=[]
 for name,old in reg['registered_future_requests'].items():
  if name==REQ:continue
  if isinstance(old.get('consumed'),dict):other.extend(v['uuid']for v in old['consumed'].values()if isinstance(v,dict)and'uuid'in v)
 check('Every spent first16 UUID is independent and not reused from any other request',len(uid)==len(set(uid))and not(set(uid)&set(other)),dict(new_UUIDs=uid,other_recorded_UUIDs=len(other)))
 before=rd(R/'control/actual_owner_attach_v2/OLD_REQUEST_IDENTITIES_BEFORE.json');old_checks=[]
 for name,old in before.items():
  if not name.startswith('DTC_'):continue
  current=reg['registered_future_requests'][name];old_checks.append(dict(request=name,unchanged=old=={k:current.get(k)for k in ['budget','remaining','consumed']}))
 check('Historical DTC budgets, identities, DONE and consumed records unchanged',all(x['unchanged']for x in old_checks),old_checks)
 adapter_path=A/'agents/B_runtime_adapter_v1/actual_readonly_adapter.py';assert sha(adapter_path)=='c3310df8a4c8fb2d94ba57742339c3220367822c62128270810060d3967107a7';adapter=load('root_final_readonly_adapter',adapter_path);consumer,contract,base=adapter.frozen_inputs();consumer.verify_original_sources(base);current,_,context=adapter.registry_context();by={(x['input_digest'],x['design'],x['profile']):x for x in base['references']}
 check('All32 original phase-I reference sources verified; no IR/R2/EP/PQ/PS substitution',len(base['references'])==32,[ref(R/'control/ORIGINAL_REFERENCE_INDEX.json'),ref(adapter_path)])
 observations=[];errors=[]
 for e in contract['expected_CH']:
  try:observations.append(adapter.observation(e,by[e['input_digest'],'CH','P0'],context,current))
  except BaseException:errors.append(dict(cohort=e['cohort'],traceback=traceback.format_exc()))
 accepted=[x for x in observations if x['status']==PASS];negative=[x for x in observations if x['status']==FAIL];terminal=len(accepted)+len(negative)==16 and not errors
 check('All16 scientific identities independently strict/negative, true164 archive and full native recovery verified',terminal,dict(accepted=len(accepted),archived_negative=len(negative),waiting_or_hold=16-len(accepted)-len(negative),readonly_errors=errors,observations=observations))
 check('Natural completion or explicit preserved negative for all16, no unspent or missing outcomes',terminal and q['remaining']==0,dict(remaining=q['remaining'],expected=16,verified_terminal=len(accepted)+len(negative)))
 # Do not infer completed science from a status flag: all observations above
 # recompute stream/chunk/native-file witnesses through the pinned read-only adapter.
 provider=rd(A/'agents/B_runtime_analysis_v1/PUBLICATION_PROVIDER.json');provider_valid=sha(provider['manifest']['path'])==provider['manifest']['sha256']and all(sha(x['path'])==x['sha256']for x in provider['files']);summary_path=next(x['path']for x in provider['files']if x['name']=='STAGEIIA_FIRST16_SUMMARY.json.gz');summary=json.loads(gzip.decompress(P(summary_path).read_bytes()));check('Paired statistical tables report coverage, exact common F denominator and positive/negative/missing',terminal and provider_valid and summary['accepted_CH']==len(accepted)and summary['archived_negative_CH']==len(negative)and provider['all_registered16_terminal_verified']is True,dict(provider=ref(A/'agents/B_runtime_analysis_v1/PUBLICATION_PROVIDER.json'),summary=summary))
 check('No subsequent48 release or automatic combination execution',plan['remaining48_not_authorized']is True and plan['no_extensions']is True and provider['summary']['remaining48_locked']is True and set(q['admitted_specs'])==expected,dict(plan=ref(R/'control/EXECUTION_PLAN.json'),new_request_cohorts=sorted(q['admitted_specs'])))
 v=dict(schema='DTC_STAGEII_FIRST16_ROOT_COMPLETION_AUDIT_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),audit_source_sha256=sha(__file__),science_execution_complete=terminal and all(x['status']=='PROVEN'for x in checks),goal_complete=False,final_scientific_review_and_published_recommendation_required=True,checks=checks,new_model_starts=0,native_scientific_writes=0,missing_final_deliverables=['DTC-MAIN narrative interpretation with counter/causality limits.','Independent final scientific review of all16.','Evidence-based remaining48 recommendation, no release.','Final Git commit, all package member SHA and remote readback.'])
 tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out=HERE/'reports'/tag;out.mkdir(parents=True,exist_ok=False);p=out/'AUDIT.json';p.write_text(json.dumps(v,indent=2)+'\n');(HERE/'LATEST.json').write_text(json.dumps(dict(path=str(p),sha256=sha(p),UTC=v['UTC'],science_execution_complete=v['science_execution_complete'],goal_complete=False),indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),requirements=len(checks),proven=sum(x['status']=='PROVEN'for x in checks),accepted=len(accepted),archived_negative=len(negative),waiting_or_hold=16-len(accepted)-len(negative),science_execution_complete=v['science_execution_complete'],goal_complete=False)))
if __name__=='__main__':report()
