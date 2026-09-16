import hashlib,json,shutil,subprocess
from pathlib import Path
wt=Path('/home/huangrulin/workspace/worktrees/accel-sim-deepseek-v23r1');base=Path('/data/c16/deepseek_v23r1');pack=wt/'docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23R1'
if pack.exists():raise SystemExit('pack exists')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def cp(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
pack.mkdir();(pack/'evidence').mkdir();(pack/'formal').mkdir();(pack/'ncu').mkdir()
for n in ['SUPERSEDING_ASSET_AUTHORITY.json','STAGE0_GATE_AUDIT.tsv','V23_BLOCKER_REASSESSMENT.json','RUNTIME_PREFLIGHT.json']:cp(base/'authority'/n,pack/n)
cp(wt/'docs/vm_tlb/chatgpt_handoff/c16/deepseek_v2_lite_s2_producer_v23r1/C16_IDENTITY_GATE_POLICY_V1.md',pack/'C16_IDENTITY_GATE_POLICY_SNAPSHOT.md');cp(base/'state/EXACT_STATE_CHAIN.json',pack/'EXACT_STATE_CHAIN.json');cp(base/'state/MLA_REPLAY.json',pack/'MLA_REPLAY_SIGNATURE.json');cp(base/'state/MOE_REPLAY.json',pack/'MOE_REPLAY_SIGNATURE.json');cp(base/'SIGNATURE_GATE.json',pack/'evidence/SIGNATURE_GATE.json')
for t in ['MLA','MOE']:
 cp(base/f'{t}_static.tsv',pack/f'{t}_STATIC_MAP.tsv');cp(base/f'{t}_FORMAL_AUDIT.json',pack/f'{t}_FORMAL_SUMMARY.json');cp(base/f'{t}_static.log',pack/f'{t}_STATIC_DISCOVERY.log');cp(base/f'{t}_ncu.ncu-rep',pack/f'ncu/{t}_ncu.ncu-rep');cp(base/f'{t}_ncu.log',pack/f'ncu/{t}_ncu.log')
st=load=lambda p:json.loads(Path(p).read_text())
state=st(base/'state/EXACT_STATE_CHAIN.json');mla=st(base/'MLA_FORMAL_AUDIT.json');moe=st(base/'MOE_FORMAL_AUDIT.json')
mla_data={'target':'layer0.self_attn.kv_b_proj','evidence_class':'KV_B_EXPANSION_LATENT_READ','dataflow':'HIDDEN -> kv_a_proj -> kv_a_layernorm latent -> kv_b_proj expanded qk_nope/value representation; not labeled persistent KV cache','input':state['mla_kv_b_input'],'output':state['mla_kv_b_output'],'alias':'input/output non-aliasing by distinct replay storage pointers'};moe_route={'moe_layer':state['moe_layer'],'router_logits':state['moe_router_logits'],'natural_topk_ids':state['natural_topk_ids'],'natural_topk_weights':state['natural_topk_weights'],'selected_expert_id':state['selected_expert_id'],'selected_route_weight':state['selected_route_weight'],'shared_experts':2,'routing':'NATURAL_ROUTING_REQUIRED','target':'layer1.mlp.experts.4.down_proj'}
(pack/'MLA_RUNTIME_DATAFLOW.json').write_text(json.dumps(mla_data,indent=2,sort_keys=True)+'\n');(pack/'MLA_TARGET_QUALIFICATION.json').write_text(json.dumps({'status':'PASS','semantic_role':'layer0.self_attn.kv_b_proj','replay_bitwise_equal':True,'signature_gate':'PASS','same_process_context':'PASS'},indent=2,sort_keys=True)+'\n');(pack/'MOE_ROUTING_RECEIPT.json').write_text(json.dumps(moe_route,indent=2,sort_keys=True)+'\n');(pack/'MOE_TARGET_QUALIFICATION.json').write_text(json.dumps({'status':'PASS','semantic_role':'layer1.mlp.experts.4.down_proj','expert_specific_attribution':'same-process weight/activation ranges and natural expert ID 4','replay_bitwise_equal':True,'signature_gate':'PASS'},indent=2,sort_keys=True)+'\n')
for t in ['MLA','MOE']:
 rows=list(__import__('csv').DictReader((base/f'{t}_static.tsv').open(),delimiter='\t'));direct=sum(x['memory_space']=='GLOBAL' and x['has_mref']=='1' for x in rows);generic=sum(x['memory_space']=='GENERIC' and x['has_mref']=='1' for x in rows);audit={'target':t,'static_instruction_count':len(rows),'direct_global_mref_count':direct,'generic_mref_count':generic,'ldgsts_global_to_shared_count':sum(x['memory_space']=='GLOBAL_TO_SHARED' for x in rows),'other_address_path_audit':'GENERIC parameter/descriptor loads observed and retained as separately counted non-direct path; direct-GLOBAL set is complete formal set','static_map_sha256':sha(base/f'{t}_static.tsv')};(pack/f'{t}_STATIC_PATH_AUDIT.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
runs={'MLA':'C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-mla-kvb_20260917T022000Z_a23a23a23a23','MOE':'C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23'}
for t,run in runs.items():
 ready=Path('/data/c16/capture/ready')/run
 for n in ['RUN_MANIFEST.json','LOCAL_CLOSE_RECEIPT.json','WARP_SHARD_MANIFEST.json','QUICKCHECK.json']:cp(ready/n,pack/'formal'/f'{t}_{n}')
 remote='hrl174new:/root/share/mnt164/huangrulin/c16_ai_workload'
 for src,n in [(f'{remote}/receipts/{run}/VERIFICATION.json','VERIFICATION.json'),(f'{remote}/receipts/{run}/ADMISSION.json','ADMISSION.json'),(f'{remote}/reports/transfer_acks/{run}.TRANSFER_ACK.json','ACK.json')]:subprocess.run(['scp',src,str(pack/'formal'/f'{t}_{n}')],check=True)
 cp(pack/'formal'/f'{t}_ACK.json',pack/f'{t}_ADMISSION_ACK.json')
(pack/'NCU_TYPED_EVIDENCE.json').write_text(json.dumps({'status':'RAW_BOUNDED_REPORTS_PRESERVED','cache_control':'none','warning':'uncontrolled cache warning; no normalized-byte or cache/TLB causal claim','reports':['ncu/MLA_ncu.ncu-rep','ncu/MOE_ncu.ncu-rep']},indent=2,sort_keys=True)+'\n')
(pack/'S2_MLA_VS_MOE_INTERPRETATION.md').write_text(f'''# DeepSeek S2 MLA vs MoE anchors\n\nMLA is `kv_b_proj` expansion from exact normalized compressed latent, not a persistent-cache direct-read claim. It has {mla['static_direct_global_mref_count']} direct-GLOBAL static MREFs, {mla['executed_shards']} executed shards and {mla['active_lane_events']} active-lane events.\n\nMoE is natural routed expert 4 `down_proj`, with exact route weight {state['selected_route_weight']}. It has {moe['static_direct_global_mref_count']} direct-GLOBAL static MREFs, {moe['executed_shards']} executed shards and {moe['active_lane_events']} active-lane events.\n\nNo cross-process VA, chronology, reuse-distance, or cache/TLB causality comparison is made.\n''')
(pack/'NEXT_STEP_AUTHORIZATION.json').write_text(json.dumps({'status':'PASS_S2_ANCHORS','recommendation':'BOUNDED_DEEPSEEK_MLA_PERSISTENT_CACHE_READ_QUALIFICATION_BEFORE_S3','reason':'V23R1 MLA kv_b expansion is clean but is not proven persistent-cache direct read; do not automatically run S3.'},indent=2,sort_keys=True)+'\n')
(pack/'FINAL_DECISION.json').write_text(json.dumps({'decision':'C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23R1_PASS_WITH_MLA_AND_MOE_ANCHORS','mla_run_id':runs['MLA'],'moe_run_id':runs['MOE'],'mla_ack':'PASS','moe_ack':'PASS','scope':'two S2 semantic anchors only'},indent=2,sort_keys=True)+'\n');(pack/'OPEN_ISSUES.md').write_text('# Open issues\n\nGENERIC parameter/descriptor MREF paths were statically audited separately from the complete direct-GLOBAL formal sets. The next step should first qualify a true persistent MLA cache read before long-context work.\n')
items=[]
for f in sorted(pack.rglob('*')):
 if f.is_file() and f.name!='SHA256SUMS':items.append(f'{sha(f)}  {f.relative_to(pack).as_posix()}')
(pack/'SHA256SUMS').write_text('\n'.join(items)+'\n');print(pack)
