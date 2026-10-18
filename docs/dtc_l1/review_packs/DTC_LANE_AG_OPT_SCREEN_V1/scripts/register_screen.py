#!/usr/bin/env python3
"""Assemble immutable eight-slot executable preregistration; never launches."""
from common import *
from strict_screen import ordered,input_identity

def main():
 assert not list((RAW/'attempts').glob('*/RUN_START.json'))
 binding=json.loads((PACK/'RUNTIME_BINDINGS.json').read_text())
 assert binding['combined_core_commit']==git(CORE,'rev-parse','HEAD')
 assert not git(CORE,'status','--porcelain')
 assert git(CORE,'rev-parse','refs/ag-publication/core-final')==binding['combined_core_commit']
 requirements={
  'X2_REFERENCE_7_CTEST.json':'PASS_7_OF_7_ORIGINAL_X2',
  'X2_REFERENCE_NORMAL_EXPORT_CPU.json':'PASS_X2_REFERENCE_REAL_NORMAL_PRINT_CPU',
  'AE_AG_INDEPENDENT_CPU.json':'PASS_137_AG_OWNED_CPU_CASES',
  'AC_AG_INDEPENDENT_CPU.json':'PASS_CPU_REAL_LDST_PIPELINE_SCOPE_ONLY',
  'AC_AE_COMPOSITE_CPU.json':'PASS_ALL_FOUR_AC_AE_COMBINATIONS_68_CPU_PROCESSES',
  'AC_AE_PREVIEW_15_CTEST.json':'PASS_15_OF_15_INCLUDING_7_ORIGINAL_X2',
  'AC_AE_PREVIEW_NORMAL_EXPORT_CPU.json':'PASS_AG_PREVIEW_REAL_X2_NORMAL_PRINT_CPU',
  'LDST_AC_AE_PREVIEW_RESULT.json':'PASS_ACTUAL_LDST_OFF_EQUIVALENCE_AND_AE_K1_SAFETY',
  'OPTIONS_FINAL_RESULT.json':'PASS_ALL_OPTIONS_OFF_EQUALS_X2_AND_OLD_T_PUBLIC_CONFIG',
  'COMBINED_SOURCE_REVIEW.json':'PASS_EXACT_AC_AE_UNION_NO_MECHANISM_CONFLICT',
  'AC_PIPELINE_PUBLIC_JOIN_CPU.json':'PASS_REAL64SM_ON_FRAME_AND_THREE_JOIN_NEGATIVES',
  'RESOURCE_POLICY_CPU_TESTS.json':'PASS_PURE_CPU_AG_RESOURCE_POLICY',
  'RUNNER_CPU_GUARDS.json':'PASS_BOUNDED_CPU_WRAPPER_GUARDS',
  'STRICT_CPU_NEGATIVES.json':'PASS_FULL_CONTROL_POSITIVE_AND_CORRUPTION_NEGATIVES',
  'INPUT_FULL_IDENTITY.json':'PASS_FRESH_ALL_511_MEMBER_SHA256'}
 evidence=[]
 for name,status in requirements.items():
  obj=json.loads((PACK/name).read_text());assert obj['status']==status,(name,obj['status'])
  evidence.append(dict(path=name,status=status,sha256=sha(PACK/name)))
 assert json.loads((PACK/'RUNNER_CPU_GUARDS.json').read_text())['runner_sha256']==sha(PACK/'scripts/run_screen.py')
 assert json.loads((PACK/'STRICT_CPU_NEGATIVES.json').read_text())['strict_sha256']==sha(PACK/'scripts/strict_screen.py')
 qualification=dict(utc=now(),status='CPU_QUALIFIED_AC_AE_ONLY_NOT_FULL_APPLICATION_CORRECTNESS',
     combined_core=binding['combined_core_commit'],evidence=evidence,
     BASE='PASS_CPU_FULL_CALIBRATION_STILL_REQUIRED',AC='PASS_BOUNDED_CPU',AE='PASS_BOUNDED_CPU',
     AD='HOLD_UNQUALIFIED_PRODUCER_EXPLICIT_ON_ACCEPTANCE_STOP',AF='EXCLUDED_NO_FIFTH_ARM',
     frozen_producers=json.loads((PACK/'PUBLISHED_PRODUCER_CONSUMPTION.json').read_text())['rows'],
     multi_ON='68_CPU_CASES_ONLY_NEVER_PERFORMANCE',architectural_value_correctness='UNPROVEN',
     full_network_integration='TO_BE_SCREENED_BY_NEW_STRICT_FULL_INPUTS_NO_NATIVE_VALUE_CLAIM')
 write(PACK/'QUALIFICATION_DECISION.json',qualification)
 write(PACK/'QUOTAS_AND_BUFFER_CHARGES.json',dict(
     common=dict(Tag_banks=4,Tag_grants_per_bank_cycle=1,Tag_total_grants_cycle=4,
       allocation_width=4,create_per_absolute_cycle=1,inject_per_absolute_cycle=1,
       refill_per_absolute_cycle=1,waiter_notifications_per_cycle=4,collection_32B_sectors_per_cycle=4,
       retire_cacheable_or_sidecar_per_absolute_cycle=1,physical_lines=640,physical_line_bytes=128,
       PIB_entries=128,ordinary_L1_bytes=16384,shared_bytes=98304,lower_cap=32768,Ref_bits=13,
       clocks_MHz='1410:1410:1410:850',Tag_sets=64,Tag_ways=8),
     AC_ON=dict(collecting_owners=1,WB_result_owners=1,data_banks=2,bytes_per_bank=81920,
       additional_data_bytes_per_SM=163840,additional_data_bytes_64SM=10485760,
       no_free_PIB_payload=True,no_bulk_copy=True,extra_collection_ports=0,WB_strictly_after_collect_done=True),
     BASE_AE_AC_OFF_additional_result_data_bytes=0,AE='ONE_FIXED_BANK_PRESERVING_HASH_NO_PORT_CHANGE',
     AD='NOT_IN_BUILD_4_WAITER_CONTRACT_NOT_MODIFIED',AF='NOT_IN_BUILD',equal_area=False))
 options=json.loads((PACK/'OPTIONS_FINAL_RESULT.json').read_text())['expected']
 reserved=json.loads((PACK/'UUID_RESERVATIONS.json').read_text())
 assert len(reserved['rows'])==len({r['uuid'] for r in reserved['rows']})==8
 specs=[]
 for row in reserved['rows']:
  workload,arm=row['workload'],row['arm'];original=json.loads((PACK/f'inputs/T/inputs/{workload}_OO128_SPEC.json').read_text())
  point=arm+'_'+workload;body=ordered(workload)
  spec=dict(point=point,order=row['order'],cohort='DISCOVERY_OPT',attempt_uuid=row['uuid'],arm=arm,workload=workload,
      source_base=X2,compiled_framework=FRAMEWORK_BUILD,combined_core=binding['combined_core_commit'],
      qualification='HOLD_UNQUALIFIED' if arm=='AD' else 'PASS_BOUNDED_CPU',
      qualification_reason='Published AD ON acceptance STOP; no AG repair, no replacement or supplementary run' if arm=='AD' else 'See QUALIFICATION_DECISION.json',
      trace_list=original['trace_list'],trace_list_sha256=original['trace_list_sha256'],
      expected_kernels=len(body),expected_instructions=original['expected_instructions'],
      expected_CTA=sum(int(r['complete_ctas']) for r in body),
      expected_commands=(PACK/f'inputs/T/inputs/{workload}_kernelslist.g').read_text().splitlines(),
      processing_window='ALL_ORIGINAL_COMMANDS_ALL_CTA_ALL_KERNELS_NATURAL_EXIT0_NO_PREFIX_NO_WARMUP_SELECTION',
      member_SHA_table_sha256=sha(PACK/'ORIGINAL_MEMBERS_SHA256.tsv'),body_audit_sha256=sha(PACK/'inputs/T/inputs/KERNEL_BODY_AUDIT.tsv'),
      runtime_path=binding['runtime_path'],runtime_sha256=binding['runtime_sha256'],
      runtime_library_path=binding['runtime_library_path'],runtime_library_sha256=binding['runtime_library_sha256'],
      expected_embedded_core_version=binding['expected_embedded_core_version'],
      expected_embedded_framework_version=binding['expected_embedded_framework_version'],
      runtime_environment=binding['runtime_environment'],
      expected_full_effective_options='UNAVAILABLE_UNQUALIFIED_NO_EXECUTION' if arm=='AD' else options[workload+'_'+arm],
      planned_AD_flag='-gpgpu_dtc_l1_progressive_wakeup 1; NOT_COMPILED_NOT_EXECUTABLE' if arm=='AD' else 'NOT_APPLICABLE',
      configs=[],K_policy=0,timeout_seconds=7200,retries=0,failed_Popen_consumes_budget=True,
      max_new_sim_concurrency=1,resource_policy_version='AG_DISCOVERY_RESOURCE_R2_V1',
      BASE_calibration_reference_sha256=sha(PACK/f'controls/{workload}_CALIBRATION_REFERENCE.json'),
      ratios='ONLY_CURRENT_COHORT_SAME_INPUT_COMMON_BASE; OLD_T_ONLY_CALIBRATION; NO_GM12')
  if arm!='AD':
   for name in ['FAST64_OO.config','FINITE_PRIMARY_COMMON.config','trace.config',arm+'.config']:
    path=PACK/'config'/name;spec['configs'].append(dict(path=str(path),sha256=sha(path)))
   values=spec['expected_full_effective_options']
   assert sum(int(values[k][0]) for k in ['-gpgpu_dtc_l1_collect_wb_pipeline','-gpgpu_dtc_l1_tag_hash_bankrow'])==(0 if arm=='BASE' else 1)
   assert values['-gpgpu_dtc_l1_invalidate_on_source_event']==['0']
  input_identity(spec)
  path='specs/'+point+'.json';write(PACK/path,spec);specs.append(path)
 policy=json.loads((PACK/'SCIENTIFIC_POLICY.json').read_text())
 policy.update(registration_phase='COMPLETE_LOCAL_EXECUTABLE_REGISTRATION_REQUIRES_PUSH_FETCH_BACK_BEFORE_ANY_START',
     qualified_performance_arms=['BASE','AC','AE'],AD_slots='HOLD_UNQUALIFIED_NO_REPLACEMENT',
     AC_ON_additional_data_bytes_per_SM=163840,AC_ON_equal_area_claim=False,
     failure_policy='STOP_ALL_SUBSEQUENT_ON_ANY_FAILED_ATTEMPT_STRICT_IDENTITY_RESOURCE_MODEL_OR_BASE_CALIBRATION_NO_RETRY_NO_RETUNE')
 write(PACK/'SCIENTIFIC_POLICY.json',policy)
 resource=json.loads((PACK/'RESOURCE_CONTRACT.json').read_text())
 resource.update(publication_state='COMPLETE_LOCAL_EXECUTABLE_REGISTRATION_REQUIRES_PUSH_FETCH_BACK',
     OOM_watchdog_implementation='independent owned-child pidfd watchdog every0.25s, also active during hashes and full audits')
 write(PACK/'RESOURCE_CONTRACT.json',resource)
 static=['AUTHORIZATION_AND_SCOPE.md','INTEGRATION_REVIEW.md','RESOURCE_CONTRACT_DIFF_AND_RULING.md',
     'METRIC_DICTIONARY.tsv','COMPARISON_FORMULAS.json','SCIENTIFIC_POLICY.json','RESOURCE_CONTRACT.json',
     'QUALIFICATION_DECISION.json','BASE_SOURCE_BINDINGS.json','QUOTAS_AND_BUFFER_CHARGES.json','RUNTIME_BINDINGS.json','SOURCE_FILES_SHA256.tsv',
     'ORIGINAL_MEMBERS_SHA256.tsv','INPUT_STAT_IDENTITIES.json','INPUT_FULL_IDENTITY.json','UPSTREAM_SOURCE_SHA256.tsv',
     'UUID_RESERVATIONS.json','PUBLISHED_PRODUCER_CONSUMPTION.json','CALIBRATION_REFERENCE_CPU_CHECK.json',
     'AC_PIPELINE_PUBLIC_JOIN_CPU.json','COMBINED_SOURCE_REVIEW.json','AF_INDEPENDENT_CPU_CONSUMPTION.json']
 files={p:sha(PACK/p) for p in static+list(requirements)}
 for prefix in ['inputs','scripts','config','specs','controls']:
  for path in sorted((PACK/prefix).rglob('*')):
   if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ['.pyc','.log']:files[str(path.relative_to(PACK))]=sha(path)
 write(PACK/'EXECUTABLE_PREREGISTRATION.json',dict(status='EXECUTABLE_PREREGISTERED_NOT_YET_STARTED',utc=now(),
     goal='DTC_LANE_AG_OPTIMIZATION_INTEGRATION_AND_SCREEN_174_R2',cohort='DISCOVERY_OPT',
     combined_core_commit=binding['combined_core_commit'],ordered_specs=specs,
     reserved_UUID_count=8,actual_start_cap=8,qualified_slots=6,HOLD_UNQUALIFIED_slots=2,
     max_concurrency=1,files=files,runtime_files=binding['runtime_files'],loader=binding['loader'],
     source_rule='published fixed X2 + exact AC/AE union, no AD/AF',
     execution_gate='COMMIT_PUSH_FETCH_BACK_RECEIPT_AND_FRESH_EACH_ATTEMPT_ADMISSION_AUTHORITY_THEN_ONE_POPEN',
     stop_policy='ANY_FAILED_STRICT_ATTEMPT_OR_PRELAUNCH_IDENTITY_RESOURCE_AUTHORITY_STOP_TERMINATES_COHORT_NO_RETRY',
     BASE_gate='BOTH_COMPLETE_FULL_STRICT_AND_FROZEN_COMMON_CALIBRATION_BEFORE_ANY_OPT',
     paper='RECOMMENDATIONS_ONLY_NO_v0.14-R1_OR_OLD44_OR_GM12_EDITS'))
 print(json.dumps(dict(status='COMPLETE_LOCAL_REGISTRATION_NOT_YET_PUBLISHED',files=len(files),slots=8,qualified=6,HOLD=2,new_simulations=0)))

if __name__=='__main__':main()
