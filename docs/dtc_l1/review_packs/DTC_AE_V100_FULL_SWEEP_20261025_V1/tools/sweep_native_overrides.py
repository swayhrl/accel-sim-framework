# These definitions deliberately supersede only admission/authority plumbing in
# the pinned native launcher. The simulator, argv, exact BA runtime class and
# one-start journal remain unchanged.
import gzip
REQUEST='DTC_AE_V100_FULL_SWEEP_20261025_V1'
TERMINAL_PEER_STATES={'COMPLETE','CLOSED','STOP_UNACCEPTED','COMPAT_PARTIAL_COMPLETE'}
def compressed_stream(path):
 disk=P(path).open('xb');stream=gzip.GzipFile(fileobj=disk,mode='wb',mtime=0);stream._native_disk=disk;return stream
def close_compressed(stream):
 disk=stream._native_disk;stream.close();disk.flush();os.fsync(disk.fileno());disk.close()
def read_current_authority():
 with (NATIVE/'control/science_authority/REGISTRY_UPDATE.lock').open('rb') as held:
  fcntl.flock(held,fcntl.LOCK_SH)
  reg=NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';r=read(reg);e=read(NATIVE/'control/CURRENT_SCIENCE_EPOCH.json')
  require(sha(reg)==e['native_registry_sha256'],'registry/epoch hash mismatch')
  return r,e
def authority_consistent():read_current_authority();return True
def assert_batch_lease():
 lease=read(ROOT/'control/BATCH_LEASE.json');p=P('/proc')/str(lease['pid'])
 require(p.exists() and int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==lease['start_ticks'],'batch lease generation gone')
 require(lease['request']==REQUEST and 'sweep_controller.py' in (p/'cmdline').read_bytes().replace(b'\0',b' ').decode(),'batch lease owner mismatch')
 require(os.readlink(p/'fd'/str(lease['fd']))==str(NATIVE/'control/qualification_ledger/NATIVE_QUALIFICATION.lock'),'global qualification lease FD mismatch')
 require('FLOCK' in (p/'fdinfo'/str(lease['fd'])).read_text(),'global qualification lease not held')
 pid=os.getpid();ancestors=[]
 for _ in range(20):
  if pid<=1:break
  ancestors.append(pid)
  if pid==lease['pid']:break
  pid=int((P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[1])
 require(lease['pid'] in ancestors,'model operation not descended from the one finite native batch controller')
 return lease
def spec_for(cohort):
 require(cohort in COHORTS,'cohort outside frozen complete-input matrix')
 p=ROOT/'control'/(cohort+'_SPEC.json');s=read(p)
 r,e=read_current_authority();q=r['registered_future_requests'][REQUEST]
 require(q['admitted_specs'].get(cohort)==sha(p) and s['request']==REQUEST and s['project']=='DTC','spec not exact-current-qualified and admitted')
 require(s['input_digest'] in read(ROOT/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['input_digests'],'input outside finite request')
 return s
def check_input(s):
 p=ROOT/'control/input_bindings'/(s['input_digest']+'.json');require(sha(p)==s['input_binding_sha256'],'whole-input qualification binding drift')
 b=read(p);d=b['qualification'];require(d['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS' and not d['issues'],'unresolved input-domain HOLD')
 entry=P(d['trace_entry']);require(sha(entry)==b['asset']['commandlist_sha256'],'commandlist SHA drift')
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(entry)],text=True))['filesystems'][0]
 require(fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared','genuine164 input mount mismatch')
 for row in d['rows']:
  p=P(row['path']);st=p.stat();require([st.st_size,st.st_mtime_ns]==row['full_SHA_current_size_mtime'],'post-fullSHA input size/mtime drift')
  with p.open('rb') as f:require(bool(f.read(1)),'unreadable full-SHA member')
 return {'status':'CURRENT_FULL_BODY_SHA_BOUND_GENUINE164_INPUT','input_digest':s['input_digest'],'kernels':len(d['rows']),'binding_sha256':sha(ROOT/'control/input_bindings'/(s['input_digest']+'.json')),'FUSE_inode':'Informational only; current whole contentSHA and immutable object member identities are the evidence, old inode validators untouched','native_values':'UNPROVEN'}
def resources(s,fresh_source=False):
 v=os.statvfs(ROOT);free=v.f_bavail*v.f_frsize
 mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 cur=int(P('/sys/fs/cgroup/memory.current').read_text());maximum=P('/sys/fs/cgroup/memory.max').read_text().strip()
 r,e=read_current_authority();q=r['registered_future_requests'][REQUEST];peers=[]
 for key,row in r['registered_future_requests'].items():
  if key==REQUEST or row.get('state') in TERMINAL_PEER_STATES:continue
  extra=row.get('reserved_write_bytes');require(type(extra) is int and extra>=0,'unknown foreign write reservation');peers.append({'request':key,'reserved_write_bytes':extra})
 # Reserve remaining live result growth plus full future native restore. Completed
 # bytes are already in df; queued/unstarted inputs may wait and are not double counted.
 own=GIB;live=[]
 for cell,row in q['consumed'].items():
  out=ROOT/'DTC/run/results'/row['uuid'];done=row.get('execution_receipt')
  if (ROOT/'control'/(cell+'_ARCHIVE_RECEIPT.json')).exists():continue
  size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) if out.exists() else 0
  if done:reserve=size+16*MIB
  else:
   cap=read(ROOT/'control'/(cell+'_SPEC.json'))['limits']['max_result_directory_bytes'];reserve=max(0,2*cap-size)
  own+=reserve;live.append({'cohort':cell,'remaining_write_and_restore_bytes':reserve})
 if fresh_source and s['cohort'] not in q['consumed']:
  reserve=2*s['limits']['max_result_directory_bytes'];own+=reserve;live.append({'cohort':s['cohort'],'new_candidate_reservation_bytes':reserve})
 peer=sum(x['reserved_write_bytes'] for x in peers);required=5*GIB+own+peer
 return {'utc':now(),'native_free_bytes':free,'free_inodes':v.f_favail,'host_MemAvailable_bytes':mem,'cgroup_memory_current':cur,'cgroup_memory_max':maximum,'required_free_bytes':required,'local_safety_floor_bytes':5*GIB,'bounded_own_remaining_write_and_restore_bytes':own,'own_reservations':live,'peer_reservations':peers,'other_outstanding_write_reservations_bytes':peer,'physical_RAM_pass':mem>=128*GIB and (maximum=='max' or int(maximum)-cur>=96*GIB),'physical_disk_pass':free>required and v.f_favail>=100000 and own<=q['reserved_write_bytes'],'fresh_local_resource_sample':True,'storage_basis':'5GiB fast-tier margin plus known pending writes only;genuine164 bulk inputs/cold assets not duplicated;each new job admitted separately'}
def prepare(cohort):
 s=spec_for(cohort);host=identity();r,e=read_current_authority();q=r['registered_future_requests'][REQUEST]
 require(q['spec_request_sha256']==sha(ROOT/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json') and q['controller_sha256']==sha(__file__),'request or qualified launcher drift')
 require(q['state'] in ['ARMED','RUNNING'] and cohort not in q['consumed'] and cohort not in q['sealed'],'consumed/sealed cell cannot run')
 require(set(q['consumed'])=={p.name.removesuffix('.INTENT.json') for p in (ROOT/'control/qualification_ledger').glob('E2-AEV100-*.INTENT.json')},'central intent accounting mismatch')
 for row in s['runtime_files']:
  p=ROOT/row['target'];require(str(p.resolve())==row['actual_realpath'] and sha(p)==row['sha256'],'runtime/config file drift')
 for kind,commit in [('core',s['core_commit']),('framework',s['framework_commit'])]:
  require(subprocess.check_output(['git','-C',str(ROOT/kind),'rev-parse','HEAD'],text=True).strip()==commit,'source HEAD drift')
  require(not subprocess.check_output(['git','-C',str(ROOT/kind),'status','--porcelain'],text=True).strip(),'source worktree dirty')
 for row in q['shared_tool_pins']:require(sha(row['path'])==row['sha256'],'pinned guard/parser dependency drift')
 asset=check_input(s);res=resources(s,True);require(res['physical_RAM_pass'] and res['physical_disk_pass'],'RESOURCE_HOLD_NO_START')
 return {'status':'SWEEP_EXACT_REGISTERED_PREPARE_PASS_NO_START','cohort':cohort,'identity':host,'resources':res,'asset':asset,'request':REQUEST,'scientific_starts':0}
def exclusive(p,obj):
 if P(p).name.endswith('.INTENT.json') and obj.get('cohort') in COHORTS:
  lease=assert_batch_lease();obj=dict(obj,batch_lease_pid=lease['pid'],batch_lease_start_ticks=lease['start_ticks'])
  def consume(r):
   q=r['registered_future_requests'][REQUEST];cohort=obj['cohort']
   require(q['remaining']>0 and cohort not in q['consumed'] and cohort not in q['sealed'],'cell not unused')
   _original_exclusive(p,obj)
   q['consumed'][cohort]={'uuid':obj['uuid'],'intent':str(P(p).resolve()),'intent_sha256':sha(p),'charged':1};q['remaining']-=1;q['state']='RUNNING'
  update_authority(consume)
 else:_original_exclusive(p,obj)
def finish_cell(cohort):
 receipt=run_native(cohort)
 def closed(r):
  q=r['registered_future_requests'][REQUEST];q['consumed'][cohort]['execution_receipt']=receipt
  q['state']='RUNNING' # A failed independent cell never refunds credit or erases peers.
 update_authority(closed);return receipt
