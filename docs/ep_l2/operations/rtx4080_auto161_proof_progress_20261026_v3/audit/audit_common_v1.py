#!/usr/bin/env python3
"""Small read-only verifier primitives. No subprocess, signal, queue or STOP mutations."""
import hashlib,json,os,pathlib,stat,time
class AuditError(Exception):
 def __init__(self,code,detail=''):self.code=code;self.detail=str(detail);super().__init__(code+': '+self.detail)
def need(condition,code,detail=''):
 if not condition:raise AuditError(code,detail)
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
class Reader:
 def __init__(self,roots,max_file=4*1024**2,max_total=64*1024**2):
  self.roots=[pathlib.Path(p).resolve() for p in roots];self.max_file=max_file;self.max_total=max_total;self.total=0;self.cache={}
 def path(self,value):
  p=pathlib.Path(value);need(p.is_absolute(),'RELATIVE_PATH',value)
  # Reject every existing symlink component, not merely the final resolved filename.
  for component in [p,*p.parents]:
   need(not component.is_symlink(),'SYMLINK_PATH',component)
  real=p.resolve();need(any(real==r or r in real.parents for r in self.roots),'OUTSIDE_ALLOWED_ROOT',p)
  need(real.is_file(),'MISSING_EVIDENCE',p);return real
 def bytes(self,value):
  p=self.path(value);s=p.stat();need(stat.S_ISREG(s.st_mode),'NONREGULAR_FILE',p)
  need(s.st_size<=self.max_file,'LONG_BODY_NOT_HASHED',{'path':str(p),'bytes':s.st_size})
  key=(str(p),s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
  if key in self.cache:return self.cache[key]
  need(self.total+s.st_size<=self.max_total,'AUDIT_READ_BUDGET_EXCEEDED',self.total+s.st_size)
  flags=os.O_RDONLY|getattr(os,'O_NOFOLLOW',0);fd=os.open(p,flags)
  try:
   before=os.fstat(fd);need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==key[1:],'EVIDENCE_CHANGED_BEFORE_READ',p)
   with os.fdopen(fd,'rb',closefd=False) as stream:data=stream.read(self.max_file+1)
   after=os.fstat(fd);need(len(data)==s.st_size and (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)==key[1:],'EVIDENCE_CHANGED_DURING_READ',p)
  finally:os.close(fd)
  self.total+=len(data);self.cache[key]=data;return data
 def obj(self,value):
  try:return json.loads(self.bytes(value))
  except (ValueError,UnicodeError) as e:raise AuditError('INVALID_JSON',str(value)) from e
 def ref(self,reference):
  need(isinstance(reference,dict),'MISSING_FILE_REF',reference)
  need(set(['path','bytes','sha256'])<=set(reference),'INCOMPLETE_FILE_REF',reference)
  need(type(reference['bytes']) is int and reference['bytes']>=0,'INVALID_REF_LENGTH',reference)
  need(isinstance(reference['sha256'],str) and len(reference['sha256'])==64 and all(x in '0123456789abcdef' for x in reference['sha256']),'INVALID_REF_DIGEST',reference)
  data=self.bytes(reference['path']);need(len(data)==reference['bytes'],'FILE_LENGTH_MISMATCH',reference['path'])
  need(hashlib.sha256(data).hexdigest()==reference['sha256'],'FILE_DIGEST_MISMATCH',reference['path']);return data
 def refobj(self,reference):
  try:return json.loads(self.ref(reference))
  except (ValueError,UnicodeError) as e:raise AuditError('INVALID_REF_JSON',reference) from e
def process_key(process):
 need(isinstance(process,dict),'MISSING_PROCESS_IDENTITY')
 keys=('boot_id','pid','start_ticks')
 need(all(k in process for k in keys),'INCOMPLETE_PROCESS_IDENTITY',process)
 need(isinstance(process['pid'],int) and process['pid']>0,'INVALID_PID',process)
 need(str(process['start_ticks']).isdigit() and bool(process['boot_id']),'INVALID_PROCESS_IDENTITY',process)
 return (process['boot_id'],process['pid'],str(process['start_ticks']))
def proc_identity(pid):
 try:
  values=pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()
  return {'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'pid':int(pid),'start_ticks':values[19],'state':values[0]}
 except (FileNotFoundError,ProcessLookupError,PermissionError):return None
def interval_checks(intervals):
 events=[];by_job={};by_slot={}
 for row in intervals:
  a,b=row['start'],row['end'];need(isinstance(a,int) and isinstance(b,int) and 0<a<b,'INVALID_EXECUTION_INTERVAL',row)
  need(row['slot'] in (0,1),'CPU_SLOT_OUTSIDE_TWO',row)
  events.extend([(a,1),(b,-1)]);by_job.setdefault(row['queue_id'],[]).append((a,b));by_slot.setdefault(row['slot'],[]).append((a,b))
 active=peak=0
 for _,delta in sorted(events,key=lambda x:(x[0],x[1])):
  active+=delta;peak=max(peak,active);need(active<=2,'CPU_CONCURRENCY_GT2',active)
 for kind,groups in [('JOB',by_job),('SLOT',by_slot)]:
  for id,spans in groups.items():
   spans.sort()
   for x,y in zip(spans,spans[1:]):need(x[1]<=y[0],'OVERLAPPING_'+kind+'_ATTEMPTS',id)
 return peak
def no_qualification(value):
 if isinstance(value,dict):
  for key,item in value.items():
   if key in ('qualification_granted','trace_qualified','exact_trace_qualified','consumer_qualified','scientific_qualified','hardware_timing_qualified','gpu_execution','gpu_executed','simulator_execution','simulation_executed','historical_queue_mutated'):
    need(item is False,'UNAUTHORIZED_QUALIFICATION_OR_GPU',{'field':key,'value':item})
   no_qualification(item)
 elif isinstance(value,list):
  for x in value:no_qualification(x)
