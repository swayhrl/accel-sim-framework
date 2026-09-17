#!/usr/bin/env python3
"""Run one requalified candidate using accepted Route-B producer with guards."""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,subprocess,sys,time
from pathlib import Path

PRODUCER=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-producer-authority-v1')
BIN=Path('/data/c16/awma/storage_sidelane_v1/producer_5143/bin/route_b_5143.so')
DRIVER=Path('/data/c16/awma/storage_sidelane_v1/requalification_20260917T121512Z/driver.py')
PARSER=Path('/data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z/hotfix_fb5d0b_admission/traceg_grammar_smoke_fb5d0b')
POST=Path('/data/c16/awma/storage_sidelane_v1/producer_5143/bin/post-traces-processing_5143')

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--candidate',type=Path,required=True);a.add_argument('--mode',choices=['canary','formal'],required=True);a.add_argument('--out',type=Path,required=True);x=a.parse_args()
 c=json.loads(x.candidate.read_text())
 if c['status']!='IDENTITY_CLOSED':raise SystemExit('identity not closed')
 if x.out.exists():raise SystemExit('output collision')
 x.out.mkdir(parents=True);raw=x.out/'raw';raw.mkdir()
 env=os.environ.copy();env.update({'PATH':'/usr/local/cuda-12.8/bin:'+env.get('PATH',''),'NVDISASM':'/usr/local/cuda-12.8/bin/nvdisasm','NO_EAGER_LOAD':'0','CUDA_INJECTION64_PATH':str(BIN),'ROUTE_B_RAW_DIR':str(raw),'ROUTE_B_FUNCTION_REGEX':re.escape(c['exact_function_producer_demangle']),'ROUTE_B_FUNCTION_OCCURRENCE':str(c['producer_selector_function_ordinal']),'TOOL_VERBOSE':'0','PYTHONUNBUFFERED':'1'})
 if x.mode=='canary':env['INSTR_END']='8'
 cmd=['/data/c16/env/c16-py310/bin/python',str(DRIVER)]
 (x.out/'TARGET_IDENTITY.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
 (x.out/'CAPTURE_COMMAND.json').write_text(json.dumps({'argv':cmd,'mode':x.mode,'selector_regex_literal':c['exact_function_producer_demangle'],'selector_ordinal':c['producer_selector_function_ordinal'],'instr_end':env.get('INSTR_END','FULL')},indent=2,sort_keys=True)+'\n')
 with (x.out/'driver.stdout').open('w') as out,(x.out/'driver.stderr').open('w') as err:
  p=subprocess.Popen(cmd,env=env,stdout=out,stderr=err)
  cap=8*1024**3
  aggregate_cap=32*1024**3
  time_cap=1800
  started=time.monotonic(); size_guard=False; aggregate_guard=False; time_guard=False
  while p.poll() is None:
   size=sum(q.stat().st_size for q in raw.rglob('*') if q.is_file())
   aggregate=sum(q.stat().st_size for q in Path('/data/c16/awma/storage_sidelane_v1').glob('captures/*/raw/*') if q.is_file())
   if size>cap:
    size_guard=True;p.terminate();break
   if aggregate>aggregate_cap:
    aggregate_guard=True;p.terminate();break
   if time.monotonic()-started>time_cap:
    time_guard=True;p.terminate();break
   time.sleep(2)
  rc=p.wait()
 (x.out/'GUARD.json').write_text(json.dumps({'per_target_cap_bytes':cap,'aggregate_cap_bytes':aggregate_cap,'time_cap_seconds':time_cap,'size_guard_triggered':size_guard,'aggregate_guard_triggered':aggregate_guard,'time_guard_triggered':time_guard,'elapsed_seconds':round(time.monotonic()-started,3),'driver_returncode':rc},indent=2,sort_keys=True)+'\n')
 if size_guard or aggregate_guard or time_guard:
  raise SystemExit('BOUNDED_PARTIAL_NOT_FORMAL resource guard')
 if rc:raise SystemExit('driver failure')
 stdout=(x.out/'driver.stdout').read_text()
 if 'EXACT_Q05_S2_REQUALIFICATION_LISTING_COMPLETE' not in stdout:raise SystemExit('workload completion missing')
 if 'ROUTEB_TERMINAL_COMPLETE' not in stdout:raise SystemExit('terminal missing')
 if f"selector_occurrence={c['producer_selector_function_ordinal']} selected=1" not in stdout:raise SystemExit('selector binding missing')
 (x.out/'lifecycle.log').write_text('\n'.join(line for line in stdout.splitlines() if line.startswith('ROUTEB_LIFECYCLE') or line.startswith('ROUTEB_TERMINAL_COMPLETE'))+'\n')
 # The terminal receipt is emitted only after pclose/rename.  On the shared
 # filesystem, wait for both atomically published members to become visible;
 # do not let a directory-cache race turn a complete producer run into a
 # postprocess attempt over an empty directory.
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  if list(raw.glob('kernel-*.trace.xz')) and (raw/'kernelslist').is_file(): break
  time.sleep(1)
 if not list(raw.glob('kernel-*.trace.xz')) or not (raw/'kernelslist').is_file():
  raise SystemExit('terminal receipt present but canonical raw members not visible after bounded wait')
 subprocess.run([str(POST),str(raw)],check=True,stdout=(x.out/'postprocess.stdout').open('w'),stderr=(x.out/'postprocess.stderr').open('w'))
 trace=next(raw.glob('kernel-*.trace.xz'));traceg=next(raw.glob('kernel-*.traceg.xz'))
 subprocess.run(['xz','-t',str(trace)],check=True)
 # post-traces-processing delegates compression to a child.  Its own exit is
 # not the completion boundary for that child, so explicitly wait until the
 # canonical traceg member is readable before consumer validation.
 deadline=time.monotonic()+60
 while True:
  check=subprocess.run(['xz','-t',str(traceg)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  if check.returncode==0: break
  if time.monotonic()>=deadline: raise SystemExit('postprocess traceg member did not reach readable xz completion')
  time.sleep(1)
 subprocess.run([str(PARSER),str(traceg)],check=True,stdout=(x.out/'validator.stdout').open('w'),stderr=(x.out/'validator.stderr').open('w'))
 if b' 2 0x' in subprocess.check_output(['xz','-dc',str(trace)]):raise SystemExit('mode2 detected')
 terminal=next(line for line in stdout.splitlines() if line.startswith('ROUTEB_TERMINAL_COMPLETE'))
 if 'drop_count=0' not in terminal or 'overflow_count=0' not in terminal:raise SystemExit('drop/overflow')
 raw_records=sum(1 for line in subprocess.check_output(['xz','-dc',str(trace)],text=True).splitlines() if line and not line.startswith('-') and not line.startswith('#'))
 receipt={'mode':x.mode,'candidate_id':c['candidate_id'],'terminal_line':terminal,'raw_records':raw_records,'trace_sha256':sha(trace),'traceg_sha256':sha(traceg),'validator_sha256':sha(PARSER),'mode2_records':0,'status':'CANARY_TERMINAL_COMPLETE' if x.mode=='canary' else 'FORMAL_LOCAL_COMPLETE'}
 (x.out/'CAPTURE_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 with (x.out/'SHA256SUMS').open('w') as f:
  for q in sorted(z for z in x.out.rglob('*') if z.is_file() and z.name!='SHA256SUMS'):f.write(f'{sha(q)}  {q.relative_to(x.out)}\n')
 print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
