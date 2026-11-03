"""Best-effort cache hints for consumed regions of this Goal's NAS read FDs.
Never edits payload, changes another process, drops global caches, or launches
a simulator. Its only OS mutation is POSIX_FADV_DONTNEED on approved read data.
"""
import pathlib,os,stat,json,time
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');NAS='/root/share/mnt164/'
class Adviser:
 def __init__(self):self.offsets={};self.closed=set();self.bytes=0;self.calls=0;self.errors=0
 def process(self,pid,start_ticks=None):
  root=P('/proc')/str(pid)
  try:
   tick=int((root/'stat').read_text().rsplit(')',1)[1].split()[19])
   if start_ticks is not None and tick!=start_ticks:return
   for fd in (root/'fd').iterdir():
    try:
     target=os.readlink(fd)
     if not target.startswith(NAS):continue
     text=(root/'fdinfo'/fd.name).read_text();pos=int(next(l.split()[1] for l in text.splitlines() if l.startswith('pos:')))
     end=max(0,pos-4*1024**2);end=end//4096*4096;key=(pid,tick,fd.name,target);before=self.offsets.get(key,0)
     if end<=before:continue
     handle=os.open(str(fd),os.O_RDONLY)
     try:
      s=os.fstat(handle)
      if not stat.S_ISREG(s.st_mode) or s.st_dev!=39:continue
      os.posix_fadvise(handle,before,end-before,os.POSIX_FADV_DONTNEED);self.offsets[key]=end;self.bytes+=end-before;self.calls+=1
     finally:os.close(handle)
    except (OSError,ValueError,StopIteration):self.errors+=1
  except (OSError,ValueError):return
 def closed_qualified_inputs(self):
  for qfile in (T/'qualification').glob('*/QUALIFICATION.json'):
   try:q=json.loads(qfile.read_bytes())
   except (OSError,ValueError):continue
   for r in q.get('rows',[]):
    path=r['path']
    if path in self.closed:continue
    try:
     p=P(path);real=str(p.resolve())
     if not real.startswith(NAS):continue
     fd=os.open(p,os.O_RDONLY)
     try:os.posix_fadvise(fd,0,0,os.POSIX_FADV_DONTNEED)
     finally:os.close(fd)
     self.closed.add(path);self.calls+=1;self.bytes+=p.stat().st_size
    except OSError:self.errors+=1
 def summary(self):return {'scope':'Own Goal read FDs or its completed full-SHA input reads only','advice_calls':self.calls,'consumed_bytes_advised':self.bytes,'best_effort_errors':self.errors,'source_payload_writes':0,'source_asset_deletions':0,'global_cache_drop':False}
def body_advice_main():
 lease=json.loads((T/'control/BODY_WORKER_LAUNCH.json').read_bytes());root=P('/proc')/str(lease['pid']);a=Adviser()
 while root.exists():
  try:
   if int((root/'stat').read_text().rsplit(')',1)[1].split()[19])!=lease['start_ticks']:break
   if 'sweep_body_qualification.py' not in (root/'cmdline').read_bytes().decode(errors='replace'):break
   children=(root/'task'/str(lease['pid'])/'children').read_text().split()
   for pid in children:a.process(int(pid))
   a.closed_qualified_inputs();tmp=T/'analysis/READ_CACHE_ADVICE.json.writing';tmp.write_text(json.dumps(a.summary(),indent=2)+'\n');os.replace(tmp,T/'analysis/READ_CACHE_ADVICE.json')
  except (OSError,ValueError):pass
  time.sleep(10)
 a.closed_qualified_inputs();(T/'analysis/READ_CACHE_ADVICE_CLOSED.json').write_text(json.dumps(a.summary(),indent=2)+'\n')
if __name__=='__main__':body_advice_main()
