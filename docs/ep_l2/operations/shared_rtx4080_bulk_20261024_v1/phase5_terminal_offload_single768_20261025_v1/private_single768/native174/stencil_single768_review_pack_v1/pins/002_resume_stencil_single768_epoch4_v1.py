"""PRIVATE CANDIDATE. Requires a new exact parent grant; no implicit resume."""
import pathlib,json,hashlib,os,time,fcntl,subprocess,sys,shutil,ctypes
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent
ID='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2';B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1');ROOT=B/'inflight'/ID
VALID=C/(ID+'_FULL_RECORD_VALIDATION_HOT_EPOCH2.json');RETAINED=B/'objects/stage_retained_native_rtx_post_epoch3_tail2_20261025_v1'
def localsha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
grantpath=pathlib.Path(sys.argv[1]);grant=json.loads(grantpath.read_text())
assert grant['status']=='APPROVED_EXACT_STENCIL_LAST2_SINGLE768_EPOCH4'
assert localsha(pathlib.Path(__file__))==grant['controller_sha256']
cp=C/'stencil768_common_v1.py';assert localsha(cp)==grant['common_sha256']
import importlib.util
s=importlib.util.spec_from_file_location('common768',cp);u=importlib.util.module_from_spec(s);s.loader.exec_module(u)
def phase(status,budget=0,**kw):u.replace(C/(ID+'_POST_EPOCH4_STATE.json'),dict(status=status,pid=os.getpid(),ticks=pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],stage_budget=budget,unix=time.time(),**kw))
def queue(status,**kw):
 with(C/'RTX4080_QUEUE.lock').open('a')as f:
  fcntl.flock(f,fcntl.LOCK_EX);rows=json.loads((C/'QUEUE.json').read_text());row=next(r for r in rows if r['id']==ID);row.update(status=status,CPU_post_epoch=4,**kw);u.replace(C/'QUEUE.json',rows)
class Lease:
 def __enter__(self):
  self.fs=[];deadline=time.monotonic()+7200
  try:
   for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
    f=open(C/name,'a');self.fs.append(f)
    while True:
     try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);break
     except BlockingIOError:assert time.monotonic()<deadline;time.sleep(.1)
  except BaseException:self.__exit__();raise
  return self
 def __exit__(self,*a):
  for f in reversed(self.fs):fcntl.flock(f,fcntl.LOCK_UN);f.close()
BOOT="import ctypes,os,sys;parent=int(sys.argv[1]);lib=ctypes.CDLL(None);assert lib.prctl(1,15,0,0,0)==0;assert os.getppid()==parent;fd=int(sys.argv[2]);token=os.read(fd,1);os.close(fd);sys.exit(125)if token!=b'G'else None;os.execv(sys.argv[3],sys.argv[3:])"
def run_core(job,num,kdir):
 assert u.sha(C/'stencil768_kernel_adapter_v1.py')==job['adapter_sha256']
 assert u.sha(C/'stencil768_common_v1.py')==job['common_sha256']
 assert u.sha(pathlib.Path('/usr/bin/nice'))=='6e3fd69addd6cff40185a406577b80ca03072588d593387a6a6ef73e9bc36348'
 assert u.sha(pathlib.Path('/usr/bin/prlimit'))=='a63d6a3b741b085776716c55a23f763280b509095faf43e5d435af7191b5e3e7'
 jobpath=kdir/'ADAPTER_JOB.json';u.save(jobpath,job);gate_in,gate_out=os.pipe();p=None
 try:
  with(kdir/'CORE_STDOUT.json').open('x')as out,(kdir/'CORE_STDERR.log').open('x')as err:
   command=['/usr/bin/nice','-n','15','/usr/bin/prlimit','--as='+str(1536*2**20),'--','python3','-B',str(C/'stencil768_kernel_adapter_v1.py'),str(jobpath)]
   p=subprocess.Popen(['python3','-B','-c',BOOT,str(os.getpid()),str(gate_in)]+command,pass_fds=(gate_in,),stdout=out,stderr=err,start_new_session=True)
   st=pathlib.Path('/proc',str(p.pid),'stat').read_text().split(') ',1)[1].split()
   u.save(u.WORK/('CORE_PROCESS_START_'+str(num)+'.json'),{'pid':p.pid,'ticks':st[19],'pgid':int(st[2]),'parent_pid':os.getpid(),'job_sha256':u.sha(jobpath),'gate_not_released_before_this_fsynced_identity':True})
   os.write(gate_out,b'G');os.close(gate_out);gate_out=None;os.close(gate_in);gate_in=None
   rc=p.wait()
  assert rc==0,('frozen5d adapter failed',num,rc)
  assert u.sha(C/'stencil768_kernel_adapter_v1.py')==job['adapter_sha256']
  assert u.sha(C/'stencil768_common_v1.py')==job['common_sha256']
  assert u.sha(pathlib.Path('/usr/bin/nice'))=='6e3fd69addd6cff40185a406577b80ca03072588d593387a6a6ef73e9bc36348'
  assert u.sha(pathlib.Path('/usr/bin/prlimit'))=='a63d6a3b741b085776716c55a23f763280b509095faf43e5d435af7191b5e3e7'
  r=json.loads((kdir/'CORE_STDOUT.json').read_text());assert r['status']=='GROUPED_ALL_SHARDS_CRC_PASS'
  u.save(kdir/'CORE_OBSERVED_EXIT0.json',{'observed_returncode':rc,'result_sha256':u.sha(kdir/'CORE_STDOUT.json'),'pid':p.pid,'source_job_sha256':u.sha(jobpath)})
  return r
 finally:
  for fd in [gate_in,gate_out]:
   if fd is not None:os.close(fd)
  if p is not None and p.poll()is None:
   try:os.killpg(p.pid,15)
   except ProcessLookupError:pass
   try:p.wait(timeout=3)
   except subprocess.TimeoutExpired:
    try:os.killpg(p.pid,9)
    except ProcessLookupError:pass
    p.wait(timeout=3)
def main():
 assert not u.WORK.exists();u.resources(True,stage_budget=u.LIMIT,admission=True);u.WORK.mkdir()
 assert u.sha(VALID)==grant['whole_validation_sha256']=='46e38ed1a10ab08d93dbbdba0e2fa0b0486cfa7db4a59e08a3d3edb61f7168e3';v=json.loads(VALID.read_text());assert v['kernels']==100 and v['counts']['sass_records']==2119914400
 for path,h in v['source_control_files'].items():assert u.sha(pathlib.Path(path))==h
 assert u.sha(RETAINED/'MANIFEST.json')==grant['retained_manifest_sha256']=='b4e90fa3243512e6967f342bd3f22928175f72bcf83d213b9dc6052d7e873f5b'
 assert u.sha(RETAINED/'COMMIT.json')==grant['retained_commit_sha256']=='9dbda4bf92b7653c6eeb86edb394a9d2c57310673f691864ae46cbcc39cad52d'
 retained=json.loads((RETAINED/'MANIFEST.json').read_text());named=[r['name']for r in v['per_kernel']];by={r['name']:r for r in v['per_kernel']};rawhash={pathlib.Path(p).name:h for p,h in v['source_files'].items()}
 old=json.loads((C/(ID+'_POST_BATCH_000.json')).read_text());grouped=[dict(r,grouped='traces/'+pathlib.Path(r['grouped']).name,CPU_post_epoch=2)for r in old['per_kernel']]
 for p in sorted(C.glob(ID+'_EPOCH3_NATIVE8_*_CLOSED.json')):
  q=json.loads(p.read_text());assert q['parent_whole_validation_sha256']==u.sha(VALID);grouped.extend(dict(r,CPU_post_epoch=3)for r in q['per_kernel'])
 assert len(grouped)==98
 for r in grouped:
  name=pathlib.Path(r['source']).name;assert r['source_sha256']==rawhash[name]and r['records']==by[name]['counts']['sass_records'];assert u.digest(ROOT/r['grouped'])==r['grouped_sha256']
 assert {pathlib.Path(r['grouped']).name for r in grouped}=={n.replace('.trace.xz','.traceg.xz')for n in named[:98]}=={p.name for p in(ROOT/'traces').glob('*.traceg.xz')}
 queue('RUNNING_CPU_POST_SINGLE768',controller_pid=os.getpid());phase('OLD98_CLOSED_CHAIN_RECHECKED',completed_kernels=98)
 for num in [99,100]:
  name='kernel-%d-ctx_0x559aa8cd3680.trace.xz'%num;stem=name[:-len('.trace.xz')];pfx='post/'+stem+'.trace_work/';kdir=u.WORK/('kernel_'+str(num));work=kdir/'work';work.mkdir(parents=True)
  phase('SINGLE768_COPY_PARTITIONS_AND_FRAMES',u.LIMIT,selected=name,completed_kernels=len(grouped))
  files=[r for r in retained['files']if r['path'].startswith(pfx)];assert len(files)==26
  for r in files:
   rel=pathlib.PurePosixPath(r['path'][len(pfx):]);assert not rel.is_absolute()and '..'not in rel.parts
   dest=work/pathlib.Path(*rel.parts);assert u.digest(RETAINED/'tree'/r['path'],dest,r['bytes'])==r['sha256']and u.sha(dest)==r['sha256']
  raw=ROOT/'traces'/name;state=json.loads((work/'CHECKPOINT.json').read_text());assert state['source_sha256']==rawhash[name]and state['partition_complete']and len(state['groups'])==9
  dest=kdir/name.replace('.trace.xz','.traceg.xz');job={'common_sha256':grant['common_sha256'],'adapter_sha256':grant['adapter_sha256'],'source_raw':str(raw),'source_sha256':rawhash[name],'source_bytes':raw.stat().st_size,'grouped':str(dest),'work':str(work),'records':by[name]['counts']['sass_records'],'ctas':by[name]['ctas'],'warps':by[name]['warps']}
  phase('SINGLE768_FROZEN5D_RESUME',u.LIMIT,selected=name,completed_kernels=len(grouped));r=run_core(job,num,kdir)
  assert r['records']==21199144 and u.sha(dest)==r['grouped_sha256']
  with Lease():
   target=ROOT/'traces'/dest.name;assert not target.exists();assert u.digest(dest,target,dest.stat().st_size)==r['grouped_sha256'];assert u.digest(target,expected_bytes=dest.stat().st_size)==r['grouped_sha256']
   r.update(grouped='traces/'+target.name,original_native_grouped_path=str(dest),CPU_post_epoch=4,NAS_closed_reopened_fullSHA=True)
   for p in [kdir/'ADAPTER_JOB.json',kdir/'CORE_STDOUT.json',kdir/'CORE_OBSERVED_EXIT0.json']:
    target=ROOT/'CPU_epoch4'/str(num)/p.name;assert u.digest(p,target,p.stat().st_size)==u.sha(p)
   u.save(ROOT/'CPU_epoch4'/str(num)/'GROUP_CLOSED.json',r)
  u.save(C/(ID+'_POST_EPOCH4_K'+str(num)+'_CLOSED.json'),r);grouped.append(r)
  # Copied old history remains fully archived; new full group is now closed on NAS.
  removed=[{'path':str(p.relative_to(kdir)),'bytes':p.stat().st_size,'sha256':u.sha(p)}for p in kdir.rglob('*')if p.is_file()]
  assert kdir.resolve().is_relative_to(u.WORK.resolve())and not kdir.is_symlink();shutil.rmtree(kdir);u.save(u.WORK/('K'+str(num)+'_VERIFIED_TEMP_CLEANUP.json'),{'removed':removed,'old_retained_tree_KEEP':str(RETAINED),'full_group_true164_closed':r['grouped_sha256']})
 phase('FINAL_ALL100_NO_NATIVE_PAYLOAD_REMAINING',0,completed_kernels=100)
 assert len(grouped)==100 and sum(r['records']for r in grouped)==2119914400
 expected={n.replace('.trace.xz','.traceg.xz')for n in named};assert {pathlib.Path(r['grouped']).name for r in grouped}==expected=={p.name for p in(ROOT/'traces').glob('*.traceg.xz')}
 for r in grouped:assert u.digest(ROOT/r['grouped'])==r['grouped_sha256']
 with Lease():
  for p in [pathlib.Path(__file__),cp,grantpath,C/'stencil768_kernel_adapter_v1.py',C/'supervise_stencil_single768_epoch4_v1.py',C/'resource_library_copy_v10_pinned.py']:
   assert u.digest(p,ROOT/'CPU_epoch4'/p.name,p.stat().st_size)==u.sha(p)
  u.save(ROOT/'POSTPROCESS_EPOCH4_FINAL100.json',{'per_kernel':grouped,'whole_validation_sha256':u.sha(VALID),'old98_reused':True,'last2_each9frames_reused':True,'no_GPU_or_scientific_record_revalidation':True})
  ctx=next((ROOT/'traces').glob('kernelslist_ctx_*'));assert not(ROOT/'traces/kernelslist.g').exists();(ROOT/'traces/kernelslist.g').write_text('\n'.join(l.replace('.trace.xz','.traceg.xz')if l.startswith('kernel-')else l for l in ctx.read_text().splitlines())+'\n')
  task=json.loads((ROOT/'TASK.json').read_text());source=json.loads((C/'STENCIL_CLOSED_RAW_ADOPTION_SOURCE_V1.json').read_text());flags=json.loads((ROOT/'TRACER_CONTROLS_FROM_ORIGINAL_GPU_STDOUT.json').read_text())['actual_printed_control_variables']
  asset={'schema':'RTX4080_FULL_TRACE_ASSET_V1','kind':'FULL_APPLICATION_TRACE','asset_id':ID,'suite':task['suite'],'source_version':task['version'],'program':task['program'],'variant':task['variant'],'argv':task['argv'],'input_identity':task.get('input_identity',task.get('input_files')),'binary_member':'bin/application','binary_sha256':source['GPU_execution']['binary_sha256'],'capture_gpu_uuid':source['GPU_execution']['actual_gpu_uuid'],'actual_cubin_arch':89,'producer_sha256':'55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73','contract_sha256':u.sha(ROOT/'contract/CONTRACT.json'),'validator_sha256':'85ff5d68408632a4f15634bfa6a6d7a504429821ed8067f1ab8f39ce1b9a6909','delegated_validator_sha256':'f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1','postprocessor_sha256':u.CORE_SHA,'CPU_post_controller_sha256':u.sha(pathlib.Path(__file__)),'raw_SHA_IO_adapter_sha256':grant['adapter_sha256'],'resource_adapter_sha256':grant['common_sha256'],'full_application':{'kernel_launches':100,'ctas':v['ctas'],'warps':v['warps'],'records':2119914400,'all_warps_terminate':True,'sampling':'NONE','commandlist':'traces/kernelslist.g'},'tracer_control_flags':flags,'numerical_status':'ORIGINAL_CAPTURE_REFERENCE_CHECKER_REPORTED_PASS','producer_semantic_qualification':'ADA7_ORDINARY_FULL_RECORD_PASS','consumer_qualification':'NOT_GRANTED','hardware_timing_calibration':'NOT_GRANTED','GPU_replayed':False,'source_keep':True,'release_bytes':0,'CPU_epochs':{'epoch2':'Original2 complete groups and whole46e100kernel validation retained; old34 terminal results have old_exit_not_separately_recorded','epoch3':'96 groups closed; allforeign reservation increase correctly stopped own work; all failure history cold retained','epoch4':{'remaining2_complete_kernels':True,'single_helper':True,'Native_stage_limit_polled':u.LIMIT,'raw_Native_copy':False,'old_frames_reused_each':9,'resource_library_copy_v10_sha256':'7e5b290e330cbc1fcc845b6a9c7ce3487d181677d117a8d77a31c60d12a42521','retained_history_object':str(RETAINED)}}}
  u.save(ROOT/'ASSET.json',asset);files=[]
  for p in sorted(ROOT.rglob('*')):
   if not p.is_file():continue
   h=u.digest(p)
   if p.parent==ROOT/'traces'and p.name in rawhash:assert h==rawhash[p.name],'original full raw changed since46e'
   files.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':h})
  u.save(ROOT/'SENDER_MANIFEST.json',{'asset':asset,'files':files})
  receiver=C/'dispatch_bulk_v3.py';assert u.sha(receiver)=='e7a090d2baed8d0177cdf4af5132490023dad4ed60d35f46271db8f3c6f52025';ns={};exec(compile(receiver.read_text().split('\nsingle=open(',1)[0],str(receiver),'exec'),ns)
  commit=ns['publish']({'asset_id':ID,'inflight':str(ROOT.relative_to(B)),'sender_manifest_sha256':u.sha(ROOT/'SENDER_MANIFEST.json')});u.save(C/(ID+'_POST_EPOCH4_COMMIT.json'),commit)
 queue('COMMITTED_VERIFIED',commit=commit);phase('COMMITTED_VERIFIED_FULL100_NO_GPU_REPLAY',0,commit=commit)
main()
