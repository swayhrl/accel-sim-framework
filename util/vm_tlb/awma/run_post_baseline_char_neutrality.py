#!/usr/bin/env python3
import json, os, shutil, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
R=Path('/root/awma_ai_translation_characterization_v1_runtime')
SRC=Path('/root/awma_rtx4080_v1_baseline_promotion_v1_runtime')
def run(target):
 s=SRC/f'ai_{target}_V1_10_80'; d=R/f'neutral_{target}_V1_10_80_OFF'; d.mkdir(parents=True,exist_ok=True)
 if (d/'traces').exists(): shutil.rmtree(d/'traces')
 shutil.copytree(s/'traces',d/'traces',symlinks=True)
 authority=json.loads((s/'command.json').read_text()); cmd=authority['argv']; env=os.environ.copy()
 env.update({k:str(v) for k,v in authority['environment'].items() if v is not None})
 env.pop('GPGPUSIM_READY_APPLICATION_DIAGNOSTICS',None)
 env['LD_LIBRARY_PATH']=f"{R}/src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release:"+env.get('LD_LIBRARY_PATH','')
 (d/'command.json').write_text(json.dumps({'argv':cmd,'environment':{k:env.get(k) for k in sorted(env) if k.startswith('GPGPUSIM_')}},indent=2,sort_keys=True)+'\n')
 (d/'start_utc.txt').write_text(datetime.now(timezone.utc).strftime('%FT%TZ')+'\n'); st=time.monotonic()
 with (d/'run.log').open('w') as out,(d/'run.stderr').open('w') as err: p=subprocess.run(cmd,cwd=d,env=env,stdout=out,stderr=err)
 (d/'rc.txt').write_text(f'{p.returncode}\n'); (d/'wall_seconds.txt').write_text(f'{time.monotonic()-st:.6f}\n'); return p.returncode
with ThreadPoolExecutor(max_workers=2) as pool:
 results=list(pool.map(run,('T0','T2')))
raise SystemExit(0 if results==[0,0] else 1)
