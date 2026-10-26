"""Exact-six additive proof graph. Pure CPU metadata; no qualification."""
import json,hashlib
PRODUCER='ROOT_MAPPING6_INDEPENDENT_STATIC_FACTS_V1'
PROFILE='EXACT6_RAW_ELF_OWNER_PC_PLR_CPU_V1'
GATES={'EXACT_STATIC_METADATA_REOPEN_OR_NEW_PROOF','COMPLETE_STATIC_MAP_METADATA_OR_ERROR_REPAIR','EXACT_MAPPING_REPAIR_WITH_NEGATIVE_REGRESSION'}
KINDS={
'ACTUAL_LOADED_IMAGE_FUNCTION_ALIAS_ASSOCIATION':('auto161_loaded_image_function_cpu_prepare_v1',[
'Actual current loaded image/JIT identity must join exact frozen image ordinal and raw cubin SHA, complete owner/relative-PC and alias identity.',
'Capture actual CUcontext/CUfunction/function-address lifetimes; disk static maps are not loaded-image evidence.',
'No flat (function,PC) projection is allowed for image-keyed maps; all relevant loaded images must be accounted for.']),
'ACTUAL_APPLICATION_INPUT_LIFETIME_AND_NUMERICAL_ORACLE':('auto161_source_runtime_cpu_prepare_v1',[
'Exact source/binary/argv and resolved loaded runtime baseline; actual input read set and initialization must be established.',
'Bind complete observed supported input bytes/order/API-success/lifetime and explicitly retain unsupported Memset/D2D/symbol/managed/mapped/external domains.',
'Use a source-aware whole-application numerical oracle; seed, declared argv and static mapper success do not prove actual input equality.']),
'COMPLETE_APPLICATION_CAPTURE_AND_CONSUMER_COMPATIBILITY':('auto161_exact_capture_consumer_prepare_v1',[
'Whole application launch/CTA/warp/record/EOF and sender+receiver full SHA closure, without ROI/sampling shortcuts.',
'Independent actual consumer format/ISA/operand/memory compatibility for the exact producer profile; no generic prior-profile inheritance.',
'Actual Native read/restore remains a separate requirement; static facts never grant trace, consumer, science or performance qualification.']),
'IMAGE_KEYED_PRODUCER_AND_CONSUMER_INTERFACE':('auto161_image_keyed_interface_cpu_prepare_v1',[
'Both producer and consumer must carry image ordinal+raw cubin SHA+owner+original relative PC as a bound key.',
'Actual loaded image/function/alias association must resolve every colliding flat owner/PC; a flat table is not an acceptable substitute.',
'Demonstrate correct independent parsing and whole-application dynamic association before claiming exact image-scoped compatibility.']),
'STATIC_CONTROL_SITE_PRODUCER_CONSUMER_DYNAMIC_CLOSURE':('auto161_isa_family_cpu_prepare_v1',[
'The independently frozen static census contains CALL/RET and/or WARPSYNC; identify exact opcode, owner, image and relative PC.',
'Provide matching new producer and independent consumer ABI, active-lane/lifecycle/control/return or named-mask closure for the actually exercised domain.',
'CALL transitive liveness summaries are not physical RF writes; zero dynamic CALL records do not qualify CALL/RET semantics.'])
}
def digest(v):
 return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def need(v,m):
 if not v:raise ValueError('MAPPING6_'+m)
def expected_kinds(fact):
 keys=['ACTUAL_LOADED_IMAGE_FUNCTION_ALIAS_ASSOCIATION','ACTUAL_APPLICATION_INPUT_LIFETIME_AND_NUMERICAL_ORACLE','COMPLETE_APPLICATION_CAPTURE_AND_CONSUMER_COMPATIBILITY']
 if fact['flat_overlap_keys']:keys.append('IMAGE_KEYED_PRODUCER_AND_CONSUMER_INTERFACE')
 if fact['latent_specialist_static_sites']:keys.append('STATIC_CONTROL_SITE_PRODUCER_CONSUMER_DYNAMIC_CLOSURE')
 return keys
def binding(row):
 return {k:row[k]for k in ['queue_id','job_sha256','binary_sha256','declared_identity_sha256']}|{'argv_sha256':digest(row['argv'])}
def apply(row,result,feedback,contract,contract_ref):
 chosen=[g for g in feedback['closed_CPU_candidate_gates']if g['producer_id']==PRODUCER and g['profile']==PROFILE]
 if not chosen:return result
 need({g['gate']for g in chosen}==GATES,'EXACT_THREE_METADATA_GATES')
 need(len({g['artifact_sha256']for g in chosen})==1,'ONE_EXACT_ARTIFACT')
 need(contract['schema']=='ROOT_EXACT6_STATIC_REPAIR_ADDITIVE_DEPENDENCY_CONTRACT_V1'and contract['exact_rows']==6 and contract['CPU_only']is True and contract['GPU_or_simulation_allowed']is False,'ROOT_CONTRACT_SCOPE')
 matches=[r for r in contract['rows']if r['queue_id']==row['queue_id']]
 need(len(matches)==1,'EXACT_SIX_ROW_ONLY');match=matches[0]
 need(match['frozen_row_sha256']==digest(row) and match['binary_sha256']==row['binary_sha256'] and match['job_sha256']==row['job_sha256'] and match['argv']==row['argv'],'CURRENT_ROW_BINDING')
 fact=match['static_fact']
 need(fact['queue_id']==row['queue_id']and fact['binary_sha256']==row['binary_sha256']and fact['CPU_proof_only']is True and fact['full_image_SHA_ordinal_owner_PC_unique']is True and fact['TSV_exact']is True and fact['raw_ELF_PLR_independent_check']['PASS']is True,'STATIC_FACT_EXACT')
 need(fact['raw_ELF_PLR_independent_check']['binary']==row['binary_sha256'],'RAW_BINARY_BOUND')
 kinds=expected_kinds(fact);need(match['new_mandatory_obligation_kinds']==kinds,'OBLIGATION_CENSUS')
 existing={p['proof_id']for p in result['missing_proofs']};added=[]
 for kind in kinds:
  proof_id='REPAIRED_MAPPING6_'+kind
  need(proof_id not in existing,'DUPLICATE_OR_PREEXISTING_ADDITION')
  adapter,evidence=KINDS[kind]
  p={'proof_id':proof_id,'binding':binding(row),'required_evidence':list(evidence),'next_adapter_id':adapter,'next_adapter_ABI':'AUTO161_ARTIFACT_V1','satisfied':False,'origin_contract_sha256':contract_ref['sha256'],'static_fact_only':True}
  if kind=='STATIC_CONTROL_SITE_PRODUCER_CONSUMER_DYNAMIC_CLOSURE':p['actual_static_site_census']=dict(fact['latent_specialist_static_sites'])
  if kind=='IMAGE_KEYED_PRODUCER_AND_CONSUMER_INTERFACE':p['flat_overlap_keys']=fact['flat_overlap_keys']
  added.append(p)
 need(added,'NO_EMPTY_DYNAMIC_DEPENDENCY_SET')
 result['missing_proofs'].extend(added)
 stage=result['next_stage']
 if stage=='WAIT_MAPPING_ADAPTER':
  need(match['mapping_primary_can_advance']is True,'MAPPING_STAGE_SCOPE')
  need(not any(p['proof_id']in GATES for p in result['missing_proofs']),'MAPPING_NOT_ALL_PROVED')
  stage='WAIT_ISA_ADAPTER'if fact['flat_overlap_keys']or fact['latent_specialist_static_sites']else'WAIT_SOURCE_RUNTIME_ADAPTER'
  need(stage==match['new_mapping_primary_next'],'MAPPING_NEXT_STAGE');result['next_stage']=stage
 result['dependency_requests']=[{'adapter_id':p['next_adapter_id'],'ABI':p['next_adapter_ABI'],'target_queue_ids':[row['queue_id']],'family_keys':[p['family_key']]if p.get('family_key')else[],'requires_proof_id':p['proof_id'],'input_binding':p['binding'],'provided_gates_must_remain_CPU_only':True,'next_stage':stage}for p in result['missing_proofs']]
 result['facts']['exact6_mapping_progress']={'schema':'EXACT6_MAPPING_STATIC_CLOSED_DYNAMIC_DEPENDENCIES_ADDED_V1','contract_ref':contract_ref,'current_binary6_attestation_ref':contract['current_binary6_attestation_ref'],'independent_static_report_ref':contract['independent_static_report_ref'],'added_proof_ids':[p['proof_id']for p in added],'static_control_census':dict(fact['latent_specialist_static_sites']),'max_static_CALL_summary_dst':fact['max_dst_count'],'flat_overlap_keys':fact['flat_overlap_keys'],'CALL_summary_is_physical_RF':False,'dynamic_or_trace_or_consumer_or_science_qualified':False}
 return result
