import csv,os,re,subprocess
from pathlib import Path
base=Path('/data/c16/deepseek_v27');static=base/'QK_static.tsv';root=base/os.environ.get('C16_V27_CAPTURE_ROOT','QK_formal_capture');cap=os.environ.get('C16_V27_CAPACITY','200000');rows=list(csv.DictReader(static.open(),delimiter='\t'));sel=[r for r in rows if r['memory_space']=='GLOBAL' and r['has_mref']=='1'];only=os.environ.get('C16_V27_STATIC_ONLY');sel=[r for r in sel if not only or r['nvbit_static_index'] in set(only.split(','))];fn=sel[0]['function_mangled_name'];tool='/data/c16/qwen3_runtime_v14/v20/tools/v20_warp_regsource.so'
if root.exists():raise SystemExit('root exists')
root.mkdir()
for n,r in enumerate(sel,1):
 i=r['nvbit_static_index'];d=root/f'mref_{i}';d.mkdir();env=os.environ.copy()
 for k in list(env):
  if k.startswith('C16_') or k=='CUDA_INJECTION64_PATH':env.pop(k,None)
 env.update({'PATH':'/usr/local/cuda-12.6/bin:'+env.get('PATH',''),'NVDISASM':'nvdisasm','CUDA_INJECTION64_PATH':tool,'C16_WARP_FUNCTION':fn,'C16_WARP_OUTPUT':str(d/'trace.bin'),'C16_WARP_STATIC':i,'C16_WARP_FUNCTION_OCCURRENCE':'0','C16_WARP_CAPACITY':cap,'C16_WARP_OPERAND':'0','C16_V27_CONTEXT_OUT':str(d/'ADDRESS_CONTEXT.json'),'C16_V27_STATIC_MAP':str(static)})
 if r['is_load']=='1':
  m=re.search(r'\[R(\d+)\.64',r['sass'])
  if not m:raise SystemExit('load reg '+i)
  env['C16_WARP_LOAD_ADDR_LO']=m.group(1)
 p=subprocess.run(['/data/c16/env/c16-qwen3-v14/bin/python','/home/huangrulin/workspace/worktrees/accel-sim-deepseek-v27/util/vm_tlb/c16/campaign/v27_qk_replay.py'],env=env,text=True,capture_output=True);(d/'stdout.log').write_text(p.stdout);(d/'stderr.log').write_text(p.stderr)
 if p.returncode or not (d/'trace.bin').is_file() or 'C16_WARP_TERMINAL' not in p.stdout:raise SystemExit('capture '+i)
 print(f'V27_QK_CAPTURE {n}/{len(sel)} static={i}',flush=True)
