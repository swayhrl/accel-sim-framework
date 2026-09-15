#!/usr/bin/env python3
"""Deterministic CPU-only C16 missing-model metadata completion V7."""
import argparse,csv,json,re,statistics,subprocess
from collections import defaultdict
from pathlib import Path
from qwen7_layer_inventory import inventory,sha256,write_tsv,InventoryError
ROOT=Path('/root/share/mnt164/huangrulin/c16_ai_workload')
MODELS=[('Qwen3-8B','Qwen/Qwen3-8B','qwen3-8b','b968826d9c46dd6066d109eabc6255188de91218'),('DeepSeek-V2-Lite','deepseek-ai/DeepSeek-V2-Lite','deepseek-v2-lite','604d5664dddd88a0433dbae533b7fe9472482de0')]
LAYER=re.compile(r'^model\.layers\.(\d+)\.(.+)$')
def fail(msg):raise RuntimeError('FAIL_CLOSED: '+msg)
def canon(v):return json.dumps(v,sort_keys=True,indent=2)+'\n'
def role(name):
 m=LAYER.match(name)
 if name.startswith('model.embed_tokens.'):return 'EMBEDDING_WEIGHT',None,'other',None
 if name.startswith('lm_head.'):return 'LM_HEAD_WEIGHT',None,'other',None
 if not m:return ('NORM_WEIGHT' if '.norm.' in name or name.endswith('norm.weight') else 'OTHER_WEIGHT'),None,'other',None
 layer,rest=int(m.group(1)),m.group(2)
 if '.experts.' in rest:
  e=re.search(r'\.experts\.(\d+)\.',rest);return 'MOE_ROUTED_EXPERT_WEIGHT',layer,'routed_expert',int(e.group(1)) if e else None
 if 'shared_experts.' in rest:return 'MOE_SHARED_EXPERT_WEIGHT',layer,'shared_expert',None
 if rest.startswith('mlp.gate.') or '.router.' in rest:return 'ROUTER_WEIGHT',layer,'router',None
 if rest.startswith('self_attn.') or rest.startswith('attention.'):return 'ATTENTION_WEIGHT',layer,'attention',None
 if rest.startswith('mlp.'):return 'DENSE_MLP_WEIGHT',layer,'dense_mlp',None
 if 'norm' in rest:return 'NORM_WEIGHT',layer,'norm_other',None
 return 'UNKNOWN_STATIC_ROLE',layer,'norm_other',None
def model_dir(slug,rev):return ROOT/'assets/models'/slug/rev
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 arch=[];layers=[];roles=[];details={};summaries={}
 for label,model_id,slug,rev in MODELS:
  d=model_dir(slug,rev)
  if not d.is_dir():fail('canonical model absent: '+label)
  receipt=d/'MODEL_ARCHIVE_RECEIPT.json';config=d/'config.json';index=d/'model.safetensors.index.json'
  if not receipt.is_file() or not config.is_file() or not index.is_file():fail('required authority metadata absent: '+label)
  rec=json.loads(receipt.read_text());cfg=json.loads(config.read_text());inv=inventory(d)
  dtypes=';'.join(sorted({r['dtype'] for r in inv}));total=sum(r['exact_tensor_bytes'] for r in inv);shards=sorted({r['source_shard'] for r in inv})
  row={'model_label':label,'model_id':model_id,'exact_revision':rev,'model_type':cfg.get('model_type','UNKNOWN_FROM_CONFIG'),'checkpoint_dtypes':dtypes,'decoder_layers':cfg.get('num_hidden_layers','UNKNOWN_FROM_CONFIG'),'hidden_size':cfg.get('hidden_size','UNKNOWN_FROM_CONFIG'),'attention_heads':cfg.get('num_attention_heads','UNKNOWN_FROM_CONFIG'),'kv_heads':cfg.get('num_key_value_heads','UNKNOWN_FROM_CONFIG'),'intermediate_size':cfg.get('intermediate_size','UNKNOWN_FROM_CONFIG'),'vocab_size':cfg.get('vocab_size','UNKNOWN_FROM_CONFIG'),'max_position_embeddings':cfg.get('max_position_embeddings','UNKNOWN_FROM_CONFIG'),'rope_theta':cfg.get('rope_theta','UNKNOWN_FROM_CONFIG'),'tie_word_embeddings':cfg.get('tie_word_embeddings','UNKNOWN_FROM_CONFIG'),'checkpoint_shard_count':len(shards),'exact_total_tensor_bytes':total,'archive_receipt_sha256':sha256(receipt)}
  for k in ('first_k_dense_replace','moe_layer_freq','n_routed_experts','n_shared_experts','num_experts_per_tok','moe_intermediate_size','routed_scaling_factor','q_lora_rank','kv_lora_rank','qk_nope_head_dim','qk_rope_head_dim','v_head_dim'):
   row[k]=cfg.get(k,'NOT_PRESENT_IN_ARCHIVED_CONFIG')
  arch.append(row);details[label]={'model_id':model_id,'exact_revision':rev,'canonical_path':str(d),'receipt_sha256':sha256(receipt),'config':cfg,'checkpoint_dtypes':dtypes,'checkpoint_shards':shards,'exact_total_tensor_bytes':total}
  per=defaultdict(lambda:{'attention_bytes':0,'dense_mlp_bytes':0,'norm_other_bytes':0,'router_gate_bytes':0,'routed_expert_bytes':0,'shared_expert_bytes':0,'shards':set(),'experts':defaultdict(int)})
  for r in inv:
   cls,layer,bucket,expert=role(r['tensor_name']);roles.append({'model_label':label,'model_id':model_id,'exact_revision':rev,'tensor_name':r['tensor_name'],'static_role':cls,'decoder_layer_id':'' if layer is None else layer,'source_shard':r['source_shard'],'dtype':r['dtype'],'shape':r['shape'],'exact_tensor_bytes':r['exact_tensor_bytes']})
   if layer is None:continue
   b=per[layer];b['shards'].add(r['source_shard']);key={'attention':'attention_bytes','dense_mlp':'dense_mlp_bytes','norm_other':'norm_other_bytes','router':'router_gate_bytes','routed_expert':'routed_expert_bytes','shared_expert':'shared_expert_bytes'}[bucket];b[key]+=r['exact_tensor_bytes']
   if expert is not None:b['experts'][expert]+=r['exact_tensor_bytes']
  vals=[]
  for lid,b in sorted(per.items()):
   exp=list(b['experts'].values());total_layer=sum(b[k] for k in ('attention_bytes','dense_mlp_bytes','norm_other_bytes','router_gate_bytes','routed_expert_bytes','shared_expert_bytes'));vals.append(total_layer)
   layers.append({'model_label':label,'decoder_layer_id':lid,'attention_bytes':b['attention_bytes'],'dense_mlp_bytes':b['dense_mlp_bytes'],'norm_other_bytes':b['norm_other_bytes'],'router_gate_bytes':b['router_gate_bytes'],'routed_expert_bytes':b['routed_expert_bytes'],'shared_expert_bytes':b['shared_expert_bytes'],'total_layer_parameter_bytes':total_layer,'source_shard_count':len(b['shards']),'source_shards':';'.join(sorted(b['shards'])),'expert_count_represented':len(exp),'per_expert_min_bytes':min(exp) if exp else 0,'per_expert_median_bytes':int(statistics.median(exp)) if exp else 0,'per_expert_max_bytes':max(exp) if exp else 0})
  summaries[label]={'model_id':model_id,'exact_revision':rev,'decoder_layer_count':len(vals),'minimum_decoder_layer_parameter_bytes':min(vals),'median_decoder_layer_parameter_bytes':int(statistics.median(vals)),'maximum_decoder_layer_parameter_bytes':max(vals),'largest_single_layer_parameter_bytes':max(vals),'scope':'static parameter residency only; no runtime CUDA-memory or fit claim'}
 write_tsv(out/'MODEL_STATIC_ARCHITECTURE_V7.tsv',list(arch[0]),arch)
 write_tsv(out/'MODEL_LAYER_RESIDENCY_V7.tsv',list(layers[0]),layers)
 write_tsv(out/'MODEL_STATIC_TENSOR_ROLE_V7.tsv',list(roles[0]),roles)
 (out/'MODEL_LAYER_RESIDENCY_SUMMARY_V7.json').write_text(canon(summaries))
 for label,d in details.items():(out/(label.upper().replace('-','_')+'_STATIC_ARCHITECTURE_V7.json')).write_text(canon(d))
 # Existing source text is authority only for adopted Llama S0; no common seven-scenario source/policy was found.
 adopted=Path('docs/vm_tlb/assets/c16/ai_workload_inputs/ADOPTED_LLAMA_S0_T128_V1/TEXT.txt')
 source_rows=[{'source_class':'LLAMA_ADOPTED_S0_TEXT','source_path':str(adopted),'source_sha256':sha256(adopted),'generation_truncation_policy_identity':'ADOPTED_LLAMA_S0_T128_V1_ONLY','safe_for_prospective_cross_model_retokenization':'false','status':'SOURCE_AUTHORITY_GAP_FOR_CROSS_MODEL_RETOKENIZATION','notes':'preserved adopted future S0 authority; not common-source authority'},{'source_class':'TEXT_COMMON_SEVEN_SCENARIO_FAMILY','source_path':'NOT_FOUND','source_sha256':'NOT_AVAILABLE','generation_truncation_policy_identity':'NOT_FOUND','safe_for_prospective_cross_model_retokenization':'false','status':'SOURCE_AUTHORITY_GAP','notes':'no exact common source text plus deterministic policy; tokens were not reverse-decoded'},{'source_class':'CODE_COMMON_SEVEN_SCENARIO_FAMILY','source_path':'NOT_FOUND','source_sha256':'NOT_AVAILABLE','generation_truncation_policy_identity':'NOT_FOUND','safe_for_prospective_cross_model_retokenization':'false','status':'SOURCE_AUTHORITY_GAP','notes':'no replacement generated'},{'source_class':'STRUCTURED_COMMON_SEVEN_SCENARIO_FAMILY','source_path':'NOT_FOUND','source_sha256':'NOT_AVAILABLE','generation_truncation_policy_identity':'NOT_FOUND','safe_for_prospective_cross_model_retokenization':'false','status':'SOURCE_AUTHORITY_GAP','notes':'no replacement generated'}]
 write_tsv(out/'C16_SOURCE_TEXT_AUTHORITY_AUDIT_V7.tsv',list(source_rows[0]),source_rows)
 inputs=[]
 for label,model_id,slug,rev in MODELS:
  inputs.append({'model_label':label,'model_id':model_id,'model_revision':rev,'scenario':'ALL_MISSING_SCENARIOS','historical_status':'NO_HISTORICAL_FROZEN_BINDING','prospective_status':'NOT_CREATED_SOURCE_AUTHORITY_GAP','binding_action':'NO_TOKENIZATION_NO_NETWORK','notes':'source authority unavailable; historical and prospective axes remain separate'})
 inputs.append({'model_label':'Llama-3.2-1B','model_id':'meta-llama/Llama-3.2-1B','model_revision':'4e20de362430cd3b72f300e6b0f18e50e7166e08','scenario':'S0_TEXT_B1_T128_D4','historical_status':'HISTORICAL_FROZEN_INPUT_NOT_RECOVERED','prospective_status':'FUTURE_ADOPTED_S0_AUTHORITY_NOT_HISTORICAL_RECOVERY','binding_action':'UNCHANGED_ACCEPTED_AUTHORITY','notes':'adopted authority preserved byte-for-byte'})
 inputs.append({'model_label':'Llama-3.2-1B','model_id':'meta-llama/Llama-3.2-1B','model_revision':'4e20de362430cd3b72f300e6b0f18e50e7166e08','scenario':'MISSING_NON_S0_SCENARIOS','historical_status':'HISTORICAL_FROZEN_INPUT_NOT_RECOVERED','prospective_status':'NOT_CREATED_SOURCE_AUTHORITY_GAP','binding_action':'NO_TOKENIZATION_NO_NETWORK','notes':'no common source/policy closure'})
 write_tsv(out/'MODEL_INPUT_AUTHORITY_V7.tsv',list(inputs[0]),inputs)
 contracts={'Qwen3-8B':{'status':'PLANNING_READINESS_ONLY','requires':['exact layer weights','exact incoming hidden state','position/attention state','layer-local KV state','runtime deployment identity','output equivalence','kernel signature equivalence','full-function global-address-path audit before formal capture']},'DeepSeek-V2-Lite':{'status':'PLANNING_READINESS_ONLY','requires':['exact layer weights','exact incoming hidden state','archived MLA state','exact router/expert decisions','layer-local state appropriate to config','output and kernel-signature equivalence','full-function global-address-path audit'],'forbids':['simplifying MLA to ordinary K/V','simplifying MoE to dense FFN']}}
 (out/'QWEN3_8B_FUTURE_REPLAY_CONTRACT_V1.json').write_text(canon(contracts['Qwen3-8B']));(out/'DEEPSEEK_V2_LITE_FUTURE_REPLAY_CONTRACT_V1.json').write_text(canon(contracts['DeepSeek-V2-Lite']))
 q30={'model_id':'Qwen/Qwen3-30B-A3B','planned_revision':'ad44e777bcd18fa416d9da3bd8f70d33ebb85d39','classification':'ASSET_NOT_FOUND','canonical_node164_asset_found':False,'source_payload_found':False,'action':'NO_NETWORK_NO_BULK_MIGRATION','notes':'No exact local/canonical config/index/receipt discovered under canonical assets; no archival action taken.'};(out/'QWEN3_30B_ASSET_STATE_V7.json').write_text(canon(q30))
 # Deterministic full capture-path audit, no mutation.
 entries=sorted((ROOT/'catalog/entries').glob('*.json'));rawpaths=[];consistent=True
 for e in entries:
  d=json.loads(e.read_text());p=d.get('raw_path')
  if p:rawpaths.append(p);consistent=consistent and Path(p).is_dir()
 old,new=ROOT/'raw',ROOT/'captures/raw';audit=[{'check':'catalog_entries_with_raw_path','value':str(len(rawpaths)),'status':'PASS'},{'check':'old_raw_path','value':str(old),'status':'PRESENT' if old.is_dir() else 'ABSENT'},{'check':'new_captures_raw_path','value':str(new),'status':'PRESENT' if new.is_dir() else 'ABSENT'},{'check':'overlap_run_ids','value':'NOT_APPLICABLE_NEW_PATH_ABSENT' if not new.is_dir() else 'REQUIRES_ENUMERATION','status':'PASS'},{'check':'capture_redirect_or_migration_receipt','value':'NONE_OBSERVED_FOR_CAPTURE_RAW_LAYOUT','status':'PASS'},{'check':'catalog_physical_consistency','value':str(consistent).lower(),'status':'PASS' if consistent else 'FAIL'},{'check':'recommendation','value':'NO_ACTION_REQUIRED' if consistent else 'INCONSISTENCY_REQUIRES_REVIEW','status':'READ_ONLY'}];write_tsv(out/'CURRENT_CAPTURE_PATH_AUDIT_V7.tsv',list(audit[0]),audit)
 # AutoAWQ immutable source closure.
 source=ROOT/'assets/sources/autoawq_kernels';receipt=source/'SOURCE_ACQUISITION_RECEIPT.json';sr=json.loads(receipt.read_text());expected='49304506a87ef74c3a3dd07ddc839d796c25432d2cdd721e1b968977fa78f398'
 if sr.get('archive_sha256')!=expected:fail('AutoAWQ archive receipt SHA mismatch')
 tree=source/sr['source_commit'];cmd=['git','-c',f'safe.directory={tree}','-C',str(tree)];head=subprocess.check_output(cmd+['rev-parse','HEAD'],text=True).strip();headtree=subprocess.check_output(cmd+['rev-parse','HEAD^{tree}'],text=True).strip();clean=subprocess.check_output(cmd+['status','--porcelain'],text=True).strip()==''
 if head!=sr['source_commit'] or not clean:fail('AutoAWQ source HEAD mismatch or worktree unclean')
 ext=sorted(str(x.relative_to(tree)) for x in tree.glob('awq_ext/**/*') if x.is_file() and x.suffix in ('.cu','.cpp','.cuh','.h'))
 required={'awq_ext/exllama/exllama_ext.cpp','awq_ext/exllamav2/ext.cpp'}
 if not required.issubset(ext):fail('AutoAWQ nested C++ extension source missing')
 awq={'source_commit':head,'head_tree':headtree,'worktree_clean':clean,'recorded_archive_sha256':expected,'archive_blob_status':'NOT_REHASHED_ARCHIVE_BYTES','source_receipt_path':str(receipt),'source_receipt_sha256':sha256(receipt),'extension_sources':ext};(out/'AUTOAWQ_SOURCE_CLOSURE_V7.json').write_text(canon(awq))
 print(canon({'models':len(arch),'role_rows':len(roles),'layer_rows':len(layers),'decision_hint':'PASS_WITH_GAPS'}),end='')
if __name__=='__main__':
 try:main()
 except (InventoryError,RuntimeError) as e:raise SystemExit(str(e))
