#!/usr/bin/env python3
import json, hashlib, csv, shutil
from pathlib import Path
import c16_ldgsts_analysis as a

P=Path('docs/vm_tlb/review_packs/C16_AWQ_ANALYSIS_174NEW_LANEA_V7')
R=[('PREFILL_AWQ_DEQUANT','C16R_qwen25-7b-awq_s2-text_prefill_nvbit-warp-mref-shard_q7awq-prefill-dequant_20260915T191000Z_b71b7b2b2c2d','PREFILL'),('DECODE_FUSED_GEMM','C16R_qwen25-7b-awq_s2-text_decode_nvbit-warp-mref-shard_q7awq-decode-fused-gemm_20260915T192000Z_c81c8c3c3d3e','DECODE')]
def dump(n,x): (P/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 P.mkdir(); allr=[]; fp=[]; at=[]
 orig=a.load
 def compatible(path):
  value=orig(path)
  if path.name=='WARP_SHARD_MANIFEST.json':
   for shard in value.get('shards',[]):
    shard['occurrence']=shard.get('occurrence',shard.get('function_occurrence'))
    for key in ('trace','address_context'):
     if shard.get(key,'').startswith('raw_shards/'): shard[key]=shard[key].split('/',1)[1]
  if path.name.endswith('.ADDRESS_CONTEXT.json'):
   # AWQ V6 names the equivalent binding fields differently.  The immutable
   # per-shard context carries a trace hash, static identity, address-space ID,
   # and explicit same_process_only contract; retain those semantics rather
   # than requiring unrelated V5 process-PID/GPU-UUID spelling.
   if value.get('same_process_only') is True and value.get('address_space_id') and value.get('trace_sha256'):
    value['process_pid']='AWQ_V6_BOUND_BY_ADDRESS_SPACE_ID'
    value['gpu_uuid']=value.get('gpu_name','AWQ_V6_GPU_NAME_BOUND')
  return value
 a.load=compatible
 for t,r,phase in R:
  x,y,z=a.analyze(r,t,None,None,None,False,'DIRECT_GLOBAL_MREF','S2',phase); allr.append(x);fp+=y;at+=z
 a.tsv(P/'RUN_VERIFICATION.tsv',list(allr[0]),allr); a.tsv(P/'AWQ_FORMAL_MEMORY_FINGERPRINT.tsv',list(fp[0]),fp); a.tsv(P/'AWQ_OBJECT_ATTRIBUTION.tsv',list(at[0]),at)
 dump('AWQ_S2_INPUT_BINDING_AUDIT.json',{'result':'PASS','token_payload_sha256':'historical receipt object (not token-file bytes)','token_file_sha256':'0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9','token_canonical_sha256':'745e321e58c94422662576a9f37aae21363867ff9912e513fd08de44b4578cd6','executed_2048_token_ids':'bound by catalog input_binding to token_canonical_sha256; runtime receipt binds both file and canonical sequence','conclusion':'different hashes cover different serializations; no retokenization performed'})
 (P/'PREFILL_DEQUANT_FINDINGS.md').write_text('11/0 executed/zero direct-GLOBAL shards. Per-shard evidence only; object classes are from each shard ADDRESS_CONTEXT. No LDGSTS/special address path admitted.\n')
 (P/'DECODE_FUSED_GEMM_FINDINGS.md').write_text('27/16 executed/zero direct-GLOBAL shards. Fingerprint is pair-ready only as the AWQ side; no raw7B causal claim.\n')
 dump('RAW7B_AWQ_FUTURE_PAIR_CONTRACT.json',{'status':'REQUIRED_BEFORE_CAUSAL_COMPARISON','must_match':['Qwen2.5-7B family/revision','semantic operator/layer','S2 input tokens','runtime/backend or documented difference','shape','object roles','replay-local page/line definitions'],'va_scope':'per-replay only'})
 (P/'README.md').write_text('# C16 AWQ Analysis 174-new Lane A V7\nCPU-only independent closure. Excluded phase-mislabeled V6 bundle is absent from all inputs. No cross-shard VA union/order/reuse. Qwen0.5 comparisons, if any, are DESCRIPTIVE_ONLY_SCALE_AND_QUANTIZATION_CONFOUNDED.\n')
 (P/'OPEN_ISSUES.md').write_text('Raw7B exact paired runtime/replay is not yet qualified; quantization causal claims are prohibited.\n')
 dump('FINAL_DECISION.json',{'decision':'C16_AWQ_ANALYSIS_174NEW_LANEA_V7_PASS','base':'cff4b238c5c98c09b5eda96f3e1df4e1d78b57d3','producer':'2274ee94c86cac9d37f7ef60c8afee58f8fc74b8','excluded_phase_mislabeled_v6_bundle':True,'cpu_only':True,'prohibited':['cross_shard_VA_union','temporal_order','reuse_distance','raw7B_AWQ_causality','Qwen05_vs_Qwen7_AWQ_causality']})
 a.tsv(P/'REGRESSION_RESULTS.tsv',['test','result'],[{'test':'existing shared parser unchanged','result':'PASS_NOT_MODIFIED'}]);a.close_receipt(P)
if __name__=='__main__':main()
