"""Exact2 existing ADA7 multistream full-record+5D data POST. No GPU/model/archive/public."""
from pathlib import Path
import os,sys,json,hashlib,time,resource,fcntl,types,signal,subprocess,stat
D=Path(__file__).resolve().parent;G=2**30
NB='/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1';RB='/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080'
QIDS=['ORD_EXT_concurrentKernels_040064f4f577_A001','ORD_EXT_concurrentKernels_3addcdfd75b6_A001']
SCHEMA='ROOT_TINY2_PER_KERNEL_MULTISTREAM_NAS_CPU1_SCOPE_V1';APPROVED='ROOT_APPROVED_CPU_ONLY_TINY2_PER_KERNEL_POST_NO_MODEL'
def need(v,m):
 if not v:raise RuntimeError(m)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
def rawjson(p,cap=4*2**20):
 p=Path(p);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode)and 0<=a.st_size<=cap,'BOUNDED_REGULAR_JSON');blocks=[];n=0
  while True:
   b=os.read(fd,min(65536,cap+1-n))
   if not b:break
   n+=len(b);need(n<=cap,'JSON_BOUND');blocks.append(b)
  z=os.fstat(fd);sig=lambda q:(q.st_dev,q.st_ino,q.st_size,q.st_mtime_ns,q.st_ctime_ns);need(sig(a)==sig(z),'SAME_FD_JSON')
 finally:os.close(fd)
 b=b''.join(blocks);return b,json.loads(b)
def save(p,x):
 with Path(p).open('x')as f:json.dump(x,f,indent=2,sort_keys=True);f.write(chr(10));f.flush();os.fsync(f.fileno())
def ref(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def scope_metadata(sp,h,metadata_only=False):
 sb,a=rawjson(sp);need(hashlib.sha256(sb).hexdigest()==h,'SCOPE_RAW_SHA')
 need(a['schema']==SCHEMA and a['status']==('UNAPPROVED_METADATA_PREFLIGHT_ONLY'if metadata_only else APPROVED),'EXACT_ROOT_SCOPE_MODE')
 need(a['runtime_root']==a['remote_runtime_root']==str(D) and a['qids']==QIDS,'EXACT_TINY2_NAMESPACE_ONLY')
 need(a['cpu_ids']==[4]and a['own_hard_bytes']==2*G and a['peer_reserved_bytes']==28*G,'FIXED_CPU1_HARD2_PEER28')
 need(a['control_transport']=='SSH_STDIN_LIGHT_CONTROL_V1'and a['owned_lease_type']=='ROOT_PRIVATE_MEMFD_FLOCK_NO_GLOBAL_CPU6'and a['control_channel_sha256']=='63a962a8f9bda7ebb652f07ec143d519d632f98006c540c39e6691b8a6bcda7f','APPROVED_V2_CONTROL_PRIVATE_FD')
 need(a['not_before_unix']<=time.time()<a['absolute_deadline_unix']<=a['not_before_unix']+900 and a['absolute_deadline_unix']<=1793241315,'FINITE900_ORIGINAL_BOUND')
 need(__import__('socket').gethostname()==a['remote_host']and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==a['remote_boot_id'],'ACTUAL_REMOTE_HOST_BOOT')
 mb,mf=rawjson(D/'CODE_MANIFEST.json');need(hashlib.sha256(mb).hexdigest()==a['code_manifest_sha256'],'CODE_MF')
 for n,r in mf['files'].items():need((D/n).stat().st_size==r['bytes']and sha(D/n)==r['sha256'],'CODE_METADATA_PIN_'+n)
 def get(n):
  r=mf['files'][n];b=(D/n).read_bytes();need(len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256'],'SAME_RAW_CODE_PIN')
  m=types.ModuleType(n);m.__file__=str(D/n);exec(compile(b,str(D/n),'exec'),m.__dict__);return m
 _,data=rawjson(D/'EXACT_TINY2_DATA_V1.json');need(data['qids']==QIDS and len(data['rows'])==2,'EXACT_TWO_DATA_ROWS')
 V=get('validate_captured4_per_kernel_multistream_v2.py')
 for i,c in enumerate(data['rows']):
  need(c['qid']==QIDS[i]and c['header_count']==9 and c['declared_source_records']==[14197,14541][i],'EXACT_TINY_COUNTS')
  v=V.identity_guard(c['qid'],Path(c['source_root']),Path(c['map_ref']['path']))
  need(c['binary_sha256']==v['task_identity']['binary_sha256']and c['argv']==v['task_identity']['argv']and c['stream_ids']==v['header_contract']['stream_ids'],'TINY_SOURCE_BINARY_ARGV_STREAM_BIND')
  V._pinned_json(v['header_contract']['source_census_ref'])
 return a,mf,data,get
def main():
 metadata_only=len(sys.argv)==4 and sys.argv[1]=='--check-metadata'
 args=sys.argv[2:]if metadata_only else sys.argv[1:];need(len(args)==2,'EXACT_SCOPE_PATH_RAW_SHA')
 a,mf,data,get=scope_metadata(Path(args[0]),args[1],metadata_only)
 if metadata_only:
  print(json.dumps(dict(status='PASS_UNAPPROVED_METADATA_ONLY_NO_POST',rows=2,declared_records=[14197,14541],qids=QIDS,no_service_reader_memfd_output_or_body=True)));return
 os.sched_setaffinity(0,{4});os.nice(15);resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(512*2**20,2*G))
 R=get('cpu1_nas_resource_v1.py');cg=R.service();need((cg/'memory.oom.group').read_text().strip()=='1','OOM_GROUP1');need(str(cg).endswith('/ep-tiny2-perkernel-'+a['run_id']+'.service'),'EXACT_SERVICE')
 fd=os.memfd_create('TINY2_OWNED_CPU_POST_LEASE',os.MFD_ALLOW_SEALING);os.fchmod(fd,0o600);st=os.fstat(fd);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);os.set_inheritable(fd,True)
 O=get('owned_runtime_v1.py');O.set_subreaper();me=O.ident(os.getpid());out=D/'runs'/a['run_id'];need(not out.exists(),'FRESH_OUTPUT');out.mkdir(parents=True)
 desc=dict(guard=me,scope_sha256=args[1],run_id=a['run_id'],code_manifest_sha256=a['code_manifest_sha256'],cgroup=str(cg),output_root=str(out),exact_jobs=QIDS,private_owned_fd=dict(type='ROOT_PRIVATE_MEMFD_FLOCK',dev=st.st_dev,inode=st.st_ino,uid=st.st_uid,mode=st.st_mode&0o777,name='TINY2_OWNED_CPU_POST_LEASE'))
 env=dict(PATH='/usr/bin:/bin',HOME='/home/huangrulin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',CFI_CPU6_SLOT_FD=str(fd),CFI_CPU6_SLOT_DESC=json.dumps(desc))
 Wire=get('ssh_stdin_light_control_v2.py');reader=Wire.RemoteReader(0,args[1],a['run_id']);samples=out/'resource_samples';samples.mkdir();refs=[];summary={};last=0;error=None
 def checkpoint():
  nonlocal last,summary
  need(time.time()<a['absolute_deadline_unix'],'ABSOLUTE_CPU_DEADLINE');reader.check();need(__import__('shutil').disk_usage(D).free>=10*G,'NAS_FLOOR10G')
  if time.monotonic()-last>=1:
   v=R.fresh(cg,a['peer_reserved_bytes']);last=time.monotonic();need(len(refs)<1024,'BOUNDED_RESOURCE_REFS')
   p=samples/('RESOURCE_%04d.json'%len(refs));save(p,v);refs.append(ref(p));summary={k:v[k]for k in ['available_bytes','own_current_bytes','own_hard_bytes','EP_reserved_bytes','physical_headroom_bytes','required_remaining_plus_peer_floor','PASS']};summary['sample_ref']=refs[-1];need(v['PASS'],'REAL_RAM_ANCESTOR_OOM_PSI')
 def child(mode,case,label,*extra):
  checkpoint();e=dict(env);e['CFI_WORKER_BIRTH_RECEIPT']=str(out/(label+'.BIRTH.json'))
  def limits():resource.setrlimit(resource.RLIMIT_AS,(1536*2**20,1536*2**20))
  with(out/(label+'.stdout.log')).open('xb')as so,(out/(label+'.stderr.log')).open('xb')as se:
   p=subprocess.Popen(['/usr/bin/python3','-I','-S','-B',str(D/'fixed_tiny2_phase_worker_v1.py'),mode,case,*map(str,extra)],stdout=so,stderr=se,stdin=subprocess.DEVNULL,env=e,pass_fds=(fd,),preexec_fn=limits,start_new_session=True)
   try:
    while p.poll()is None:checkpoint();time.sleep(.2)
    need(p.wait()==0,'EXACT_PHASE_FAILED_'+label)
   except BaseException:
    if p.poll()is None:
     who=O.ident(p.pid)
     if who is not None:O.send(who,signal.SIGTERM)
     try:p.wait(timeout=5)
     except subprocess.TimeoutExpired:
      if who is not None:O.send(who,signal.SIGKILL)
      p.wait(timeout=5)
    raise
  checkpoint()
 try:
  reader.start();reader.wait_ready();checkpoint()
  save(out/'START.json',dict(owner=me,boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),run_id=a['run_id'],scope_sha256=args[1],code_manifest_sha256=a['code_manifest_sha256'],cgroup=str(cg),CPU=[4],noGPU=True,no_model=True,CPU_slot=dict(type='ROOT_PRIVATE_MEMFD_FLOCK',path=os.readlink('/proc/self/fd/'+str(fd)),fd=fd,dev=st.st_dev,inode=st.st_ino,actual_fdinfo=Path('/proc/self/fdinfo/'+str(fd)).read_text())))
  case_results=[]
  for ci,c in enumerate(data['rows']):
   caseout=out/c['qid'];caseout.mkdir();child('VALIDATE',c['qid'],'VALIDATE_'+str(ci),caseout)
   _,v=rawjson(caseout/'PER_KERNEL_RECORD_VALIDATION.json');need(v['status']=='PER_KERNEL_MULTISTREAM_FULL_RECORD_CHECKS_PASS'and v['strict_single_stream_ordinary']is False and v['full_application_concurrent_model']is False,'NEW_TYPED_PER_KERNEL_RESULT_ONLY')
   grouped=caseout/'grouped';grouped.mkdir();receipts=[];grouprefs=[];mapping={}
   for ki,k in enumerate(v['per_kernel']):
    src=Path(c['source_root'])/'traces'/k['name'];dst=grouped/k['name'].replace('.trace.xz','.traceg.xz');work=caseout/'scratch'/k['name']
    child('GROUP',c['qid'],'GROUP_%d_%d'%(ci,ki),src,dst,work)
    _,gr=rawjson(work/'GROUP_RECEIPT.json');_,state=rawjson(work/'CHECKPOINT.json')
    need(gr['source_sha256']==v['source_files'][str(src)]and gr['records']==k['counts']['sass_records']and gr['ctas']==k['ctas']and gr['warps']==k['warps']and gr['closed_reopened_full_xz_crc']is True,'SOURCE_WHOLESHA_COUNT_SHAPE_AND_GROUPED_CRC_JOIN')
    stream=[s for s in state['header']if s.startswith('-cuda stream id = ')]
    need(len(stream)==1 and int(stream[0].split('=',1)[1])==k['header']['stream_id'],'UNCHANGED5D_RETAINS_PER_KERNEL_STREAM_HEADER')
    receipts.append(dict(kernel=k['name'],original_command_index=k['producer_command_index'],original_kernel_index=k['original_kernel_index'],stream_id=k['header']['stream_id'],group_receipt_ref=ref(work/'GROUP_RECEIPT.json')))
    grouprefs.append(dict(kernel=dst.name,path=str(dst),sha256=gr['grouped_sha256'],POST_whole_SHA_closed=True));mapping[k['name']]=dst.name
   rawlists=list((Path(c['source_root'])/'traces').glob('kernelslist_ctx_*'));need(len(rawlists)==1,'EXACT_ORIGINAL_COMMANDLIST')
   commands=rawlists[0].read_text().splitlines();(grouped/'kernelslist.g').write_text(chr(10).join(mapping.get(x,x)for x in commands)+chr(10))
   _,tapstate=rawjson(caseout/'SAME_PASS_FEATURE_TAP_STATE.json');T=get('post_feature_tap_v1.py');tap=T.FeatureTap(tapstate['max_features'])
   for key in ['features','records','active','inactive','active_unknown']:setattr(tap,key,tapstate[key])
   need(tap.records==v['counts']['sass_records'],'SAME_RECORD_PASS_TAP_COUNT')
   feature=tap.finish(ref(caseout/'PER_KERNEL_RECORD_VALIDATION.json'),ref(grouped/'kernelslist.g'),grouprefs,v['per_kernel'])
   feature.update(profile=v['profile'],record_result_status=v['status'],strict_single_stream_ordinary=False,inter_stream_happens_before='UNKNOWN_NOT_CAPTURED_OR_VALIDATED',producer_command_order_not_CUDA_HB=True,full_application_concurrent_model=False,canonical161_complete=False)
   save(caseout/'ACTUAL_PER_KERNEL_ACTIVE_FEATURE_WITNESS_INDEX.json',feature)
   record=dict(status=v['status'],profile=v['profile'],queue_id=c['qid'],binary_sha256=c['binary_sha256'],argv=c['argv'],stream_ids=v['stream_ids'],kernels=v['kernels'],records=v['counts']['sass_records'],validation_ref=ref(caseout/'PER_KERNEL_RECORD_VALIDATION.json'),index_ref=ref(grouped/'kernelslist.g'),group_receipts=receipts,feature_ref=ref(caseout/'ACTUAL_PER_KERNEL_ACTIVE_FEATURE_WITNESS_INDEX.json'),strict_single_stream_ordinary=False,inter_stream_happens_before='UNKNOWN_NOT_CAPTURED_OR_VALIDATED',command_order='PRODUCER_RECORDED_ONLY_NOT_CUDA_HB',full_application_concurrent_model=False,consumer_qualification=False,whole_input_functional=False,numeric_performance_science_genericCFI=False,actual_input_capsules=False,SourceKEEP=True,release_bytes=0)
   save(caseout/'CPU_RECEIVER.json',record);case_results.append(ref(caseout/'CPU_RECEIVER.json'))
  save(out/'CPU_RESULT.json',dict(status='TINY2_PER_KERNEL_MULTISTREAM_FULL_RECORDS_AND_GROUPS_CLOSED',scope_sha256=args[1],run_id=a['run_id'],code_manifest_sha256=a['code_manifest_sha256'],cases=case_results,strict_single_stream_ordinary=False,inter_stream_happens_before='UNKNOWN_NOT_CAPTURED_OR_VALIDATED',full_application_concurrent_model=False,consumer_qualification=False,whole_input_functional=False,numeric_performance_science_genericCFI=False,actual_input_capsules=False,SourceKEEP=True,release_bytes=0))
 except BaseException as e:
  error=dict(error=repr(e),traceback=__import__('traceback').format_exc(),channel_error=e.as_dict()if isinstance(e,Wire.ChannelError)else None,reader_error_snapshot=reader.error_snapshot());save(out/'CPU_FAILURE_RETAINED.json',error)
 finally:
  if O.children(me):O.cleanup(me)
  O.reap();need(not O.children(me),'OWNED_DESCENDANTS_NOT_CLOSED');reader.finish_after_owned_closed()
  save(out/'RESOURCE_AND_CLOSURE.json',dict(owner=me,boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),scope_sha256=args[1],run_id=a['run_id'],code_manifest_sha256=a['code_manifest_sha256'],tracked_children=[],cgroup=str(cg),resource_snapshot_refs=refs,last_resource_summary=summary,error=error,CPU_slot_closed_after_owned_wait=True,SSH_stdin_reader_joined_after_owned=True,SourceKEEP=True));os.close(fd)
 if error:raise RuntimeError(error['error'])
if __name__=='__main__':main()
