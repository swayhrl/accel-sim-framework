"""Read-only source/history/qualification audit following the full four-cell join."""
import pathlib,json,hashlib,subprocess,csv,datetime
from fractions import Fraction
T=pathlib.Path('/root/data/dtc_main_20261023_v1/ae_fair_v1');N=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2');F=pathlib.Path('/root/data/dtc_main_20261023_v1/accel-sim-framework');P=F/'docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_EPOCH2_20261023_V1';O=F/'docs/dtc_l1/review_packs/DTC_MAIN_NATIVE_ONBOARDING_20261023_V1'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
original_files=[]
for row in csv.DictReader((O/'FILES_SHA256.tsv').read_text().splitlines(),delimiter='\t'):
 p=O/row['path'];assert p.resolve().is_relative_to(O.resolve()) and sha(p)==row['sha256'],row['path'];original_files.append(row['path'])
preimages=read(O/'live/CONTROL_PREIMAGE_SHA256.json');assert len(preimages)==77
allowed={str(N/'control/CURRENT_SCIENCE_EPOCH.json'),str(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'),str(N/'bin/native')};changes=[];unchanged=[]
for name,pre in preimages.items():
 p=pathlib.Path(name);current=sha(p) if p.exists() else None
 if current==pre['sha256']:unchanged.append(name)
 else:
  assert name in allowed,'unexpected historical control mutation:'+name
  changes.append({'path':name,'preimage_sha256':pre['sha256'],'current_sha256':current,'scope':'Versioned current epoch/authority/entry update; historical scientific rows separately verified unchanged.'})
for name in ['aefair_controller.py','aefair_install.py','aefair_native.py','aefair_result.py','aefair_strict.py']:assert sha(T/'tools'/name)==sha(P/'tools'/name),name
front=T/'tools/native_epoch2_frontend.py';old=P/'tools/native_epoch2_frontend.py';assert old.read_text().count("T/'tools/aefair_result.py'")==1
assert old.read_text().replace("T/'tools/aefair_result.py'","T/'tools/aefair_result_gate_v2.py'")==front.read_text()
assert sha(front)==sha(P/'amendments/outbox_revision2/native_epoch2_frontend.py')
assert sha(T/'tools/aefair_result_gate_v2.py')==sha(P/'amendments/outbox_revision2/aefair_result_gate_v2.py')
registered_wrapper=read(T/'control/NATIVE_REQUEST_INSTALL_RECEIPT.json')['native_entry_sha256'];wrapper=(N/'bin/native').read_text();scientific_delegate='exec /usr/bin/python3 -B /root/data/dtc_main_20261023_v1/ae_fair_v1/tools/native_epoch2_frontend.py "$@"'
expected_wrapper='''#!/bin/sh
set -eu
# COPY_ONLY asset queries only; scientific argv delegate remains unchanged.
if [ "$#" -ge 2 ]; then
  case "$1:$2" in
    asset:ensure|project:assets)
      exec /usr/bin/python3 -B /root/data/ep_dtc_trace_migration_20261024_v1/tools/trace_assets.py "$@"
      ;;
  esac
fi
'''+scientific_delegate+'\n'
assert wrapper==expected_wrapper and wrapper.splitlines()[-1]==scientific_delegate,'scientific delegate compatibility requires review'
wrapper_scope={'registered_wrapper_sha256':registered_wrapper,'current_wrapper_sha256':sha(N/'bin/native'),'observed_change':'COPY_ONLY asset:ensure/project:assets query branch added by shared asset routing','scientific_experiment_and_result_delegate_exactly_preserved':scientific_delegate,'four_scientific_operations_do_not_match_asset_query_case':True,'whole_wrapper_unchanged_claim':False}
corechanges=git(T/'core','diff','--name-only','c8090115bd57512b1b23fca7d925301fa620c751','HEAD').splitlines()
assert set(corechanges)=={'CMakeLists.txt','src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-cache.h','tests/dtc_l1_aefair_cache_hash_test.cc'}
assert not git(T/'core','diff','c8090115bd57512b1b23fca7d925301fa620c751','HEAD','--','src/gpgpu-sim/dtc-l1-tag-index.h')
frameworkchanges=git(T/'framework','diff','--name-only','8e43c75a5e2eb60a8466084602b7df8117111e89','HEAD').splitlines();assert set(frameworkchanges)=={'gpu-simulator/accel-sim.cc','gpu-simulator/ag7_policyb_progress.h'}
observer=[]
for name in ['accel-sim.cc','ag7_policyb_progress.h']:
 candidates=[N/'DTC/src/producer-overlay'/name,N/'DTC/src/producer-overlay/gpu-simulator'/name];source=next(p for p in candidates if p.exists());assert sha(source)==sha(T/'framework/gpu-simulator'/name);observer.append({'file':name,'accepted_overlay_source':str(source),'sha256':sha(source)})
for name,head in [('core','c8090115bd57512b1b23fca7d925301fa620c751'),('framework','8e43c75a5e2eb60a8466084602b7df8117111e89')]:
 assert git(N/'DTC/src'/name,'rev-parse','HEAD')==head and not git(N/'DTC/src'/name,'status','--porcelain')
build=read(P/'BUILD_AND_TARGETED_CPU_QUALIFICATION.json');assert build['status']=='NEW_CORE_AND_FRAMEWORK_BUILD_TARGETED_CPU_PASS' and build['linear_frozen_current_stdout_exact'] and build['new_full_simulator_starts']==0
assert 'observations=1048576 moved=917504 separated=32 negative_assertions=4 PASS' in build['hash_test_stdout']
assert sha(T/'DTC/bin/accel-sim.out')==build['framework_binary']['sha256'] and sha(T/'DTC/env/lib/libcudart.so')==build['core_library']['sha256']
entry=read(P/'ENTRY_CPU_QUALIFICATION.json');assert entry['status']=='PASS_TARGETED_CPU_ENTRY_AND_IDENTITY_ONLY' and entry['native_full_simulator_starts']==0
cpu=read(P/'amendments/revision2/CPU_QUALIFICATION.json');assert cpu['status']=='PASS_UNUSED_BASELINE_MODE_CPU_QUALIFICATION_ONLY' and all(cpu[k]==0 for k in ['kernels','trace_body_members_read','model_cycle_calls','simulation_threads_started','full_simulator_starts'])
assert [r['returncode'] for r in cpu['cases']]==[0,0,1] and cpu['cases'][-1]['status']=='EXPECTED_EXACT_PRODUCTION_REJECTION'
assert sha(T/'prepared_revision2/aefair_base_constructor_probe.cc')==cpu['probe_source_sha256'] and sha(T/'prepared_revision2/aefair_base_constructor_probe')==cpu['probe_binary_sha256']
metacpu=read(P/'amendments/revision2/METADATA_CPU_QUALIFICATION.json');assert 'PASS' in metacpu['status']
gatecpu=read(P/'amendments/outbox_revision2/CPU_QUALIFICATION.json');assert gatecpu['status']=='PASS_POSTPROCESS_RESOURCE_METADATA_ONLY' and gatecpu['tests']==8 and gatecpu['returncode']==0 and gatecpu['model_starts']==0
consumer=read(P/'consumer/QUALIFICATION_SCOPE.json');assert consumer['observed_exit_code']==0 and sha(T/'aefair_analysis.py')==consumer['source_sha256'] and sha(T/'aefair_analysis_test.py')==consumer['test_source_sha256'] and len(consumer['positive_cases'])+len(consumer['expected_rejections'])==12
applied=read(T/'control/UNUSED_CPLUS_AMENDMENT_APPLIED.json');assert applied['starts_consumed_before']==applied['starts_consumed_after']==1 and applied['remaining_before']==applied['remaining_after']==3 and applied['extra_model_starts']==applied['refunds']==applied['Core_Framework_binary_changes']==0
for name in ['E2-AEFAIR-CM_SPEC.json','E2-AEFAIR-CH_SPEC.json','SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','SCIENCE_AUTHORIZATION.json']:assert sha(T/'control'/name)==sha(T/'prepared_revision2'/name)
route=read(T/'control/OUTBOX_GATE_REVISION2_APPLIED.json');assert route['original_outbox_unchanged'] and route['model_signals']==route['new_model_starts_by_this_operation']==route['science_registry_writes']==route['budget_or_refund_changes']==0
paper=read(O/'PAPER_IDENTITY.json');assert paper['last_user_confirmed_mother']=='English v0.23' and paper['user_reconfirmed_in_this_session'] and not paper['newer_mother_promoted'] and not paper['manuscript_edited']
docchanges=git(F,'diff','--name-only','87c5834de9a056b933e157b52c817cfc8cd6f091','HEAD').splitlines();prefix=str(P.relative_to(F))+'/'
assert all(n=='DTC_MAIN_ACTIVE_GOAL.md' or n.startswith(prefix) for n in docchanges),'inherited manuscript/evidence files changed'
rows={}
for cell in ['CM','CH','DM','DH']:
 i=read(T/'control/qualification_ledger'/('E2-AEFAIR-'+cell+'.INTENT.json'));rows[cell]=read(pathlib.Path(i['output'])/'AEFAIR_STRICT.json')
cross={k:{'CM':rows['CM']['effective_options'].get(k),'DM':rows['DM']['effective_options'].get(k)} for k in set(rows['CM']['effective_options'])|set(rows['DM']['effective_options']) if rows['CM']['effective_options'].get(k)!=rows['DM']['effective_options'].get(k)}
clock={k:v for k,v in rows['CM']['effective_options'].items() if 'clock' in k.lower() or 'freq' in k.lower()};assert clock and all(rows['DM']['effective_options'].get(k)==v for k,v in clock.items())
result=read(T/'analysis/COMPLETE_RESULT.json');assert Fraction(rows['DM']['cycles']*rows['CH']['cycles'],rows['DH']['cycles']*rows['CM']['cycles'])==Fraction(result['interaction_R']['exact'])
audit={'schema':'DTC_AEFAIR_SOURCE_HISTORY_CONTRACT_AUDIT_V1','status':'PASS_SOURCE_HISTORY_AND_BOUNDED_CLAIM_REQUIREMENTS','immutable_onboarding_package_files_sha_checked':len(original_files),'historical_control_preimages':77,'historical_controls_unchanged':len(unchanged),'versioned_current_authority_updates':changes,'historical_scientific_control_changes':0,'original_qualified_source_worktrees_unchanged':True,'original44_status_counts':read(O/'VALIDATION.json')['original44_status_counts'],'paper_identity_and_unresolved_scope':paper,'inherited_tracked_document_changes_outside_new_goal_pack':0,'goal_document_changes_checked':len(docchanges),'frozen_execution_tool_sources_match_published_release':True,'sole_native_entry_scientific_delegate_scope':wrapper_scope,'sole_frontend_only_result_module_changed_after_frozen_release':True,'core_changed_files':corechanges,'AE_helper_unchanged_from_parent':True,'framework_changed_files':frameworkchanges,'framework_observer_matches_accepted_overlay':observer,'within_design_effective_option_changes':{'CM_CH':['-gpgpu_cache:dl1'],'DM_DH':['-gpgpu_dtc_l1_tag_hash_bankrow']},'cross_design_effective_option_differences':cross,'common_clock_configuration':clock,'predeclared_science_contract':read(P/'SCIENCE_CONTRACT.json'),'qualification_scope':{'hash_addresses':1048576,'cache_set_moves':917504,'separated_pairs':32,'expected_geometry_assertions':4,'legacy_linear_digest_equal':True,'entry_cpu_cases':len(entry['tests']),'real_constructor_cases':3,'metadata_revision_qualification':metacpu,'outbox_metadata_tests':8,'consumer_synthetic_cases':12,'consumer_whole_four_archive_restore_integration':'PASS_COMPLETE_RESULT_JSON','no_historical_suites_rerun':True,'qualification_gate_zero_bytes_scope':'Gate invocation payload only; qualification receipts themselves are metadata writes.'},'source_build':{'compiler':build['compiler'],'CUDA_header_version':build['CUDA_header_version'],'binary_sha256':build['framework_binary']['sha256'],'library_sha256':build['core_library']['sha256'],'historical_same_binary_claim':False},'independent_R_cross_product_exact':result['interaction_R'],'all_earlier_negative_HOLD_and_F_states_preserved':True,'scope_limits':['One deterministic discovery GEMM, one point per arm','Cplus32x24/PIB256/MSHR512 differs from DTC64x8/PIB128/physical640+ordinary16KiB','PAPER_BASE standard cache timing finite_service0 versus DTC finiteV1 flag1','No added modeled hash delay is an assumption; hardware timing/area not established','Native numerical correctness/coherence and PPA remain unproven','v0.23 actual package and line-by-line manuscript audit remain unavailable; no substitute mother promoted','No pooledGM, historical F or Hotspot admission-HOLD promotion'],'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (T/'analysis/SOURCE_HISTORY_CONTRACT_AUDIT.json').open('x') as f:json.dump(audit,f,indent=2);f.write('\n')
print(json.dumps({'status':audit['status'],'onboarding_files':len(original_files),'historical_unchanged':len(unchanged),'permitted_current_updates':changes,'cross_design_differences':cross,'common_clock':clock,'paper_identity':paper},indent=2))
