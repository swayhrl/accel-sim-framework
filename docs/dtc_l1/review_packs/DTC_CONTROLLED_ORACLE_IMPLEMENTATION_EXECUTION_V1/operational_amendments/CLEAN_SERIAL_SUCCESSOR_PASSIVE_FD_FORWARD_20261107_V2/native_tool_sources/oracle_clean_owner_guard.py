"""CPU candidate. Serial clean-Main succession, never an old-image repair.

No imports acquire production locks or write authority. CPU fixtures use only
temporary locks. DTC-MAIN must separately release actual acquisition/dispatch.
"""
from pathlib import Path
import contextlib,fcntl,hashlib,json,os,re,sys,threading

OLD_IDENTITIES=((1498278,977758783),(438646,1072993843))
REQUEST='DTC_ORACLE_REMAINING24_20261106_V1'
AUTHORITY='18b1ee9d339902e555fc2e04ef51c84f77dfe1b1'
BASE=Path('/root/data/dtc_controlled_oracle_20261106_v1')
FIXED_LOCK_PATHS={'governance':str(BASE/'control/OWNER_RECOVERY_AND_CLOSEOUT.lock'),
 'owner':'/root/data/dtc_main_v100_sweep_20261025_v1/control/FINITE_CONTROLLER.lock',
 'qualification':'/root/data/ep_l2_dtc_l1_native_v2/control/qualification_ledger/NATIVE_QUALIFICATION.lock',
 'shared':str(BASE/'control/SHARED_DISPATCH_OWNER.lock')}
FIXED_LOCK_IDENTITIES={'governance':(2128,62219596),'owner':(2128,61758282),
 'qualification':(2128,61622661),'shared':(2128,62213534)}
INITIAL_MATRIX_SHA='658fc5f35827d3c516b8d3eba06501b33e0d55dc1d546a4ae832ef9819e7b81a'
class Hold(RuntimeError):pass
def need(value,reason):
 if not value:raise Hold(reason)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def encoded(value):return(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
def pin(ref):
 p=Path(ref['path']);need(sha(p)==ref['sha256'],'SOURCE_PIN_DRIFT:'+str(p));return p
def process(pid,proc=Path('/proc')):
 p=Path(proc)/str(pid)
 try:
  a=(p/'stat').read_text().rsplit(')',1)[1].split()
  return dict(pid=pid,state=a[0],ppid=int(a[1]),start_ticks=int(a[19]),
              cmdline=(p/'cmdline').read_bytes().split(b'\0'),
              tracer_pid=int(re.search(r'^TracerPid:\s*(\d+)',(p/'status').read_text(),re.M)[1]))
 except FileNotFoundError:return None
def terminal(snapshot,pid,start):
 if snapshot is None:return dict(pid=pid,start_ticks=start,state='ABSENT')
 need(snapshot['pid']==pid,'PROCESS_SNAPSHOT_PID_MISMATCH')
 if snapshot['start_ticks']!=start:
  return dict(pid=pid,start_ticks=start,state='OLD_GENERATION_ABSENT_UNRELATED_PID_REUSE',
              unrelated_current_start_ticks=snapshot['start_ticks'])
 need(snapshot['state']=='Z','OLD_OWNER_OR_HELPER_NOT_TERMINAL')
 return dict(pid=pid,start_ticks=start,state='ZOMBIE_NO_USERSPACE')
def retired_processes(proc=Path('/proc')):
 return [terminal(process(pid,proc),pid,start)for pid,start in OLD_IDENTITIES]
def ancestry(pid,owner_pid,owner_start,proc=Path('/proc')):
 chain=[];seen=set()
 for _ in range(64):
  need(pid>0 and pid not in seen,'ANCESTRY_CYCLE_OR_MISSING_OWNER');seen.add(pid)
  s=process(pid,proc);need(s is not None and s['state']!='Z','DESCENDANT_PROCESS_MISSING_OR_ZOMBIE')
  chain.append(dict(pid=pid,start_ticks=s['start_ticks']))
  if pid==owner_pid:
   need(s['start_ticks']==owner_start,'ANCESTRY_OWNER_START_DRIFT');return chain
  pid=s['ppid']
 raise Hold('OWNER_NOT_IN_ACTUAL_PROCESS_ANCESTRY')
def lock_record(text,pid,device,inode):
 rows=[]
 for line in text.splitlines():
  if not line.startswith('lock:'):continue
  values=line.split()
  need('->'not in values and len(values)>=9,'BLOCKED_OR_MALFORMED_LOCK_RECORD')
  # fdinfo format lock: N: FLOCK ADVISORY WRITE PID major:minor:inode 0 EOF
  if values[2]!='FLOCK':continue
  major,minor,ino=values[6].split(':')
  actual_device=os.makedev(int(major,16),int(minor,16))
  if int(ino)==inode and actual_device==device:
   need(values[3]=='ADVISORY'and values[4]=='WRITE'and int(values[5])==pid
        and values[7:]==['0','EOF'],'EXCLUSIVE_WHOLE_FILE_CURRENT_OWNER_FLOCK_REQUIRED')
   rows.append(line)
 need(len(rows)==1,'EXACT_ONE_CURRENT_OWNER_EXCLUSIVE_FLOCK_REQUIRED');return rows[0]
def verify_lock(reference,pid,proc=Path('/proc')):
 path=Path(reference['path']);st=path.stat();fd=reference['fd'];p=Path(proc)/str(pid)
 need(type(fd)is int and fd>=0,'REAL_LOCK_FD_REQUIRED')
 need(st.st_dev==reference['device']and st.st_ino==reference['inode'],'LOCK_PATH_DEVICE_INODE_DRIFT')
 actual=(p/'fd'/str(fd)).stat()
 need((actual.st_dev,actual.st_ino)==(st.st_dev,st.st_ino),'LOCK_FD_DEVICE_INODE_MISMATCH')
 need(os.readlink(p/'fd'/str(fd))==str(path),'LOCK_FD_TARGET_MISMATCH')
 return lock_record((p/'fdinfo'/str(fd)).read_text(),pid,st.st_dev,st.st_ino)
def all_references(paths,proc=Path('/proc')):
 """Bootstrap only; never inside registry EX or per-model resource sampler."""
 identities={(Path(p).stat().st_dev,Path(p).stat().st_ino):str(p)for p in paths}
 found=[]
 for p in Path(proc).iterdir():
  if not p.name.isdecimal():continue
  try:entries=list((p/'fd').iterdir())
  except FileNotFoundError:continue
  except PermissionError:raise Hold('CANNOT_PROVE_ALL_LOCK_REFERENCES')
  for fd in entries:
   try:
    st=fd.stat()
    if(st.st_dev,st.st_ino)in identities:
     found.append(dict(pid=int(p.name),fd=int(fd.name),path=identities[st.st_dev,st.st_ino],
                       fdinfo=(p/'fdinfo'/fd.name).read_text()))
   except FileNotFoundError:continue
   except PermissionError:raise Hold('CANNOT_PROVE_ALL_LOCK_REFERENCES')
 return found
def require_exclusive_references(references,allowed_pid):
 need(all(r['pid']==allowed_pid for r in references),'FOREIGN_PROCESS_HAS_GLOBAL_OR_SHARED_LOCK_REFERENCE')
 return True
def classify_open_references(references,allowed_pid=None):
 """An open FD is not an acquired FLOCK. Kernel EX acquisition is decisive.

 Foreign SH/EX or unclassified lock/wait records fail closed. Passive unlocked
 opens are audited, never treated as a scientific lease or permission.
 """
 passive=[];own=[]
 for row in references:
  if row['pid']==allowed_pid:own.append(row);continue
  records=[line for line in row['fdinfo'].splitlines()if line.startswith('lock:')]
  need(not records,'FOREIGN_ACTUAL_OR_UNCLASSIFIED_LOCK_RECORD_HOLD')
  passive.append(row)
 return dict(passive_unlocked_open_references=passive,current_owner_references=own,
             passive_FDs_confer_no_scientific_permission=True)
def require_fixed_lock_identities(references):
 need({x['role']:(x['device'],x['inode'])for x in references}==FIXED_LOCK_IDENTITIES,
      'ORIGINAL_GLOBAL_LOCK_DEVICE_INODES_REQUIRED_NO_NEW_FILE_SUBSTITUTES')
 return True
def require_old32_closed(proof):
 need(proof['schema']=='DTC_ORACLE_ORIGINAL32_IMMUTABLE_CLOSURE_V1'
      and proof['request']=='DTC_ORACLE_INITIAL8_20261106_V1'
      and proof['budget']==32 and proof['remaining']==0 and len(proof['rows'])==32,'ORIGINAL32_SCOPE_NOT_CLOSED')
 need(len({x['cohort']for x in proof['rows']})==32 and len({x['uuid']for x in proof['rows']})==32,
      'ORIGINAL32_DUPLICATE_IDENTITIES')
 matrix_path=BASE/'initial8/control/MATRIX.fixed.json'
 need(sha(matrix_path)==INITIAL_MATRIX_SHA,'ORIGINAL_FIXED_INITIAL32_MATRIX_PIN')
 points={p['cohort']:p for p in read(matrix_path)['points']}
 need(set(points)=={x['cohort']for x in proof['rows']},'EXACT_ORIGINAL32_COHORT_SET')
 for row in proof['rows']:
  need(row['state']=='PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE','ORIGINAL32_NOT_FULLY_ACCEPTED')
  for k in ['result','DONE','NATIVE_EXIT','spec']:pin(row[k])
  result=read(row['result']['path']);done=read(row['DONE']['path'])
  cohort=row['cohort'];root=BASE/'initial8';spec=read(row['spec']['path']);point=points[cohort]
  expected={'result':root/'analysis'/(cohort+'.RESULT.json'),
            'DONE':root/'control/qualification_ledger'/(cohort+'.DONE.json'),
            'NATIVE_EXIT':root/'DTC/run/results'/row['uuid']/'NATIVE_EXIT.json',
            'spec':root/'control/specs'/(cohort+'.json')}
  need(all(Path(row[k]['path'])==p for k,p in expected.items()),'ORIGINAL32_EXACT_NATIVE_SOURCE_LOCATIONS')
  need(spec['cohort']==cohort and spec['plan_id']==point['plan_id']
       and spec['input_digest']==point['input_digest']and spec['oracle_mode']==point['mode'],
       'ORIGINAL32_FULL_INPUT_PLAN_MODE_IDENTITY')
  need(done==read(row['NATIVE_EXIT']['path'])and result['uuid']==done['uuid']==row['uuid'],
       'ORIGINAL32_DONE_EXIT_RESULT_UUID')
  need(result['state']==row['state'],'ORIGINAL32_RESULT_STATUS')
 return True
def verify_parent_lease(plan,*,caller_pid=None,proc=Path('/proc'),allow_cpu_fixture=False):
 """Authentic private lease + real ancestry; no legacy marker/frame fiction."""
 need(plan['request']==REQUEST and plan['expected_new_starts']==96,'ONLY_FROZEN_NEW96')
 lease=read(pin(plan['clean_owner_lease']))
 if not allow_cpu_fixture:
  need(all(Path(p).stat().st_dev==2128 for p in[plan['clean_owner_lease']['path'],__file__,
       lease['controller']['path']]),'RUNTIME_GUARD_LEASE_CONTROLLER_MUST_BE_NATIVE_LOCAL_DEVICE2128')
 need(lease['schema']=='DTC_ORACLE_CLEAN_MAIN_PRIVATE_LEASE_V1'
      and lease['request']==REQUEST and lease['budget']==96 and lease['old32_new_starts']==0,
      'NEW_PRIVATE_LEASE_SCOPE')
 owner=lease['pid'];start=lease['start_ticks'];s=process(owner,proc)
 need((owner,start)not in OLD_IDENTITIES and s is not None and s['state']!='Z'
      and s['start_ticks']==start and s['tracer_pid']==0,'ACTUAL_NEW_OWNER_NOT_NORMAL_OR_STILL_TRACED')
 need(plan['parent_pid']==owner and plan['parent_start_ticks']==start,'TRUTHFUL_NEW_PLAN_PARENT')
 source=pin(lease['controller']);need(plan['parent_controller_path']==str(source)
      and plan['parent_controller_sha256']==lease['controller']['sha256'],'NEW_PARENT_SOURCE_PIN')
 need(str(source).encode()in s['cmdline'],'NEW_OWNER_CMDLINE_SOURCE')
 need(lease['guard_sha256']==sha(__file__),'ACTUAL_GUARD_SOURCE_PIN')
 retired_processes(proc)
 roles={x['role']for x in lease['locks']}
 need(roles=={'governance','owner','qualification','shared'}and len(lease['locks'])==4,'ALL_FOUR_UNIQUE_LOCK_SCOPES')
 if not allow_cpu_fixture:
  need({x['role']:x['path']for x in lease['locks']}==FIXED_LOCK_PATHS,
       'ACTUAL_GLOBAL_LOCK_PATHS_REQUIRED_NOT_ARBITRARY_PRIVATE_LOCKS')
  require_fixed_lock_identities(lease['locks'])
 for reference in lease['locks']:verify_lock(reference,owner,proc)
 chain=ancestry(os.getpid()if caller_pid is None else caller_pid,owner,start,proc)
 need(process(owner,proc)['start_ticks']==start,'OWNER_CHANGED_DURING_CHECK')
 return dict(lease,actual_ancestry=chain,actual_private_lease_path=plan['clean_owner_lease']['path'])
class CleanMainLocks:
 """Dormant management-only acquisition. CPU tests substitute temporary paths.

 Lease is emitted once, never over a historical lease. Resources remain owned
 through healthy-worker lifetime; caller must not close while children live.
 """
 def __init__(self,paths):self.paths=paths;self.handles=[]
 def __enter__(self):
  retired_processes();need(set(self.paths)=={'governance','owner','qualification','shared'},'EXACT_LOCK_SCOPES')
  need(self.paths==FIXED_LOCK_PATHS,'PRODUCTION_BOOTSTRAP_MUST_ACQUIRE_REAL_GLOBAL_SCOPES')
  before=classify_open_references(all_references(self.paths.values()))
  try:
   for role in ['governance','owner','qualification','shared']:
    p=Path(self.paths[role]);st=p.stat()
    need((st.st_dev,st.st_ino)==FIXED_LOCK_IDENTITIES[role],'GLOBAL_LOCK_INODE_CHANGED_BEFORE_OPEN')
    h=p.open('r+b');self.handles.append(h)
    current=os.fstat(h.fileno())
    need((current.st_dev,current.st_ino)==FIXED_LOCK_IDENTITIES[role],'GLOBAL_LOCK_INODE_CHANGED_DURING_OPEN')
    fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)
   self.references=[]
   for role,h in zip(['governance','owner','qualification','shared'],self.handles):
    st=os.fstat(h.fileno());row=dict(role=role,path=str(Path(h.name)),fd=h.fileno(),device=st.st_dev,inode=st.st_ino)
    verify_lock(row,os.getpid());self.references.append(row)
   require_fixed_lock_identities(self.references)
   retired_processes();after=classify_open_references(all_references(self.paths.values()),os.getpid())
   self.bootstrap_open_reference_evidence=dict(before=before,after=after,
      all_four_actual_EX_acquisitions_verified=True,external_passive_FDs_not_owners=True)
   return self
  except BaseException:self.__exit__(None,None,None);raise
 def __exit__(self,*unused):
  for h in reversed(self.handles):h.close()
  self.handles=[]

def build_private_lease(controller,locks,closed32_proof):
 require_old32_closed(closed32_proof)
 need(threading.current_thread()is threading.main_thread(),'NEW_REAL_MAIN_THREAD_ONLY')
 need(sys.dont_write_bytecode and not sys.is_finalizing()and not getattr(threading,'_SHUTTING_DOWN',False),
      'CLEAN_NORMAL_INTERPRETER_REQUIRED')
 source=pin(controller);self_process=process(os.getpid())
 main=sys.modules['__main__']
 need(Path(main.__file__).resolve()==source.resolve()and sha(main.__file__)==controller['sha256'],
      'TRUE_NEW_MAIN_SOURCE_REQUIRED_NOT_ARGV_SUBSTRING')
 need(str(source).encode()in self_process['cmdline'],'CLEAN_MAIN_ACTUAL_SOURCE_COMMAND')
 return dict(schema='DTC_ORACLE_CLEAN_MAIN_PRIVATE_LEASE_V1',pid=os.getpid(),start_ticks=self_process['start_ticks'],
    controller=controller,request=REQUEST,budget=96,old32_new_starts=0,
    locks=locks.references,guard_sha256=sha(__file__),authority_commit=AUTHORITY,
    retired_old_processes=retired_processes(),original32_closure_sha256=hashlib.sha256(encoded(closed32_proof)).hexdigest(),
    bootstrap_open_reference_evidence=locks.bootstrap_open_reference_evidence,
    identity_statement='New serial operational owner; never old PID/lease/frame continuation')

if __name__=='__main__':print(json.dumps(dict(status='CPU_CANDIDATE_ONLY',actual_lock_acquisitions=0,models=0,registrations=0)))
