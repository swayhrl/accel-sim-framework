#!/usr/bin/env python3
import csv,hashlib,json,subprocess
from pathlib import Path

COORD='2d1db5b8262f07fa7ebdec6122ac7359fdd86960'
AUTH={'static_footprint':'c72d28b17247f25d0c3613604ab6cab1737666e0','threshold_native':'b17193ff6b3786fd01d5bfe83b5c1a0a03859729','threshold_consumer':'6d226cd99946d3bd7b41c5ee005285183efbb915','l2_read_hit':'915707348617f7a8f432bad7a434a98d78b487c8'}
OUT='docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_CONSUMER_174NEW_V1'
RAW_FIELDS=['K','split','sharing_state','raw_source','n','min_ms','median_ms','max_ms','mean_ms','cv','bootstrap_ratio_p05','bootstrap_ratio_median','bootstrap_ratio_p95','l2_read_hit_sectors','l2_read_miss_sectors','l2_read_hit_fraction','gemm_dram_bytes','reduction_dram_bytes','total_dram_bytes','gemm_grid','reduction_grid','scratch_bytes','correctness','status']
CMP_FIELDS=['K','split','shared_median_ms','per_mtile_median_ms','timing_ratio_per_mtile_shared','timing_delta_ms','shared_l2_hit_fraction','per_mtile_l2_hit_fraction','l2_hit_fraction_delta','shared_l2_miss_sectors','per_mtile_l2_miss_sectors','miss_ratio','shared_gemm_dram_bytes','per_mtile_gemm_dram_bytes','dram_ratio','bootstrap_timing_ratio_p05','bootstrap_timing_ratio_median','bootstrap_timing_ratio_p95','interpretation_status']
def blob(repo,c,p):return subprocess.check_output(['git','show',f'{c}:{p}'],cwd=repo)
def sha(x):return hashlib.sha256(x).hexdigest()
def wt(p,fields):
 with p.open('w',newline='') as f:csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n').writeheader()
def main():
 repo=Path.cwd();out=repo/OUT;out.mkdir(parents=True,exist_ok=True);subprocess.run(['git','merge-base','--is-ancestor',COORD,'HEAD'],cwd=repo,check=True)
 bindings={}
 paths={'static_footprint':('docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_STATIC_AUDIT_174NEW_V1','PER_SPLIT_FOOTPRINT.tsv'),'threshold_native':('docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_NATIVE_109_V1','TIMING_SAMPLES.tsv'),'threshold_consumer':('docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_CONSUMER_174NEW_V1','FINAL_DECISION.json'),'l2_read_hit':('docs/vm_tlb/review_packs/C16_SPLITK_L2_READ_HIT_DIAGNOSTIC_109_V1','L2_READ_HIT_SUMMARY.tsv')}
 for key,c in AUTH.items():
  subprocess.check_call(['git','cat-file','-e',f'{c}^{{commit}}'],cwd=repo);pack,name=paths[key];data=blob(repo,c,f'{pack}/{name}');bindings[key]={'commit':c,'path':f'{pack}/{name}','sha256':sha(data)}
 gate8=subprocess.run(['git','ls-remote','--heads','git@github.com:swayhrl/accel-sim-framework.git','hrl/c16-splitk-crossm-reuse-causal-prep-174new-v1'],cwd=repo,text=True,capture_output=True,check=True).stdout.strip()
 gate7=subprocess.run(['git','ls-remote','--heads','git@github.com:swayhrl/accel-sim-framework.git','hrl/c16-splitk-crossm-reuse-causal-native-109-v1'],cwd=repo,text=True,capture_output=True,check=True).stdout.strip()
 audit={'schema_version':1,'status':'SCAFFOLD_READY_WAITING_LANE8_LANE7','coordination_head':COORD,'authority_bindings':bindings,'lane8_remote_head_observed':gate8.split()[0] if gate8 else None,'lane7_remote_head_observed':gate7.split()[0] if gate7 else None,'formal_consumption_started':False,'required_gate':['Lane8 EARLY_GATE supports execution','Lane7 final commit/tree and SHA closed','GPU lock released','correctness/launch closed','raw timing and NCU rows present'],'gpu_used':False,'gpu_lock_requested':False,'lane4_partial_accessed':False};(out/'AUTHORITY_AUDIT.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
 wt(out/'RAW_RECOMPUTE.tsv',RAW_FIELDS);wt(out/'REUSE_CAUSAL_COMPARISON.tsv',CMP_FIELDS)
 ncu={'schema_version':1,'status':'WAITING_FOR_ACCEPTED_PRODUCER_RAW','recompute_formula':{'hit_fraction':'read_hit_sectors / (read_hit_sectors + read_miss_sectors)','dram_ratio':'PER_MTILE GEMM DRAM / SHARED GEMM DRAM','miss_ratio':'PER_MTILE read misses / SHARED read misses'},'kernel_scope':'GEMM primary; split8 reduction reported separately','claim_boundary':'weight-side address-sharing intervention; no tensor attribution or NVIDIA replacement claim'};(out/'NCU_RECOMPUTE.json').write_text(json.dumps(ncu,indent=2,sort_keys=True)+'\n')
 (out/'MECHANISM_INTERPRETATION.md').write_text('# 机制解释（准备态）\n\n未来只比较同一patched binary下SHARED与PER_MTILE。K2560 split1应检验hit下降/DRAM与timing上升；K3072检验额外损失是否较小；split8检验约95.9%高hit是否依赖跨M地址共享。若不支持，直接降级机制解释，不追加replica扫描。\n')
 (out/'FINAL_DECISION.json').write_text(json.dumps({'schema_version':1,'status':'CONSUMER_SCAFFOLD_READY_WAITING_PRODUCER','scientific_decision_zh':'尚无新因果对照raw，不能判断跨M地址共享是否为高L2 hit的重要来源','future_bootstrap':{'unit':'complete mirror block','seed':20260928,'resamples':1000,'quantiles':[.05,.5,.95]},'new_result_prefilled':False,'gpu_used':False},indent=2,sort_keys=True)+'\n')
 (out/'OPEN_ISSUES.md').write_text('# Open issues\n\n- 等待Lane8 EARLY_GATE与Lane7 final/raw。\n- 若结果不支持，停止并降级解释，不做replica=2/4/8扫描。\n')
 (out/'README.md').write_text('# C16 split-K跨M复用因果consumer scaffold\n\nCPU-only准备态。新结果表只有schema；正式消费必须从Lane7 raw timing/NCU重算。\n')
 files=sorted(p for p in out.iterdir() if p.is_file() and p.name!='SHA256SUMS');(out/'SHA256SUMS').write_text('\n'.join(f'{sha(p.read_bytes())}  {p.name}' for p in files)+'\n')
if __name__=='__main__':main()
