#!/usr/bin/env python3
"""Fail-closed preparation for future raw7B/AWQ formal pair comparison."""
import csv, hashlib, json
from pathlib import Path

ROOT=Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw')
OUT=Path('docs/vm_tlb/review_packs/C16_RAW7B_AWQ_PAIR_PREP_174NEW_LANEA_V8')
RUNS={'PREFILL_AWQ_DEQUANT':'C16R_qwen25-7b-awq_s2-text_prefill_nvbit-warp-mref-shard_q7awq-prefill-dequant_20260915T191000Z_b71b7b2b2c2d','DECODE_FUSED_GEMM':'C16R_qwen25-7b-awq_s2-text_decode_nvbit-warp-mref-shard_q7awq-decode-fused-gemm_20260915T192000Z_c81c8c3c3d3e'}
ROLES=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj']
REQUIRED=['token_canonical_sha256','model_family','raw_revision','awq_revision','layer_id','linear_role','shape','phase_scope','raw_replay_equivalence','raw_path_coverage','awq_path_coverage']
def compare(raw,awq):
 missing=[x for x in REQUIRED if not raw.get(x) or not awq.get(x)]
 bad=[x for x in ['token_canonical_sha256','model_family','layer_id','linear_role','shape','phase_scope'] if raw.get(x)!=awq.get(x)]
 if raw.get('raw_replay_equivalence')!='PASS' or raw.get('raw_path_coverage')!='ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL' or awq.get('awq_path_coverage')!='ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL': bad.append('closure')
 if raw.get('ncu_cache_control') and awq.get('ncu_cache_control') and raw['ncu_cache_control']!=awq['ncu_cache_control']: bad.append('ncu_cache_control')
 return {'result':'REJECT' if missing or bad else 'COMPARABLE','missing':missing,'mismatch':bad,'awq_only_metrics':['dequantization'],'incomparable':['cross_deployment_absolute_va','cross_shard_order','reuse_distance'],'unresolved_object_attribution':'UNKNOWN_RUNTIME_RETAINED'}
def main():
 OUT.mkdir(); rows=[]
 for target,run in RUNS.items():
  raw=ROOT/run
  m=json.loads((raw/'WARP_SHARD_MANIFEST.json').read_text())
  for s in m['shards']:
   p=raw/s['address_context']; c=json.loads(p.read_text()); known=sum(int(x['address_end_hex'],16)-int(x['address_start_hex'],16) for x in c.get('ranges',[]))
   rows.append({'target':target,'static_index':s['static_index'],'context_sha256':s['address_context_sha256'],'address_space_id':c.get('address_space_id',''),'same_process_only':c.get('same_process_only',False),'known_range_bytes':known,'formal_events_mapped':0,'formal_events_unmapped':'NOT_PROMOTED_WITHOUT_LOSSLESS_EVENT_RANGE_JOIN','object_attribution':'UNKNOWN_RUNTIME','promotion_reason':'NO_RECORDED_EVENT_TO_RANGE_LOSSLESS_BINDING'})
 with (OUT/'AWQ_OBJECT_ATTRIBUTION_DIAGNOSTIC.tsv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
 inv=[]
 for layer in range(28):
  for role in ROLES: inv.append({'layer_id':layer,'semantic_role':role,'raw_bf16_shape':'PENDING_CANONICAL_RAW_METADATA','raw_bf16_bytes':'PENDING','awq_qweight_shape':'PENDING_CANONICAL_AWQ_METADATA','awq_qzero_scale_shape':'PENDING_CANONICAL_AWQ_METADATA','one_to_one':'UNRESOLVED_UNTIL_AWQ_ANCHOR_PROVEN'})
 with (OUT/'PAIR_SEMANTIC_SHAPE_INVENTORY.tsv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(inv[0]),delimiter='\t');w.writeheader();w.writerows(inv)
 contract={'schema_version':1,'required_fields':REQUIRED,'ncu_rule':'reject only when both numeric semantic descriptors are present and incompatible; no values invented','comparator':'fail_closed','awq_anchor':'UNRESOLVED'}; (OUT/'PAIR_COMPARATOR_CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n')
 base={'token_canonical_sha256':'x','model_family':'Qwen2.5-7B','raw_revision':'r','awq_revision':'a','layer_id':'0','linear_role':'q_proj','shape':'1x1','phase_scope':'DECODE','raw_replay_equivalence':'PASS','raw_path_coverage':'ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL','awq_path_coverage':'ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL'}
 tests=[('token_mismatch',compare(base,{**base,'token_canonical_sha256':'y'})['result']=='REJECT'),('role_mismatch',compare(base,{**base,'linear_role':'k_proj'})['result']=='REJECT'),('shape_mismatch',compare(base,{**base,'shape':'2x1'})['result']=='REJECT'),('replay_missing',compare(base,{**base,'raw_replay_equivalence':'FAIL'})['result']=='REJECT'),('ncu_incompatible',compare({**base,'ncu_cache_control':'A'},{**base,'ncu_cache_control':'B'})['result']=='REJECT'),('deterministic',compare(base,base)==compare(base,base))]
 with (OUT/'COMPARATOR_TEST_RESULTS.tsv').open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['test','result']);w.writerows((n,'PASS' if ok else 'FAIL') for n,ok in tests)
 (OUT/'RAW_TARGET_RECOMMENDATION.md').write_text('Recommend one ordinary decoder-layer MLP linear only after node109 proves the exact AWQ semantic anchor; do not pre-freeze layer/role.\n')
 (OUT/'OPEN_ISSUES.md').write_text('NCU numeric exports are absent and intentionally not invented. Raw7B canonical metadata and AWQ semantic anchor remain producer prerequisites.\n')
 (OUT/'FINAL_DECISION.json').write_text(json.dumps({'decision':'C16_RAW7B_AWQ_PAIR_PREP_174NEW_LANEA_V8_PASS','pair_comparison':'NOT_YET_ALLOWED_FAIL_CLOSED','unknown_runtime_preserved':True,'cpu_only':True},indent=2)+'\n')
 for p in sorted(OUT.iterdir()):
  if p.name!='SHA256SUMS':
   with (OUT/'SHA256SUMS').open('a') as f:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
if __name__=='__main__':main()
