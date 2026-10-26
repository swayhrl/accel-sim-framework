#!/usr/bin/python3
"""Selected-only immutable5d CPU scheduler. No capture, validator, simulator or publisher dispatch."""
from pathlib import Path
import os,sys,json,hashlib,time,stat,subprocess,signal,fcntl,concurrent.futures,threading,importlib.util,resource,socket,queue,math,errno
HERE=Path(__file__).resolve().parent
POST=HERE/'preimages/postprocess_nas_sharded_v4.py'
POST_SHA='5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d'
BOOT="import os,sys,ctypes;lib=ctypes.CDLL(None);parent=int(sys.argv[1]);fd=int(sys.argv[2]);assert lib.prctl(1,15,0,0,0)==0;assert os.getppid()==parent;token=os.read(fd,1);os.close(fd);sys.exit(125)if token!=b'G'else None;os.execv(sys.argv[3],sys.argv[3:])"
JOB='ORD_Rodinia_streamcluster_1be5fda1aa60_A001'
PROD_ROOT=Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/inflight')/JOB
AUTH=Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control/ROOT_STREAMCLUSTER_CPU_RESUME_EXEC_APPROVAL_V2.json')
TOOLS=['/usr/bin/taskset','/usr/bin/nice','/usr/bin/prlimit','/usr/bin/python3','/usr/bin/sort']
def need(x,m):
 if not x:raise RuntimeError('CPU_RESUME_HOLD_'+m)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def payload_sha(p,check):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  while True:
   check();b=f.read(2**20);check()
   if not b:break
   h.update(b)
 return h.hexdigest()
def token(p):
 s=Path(p).lstat();return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_uid,s.st_gid)
def regular(p):
 s=Path(p).lstat();need(stat.S_ISREG(s.st_mode)and not Path(p).is_symlink(),'REGULAR_NO_SYMLINK');return token(p)
def no_links(p):
 for q in[Path(p),*Path(p).parents]:need(not q.is_symlink(),'PATH_SYMLINK')
def readref(ref,limit=8*2**20):
 p=Path(ref['path']);no_links(p);before=regular(p);need(before[2]<=limit,'BOUNDED_METADATA')
 with p.open('rb')as f:
  need(token(p)==before,'METADATA_OPEN');raw=f.read(limit+1);need(len(raw)<=limit,'METADATA_GROWTH')
 need(token(p)==before and len(raw)==ref['bytes']and hashlib.sha256(raw).hexdigest()==ref['sha256'],'METADATA_REF_SHA_BYTES')
 return json.loads(raw)
def save(p,v):
 raw=canon(v)
 with Path(p).open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
def ref(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def ticks(pid):
 try:return Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()[19]
 except FileNotFoundError:return None
def lease_check(rows):
 need(rows,'INHERITED_NEW_RECOVERY_LEASES_REQUIRED')
 for x in rows:
  fd=x['fd'];p=Path(x['path']);no_links(p);need(token(p)==tuple(x['identity']),'LEASE_PATH_IDENTITY')
  st=os.fstat(fd);need((st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns,st.st_mode,st.st_uid,st.st_gid)==tuple(x['identity']),'LEASE_FD_IDENTITY')
  need(ticks(x['owner_pid'])==x['owner_start_ticks'],'LEASE_OWNER_TICKS')
  ancestor=os.getpid()
  for _ in range(64):
   if ancestor==x['owner_pid']:break
   need(ancestor>1,'LEASE_OWNER_NOT_ANCESTOR');ancestor=int(Path('/proc',str(ancestor),'stat').read_text().split(') ',1)[1].split()[1])
  else:raise RuntimeError('CPU_RESUME_HOLD_LEASE_ANCESTRY_BOUND')
  info=Path('/proc/self/fdinfo',str(fd)).read_text();need('FLOCK' in info and 'WRITE' in info,'INHERITED_OFD_FLOCK_REQUIRED')
  parentfd=Path('/proc',str(x['owner_pid']),'fd',str(fd));need(parentfd.exists()and parentfd.stat().st_ino==st.st_ino and parentfd.stat().st_dev==st.st_dev,'LEASE_INHERITED_OWNER_FD')
  found=False
  for line in Path('/proc/locks').read_text().splitlines():
   a=line.split()
   if len(a)>=6 and a[1:4]==['FLOCK','ADVISORY','WRITE']and a[4]==str(x['owner_pid']):
    v=a[5].split(':')
    if len(v)==3 and(int(v[0],16),int(v[1],16),int(v[2]))==(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino):found=True
  need(found,'NEW_RECOVERY_LEASE_NOT_HELD')
def own_members(owner):
 found=[]
 for p in Path('/proc').glob('[0-9]*/stat'):
  try:
   f=p.read_text().split(') ',1)[1].split()
   if int(f[2])==int(f[3])==owner['pid']and int(f[19])>=int(owner['start_ticks'])and f[0]not in['Z','X','x']:found.append(dict(pid=int(p.parent.name),start_ticks=f[19]))
  except(FileNotFoundError,ProcessLookupError):pass
 return found
def cleanup(owners):
 actions=[]
 for sig in[signal.SIGTERM,signal.SIGKILL]:
  for owner in owners:
   for row in own_members(owner):
    try:fd=os.pidfd_open(row['pid'])
    except ProcessLookupError:continue
    try:
     f=Path('/proc',str(row['pid']),'stat').read_text().split(') ',1)[1].split()
     if f[19]==row['start_ticks']and int(f[2])==int(f[3])==owner['pid']:signal.pidfd_send_signal(fd,sig,None,0);actions.append(dict(**row,signal=int(sig)))
    except(ProcessLookupError,FileNotFoundError):pass
    finally:os.close(fd)
  until=time.monotonic()+2
  while time.monotonic()<until and any(own_members(x)for x in owners):time.sleep(.02)
 need(not any(own_members(x)for x in owners),'UNRESOLVED_OWN_SESSION_ROOT_REQUIRED')
 return actions
def admit(spec,work,grant_ref,qualification):
 need(sha(POST)==POST_SHA,'FROZEN_5D_SHA')
 root=Path(spec['source_root']).absolute();work=Path(work).absolute();no_links(root);no_links(work)
 need(not work.exists(),'NEW_ATTEMPT_ONLY');need(type(spec['workers'])is int and spec['workers']in[1,2],'MAX_QUALIFIED_CPU2')
 need(type(spec['timeout_seconds'])is int and 0<spec['timeout_seconds']<=72000,'FINITE_TIME')
 need(type(spec['scratch_budget_bytes'])is int and 2**20<=spec['scratch_budget_bytes']<=64*2**30,'FINITE_SHARD_SCRATCH')
 need(type(spec['own_output_limit_bytes'])is int and 2**20<=spec['own_output_limit_bytes']<=128*2**30,'POLLED_OWN_LIMIT')
 need(spec['source_KEEP']is True and spec['capture_GPU_validator_allowed']is False,'CPU_ONLY_SOURCE_KEEP')
 snapshot=readref(spec['snapshot_ref']);names=snapshot['declared_order'];need(len(names)==len(set(names))and names,'EXACT_F9_KERNEL_SET')
 for n in names:need(Path(n).name==n and n.startswith('kernel-')and n.endswith('.trace.xz'),'EXACT_RAW_NAME')
 known=snapshot['known_raw_sha256'];need(set(known)==set(names)==set(snapshot['per_kernel']),'F9_SCOPE')
 need(set(p.name for p in(root/'traces').glob('kernel*.trace.xz'))==set(names),'CURRENT_RAW_METADATA_SET')
 selected=spec['selected'];need(type(selected)is list and 0<len(selected)<=8 and len(selected)==len(set(selected))and set(selected)<=set(names),'EXACT_FINITE_SELECTION_MAX8')
 reused=spec['reuse'];need(type(reused)is list and len({x['name']for x in reused})==len(reused)and {x['name']for x in reused}<=set(names)-set(selected),'DISJOINT_REUSE_SELECTION')
 cpus=spec['cpu_ids'];need(type(cpus)is list and len(cpus)==spec['workers']and len(set(cpus))==len(cpus)and all(type(c)is int for c in cpus)and set(cpus)<=os.sched_getaffinity(0),'EXACT_DISJOINT_CPU_SET')
 if qualification:
  no_links(HERE/'fixtures');need(root.resolve().is_relative_to((HERE/'fixtures').resolve())and work.resolve().is_relative_to((HERE/'fixtures').resolve()),'QUALIFICATION_PRIVATE_ONLY')
  cutoff=time.time()+spec['timeout_seconds']
 else:
  need(grant_ref is not None and Path(grant_ref['path'])==AUTH,'ROOT_EXACT_AUTHORITY_REQUIRED_BEFORE_BODY')
  g=readref(grant_ref);need(AUTH.stat().st_uid==0 and AUTH.stat().st_mode&0o022==0,'ROOT_AUTHORITY_OWNER')
  need(g['schema']=='ROOT_STREAMCLUSTER_SELECTED_CPU_POST_V2'and g['status']=='ROOT_APPROVED_EXACT_CPU_ONLY_POST_V2','ROOT_APPROVAL')
  need(g['spec_sha256']==hashlib.sha256(canon(spec)).hexdigest()and g['code_manifest_sha256']==sha(HERE/'CODE_MANIFEST.json'),'ROOT_CODE_SPEC')
  mf=json.loads((HERE/'CODE_MANIFEST.json').read_text())
  for n,row in mf['files'].items():need(sha(HERE/n)==row['sha256']and(HERE/n).stat().st_size==row['bytes'],'ROOT_FRESH_CODE')
  need(work.resolve().is_relative_to((HERE/'runs').resolve())and g['work_root']==str(work),'EXACT_NEW_PRIVATE_RECOVERY_WORK')
  expected_lease_paths={'RTX_SOURCE_174':str(AUTH.parent/'RTX4080_SOURCE.lock'),'RTX_TARGET_174':str(AUTH.parent/'RTX4080_TARGET.lock')}
  need({x['role']:x['path']for x in spec['leases']}==expected_lease_paths,'EXACT_RECOVERY_LEASE_PATHS')
  need(root==PROD_ROOT and snapshot['job_id']==JOB and spec['snapshot_ref']['sha256']==sha(HERE/'preimages/FROZEN_ADOPTION_INPUT_V1.json'),'FIXED_STREAMCLUSTER_ONLY')
  need(g['host']==socket.gethostname()and g['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'ROOT_HOST_BOOT')
  need(type(g['not_before_unix'])in[int,float]and type(g['absolute_deadline_unix'])in[int,float]and math.isfinite(g['not_before_unix'])and math.isfinite(g['absolute_deadline_unix'])and g['not_before_unix']<=time.time()<g['absolute_deadline_unix']and g['absolute_deadline_unix']-g['not_before_unix']<=72000,'ROOT_NONRENEWABLE_DEADLINE')
  need(g['resource_policy']=='NAS_ONLY_CPU2_AS1536M_NO_ENFORCED_BANDWIDTH_EXCLUSIVE_RTX_V1','EXPLICIT_RESOURCE_IO_PROFILE')
  term=readref(g['terminal_evidence_ref']);gatepath=HERE/'preimages/metadata_gate_v1.py';sp=importlib.util.spec_from_file_location('exact_old_gate',gatepath);gate=importlib.util.module_from_spec(sp);sp.loader.exec_module(gate);gate.boundary(term,snapshot)
  need({x['role']for x in spec['leases']}=={'RTX_SOURCE_174','RTX_TARGET_174'},'NEW_NATIVE174_RECOVERY_WRITER_LEASES')
  need(sorted(os.sched_getaffinity(0))==sorted(spec['cpu_ids'])and os.getpriority(os.PRIO_PROCESS,0)>=15,'EXACT_PARENT_CPU_NICE')
  soft,hard=resource.getrlimit(resource.RLIMIT_AS);need(0<soft<=2*2**30 and 0<hard<=2*2**30,'PARENT_BOUNDED_AS')
  cutoff=min(time.time()+spec['timeout_seconds'],g['absolute_deadline_unix'])
 lease_check(spec['leases']);need(time.time()<cutoff,'DEADLINE_AFTER_METADATA')
 for tool,expected in spec['tool_sha256'].items():need(tool in TOOLS and sha(Path(tool).resolve())==expected,'EXACT_EXTERNAL_TOOL')
 need(set(spec['tool_sha256'])==set(TOOLS),'COMPLETE_FIXED_TOOL_PINS')
 return snapshot,root,work,cutoff
def own_tree_size(root):
 total=0
 def error(e):
  if e.errno!=errno.ENOENT:raise e
 for parent,dirs,files in os.walk(root,followlinks=False,onerror=error):
  for name in files:
   try:
    v=(Path(parent)/name).stat()
    if stat.S_ISREG(v.st_mode):total+=v.st_size
   except OSError as e:
    if e.errno!=errno.ENOENT:raise
 return total
def run(spec,work,grant_ref=None,qualification=False):
 snapshot,root,work,cutoff=admit(spec,work,grant_ref,qualification);mono_cutoff=time.monotonic()+max(0,cutoff-time.time());work.mkdir(parents=True)
 active={};all_processes=[];owners=[];peak_active=[0];lock=threading.Lock();abort=threading.Event();results={};reused=[];new=[];invocations=[]
 def check():
  need(time.time()<cutoff and time.monotonic()<mono_cutoff,'ABSOLUTE_DEADLINE');lease_check(spec['leases'])
  need(not abort.is_set(),'OWN_FAILURE_STOP')
  need(own_tree_size(work)<=spec['own_output_limit_bytes'],'POLLED_OUTPUT_SCRATCH_LIMIT')
  if not qualification:need(__import__('shutil').disk_usage(work).free>=20*2**30,'NAS_FLOOR')
 def expected(name,r):
  q=snapshot['per_kernel'][name]
  need(r['status']=='GROUPED_ALL_SHARDS_CRC_PASS'and r['source_sha256']==snapshot['known_raw_sha256'][name],'ACTUAL_RAW_BODY_SHA')
  need([r['records'],r['ctas'],r['warps']]==[q['records'],q['ctas'],q['warps']],'F9_COUNTS')
  need(r['closed_reopened_full_xz_crc']is True and r['source_keep']is True,'FROZEN5D_CRC_SOURCE_KEEP')
 try:
  for x in spec['reuse']:
   check();name=x['name'];r=readref(x['receipt_ref']);expected(name,r);need(x['postprocessor_sha256']==POST_SHA,'REUSE_5D_PIN')
   grouped=Path(x['grouped_path']);no_links(grouped);need(grouped.resolve().is_relative_to(root.resolve())or(qualification and grouped.resolve().is_relative_to((HERE/'fixtures').resolve())),'REUSE_GROUP_PRIVATE_ORIGINAL_PATH')
   before=regular(grouped);need(payload_sha(grouped,check)==r['grouped_sha256']and token(grouped)==before and grouped.stat().st_size==r['grouped_bytes'],'REUSE_FRESH_FULL_GROUP_SHA')
   results[name]=dict(name=name,origin='REUSED_STRICT_CLOSED5D',result=r,receipt_ref=x['receipt_ref'],grouped_path=str(grouped),grouped_current_identity=before,current_raw_body_reconciliation_still_required_at_archive=True);reused.append(name)
  cpu_slots=queue.Queue()
  for cpu_id in spec['cpu_ids']:cpu_slots.put(cpu_id)
  def one(pair):
   ix,name=pair;check();source=root/'traces'/name;no_links(source);before=regular(source);kdir=work/('kernel_'+str(ix));kdir.mkdir();out=kdir/name.replace('.trace.xz','.traceg.xz');scratch=kdir/'work'
   while True:
    check()
    try:cpu=cpu_slots.get(timeout=.1);break
    except queue.Empty:continue
   argv=['/usr/bin/taskset','-c',str(cpu),'/usr/bin/nice','-n','15','/usr/bin/prlimit','--as=1610612736:1610612736','--core=0:0','--','/usr/bin/python3','-I','-S','-B',str(POST),str(source),str(out),str(scratch),'--cta-span','64','--scratch-budget',str(spec['scratch_budget_bytes'])]
   check()
   with(kdir/'stdout.json').open('xb')as stdout,(kdir/'stderr.log').open('xb')as stderr:
    gate_in,gate_out=os.pipe();p=None
    try:
     with lock:
      need(not abort.is_set(),'STOP_BEFORE_BIRTH')
      p=subprocess.Popen(['/usr/bin/python3','-I','-S','-B','-c',BOOT,str(os.getpid()),str(gate_in)]+argv,stdout=stdout,stderr=stderr,start_new_session=True,pass_fds=(gate_in,),env=dict(PATH='/usr/bin:/bin',LC_ALL='C',TMPDIR=str(kdir),PYTHONDONTWRITEBYTECODE='1'))
      all_processes.append(p);owner=dict(pid=p.pid,start_ticks=ticks(p.pid));need(owner['start_ticks']is not None,'OWNED_BIRTH_IDENTITY');owners.append(owner);active[p.pid]=p;peak_active[0]=max(peak_active[0],len(active));invocations.append(dict(name=name,argv=argv,owner=owner));save(kdir/'PROCESS_START.json',dict(**owner,argv=argv,source_identity=before,unreleased_bootstrap_cannot_fork=True));check()
      os.write(gate_out,b'G')
    except BaseException:
     os.close(gate_out);gate_out=None
     if p is not None:p.wait(timeout=5)
     raise
    finally:
     os.close(gate_in)
     if gate_out is not None:os.close(gate_out)
    try:
     while p.poll()is None:
      check();time.sleep(.05)
     need(p.returncode==0,'FROZEN5D_NONZERO_'+str(p.returncode));need(not own_members(owner),'OWN_DESCENDANT_AFTER_EXIT')
    finally:
     with lock:active.pop(p.pid,None)
   need((kdir/'stdout.json').stat().st_size<=2**20,'RESULT_METADATA_CAP');r=json.loads((kdir/'stdout.json').read_text());expected(name,r)
   need(token(source)==before,'RAW_SOURCE_CHANGED_DURING_POST');need(r['grouped']==str(out)and payload_sha(out,check)==r['grouped_sha256']and out.stat().st_size==r['grouped_bytes'],'GROUPED_CLOSED_REOPEN_SHA')
   check();receipt=dict(schema='SELECTED_CPU_POST_CLOSED_V2',name=name,postprocessor_sha256=POST_SHA,original_f9_metadata=snapshot['metadata'],source_before_after_identity=before,result=r,observed_helper_exitcode=p.returncode,owned_session_empty=True,qualification_only=qualification,source_KEEP=True)
   save(kdir/'POST_CLOSED_RECEIPT_V2.json',receipt);cpu_slots.put(cpu)
   return name,dict(name=name,origin='NEW_ACTUAL_FROZEN5D',result=r,receipt_ref=ref(scratch/'GROUP_RECEIPT.json'),execution_ref=ref(kdir/'POST_CLOSED_RECEIPT_V2.json'),grouped_path=str(out),current_raw_body_reconciliation_still_required_at_archive=True)
  pool=concurrent.futures.ThreadPoolExecutor(max_workers=spec['workers']);futures=[]
  try:
   futures=[pool.submit(one,pair)for pair in enumerate(spec['selected'])]
   for future in concurrent.futures.as_completed(futures):
    name,r=future.result();results[name]=r;new.append(name)
  except BaseException:
   abort.set();cleanup(owners)
   for p in all_processes:
    try:p.wait(timeout=5)
    except subprocess.TimeoutExpired:pass
   for f in futures:f.cancel()
   raise
  finally:pool.shutdown(wait=True,cancel_futures=True)
  check();ordered=[results[n]for n in snapshot['declared_order']if n in results]
  result=dict(schema='STREAMCLUSTER_SELECTED_CPU_POST_BATCH_CLOSED_V2',status='CPU_POST_BATCH_CLOSED_FULL_ARCHIVE_PENDING',qualification_only=qualification,source_KEEP=True,processed_selected=spec['selected'],actual_POST_invocations=invocations,peak_live_helper_processes=peak_active[0],reused_names=reused,per_kernel=ordered,whole_application_group_set_complete=set(results)==set(snapshot['declared_order']),records=sum(r['result']['records']for r in ordered),original_f9_reused=True,validator_rerun=False,GPU_capture_executed=False,archive_receiver_CURRENT_complete=False,full_current_raw_SHA_reconciliation_at_archive_required=True,unknown_old_partial_never_reused_or_deleted=True,IO_policy='NO_ENFORCED_BANDWIDTH_LIMIT; maxCPU2 and exact inherited writer leases',all_own_sessions_empty=not any(own_members(x)for x in owners))
  save(work/'BATCH_CLOSED.json',result);return result
 except BaseException as e:
  abort.set();cleanup_error=None
  try:actions=cleanup(owners)
  except BaseException as ce:actions=[];cleanup_error=repr(ce)
  for process in all_processes:
   try:process.wait(timeout=3)
   except subprocess.TimeoutExpired:cleanup_error='OWN_CHILD_REAP_PENDING_ROOT_REQUIRED'
  save(work/'FAILED_RETAINED.json',dict(error=repr(e),own_cleanup=actions,cleanup_error=cleanup_error,source_KEEP=True,all_old_partials_KEEP=True,qualification_granted=False));raise
def main():
 p=__import__('argparse').ArgumentParser();p.add_argument('--spec',required=True);p.add_argument('--spec-sha',required=True);p.add_argument('--work',required=True);p.add_argument('--qualification',action='store_true');p.add_argument('--grant');p.add_argument('--grant-sha');a=p.parse_args()
 spec=readref(dict(path=a.spec,sha256=a.spec_sha,bytes=Path(a.spec).stat().st_size));grant=None if a.grant is None else dict(path=a.grant,sha256=a.grant_sha,bytes=Path(a.grant).stat().st_size)
 os.nice(15);resource.setrlimit(resource.RLIMIT_AS,(2*2**30,2*2**30));print(json.dumps(run(spec,a.work,grant,a.qualification)))
if __name__=='__main__':main()
