from closure_local import *
from closure_resources import UTIL,checkpoint
old=load(B/'evidence/AWMA_C16_IMMUTABLE_RUN_MANIFEST_METADATA_CROSSCHECK.json')
six=[r for r in old if r.get('raw_path') and not any(m['equals_catalog_raw_manifest'] for m in r['manifest_checks'])]
code=UTIL+'\nreq='+repr(six)+r'''
import hashlib
out=[]
for r in req:
 p=r['raw_path'];o=dict(run_id=r['run_id'],path=p,catalog_expected=r['raw_manifest_sha256'],root=meta(p),files=[],documents=[])
 if not p.startswith('/root/share/mnt164/huangrulin/c16_ai_workload/raw/') or '..' in Path(p).parts:o['status']='IDENTITY_HOLD';out.append(o);continue
 try:
  for e in os.scandir(p):
   s=meta(e.path);o['files'].append(s)
   if e.is_file(follow_symlinks=False) and e.name.lower().endswith(('.json','.jsonl','.sha256','.tsv','.md','.txt','.csv')) and s.get('size',10**10)<=262144 and not any(z in e.name.lower() for z in ['tokens','prompt','input_text']):
    b=Path(e.path).read_bytes();o['documents'].append(dict(path=e.path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),text=b.decode(errors='replace')))
 except OSError as e:o['error']=str(e)
 out.append(o)
print(json.dumps(dict(utc=time.time(),records=out,mount=cmd(['findmnt','-J','-T','/root/share/mnt164/huangrulin/c16_ai_workload/raw']))))
'''
checkpoint('P3_BEFORE_SMALL_MANIFESTS')
x=remote('hrl-174-new',code,70);save('evidence/AWMA_SIX_EXACT_RAW_DIRECTORY_AND_SMALL_MANIFEST_DOCUMENTS.json',x)
for r in x['records']:
 print(r['run_id'],[(Path(f['path']).name,f.get('size')) for f in r['files']][:20])
 for d in r['documents']:
  if 'manifest' in Path(d['path']).name.lower():print('MANIFEST',Path(d['path']).name,d['sha256'],d['text'][:650])
