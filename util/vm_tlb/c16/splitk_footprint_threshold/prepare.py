#!/usr/bin/env python3
"""CPU-only node109 preparation; never imports torch or a CUDA extension."""
import argparse,csv,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
from contracts import *

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def atomic(path,value):
 tmp=path.with_name(path.name+'.tmp');tmp.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');tmp.replace(path)
def tsv(path,rows):
 with open(path,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--root',type=Path,default=Path('/data/c16/splitk_footprint_threshold_native_v1'));a=p.parse_args()
 if 'torch' in sys.modules:raise RuntimeError('torch imported in CPU prep')
 if a.root.exists():raise RuntimeError(f'root exists {a.root}')
 if sha(Path(A_PATH))!=A_SHA or sha(Path(B_PATH))!=B_SHA:raise RuntimeError('binary hash')
 if tiny_reference()['reference_sha256']!=TINY_SHA:raise RuntimeError('tiny reference')
 run_id='C16R_splitk-footprint-threshold-native-v1_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run=a.root/run_id;raw=run/'raw';raw.mkdir(parents=True);(a.root/'ACTIVE_RUN_ID').write_text(run_id+'\n')
 pack=a.repo/'docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_NATIVE_109_V1';pack.mkdir(parents=True)
 src=[];names=('contracts.py','test_contracts.py','runner.py','validate_launch.py','prepare.py','run_locked.sh','analyze.py','reseal.py')
 for name in names:
  q=a.repo/'util/vm_tlb/c16/splitk_footprint_threshold'/name;src.append({'path':str(q.relative_to(a.repo)),'sha256':sha(q),'bytes':q.stat().st_size})
 endpoint='1544018d967003c2825eb69f56440f641f5f5581';ep_files={}
 for name in ('SOURCE_AND_AUTHORITY.json','W4_TIMING_SUMMARY.tsv','W4_STATE_INTERACTION.tsv','NCU_SUMMARY.json'):
  data=subprocess.check_output(['git','-C',str(a.repo),'show',f'{endpoint}:docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_109_V1/{name}']);ep_files[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
 receipt={'status':'CPU_PREP_COMPLETE_WAITING_STATIC_GATE','goal':'C16_SPLITK_FOOTPRINT_THRESHOLD_NATIVE_109_V1','run_id':run_id,'coordination_head':'f10a40ccd25cf3179a619abe21881fdf19c973a1','endpoint_commit':endpoint,'fixed':{'M':M,'N':N,'K':list(KS),'split':[1,8],'state':'WARM_SAME_ARM','synthetic_version':SYNTH_VERSION},'accepted_binaries':{'A':{'path':A_PATH,'sha256':sha(Path(A_PATH))},'B':{'path':B_PATH,'sha256':sha(Path(B_PATH))}},'tiny_reference':tiny_reference(),'sources':src,'endpoint_files':ep_files,'cuda_imported':False,'gpu_lock_requested':False,'lane4_partial_accessed':False}
 manifest={'status':'CPU_PREP_COMPLETE_WAITING_STATIC_GATE','run_id':run_id,'cells':[{"point":point_name(k),"K":k,"arm":arm,"state":"WARM_SAME_ARM"} for k in KS for arm in ('A','B')],'timing':{'global_warmups_per_arm':10,'blocks':25,'order':['A','B','B','A'],'same_arm_warmups_per_sample':2,'samples_per_arm':50},'ncu':{'profiles':8,'metrics':['l1tex__t_bytes.sum','lts__t_bytes.sum','dram__bytes.sum','gpu__time_duration.sum'],'replay_mode':'application','cache_control':'none'},'source_files':src,'gate_status':'PENDING'}
 atomic(raw/'CPU_PREP_RECEIPT.json',receipt);atomic(pack/'CPU_PREP_RECEIPT.json',receipt);atomic(pack/'SOURCE_AND_RUN_MANIFEST.json',manifest);tsv(pack/'EXPECTED_LAUNCH_SCRATCH.tsv',expected_rows());tsv(pack/'K_FOOTPRINT_PRELIMINARY.tsv',footprint_rows());(pack/'README.md').write_text(f'# Split-K footprint threshold native prep\n\nRUN_ID: `{run_id}`\n\nCPU prep complete; GPU remains forbidden until Lane8 STATIC_GATE is supported and bound.\n')
 print(json.dumps({'status':receipt['status'],'run_id':run_id,'run':str(run)}))
if __name__=='__main__':main()
