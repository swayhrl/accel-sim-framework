from audit_local import *
from collect_audit import SNAP
models=list(csv.DictReader((P/'SIX_ROW_TRUE164_AUTHORITY_PROOF.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
code=SNAP[:SNAP.index('x=dict(')]+r'''
base='/root/share/mnt164/huangrulin/c16_ai_workload'
out=dict(utc=time.time(),mount=cmd(['findmnt','-J','-T',base]),models=[],indexes=[],metadata_directories=[])
'''+ '\nmodels='+repr(models)+r'''
for m in models:
 p=m['authority_alias_174new'];s=meta(p);s['expected_sha256']=m['sha256_expected'];s['reused_full_content_proof']='ab95e0aa46c73f6297315ecbbae09de10b09ce87'
 s['identity_matches_historical']=s.get('size')==int(m['size_bytes']) and s.get('mtime_ns')==int(m['authority_projected_mtime_ns']) and s.get('inode')==int(m['authority_projected_inode']);out['models'].append(s)
queue=[(base+'/catalog',0),(base+'/provenance/awma',0)]
n=0
while queue and n<1200:
 p,d=queue.pop(0)
 try:
  for e in os.scandir(p):
   n+=1;s=meta(e.path)
   if e.is_dir(follow_symlinks=False):
    out['metadata_directories'].append(s)
    if d<2:queue.append((e.path,d+1))
   elif e.name.endswith(('.tsv','.json','.jsonl','.csv','.md')) and s.get('size',10**9)<256000:
    out['indexes'].append(dict(**s,content=Path(e.path).read_text(errors='replace')))
   if n>=1200:break
 except OSError as e:out['metadata_directories'].append(dict(path=p,error=str(e)))
out['entries_limit']=1200;out['observed']=n
print(json.dumps(out))
'''
x=remote('hrl-174-new',code,90);save('evidence/TRUE164_C16_AWMA_CATALOG_AND_SIX_MODEL_METADATA.json',x)
print('models current identity',sum(x['identity_matches_historical'] for x in x['models']),'/',len(x['models']),'catalog files',len(x['indexes']))
print([r['path'] for r in x['indexes']][:25])
