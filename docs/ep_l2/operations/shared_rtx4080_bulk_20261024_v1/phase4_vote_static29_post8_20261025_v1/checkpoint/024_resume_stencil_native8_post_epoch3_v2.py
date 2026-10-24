"""Post-only continuation of a fully validated immutable100-kernel GPU capture."""
import pathlib,json,hashlib,os,time,fcntl,subprocess,sys,collections,shutil,traceback
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent;B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
ID='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2';ROOT=B/'inflight'/ID;VALID=C/(ID+'_FULL_RECORD_VALIDATION_HOT_EPOCH2.json');STAGE=C/'post_complete_kernel_native_batch_v4.py';SCHED=C/'post_app_parallel_v5.py';WORK=N/(ID+'_post_native_epoch3');R3WORK=N/(ID+'_validation_hot_epoch2')
def sha(p,rate=True):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):
   t=time.monotonic();h.update(b)
   if rate:time.sleep(max(0,len(b)/(15*2**20)-(time.monotonic()-t)))
 return h.hexdigest()
def save(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();tmp=p.with_name(p.name+'.tmp')
 with tmp.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def replace(p,o):
 tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(o,indent=2)+'\n');os.replace(tmp,p)
def ticks(pid):return pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()[19]
def phase(status,**kw):replace(C/(ID+'_POST_EPOCH3_STATE.json'),dict(status=status,pid=os.getpid(),start_ticks=ticks(os.getpid()),unix=time.time(),**kw))
class Lease:
 def __enter__(self):
  self.fs=[];deadline=time.time()+7200
  try:
   for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
    f=open(C/name,'a');self.fs.append(f)
    while True:
     try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);break
     except BlockingIOError:assert time.time()<deadline;time.sleep(.1)
  except BaseException:self.__exit__();raise
  return self
 def __exit__(self,*a):
  for f in reversed(self.fs):fcntl.flock(f,fcntl.LOCK_UN);f.close()
def copy(s,d):
 d.parent.mkdir(parents=True,exist_ok=True)
 with s.open('rb')as f,d.open('xb')as out:
  for b in iter(lambda:f.read(2**20),b''):
   t=time.monotonic();out.write(b);time.sleep(max(0,len(b)/(15*2**20)-(time.monotonic()-t)))
  out.flush();os.fsync(out.fileno())
 assert sha(s)==sha(d)
def queue(status,**kw):
 with(C/'RTX4080_QUEUE.lock').open('a')as f:
  fcntl.flock(f,fcntl.LOCK_EX);rows=json.loads((C/'QUEUE.json').read_text());row=next(x for x in rows if x['id']==ID);row.update(status=status,**kw);replace(C/'QUEUE.json',rows)
def main():
 approval=pathlib.Path(sys.argv[1]);grant=json.loads(approval.read_text());assert grant['status']=='APPROVED_STENCIL_POST_ONLY_NATIVE8_NO_GPU_NO_RECORD_REVALIDATION'
 assert grant['controller_sha256']==sha(pathlib.Path(__file__))and sha(STAGE)==grant['stage_sha256']=='df4750e87caf2d951efb1cd4a96e97e24aca6d1230bde88ee65ec8d5924b652e'
 assert sha(SCHED)==grant['scheduler_sha256']=='c6fdc374344f4bb1d9cdec8f396807a9aef8d9b1fcf4741fc8477b18b86a0c2a'
 assert sha(VALID)==grant['whole_validation_sha256']=='46e38ed1a10ab08d93dbbdba0e2fa0b0486cfa7db4a59e08a3d3edb61f7168e3'
 complete=R3WORK/'CONTROLLER_COMPLETE.json';assert not(R3WORK/'FAILURE.json').exists()and sha(complete)==grant['R3_complete_sha256']
 assert json.loads(complete.read_text())['observed_all_phase_returncodes']==0 and json.loads(complete.read_text())['output_sha256']==sha(VALID)
 assert (C/(ID+'_HOT_EPOCH2_FAILURE.json')).exists()and sha(C/(ID+'_HOT_EPOCH2_FAILURE.json'))==grant['retained_cpu_failure_sha256']
 assert not WORK.exists();WORK.mkdir();val=json.loads(VALID.read_text());assert val['kernels']==100 and val['counts']['sass_records']==2119914400
 assert sha(ROOT/'FULL_RECORD_VALIDATION.json')==sha(VALID)
 for p,h in val['source_control_files'].items():assert sha(pathlib.Path(p))==h
 sourcefile=C/'STENCIL_CLOSED_RAW_ADOPTION_SOURCE_V1.json';assert sha(sourcefile)=='2fe8ff656649af32304d7e208e26c91b7fce11e1ba4ab22331b89a7bce1a16d4';source=json.loads(sourcefile.read_text())
 for x in source['raw_members']:
  p=ROOT/x['path'];assert(p.stat().st_size,p.stat().st_mtime_ns)==(x['bytes'],x['mtime_ns'])
 # Prior epoch ended naturally. No process is stopped or new GPU/SIM started here.
 for pid,tick in [(1021666,'960786311'),(1021667,'960786315')]:
  p=pathlib.Path('/proc',str(pid),'stat')
  if p.exists():assert p.read_text().split(') ',1)[1].split()[19]!=tick or p.read_text().split(') ',1)[1].split()[0]=='Z'
 oldout=C/(ID+'_POST_BATCH_000.json');assert sha(oldout)==grant['first2_closed_post_sha256'];old=json.loads(oldout.read_text());assert old['kernels']==2
 proof=ROOT/'post_batch_receipts/000_INTERNAL_GROUPING_VIEW.json';assert sha(proof)==old['source_validation_sha256']and json.loads(proof.read_text())['upstream_whole_application_validation_sha256']==sha(VALID)
 names=[r['name']for r in val['per_kernel']];allrows={r['name']:r for r in val['per_kernel']};rawhash={pathlib.Path(p).name:h for p,h in val['source_files'].items()};grouped=[]
 for r in old['per_kernel']:
  name=pathlib.Path(r['source']).name;p=ROOT/'traces'/pathlib.Path(r['grouped']).name
  assert r['source_sha256']==rawhash[name]and sha(p)==r['grouped_sha256']and r['records']==allrows[name]['counts']['sass_records']
  grouped.append(dict(r,grouped='traces/'+p.name,original_closed_grouped_path=r['grouped'],grouped_path_scope='ARCHIVE_RELATIVE_EXISTING_CLOSED_EPOCH2_GROUP',CPU_post_epoch=2))
 assert len(grouped)==2 and {pathlib.Path(r['grouped']).name for r in grouped}=={n.replace('.trace.xz','.traceg.xz')for n in names[:2]}
 assert {p.name for p in(ROOT/'traces').glob('*.traceg.xz')}=={pathlib.Path(r['grouped']).name for r in grouped}
 queue('RUNNING_CPU_POST_NATIVE8',controller_pid=os.getpid(),controller_start_ticks=ticks(os.getpid()),CPU_post_epoch=3)
 for offset in range(2,100,8):
  selected=names[offset:offset+8];batchid=f'EPOCH3_NATIVE8_{offset:03d}';jobpath=C/(ID+'_'+batchid+'_JOB.json');out=C/(ID+'_'+batchid+'_CLOSED.json');work=WORK/batchid
  job={'kind':'CLOSED_COMPLETE_APP_GROUPING_BATCH_NOT_NEW_APPLICATION','stage_code_sha256':sha(STAGE),'source_root':str(ROOT),'target_root':str(ROOT),'whole_validation':str(VALID),'whole_validation_sha256':sha(VALID),'whole_kernel_count':100,'whole_record_count':2119914400,'selected_names':selected,'work':str(work),'output':str(out),'batch_id':batchid,'aggregate_IO_lock':str(R3WORK/'AGGREGATE_NAS_READ.lock'),'scope':'Completekernels internally scheduled; original complete100-launch application remains sole formal asset'};save(jobpath,job)
  phase('NATIVE8_PREFETCH_GROUP_COPY_CLOSED_BATCH',completed_kernels=len(grouped),total_kernels=100,selected=selected)
  with(C/(ID+'_'+batchid+'.log')).open('x')as f:p=subprocess.run(['python3','-B',str(STAGE),str(jobpath)],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  assert p.returncode==0,('whole-stage guarded worker failed',batchid,p.returncode)
  q=json.loads(out.read_text());assert q['kernels']==len(selected)and q['records']==sum(allrows[n]['counts']['sass_records']for n in selected)
  assert {pathlib.Path(r['grouped']).name for r in q['per_kernel']}=={n.replace('.trace.xz','.traceg.xz')for n in selected}
  grouped.extend(dict(r,CPU_post_epoch=3)for r in q['per_kernel']);save(WORK/(batchid+'_ADOPTED.json'),{'batch_closed_sha256':sha(out),'completed_kernels':len(grouped),'source_GPU_replayed':False})
 phase('ALL100_GROUPED_FINAL_ASSET_CLOSE',completed_kernels=100,total_kernels=100)
 assert len(grouped)==100 and sum(r['records']for r in grouped)==2119914400
 expected={n.replace('.trace.xz','.traceg.xz')for n in names};assert {pathlib.Path(r['grouped']).name for r in grouped}=={p.name for p in(ROOT/'traces').glob('*.traceg.xz')}==expected
 for r in grouped:assert sha(ROOT/r['grouped'])==r['grouped_sha256']
 with Lease():
  for p in[pathlib.Path(__file__),approval,STAGE,SCHED,C/'supervise_stencil_post_native8_epoch3_v2.py',complete,C/(ID+'_HOT_EPOCH2_FAILURE.json')]:copy(p,ROOT/'CPU_epoch3'/p.name)
  save(ROOT/'POSTPROCESS_NATIVE8_EPOCH3.json',{'status':'ALL100_COMPLETE_APP_GROUPS_CLOSED_SHA_PASS','per_kernel':grouped,'source_whole_validation_sha256':sha(VALID),'no_GPU_or_record_revalidation':True,'partial_old_post_batches_scope':'Retained failed CPU scratch/history, excluded from active kernelslist.g; no CRC/fulltrace qualification claimed for those files'})
  ctx=next((ROOT/'traces').glob('kernelslist_ctx_*'));assert not(ROOT/'traces/kernelslist.g').exists();(ROOT/'traces/kernelslist.g').write_text('\n'.join(l.replace('.trace.xz','.traceg.xz')if l.startswith('kernel-')else l for l in ctx.read_text().splitlines())+'\n')
  task=json.loads((ROOT/'TASK.json').read_text());flags=json.loads((ROOT/'TRACER_CONTROLS_FROM_ORIGINAL_GPU_STDOUT.json').read_text())['actual_printed_control_variables']
  asset={'schema':'RTX4080_FULL_TRACE_ASSET_V1','kind':'FULL_APPLICATION_TRACE','asset_id':ID,'suite':task['suite'],'source_version':task['version'],'program':task['program'],'variant':task['variant'],'argv':task['argv'],'input_identity':task.get('input_identity',task.get('input_files')),'binary_member':'bin/application','binary_sha256':source['GPU_execution']['binary_sha256'],'capture_gpu_uuid':source['GPU_execution']['actual_gpu_uuid'],'actual_cubin_arch':89,'producer_sha256':'55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73','contract_sha256':sha(ROOT/'contract/CONTRACT.json'),'validator_sha256':'85ff5d68408632a4f15634bfa6a6d7a504429821ed8067f1ab8f39ce1b9a6909','delegated_validator_sha256':'f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1','postprocessor_sha256':'5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d','parallel_post_scheduler_sha256':sha(SCHED),'native_post_stage_sha256':sha(STAGE),'CPU_post_controller_sha256':sha(pathlib.Path(__file__)),'original_GPU_capture_job':'ORD_LATE_stencil_c3e987b033b4_A001','GPU_replayed':False,'full_application':{'kernel_launches':100,'ctas':val['ctas'],'warps':val['warps'],'records':2119914400,'all_warps_terminate':True,'sampling':'NONE','commandlist':'traces/kernelslist.g'},'tracer_control_flags':flags,'numerical_status':'ORIGINAL_CAPTURE_REFERENCE_CHECKER_REPORTED_PASS','numerical_reference_policy':'Original same-capture Parboilchecker/stdout retained; CPU post gives no stronger numerical oracle','producer_semantic_qualification':'ADA7_ORDINARY_FULL_RECORD_PASS','consumer_qualification':'NOT_GRANTED','hardware_timing_calibration':'NOT_GRANTED','source_keep':True,'release_bytes':0,'CPU_epochs':{'R3_validation':{'full_validation_sha256':sha(VALID),'COMPLETE_member':'CPU_epoch3/CONTROLLER_COMPLETE.json','terminal_old_results_reused':34,'old_per_kernel_exit_not_separately_recorded':True},'old_post2':{'first2_complete_groups_reused':True,'failed_resource_scan_history_retained':True},'post_epoch3':{'max_complete_kernels':8,'Native_total_stage_bytes':4*2**30,'external_aggregate_RSS_polled_bytes':16*2**30,'large_NAS_reads_and_writes_shared_bytes_per_sec':15*2**20}}};save(ROOT/'ASSET.json',asset)
  files=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(ROOT.rglob('*'))if p.is_file()];save(ROOT/'SENDER_MANIFEST.json',{'asset':asset,'files':files})
  receiver=C/'dispatch_bulk_v3.py';assert sha(receiver)=='e7a090d2baed8d0177cdf4af5132490023dad4ed60d35f46271db8f3c6f52025';ns={};exec(compile(receiver.read_text().split('\nsingle=open(',1)[0],str(receiver),'exec'),ns)
  commit=ns['publish']({'asset_id':ID,'inflight':str(ROOT.relative_to(B)),'sender_manifest_sha256':sha(ROOT/'SENDER_MANIFEST.json')});save(C/(ID+'_POST_EPOCH3_COMMIT.json'),commit)
 queue('COMMITTED_VERIFIED',commit=commit,end_unix=time.time());phase('COMMITTED_VERIFIED_FULL100_NO_GPU_REPLAY',commit=commit)
if __name__=='__main__':
 try:main()
 except BaseException as e:
  fail={'status':'FAILED_RETAINED_CPU_POST_EPOCH3','error':repr(e),'traceback':traceback.format_exc(),'no_GPU_or_SIM_execution':True,'source_KEEP':True,'unix':time.time()};save(C/(ID+'_POST_EPOCH3_FAILURE.json'),fail);queue('FAILED_RETAINED',failure_receipt=str(C/(ID+'_POST_EPOCH3_FAILURE.json')));phase('FAILED_RETAINED_CPU_POST_ONLY',failure=fail);raise
