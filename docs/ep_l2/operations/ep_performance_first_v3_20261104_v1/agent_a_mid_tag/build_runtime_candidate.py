from pathlib import Path as P
import json,hashlib,copy,re,py_compile
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');A=J/'research/performance_first_v3_20261104_v1/agent_a_mid_tag';R=A/'runtime_candidate';ROOT=J/'execution_midtag_v3_20261104_v1/midtag';REQ='EP_L2_MID_TAG_850MHZ_V1_20261104'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(P(p).read_text())
def put(p,d):P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');return ref(p)
scope=read(R/'FAMILY_SCOPE.json');modes={x['id']:x['mode']for x in scope['points']}
p=R/'mode_contract.py';p.write_text(p.read_text().replace("FAMILY_SCOPE_SHA='TO_BIND'","FAMILY_SCOPE_SHA="+repr(sha(R/'FAMILY_SCOPE.json'))))
p=R/'ep_perf_common_v2.py';t=p.read_text().replace("ROOT = P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_system850_v2_20261104_v1/system')","ROOT = P("+repr(str(ROOT))+")").replace("GOAL = 'EP_L2_SYSTEM_850MHZ_PARAMETER_FAMILY_V2_20261104_V1'","GOAL = "+repr(REQ));p.write_text(t)
p=R/'mode_aware_terminal.py';t=p.read_text().replace("'mode_contract.py': 'f1a338fd72e6d09b76d91a567cbc8ed9201e7e10c72e1f1c9f1224a125c6a549'","'mode_contract.py': "+repr(sha(R/'mode_contract.py')));p.write_text(t)
p=R/'ep_perf_native_wv_modes_draft.py';t=p.read_text();t=re.sub(r'^SCOPED_MODES = .*$', 'SCOPED_MODES = '+repr(modes),t,flags=re.M).replace('outside exact12 SYSTEM850 scope/mode','outside exact8 midTag scope/mode').replace('not an approved12 SYSTEM850 cohort','not an exact8 midTag cohort').replace("MODE_CONTRACT_SHA='f1a338fd72e6d09b76d91a567cbc8ed9201e7e10c72e1f1c9f1224a125c6a549'","MODE_CONTRACT_SHA="+repr(sha(R/'mode_contract.py'))).replace("NEW_VALIDATOR_SHA='5206098aa508043359b94eca7f52835c244c579ebaab64452021a844d13ce035'","NEW_VALIDATOR_SHA="+repr(sha(R/'mode_aware_terminal.py')))
a=t.index("    route=read(ROOT/'control/NATIVE_ENTRY_ROUTE_RECOVERY_20261104_V1.json')");b=t.index('    s = spec_for(case, require_release=False)',a)
t=t[:a]+'''    # No installed receipt => HOLD before spec consumption, resource claims or fork.
    route=read(ROOT/'control/NATIVE_ENTRY_ROUTE_V3.json')
    need(route['goal']==GOAL and route['status']=='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE','native route not Main installed')
    need(route.get('approved_by')=='EP-MAIN' and route.get('scientific_scope_activated')is True,'scope not activated')
    # Immutable exact shared Native pin. Any future route change HOLDs.
    need(ref(NATIVE/'bin/native')==route['global_shared_native_ref'],'global Native changed; exact route review required')
    entry=route['entry_ref'];registry,_=authority()
    need(registry['registered_future_requests'][GOAL]['native_entry_ref']==entry,'registered sole-entry mismatch')
    need(P(entry['path'])==ROOT.parent/'bin/native_midtag_v3' and sha(entry['path'])==entry['sha256'],'scoped entry mismatch')
    need(route.get('exact_cohorts')==sorted(ALLOWED_COHORTS),'Native cohort scope mismatch')
''' +t[b:];p.write_text(t)
p=R/'ep_perf_archive.py';t=p.read_text().replace('ep_l2_system850_v2_20261104_v1/system','ep_l2_midtag_v3_20261104_v1/midtag');p.write_text(t)
front='''import json,os,sys
from ep_perf_common_v2 import *
COHORTS=COHORTS_PLACEHOLDER
def main(args):
 need(os.environ.get('EP_FULL_PERF_NATIVE_ENTRY')=='1','sole entry required')
 need(len(args)==5 and args[0]=='experiment' and args[3:]==['--project','EP_L2'],'exact Native EP command')
 need(args[1]in['prepare','inspect','run-native','accept'],'operation')
 case=args[2];need(case in COHORTS,'outside exact8 midTag scope')
 registry,_=authority();q=registry['registered_future_requests'].get(GOAL);need(q is not None,'fresh Main request not registered')
 p=ROOT/'cases'/case/'control/FROZEN_SPEC.json';need(case in q['admitted_specs']and sha(p)==q['admitted_specs'][case],'spec not exactly registered')
 s=read(p);item=s['host_engine_ref'];need(P(item['path']).is_relative_to(P(__file__).resolve().parent)and sha(item['path'])==item['sha256'],'engine location/pin')
 if args[1]=='accept':return module(s['postprocess_module_ref'],'midtag_exact_postprocess').postprocess(case)
 return module(item,'midtag_exact_engine').main(args)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:])))
 except Exception as e:print(json.dumps(dict(status='HOLD',reason=str(e),automatic_retry=False)),file=sys.stderr);sys.exit(2)
'''.replace('COHORTS_PLACEHOLDER',repr(sorted(modes)))
(R/'ep_perf_frontend.py').write_text(front)
native=A/'native_midtag_v3.candidate';native.write_text("#!/usr/bin/env python3\nimport os,sys\nos.environ['EP_FULL_PERF_NATIVE_ENTRY']='1'\nos.execv('/usr/bin/python3',['/usr/bin/python3',"+repr(str(R/'ep_perf_frontend.py'))+"]+sys.argv[1:])\n");native.chmod(0o755)
modeq=put(A/'evidence/MODE_CPU_CANDIDATE_QUALIFICATION.json',dict(status='PASS_MIDTAG_CPU_ENGINEERING_NOT_APPLICATION',source_identity=scope['source_identity'],protocol_ref=ref(A/'evidence/PRODUCTION_CPU_AND_MS_NI.json'),actual282_ref=ref(A/'evidence/ACTUAL282_CPU_RECEIPT.json'),application_NI='NOT_MEASURED',B0_M0a_application_NI='NOT_PROVEN_HELD_ON'))
mods=[ref(R/n)for n in ['ep_perf_common_v2.py','ep_perf_native_wv_modes_draft.py','mode_contract.py','mode_aware_terminal.py','ep_perf_postprocess.py','ep_perf_archive.py','ep_perf_frontend.py']]
hostq=put(A/'evidence/HOST_CANDIDATE_QUALIFICATION.json',dict(schema='EP_PFV3_MIDTAG_HOST_CANDIDATE_V1',status='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',source_identity=scope['source_identity'],modules=mods,modes_qualified=['S','WV_ZERO_RO'],profiles_qualified=['PFV3_MIDTAG_G32W16','PFV3_MIDTAG_G64W8'],activation_permission=False,new_science_budget_registered=0))
for p in sorted((A/'spec_candidates').glob('*.json')):
 s=read(p);old=read(s['provenance_prior_spec_ref']['path']);s.update(schema='EP_FULL_PERF_EXACT_SPEC_V1',application_budget=1,application_budget_semantics='PROPOSED_ONE_START_CONTRACT_ONLY_NOT_REGISTERED_AUTHORITY',native_entry_ref=ref(native),host_common_ref=ref(R/'ep_perf_common_v2.py'),host_engine_ref=ref(R/'ep_perf_native_wv_modes_draft.py'),mode_contract_ref=ref(R/'mode_contract.py'),validation_module_ref=ref(R/'mode_aware_terminal.py'),postprocess_module_ref=ref(R/'ep_perf_postprocess.py'),archive_module_ref=ref(R/'ep_perf_archive.py'),host_qualification_ref=hostq,mode_cpu_qualification_ref=modeq,resource_module_ref=old['resource_module_ref'],resource_policy_ref=old['resource_policy_ref'],native_boot_id=old['native_boot_id'],native_mount_namespace=old['native_mount_namespace'],host_cpu=None)
 pins={k:v for k,v in old['pinned_files'].items()if '/env/lib/'in k or'/common-lib/'in k};pins.update({r['path']:r['sha256']for r in mods});s['pinned_files']=pins
 assert not any(k in s for k in ['approved_launches','Main_scientific_launch_authorization'])
 put(p,s)
for p in R.glob('*.py'):py_compile.compile(str(p),doraise=True)
scope_index=read(A/'MID_TAG_FAMILY_SCOPE.json')
for row in scope_index['points']:row['spec_ref']=ref(row['spec_ref']['path'])
put(A/'MID_TAG_FAMILY_SCOPE.json',scope_index)
print(json.dumps(dict(status='CANDIDATE_READY_FOR_DRY_HOSTQ_NOT_ACTIVATED',runtime_root=str(R),intended_execution_root=str(ROOT),request_id=REQ)))

