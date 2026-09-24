#!/usr/bin/env python3
"""Launcher-only adaptation for immutable accepted Route-B producer."""
import fcntl,json,os,re,subprocess,sys
from pathlib import Path
t=json.loads(Path(sys.argv[1]).read_text()); mode=sys.argv[2]; out=Path(sys.argv[3]); out.mkdir(parents=True,exist_ok=False)
ledger=Path(t['producer_ledger'])
prefix=f"ROUTEB_CENSUS_LAUNCH grid_launch_id={t['producer_global_navigation']} function="
line=next(x.rstrip('\n') for x in ledger.open(errors='replace') if x.startswith(prefix))
fn=line.split(' function=',1)[1].rsplit(' grid=',1)[0]
if f"grid={t['grid']} block={t['block']}" not in line: raise SystemExit('fresh producer shape mismatch')
raw=out/'raw'; raw.mkdir()
env=os.environ.copy(); env.update({'CUDA_INJECTION64_PATH':'/data/c16/awma/storage_sidelane_v1/producer_5143/bin/route_b_5143.so','ROUTE_B_RAW_DIR':str(raw),'ROUTE_B_FUNCTION_REGEX':re.escape(fn),'ROUTE_B_FUNCTION_OCCURRENCE':str(t['producer_selector_ordinal']),'NO_EAGER_LOAD':'0','NVDISASM':'/usr/local/cuda-12.8/bin/nvdisasm','TOOL_VERBOSE':'0','PYTHONUNBUFFERED':'1'})
env['PATH']='/usr/local/cuda-12.8/bin:'+env['PATH']
if mode=='canary': env['INSTR_END']='8'
(out/'IDENTITY.json').write_text(json.dumps({**t,'producer_demangle':fn,'mode':mode},indent=2,sort_keys=True)+'\n')
lock=open('/data/c16/locks/c16_gpu_campaign.lock','w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
with (out/'stdout.log').open('w') as so,(out/'stderr.log').open('w') as se:
 r=subprocess.run(['/data/c16/env/c16-py310/bin/python',t['driver_path'],*t.get('driver_args',[])],env=env,stdout=so,stderr=se)
(out/'returncode.txt').write_text(str(r.returncode)+'\n')
if r.returncode: raise SystemExit(r.returncode)
