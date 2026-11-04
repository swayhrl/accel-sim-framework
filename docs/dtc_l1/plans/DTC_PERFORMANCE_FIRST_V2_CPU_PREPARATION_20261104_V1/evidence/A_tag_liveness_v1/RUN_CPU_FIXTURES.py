#!/usr/bin/env python3
"""CPU-only replay to a new, exclusive true164 output directory. No model entry point."""
from pathlib import Path
import argparse, os, subprocess, json, resource, hashlib, time, datetime

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-root',required=True);p.add_argument('--output-root',required=True);p.add_argument('--cpu',required=True,type=int);a=p.parse_args()
 src=Path(a.source_root).resolve();out=Path(a.output_root).resolve()
 assert str(out).startswith('/root/share/mnt164/'), 'all outputs must remain true164'
 assert not out.exists(), 'exclusive output root required; do not overwrite frozen evidence'
 assert a.cpu in os.sched_getaffinity(0), 'CPU outside process legal mask'
 out.mkdir(parents=True);(out/'tmp').mkdir();env=dict(os.environ,TMPDIR=str(out/'tmp'),TMP=str(out/'tmp'),TEMP=str(out/'tmp'),PYTHONDONTWRITEBYTECODE='1')
 def limit():
  os.nice(19);os.sched_setaffinity(0,{a.cpu});resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_CPU,(60,60))
 records=[]
 for name,define in [('original',0),('global_idle_lru_v2cpu',1)]:
  exe=out/('unit_'+name);cmd=['g++','-std=c++17','-O1','-Wall','-Wextra','-DGLOBAL_IDLE='+str(define),'-I'+str(src/'include'/name),str(src/'tag_liveness_cpu.cpp'),'-o',str(exe)]
  r=subprocess.run(cmd,capture_output=True,text=True,env=env,preexec_fn=limit,timeout=70)
  (out/(name+'.compile.stdout.log')).write_text(r.stdout);(out/(name+'.compile.stderr.log')).write_text(r.stderr);assert r.returncode==0
  start=time.monotonic();r=subprocess.run([str(exe)],capture_output=True,text=True,env=env,preexec_fn=limit,timeout=60)
  (out/(name+'.stdout.jsonl')).write_text(r.stdout);(out/(name+'.stderr.log')).write_text(r.stderr);assert r.returncode==0
  rows=[json.loads(x)for x in r.stdout.splitlines()];records.append(dict(header=name,case_n=len(rows),cases=rows,elapsed_host_seconds=time.monotonic()-start,compile_argv=cmd,execution_argv=[str(exe)],header_sha256=hashlib.sha256((src/'include'/name/'dtc-l1-common.h').read_bytes()).hexdigest()))
 result=dict(status='PASS_EXPECTED_PROGRESS_AND_HOLD_CLASSES',recorded_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_root=str(src),cpu=a.cpu,runs=records,actual_model_starts=0,finite_tests_not_universal_proof=True)
 (out/'CPU_REPLAY_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'output_root':str(out),'case_n':sum(x['case_n']for x in records),'status':result['status']}))
if __name__=='__main__':main()
