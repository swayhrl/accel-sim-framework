"""Public platform resource guard; exact final V10 progress helper text, no private code import."""
from pathlib import Path
from collections import deque
import os,stat,json,hashlib,time,subprocess,threading
P=Path;MIB=2**20;GIB=2**30
_io_pressure_cached=(0,100)
_block_observation=None
_block_health={'known':False}
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def bounded_json_raw(p):
 path=P(p);before=path.stat();need(before.st_size<=128*MIB,'RESOURCE_HOLD_PLATFORM_METADATA128MIB')
 with path.open('rb')as f:raw=f.read(128*MIB+1)
 need(len(raw)<=128*MIB,'RESOURCE_HOLD_PLATFORM_METADATA_GROWTH128MIB')
 return raw
def read(p):return json.loads(bounded_json_raw(p))
def block_health():
 global _block_observation,_block_health
 now=time.monotonic()
 if _block_observation and now-_block_observation[0]<5:return _block_health
 try:
  row=next(line.split() for line in P('/proc/diskstats').read_text().splitlines() if line.split()[2]=='sdf')
  values=list(map(int,row[3:]));previous=_block_observation;_block_observation=(now,values)
  if previous:
   elapsed=now-previous[0];old=previous[1];ops=values[0]-old[0]+values[4]-old[4]
   busy=max(0,values[9]-old[9])/elapsed/10
   await_ms=max(0,values[3]-old[3]+values[7]-old[7])/max(1,ops)
   _block_health={'known':True,'device':'sdf','busy_percent':busy,'await_ms':await_ms,'inflight':values[8]}
 except (OSError,StopIteration,ValueError,IndexError):_block_health={'known':False}
 return _block_health

def adaptive_io_rate(maximum,full=None):
 global _io_pressure_cached
 if full is None:
  now=time.monotonic()
  if now-_io_pressure_cached[0]>=5:
   try:
    line=next(x for x in P('/proc/pressure/io').read_text().splitlines() if x.startswith('full '));full=float(next(x.split('=')[1] for x in line.split() if x.startswith('avg10=')))
   except (OSError,StopIteration,ValueError):full=100
   _io_pressure_cached=(now,full)
  full=_io_pressure_cached[1]
 health=block_health()
 if health.get('known') and health['busy_percent']<10 and health['await_ms']<25 and health['inflight']<4:
  return min(maximum,32*MIB)
 return min(maximum,(30 if full<5 else 10 if full<10 else 4 if full<20 else 1)*MIB)

def _progress_process_identity(proof):
 pid=proof['pid'];ticks=proof['start_ticks']
 need(type(pid)is int and type(ticks)is int and pid>0 and ticks>0,'RESOURCE_HOLD_ACTIVE_PID_PROOF_INVALID')
 try:row=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()
 except (FileNotFoundError,ProcessLookupError):return None
 if int(row[19])!=ticks or row[0]in ['Z','X','x']:return None
 return {'pid':pid,'start_ticks':ticks}

class _ProgressTail:
 def __init__(self):self.pending=bytearray();self.records=deque(maxlen=32);self.record_count=0;self.decoded_bytes=0
 def add_record(self,line):
  if not line.strip():return
  try:row=json.loads(line)
  except (ValueError,UnicodeDecodeError)as e:raise RuntimeError('RESOURCE_HOLD_ACTIVE_PROGRESS_BAD_JSON')from e
  need(isinstance(row,dict),'RESOURCE_HOLD_ACTIVE_PROGRESS_BAD_JSON_TYPE');self.records.append(row);self.record_count+=1
 def feed(self,data):
  self.decoded_bytes+=len(data);need(self.decoded_bytes<=64*MIB,'RESOURCE_HOLD_ACTIVE_PROGRESS_DECODED64M_LIMIT')
  self.pending.extend(data)
  while True:
   at=self.pending.find(b'\n')
   if at<0:break
   need(at<=256*1024,'RESOURCE_HOLD_ACTIVE_PROGRESS_RECORD256K_LIMIT');line=bytes(self.pending[:at]);del self.pending[:at+1];self.add_record(line)
  need(len(self.pending)<=256*1024,'RESOURCE_HOLD_ACTIVE_PROGRESS_RECORD256K_LIMIT')
 def finish(self,allow_live_partial):
  if self.pending.strip():
   try:row=json.loads(self.pending)
   except (ValueError,UnicodeDecodeError):
    need(allow_live_partial and bool(self.records)and bytes(self.pending).lstrip().startswith(b'{'),'RESOURCE_HOLD_ACTIVE_PROGRESS_TRUNCATED_JSON')
   else:
    need(isinstance(row,dict),'RESOURCE_HOLD_ACTIVE_PROGRESS_BAD_JSON_TYPE');self.records.append(row);self.record_count+=1;self.pending.clear()
  need(bool(self.records),'RESOURCE_HOLD_ACTIVE_PROGRESS_UNREADABLE')
  return self.records[-1]

def _progress_snapshot(out):
 """Bounded metadata read; a live final gzip member need not have its trailer yet."""
 import zlib
 out=P(out);plain=out/'progress.jsonl';compressed=False
 if plain.exists():path=plain
 else:path=out/'progress.jsonl.gz';compressed=True
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW);tail=_ProgressTail();raw_bytes=0;frames=0;decoder=None;last_eof=False;member_prefix=b''
 with os.fdopen(fd,'rb',buffering=0)as stream:
  before=os.fstat(stream.fileno());need(stat.S_ISREG(before.st_mode),'RESOURCE_HOLD_ACTIVE_PROGRESS_FILE_TYPE')
  if not compressed:
   start=max(0,before.st_size-4096);stream.seek(start);raw=stream.read(before.st_size-start);raw_bytes=len(raw)
   if start:raw=raw.split(b'\n',1)[1]if b'\n'in raw else b''
   tail.feed(raw);last=tail.finish(True)
  else:
   need(before.st_size<=16*MIB,'RESOURCE_HOLD_ACTIVE_PROGRESS_COMPRESSED16M_LIMIT');left=before.st_size
   while left:
    raw=stream.read(min(64*1024,left));need(bool(raw),'RESOURCE_HOLD_ACTIVE_PROGRESS_TRUNCATED_FILE');left-=len(raw);raw_bytes+=len(raw);data=raw
    while data:
     if decoder is None:decoder=zlib.decompressobj(31);member_prefix=b''
     if len(member_prefix)<2:
      member_prefix+=data[:2-len(member_prefix)]
      need(b'\x1f\x8b'.startswith(member_prefix),'RESOURCE_HOLD_ACTIVE_PROGRESS_BAD_GZIP_HEADER')
     previous=len(data)
     try:decoded=decoder.decompress(data,min(64*1024,64*MIB-tail.decoded_bytes+1))
     except zlib.error as e:raise RuntimeError('RESOURCE_HOLD_ACTIVE_PROGRESS_BAD_GZIP')from e
     tail.feed(decoded)
     if decoder.eof:
      frames+=1;data=decoder.unused_data;decoder=None;last_eof=not data
     else:
      data=decoder.unconsumed_tail;last_eof=False
      need(bool(decoded)or len(data)<previous,'RESOURCE_HOLD_ACTIVE_PROGRESS_DECODER_NO_PROGRESS')
   last=tail.finish(decoder is not None)
  after=os.fstat(stream.fileno());path_after=path.lstat()
  need(stat.S_ISREG(path_after.st_mode)and before.st_dev==after.st_dev==path_after.st_dev and before.st_ino==after.st_ino==path_after.st_ino,'RESOURCE_HOLD_ACTIVE_PROGRESS_PATH_FD_CHANGED')
  need(after.st_size>=before.st_size and path_after.st_size>=before.st_size,'RESOURCE_HOLD_ACTIVE_PROGRESS_FILE_TRUNCATED')
  if compressed:need(after.st_size<=16*MIB and path_after.st_size<=16*MIB,'RESOURCE_HOLD_ACTIVE_PROGRESS_COMPRESSED16M_LIMIT')
 meta={'path':str(path),'format':'gzip_stream'if compressed else'plain_tail','compressed_bytes_read':raw_bytes if compressed else 0,'plain_bytes_read':raw_bytes if not compressed else 0,'decoded_bytes':tail.decoded_bytes,'complete_records_seen':tail.record_count,'retained_records':len(tail.records),'gzip_completed_members':frames if compressed else None,'gzip_last_member_eof':last_eof if compressed else None,'live_unfinalized_gzip_CRC_not_claimed':compressed and decoder is not None,'pending_bytes_not_adopted_as_complete':len(tail.pending),'limits':{'compressed_bytes':16*MIB,'decoded_bytes':64*MIB,'retained_records':32,'single_record_bytes':256*1024}}
 return last,meta

def _current_foreign_progress(out,proof):
 """Exact proof identity on both sides; concurrent exit/Z is not an active health failure."""
 before=_progress_process_identity(proof)
 if before is None:return None
 try:
  last,meta=_progress_snapshot(out)
  has_identity='pid'in last or 'start_ticks'in last
  if meta['format']=='gzip_stream'or has_identity:
   need(type(last.get('pid'))is int and type(last.get('start_ticks'))is int and last['pid']==proof['pid']and last['start_ticks']==proof['start_ticks'],'RESOURCE_HOLD_ACTIVE_PROGRESS_PID_TICKS_MISMATCH')
   meta['record_identity']='MATCHED_EXACT_PROOF_PID_START_TICKS'
  else:meta['record_identity']='LEGACY_PLAIN_SCHEMA_WITHOUT_PID_FIELDS_LIVE_PROOF_PRE_POST'
  age=(time.monotonic_ns()-last['mono_ns'])/1e9
  need(age<=30,'RESOURCE_HOLD_ACTIVE_AEFAIR_PROGRESS_FRESHNESS')
  completed=last['completed'];phase=last['phase']
 except (RuntimeError,OSError,ValueError,KeyError,TypeError)as e:
  if _progress_process_identity(proof)is None:return None
  if isinstance(e,RuntimeError)and str(e).startswith('RESOURCE_HOLD_'):raise
  raise RuntimeError('RESOURCE_HOLD_ACTIVE_PROGRESS_UNREADABLE: '+repr(e))from e
 if _progress_process_identity(proof)!=before:return None
 return {'pid':proof['pid'],'start_ticks':proof['start_ticks'],'completed':completed,'phase':phase,'progress_age_seconds':age,'progress_reader':meta}

def allocated_tree(root):
 root=P(root);total=root.lstat().st_blocks*512 if root.exists()else 0
 def err(e):
  if e.errno!=2:raise e
 for base,dirs,files in os.walk(root,onerror=err,followlinks=False):
  for name in dirs+files:
   try:s=os.lstat(P(base)/name)
   except OSError as e:
    if e.errno==2:continue
    raise
   if not stat.S_ISLNK(s.st_mode):total+=s.st_blocks*512
 return total
class Resources:
 def __init__(self,profile,extra_budget_roots=(),clock=time.monotonic,sleeper=time.sleep):
  self.profile=profile;self.work=P(profile['native_work_root']);self.clock=clock;self.sleep=sleeper
  self.extra_roots=[P(x)for x in extra_budget_roots];self.last=0;self.value=None;self.samples=[];self.counters=dict(read=0,write=0);self.started=clock();self.lock=threading.RLock()
  self.testing=profile['execution_scope']=='QUALIFICATION'
  need(profile['execution_scope']in['QUALIFICATION','PRODUCTION'],'RESOURCE_HOLD_PROFILE_SCOPE')
 def _platform(self):
  q=self.profile;registry=read(q['native_registry'])
  legacy_raw=bounded_json_raw(P(__file__).with_name('legacy_foreign_binding.json'));legacy=json.loads(legacy_raw)
  need(hashlib.sha256(legacy_raw).hexdigest()==q['legacy_foreign_binding_sha256'],'RESOURCE_HOLD_LEGACY_PLATFORM_BINDING_SHA')
  old=registry.get('registered_future_requests',{}).get(legacy['legacy_request_id'])
  need(old is not None and old.get('state')==legacy['legacy_request_must_remain_state']and old.get('remaining')==legacy['legacy_request_must_remain_remaining']and old.get('budget')==legacy['legacy_request_budget']and old.get('reserved_write_bytes')==legacy['legacy_reservation_not_retired_bytes'],'RESOURCE_HOLD_NEW_LEGACY_PLATFORM_BINDING_REQUIRED')
  reserved=sum(x.get('reserved_write_bytes',0)for x in registry.get('registered_future_requests',{}).values())
  active=[]
  for request_id,registered in registry.get('registered_future_requests',{}).items():
   if request_id==legacy['legacy_request_id']:continue  # exact public binding proves these four terminal; reservation still counted above
   consumed=registered.get('consumed',{})
   if not isinstance(consumed,dict):continue
   for record in consumed.values():
    if not isinstance(record,dict)or record.get('execution_receipt')or not record.get('intent'):continue
    intent=P(record['intent'])
    done=intent.with_name(intent.name.replace('.INTENT.','.DONE.'))
    if done.exists():continue
    # Source of active intents is shared authority; unreadability never means quiescence.
    try:i=read(intent)
    except (OSError,ValueError,TypeError)as e:raise RuntimeError('RESOURCE_HOLD_FOREIGN_INTENT_UNREADABLE: '+str(intent))from e
    out=P(i['output']);proof=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
    if not proof.exists():continue
    p=read(proof);state=_current_foreign_progress(out,p)
    if state is not None:state['cohort']=i['cohort'];active.append(state)
  return registry,reserved,active
 def check(self,force=False):
  with self.lock:
   need(not hasattr(self,'deadline')or self.clock()<self.deadline,'RESOURCE_HOLD_FINITE_STAGE_DEADLINE')
   if not force and self.value and self.clock()-self.last<1:return self.value
   q=self.profile
   if self.testing:
    sample=read(q['qualification_resource_state'])
    need(sample['host_ok']and sample['mount_ok'],'RESOURCE_HOLD_TEST_HOST_MOUNT')
    need(sample['foreign_ok'],'RESOURCE_HOLD_TEST_FOREIGN_PROGRESS')
    reserved=sample['reserved_bytes'];free=sample['free_bytes'];available=sample['mem_available'];cg=sample['cgroup_available'];inodes=sample['free_inodes'];rate=sample['rate'];active=[]
   else:
    need(os.uname().nodename==q['expected_host']and os.readlink('/proc/self/ns/mnt')==q['expected_mount_namespace']and P('/root/data').stat().st_dev==q['native_device'],'RESOURCE_HOLD_TARGET_IDENTITY')
    fs=json.loads(subprocess.check_output(['/usr/bin/findmnt','-J','-T',q['nas_mount_root']],text=True))['filesystems'][0]
    need(fs['source']==q['nas_endpoint']and fs['fstype']=='fuse.sshfs','RESOURCE_HOLD_NOT_GENUINE164')
    registry,reserved,active=self._platform()
    disk=os.statvfs('/root/data');free=disk.f_bavail*disk.f_frsize;inodes=disk.f_favail
    available=int(next(x.split()[1]for x in P('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024
    cur=int(P('/sys/fs/cgroup/memory.current').read_text());maximum=P('/sys/fs/cgroup/memory.max').read_text().strip();cg=2**63 if maximum=='max'else int(maximum)-cur
    pressure={line.split()[0]:{a.split('=')[0]:float(a.split('=')[1])for a in line.split()[1:]}for line in P('/proc/pressure/io').read_text().splitlines()}
    rate=adaptive_io_rate(q['maximum_io_bytes_sec'],pressure.get('full',{}).get('avg10',100))
   required=5*GIB+reserved+GIB+256*MIB
   need(free>=required and inodes>=100000,'RESOURCE_HOLD_SHARED_SSD_ALL_PROJECT_RESERVATIONS')
   need(available>=64*GIB and cg>=GIB,'RESOURCE_HOLD_HOST_OR_CGROUP_RAM')
   own=allocated_tree(self.work)+sum(allocated_tree(x)for x in self.extra_roots if x!=self.work)
   need(own<=256*MIB,'RESOURCE_HOLD_OWN_NATIVE_TOTAL256MIB')
   value=dict(observed_unix=time.time(),free=free,required_free=required,registered_foreign_reserved_bytes=reserved,own_allocated_bytes=own,rate=rate,active_foreign=active,host_MemAvailable_bytes=available,cgroup_available=cg,source_keep=True,all_policy_gates_pass=True)
   self.last=self.clock();self.value=value;self.samples.append(value);self.samples=self.samples[-128:];return value
 def window(self,requested):
  value=self.check(True);remaining=256*MIB-value['own_allocated_bytes']-16*MIB
  limit=min(requested,64*MIB,max(0,remaining//MIB*MIB));need(remaining>=MIB and limit>0,'RESOURCE_HOLD_OWN_DYNAMIC_WINDOW');return limit
 def account(self,n,direction):
  need(direction in self.counters and n>=0,'RESOURCE_HOLD_IO_COUNTER')
  self.counters[direction]+=n;rate=self.check(False)['rate'];need(rate>0,'RESOURCE_HOLD_IO_RATE')
  due=sum(self.counters.values())/rate-(self.clock()-self.started)
  if due>0:self.sleep(due)
