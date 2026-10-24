import pathlib,json,hashlib,os,time,subprocess,lzma,concurrent.futures,shutil,signal,resource,threading,traceback
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
A=B/'objects/ORD_PolyBench_GPU_3MM_f1a41d8f9e59_A002_CPU_RESUME'
W=C.parent/'parallel_post_3mm_AB_A001';W.mkdir(exist_ok=False)
POST=C/'postprocess_nas_sharded_v4.py';deadline=time.time()+7200;children={};lock=threading.Lock()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def expanded(p):
 h=hashlib.sha256();n=0
 with lzma.open(p,'rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b);n+=len(b)
 return n,h.hexdigest()
def save(p,o):p.write_text(json.dumps(o,indent=2)+'\n')
assert sha(POST)=='5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d'
identity={'pid':os.getpid(),'start_ticks':pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],'deadline_unix':deadline,'max_concurrent_kernel_postprocessors':2,'per_child_RLIMIT_AS_bytes':1536*2**20,'aggregate_child_virtual_address_bound':3072*2**20,'sort_memory_per_child':256*2**20,'partition_buffer_per_child':64*2**20,'private_local_disk_hard_bound':4*2**30,'local_free_reserve':10*2**30,'NAS_reads_only':True,'GPU_execution':False,'source_KEEP':True,'tool_sha256':sha(POST)}
save(W/'IDENTITY.json',identity)
m=json.loads((A/'MANIFEST.json').read_text());commit=json.loads((A/'COMMIT.json').read_text());assert sha(A/'MANIFEST.json')==commit['manifest_sha256']
entries=[x for x in m['files']if x['path'].endswith('.trace.xz')];assert len(entries)==3
for x in entries:
 src=A/x['path'];dest=W/src.name
 assert sha(src)==x['sha256']
 with src.open('rb')as f,dest.open('xb')as o:
  for b in iter(lambda:f.read(2**20),b''):
   now=time.monotonic();o.write(b);time.sleep(max(0,len(b)/(15*2**20)-(time.monotonic()-now)))
  o.flush();os.fsync(o.fileno())
 assert sha(dest)==x['sha256']
def preexec():os.nice(15);resource.setrlimit(resource.RLIMIT_AS,(1536*2**20,1536*2**20))
def one(x):
 src=W/pathlib.Path(x['path']).name;dest=W/src.name.replace('.trace.xz','.traceg.xz');work=W/(src.stem+'_work')
 started=time.time()
 with (W/(src.name+'.post.log')).open('x')as f:
  p=subprocess.Popen(['python3','-B',str(POST),str(src),str(dest),str(work),'--scratch-budget',str(2*2**30)],stdout=f,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=preexec)
  with lock:children[p.pid]=p
  rc=p.wait()
  with lock:children.pop(p.pid,None)
 assert rc==0,('post failed',src,rc)
 r=json.loads((work/'GROUP_RECEIPT.json').read_text());reference=A/x['path'].replace('.trace.xz','.traceg.xz')
 n,digest=expanded(dest);oldn,olddigest=expanded(reference);assert(n,digest)==(oldn,olddigest),'full expanded grouped bytes differ'
 assert sha(src)==x['sha256']
 out={'source':x['path'],'source_sha256':x['sha256'],'status':'FULL_DECOMPRESSED_BYTE_AND_CRC_EQUIVALENCE_PASS','expanded_bytes':n,'expanded_sha256':digest,'records':r['records'],'ctas':r['ctas'],'warps':r['warps'],'elapsed_s':time.time()-started,'group_sha256':sha(dest),'reference_group_sha256':sha(reference)}
 save(W/(src.name+'.EQUIVALENCE.json'),out);shutil.rmtree(work)
 return out
futures=[];start=time.time();results=[]
try:
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  futures=[pool.submit(one,x)for x in entries]
  while not all(f.done()for f in futures):
   used=sum(p.stat().st_size for p in W.rglob('*')if p.is_file())
   assert used<4*2**30,'private local disk budget'
   assert shutil.disk_usage(W).free>10*2**30,'local reserve'
   assert time.time()<deadline,'AB finite deadline'
   time.sleep(2)
  results=[f.result()for f in futures]
 report={'status':'PARALLEL2_KERNELS_REAL_3MM_EQUIVALENCE_PASS','identity':identity,'parent_asset_id':commit['asset_id'],'parent_manifest_sha256':commit['manifest_sha256'],'kernels':results,'elapsed_s':time.time()-start,'no_GPU_replay':True,'no_NAS_writes':True,'publish_not_granted_by_this_AB':True}
 save(C/'PARALLEL_POST_V4_REAL_3MM_AB_V1.json',report);save(W/'QUALIFICATION.json',report)
except BaseException as e:
 with lock:
  for p in children.values():
   if p.poll()is None:os.killpg(p.pid,signal.SIGTERM)
 save(W/'FAILURE.json',{'error':repr(e),'traceback':traceback.format_exc(),'source_KEEP':True})
 raise
