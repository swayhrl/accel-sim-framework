# Pure/default-real-reference binder. Writes only candidate output directory.
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,math,os
P=Path(__file__).resolve().parent;V=P.parents[1]
R=P/'qualified_runtime';J=V.parents[1]
Q=V/'main/new_source_qualification';M=V/'activation_20261104_v1/main_qualification'
DATA=J/'execution_cc_cam_highclock_20261104_v1/highclock'
def ref(p):p=Path(p);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def exact(r):assert ref(r['path'])['sha256']==r['sha256'],r;return json.loads(Path(r['path']).read_text())
def defaults():
 proposal=json.loads((V/'main/authorization_packages/HIGH_CLOCK_REPAIRED_SOURCE_QUALIFICATION_AND_PERFORMANCE_V1.json').read_text());native=json.loads((P/'native_install_candidate/NATIVE_INSTALL_PLAN.json').read_text())
 return dict(source_qualification_ref=ref(Q/'SOURCE_CPU_BUILD_QUALIFICATION.json'),mode_cpu_qualification_ref=ref(Q/'S_F_MODE_CPU_QUALIFICATION.json'),ro_qualification_ref=ref(Q/'VECTOR_NEW_SOURCE_RO_QUALIFICATION.json'),eligibility_ref=ref(M/'VECTOR_REPAIRED_SOURCE_INPUT_ELIGIBILITY.json'),host_qualification_ref=ref(M/'HIGHCLOCK_DERIVED_HOST_QUALIFICATION.json'),resource_module_ref=proposal['resource_adapter_ref'],resource_policy_ref=proposal['resource_policy_ref'],authorization_ref=ref(DATA/'control/USER_AUTHORIZATION.json'),native_entry_ref=native['entry_ref'],native_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),native_mount_namespace=os.readlink('/proc/self/ns/mnt'))
def bind_all(bindings=None,output_dir=None):
 b=defaults();b.update(bindings or {})
 for k in ['source_qualification_ref','mode_cpu_qualification_ref','ro_qualification_ref','eligibility_ref','host_qualification_ref','authorization_ref','resource_policy_ref']:exact(b[k])
 assert ref(b['resource_module_ref']['path'])['sha256']==b['resource_module_ref']['sha256']
 sp=importlib.util.spec_from_file_location('activation_exact_binder',P/'bind_highclock_specs.py');binder=importlib.util.module_from_spec(sp);sp.loader.exec_module(binder)
 sp=importlib.util.spec_from_file_location('activation_exact_mode_contract',R/'mode_contract.py');contract=importlib.util.module_from_spec(sp);sp.loader.exec_module(contract)
 result=[]
 for f in sorted((P/'drafts').glob('*.json')):
  original=json.loads(f.read_text());s=binder.bind(original,b)
  # Runtime admission predictions use measured processRSS; hard limits retained.
  parent=contract.exact(s['configuration_template_spec_ref']);done=Path('/root/data/ep_l2_dtc_l1_native_v2/control/qualification_ledger')/(parent['cohort']+'.DONE.json');d=json.loads(done.read_text());peak=d['peak_process_tree_RSS_bytes'];s['estimated_peak_RAM_bytes']=math.ceil(peak*1.1)+(16<<20);s['RAM_prediction_evidence']=dict(parent_done_ref=ref(done),parent_source_identity=d['source_identity'],measured_peak_RSS=peak,prediction_formula='ceil(observedRSS*1.10)+16MiB; new Source actualRSS still monitored, not asserted measured');s['limits']['result_bytes']=128<<20
  s['status']='MAIN_REAL_QUALIFICATIONS_BOUND_CANDIDATE_PENDING_NATIVE_REGISTRATION_PREPARE';s['old_application_acceptance_inherited']=False;s['scope_launches_authorized']=6;s['automatic_retry']=False;s['refund']=False
  contract.validate_static(s);assert s['expected_effective_options']==original['expected_effective_options']and s['ordered_configs']==original['ordered_configs'];result.append(s)
 by={s['cohort']:s for s in result}
 for s in result:
  if s['mode']=='S':contract.validate_fair_pair(s,by[s['same_background_peer_cohort']])
 if output_dir is not None:
  out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
  for s in result:(out/(s['cohort']+'.json')).write_text(json.dumps(s,indent=2,sort_keys=True)+'\n')
 return result,b
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bindings-json');p.add_argument('--output-dir',default=str(P/'spec_candidates'));a=p.parse_args();over=json.loads(Path(a.bindings_json).read_text())if a.bindings_json else{};ss,bindings=bind_all(over,a.output_dir)
 index=dict(schema='EP_ACTIVATION_B_REAL_MAIN_BOUND_SIX_SPEC_CANDIDATES_V1',status='PASS_REAL_MAIN_SOURCE_MODE_INPUT_RO_HOST_REFS_BOUND_NOT_REGISTERED_OR_NATIVE_PREPARED',bindings=bindings,specs=[dict(cohort=s['cohort'],ref=ref(Path(a.output_dir)/(s['cohort']+'.json')),mode=s['mode'],profile=s['profile'],Source=s['source_identity'],RAM_prediction_bytes=s['estimated_peak_RAM_bytes'])for s in ss],native_installed_by_this_script=False,registry_writes=0,starts=0)
 (P/'REAL_BOUND_SIX_SPEC_INDEX.json').write_text(json.dumps(index,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(status=index['status'],points=len(ss),index_ref=ref(P/'REAL_BOUND_SIX_SPEC_INDEX.json'))))
