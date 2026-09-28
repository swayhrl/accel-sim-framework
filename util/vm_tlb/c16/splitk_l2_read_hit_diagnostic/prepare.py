#!/usr/bin/env python3
"""CPU-only NCU metric selection and authority freeze."""
import argparse,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path

HIT='lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum'
MISS='lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum'
CROSS=['l1tex__t_bytes.sum','lts__t_bytes.sum','dram__bytes.sum','gpu__time_duration.sum']
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def atomic(path,value):
 tmp=path.with_name(path.name+'.tmp');tmp.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');tmp.replace(path)
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--root',type=Path,default=Path('/data/c16/splitk_l2_read_hit_diagnostic_v1'));p.add_argument('--ncu',default='/opt/nvidia/nsight-compute/2025.1.1/target/linux-desktop-glibc_2_11_3-x64/ncu');a=p.parse_args()
 if 'torch' in sys.modules:raise RuntimeError('CPU stage imported torch')
 if a.root.exists():raise RuntimeError(f'root exists {a.root}')
 version=subprocess.check_output([a.ncu,'--version'],text=True);query=subprocess.check_output([a.ncu,'--query-metrics','--query-metrics-mode','suffix','--chips','ad103','--metrics',HIT.removesuffix('.sum')+','+MISS.removesuffix('.sum')],text=True)
 for name,phrase in ((HIT,'reads that hit'),(MISS,'reads that missed')):
  if name not in query or phrase not in query:raise RuntimeError(f'metric semantics unavailable {name}')
 run_id='C16R_splitk-l2-read-hit-diagnostic-v1_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run=a.root/run_id;raw=run/'raw';raw.mkdir(parents=True);(a.root/'ACTIVE_RUN_ID').write_text(run_id+'\n');(raw/'NCU_VERSION.txt').write_text(version);(raw/'NCU_QUERY_SELECTED_SUFFIX.txt').write_text(query)
 pack=a.repo/'docs/vm_tlb/review_packs/C16_SPLITK_L2_READ_HIT_DIAGNOSTIC_109_V1';pack.mkdir(parents=True);(pack/'NCU_QUERY_SELECTED_SUFFIX.txt').write_text(query)
 threshold='b17193ff6b3786fd01d5bfe83b5c1a0a03859729';static='c72d28b17247f25d0c3613604ab6cab1737666e0';coord='659a12c2576580e0ad1bd2be0401fe21dd26f624'
 authority={'status':'PASS','coordination_commit':coord,'threshold_producer_final':threshold,'static_audit_final':static,'threshold_pack':'docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_NATIVE_109_V1','accepted_binaries':{'A':{'path':'/data/c16/env/c16-awq-v6/lib/python3.10/site-packages/awq_ext.cpython-310-x86_64-linux-gnu.so','sha256':'9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7'},'B':{'path':'/data/c16/e1_lowbit_splitk_native_ab_v1/build/lib/awq_split1_ext.cpython-310-x86_64-linux-gnu.so','sha256':'1aa8db13f5fd10651aa4241f58200e3a7075214d34cca4d70fbcbe7cbbc07887'}},'synthetic_version':'GPT3_SHAPE_SYNTH_V1','fixed':{'M':256,'N':49152,'K':[2048,2560,3072,4096],'split':[1,8],'state':'WARM_SAME_ARM'},'lane4_partial_accessed':False}
 for x in authority['accepted_binaries'].values():
  if sha(Path(x['path']))!=x['sha256']:raise RuntimeError('binary mismatch')
 selection={'status':'METRIC_SELECTION_PASS_GPU_AUTHORIZED','ncu_version':version.strip().splitlines()[-1],'chip':'ad103 (RTX4080/SM89)','query_command':[a.ncu,'--query-metrics','--query-metrics-mode','suffix','--chips','ad103','--metrics',HIT.removesuffix('.sum')+','+MISS.removesuffix('.sum')],'query_output_sha256':sha(raw/'NCU_QUERY_SELECTED_SUFFIX.txt'),'candidates':[{'metric':HIT,'unit':'sector','semantics':'# of LTS sectors from unit TEX for reads that hit'},{'metric':MISS,'unit':'sector','semantics':'# of LTS sectors from unit TEX for reads that missed'}],'selected_metrics':[HIT,MISS],'cross_check_metrics':CROSS,'derived_read_hit_fraction':'hit/(hit+miss)','scope':'per selected kernel row; srcunit TEX op_read L2 lookup behavior','not_tensor_attribution':True,'decision_rule':'capacity-knee directionally consistent only if K2560->3072 B GEMM hit fraction decreases and miss sectors increase, while absolute A GEMM hit-fraction change is smaller; no causal significance threshold','cuda_imported':False,'gpu_lock_requested':False}
 atomic(pack/'AUTHORITY.json',authority);atomic(pack/'METRIC_SELECTION.json',selection);atomic(raw/'AUTHORITY.json',authority);atomic(raw/'METRIC_SELECTION.json',selection);(pack/'README.md').write_text(f'# Split-K L2 read-hit diagnostic\n\nRUN_ID: `{run_id}`\n\nCPU metric selection PASS; GPU execution authorized only for eight fixed profiles.\n')
 print(json.dumps({'status':selection['status'],'run_id':run_id,'metrics':selection['selected_metrics']}))
if __name__=='__main__':main()
