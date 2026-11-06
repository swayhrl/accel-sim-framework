from pathlib import Path
import json,hashlib,subprocess,fcntl,datetime,tarfile,os,base64,io
P=Path(__file__).resolve().parent.parent;M=P/'main'
J=P.parent.parent
NAS=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_unified_memory_taxonomy_20261106_v1')
BASE='1c63b67beace667ea8a8028d77fbf9e5f2a9afc7'
BRANCH='hrl/ep-l2-unified-memory-taxonomy-20261106-v1'
PREFIX='docs/ep_l2/operations/ep_l2_unified_memory_taxonomy_20261106_v1'
REPO='repos/swayhrl/accel-sim-framework'
def read(p):return json.loads(Path(p).read_bytes())
def digest(b):return hashlib.sha256(b).hexdigest()
def write(p,x):
 p=Path(p);t=p.with_name('.'+p.name+'.tmp')
 t.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n');os.replace(t,p)
def ref(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':digest(b),'bytes':len(b)}
def clean(x):
 if isinstance(x,dict):return {k:clean(v)for k,v in x.items()if not any(t in k.lower()for t in ['token','nonce','secret'])}
 if isinstance(x,list):return [clean(v)for v in x]
 return x
def api(method,path,body=None,missing=False):
 a=['/usr/local/bin/gh','api','-X',method,path]
 if body is not None:write(M/'PUBLICATION_API_REQUEST.json',body);a+=['--input',str(M/'PUBLICATION_API_REQUEST.json')]
 r=subprocess.run(a,capture_output=True,timeout=180)
 if r.returncode:
  if missing and b'404' in r.stderr:return None
  raise RuntimeError('GitHub API '+method+' '+r.stderr.decode(errors='replace')[-500:])
 return json.loads(r.stdout)
def gather():
 skip={'REGISTRY_PREIMAGE.json','PUBLICATION_API_REQUEST.json','REVIEW_PACKAGE_MANIFEST.json','TRUE164_SMALL_EVIDENCE_ARCHIVE_RECEIPT.json','REMOTE_PUBLICATION_RECEIPT.json','FINAL_TASK_COMPLETION.json'}
 files={}
 for f in P.rglob('*'):
  if f.is_file() and '__pycache__'not in f.parts and f.name not in skip and f.suffix in ['.json','.md','.csv','.py','.cc','.config','.stdout','.stderr','.txt']:
   assert not f.is_symlink()
   files[str(f.relative_to(P))]=f
 assert sum(x.stat().st_size for x in files.values())<32*(1<<20)
 for name,f in files.items():
  if f.suffix in ['.md','.py','.cc','.config']:
   for n,line in enumerate(f.read_text().splitlines(),1):
    assert line==line.rstrip(' \t'),'trailing whitespace '+name+':'+str(n)
 return files
def archive(files):
 NAS.mkdir(exist_ok=True)
 receipt=M/'TRUE164_SMALL_EVIDENCE_ARCHIVE_RECEIPT.json'
 if receipt.exists():
  r=read(receipt);assert ref(r['archive_ref']['path'])==r['archive_ref'];return r
 mount=subprocess.run(['findmnt','-T','/root/share/mnt164','-o','TARGET,SOURCE,FSTYPE','-n'],capture_output=True,text=True,check=True).stdout.strip()
 assert '10.208.130.164:/home/shared' in mount and 'fuse.sshfs' in mount
 assert os.statvfs('/root/data').f_bavail*os.statvfs('/root/data').f_frsize>5*(1<<30)
 members=[{'member':n,**ref(f)}for n,f in sorted(files.items())]
 manifest={'schema':'EP_L2_UNIFIED_TAXONOMY_REVIEW_PACKAGE_V1','files':members,'original_bytes_preserved':True,'new_scientific_starts':0,'budget_consumption':0,'excluded':['Native registry preimage','CPU fixture executable (SHA/source/receipts retained)','all raw/Trace/ELF production assets'],'authority':BASE}
 write(M/'REVIEW_PACKAGE_MANIFEST.json',manifest)
 files={**files,'main/REVIEW_PACKAGE_MANIFEST.json':M/'REVIEW_PACKAGE_MANIFEST.json'}
 target=NAS/'UNIFIED_MEMORY_TAXONOMY_V1_SMALL_EVIDENCE.tar.gz'
 assert not target.exists()
 partial=target.with_suffix('.gz.partial')
 assert not partial.exists()
 with tarfile.open(partial,'w:gz',compresslevel=6)as tf:
  for name,f in sorted(files.items()):tf.add(f,arcname=name,recursive=False)
 body=partial.read_bytes();whole=digest(body)
 with tarfile.open(fileobj=io.BytesIO(body),mode='r:gz')as tf:
  assert sorted(tf.getnames())==sorted(files)
  for item in tf:
   assert item.isfile();bb=tf.extractfile(item).read()
   assert bb==files[item.name].read_bytes()
 os.replace(partial,target)
 assert digest(target.read_bytes())==whole
 r={'schema':'EP_L2_TAXONOMY_SMALL_TRUE164_ARCHIVE_RECEIPT_V1','status':'TRUE164_ALL_MEMBERS_AND_CLOSED_REOPEN_WHOLE_SHA_PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mount':mount,'archive_ref':ref(target),'file_count':len(files),'uncompressed_file_bytes':sum(x.stat().st_size for x in files.values()),'package_manifest_ref':ref(M/'REVIEW_PACKAGE_MANIFEST.json'),'new_scientific_starts':0,'budget_consumption':0,'Source_KEEP':True,'released_bytes':0,'full_native_restore_required':False,'qualification':'Review metadata archive only; not a scientific result archive or new model qualification'}
 write(receipt,r);write(NAS/receipt.name,r)
 return r
def main():
 audit=read(M/'MAIN_INDEPENDENT_ACCEPTANCE_AUDIT.json')
 assert audit['status'].endswith('_PASS')and audit['new_scientific_starts']==audit['budget_consumption']==0
 assert read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')==read(M/'REGISTRY_PREIMAGE.json')
 files=gather();ar=archive(files)
 files.update({'main/REVIEW_PACKAGE_MANIFEST.json':M/'REVIEW_PACKAGE_MANIFEST.json','main/TRUE164_SMALL_EVIDENCE_ARCHIVE_RECEIPT.json':M/'TRUE164_SMALL_EVIDENCE_ARCHIVE_RECEIPT.json'})
 with (J/'execution_performance_first_20261103_v1/control/MAIN_GIT_PUBLICATION.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  r=api('GET',REPO+'/git/ref/heads/'+BRANCH,missing=True)
  if r is None:r=api('POST',REPO+'/git/refs',{'ref':'refs/heads/'+BRANCH,'sha':BASE})
  assert r['object']['sha']==BASE,'Existing branch moved; retain evidence, never force'
  bc=api('GET',REPO+'/git/commits/'+BASE);tree=bc['tree']['sha']
  entries=[];manifest=[]
  for name,f in sorted(files.items()):
   original=f.read_bytes()
   exported=(json.dumps(clean(json.loads(original)),sort_keys=True,separators=(',',':'))+'\n').encode()if f.suffix=='.json' else original
   e={'path':PREFIX+'/'+name,'mode':'100644','type':'blob'}
   if len(exported)>2*(1<<20):
    bb=api('POST',REPO+'/git/blobs',{'content':base64.b64encode(exported).decode(),'encoding':'base64'})
    e['sha']=bb['sha']
   else:e['content']=exported.decode('utf-8')
   entries.append(e)
   manifest.append({'file':name,'original_ref':ref(f),'export_sha256':digest(exported),'export_bytes':len(exported),'git_blob':hashlib.sha1(b'blob '+str(len(exported)).encode()+b'\0'+exported).hexdigest(),'raw_preserved':original==exported})
  ex=json.dumps({'schema':'TAXONOMY_REVIEW_EXPORT_V1','files':manifest,'redaction':'recursive token/nonce/secret JSON keys omitted; JSON compact encoding; original and export SHA recorded','new_scientific_starts':0,'budget_consumption':0},sort_keys=True,indent=2)+'\n'
  entries.append({'path':PREFIX+'/REVIEW_EXPORT_MANIFEST.json','mode':'100644','type':'blob','content':ex})
  for i in range(0,len(entries),25):tree=api('POST',REPO+'/git/trees',{'base_tree':tree,'tree':entries[i:i+25]})['sha']
  commit=api('POST',REPO+'/git/commits',{'message':'EP-L2 unified memory taxonomy: 103 rows, exact evidence and four-point request; no model starts','tree':tree,'parents':[BASE]})
  assert api('GET',REPO+'/git/ref/heads/'+BRANCH)['object']['sha']==BASE
  api('PATCH',REPO+'/git/refs/heads/'+BRANCH,{'sha':commit['sha'],'force':False})
  assert api('GET',REPO+'/git/ref/heads/'+BRANCH)['object']['sha']==commit['sha']
  subtree=tree
  for part in PREFIX.split('/'):
   d=api('GET',REPO+'/git/trees/'+subtree);subtree=next(x['sha']for x in d['tree']if x['path']==part and x['type']=='tree')
  d=api('GET',REPO+'/git/trees/'+subtree+'?recursive=1');assert not d.get('truncated')
  by={x['path']:x['sha']for x in d['tree']if x['type']=='blob'}
  for r in manifest:assert by[r['file']]==r['git_blob']
  assert by['REVIEW_EXPORT_MANIFEST.json']==hashlib.sha1(b'blob '+str(len(ex.encode())).encode()+b'\0'+ex.encode()).hexdigest()
  bodies=[]
  for n in ['README.md','UNIFIED_WORKLOAD_MEMORY_TAXONOMY_V1.json','NEXT_EXACT_PERFORMANCE_EXPERIMENT_REQUEST.json','main/MAIN_INDEPENDENT_ACCEPTANCE_AUDIT.json','main/TRUE164_SMALL_EVIDENCE_ARCHIVE_RECEIPT.json']:
   bb=api('GET',REPO+'/git/blobs/'+by[n]);raw=base64.b64decode(bb['content'])
   mr=next(x for x in manifest if x['file']==n)
   assert digest(raw)==mr['export_sha256'];bodies.append({'file':n,'sha256':digest(raw),'bytes':len(raw)})
  receipt={'status':'REMOTE_BRANCH_ALL_GIT_BLOBS_AND_FIVE_PRIMARY_BODIES_VERIFIED','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':BRANCH,'head':commit['sha'],'parent':BASE,'prefix':PREFIX,'files':len(entries),'body_readback':bodies,'archive_receipt_ref':ref(M/'TRUE164_SMALL_EVIDENCE_ARCHIVE_RECEIPT.json'),'new_scientific_starts':0,'budget_consumption':0}
  write(M/'REMOTE_PUBLICATION_RECEIPT.json',receipt);write(NAS/'REMOTE_PUBLICATION_RECEIPT.json',receipt)
  print(json.dumps(receipt))
if __name__=='__main__':main()
