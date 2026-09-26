#!/usr/bin/env python3
import argparse,fcntl,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--driver',type=Path,required=True);p.add_argument('driver_args',nargs=argparse.REMAINDER);a=p.parse_args();a.run.mkdir(parents=True,exist_ok=False)
lock=open('/data/c16/locks/c16_gpu_campaign.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
driver_args=a.driver_args[1:] if a.driver_args and a.driver_args[0]=='--' else a.driver_args
cmd=['nsys','profile','--force-overwrite=true','--trace=cuda,nvtx','--sample=none','--output',str(a.run/'atlas'),'/data/c16/env/c16-py310/bin/python',str(a.driver),*driver_args]
with (a.run/'driver.stdout').open('w') as so,(a.run/'driver.stderr').open('w') as se:r=subprocess.run(cmd,stdout=so,stderr=se)
(a.run/'returncode.txt').write_text(str(r.returncode)+'\n')
if r.returncode: raise SystemExit(r.returncode)
subprocess.run(['nsys','export','--type','sqlite','--force-overwrite','true','--output',str(a.run/'atlas.sqlite'),str(a.run/'atlas.nsys-rep')],check=True,stdout=subprocess.DEVNULL)
