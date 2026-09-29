#!/usr/bin/env python3
import csv,hashlib,json,subprocess
from pathlib import Path
COORD='bd988aeb570708e5a41bab45433e9e49eac53c9a';OUT='docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_CONSUMER_174NEW_V1'
AUTH={'grouped_strong_baseline':'e7855278076c7e0360d39b18424cc8f048f51da5','crossm_causal':'2113422f7e6b7e5a851469511d26a9ddf7123d4e','threshold':'6d226cd99946d3bd7b41c5ee005285183efbb915','lr09':'38d4df40b615625c15d1843a69a23eb954ac0bef'}
RAW=['M','split','raw_source','n','min_ms','median_ms','max_ms','mean_ms','cv','gemm_duration_ns','reduction_duration_ns','reduction_dram_bytes','l2_read_hit_sectors','l2_read_miss_sectors','l2_read_hit_fraction','gemm_dram_bytes','gemm_grid','cta_per_76sm','correctness','status']
SWEEP=['M','mtile_count','split1_cta','split8_cta','split1_cta_per_sm','split1_median_ms','split8_median_ms','split1_relative_gain','bootstrap_gain_p05','bootstrap_gain_median','bootstrap_gain_p95','split1_hit_fraction','split8_hit_fraction','hit_difference_pp','split1_gemm_dram_bytes','split8_gemm_dram_bytes','split8_reduction_duration_ns','split8_reduction_dram_bytes','interpretation_status']
def b(r,c,p):return subprocess.check_output(['git','show',f'{c}:{p}'],cwd=r)
def sh(x):return hashlib.sha256(x).hexdigest()
def wt(p,f):
 with p.open('w',newline='') as h:csv.DictWriter(h,fieldnames=f,delimiter='\t',lineterminator='\n').writeheader()
def main():
 r=Path.cwd();o=r/OUT;o.mkdir(parents=True,exist_ok=True);subprocess.run(['git','merge-base','--is-ancestor',COORD,'HEAD'],cwd=r,check=True)
 paths={'grouped_strong_baseline':'docs/vm_tlb/review_packs/C16_SPLITK_GROUPED_CTA_BASELINE_CONSUMER_174NEW_V1/FINAL_DECISION.json','crossm_causal':'docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_CONSUMER_174NEW_V1/FINAL_DECISION.json','threshold':'docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_CONSUMER_174NEW_V1/FINAL_DECISION.json','lr09':'docs/vm_tlb/literature_notes/c16/rounds/2026-09-29_LR09_SPLITK_LOCALITY_SCHEDULING_AND_STRONG_BASELINES.md'}
 bind={k:{'commit':c,'path':paths[k],'sha256':sh(b(r,c,paths[k]))} for k,c in AUTH.items()}
 def poll(x):
  z=subprocess.run(['git','ls-remote','--heads','git@github.com:swayhrl/accel-sim-framework.git',x],cwd=r,text=True,capture_output=True,check=True).stdout.strip();return z.split()[0] if z else None
 audit={'schema_version':1,'status':'SCAFFOLD_READY_WAITING_LANE8_LANE7','coordination_head':COORD,'authority_bindings':bind,'lane8_expected_branch':'hrl/c16-grouped-residual-parallelism-prep-174new-v1','lane8_remote_head_observed':poll('hrl/c16-grouped-residual-parallelism-prep-174new-v1'),'lane7_expected_branch':'hrl/c16-grouped-residual-parallelism-native-109-v1','lane7_remote_head_observed':poll('hrl/c16-grouped-residual-parallelism-native-109-v1'),'formal_consumption_started':False,'gpu_used':False,'gpu_lock_requested':False,'lane4_partial_accessed':False};(o/'AUTHORITY_AUDIT.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
 wt(o/'RAW_RECOMPUTE.tsv',RAW);wt(o/'M_SWEEP_COMPARISON.tsv',SWEEP)
 (o/'NCU_RECOMPUTE.json').write_text(json.dumps({'status':'WAITING_FOR_ACCEPTED_PRODUCER_RAW','formulas':{'hit_fraction':'hit/(hit+miss)','cta_per_76sm':'GEMM grid / 76','split1_gain':'1 - split1 median / split8 median'},'split8_reduction':'separate duration and DRAM'},indent=2,sort_keys=True)+'\n')
 (o/'PARALLELISM_INTERPRETATION.md').write_text('# 并行度解释（准备态）\n\n未来比较M1/M16同grid下partial-tile因素，以及M16→M32→M64 split1 CTA从96→192→384时split8收益是否衰减。必须先确认split1 L2 hit保持高位。\n');(o/'RELATED_WORK_POSITIONING.md').write_text('# 文献定位\n\nLR09确认grouped/swizzled locality与Stream-K式parallel decomposition均为已有软件能力。若残余只来自低CTA供给，不能包装成新cache/split机制。\n');(o/'FINAL_DECISION.json').write_text(json.dumps({'schema_version':1,'status':'CONSUMER_SCAFFOLD_READY_WAITING_PRODUCER','new_result_prefilled':False,'future_bootstrap':{'unit':'complete ABBA block','seed':20260929,'resamples':1000,'quantiles':[.05,.5,.95]},'gpu_used':False},indent=2,sort_keys=True)+'\n');(o/'OPEN_ISSUES.md').write_text('# Open issues\n\n- 等待Lane8 gate与Lane7 final/raw。\n- 禁止追加M128/M256、split或GROUP_M扫描。\n');(o/'README.md').write_text('# C16 grouped residual parallelism consumer scaffold\n\n新结果表只有schema；正式消费从raw timing/NCU独立重算。\n')
 files=sorted(x for x in o.iterdir() if x.is_file() and x.name!='SHA256SUMS');(o/'SHA256SUMS').write_text('\n'.join(f'{sh(x.read_bytes())}  {x.name}' for x in files)+'\n')
if __name__=='__main__':main()
