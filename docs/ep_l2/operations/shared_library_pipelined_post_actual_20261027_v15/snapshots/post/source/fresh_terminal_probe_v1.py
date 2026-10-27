"""Exact old terminal and structured Linux held/pending locks. No lock acquisition/GPU."""
import pathlib,os,json,time,subprocess,shlex,re
REMOTE={795210:'360511682',795292:'360513379',1008828:'367078090',1026614:'367568855'}
NATIVE_SOURCE='/root/data/shared_rtx4080_trace_library_20261024_v1/control/RTX4080_SOURCE.lock'
NATIVE_TARGET='/root/data/shared_rtx4080_trace_library_20261024_v1/control/RTX4080_TARGET.lock'
def parse_locks(lines,device,inode):
 records=[];unknown=[]
 wanted=(os.major(device),os.minor(device),inode)
 for raw in lines:
  fields=raw.split();waiting=len(fields)>1 and fields[1]=='->';row=fields[2:]if waiting else fields[1:]
  keys=[]
  for item in fields:
   if re.fullmatch(r'[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9]+',item):
    a,b,c=item.split(':');keys.append((int(a,16),int(b,16),int(c)))
  if wanted not in keys:continue
  try:
   assert len(row)==7 and re.fullmatch(r'[0-9]+:',fields[0])
   kind,advisory,mode,pid,key,begin,end=row
   a,b,c=key.split(':');assert(int(a,16),int(b,16),int(c))==wanted
   assert kind in ('FLOCK','POSIX','OFDLCK')and advisory in ('ADVISORY','MANDATORY')and mode in ('READ','WRITE')
   assert re.fullmatch(r'-?[0-9]+',pid)and begin.isdigit()and(end=='EOF'or end.isdigit())
  except (AssertionError,ValueError):unknown.append(raw);continue
  records.append(dict(raw=raw,waiting=waiting,kind=kind,advisory=advisory,mode=mode,pid=int(pid),begin=begin,end=end))
 return dict(held=[r for r in records if not r['waiting']],waiting=[r for r in records if r['waiting']],unknown=unknown,raw_matching=[r['raw']for r in records]+unknown)
def scan(pids,paths):
 rows=[]
 for pid in pids:
  p=pathlib.Path('/proc',str(pid),'stat');rows.append(dict(pid=pid,state='ABSENT'if not p.exists()else'PRESENT_HOLD'))
 related=[]
 for p in pathlib.Path('/proc').glob('[0-9]*/stat'):
  try:f=p.read_text().split(') ',1)[1].split()
  except (FileNotFoundError,ProcessLookupError):continue
  if int(f[2])in pids or int(f[3])in pids:related.append(int(p.parent.name))
 text=pathlib.Path('/proc/locks').read_text().splitlines();locks=[]
 for path in paths:
  st=pathlib.Path(path).stat();locks.append(dict(path=path,device=st.st_dev,inode=st.st_ino,**parse_locks(text,st.st_dev,st.st_ino)))
 return dict(handles=rows,related=related,locks=locks,boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip())
def admit_locks(result,owned_pid,owned_paths):
 for row in result['locks']:
  row['own_exact_held']=[]
  if owned_pid is not None and row['path']in owned_paths:
   row['own_exact_held']=[r for r in row['held']if r['kind']=='FLOCK'and r['advisory']=='ADVISORY'and r['mode']=='WRITE'and r['pid']==owned_pid and r['begin']=='0'and r['end']=='EOF']
  row['blocking_held']=[r for r in row['held']if r not in row['own_exact_held']]
 return not result['related']and all(r['state']=='ABSENT'for r in result['handles'])and all(not r['blocking_held']and not r['unknown']for r in result['locks'])
def observe(owned_pid=None):
 src=pathlib.Path(__file__).read_text().split('def observe(owned_pid=None):')[0]+"\nprint(json.dumps(scan([795210,795292,1008828,1026614],['/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_LOCAL_IO.lock','/data/c16/locks/c16_gpu_campaign.lock'])))"
 p=subprocess.run(['ssh','-n','-o','BatchMode=yes','-o','ConnectTimeout=8','gpu109','python3 -B -c '+shlex.quote(src)],capture_output=True,text=True,timeout=12)
 if p.returncode:raise RuntimeError('fresh exact109 terminal unavailable')
 remote=json.loads(p.stdout);native=scan([1376608,1410582],[NATIVE_SOURCE,NATIVE_TARGET,'/root/data/shared_rtx4080_trace_library_20261024_v1/control/RTX4080_DISPATCHER.lock'])
 remote_closed=admit_locks(remote,None,set());native_closed=admit_locks(native,owned_pid,{NATIVE_SOURCE,NATIVE_TARGET})
 return dict(schema='FRESH_EXACT_OLD_STREAMCLUSTER_TERMINAL_HELD_PENDING_V2',unix=time.time(),closed=remote_closed and native_closed,native=native,remote=remote,no_waitpid_or_signal_or_lock_acquire=True,root_did_not_reap_original=True,pending_waiters_are_not_holders=True,terminal_basis='Current original identities absent and actual held records absent except exact current SOURCE/TARGET owner; original watchdog wait/cleanup evidence retained')
