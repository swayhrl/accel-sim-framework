"""Main-only sealing helper: reads approved reviews; never mints authority or starts models."""
from pathlib import Path as P
import argparse,json,hashlib,sys
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');V=J/'research/performance_first_v3_20261104_v1';F=V/'activation_20261104_v1/agent_a_formal';R=V/'activation_20261104_v1/runtimes/midtag';DATA=J/'execution_midtag_v3_20261104_v1/midtag'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(P(p).read_text())
def put(p,d):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');return ref(p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode-review',required=True);ap.add_argument('--host-review',required=True);ap.add_argument('--resource-module',required=True);ap.add_argument('--resource-policy',required=True);ap.add_argument('--output-dir',default=str(F/'bound_specs'));args=ap.parse_args()
 mode=read(args.mode_review);host=read(args.host_review)
 assert mode['approved_by']==host['approved_by']=='EP-MAIN'
 assert mode['status']=='MAIN_REVIEWED_MIDTAG_MODE_CPU_PASS_NOT_APPLICATION'
 assert host['status']=='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED'
 assert mode['source_identity']==host['source_identity']
 source=mode['source_identity'];auth=read(DATA/'control/USER_AUTHORIZATION.json')
 assert auth['explicit_user_approval']and auth['approved_launches']==8 and auth['Source5']==source
 assert auth['user_request_ref']==ref(DATA/'control/USER_REQUEST.txt')
 assert not mode.get('fixture_only',False)and not host.get('fixture_only',False)
 sys.path.insert(0,str(R));import mode_contract as mc
 entry=dict(path=str(DATA.parent/'bin/native_midtag_v3'),sha256=sha(F/'native_midtag_v3'))
 needed=[R/n for n in ['ep_perf_common_v2.py','ep_perf_native_wv_modes_draft.py','mode_contract.py','mode_aware_terminal.py','ep_perf_postprocess.py','ep_perf_archive.py','ep_perf_frontend.py']]
 needed +=[V/'activation_20261104_v1/agent_d_execution/native_route_guard_v3.py',V/'activation_20261104_v1/agent_d_execution/safe_native_core_v3.py',P(args.resource_module)]
 needed +=[P(args.resource_module).with_name('resources_v3.py'),P(args.resource_policy)]
 for p in needed:assert ref(p)in host['modules'],('Main Host review missing final module',str(p))
 for r in host['modules']:assert sha(r['path'])==r['sha256']
 for r in [mode['protocol_ref'],mode['actual282_ref']]:assert sha(r['path'])==r['sha256']
 points=[];specs={}
 for p in sorted((F/'spec_candidates').glob('*.json')):
  s=read(p);base=read(V/'agent_a_mid_tag/spec_candidates'/p.name)
  assert s['source_identity']==base['source_identity']==source and s['expected_effective_options']==base['expected_effective_options']and s['input_identity_sha256']==base['input_identity_sha256']and s['observer_env']==base['observer_env']
  s.update(status='MAIN_BOUND_EXACT_ONE_START_SPEC_NOT_AUTHORITY_BY_ITSELF',Main_review_status='EP_MAIN_REVIEWED_ENGINEERING_NOT_APPLICATION',mode_cpu_qualification_ref=ref(args.mode_review),host_qualification_ref=ref(args.host_review),resource_module_ref=ref(args.resource_module),resource_policy_ref=ref(args.resource_policy),native_entry_ref=entry,Main_scientific_launch_authorization=ref(DATA/'control/USER_AUTHORIZATION.json'))
  for p2 in needed+[P(args.resource_policy)]:s['pinned_files'][str(p2)]=sha(p2)
  assert s['Main_scientific_launch_authorization']==ref(DATA/'control/USER_AUTHORIZATION.json')
  assert s['cohort']in auth['allowed_cohorts']and s['application_budget']==s['approved_launches']==1 and not s['M']and not s['T']and s['ro_qualification_ref']is None
  for field in ['ordered_configs']:
   for r in s[field]:assert sha(r['path'])==r['sha256']
  mc.validate_static(s)
  dest=P(args.output_dir)/(s['cohort']+'.json');r=put(dest,s);points.append(dict(cohort=s['cohort'],spec_ref=r,canonical_path=str(DATA/'cases'/s['cohort']/'control/FROZEN_SPEC.json'),estimated_peak_RAM_bytes=s['estimated_peak_RAM_bytes'],estimated_remaining_write_bytes=16<<20,priority=0 if'_FWT_'in s['cohort']else 1));specs[s['cohort']]=s
 for s in specs.values():
  if s['mode']=='S':mc.validate_fair_pair(s,specs[s['same_background_peer_cohort']])
 assert len(points)==8 and sorted(x['cohort']for x in points)==auth['allowed_cohorts']
 receipt=dict(status='MAIN_REVIEW_REFS_BOUND_STATIC_MODE_PAIR_PASS_NOT_REGISTERED_BY_THIS_HELPER',request_id=auth['goal'],source_identity=source,authorization_ref=ref(DATA/'control/USER_AUTHORIZATION.json'),mode_review_ref=ref(args.mode_review),host_review_ref=ref(args.host_review),resource_module_ref=ref(args.resource_module),resource_policy_ref=ref(args.resource_policy),entry_ref=entry,points=points,new_budget_written=False,shared_Native_written=False,model_starts=0)
 put(F/'BOUND_FINAL_SPEC_INDEX.json',receipt);print(json.dumps(dict(status=receipt['status'],index_ref=ref(F/'BOUND_FINAL_SPEC_INDEX.json'))))
if __name__=='__main__':main()

