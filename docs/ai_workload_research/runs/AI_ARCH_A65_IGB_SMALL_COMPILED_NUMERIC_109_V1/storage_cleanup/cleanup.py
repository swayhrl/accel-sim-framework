"""User-approved exact first-batch local cleanup, with immutable remote SHA proof."""
import os,sys,json,time,hashlib,subprocess,shutil,stat,concurrent.futures
from pathlib import Path
R=Path(__file__).resolve().parent
BASE=Path('/data/c16')
E1='C16R_qwen2p5-7b-instruct-awq_s2-text-d1-d3_decode3_nvbit1771-sim-native-full-sass_bounded-context_20260925T120107Z_2b41b26fdb03'
RAW=BASE/'e1_bounded_decode_trace_v1/formal_d1_d3_20260925_v3/raw'
LINK=BASE/'e1_bounded_decode_trace_v1/pipeline/transferred'/E1/'traces'
MODELS=json.loads(Path('/tmp/aiarch_storage109_20261016_dependency_checks.json').read_text())['models']
TARGETS=[Path('/home/huangrulin/.cache/pip/http'),Path('/home/huangrulin/.cache/pip/http-v2')]+[Path(x['path']) for x in MODELS]+[RAW,LINK]
AUTH=json.loads(Path('/tmp/aiarch_storage164_20261016_inventory.json').read_text())
os.sched_setaffinity(0,[0,2,4,6])
def save(name,v):
 p=R/name;tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,indent=2)+'\n');os.replace(tmp,p)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return h.hexdigest()
def files(root):return sorted(p for p in root.rglob('*') if p.is_file() and not p.is_symlink())
def inventory(root):
 assert root.is_absolute() and root.is_dir() and not root.is_symlink() and root.resolve()==root
 assert root in TARGETS
 rows=[]
 for p in sorted(root.rglob('*')):
  st=p.lstat();assert not stat.S_ISLNK(st.st_mode),'SYMLINK_NOT_ALLOWED '+str(p)
  assert stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode)
  if p.is_file():rows.append({'path':str(p),'bytes':st.st_size,'allocated':st.st_blocks*512,'dev':st.st_dev,'ino':st.st_ino,'nlink':st.st_nlink,'mtime_ns':st.st_mtime_ns})
 return rows
def busy_roots():
 found=[];denied=[];infrastructure=[]
 for q in Path('/proc').iterdir():
  if not q.name.isdigit():continue
  try:
   if q.stat().st_uid!=os.getuid():continue
   for p in (q/'fd').iterdir():
    try:
     target=os.readlink(p)
     if any(target==str(x) or target.startswith(str(x)+'/') for x in TARGETS):found.append({'pid':int(q.name),'fd':p.name,'path':target})
    except (FileNotFoundError,PermissionError):pass
   for line in (q/'maps').read_text().splitlines():
    if any(str(x)+'/' in line for x in TARGETS):found.append({'pid':int(q.name),'map':line})
  except FileNotFoundError:pass
  except PermissionError:
   name=(q/'comm').read_text().strip()
   if name in ['sshd','(sd-pam)']:infrastructure.append({'pid':int(q.name),'comm':name,'reason':'non-dumpable authenticated session or PAM infrastructure, not a payload worker'})
   else:denied.append(int(q.name))
 return {'busy':found,'unreadable_own_processes':denied,'infrastructure_exceptions':infrastructure,'scope':'current UID file descriptors and mappings; no process killed'}
def delete(root,expected):
 assert inventory(root)==expected,'TARGET_CHANGED_SINCE_INVENTORY'
 activity=busy_roots();save('last_occupancy_check.json',activity);assert not activity['busy'] and not activity['unreadable_own_processes'],'ACTIVE_OR_UNKNOWN_OWNER_PROCESS'
 before=shutil.disk_usage(root).free;t=time.time();shutil.rmtree(root)
 assert not root.exists()
 row={'target':str(root),'deleted_epoch':t,'files':len(expected),'logical_bytes':sum(x['bytes'] for x in expected),'free_before_bytes':before,'free_after_bytes':shutil.disk_usage(BASE).free,'status':'DELETED_EXACT_APPROVED_TARGET'}
 with (R/'deletions.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 print('DELETED',root,flush=True)
def local_hash():
 rows=[]
 for x in MODELS:
  p=Path(x['path']);rec=next(a for a in AUTH['models'] if a['revision']==p.name)
  for line in rec['inventory'].splitlines()[1:]:
   rel,num,h=line.split('\t');q=p/rel;assert q.stat().st_size==int(num);actual=sha(q);assert actual==h,'LOCAL_MODEL_SHA_FAILED '+str(q);rows.append({'path':str(q),'bytes':int(num),'sha256':actual})
 m=Path('/data/c16/e1_bounded_decode_trace_v1/pipeline/transferred')/E1/'RUN_MANIFEST.json'
 d=json.loads(m.read_text());assert sha(m)=='db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389'
 count=0
 for x in d['artifacts']:
  if not x['relative_path'].startswith('traces/'):continue
  q=LINK/x['relative_path'][len('traces/'):];other=RAW/q.name;assert q.stat().st_ino==other.stat().st_ino and q.stat().st_nlink==2
  actual=sha(q);assert actual==x['sha256'],'LOCAL_E1_SHA_FAILED '+str(q);rows.append({'path':str(q),'other_hardlink':str(other),'bytes':q.stat().st_size,'sha256':actual});count+=1
 assert count==9032;save('local_payload_hashes.json',{'status':'PASS','files':rows});return True
REMOTE=r'''
from pathlib import Path
import hashlib,json,os,time,sys
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
r=Path('/root/share/mnt164/huangrulin/c16_ai_workload');rows=[];done=0;last=time.monotonic()
def sha(p):
 global done,last
 h=hashlib.sha256();before=p.stat()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):
   h.update(b);done+=len(b)
   if time.monotonic()-last>30:print('REMOTE_SHA_PROGRESS_BYTES',done,flush=True,file=sys.stderr);last=time.monotonic()
 after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 return h.hexdigest()
for name in ['deepseek-v2-lite','qwen3-8b','qwen2.5-7b-instruct-raw','qwen2.5-7b-instruct-awq','qwen2.5-0.5b-instruct']:
 revisions={'deepseek-v2-lite':'604d5664dddd88a0433dbae533b7fe9472482de0','qwen3-8b':'b968826d9c46dd6066d109eabc6255188de91218','qwen2.5-7b-instruct-raw':'a09a35458c702b33eeacc393d103063234e8bc28','qwen2.5-7b-instruct-awq':'b25037543e9394b818fdfca67ab2a00ecc7dd641','qwen2.5-0.5b-instruct':'7ae557604adf67be50417f59c2c2f167def9a775'}
 q=r/'assets/models'/name/revisions[name];rec=json.loads((q/'MODEL_ARCHIVE_RECEIPT.json').read_text());a=q/'SOURCE_INVENTORY.tsv';b=q/'DESTINATION_INVENTORY.tsv';assert a.read_bytes()==b.read_bytes();assert sha(a)==rec['source_inventory_file_sha256']
 for line in a.read_text().splitlines()[1:]:
  rel,num,h=line.split('\t');p=q/rel;assert p.stat().st_size==int(num);actual=sha(p);assert actual==h,'REMOTE_MODEL_SHA_FAILED '+str(p);rows.append({'path':str(p),'bytes':int(num),'sha256':actual})
run='C16R_qwen2p5-7b-instruct-awq_s2-text-d1-d3_decode3_nvbit1771-sim-native-full-sass_bounded-context_20260925T120107Z_2b41b26fdb03';q=r/'raw'/run;p=q/'RUN_MANIFEST.json';assert sha(p)=='db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389';d=json.loads(p.read_text())
for x in d['artifacts']:
 p=q/x['relative_path'];assert p.stat().st_size==x['size_bytes'];actual=sha(p);assert actual==x['sha256'],'REMOTE_E1_SHA_FAILED '+str(p);rows.append({'path':str(p),'bytes':p.stat().st_size,'sha256':actual})
print(json.dumps({'status':'PASS_FULL_CURRENT_164_PAYLOAD_SHA256','hashed_bytes':done,'files':rows,'archive_writes':0}))
'''
def remote_hash():
 with (R/'remote_sha_progress.log').open('w') as log:
  p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','hrl174new','python3','-'],input=REMOTE,text=True,stdout=subprocess.PIPE,stderr=log,timeout=10800)
 assert p.returncode==0,'REMOTE_VERIFY_FAILED; see log';v=json.loads(p.stdout);assert v['status']=='PASS_FULL_CURRENT_164_PAYLOAD_SHA256';save('remote_payload_hashes.json',v);return True
if __name__=='__main__':
 assert not (R/'finished.json').exists()
 try:
  save('start.json',{'script_sha256':sha(Path(__file__)),'epoch':time.time(),'approved_by_user':'2026-10-16 explicit first batch cleanup then resume A65','targets':[str(x) for x in TARGETS],'free_before_bytes':shutil.disk_usage(BASE).free,'protected':['A61 all assets','A26GR1 all assets','other AWMA/C16','node164 authority']})
  inv={str(x):inventory(x) for x in TARGETS};save('predelete_inventory.json',inv)
  activity=busy_roots();save('initial_occupancy_check.json',activity);assert not activity['busy'] and not activity['unreadable_own_processes']
  # Cache directories contain disposable HTTP responses only, with no shared inode.
  for x in TARGETS[:2]:
   assert all(a['nlink']==1 for a in inv[str(x)]);delete(x,inv[str(x)])
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   a=pool.submit(local_hash);b=pool.submit(remote_hash);assert a.result() and b.result()
  for x in TARGETS[2:7]:delete(x,inv[str(x)])
  # Validate both original inventories before unlinking either half of the pair.
  assert inventory(RAW)==inv[str(RAW)] and inventory(LINK)==inv[str(LINK)]
  delete(RAW,inv[str(RAW)])
  # nlink deliberately changed from two to one after deleting the first alias.
  remaining=inventory(LINK)
  assert [{**x,'nlink':2} for x in remaining]==inv[str(LINK)]
  delete(LINK,remaining)
  save('finished.json',{'status':'PASS_FIRST_BATCH_CLEANUP','free_after_bytes':shutil.disk_usage(BASE).free,'deleted_targets':[str(x) for x in TARGETS],'node164_modified':False,'A61_A26GR1_modified':False,'GPU_lock_attempts':0})
 except BaseException as e:
  save('failure.json',{'status':'STOP_CLEANUP_FAILED_CLOSED','error':repr(e)});raise
