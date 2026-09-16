import hashlib,json,shutil,subprocess
from pathlib import Path
wt=Path('/home/huangrulin/workspace/worktrees/accel-sim-qwen3-v20');base=Path('/data/c16/qwen3_runtime_v14/v20');pack=wt/'docs/vm_tlb/review_packs/C16_QWEN3_S3_KV_SCALING_109_V20'
if pack.exists():raise SystemExit('review pack exists')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def cp(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def load(p):return json.loads(Path(p).read_text())
pack.mkdir();(pack/'evidence').mkdir();(pack/'formal').mkdir();(pack/'ncu').mkdir()
for s in ('S2_TEXT','S3_TEXT'):
 for stem in (f'{s}_kpost_receipt.json',f'{s}_isolated_repeat_receipt.json') :cp(base/stem,pack/'evidence'/stem)
 for stem in (f'{s}_isolated_full.nsys-rep',f'{s}_isolated_full.sqlite',f'{s}_incontext_full.nsys-rep',f'{s}_incontext_full.sqlite'):cp(base/stem,pack/'evidence'/stem)
 for stem in (f'{s}_isolated_ncu.ncu-rep',f'{s}_isolated_ncu.log'):cp(base/stem,pack/'ncu'/stem)
for src,dst in [(base/'v20_signature_gate.json',pack/'evidence'/'SIGNATURE_GATE.json'),(base/'V20_repeatk_static.tsv',pack/'evidence'/'STATIC_MREF_MAP.tsv'),(base/'S2_V20_full_scope_audit.json',pack/'formal'/'S2_FULL_SCOPE_AUDIT.json'),(base/'S3_V20_full_scope_audit.json',pack/'formal'/'S3_FULL_SCOPE_AUDIT.json'),(base/'V20_static_discovery.log',pack/'evidence'/'STATIC_DISCOVERY.log')]:cp(src,dst)
runs={'S2_TEXT':'C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v20-s2-repeat-k_20260916T162000Z_202020202020','S3_TEXT':'C16R_qwen3-8b_s3-text_decode_nvbit-warp-mref-shard_v20-s3-repeat-k_20260916T163000Z_303030303030'}
for s,run in runs.items():
 ready=Path('/data/c16/capture/ready')/run
 for name in ('RUN_MANIFEST.json','LOCAL_CLOSE_RECEIPT.json','WARP_SHARD_MANIFEST.json','QUICKCHECK.json'):cp(ready/name,pack/'formal'/f'{s}_{name}')
 remote=f'hrl174new:/root/share/mnt164/huangrulin/c16_ai_workload'
 for src,name in [(f'{remote}/receipts/{run}/VERIFICATION.json','VERIFICATION.json'),(f'{remote}/receipts/{run}/ADMISSION.json','ADMISSION.json'),(f'{remote}/reports/transfer_acks/{run}.TRANSFER_ACK.json','TRANSFER_ACK.json')]:
  subprocess.run(['scp',src,str(pack/'formal'/f'{s}_{name}')],check=True)
s2,s3=load(base/'S2_V20_full_scope_audit.json'),load(base/'S3_V20_full_scope_audit.json');kr2,kr3=load(base/'S2_TEXT_kpost_receipt.json'),load(base/'S3_TEXT_kpost_receipt.json')
comparison={'schema_version':1,'comparison_scope':'same isolated layer0.self_attn.repeat_kv(K) KV_STORAGE_DIRECT_READ target; fresh V20 full-scope captures only','safe_claims_only':True,'forbidden':['cross-process absolute VA comparison','cross-replay VA union','cross-shard chronology','reuse-distance inference','cache/TLB causality from event scaling'],'S2':{'k_post':kr2['k_post'],'repeat_k':kr2['repeat_k'],'grid_x':s2['expected_grid_x'],'active_lane_events':s2['active_lane_events'],'executed_shards':s2['executed_shards'],'zero_shards':s2['zero_shards'],'static_mref_count':s2['captured_static_shards'],'full_scope_gate':s2['full_scope_gate'],'pages':{k:s2[k] for k in ['aggregate_unique_4k_pages','aggregate_unique_64k_pages','aggregate_unique_2m_pages','aggregate_unique_128b_lines']}},'S3':{'k_post':kr3['k_post'],'repeat_k':kr3['repeat_k'],'grid_x':s3['expected_grid_x'],'active_lane_events':s3['active_lane_events'],'executed_shards':s3['executed_shards'],'zero_shards':s3['zero_shards'],'static_mref_count':s3['captured_static_shards'],'full_scope_gate':s3['full_scope_gate'],'pages':{k:s3[k] for k in ['aggregate_unique_4k_pages','aggregate_unique_64k_pages','aggregate_unique_2m_pages','aggregate_unique_128b_lines']}},'ratios':{'grid_x_s3_over_s2':s3['expected_grid_x']/s2['expected_grid_x'],'active_lane_events_s3_over_s2':s3['active_lane_events']/s2['active_lane_events']}}
(pack/'CONTEXT_SCALING_COMPARISON.json').write_text(json.dumps(comparison,indent=2,sort_keys=True)+'\n')
static={'schema_version':1,'function_mangled':'_ZN2at6native18elementwise_kernelILi128ELi4EZNS0_22gpu_kernel_impl_nocastIZZZNS0_23direct_copy_kernel_cudaERNS_18TensorIteratorBaseEENKUlvE1_clEvENKUlvE10_clEvEUlN3c108BFloat16EE_EEvS4_RKT_EUliE_EEviT1_','static_map_sha256':sha(base/'V20_repeatk_static.tsv'),'static_instruction_rows':968,'direct_global_mref_count':8,'ldgsts_global_to_shared_count':0,'other_address_bearing_special_path_count':0,'libtorch_cuda_sha256':'761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a','audit':'register-pair capture is used for LDG source addresses; MREF capture remains used for STG destination addresses'}
(pack/'STATIC_PATH_AUDIT.json').write_text(json.dumps(static,indent=2,sort_keys=True)+'\n')
build={'schema_version':1,'nvbit':'1.7.5','nvcc':'12.6','tool':'v20_warp_regsource.so','tool_sha256':sha(base/'tools/v20_warp_regsource.so'),'tool_source_sha256':sha(wt/'util/vm_tlb/c16/campaign/v20_warp_tool.cu'),'inject_source_sha256':sha(wt/'util/vm_tlb/c16/campaign/v20_warp_inject.cu'),'static_discovery_tool_sha256':sha(base/'tools/v20_static_discovery.so'),'static_discovery_source_sha256':sha(wt/'util/vm_tlb/c16/campaign/v20_static_discovery.cu'),'libtorch_cuda_sha256':static['libtorch_cuda_sha256'],'load_address_register_pairs':{'237':'R4:R5','475':'R4:R5','713':'R4:R5','950':'R2:R3'}}
(pack/'PRODUCER_BUILD_RECEIPT.json').write_text(json.dumps(build,indent=2,sort_keys=True)+'\n')
(pack/'NCU_TYPED_EVIDENCE.json').write_text(json.dumps({'schema_version':1,'status':'PRESERVED_BOUNDED_NATIVE_REPORTS','reports':[{'scenario':s,'report':f'ncu/{s}_isolated_ncu.ncu-rep','log':f'ncu/{s}_isolated_ncu.log','cache_control':'none','warning':'uncontrolled GPU caches; no normalized byte claim or cache/TLB causal claim'} for s in ('S2_TEXT','S3_TEXT')]},indent=2,sort_keys=True)+'\n')
(pack/'README.md').write_text('# C16 Qwen3 S3 KV scaling V20\n\nDecision: `C16_QWEN3_S3_KV_SCALING_109_V20_PASS`. This is scoped strictly to layer0 first-decode `self_attn.repeat_kv(K)` as `KV_STORAGE_DIRECT_READ` materialization.\n\nFresh V20 isolated replays and full-scope captures were used for both S2 and S3; V18R2/V19 history was not used as the scaling baseline.\n')
(pack/'FINAL_DECISION.md').write_text('# Final decision\n\n`C16_QWEN3_S3_KV_SCALING_109_V20_PASS`\n\nBoth exact S2_TEXT B1/T2048/D32 and S3_TEXT B1/T8192/D16 first-decode K-post states passed isolated replay bitwise equivalence, in-context signature equivalence, fresh static/path closure, full CTA/address-membership gates, complete formal capture, serial Pipeline admission and positive ACK.\n\nThe result applies only to K-cache storage read / repeat-K materialization. QK/AV are not called direct KV-cache reads.\n')
(pack/'OPEN_ISSUES.md').write_text('# Open issues\n\nNCU reports are preserved with native metric representation and uncontrolled-cache warnings. This pack makes no cache/TLB causal statement. Cross-process virtual-address comparisons, chronology, and reuse distance are prohibited.\n')
(pack/'SHA256SUMS').write_text('')
items=[]
for p in sorted(pack.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS':items.append(f'{sha(p)}  {p.relative_to(pack).as_posix()}')
(pack/'SHA256SUMS').write_text('\n'.join(items)+'\n')
print(pack)
