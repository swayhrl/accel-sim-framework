#!/usr/bin/env python3
import argparse,hashlib,json,subprocess,time,gzip
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--full-top',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);repo=Path(__file__).resolve().parents[3];tb=repo/'rtl/ep_l2/tb/ep_l2_slice_tb.sv';filelist='rtl/ep_l2/flow/full_slice_filelist.f' if a.full_top else 'rtl/ep_l2/flow/filelist.f';files=[repo/n for n in (repo/filelist).read_text().splitlines() if n]
result=[]
for label,mode,gen in [('B16',0,32),('UNIFIED',1,32),('S64',2,32),('GENERATION_EXHAUSTION',0,3)]:
 vvp=a.out/(label+'.vvp');cmd=['iverilog','-g2012','-Wall','-s','ep_l2_slice_tb','-P',f'ep_l2_slice_tb.MODE={mode}','-P',f'ep_l2_slice_tb.GEN_W={gen}','-o',str(vvp),'-f',filelist,str(tb)]+(['-DEP_L2_FULL_TOP'] if a.full_top else [])
 with (a.out/(label+'-compile.log')).open('w') as f:subprocess.run(cmd,cwd=repo,stdout=f,stderr=subprocess.STDOUT,check=True)
 with (a.out/(label+'-run.log')).open('w') as f:r=subprocess.run(['vvp',str(vvp)],cwd=repo,stdout=f,stderr=subprocess.STDOUT,timeout=90)
 blob=vvp.read_bytes();archive=vvp.with_suffix('.vvp.gz');archive.write_bytes(gzip.compress(blob,6,mtime=0));assert gzip.decompress(archive.read_bytes())==blob
 row={'full_synthesizable_top':a.full_top,'mode':mode,'GEN_W':gen,'compile_command':cmd,'returncode':r.returncode,'binary_sha256':hashlib.sha256(blob).hexdigest(),'exact_binary_archive':str(archive),'stimulus_sha256':hashlib.sha256(tb.read_bytes()).hexdigest(),'RTL_sha256':{str(n.relative_to(repo)):hashlib.sha256(n.read_bytes()).hexdigest() for n in files}};result.append(row);(a.out/'FUNCTIONAL_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');assert r.returncode==0, label;vvp.unlink();print(label,'PASS',flush=True)
