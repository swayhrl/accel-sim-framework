#!/usr/bin/env python3
"""Launcher adaptation only: run accepted Route-B census-only under the GPU lock."""
import fcntl,json,os,re,subprocess,sys
from pathlib import Path
target=json.loads(Path(sys.argv[1]).read_text())
out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=False)
lock=open('/data/c16/locks/c16_gpu_campaign.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
driver=Path(target['driver_path']);
env=os.environ.copy();env.update({'CUDA_INJECTION64_PATH':'/data/c16/awma/storage_sidelane_v1/producer_5143/bin/route_b_5143.so','ROUTE_B_RAW_DIR':str(out/'raw'),'ROUTE_B_FUNCTION_REGEX':re.escape(target['exact_function']),'ROUTE_B_LAUNCH_CENSUS_ONLY':'1','NO_EAGER_LOAD':'0','NVDISASM':'/usr/local/cuda-12.8/bin/nvdisasm','TOOL_VERBOSE':'0','PYTHONUNBUFFERED':'1'})
env['PATH']='/usr/local/cuda-12.8/bin:'+env['PATH']
(out/'TARGET.json').write_text(json.dumps(target,indent=2,sort_keys=True)+'\n')
with (out/'stdout.log').open('w') as so,(out/'stderr.log').open('w') as se:
 r=subprocess.run(['/data/c16/env/c16-py310/bin/python',str(driver),*target.get('driver_args',[])],env=env,stdout=so,stderr=se)
(out/'returncode.txt').write_text(str(r.returncode)+'\n')
if r.returncode: raise SystemExit(r.returncode)
