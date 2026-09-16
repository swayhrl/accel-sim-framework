import csv,os,subprocess
from pathlib import Path
mp=Path('/data/c16/qwen3_runtime_v14/v18r2_repeatk_static.tsv');root=Path('/data/c16/qwen3_runtime_v14/v18r2_repeatk_capture');tool='/data/c16/results/C16_V5_LDGSTS/tools/c16_ldgsts_operand_sm89.so';fn='_ZN2at6native27unrolled_elementwise_kernelIZZZNS0_23direct_copy_kernel_cudaERNS_18TensorIteratorBaseEENKUlvE1_clEvENKUlvE5_clEvEUlfE_NS_6detail5ArrayIPcLi2EEE23TrivialOffsetCalculatorILi1EjESC_NS0_6memory12LoadWithCastILi1EEENSD_13StoreWithCastILi1EEEEEviT_T0_T1_T2_T3_T4_';idx=[r['nvbit_static_index'] for r in csv.DictReader(mp.open(),delimiter='\t') if r['memory_space']=='GLOBAL' and r['has_mref']=='1'];root.mkdir(parents=True,exist_ok=False)
for n,i in enumerate(idx,1):
 d=root/f'mref_{i}';d.mkdir();t=d/'trace.bin';e=os.environ.copy();e.update({'PATH':'/usr/local/cuda-12.6/bin:'+e['PATH'],'NVDISASM':'nvdisasm','CUDA_INJECTION64_PATH':tool,'C16_WARP_FUNCTION':fn,'C16_WARP_OUTPUT':str(t),'C16_WARP_STATIC':i,'C16_WARP_FUNCTION_OCCURRENCE':'0','C16_WARP_CAPACITY':'5000000','C16_WARP_OPERAND':'0','C16_V18R2_CONTEXT_OUT':str(d/'ADDRESS_CONTEXT.json'),'C16_V18R2_STATIC_MAP':str(mp)})
 p=subprocess.run(['/data/c16/env/c16-qwen3-v14/bin/python','/tmp/v18r2_repeatk.py'],env=e,text=True,capture_output=True);(d/'stdout.log').write_text(p.stdout);(d/'stderr.log').write_text(p.stderr)
 if p.returncode or not t.exists():raise SystemExit(str(i))
 print(n,len(idx),i,flush=True)
