#!/usr/bin/env python3
"""Independent exact CPU-proof acceptance; never executes candidate adapter code."""
import pathlib,hashlib,json
from audit_common_v1 import need,canonical
ROOT=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/auto161_pipeline_20261026_v1/root/proof_progress_v3')
BASELINE_SHA='83fe7a028ea4c06620a1d83f7a1cf4f1dcc855d7585dbc2b3c921668cf0fc1db'
def verify_progress(reader,ctx,row,result):
 index=ROOT/'BASELINE_ACCEPTED_RESULTS_V1.json'
 need(hashlib.sha256(reader.bytes(index)).hexdigest()==BASELINE_SHA,'V3_BASELINE_PIN_CHANGED')
 baseline=reader.obj(index);matches=[x for x in baseline['rows']if x['queue_id']==row['queue_id']]
 need(len(matches)==1 and matches[0]['frozen_row_sha256']==canonical(row),'V3_BASELINE_EXACT_ROW')
 old=reader.refobj(matches[0]['baseline_result_ref']);old_ack=reader.refobj(matches[0]['accepted_ACK_ref'])
 need(old_ack['result_ref']==matches[0]['baseline_result_ref'],'V3_BASELINE_ACK_RESULT_JOIN')
 original=result.get('original_missing_proofs')
 need(original==old['missing_proofs'],'V3_ORIGINAL_TYPED_PROOFS_DERIVATION_CHANGED')
 registry=reader.refobj(ctx['allowlist_ref']);bindings={}
 for ref in ctx.get('dependency_artifacts',[]):
  d=reader.refobj(ref)
  if d.get('status')!='PASS' or d.get('row_bindings',{}).get(row['queue_id'])!=canonical(row):continue
  if row['queue_id']not in d.get('target_queue_ids',[]):continue
  if ctx.get('missing_dependency_sha256'):continue
  identity=(d.get('producer_id'),d.get('profile'))
  gate=None;proof=None
  if identity==('AUTO161_EXISTING_STATIC_REOPEN_CPU_V1','AUTO161_EXISTING_STATIC_METADATA_REOPEN_CPU_V1'):
   gate='EXACT_STATIC_METADATA_REOPEN_OR_NEW_PROOF';proof=gate
  if identity==('AUTO161_C8_AVAILABILITY_REVIEW_ADAPTER_V1','AUTO161_EXISTING_C8_AVAILABILITY_REVIEW_V1'):
   gate='EXISTING_C8_AVAILABILITY_METADATA_REVIEW_CLOSED_V1';proof='ROOT_AVAILABLE_WORKLOAD_ROUTE_DECISION'
  if gate and gate in d.get('provided_gates',[]):
   bindings.setdefault(proof,[]).append((ref['sha256'],d['producer_id'],d['profile']))
 expected=[];remaining=[]
 for item in original:
  choices=bindings.get(item['proof_id'],[])
  if choices:
   h,p,profile=min(choices)
   expected.append({'proof_id':item['proof_id'],'artifact_sha256':h,'producer_id':p,'profile':profile,'CPU_only':True})
  else:remaining.append(item)
 need(result.get('cpu_resolved_proofs')==expected,'V3_UNPROVEN_OR_MISSING_CPU_DISCHARGE')
 stage=old['next_stage']
 completed={x['proof_id']for x in expected}
 if stage=='WAIT_EXISTING_AVAILABILITY_REVIEW'and 'ROOT_AVAILABLE_WORKLOAD_ROUTE_DECISION'in completed:stage='WAIT_SOURCE_RUNTIME_ADAPTER'
 current=result.get('missing_proofs',[])
 if stage=='WAIT_SOURCE_RUNTIME_ADAPTER'and old['next_stage']=='WAIT_EXISTING_AVAILABILITY_REVIEW':
  additions=[x for x in current if x.get('proof_id')=='SOURCE_RUNTIME_ORACLE_EXACT_PROOF']
  need(len(additions)==1,'V3_AVAILABILITY_NEEDS_RUNTIME_PROOF')
  extra=additions[0];b=extra.get('binding',{})
  need(b=={'queue_id':row['queue_id'],'job_sha256':row['job_sha256'],'binary_sha256':row['binary_sha256'],'argv_sha256':canonical(row['argv']),'declared_identity_sha256':row['declared_identity_sha256']},'V3_RUNTIME_NEXT_PROOF_IDENTITY')
  need(extra.get('satisfied')is False and extra.get('next_adapter_id')=='auto161_source_runtime_cpu_prepare_v1' and extra.get('next_adapter_ABI')=='AUTO161_ARTIFACT_V1' and len(extra.get('required_evidence',[]))>=3,'V3_RUNTIME_PROOF_UNQUALIFIED')
  need([x for x in current if x.get('proof_id')!='SOURCE_RUNTIME_ORACLE_EXACT_PROOF']==remaining,'V3_UNAUTHORIZED_DYNAMIC_OR_CPU_PROOF_REMOVAL')
 else:need(current==remaining,'V3_UNAUTHORIZED_DYNAMIC_OR_CPU_PROOF_REMOVAL')
 need(current,'V3_CPU_CANNOT_GRANT_COMPLETION')
 requests=result.get('dependency_requests',[])
 need(len(requests)==len(current) and {x['requires_proof_id']for x in requests}=={x['proof_id']for x in current},'V3_STALE_OR_LOST_NEXT_REQUEST')
 need(all(x['target_queue_ids']==[row['queue_id']]and x['next_stage']==stage for x in requests),'V3_REQUEST_ROUTE_BINDING')
 prior_stage=matches[0]['accepted_state']
 if prior_stage=='WAIT_SOURCE_RUNTIME_ADAPTER'and old['next_stage']=='WAIT_EXISTING_AVAILABILITY_REVIEW':
  need(stage=='WAIT_SOURCE_RUNTIME_ADAPTER','V3_PREVIOUS_ACCEPTED_AVAILABILITY_REGRESSION')
 return stage
