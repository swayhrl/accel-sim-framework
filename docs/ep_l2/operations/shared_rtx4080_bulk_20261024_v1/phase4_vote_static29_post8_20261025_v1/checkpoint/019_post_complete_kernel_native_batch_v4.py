"""CPU grouping scheduling batch; never an independent application or GPU capture."""
import pathlib,json,hashlib,subprocess,os,time,fcntl,collections,shutil,importlib.util,sys
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent;B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
POST=C/'postprocess_nas_sharded_v4.py';SCHED=C/'post_app_parallel_v5.py';HOT=C/'validate_app_hot_resume_v4r3.py'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def save(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');assert not p.exists()
 with tmp.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
class Lease:
 def __enter__(self):
  self.files=[];deadline=time.time()+600
  try:
   for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
    f=open(C/name,'a');self.files.append(f)
    while True:
     try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);break
     except BlockingIOError:assert time.time()<deadline;time.sleep(.5)
  except BaseException:self.__exit__();raise
  return self
 def __exit__(self,*args):
  for f in reversed(self.files):fcntl.flock(f,fcntl.LOCK_UN);f.close()
jobpath=pathlib.Path(sys.argv[1]);job=json.loads(jobpath.read_text());assert job['kind']=='CLOSED_COMPLETE_APP_GROUPING_BATCH_NOT_NEW_APPLICATION'
assert sha(pathlib.Path(__file__))==job['stage_code_sha256']
assert sha(POST)=='5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d'
assert sha(SCHED)=='c6fdc374344f4bb1d9cdec8f396807a9aef8d9b1fcf4741fc8477b18b86a0c2a'
assert sha(HOT)=='85ff5d68408632a4f15634bfa6a6d7a504429821ed8067f1ab8f39ce1b9a6909'
root=pathlib.Path(job['source_root']).resolve();assert B.resolve()in root.parents
targetroot=pathlib.Path(job.get('target_root',job['source_root'])).resolve();assert (B/'inflight').resolve()in targetroot.parents,'Never write an existing immutable object'
validation=pathlib.Path(job['whole_validation']);assert sha(validation)==job['whole_validation_sha256'];v=json.loads(validation.read_text())
assert v['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'and v['all_declared_warps_terminate']and v['kernel_commandlist_exact_set']and v['stats_record_counts_match']
assert v['kernels']==job['whole_kernel_count']and v['counts']['sass_records']==job['whole_record_count']
selected=job['selected_names'];assert 1<=len(selected)<=8 and len(selected)==len(set(selected))
allrows={r['name']:r for r in v['per_kernel']};hashes={pathlib.Path(p).name:h for p,h in v['source_files'].items()};assert set(allrows)==set(hashes)
for name in selected:assert name in allrows and pathlib.PurePosixPath(name).name==name and name.endswith('.trace.xz')
work=pathlib.Path(job['work']).resolve();assert N in work.parents and os.stat(work.parent).st_dev==2128 and not work.exists();work.mkdir();save(work/'JOB.json',job)
output=pathlib.Path(job['output']).resolve();assert output.parent==C and not output.exists()
assert shutil.disk_usage(N).free>9*2**30+4*2**30
ratepath=pathlib.Path(job['aggregate_IO_lock']).resolve();assert N in ratepath.parents and ratepath.is_file()and os.stat(ratepath).st_dev==2128
spec=importlib.util.spec_from_file_location('hot',HOT);hot=importlib.util.module_from_spec(spec);spec.loader.exec_module(hot);rate=open(ratepath,'a')
inp=work/'input';(inp/'traces').mkdir(parents=True);before={};staged=[]
for name in selected:
 raw=root/'traces'/name;st=raw.stat();before[name]=(st.st_size,st.st_mtime_ns)
 dest=inp/'traces'/name;assert hot.digest(raw,rate,dest,st.st_size)==hashes[name]and sha(dest)==hashes[name]
 assert (raw.stat().st_size,raw.stat().st_mtime_ns)==before[name]
 staged.append({'name':name,'bytes':st.st_size,'sha256':hashes[name]})
members=[allrows[n]for n in selected];counts=collections.Counter()
for r in members:counts.update(r['counts'])
sub=dict(v);sub.update(kernels=len(selected),ctas=sum(r['ctas']for r in members),warps=sum(r['warps']for r in members),counts=dict(counts),per_kernel=members,source_files={str(inp/'traces'/n):hashes[n]for n in selected},scope='INTERNAL_COMPLETE_KERNEL_CPU_SCHEDULING_VIEW_NOT_AN_INDEPENDENT_APPLICATION',parent_whole_application_validation_sha256=sha(validation))
save(inp/'FULL_RECORD_VALIDATION.json',sub);save(work/'PREFETCH_CLOSED_SHA.json',{'source_members':staged,'parent_whole_application_validation_sha256':sha(validation),'source_KEEP':True})
dest=work/'post';postout=work/'POST_RESULT.json'
with(work/'POST_PROCESS.log').open('x')as f:p=subprocess.run(['python3','-B',str(SCHED),str(inp),'--post',str(POST),'--dest-root',str(dest),'--output',str(postout),'--max-workers','8','--minimum-free',str(9*2**30),'--aggregate-spill-budget',str(4*2**30),'--per-shard-scratch-budget',str(2**30),'--deadline-sec','7200'],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
assert p.returncode==0,'whole-stage external recursive supervisor must cover all helper/sort PGs'
q=json.loads(postout.read_text());assert q['kernels']==len(selected)and q['records']==sum(allrows[n]['counts']['sass_records']for n in selected)
assert {pathlib.Path(r['source']).name for r in q['per_kernel']}==set(selected)
closed=[]
for r in q['per_kernel']:
 name=pathlib.Path(r['source']).name;group=pathlib.Path(r['grouped']);assert group.parent==dest and sha(group)==r['grouped_sha256']and r['source_sha256']==hashes[name]
 source_raw=root/'traces'/name;assert(source_raw.stat().st_size,source_raw.stat().st_mtime_ns)==before[name]
 with Lease():
  (targetroot/'traces').mkdir(parents=True,exist_ok=True)
  target=targetroot/'traces'/group.name;assert not target.exists()
  assert hot.digest(group,rate,target,group.stat().st_size)==r['grouped_sha256']
  assert hot.digest(target,rate,expected_size=group.stat().st_size)==r['grouped_sha256']
  row=dict(r,original_closed_native_grouped_path=str(group),grouped='traces/'+group.name,grouped_path_scope='ARCHIVE_RELATIVE_AFTER_CLOSED_COPY',NAS_closed_reopen_SHA=True)
  save(targetroot/'post_native_batch_receipts'/job['batch_id']/(group.name+'.json'),row)
  closed.append(row)
# Preserve control evidence on true164, before releasing only the temporary Native read/group buffers.
receipt={'status':'SELECTED_COMPLETE_KERNELS_NATIVE_GROUPED_TRUE164_CLOSED_NOT_INDEPENDENT_APP','batch_id':job['batch_id'],'kernels':len(selected),'records':q['records'],'per_kernel':closed,'parent_whole_validation_sha256':sha(validation),'stage_code_sha256':sha(pathlib.Path(__file__)),'scheduler_sha256':sha(SCHED),'postprocessor_sha256':sha(POST),'source_KEEP':True,'aggregate_large_NAS_read_plus_write_bytes_per_second':15*2**20,'GNU_sort_memory_scope':'Each sort-S256M and Python has separate1.5GiB AS; external whole-tree RSS16GiB/Native staging4GiB polled guard required','scratch_location':'Native ext4 only; all partition/frame/sort files below explicit4GiB stage work tree'}
with Lease():
 for src in [jobpath,postout,inp/'FULL_RECORD_VALIDATION.json',work/'PREFETCH_CLOSED_SHA.json']:
  target=targetroot/'post_native_batch_receipts'/job['batch_id']/src.name
  if target.exists():assert sha(target)==sha(src)
  else:
   target.parent.mkdir(parents=True,exist_ok=True)
   assert hot.digest(src,rate,target,src.stat().st_size)==sha(src)
 save(targetroot/'post_native_batch_receipts'/job['batch_id']/'BATCH_CLOSED.json',receipt)
 assert sha(validation)==job['whole_validation_sha256']
removed=[]
for p in list((inp/'traces').iterdir())+list(dest.glob('*.traceg.xz')):
 assert work in p.resolve().parents and not p.is_symlink()
 h=sha(p);removed.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h});p.unlink()
save(work/'TEMPORARY_BUFFER_CLEANUP.json',{'removed':removed,'raw_source_still_on_true164':True,'grouped_targets_closed_reopen_SHA':True,'original_source_KEEP':True,'no_scientific_original_payload_deleted':True})
save(output,receipt);print(json.dumps(receipt))
