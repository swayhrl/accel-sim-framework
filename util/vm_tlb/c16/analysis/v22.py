import json,hashlib,os
from pathlib import Path
ROOT=Path('/root/share/mnt164/huangrulin/c16_ai_workload');A=ROOT/'assets/models/deepseek-v2-lite/604d5664dddd88a0433dbae533b7fe9472482de0';O=Path('docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_AUTHORIZATION_174NEW_V22')
def sh(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 O.mkdir();c=json.load(open(A/'config.json'));files=[p for p in A.iterdir() if p.is_file()];size=sum(p.stat().st_size for p in files);auth={'model_id':'deepseek-ai/DeepSeek-V2-Lite','revision':'604d5664dddd88a0433dbae533b7fe9472482de0','config_sha256':sh(A/'config.json'),'asset_bytes':size,'architecture':c.get('architectures'),'cpu_only':True,'capacity_mode':'EXACT_SEMANTIC_LAYER_STREAMING_REPLAY','native_full_resident':'PRECHECK_REQUIRED'}
 mla={'dataflow':'MLA: q projection; compressed kv latent; kv_a/kv_b expansion; RoPE/nope split; attention uses reconstructed K/V','formal_targets':['mla_kv_latent_read','mla_kv_b_expand','attention_output_projection'],'not_ordinary_mha':True};moe={'dataflow':'MoE router logits -> top-k natural routing -> selected expert MLPs -> weighted combine','formal_targets':['router_topk_natural_routing','selected_expert_down_proj','moe_combine'],'not_dense_mlp':True,'routing':'NATURAL_ROUTING_REQUIRED'}
 inp={'authority':'DeepSeek canonical S2 input','source':'C16_PROSPECTIVE_COMMON_INPUT_V2','retokenization':False,'status':'PREEXECUTION_CANONICAL_AUTHORITY_REQUIRED'};contract={'producer_host':'node109','model':auth,'runtime_api':{'must_capture':'runtime/backend/version, MLA and MoE routing observables','no_gpu_by_consumer':True},'mla':mla,'moe':moe,'scenarios':['S2','S3'],'stop_conditions':['input_hash_mismatch','revision_mismatch','non-natural_moe_routing','overflow_drop','semantic_target_mismatch']}
 for n,x in [('MODEL_AUTHORITY.json',auth),('DEEPSEEK_S2_INPUT_AUTHORITY.json',inp),('MLA_DATAFLOW_AND_TARGETS.json',mla),('MOE_DATAFLOW_AND_TARGETS.json',moe),('NODE109_PRODUCER_EXECUTION_CONTRACT.json',contract),('FINAL_DECISION.json',{'decision':'C16_DEEPSEEK_V2_LITE_AUTHORIZATION_174NEW_V22_PASS','next_lineage':'DeepSeek-V2-Lite','gpu_execution':False})]:open(O/n,'w').write(json.dumps(x,indent=2,sort_keys=True)+'\n')
 open(O/'README.md','w').write('CPU-only DeepSeek-V2-Lite authorization. MLA and natural-routing MoE are explicit first-class dataflows.\n');open(O/'OPEN_ISSUES.md','w').write('Producer must satisfy exact runtime/API contract before GPU execution.\n')
 with open(O/'SHA256SUMS','w') as f:
  for p in sorted(O.iterdir()):
   if p.name!='SHA256SUMS':f.write(sh(p)+'  '+p.name+'\n')
main()
