
import pathlib,os,sys,subprocess,json,hashlib,time,stat,datetime
os.nice(19)
subprocess.run(['ionice','-c','3','-p',str(os.getpid())],capture_output=True,check=True)
P=[{'model_slug': 'qwen2.5-7b-instruct-raw', 'revision': 'a09a35458c702b33eeacc393d103063234e8bc28', 'source_original_path': '/workspace/c16_assets/c16-a/metadata/Qwen__Qwen2.5-7B-Instruct__a09a35458c702b33eeacc393d103063234e8bc28/model-00004-of-00004.safetensors', 'source_outbound_path': '/workspace/c16_exchange/autodl_wave1/outbound/C16_GPU_PACKAGE_P2_168c9714/models/c16_qwen25_7b_raw_reference/model-00004-of-00004.safetensors', 'candidate_path': '/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/qwen2.5-7b-instruct-raw/a09a35458c702b33eeacc393d103063234e8bc28/model-00004-of-00004.safetensors', 'expected_size': 3556377672, 'expected_sha256': '1a72d403cdf0c1ec3cb7f289f17b394a01e64394c2e9b3c0f94dbce3faf879bd', 'receipt_path': '/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/qwen2.5-7b-instruct-raw/a09a35458c702b33eeacc393d103063234e8bc28/MODEL_ARCHIVE_RECEIPT.json', 'expected_receipt_sha256': 'cee32868231b30f42f71fa89e523069b09d6a20455730825b70b5cfbc9411b0c', 'pinned_current_projected_identity': {'dev': 39, 'inode': 76328941, 'nlink': 1, 'size': 3556377672, 'uid': 1011, 'gid': 1011, 'mode': 511, 'mtime_ns': 1789226713000000000, 'ctime_ns': 1789226713000000000}, 'kind': 'SCIENTIFIC_MODEL_SHARD'}, {'model_slug': 'qwen2.5-7b-instruct-awq', 'revision': 'b25037543e9394b818fdfca67ab2a00ecc7dd641', 'source_original_path': '/workspace/c16_assets/c16-a/metadata/Qwen__Qwen2.5-7B-Instruct-AWQ__b25037543e9394b818fdfca67ab2a00ecc7dd641/model-00001-of-00002.safetensors', 'source_outbound_path': '/workspace/c16_exchange/autodl_wave1/outbound/C16_GPU_PACKAGE_P3_168c9714/models/c16_qwen25_7b_awq/model-00001-of-00002.safetensors', 'candidate_path': '/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/qwen2.5-7b-instruct-awq/b25037543e9394b818fdfca67ab2a00ecc7dd641/model-00001-of-00002.safetensors', 'expected_size': 3996422976, 'expected_sha256': '4ad6e70f93823a9228931615e04b5e9293854c236fb4bd5f85e27f3b600605ad', 'receipt_path': '/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/qwen2.5-7b-instruct-awq/b25037543e9394b818fdfca67ab2a00ecc7dd641/MODEL_ARCHIVE_RECEIPT.json', 'expected_receipt_sha256': '4675e78cd8d0ef6b2657be4998b258ade054a87615f168048cf6d27d93360cb7', 'pinned_current_projected_identity': {'dev': 39, 'inode': 76328944, 'nlink': 1, 'size': 3996422976, 'uid': 1011, 'gid': 1011, 'mode': 511, 'mtime_ns': 1789229111000000000, 'ctime_ns': 1789229111000000000}, 'kind': 'SCIENTIFIC_MODEL_SHARD'}, {'model_slug': 'qwen2.5-7b-instruct-awq', 'revision': 'b25037543e9394b818fdfca67ab2a00ecc7dd641', 'source_original_path': '/workspace/c16_assets/c16-a/metadata/Qwen__Qwen2.5-7B-Instruct-AWQ__b25037543e9394b818fdfca67ab2a00ecc7dd641/model-00002-of-00002.safetensors', 'source_outbound_path': '/workspace/c16_exchange/autodl_wave1/outbound/C16_GPU_PACKAGE_P3_168c9714/models/c16_qwen25_7b_awq/model-00002-of-00002.safetensors', 'candidate_path': '/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/qwen2.5-7b-instruct-awq/b25037543e9394b818fdfca67ab2a00ecc7dd641/model-00002-of-00002.safetensors', 'expected_size': 1574406784, 'expected_sha256': '920a8cc9d3c81668f18014a69bb041ab8bab22a31640a713f90f5e7580e2f126', 'receipt_path': '/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/qwen2.5-7b-instruct-awq/b25037543e9394b818fdfca67ab2a00ecc7dd641/MODEL_ARCHIVE_RECEIPT.json', 'expected_receipt_sha256': '4675e78cd8d0ef6b2657be4998b258ade054a87615f168048cf6d27d93360cb7', 'pinned_current_projected_identity': {'dev': 39, 'inode': 76328945, 'nlink': 1, 'size': 1574406784, 'uid': 1011, 'gid': 1011, 'mode': 511, 'mtime_ns': 1789218866000000000, 'ctime_ns': 1789218866000000000}, 'kind': 'SCIENTIFIC_MODEL_SHARD'}];RATE=8*1024**2;CAP=64*1024**2
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'
started=time.monotonic();total=0;done=[]
def identity(s):return dict(dev=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,size=s.st_size,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)
def emit(x):print(json.dumps(x),flush=True)
def check():
 m=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164','-o','TARGET,SOURCE,FSTYPE'],text=True))['filesystems'][0]
 assert (m['target'],m['source'],m['fstype'])==('/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs')
 sv=os.statvfs('/root/share');mem=int(next(l.split()[1] for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
 cgmax=pathlib.Path('/sys/fs/cgroup/memory.max').read_text().strip();cgcur=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())
 io=pathlib.Path('/proc/pressure/io').read_text();some=float(io.splitlines()[0].split('avg10=')[1].split()[0])
 full=float(io.splitlines()[1].split('avg10=')[1].split()[0]);assert mem>=64*1024**3 and sv.f_bavail*sv.f_frsize>=40*1024**3
 assert cgmax=='max' or int(cgmax)-cgcur>=64*1024**2
 # Explicit latest user amendment: PSI is recorded only; no fixed10 rejection.
 return dict(MemAvailable_bytes=mem,Share_available_bytes=sv.f_bavail*sv.f_frsize,io_some_avg10=some,io_full_avg10=full)
def guarded_chunk_resource():
 # A bounded pause retains this open FD/digest instead of re-reading a prefix.
 # It is part of this finite hash job, never a resident watcher. All thresholds
 # stay unchanged, and Source leases are rechecked before resuming any read.
 paused=False;pause_start=time.monotonic()
 while True:
  try:resource=check();break
  except AssertionError as error:
   if str(error)!='CURRENT_IO_PRESSURE_HOLD':raise
   if not paused:emit(dict(event='IO_PAUSE',reason=str(error),max_pause_seconds=120,payload_read_during_pause=0));paused=True
   assert time.monotonic()-pause_start<120,'CURRENT_IO_PRESSURE_HOLD_AFTER_BOUNDED_PAUSE'
   time.sleep(5)
 if paused:
  emit(dict(event='RESOURCE_READY',resource=resource))
  assert json.loads(sys.stdin.readline())['action']=='CONTINUE','SOURCE_RESOURCE_HOLD'
 return resource
try:
 for item in P:
  p=pathlib.Path(item['candidate_path']);assert all(not q.is_symlink() for q in [p,*p.parents])
  s=p.lstat();before=identity(s);assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size==item['expected_size']
  assert before==item['pinned_current_projected_identity'],'PINNED_CURRENT_IDENTITY_DRIFT_HOLD'
  resource_before=check()
  emit(dict(event='FILE_READY',path=str(p),kind=item['kind'],identity=before,resource=resource_before,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
  command=json.loads(sys.stdin.readline());assert command['action']=='CONTINUE','SOURCE_RESOURCE_HOLD'
  fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW);h=hashlib.sha256();offset=0
  with os.fdopen(fd,'rb',buffering=0) as f:
   assert identity(os.fstat(f.fileno()))==before
   while offset<s.st_size:
    resource=guarded_chunk_resource();remaining=min(CAP,s.st_size-offset);segment_start=time.monotonic();segment=0
    while segment<remaining:
     b=f.read(min(1024**2,remaining-segment));assert b,'UNEXPECTED_EOF';h.update(b);offset+=len(b);segment+=len(b);total+=len(b)
     time.sleep(max(0,segment/RATE-(time.monotonic()-segment_start)))
    assert identity(os.fstat(f.fileno()))==before and identity(p.lstat())==before,'MODEL_IDENTITY_DRIFT_HOLD'
    emit(dict(event='PROGRESS',path=str(p),kind=item['kind'],offset=offset,total_read_bytes=total,resource=resource))
    command=json.loads(sys.stdin.readline());assert command['action']=='CONTINUE','SOURCE_RESOURCE_HOLD'
   assert f.read(1)==b''
  digest=h.hexdigest();assert digest==item['expected_sha256'],'FULL_SHA_MISMATCH_HOLD'
  row=dict(item,actual_sha256=digest,bytes_hashed=offset,read_range_start=0,read_range_end_exclusive=offset,resource_before=resource_before,resource_after=check(),status='FULL_SHA256_MATCH',full_hash_pass_count=1,observed_projected_stat_before=before,observed_projected_stat_after=identity(p.lstat()),native164_path=str(p).replace('/root/share/mnt164','/home/shared',1),uid_gid_mode_source='SSHFS_PROJECTED_NOT_REMOTE_NATIVE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
  done.append(row);emit(dict(event='FILE_DONE',record=row))
 emit(dict(event='COMPLETE',records=done,elapsed_seconds=time.monotonic()-started,all_payload_writes=0,source_files_modified_or_deleted=0,models_hashed=sum(x['kind']=='SCIENTIFIC_MODEL_SHARD' for x in done),rate_cap_bytes_per_second=RATE,single_file_stream=True))
except Exception as e:
 emit(dict(event='HOLD',reason=type(e).__name__+': '+str(e),completed_records=done,elapsed_seconds=time.monotonic()-started,partial_stream_may_exist=True,payload_writes=0))
 raise
