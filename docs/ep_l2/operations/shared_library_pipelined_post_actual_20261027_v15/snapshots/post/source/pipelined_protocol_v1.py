"""Exact frozen-asset POST/capture separation. No capture execution or production authorization."""
from pathlib import Path
import os,json,hashlib,stat,time,socket,re
from fresh_terminal_probe_v1 import parse_locks
CONTROL=Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
NAS=Path('/root/share/mnt164/huangrulin/traces')
ORIGINAL_DEADLINE=1793241315.9269235
def need(x,m):
 if not x:raise RuntimeError('PIPELINED_POST_HOLD_'+m)
def rawref(r,root_authority=False,qualification=False):
 p=Path(r['path'])
 for q in [p,*p.parents]:need(not q.is_symlink(),'SYMLINK_REF')
 st=p.stat();need(stat.S_ISREG(st.st_mode)and st.st_size==r['bytes']and 0<st.st_size<=8*2**20,'METADATA_REGULAR_CAP')
 if root_authority and not qualification:need(p.resolve().is_relative_to(CONTROL.resolve())and st.st_uid==0 and not st.st_mode&0o022,'NATIVE_ROOT_AUTHORITY')
 b=p.read_bytes();z=p.stat();need((st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)and hashlib.sha256(b).hexdigest()==r['sha256'],'EXACT_REF')
 return json.loads(b)
def physical(p):
 p=Path(p)
 for q in [p,*p.parents]:need(not q.is_symlink(),'SYMLINK_PATH')
 return p.resolve(strict=True)
def overlap(a,b):return a==b or a.is_relative_to(b)or b.is_relative_to(a)
def proc(pid):
 try:
  t=Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
  return dict(pid=int(pid),start_ticks=t[19],state=t[0])
 except(FileNotFoundError,ProcessLookupError):return None
def same_owner(row):
 a=proc(row['pid']);need(a is not None and a['start_ticks']==str(row['start_ticks'])and a['state']not in ['Z','X','x'],'LIVE_OWNER')
 return a
def lock_snapshot(path):
 p=physical(path);before=p.stat();text=Path('/proc/locks').read_text().splitlines();after=p.stat()
 need((before.st_dev,before.st_ino)==(after.st_dev,after.st_ino),'LOCK_PATH_IDENTITY_CHANGED')
 return parse_locks(text,before.st_dev,before.st_ino)
def exact_write(row):
 return row['kind']=='FLOCK'and row['advisory']=='ADVISORY'and row['mode']=='WRITE'and row['pid']>0 and row['begin']=='0'and row['end']=='EOF'
def flock_rows(path):
 snap=lock_snapshot(path)
 need(not snap['unknown']and all(exact_write(r)for r in snap['held']),'UNKNOWN_POSIX_SHARED_OR_MALFORMED_HELD')
 return [r['pid']for r in snap['held']]
def owner_lock(row,path):
 same_owner(row);p=physical(path);st=p.stat();fp=Path('/proc',str(row['pid']),'fd',str(row['fd']));f=fp.stat()
 need((f.st_dev,f.st_ino)==(st.st_dev,st.st_ino),'OWNER_OFD_INODE')
 need('FLOCK' in Path('/proc',str(row['pid']),'fdinfo',str(row['fd'])).read_text(),'OWNER_OFD_FLOCK')
 need(flock_rows(p)==[int(row['pid'])],'EXACT_KERNEL_FLOCK_OWNER')
 same_owner(row)
def validate_capture(r,protected,qualification=False):
 c=rawref(r,True,qualification)
 need(c['schema']=='ROOT_EXACT_DISJOINT_CAPTURE_PROOF_V1'and c['status']=='ROOT_APPROVED_GATED_CAPTURE_EXACT_V1','CAPTURE_ROOT_PROOF')
 need(c['host']==socket.gethostname()and c['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'CAPTURE_HOST_BOOT')
 need(c['not_before_unix']<=time.time()<c['absolute_deadline_unix']<=ORIGINAL_DEADLINE,'CAPTURE_NONRENEWED_DEADLINE')
 need(c['GPU_LOCAL_IO_exclusivity_preserved']is True and c['legacy_unknown_writer_exemption']is False,'NO_GPU_OR_FOREIGN_BYPASS')
 scope=rawref(c['capture_scope_ref']);need(scope['native_run_root']==c['private_run_root']and scope['remote_run_root']==c['remote_private_run_root']and scope['native_run_id']==c['run_id']and scope['code_sha256']==c['capture_code_sha256'],'CAPTURE_SCOPE_CODE_BINDING')
 owner=c['native_owner'];same_owner(owner)
 cmd=Path('/proc',str(owner['pid']),'cmdline').read_bytes();need(hashlib.sha256(cmd).hexdigest()==c['owner_cmdline_sha256'],'EXACT_CAPTURE_ARGV')
 need(0<len(c['code_refs'])<=128,'CAPTURE_CODE_REFS')
 for rcode in c['code_refs']:
  q=physical(rcode['path']);b=q.read_bytes();need(len(b)==rcode['bytes']and len(b)<=2**20 and hashlib.sha256(b).hexdigest()==rcode['sha256'],'CAPTURE_CODE_DRIFT')
 root=physical(c['private_run_root']);need(qualification or root.is_relative_to(NAS.resolve()),'CAPTURE_PRIVATE_NAS')
 reads=[physical(v)for v in c['read_roots']];writes=[physical(v)for v in c['write_roots']]
 need(writes and all(w==root or w.is_relative_to(root)for w in writes),'CAPTURE_ONLY_PRIVATE_WRITES')
 need(all(not overlap(w,z)for w in writes for z in protected),'CAPTURE_WRITE_INTERSECTION')
 need(all(not overlap(v,z)for v in reads for z in protected[1:]),'CAPTURE_READ_POST_PRIVATE_INTERSECTION')
 # Exact lock list is Root pinned, not a mutable writer-authored registry.
 for l in c['native_locks']:
  need(l['pid']==owner['pid']and str(l['start_ticks'])==str(owner['start_ticks']),'CAPTURE_LOCK_SAME_OWNER')
  owner_lock(l,l['path'])
 return c
def validate_publisher(r,protected,qualification=False):
 c=rawref(r,True,qualification)
 need(c['schema']=='ROOT_EXACT_METADATA_PUBLISHER_PROOF_V1'and c['status']=='ROOT_APPROVED_METADATA_ONLY_PUBLISHER_V1','PUBLISHER_ROOT_PROOF')
 need(c['host']==socket.gethostname()and c['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'PUBLISHER_HOST_BOOT')
 need(c['not_before_unix']<=time.time()<c['absolute_deadline_unix']<=ORIGINAL_DEADLINE,'PUBLISHER_DEADLINE')
 need(c['metadata_only']is True and c['tracebody_write_allowed']is False and c['GPU_or_capture_execution_allowed']is False,'PUBLISHER_METADATA_ONLY')
 o=c['native_owner'];same_owner(o)
 singleton=c['singleton_lock'];need(singleton['pid']==o['pid']and str(singleton['start_ticks'])==str(o['start_ticks']),'PUBLISHER_SINGLETON_OWNER')
 if not qualification:need(singleton['path']==str(CONTROL/'RTX4080_CATALOG_PUBLISHER.lock'),'PUBLISHER_SINGLETON_PATH')
 owner_lock(singleton,singleton['path'])
 need(hashlib.sha256(Path('/proc',str(o['pid']),'cmdline').read_bytes()).hexdigest()==c['owner_cmdline_sha256'],'PUBLISHER_EXACT_ARGV')
 need(0<len(c['code_refs'])<=16,'PUBLISHER_CODE_PINS')
 for rcode in c['code_refs']:
  q=physical(rcode['path']);b=q.read_bytes();need(len(b)==rcode['bytes']and len(b)<=2**20 and hashlib.sha256(b).hexdigest()==rcode['sha256'],'PUBLISHER_CODE_DRIFT')
 writes=[physical(v)for v in c['write_roots']]
 need(writes and all(not overlap(w,z)for w in writes for z in protected),'PUBLISHER_WRITE_INTERSECTION')
 if not qualification:need(all(w.is_relative_to(NAS.resolve())or w.is_relative_to(CONTROL.resolve())for w in writes),'PUBLISHER_FIXED_STORAGE')
 return c
def publisher_lock(c,path):
 o=c['native_owner'];need(str(path)in c['native_lock_paths'],'PUBLISHER_ROOT_LOCK_PATH')
 st=Path(path).stat();matches=[]
 for q in Path('/proc',str(o['pid']),'fd').iterdir():
  try:
   z=q.stat()
   if(z.st_dev,z.st_ino)==(st.st_dev,st.st_ino)and 'FLOCK' in Path('/proc',str(o['pid']),'fdinfo',q.name).read_text():matches.append(int(q.name))
  except(FileNotFoundError,ProcessLookupError):pass
 need(len(matches)==1,'PUBLISHER_EXACT_LIVE_OFD')
 owner_lock(dict(**o,fd=matches[0]),path)
def check_global(a,protected,qualification=False):
 paths=a['global_writer_lock_paths']+a['global_scheduler_lock_paths']
 expected=[str(CONTROL/('RTX4080_'+n+'.lock'))for n in ['SOURCE','TARGET','DISPATCHER','QUEUE']]
 if not qualification:need(paths==expected,'FIXED_GLOBAL_LOCK_PATHS')
 captures=[(r,rawref(r,True,qualification))for r in a['admitted_capture_proof_refs']]
 publishers=[(r,rawref(r,True,qualification))for r in a['admitted_metadata_publisher_proof_refs']]
 for r,c in captures:need(c['schema']=='ROOT_EXACT_DISJOINT_CAPTURE_PROOF_V1'and c['status']=='ROOT_APPROVED_GATED_CAPTURE_EXACT_V1','PINNED_CAPTURE_AUTHORIZATION')
 for r,c in publishers:need(c['schema']=='ROOT_EXACT_METADATA_PUBLISHER_PROOF_V1'and c['status']=='ROOT_APPROVED_METADATA_ONLY_PUBLISHER_V1','PINNED_PUBLISHER_AUTHORIZATION')
 observations=[]
 def match(pid,path):
  cm=[(r,c,l)for r,c in captures for l in c['native_locks']if l['path']==str(path)and l['pid']==pid]
  pm=[(r,c)for r,c in publishers if c['native_owner']['pid']==pid and str(path)in c['native_lock_paths']]
  need(len(cm)+len(pm)==1,'UNKNOWN_OR_LEGACY_GLOBAL_WRITER')
  return cm,pm
 def pending(snap,path):
  need(not snap['unknown'],'UNKNOWN_MALFORMED_KERNEL_RECORD')
  for row in snap['waiting']:
   need(exact_write(row),'UNKNOWN_POSIX_SHARED_OR_MALFORMED_PENDING')
   cm,pm=match(row['pid'],path)
   if cm:
    # Capture must already own its complete Root-acknowledged lease set;
    # a half-started capture is not silently admitted as a mere waiter.
    validate_capture(cm[0][0],protected,qualification)
   else:validate_publisher(pm[0][0],protected,qualification)
 for path in paths:
  p=physical(path);snap=lock_snapshot(p);pending(snap,p)
  if not snap['held']:
   observations.append(dict(path=str(p),state='KERNEL_READONLY_SNAPSHOT_FREE',known_pending=len(snap['waiting'])));continue
  need(len(snap['held'])==1 and exact_write(snap['held'][0]),'UNKNOWN_POSIX_SHARED_OR_MULTIPLE_HELD')
  original=snap['held'][0]['pid'];cm,pm=match(original,p);failure=None
  for attempt in range(4):
   try:
    if cm:
     r,c,l=cm[0];validate_capture(r,protected,qualification);owner_lock(l,p)
    else:
     r,c=pm[0];validate_publisher(r,protected,qualification);publisher_lock(c,p)
    observations.append(dict(path=str(p),state='EXACT_ROOT_WRITER_CURRENT_OFD',owner_pid=original));break
   except (RuntimeError,OSError)as e:
    failure=e;fresh=lock_snapshot(p);pending(fresh,p)
    # No active probing or lock mutation: the only evidence is a fresh,
    # fully parsed kernel table snapshot after a known writer released.
    if not fresh['held']:
     observations.append(dict(path=str(p),state='KNOWN_WRITER_RELEASED_READONLY_KERNEL_FREE',previous_owner_pid=original,known_pending=len(fresh['waiting'])));break
    need(len(fresh['held'])==1 and exact_write(fresh['held'][0])and fresh['held'][0]['pid']==original,'WRITER_CHANGED_OR_UNKNOWN_WHILE_HELD')
    if attempt==3:raise failure
    time.sleep(.01)
  else:raise RuntimeError('PIPELINED_POST_HOLD_BOUNDED_LOCK_OBSERVATION')
 return dict(status='PASS_EXACT_CURRENT_LOCK_DOMAIN',observation_mode='READ_ONLY_PROC_LOCKS_NO_FLOCK_PROBE',observations=observations)

def expected_asset_leases(a,qualification=False,run=None):
 job=a['post_asset_job_id'];need(re.fullmatch('[A-Za-z0-9_]{1,100}',job),'VALIDATED_JOB_ID')
 root=Path(a['asset_control_root'])
 if qualification:need(run is not None and physical(root).is_relative_to((Path(__file__).parent/'fixtures').resolve()),'PRIVATE_FIXTURE_CONTROL')
 else:need(root==CONTROL/'asset_operations'/job,'FIXED_PER_ASSET_CONTROL')
 return {'ASSET_POST':str(root/'POST.lock'),'ASSET_CAPTURE_EXCLUSION':str(root/'CAPTURE.lock')}
def outer_admit(a,scope_ref,qualification=False,run=None):
 need(a['pipelined_protocol']=='ROOT_FROZEN_READONLY_ASSET_POST_V1'and a['status']=='ROOT_APPROVED_PIPELINED_FINITE_COMPLETION_V1','PROTOCOL_AND_ROOT_STATUS')
 need(a['authorize_exact_dynamic_inner_grants']is True,'NO_SELF_AUTHORIZATION')
 if not qualification:rawref(scope_ref,True,False)
 need(a['original_72h_absolute_deadline_unix']==ORIGINAL_DEADLINE,'ORIGINAL_DEADLINE')
 policy=rawref(a['resource_ref']);extra=6*2**30 if a['admitted_capture_proof_refs']else 0
 need(policy['scope_id']==a['scope_id']and policy['own_RAM_bytes']>=a['approved_profile_matrix'][a['selected_profile']]['worst_AS_bytes']+extra,'NATIVE_POST_PLUS_CAPTURE_6G_RAM_SEPARATE_FROM_REMOTE20G')
 need(a['selected_profile']in ['CPU2','CPU4','CPU8']and a['approved_profile_matrix'][a['selected_profile']]['worst_AS_bytes']<=(28*2**30),'RAM28G_MAX')
 frozen=rawref(a['frozen_source_proof_ref'],True,qualification)
 need(frozen['schema']=='ROOT_FROZEN_READ_ONLY_POST_ASSET_V1'and frozen['source_mode']=='FrozenReadOnly'and frozen['source_KEEP']is True,'FROZEN_READ_ONLY_PROOF')
 need(frozen['job_id']==a['post_asset_job_id']and frozen['snapshot_ref']==a['base_spec']['snapshot_ref']and frozen['source_root']==a['base_spec']['source_root'],'EXACT_F9_SOURCE_PROOF')
 rawref(frozen['snapshot_ref'])
 # Migration evidence is separately Root-issued only after bounded cooperative old-owner closure.
 migration=rawref(a['migration_closed_proof_ref'],True,qualification)
 need(migration['schema']=='ROOT_POST_OLD_CONTROLLER_CLOSED_V1'and migration['all_owned_closed']is True and migration['original_global_AUTH_absent']is True and migration['no_hot_replace']is True ,'OLD_MIGRATION_CLOSED')
 oldclosed=rawref(migration['old_controller_closed_ref'])
 need(oldclosed['status']=='ALL_OWNED_CLOSED_BEFORE_LAST_FD_CLOSE'and oldclosed['owner'][0]==migration['old_owner']['pid']and str(oldclosed['owner'][1])==str(migration['old_owner']['start_ticks']),'ACTUAL_OLD_CONTROLLER_RECEIPT_DISTINCT_FROM_ROOT_PROOF')
 if not qualification:need(not(CONTROL/'ROOT_STREAMCLUSTER_CPU_RESUME_EXEC_APPROVAL_V2.json').exists(),'LEGACY_AUTH_ACTUALLY_ABSENT')
 need(proc(migration['old_owner']['pid'])is None or proc(migration['old_owner']['pid'])['start_ticks']!=str(migration['old_owner']['start_ticks']),'OLD_OWNER_STILL_LIVE')
 source=physical(frozen['source_root']);private=physical(a['private_output_parent']);need(qualification or private==Path(__file__).parent/'runs'/a['scope_id'],'EXACT_NEW_POST_RUN');closed=[physical(v)for v in a['closed_adoption_output_roots']]
 need(not overlap(source,private),'POST_SOURCE_OUTPUT_INTERSECTION')
 if not qualification:need(source.is_relative_to(NAS.resolve())and private.is_relative_to(NAS.resolve()),'POST_NAS_ONLY')
 authority=Path(a['private_inner_AUTH_path']);need(authority.parent.resolve()==private and authority.name=='PRIVATE_POST_AUTH.json','PRIVATE_AUTH_ONLY')
 leases=expected_asset_leases(a,qualification,run)
 for p in leases.values():physical(p)
 check_global(a,[source,private,*closed],qualification)
 return frozen
def selected_admit(spec,work,grant_ref,qualification=False):
 # Called only for production; CPU fixtures exercise this helper separately.
 g=rawref(grant_ref)
 scope_ref=g['pipelined_root_scope_ref'];a=rawref(scope_ref,True,qualification)
 need(g['schema']=='ROOT_STREAMCLUSTER_PIPELINED_CPU_POST_V1'and g['status']=='ROOT_APPROVED_REMAINING_BATCH_V1','NEW_INNER_SCHEMA')
 need(g['completion_scope_raw_sha256']==scope_ref['sha256']and g['spec_sha256']==hashlib.sha256((json.dumps(spec,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest(),'PINNED_SCOPE_SPEC')
 need(Path(grant_ref['path'])==Path(a['private_inner_AUTH_path'])and g['work_root']==str(work),'PRIVATE_AUTH_WORK')
 outer_admit(a,scope_ref,qualification,Path(work))
 need({x['role']:x['path']for x in spec['leases']}==expected_asset_leases(a,qualification,Path(work)),'EXACT_ASSET_LEASES')
 need(spec['source_root']==a['base_spec']['source_root']and spec['snapshot_ref']==a['base_spec']['snapshot_ref'],'EXACT_FROZEN_SOURCE')
 need(spec['workers']==a['base_spec']['workers']and spec['cpu_ids']==a['base_spec']['cpu_ids'],'EXACT_CPU')
 mf=rawref(a['code_manifest_ref']);need(a['code_manifest_ref']['sha256']==a['code_sha256'],'EXACT_CODE_MANIFEST')
 for name,row in mf['files'].items():
  q=Path(__file__).parent/name;need(q.resolve().is_relative_to(Path(__file__).parent.resolve())and q.stat().st_size==row['bytes']and hashlib.sha256(q.read_bytes()).hexdigest()==row['sha256'],'FRESH_CODE')
 need(sorted(os.sched_getaffinity(0))==sorted(spec['cpu_ids'])and os.getpriority(os.PRIO_PROCESS,0)>=15,'EXACT_AFFINITY_NICE')
 need(g['code_manifest_sha256']==a['code_sha256']and g['original_72h_absolute_deadline_unix']==ORIGINAL_DEADLINE,'PINNED_CODE_DEADLINE')
 need(g['not_before_unix']<=time.time()<g['absolute_deadline_unix']<=ORIGINAL_DEADLINE and g['absolute_deadline_unix']-g['not_before_unix']<=a['attempt_seconds'],'INNER_DEADLINE')
 return a,g
def periodic(a,qualification=False):
 source=physical(a['base_spec']['source_root']);private=physical(a['private_output_parent']);closed=[physical(v)for v in a['closed_adoption_output_roots']]
 return check_global(a,[source,private,*closed],qualification)
