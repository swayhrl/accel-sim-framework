"""Independent mapping-six proof graph audit. Never executes candidate code."""
import ast,pathlib,json,hashlib,copy
from audit_common_v1 import need,canonical
import audit_progress_v3 as base
CONTRACT_REF={'path': '/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/auto161_pipeline_20261026_v1/mapping6_additive_progress_prepare_20261027_v1/ROOT_ADDITIVE_CONTRACT_V1.json', 'sha256': '6a63bea9da069b345df5724001c6f50df8ce310b66a14aedbf3e484b8934ddcd', 'bytes': 19546}
RULE_REF={'path': '/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/auto161_pipeline_20261026_v1/mapping6_additive_progress_prepare_20261027_v1/mapping6_additive_rules_v1.py', 'sha256': '9815134618006abbb7408c40230ff0785455fd118d7cf7ebccaf7d78bc42bb6c', 'bytes': 7262}
PRODUCER='ROOT_MAPPING6_INDEPENDENT_STATIC_FACTS_V1'
PROFILE='EXACT6_RAW_ELF_OWNER_PC_PLR_CPU_V1'
GATES={'EXACT_STATIC_METADATA_REOPEN_OR_NEW_PROOF','COMPLETE_STATIC_MAP_METADATA_OR_ERROR_REPAIR','EXACT_MAPPING_REPAIR_WITH_NEGATIVE_REGRESSION'}
def verify_progress(reader,ctx,row,result):
 index=base.ROOT/'BASELINE_ACCEPTED_RESULTS_V1.json'
 need(hashlib.sha256(reader.bytes(index)).hexdigest()==base.BASELINE_SHA,'V4_BASELINE_PIN')
 matches=[x for x in reader.obj(index)['rows']if x['queue_id']==row['queue_id']]
 need(len(matches)==1 and matches[0]['frozen_row_sha256']==canonical(row),'V4_BASELINE_ROW')
 old=reader.refobj(matches[0]['baseline_result_ref'])
 original=old['missing_proofs'];need(result.get('original_missing_proofs')==original,'V4_ORIGINAL_PROOFS_CHANGED')
 choices={};mapping_refs=[]
 all_sha={x['sha256']for x in ctx.get('dependency_artifacts',[])}
 for ref in ctx.get('dependency_artifacts',[]):
  d=reader.refobj(ref)
  if d.get('status')!='PASS'or d.get('row_bindings',{}).get(row['queue_id'])!=canonical(row)or row['queue_id']not in d.get('target_queue_ids',[])or set(d.get('requires',[]))-all_sha:continue
  identity=(d.get('producer_id'),d.get('profile'));gates=d.get('provided_gates',[])
  rules={}
  if identity==('AUTO161_EXISTING_STATIC_REOPEN_CPU_V1','AUTO161_EXISTING_STATIC_METADATA_REOPEN_CPU_V1'):rules={'EXACT_STATIC_METADATA_REOPEN_OR_NEW_PROOF':'EXACT_STATIC_METADATA_REOPEN_OR_NEW_PROOF'}
  elif identity==('AUTO161_C8_AVAILABILITY_REVIEW_ADAPTER_V1','AUTO161_EXISTING_C8_AVAILABILITY_REVIEW_V1'):rules={'EXISTING_C8_AVAILABILITY_METADATA_REVIEW_CLOSED_V1':'ROOT_AVAILABLE_WORKLOAD_ROUTE_DECISION'}
  elif identity==(PRODUCER,PROFILE):
   need(set(gates)==GATES and len(gates)==3,'V4_EXACT_THREE_MAPPING_GATES');mapping_refs.append(ref)
   rules={g:g for g in GATES}
  for gate,proof in rules.items():
   if gate in gates:choices.setdefault(proof,[]).append((ref['sha256'],d['producer_id'],d['profile']))
 expected=[];remaining=[]
 for p in original:
  found=choices.get(p['proof_id'],[])
  if found:
   h,pid,profile=min(found);expected.append(dict(proof_id=p['proof_id'],artifact_sha256=h,producer_id=pid,profile=profile,CPU_only=True))
  else:remaining.append(p)
 need(result.get('cpu_resolved_proofs')==expected,'V4_UNPROVEN_CPU_DISCHARGE')
 if not mapping_refs:return base.verify_progress(reader,ctx,row,result)
 need(len(mapping_refs)==1,'V4_ONE_MAPPING_ARTIFACT')
 c=reader.refobj(CONTRACT_REF);source=reader.refobj(c['independent_static_report_ref']);att=reader.refobj(c['current_binary6_attestation_ref'])
 need(c['schema']=='ROOT_EXACT6_STATIC_REPAIR_ADDITIVE_DEPENDENCY_CONTRACT_V1'and c['exact_rows']==6 and c['CPU_only']is True and c['GPU_or_simulation_allowed']is False,'V4_EXACT_CONTRACT')
 need([x['static_fact']for x in c['rows']]==source['closed_six'],'V4_STATIC_SOURCE_JOIN')
 ms=[x for x in c['rows']if x['queue_id']==row['queue_id']]
 need(len(ms)==1 and ms[0]['frozen_row_sha256']==canonical(row)and ms[0]['binary_sha256']==row['binary_sha256']and ms[0]['job_sha256']==row['job_sha256']and ms[0]['argv']==row['argv'],'V4_EXACT_SIX_SCOPE');m=ms[0];f=m['static_fact']
 actual=[x for x in att['rows']if x['queue_id']==row['queue_id']]
 need(att.get('all_match')is True and len(actual)==1 and actual[0]['MATCH']is True and actual[0]['O_NOATIME']is True and actual[0]['path']==row['argv'][0]and actual[0]['actual_sha256']==row['binary_sha256'],'V4_CURRENT_BINARY')
 # Read pinned literals as data, without importing or executing the candidate implementation.
 raw=reader.bytes(RULE_REF['path']);need(hashlib.sha256(raw).hexdigest()==RULE_REF['sha256'],'V4_RULE_DATA_PIN')
 tree=ast.parse(raw);nodes=[x for x in tree.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='KINDS'for t in x.targets)]
 need(len(nodes)==1,'V4_STATIC_EVIDENCE_LITERAL');kind_specs=ast.literal_eval(nodes[0].value)
 kinds=['ACTUAL_LOADED_IMAGE_FUNCTION_ALIAS_ASSOCIATION','ACTUAL_APPLICATION_INPUT_LIFETIME_AND_NUMERICAL_ORACLE','COMPLETE_APPLICATION_CAPTURE_AND_CONSUMER_COMPATIBILITY']
 if f['flat_overlap_keys']>0:kinds.append('IMAGE_KEYED_PRODUCER_AND_CONSUMER_INTERFACE')
 if f['latent_specialist_static_sites']:kinds.append('STATIC_CONTROL_SITE_PRODUCER_CONSUMER_DYNAMIC_CLOSURE')
 need(m['new_mandatory_obligation_kinds']==kinds,'V4_EXPLICIT_ADDENDUM_CENSUS')
 b={k:row[k]for k in ['queue_id','job_sha256','binary_sha256','declared_identity_sha256']};b['argv_sha256']=canonical(row['argv'])
 additions=[]
 for kind in kinds:
  adapter,evidence=kind_specs[kind]
  p=dict(proof_id='REPAIRED_MAPPING6_'+kind,binding=b.copy(),required_evidence=list(evidence),next_adapter_id=adapter,next_adapter_ABI='AUTO161_ARTIFACT_V1',satisfied=False,origin_contract_sha256=CONTRACT_REF['sha256'],static_fact_only=True)
  if kind=='STATIC_CONTROL_SITE_PRODUCER_CONSUMER_DYNAMIC_CLOSURE':p['actual_static_site_census']=f['latent_specialist_static_sites']
  if kind=='IMAGE_KEYED_PRODUCER_AND_CONSUMER_INTERFACE':p['flat_overlap_keys']=f['flat_overlap_keys']
  additions.append(p)
 stage=old['next_stage']
 if stage=='WAIT_MAPPING_ADAPTER':
  need(not any(x['proof_id']in GATES for x in remaining),'V4_UNCLOSED_MAPPING')
  stage='WAIT_ISA_ADAPTER'if f['flat_overlap_keys']or f['latent_specialist_static_sites']else'WAIT_SOURCE_RUNTIME_ADAPTER'
  need(stage==m['new_mapping_primary_next']and m['mapping_primary_can_advance']is True,'V4_MAPPING_ROUTE')
 need(result.get('missing_proofs')==remaining+additions and bool(additions),'V4_LOST_DYNAMIC_OR_ADDITIVE_PROOFS')
 requests=[dict(adapter_id=p['next_adapter_id'],ABI=p['next_adapter_ABI'],target_queue_ids=[row['queue_id']],family_keys=[p['family_key']]if p.get('family_key')else[],requires_proof_id=p['proof_id'],input_binding=p['binding'],provided_gates_must_remain_CPU_only=True,next_stage=stage)for p in remaining+additions]
 need(result.get('dependency_requests')==requests,'V4_STALE_REQUEST_OR_ROUTE')
 facts=result.get('facts',{}).get('exact6_mapping_progress',{})
 need(facts.get('contract_ref')==CONTRACT_REF and facts.get('current_binary6_attestation_ref')==c['current_binary6_attestation_ref']and facts.get('independent_static_report_ref')==c['independent_static_report_ref']and facts.get('added_proof_ids')==[p['proof_id']for p in additions]and facts.get('static_control_census')==f['latent_specialist_static_sites']and facts.get('max_static_CALL_summary_dst')==f['max_dst_count']and facts.get('flat_overlap_keys')==f['flat_overlap_keys']and facts.get('CALL_summary_is_physical_RF')is False and facts.get('dynamic_or_trace_or_consumer_or_science_qualified')is False,'V4_FACT_SCOPE_OR_QUALIFICATION')
 return stage
