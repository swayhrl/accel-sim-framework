import csv,os,re,subprocess
from pathlib import Path
target=os.environ['C16_V23R1_TARGET'];base=Path('/data/c16/deepseek_v23r1');static=base/f'{target}_static.tsv';root=base/f'{target}_formal_capture'
tool='/data/c16/qwen3_runtime_v14/v20/tools/v20_warp_regsource.so';rows=list(csv.DictReader(static.open(),delimiter='\t'));selected=[r for r in rows if r['memory_space']=='GLOBAL' and r['has_mref']=='1'];fn=selected[0]['function_mangled_name']
if root.exists():raise SystemExit('capture root exists')
root.mkdir()
for n,row in enumerate(selected,1):
 i=row['nvbit_static_index'];d=root/f'mref_{i}';d.mkdir();env=os.environ.copy()
 for k in list(env):
  if k.startswith('C16_') or k=='CUDA_INJECTION64_PATH':env.pop(k,None)
 env.update({'PATH':'/usr/local/cuda-12.6/bin:'+env.get('PATH',''),'NVDISASM':'nvdisasm','CUDA_INJECTION64_PATH':tool,'C16_WARP_FUNCTION':fn,'C16_WARP_OUTPUT':str(d/'trace.bin'),'C16_WARP_STATIC':i,'C16_WARP_FUNCTION_OCCURRENCE':'0','C16_WARP_CAPACITY':'200000','C16_WARP_OPERAND':'0','C16_V23R1_CONTEXT_OUT':str(d/'ADDRESS_CONTEXT.json'),'C16_V23R1_STATIC_MAP':str(static),'C16_V23R1_TARGET':target})
 if row['is_load']=='1':
  m=re.search(r'\[R(\d+)\.64',row['sass'])
  if not m:raise SystemExit('no source register '+i)
  env['C16_WARP_LOAD_ADDR_LO']=m.group(1)
 p=subprocess.run(['/data/c16/env/c16-qwen3-v14/bin/python','/home/huangrulin/workspace/worktrees/accel-sim-deepseek-v23r1/util/vm_tlb/c16/campaign/v23r1_replay.py'],env=env,text=True,capture_output=True);(d/'stdout.log').write_text(p.stdout);(d/'stderr.log').write_text(p.stderr)
 if p.returncode or not (d/'trace.bin').is_file() or 'C16_WARP_TERMINAL' not in p.stdout:raise SystemExit('capture failed '+i)
 print(f'C16_V23R1_CAPTURE {target} {n}/{len(selected)} static={i}',flush=True)
