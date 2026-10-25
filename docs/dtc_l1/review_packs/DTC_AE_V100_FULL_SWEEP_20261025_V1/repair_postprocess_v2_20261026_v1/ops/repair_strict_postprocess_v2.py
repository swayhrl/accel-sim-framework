"""Postprocess reviewer for the ten sentinel expected-`-trace` copy defects.

No frozen file, registry, attempt, source identity or model is changed. The
registered v1 terminal function executes unchanged in a private module; only
its sentinel_population callback receives a corrected local expected echo.
"""
import pathlib,json,hashlib,importlib.util,copy
P=pathlib.Path
R=P('/root/data/dtc_failure_repair_20261025_v1/validation')
BASE=R/'tools/repair_strict_v1.py'
BASE_SHA256='f9fb0385e69e2265c933c9d827ce0c4da1c0a5de67eb506613d74f8182f6831e'
REQUEST='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1'
SENTINEL_INPUTS={'3375b4a8feb883fc39f2a7777d224f921a1ecd9ff3d624654a0c69efab0a0d09','a24dde1bad963516ca1bb24a809c5c624e0c18ed216bc75711e3ebe20630cc6b'}
INHERITED_TRACE='/root/workspace/assets/traces/bundles/d57ff01eded73f7a62a3d71b5c8e8a1b16e003d4217acaa337d591f401312326/tree/kernelslist.g'
CORE_COMMIT='9eedb3131937748f0492fa83aad37d3691118d70'
CORE_SOURCE=R.parent/'core/src/gpgpu-sim/shader.cc'
CORE_SOURCE_SHA256='e67a486ef18abf2b8515bc5bb887812c058d29fe9fed8544320cc008e3b4ca11'
def sha(path):return hashlib.sha256(P(path).read_bytes()).hexdigest()
def canon_sha(value):return hashlib.sha256((json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
def corrected_sentinel_spec(spec,domain):
 assert spec['request']==REQUEST and spec['validation_kind']=='COMPONENT_SENTINEL_NOT_FORMAL'
 assert spec['input_digest'] in SENTINEL_INPUTS and spec['component_mode'] in ['LEGACY','BASE','IO','OO','SECTOR']
 assert spec['cohort']=='E2-AEREPAIR-SENT-'+spec['input_digest'][:16]+'-'+spec['component_mode']+'-V1'
 assert spec['core_commit']==CORE_COMMIT and sha(CORE_SOURCE)==CORE_SOURCE_SHA256
 labels={'LEGACY':None,'BASE':'PAPER_BASE','IO':'PAPER_IO','OO':'PAPER_OO','SECTOR':'MODERN_OO_SECTOR'}
 assert spec['terminal_contract']['mode_label']==labels[spec['component_mode']]
 argv=spec['native_simulator_argv'];assert argv.count('-trace')==1
 index=argv.index('-trace');assert index+1<len(argv)
 entry=argv[index+1];assert entry==domain['trace_entry'] and entry!=INHERITED_TRACE
 assert spec['expected_options']['-trace']==[INHERITED_TRACE] and len(spec['expected_options'])==270
 fixed=copy.deepcopy(spec);fixed['expected_options']['-trace']=[entry]
 assert {k:v for k,v in fixed['expected_options'].items() if k!='-trace'}=={k:v for k,v in spec['expected_options'].items() if k!='-trace'}
 correction={'schema':'EXACT_COMPONENT_EXPECTED_TRACE_COPY_DEFECT_V2','classification':'SPEC_EXPECTED_ECHO_METADATA_COPY_DEFECT_NOT_MODEL_OR_INPUT_CHANGE','field':'expected_options.-trace','frozen_incorrect_expectation':[INHERITED_TRACE],'corrected_expected_echo':[entry],'authority_for_correction':'Exact frozen native_simulator_argv -trace argument equals separately SHA-bound qualification.trace_entry; unchanged v1 terminal independently verifies actual launch argv, model maps, strace member opens, commands, all bound metadata and raw option echo.','frozen_expected_options_sha256':canon_sha(spec['expected_options']),'postprocess_expected_options_sha256':canon_sha(fixed['expected_options']),'unchanged_other_option_count':269,'frozen_spec_modified':False,'input_bytes_modified':False,'new_model_starts':0}
 if spec['component_mode'] in ['IO','OO','SECTOR']:
  old_pair=['DTC_L1_lower_requests_acquired','DTC_L1_lower_requests_released'];new_pair=['DTC_L1_lower_credit_acquired','DTC_L1_lower_credit_released'];pairs=fixed['terminal_contract']['equal_counter_pairs']
  assert pairs.count(old_pair)==1 and new_pair not in pairs
  pairs[pairs.index(old_pair)]=new_pair
  source_lines={'IO':[6025,6028],'OO':[6160,6163],'SECTOR':[6092,6095]}[spec['component_mode']]
  correction['counter_alias_correction']={'classification':'MODE_SPECIFIC_RAW_COUNTER_NAME_COPY_DEFECT','frozen_pair':old_pair,'actual_source_printed_pair':new_pair,'unchanged_predicate':'dtc_l1_lower_requests_acquired() == dtc_l1_lower_requests_released()','source_path':str(CORE_SOURCE),'source_sha256':CORE_SOURCE_SHA256,'source_commit':CORE_COMMIT,'mode_specific_print_lines':source_lines,'BASE_print_lines':[6228,6231],'no_counter_or_comparison_removed':True}
  assert len(pairs)==len(spec['terminal_contract']['equal_counter_pairs'])
 else:assert fixed['terminal_contract']==spec['terminal_contract']
 return fixed,correction
def adapted():
 assert sha(BASE)==BASE_SHA256,'original registered strict source changed'
 loader=importlib.util.spec_from_file_location('private_registered_strict_v1_for_postprocess_v2',BASE);base=importlib.util.module_from_spec(loader);loader.loader.exec_module(base)
 original=base.sentinel_population
 def sentinel_population(raw,spec,domain,legacy):
  fixed,correction=corrected_sentinel_spec(spec,domain)
  result=original(raw,fixed,domain,legacy)
  result['exact_metadata_defect_correction']=correction
  return result
 base.sentinel_population=sentinel_population
 return base
def terminal(cell):
 base=adapted();proof=base.terminal(cell)
 assert proof['strict_overlay_sha256']==BASE_SHA256
 component=proof['validation_kind']=='COMPONENT_SENTINEL_NOT_FORMAL'
 if component:assert proof['exact_metadata_defect_correction']['unchanged_other_option_count']==269
 proof.update(schema='DTC_FAILURE_REPAIR_CORRECTNESS_POSTPROCESS_REVIEW_V2',registered_base_strict_path=str(BASE),registered_base_strict_sha256=BASE_SHA256,postprocess_reviewer_path=str(P(__file__)),postprocess_reviewer_sha256=sha(__file__),registered_v1_source_unmodified=True,registered_v1_terminal_body_executed_unchanged=True,registered_v1_sentinel_population_unmodified_PASS=False if component else None,strict_overlay_sha256_semantics='Registered v1 file identity, retained to match actual launch authority; for component cases its private sentinel_population callback was substituted by this explicitly identified v2. This does not claim that unmodified v1 accepted the sentinel.',postprocess_only_no_new_science_start=True,original288_untouched=True)
 return proof
