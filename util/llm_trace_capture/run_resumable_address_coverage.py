#!/usr/bin/env python3
"""Resumable, per-trace exact address coverage for frozen M4A traceg inputs."""
from __future__ import annotations
import argparse, copy, hashlib, json, os, signal, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from analyze_trace_address_coverage import new_output, scan_file, merge_output, summary

STOP = False
def now(): return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def atomic(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_name(path.name+'.tmp')
 data=(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode()
 with tmp.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)
def encode(o,trace,sha):
 for n in ('minimum_observed_simva','maximum_observed_simva'):
  if o[n] is not None:o[n]=hex(o[n])
 for q in o['by_object'].values():
  q['pages_64k']=sorted(q['pages_64k']);q['pages_2m']=sorted(q['pages_2m'])
  for n in ('min_classifiable_address','max_classifiable_address'):
   if q[n] is not None:q[n]=hex(q[n])
 o['address_format_counts']=dict(o['address_format_counts']);o['trace']={'path':str(trace),'filename':trace.name,'sha256':sha};return o
def decode_partial(x):
 for n in ('minimum_observed_simva','maximum_observed_simva'):
  if x[n] is not None:x[n]=int(x[n],16)
 for q in x['by_object'].values():
  q['pages_64k']=set(q['pages_64k']);q['pages_2m']=set(q['pages_2m'])
  for n in ('min_classifiable_address','max_classifiable_address'):
   if q[n] is not None:q[n]=int(q[n],16)
 from collections import Counter
 x['address_format_counts']=Counter(x['address_format_counts']);return x
def aggregate(input_root,work,roi,files):
 o,rs=new_output(input_root,roi)
 for f in files:
  p=work/'partial'/(f.name+'.json');x=json.loads(p.read_text());
  if x['trace']['sha256']!=digest(f):raise RuntimeError('partial identity mismatch '+str(f))
  merge_output(o,decode_partial(x))
 out=summary(o); addrs=[]
 for q in out['by_object'].values():
  if q['min_classifiable_address'] is not None:addrs.extend((int(q['min_classifiable_address'],16),int(q['max_classifiable_address'],16)))
 out['trace_files_processed']=len(files)
 lo=out['minimum_observed_simva'];hi=out['maximum_observed_simva']
 out['minimum_observed_simva']=hex(lo) if lo is not None else None;out['maximum_observed_simva']=hex(hi) if hi is not None else None
 out['minimum_required_va_width']=hi.bit_length() if hi is not None else 0
 # Individual partials preserve no raw addresses; upper-bound counters are exact
 # because scan_file records them in its per-trace VA domain fields below.
 out['partial_set_sha256']=hashlib.sha256(''.join(digest(work/'partial'/(f.name+'.json')) for f in files).encode()).hexdigest();return out
def partial_output(work,f,sha):
 p=work/'partial'/(f.name+'.json')
 if not p.exists(): return None
 try: x=json.loads(p.read_text())
 except (OSError,json.JSONDecodeError): return None
 if x.get('trace',{}).get('path')!=str(f) or x.get('trace',{}).get('filename')!=f.name or x.get('trace',{}).get('sha256')!=sha:return None
 return decode_partial(x)
def snapshot(o):
 # summary converts page sets to counts; keep the live accumulator mutable.
 return summary(copy.deepcopy(o))
def build_partial(trace_s, ranges_data, roi, part_s):
 """Independent worker: one immutable input produces one atomic partial."""
 f=Path(trace_s); sha=digest(f)
 atomic(Path(part_s),encode(scan_file(f,ranges_data,roi),f,sha))
 return str(f),sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--roi',choices=('prefill','decode1'),required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--workers',type=int,default=1);a=p.parse_args()
 if a.workers < 1:p.error('--workers must be >= 1')
 files=sorted((a.input/'traces').glob('*.traceg.xz'));work=a.work/a.roi;start=time.time();pid=os.getpid()
 def halt(sig,_):
  global STOP;STOP=True
  atomic(work/'exit.json',{'status':'SIGNAL','signal':sig,'pid':pid,'timestamp':now()})
 for s in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP):signal.signal(s,halt)
 atomic(work/'run.log',{'command':sys.argv,'pid':pid,'start_timestamp':now(),'input':str(a.input),'roi':a.roi})
 done=0
 try:
  o,rs=new_output(a.input,a.roi); pending=[]
  # Validate every pre-existing partial against its immutable input before skip.
  for f in files:
   sha=digest(f);x=partial_output(work,f,sha)
   if x is None: pending.append(f)
   else: merge_output(o,x);done+=1
  def report(last):
   final=snapshot(o)
   atomic(work/'progress.json',{'roi':a.roi,'completed_files':done,'total_files':len(files),'last_completed_trace':last,'elapsed_seconds':round(time.time()-start,3),'memory_instructions':final['memory_instructions'],'lane_references':final['lane_references'],'requested_bytes':final['requested_bytes'],'by_object':final['by_object'],'decoder_invariant_failures':final['decoder_invariant_failures']})
   print(json.dumps({'roi':a.roi,'completed_files':done,'total_files':len(files),'last_completed_trace':last,'lane_references':final['lane_references']},sort_keys=True),flush=True)
  if pending and a.workers==1:
   for f in pending:
    if STOP: raise KeyboardInterrupt
    _,sha=build_partial(str(f),rs,a.roi,str(work/'partial'/(f.name+'.json')));x=partial_output(work,f,sha)
    if x is None:raise RuntimeError('atomic partial validation failed '+str(f))
    merge_output(o,x);done+=1;report(f.name)
  elif pending:
   with ProcessPoolExecutor(max_workers=a.workers) as pool:
    jobs={pool.submit(build_partial,str(f),rs,a.roi,str(work/'partial'/(f.name+'.json'))):f for f in pending}
    for job in as_completed(jobs):
     if STOP:
      for other in jobs:other.cancel()
      raise KeyboardInterrupt
     f=jobs[job];_,sha=job.result();x=partial_output(work,f,sha)
     if x is None:raise RuntimeError('atomic partial validation failed '+str(f))
     merge_output(o,x);done+=1
     if done==len(files) or done%16==0:report(f.name)
  else: report('all pre-existing partials validated')
  one=aggregate(a.input,work,a.roi,files);two=aggregate(a.input,work,a.roi,files)
  b1=json.dumps(one,sort_keys=True,separators=(',',':')).encode();b2=json.dumps(two,sort_keys=True,separators=(',',':')).encode()
  if b1!=b2:raise RuntimeError('non-deterministic aggregation')
  one['canonical_sha256']=hashlib.sha256(b1).hexdigest();atomic(work/'final.json',one);atomic(work/'exit.json',{'status':'PASS','return_code':0,'pid':pid,'end_timestamp':now(),'completed_files':done})
 except Exception as e:
  atomic(work/'exit.json',{'status':'ERROR','return_code':1,'pid':pid,'end_timestamp':now(),'completed_files':done,'error':repr(e)});raise
if __name__=='__main__':main()
