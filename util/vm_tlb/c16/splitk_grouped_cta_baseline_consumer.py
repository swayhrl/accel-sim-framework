#!/usr/bin/env python3
import csv,hashlib,json,subprocess
from pathlib import Path
COORD='8e3505e932534fe5cdb334d68862c2bc9355702b';OUT='docs/vm_tlb/review_packs/C16_SPLITK_GROUPED_CTA_BASELINE_CONSUMER_174NEW_V1'
AUTH={'static_footprint':'c72d28b17247f25d0c3613604ab6cab1737666e0','threshold_consumer':'6d226cd99946d3bd7b41c5ee005285183efbb915','l2_read_hit':'915707348617f7a8f432bad7a434a98d78b487c8','crossm_causal':'2113422f7e6b7e5a851469511d26a9ddf7123d4e','lr09':'38d4df40b615625c15d1843a69a23eb954ac0bef'}
RAW=['K','split','mapping','raw_source','n','min_ms','median_ms','max_ms','mean_ms','cv','l2_read_hit_sectors','l2_read_miss_sectors','l2_read_hit_fraction','gemm_dram_bytes','reduction_dram_bytes','total_dram_bytes','gemm_grid','reduction_grid','scratch_bytes','correctness','row_calibration_status','status']
CMP=['K','split','row_median_ms','group_median_ms','group_row_timing_ratio','timing_improvement_fraction','row_hit_fraction','group_hit_fraction','hit_delta_pp','row_miss_sectors','group_miss_sectors','miss_ratio','row_gemm_dram_bytes','group_gemm_dram_bytes','dram_ratio','bootstrap_ratio_p05','bootstrap_ratio_median','bootstrap_ratio_p95','interpretation_status']
EQ=['K','mapping','split1_median_ms','split8_median_ms','split1_gain','split1_hit_fraction','split8_hit_fraction','hit_difference_pp','split1_gemm_dram_bytes','split8_gemm_dram_bytes','dram_ratio_split1_split8','conclusion_status']
def bl(repo,c,p):return subprocess.check_output(['git','show',f'{c}:{p}'],cwd=repo)
def sh(x):return hashlib.sha256(x).hexdigest()
def wt(p,f):
 with p.open('w',newline='') as h:csv.DictWriter(h,fieldnames=f,delimiter='\t',lineterminator='\n').writeheader()
def main():
 repo=Path.cwd();out=repo/OUT;out.mkdir(parents=True,exist_ok=True);subprocess.run(['git','merge-base','--is-ancestor',COORD,'HEAD'],cwd=repo,check=True)
 paths={'static_footprint':'docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_STATIC_AUDIT_174NEW_V1/PER_SPLIT_FOOTPRINT.tsv','threshold_consumer':'docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_CONSUMER_174NEW_V1/FINAL_DECISION.json','l2_read_hit':'docs/vm_tlb/review_packs/C16_SPLITK_L2_READ_HIT_DIAGNOSTIC_109_V1/L2_READ_HIT_SUMMARY.tsv','crossm_causal':'docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_CONSUMER_174NEW_V1/FINAL_DECISION.json','lr09':'docs/vm_tlb/literature_notes/c16/rounds/2026-09-29_LR09_SPLITK_LOCALITY_SCHEDULING_AND_STRONG_BASELINES.md'}
 bindings={k:{'commit':c,'path':paths[k],'sha256':sh(bl(repo,c,paths[k]))} for k,c in AUTH.items()}
 def poll(branch):
  x=subprocess.run(['git','ls-remote','--heads','git@github.com:swayhrl/accel-sim-framework.git',branch],cwd=repo,text=True,capture_output=True,check=True).stdout.strip();return x.split()[0] if x else None
 audit={'schema_version':1,'status':'SCAFFOLD_READY_WAITING_LANE8_LANE7','coordination_head':COORD,'authority_bindings':bindings,'lane8_expected_branch':'hrl/c16-splitk-grouped-cta-baseline-prep-174new-v1','lane8_remote_head_observed':poll('hrl/c16-splitk-grouped-cta-baseline-prep-174new-v1'),'lane7_expected_branch':'hrl/c16-splitk-grouped-cta-baseline-native-109-v1','lane7_remote_head_observed':poll('hrl/c16-splitk-grouped-cta-baseline-native-109-v1'),'formal_consumption_started':False,'gpu_used':False,'gpu_lock_requested':False,'lane4_partial_accessed':False};(out/'AUTHORITY_AUDIT.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
 wt(out/'RAW_RECOMPUTE.tsv',RAW);wt(out/'GROUPED_STRONG_BASELINE_COMPARISON.tsv',CMP);wt(out/'EQUAL_MAPPING_SPLIT_COMPARISON.tsv',EQ)
 (out/'NCU_RECOMPUTE.json').write_text(json.dumps({'status':'WAITING_FOR_ACCEPTED_PRODUCER_RAW','formulas':{'hit_fraction':'hit/(hit+miss)','group_row_dram_ratio':'GROUP GEMM DRAM / ROW GEMM DRAM','equal_mapping_split1_gain':'1 - split1_GROUP median / split8_GROUP median'},'kernel_scope':'GEMM primary; split8 reduction separate'},indent=2,sort_keys=True)+'\n')
 (out/'RELATED_WORK_POSITIONING.md').write_text('# 文献定位\n\nLR09已将Triton GROUP_M、CUTLASS/Stream-K式CTA排序与局部性优化定位为已有软件能力。GROUP_M16只能作为强基线，不能作为新机制贡献。\n')
 (out/'SCIENTIFIC_INTERPRETATION.md').write_text('# 科学解释（准备态）\n\n尚无Lane7 raw，不能判断grouped mapping恢复多少reuse或split8是否仍占优。若grouped基本解决问题，必须降级新split机制故事；若不支持，也不追加GROUP_M或split参数扫描。\n')
 (out/'FINAL_DECISION.json').write_text(json.dumps({'schema_version':1,'status':'CONSUMER_SCAFFOLD_READY_WAITING_PRODUCER','new_result_prefilled':False,'future_bootstrap':{'unit':'complete mirror block','seed':20260929,'resamples':1000,'quantiles':[.05,.5,.95]},'gpu_used':False},indent=2,sort_keys=True)+'\n');(out/'OPEN_ISSUES.md').write_text('# Open issues\n\n- 等待Lane8 EARLY_GATE与Lane7 final/raw。\n- 不扫GROUP_M=2/4/8。\n- 若strong baseline解决问题，降级新机制空间。\n');(out/'README.md').write_text('# C16 grouped CTA strong-baseline consumer scaffold\n\n新结果表只有schema；正式消费必须从raw timing/NCU独立重算。\n')
 files=sorted(x for x in out.iterdir() if x.is_file() and x.name!='SHA256SUMS');(out/'SHA256SUMS').write_text('\n'.join(f'{sh(x.read_bytes())}  {x.name}' for x in files)+'\n')
if __name__=='__main__':main()
