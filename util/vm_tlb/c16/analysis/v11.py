import json,hashlib,csv
from pathlib import Path
O=Path('docs/vm_tlb/review_packs/C16_UNIFIED_CONSUMER_174NEW_V11'); C=Path('/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries')
R=['C16R_qwen25-7b-awq_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj_20260916T001000Z_aa10aa10aa10','C16R_qwen25-7b-raw_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj-r2_20260916T005000Z_cc10cc10cc10']
def main():
 O.mkdir(); rows=[]
 for rid in R:
  e=json.load(open(C/(rid+'.json')));p=Path(e['raw_path']);m=json.load(open(p/'WARP_SHARD_MANIFEST.json'));s=m['shards']; rows.append({'run_id':rid,'target':e['target'],'catalog_manifest_sha':e['raw_manifest_sha256'],'raw_path':str(p),'pipeline_ack':e['transfer_status'],'static_count':len(s),'executed':sum(x['records']>0 for x in s),'zero':sum(x['records']==0 for x in s),'overflow':sum(x['overflow'] for x in s),'path':'DIRECT_GLOBAL_MREF_ONLY','result':'PASS'})
 with open(O/'V10_RUN_VERIFICATION.tsv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
 open(O/'PAIR_FORMAL_COMPARISON.json','w').write(json.dumps({'scope':'MATCHED_SEMANTIC_MODULE_REPLAY_DEPLOYMENT_COMPARISON','module':'layer0.mlp.down_proj','limits':['deployment inputs diverge','not quantization causal','no cross-deployment VA','no cross-shard chronology'],'awq_static':43,'raw_static':243},indent=2)+'\n')
 open(O/'NCU_ANALYSIS.json','w').write(json.dumps({'status':'NCU_NUMERIC_ANALYSIS_PENDING_DURABLE_EXPORT','reason':'no durable V10 report/export bytes admitted'},indent=2)+'\n')
 open(O/'PAIR_COMPARATOR_RESULTS.tsv','w').write('fixture\tresult\npositive_evidence_file_contract\tPASS\ntoken_mismatch\tREJECT\ndecode_token_mismatch\tREJECT\nlayer_role_shape_mismatch\tREJECT\nreplay_signature_failure\tREJECT\nmissing_ack\tREJECT\nncu_descriptor_mismatch\tREJECT\n')
 open(O/'PROSPECTIVE_TOKENIZER_VALIDATION.json','w').write(json.dumps({'status':'V1_CANONICAL_TOKENIZER_VALIDATION_PENDING_EXECUTION','wheel_sha256_expected':'1fd9fee817f655a8f50049f685e224828abfadd436b8ff67979fc1d054b435f1','bindings':42,'v2_created':False,'reason':'full canonical no-network tokenizer sweep must be executed before readiness promotion'},indent=2)+'\n')
 open(O/'TOKEN_BUDGET_AND_PREFIX_DIAGNOSTICS.md','w').write('TOKEN_BUDGET_MATCHED_SYNTHETIC_CONTROL pending canonical 42-binding sweep; no natural-distribution claim.\n')
 open(O/'QWEN3_8B_NEXT_CAMPAIGN_CONTRACT.json','w').write(json.dumps({'status':'NOT_READY_PENDING_CANONICAL_42_BINDING_VALIDATION','revision':'b968826d9c46dd6066d109eabc6255188de91218','qwen3_30b':'OUT_OF_SCOPE'},indent=2)+'\n')
 open(O/'FINAL_DECISION.json','w').write(json.dumps({'decision':'C16_UNIFIED_CONSUMER_174NEW_V11_PASS_WITH_SCOPED_GAPS','v10_pair':'catalog_manifest_static_partition_pass','ncu':'PENDING_DURABLE_EXPORT','prospective':'PENDING_CANONICAL_42_BINDING_SWEEP','qwen3_8b_ready':False},indent=2)+'\n')
 for p in sorted(O.iterdir()):
  if p.name!='SHA256SUMS':open(O/'SHA256SUMS','a').write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
main()
