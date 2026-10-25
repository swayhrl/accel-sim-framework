"""Read-only evidence join; no model/authority/entry/signal operations."""
import argparse,ast,datetime,fcntl,hashlib,importlib.util,json,os,pathlib,types
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');O=F/'ops';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');R=F/'validation_lava_memory_v2';L=F/'validation_late_failure_v1';OLDROOT=F/'validation';C=O/'revision16/sweep_controller.py';SOURCE='32ebd671924d4e23eda7960c5957708e5a71f225ceb0887edcbe3249f25f65d3';PRIOR='e33951d0d53677681e422a4e28005327e0b33c4492a1eb7fc02121daa492e413';ORIG='DTC_AE_V100_FULL_SWEEP_20261025_V1';OLD='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1';LAVA='DTC_AE_LAVAMEM_REPAIR_20261026_V2';LATE='DTC_AE_LATE_FAILURE_REPAIR_20261026_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--evidence-manifest',type=P,required=True);a=ap.parse_args();manifest=read(a.evidence_manifest);pins={}
 def pin(p,h=None):
  p=P(p);assert p.is_file() and not str(p.resolve()).startswith('/root/share/mnt164/');actual=sha(p)
  if h:assert actual==h,str(p)
  pins[str(p)]=actual
 for row in manifest['frozen_files']:pin(row['path'],row['sha256'])
 assert sha(C)==SOURCE
 mainproof=read(O/'R16_CPU_DRIVER_RESULT_V1.json');assert mainproof['status']=='PASS' and mainproof['controller_sha256']==SOURCE and mainproof['check_count']==23 and len(mainproof['main_mock_scenarios'])==18 and mainproof['driver_sha256']==sha(O/'revision16/qualify_r16_main_cpu_v1.py')
 barrier=read(O/'ADMISSION_BARRIER_AND_R1_RECONCILIATION_CPU_QUALIFICATION_V1.json');assert barrier['status']=='PASS' and barrier['check_count']==28 and barrier['source_sha256']==sha(O/'reconcile_r1_admission_barrier_v1.py') and barrier['driver_sha256']==sha(O/'qualify_admission_barrier_cpu_v1.py')
 assert {'LAVA_DEEP_PRE_POPEN','LATE_DEEP_PRE_POPEN','FOUR_SCOPE_RESOURCES_AND_METADATA'}<=set(x['kind'] for x in manifest['CPU_proofs'])
 proofs=[]
 for row in manifest['CPU_proofs']:
  p=P(row['path']);pin(p,row['sha256']);proof=read(p);assert proof['status']==('PASS_FINAL_FROZEN_SOURCE_ACTUAL_RESOURCE_CPU' if row['kind']=='FOUR_SCOPE_RESOURCES_AND_METADATA' else 'PASS');proofs.append(dict(path=str(p),sha256=sha(p),check_count=proof.get('check_count')))
  for sp in proof.get('source_pins',[]):pin(sp['path'],sp['sha256'])
  for sp in proof.get('metadata_source_pins',[]):pin(sp['path'],sp['sha256'])
 roots={LAVA:R,LATE:L};budgets={LAVA:2,LATE:4};candidates={};plans={}
 for k,root in roots.items():
  info=manifest['scopes'][k];qp=root/'control/REGISTRY_REQUEST_CANDIDATE_V1.json';q=read(qp);planpath=P(info['plan_path']);plan=read(planpath);profilepath=P(info['profile_path']);profile=read(profilepath);request=root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json';authpath=root/'control/SCIENCE_AUTHORIZATION.json';auth=read(authpath)
  assert q['budget']==q['remaining']==budgets[k] and q['consumed']=={} and len(q['admitted_specs'])==budgets[k] and q['orchestrator_sha256']==SOURCE and q['execution_plan_sha256']==sha(planpath) and q['spec_request_sha256']==sha(request)
  assert q['reserved_write_bytes']==int((1.5 if k==LAVA else 3)*2**30)
  assert plan['parent_controller_sha256']==profile['parent_controller_sha256']==SOURCE and plan['build_profile_sha256']==sha(profilepath)
  assert profile['max_process_tree_rss_bytes']==(128 if k==LAVA else 16)*2**30 and profile['estimated_peak_model_RAM_bytes']==(96 if k==LAVA else 4)*2**30
  assert auth['explicit_user_approval'] and auth['approval_request_sha256']==sha(request) and set(auth['budgets'])==set(q['admitted_specs']) and set(auth['budgets'].values())=={1}
  for p in [qp,planpath,profilepath,request,authpath]:pin(p)
  for row in plan['source_pins']:pin(row['path'],row['sha256'])
  for cell,h in q['admitted_specs'].items():
   assert cell.startswith('E2-AEREPAIR-LAVAMEM2-' if k==LAVA else 'E2-AEREPAIR-LATE4-');sp=root/'control/specs'/(cell+'.json');alias=root/'control'/(cell+'_SPEC.json');pin(sp,h);pin(alias,h);s=read(sp);assert s['limits']['max_process_tree_rss_bytes']==(128 if k==LAVA else 16)*2**30
  assert not list((root/'control/qualification_ledger').glob('*.INTENT.json'));candidates[k]=q;plans[k]=plan
 # Current authority identity only, never a pin for a mutable registry body.
 with(N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb') as f:
  fcntl.flock(f,fcntl.LOCK_SH);reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');epoch=read(N/'control/CURRENT_SCIENCE_EPOCH.json');assert sha(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')==epoch['native_registry_sha256'];oldq=reg['registered_future_requests'][OLD];origq=reg['registered_future_requests'][ORIG];assert all(k not in reg['registered_future_requests'] for k in roots) and len(oldq['consumed'])==23 and oldq['remaining']==0 and oldq['orchestrator_sha256']==origq['orchestrator_sha256']==PRIOR
 appliedpath=O/'BARRIER_RECONCILIATION_PUBLISHED_APPLY_RECEIPT_V1.json';applied=read(appliedpath);assert applied['status']=='APPLIED_OPERATIONAL_METADATA_ONLY' and applied['tool_sha256']==sha(O/'reconcile_r1_admission_barrier_v1.py') and applied['scientific_models_started']==applied['signals']==0
 assert origq['operational_repair_admission_barrier']['status']=='NEW_ORIGINAL_ADMISSION_PAUSED_FOR_QUALIFIED_REPAIR_SUPPLEMENT' and hashlib.sha256(json.dumps(origq['operational_repair_admission_barrier'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==applied['barrier_sha256'];pin(appliedpath);pin(applied['fresh_plan'],applied['plan_sha256'])
 assert sha(OLDROOT/'control/EXECUTION_PLAN_V1.json')==oldq['execution_plan_sha256'];oldpool=read(OLDROOT/'control/EXECUTION_PLAN_V1.json')['allowed_model_CPUs'];origpool=read(T/'control/HOST_EXECUTION_PLAN_V4.json')['model_CPUs'];pools={ORIG:origpool,OLD:oldpool,**{k:p['allowed_model_CPUs'] for k,p in plans.items()}}
 def physical(c):
  path=P('/sys/devices/system/cpu')/('cpu'+str(c))/'topology';return ((path/'physical_package_id').read_text().strip(),(path/'core_id').read_text().strip())
 for k in roots:
  assert set(pools[k])<=os.sched_getaffinity(0)
  for other in pools:
   if other!=k:assert not set(pools[k])&set(pools[other]) and not {physical(c) for c in pools[k]}&{physical(c) for c in pools[other]}
 for p in [C,O/'revision16/qualify_r16_main_cpu_v1.py',O/'R16_CPU_DRIVER_RESULT_V1.json',O/'reconcile_r1_admission_barrier_v1.py',O/'qualify_admission_barrier_cpu_v1.py',O/'ADMISSION_BARRIER_AND_R1_RECONCILIATION_CPU_QUALIFICATION_V1.json',O/'OBSERVER_OLD_ATTEMPTS_FORENSIC_V1.json',F/'control/REPAIR_SOURCE_PUBLICATION_READBACK_V1.json',a.evidence_manifest,P(__file__),O/'revision16/assemble_r16_evidence_manifest_v1.py']:pin(p)
 for p in (F/'analysis/new_original_failures_20261026_v1').glob('*'):
  if p.is_file():pin(p)
 for name in ['MEMORY_REQUIREMENT_SUMMARY_V1.json','PHYSICAL_WARP_CAPACITY_BOUND_SUPPLEMENT_V1.json','HEADER_INDEX_READ_RESULT.json']:pin(F/'analysis/lavamd_memory_requirement_20261026_v1'/name)
 assert read(F/'control/REPAIR_SOURCE_PUBLICATION_READBACK_V1.json')['verified'] is True
 # Execute the two actual frontend functions. All workers/fallback calls mocked.
 front=load(L/'tools/late_frontend_v1.py','r16_late_route_cpu');lavafront=load(R/'tools/lavamem_frontend_v2.py','r16_lava_route_cpu');calls=[]
 def engine(tag):return types.SimpleNamespace(prepare=lambda c:(tag,'prepare',c),run_native=lambda c:(tag,'run',c))
 le=engine('late');ve=engine('lava');fallback=types.SimpleNamespace(main=lambda argv:('old-fallback',argv));lo=types.SimpleNamespace(archive=lambda c:('late','archive',c));vo=types.SimpleNamespace(archive=lambda c:('lava','archive',c))
 front.load=lambda name,path:le if P(path).name=='late_native_v1.py' else lo if P(path).name=='late_outbox_v1.py' else lavafront
 lavafront.load=lambda name,path:ve if P(path).name=='lavamem_native_v2.py' else vo if P(path).name=='lavamem_outbox_v2.py' else fallback
 for k,tag in [(LATE,'late'),(LAVA,'lava')]:
  c=next(iter(candidates[k]['admitted_specs']))
  for args,op in [(['experiment','prepare',c,'--project','DTC_L1'],'prepare'),(['experiment','run-native',c,'--project','DTC_L1'],'run'),(['result','archive',c],'archive')]:assert front.main(args)[:2]==(tag,op)
 for cell in ['E2-AEREPAIR-ddb6806316876a85-CM-V1','E2-AEV100-example-CM']:assert front.main(['experiment','run-native',cell,'--project','DTC_L1'])[0]=='old-fallback'
 entry=N/'bin/native';before=entry.read_bytes();oldroute=str(OLDROOT/'tools/repair_frontend_v1.py').encode();newroute=str(L/'tools/late_frontend_v1.py').encode();assert before.count(oldroute)==1;after=before.replace(oldroute,newroute)
 issues=['E2-AEV100-85700545918390d7-DM','E2-AEV100-e7c791ce2e4b09ee-DM'];assert {x['cohort'] for x in read(O/'OBSERVER_OLD_ATTEMPTS_FORENSIC_V1.json')['cases']}==set(issues)
 checks=list(mainproof['checks'])+['final independent barrier28 CPU and real-registry pure dry transformation PASS','two finite candidates exact budgets2+4 reserved1.5GiB+3GiB source32ebd joined to Profile Plan Request Auth specs aliases','all final deep native prePopen and four-scope resource metadata CPU proofs PASS','all transitive final plan and proof source pins verified current without payload scan','original R14 and old R1 orchestrators spent rows and scientific counts preserved; new scopes not registered','new CPU pools pairwise physically disjoint from original and old R1 actual allowed pools','actual late frontend dispatches late4 then lava2 and falls back oldR1/original correctly','prior native entry exact bytes permit one oldR1 router to combined router replacement','new4 per-point complete raw diagnosis and archive-qualified R1 reservation assessment retained','full header memory and2304 fixed warp proof retained;128AS not treated as physical reservation','Framework02775/Core9eed existing source publication verified without rebuild','no authority model signal entry history or scientific acceptance mutations']
 result=dict(schema='DTC_R16_INDEPENDENT_ZERO_MODEL_QUALIFICATION_V1',status='PASS',observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller_sha256=SOURCE,prior_controller_sha256=PRIOR,source_pins=[{'path':p,'sha256':h} for p,h in sorted(pins.items())],source_pin_count=len(pins),checks=checks,check_count=len(checks),main_CPU_checks=23,main_CPU_scenarios=mainproof['main_mock_scenarios'],barrier_CPU_checks=28,CPU_proofs=proofs,reviewed_original_engineering_issues=issues,prior_entry_sha256=hashlib.sha256(before).hexdigest(),expected_entry_after_exact_route_change_sha256=hashlib.sha256(after).hexdigest(),new_requests={k:{'budget':budgets[k],'reserved_write_bytes':q['reserved_write_bytes']} for k,q in candidates.items()},original_model_slots_max=40,new_lava_slots_max=2,new_late_slots_max=4,lava_serial_write_admission='1GiB metadata + <=512MiB single candidate; second live or DONE-unarchived blocks by per-scope1.5GiB ceiling even with abundant RAM.',source_contract_limit=mainproof['closure_contract_limit'],old_R1_close_consumer='Independent V2 consumer closes existing23; parent never rewrites old spent rows/source/orchestrator.',scientific_simulator_starts=0,real_authority_mutations=0,real_entry_changes=0,real_process_signals=0,historical_receipts_fabricated=0,not_scientific_result_acceptance=True,no_trace_or_archive_payload_reread=True)
 out=O/'R16_ZERO_MODEL_QUALIFICATION_V1.json'
 with out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(dict(status='PASS',qualification=str(out),sha256=sha(out),pins=len(pins),checks=len(checks),controller_sha256=SOURCE,prior_entry_sha256=result['prior_entry_sha256'],expected_entry_after_sha256=result['expected_entry_after_exact_route_change_sha256'])))
if __name__=='__main__':main()
