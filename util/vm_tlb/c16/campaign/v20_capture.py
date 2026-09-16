import csv,os,subprocess
from pathlib import Path

scenario=os.environ['C16_V20_SCENARIO']
label=os.environ.get('C16_V20_CAPTURE_LABEL',scenario)
base=Path('/data/c16/qwen3_runtime_v14/v20')
static=base/'V20_repeatk_static.tsv'
root=base/f'{label}_formal_capture'
tool='/data/c16/qwen3_runtime_v14/v20/tools/v20_warp_regsource.so'
fn='_ZN2at6native18elementwise_kernelILi128ELi4EZNS0_22gpu_kernel_impl_nocastIZZZNS0_23direct_copy_kernel_cudaERNS_18TensorIteratorBaseEENKUlvE1_clEvENKUlvE10_clEvEUlN3c108BFloat16EE_EEvS4_RKT_EUliE_EEviT1_'
rows=list(csv.DictReader(static.open(),delimiter='\t'))
indices=[r['nvbit_static_index'] for r in rows if r['memory_space']=='GLOBAL' and r['has_mref']=='1']
load_register_lo={'237':'4','475':'4','713':'4','950':'2'}
if root.exists():raise SystemExit(f'capture root exists: {root}')
root.mkdir()
for ordinal,index in enumerate(indices,1):
 d=root/f'mref_{index}';d.mkdir();trace=d/'trace.bin';env=os.environ.copy()
 for key in list(env):
  if key in {'C16_CTA_BEGIN','C16_CTA_END','C16_WARP_FUNCTION','C16_WARP_STATIC','C16_WARP_OUTPUT','C16_WARP_FUNCTION_OCCURRENCE','C16_WARP_CAPACITY','C16_WARP_OPERAND','C16_V20_CONTEXT_OUT','C16_V20_STATIC_MAP'} or 'CTA' in key and key.startswith('C16_'):
   env.pop(key,None)
 env.update({'PATH':'/usr/local/cuda-12.6/bin:'+env.get('PATH',''),'NVDISASM':'nvdisasm','CUDA_INJECTION64_PATH':tool,'C16_WARP_FUNCTION':fn,'C16_WARP_OUTPUT':str(trace),'C16_WARP_STATIC':index,'C16_WARP_FUNCTION_OCCURRENCE':'0','C16_WARP_CAPACITY':'5000000','C16_WARP_OPERAND':'0','C16_V20_CONTEXT_OUT':str(d/'ADDRESS_CONTEXT.json'),'C16_V20_STATIC_MAP':str(static),'C16_V20_SCENARIO':scenario})
 if index in load_register_lo:env['C16_WARP_LOAD_ADDR_LO']=load_register_lo[index]
 p=subprocess.run(['/data/c16/env/c16-qwen3-v14/bin/python','/home/huangrulin/workspace/worktrees/accel-sim-qwen3-v20/util/vm_tlb/c16/campaign/v20_repeatk.py'],env=env,text=True,capture_output=True)
 (d/'stdout.log').write_text(p.stdout);(d/'stderr.log').write_text(p.stderr)
 if p.returncode or not trace.is_file() or 'C16_WARP_TERMINAL' not in p.stdout:raise SystemExit(f'capture failed static={index} rc={p.returncode}')
 print(f'C16_V20_CAPTURE {scenario} {ordinal}/{len(indices)} static={index}',flush=True)
