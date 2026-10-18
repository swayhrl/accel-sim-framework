#!/usr/bin/env python3
import argparse,hashlib,json,subprocess,time,gzip
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--resume',action='store_true');p.add_argument('--full-top',action='store_true');p.add_argument('--sim-timeout',type=int,default=90);p.add_argument('--unified-last-physical',action='store_true');a=p.parse_args();
if a.unified_last_physical and not a.full_top:p.error('--unified-last-physical requires --full-top')
# Host wall time only: full1024-Tag gate simulation; no RTL cycle/II change.
wall_timeout=max(a.sim_timeout,2400) if a.unified_last_physical else a.sim_timeout
a.out.mkdir(parents=True,exist_ok=a.resume);repo=Path(__file__).resolve().parents[3];tb=repo/'rtl/ep_l2/tb/ep_l2_slice_tb.sv';filelist='rtl/ep_l2/flow/full_slice_filelist.f' if a.full_top else 'rtl/ep_l2/flow/filelist.f';files=[repo/n for n in (repo/filelist).read_text().splitlines() if n]
result=[]
if a.resume and (a.out/'FUNCTIONAL_RECEIPT.json').exists():
 result=json.loads((a.out/'FUNCTIONAL_RECEIPT.json').read_text())
 for row in result:
  assert row['returncode']==0 and row['full_synthesizable_top']==a.full_top
  assert row['stimulus_sha256']==hashlib.sha256(tb.read_bytes()).hexdigest()
  assert row['RTL_sha256']=={str(n.relative_to(repo)):hashlib.sha256(n.read_bytes()).hexdigest() for n in files}
  with gzip.open(row['exact_binary_archive'],'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['binary_sha256']
cases=[('UNIFIED_LAST_PHYSICAL',1,32)] if a.unified_last_physical else [('B16',0,32),('UNIFIED',1,32),('S64',2,32),('GENERATION_EXHAUSTION',0,3)]
for label,mode,gen in cases:
 if any(row['mode']==mode and row['GEN_W']==gen for row in result):continue
 vvp=a.out/(label+'.vvp')
 if vvp.exists():
  raw=vvp.read_bytes();prior=vvp.with_name(label+'.incomplete-'+hashlib.sha256(raw).hexdigest()[:12]+'.vvp.gz');prior.write_bytes(gzip.compress(raw,6,mtime=0));assert gzip.decompress(prior.read_bytes())==raw;vvp.unlink()
 captured={str(n.relative_to(repo)):hashlib.sha256(n.read_bytes()).hexdigest() for n in files};fixture_sha=hashlib.sha256(tb.read_bytes()).hexdigest();fl_sha=hashlib.sha256((repo/filelist).read_bytes()).hexdigest()
 cmd=['iverilog','-g2012','-Wall','-s','ep_l2_slice_tb','-P',f'ep_l2_slice_tb.MODE={mode}','-P',f'ep_l2_slice_tb.GEN_W={gen}','-o',str(vvp),'-f',filelist,str(tb)]+(['-DEP_L2_FULL_TOP'] if a.full_top else [])+(['-DEP_L2_UNIFIED_LAST_PHYSICAL_ONLY'] if a.unified_last_physical else [])
 with (a.out/(label+'-compile.log')).open('w') as f:subprocess.run(cmd,cwd=repo,stdout=f,stderr=subprocess.STDOUT,check=True)
 with (a.out/(label+'-run.log')).open('w') as f:r=subprocess.run(['stdbuf','-oL','-eL','vvp',str(vvp)],cwd=repo,stdout=f,stderr=subprocess.STDOUT,timeout=wall_timeout)
 assert captured=={str(n.relative_to(repo)):hashlib.sha256(n.read_bytes()).hexdigest() for n in files} and fixture_sha==hashlib.sha256(tb.read_bytes()).hexdigest() and fl_sha==hashlib.sha256((repo/filelist).read_bytes()).hexdigest(),'compile/run inputs changed'
 blob=vvp.read_bytes();archive=vvp.with_suffix('.vvp.gz');archive.write_bytes(gzip.compress(blob,6,mtime=0));assert gzip.decompress(archive.read_bytes())==blob
 text=(a.out/(label+'-run.log')).read_text();marker='UNIFIED_LAST_PHYSICAL_BOUNDARY' if a.unified_last_physical else 'CASE generation exhaustion' if gen<8 else 'RTL_RESULT';assert marker in text and 'PASS' in text,'terminal qualification marker absent'
 row={'host_wall_timeout_seconds':wall_timeout,'RTL_fixture_cycle_watchdog':30000,'qualification_scope':'Unified full1024Tags/highestPID1167/bankcompatible exhaustion/resume' if a.unified_last_physical else 'twelve byte/lifecycle cases and small generation exhaustion','full_synthesizable_top':a.full_top,'mode':mode,'GEN_W':gen,'compile_command':cmd,'returncode':r.returncode,'binary_sha256':hashlib.sha256(blob).hexdigest(),'exact_binary_archive':str(archive),'stimulus_sha256':hashlib.sha256(tb.read_bytes()).hexdigest(),'RTL_sha256':{str(n.relative_to(repo)):hashlib.sha256(n.read_bytes()).hexdigest() for n in files}};result.append(row);(a.out/'FUNCTIONAL_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');assert r.returncode==0, label;vvp.unlink();print(label,'PASS',flush=True)
