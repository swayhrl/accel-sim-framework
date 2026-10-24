from audit_local import *
from collect_audit import SNAP
import io
x=json.loads((R/'evidence/TRUE164_C16_AWMA_CATALOG_AND_SIX_MODEL_METADATA.json').read_text(encoding='utf8'))
entries={}
for r in x['indexes']:
 try:
  e=json.loads(r['content'])
  if isinstance(e,dict) and e.get('run_id') and e.get('raw_path'):entries[e['run_id']]=e
 except (ValueError,TypeError):pass
req=[{k:e.get(k) for k in ['run_id','raw_path','raw_bytes','raw_manifest_sha256','transfer_status','producer_host','scientific_status','instrument','model','phase','target']} for e in entries.values()]
code=SNAP[:SNAP.index('x=dict(')]+ '\nreq='+repr(req)+r'''
import hashlib
out=[]
for r in req:
 p=r['raw_path']
 if not p or not p.startswith('/root/share/mnt164/huangrulin/c16_ai_workload/') or '..' in Path(p).parts:
  out.append(dict(run_id=r['run_id'],status='IDENTITY_HOLD'));continue
 row=dict(**r,root_stat=meta(p),manifest_checks=[])
 for name in ['RUN_MANIFEST.json','TRANSFER_RECEIPT.json','TRANSFER_ACK.json','RESTORE_RECEIPT.json']:
  f=p+'/'+name
  if os.path.isfile(f) and os.path.getsize(f)<=131072:
   b=Path(f).read_bytes();h=hashlib.sha256(b).hexdigest();row['manifest_checks'].append(dict(path=f,bytes=len(b),sha256=h,equals_catalog_raw_manifest=h==r.get('raw_manifest_sha256')))
 out.append(row)
print(json.dumps(out))
'''
rows=remote('hrl-174-new',code,90);save('evidence/AWMA_C16_IMMUTABLE_RUN_MANIFEST_METADATA_CROSSCHECK.json',rows)
print('unique runs',len(rows),'present',sum('error' not in r.get('root_stat',{'error':1}) for r in rows),'manifest digest match',sum(any(m['equals_catalog_raw_manifest'] for m in r.get('manifest_checks',[])) for r in rows))
# Keep full catalog contents local; publish only explicit scientific metadata and digests.
private=P/'TRUE164_C16_AWMA_CATALOG_FULL_READONLY_SNAPSHOT.json';private.write_text(json.dumps(x,ensure_ascii=False),encoding='utf8')
for r in x['indexes']:
 b=r.pop('content').encode();r['content_sha256']=hashlib.sha256(b).hexdigest();r['content_bytes']=len(b)
save('evidence/TRUE164_C16_AWMA_CATALOG_AND_SIX_MODEL_METADATA.json',x)
review=Path('D:/repo/164-existing-archive-review-20261019-v1/docs/ep_l2/operations/164_existing_archive_review_20261019_v1')
for name in ['IMMUTABLE_GIT_EVIDENCE_CATALOG.json','OLD174_ALREADY_ARCHIVED_RECOVERY_OPPORTUNITIES.csv']:(R/'references'/name).write_bytes((review/name).read_bytes())
ops=list(csv.DictReader((review/'OLD174_ALREADY_ARCHIVED_RECOVERY_OPPORTUNITIES.csv').open(encoding='utf-8-sig')))
req=[dict(asset_id=r['asset_id'],source=r['canonical_source_path'],target=r['native164_archive_path']) for r in ops]
for alias,which in [('hrl','SOURCE'),('hrl-174-new','TRUE164')]:
 code=SNAP[:SNAP.index('x=dict(')]+'\nreq='+repr(req)+'\nout=[]\nfor r in req:\n p=r["source"] if '+repr(which)+'=="SOURCE" else r["target"].replace("/home/shared/","/root/share/mnt164/",1)\n if p and p.startswith(("/workspace/","/tmp/","/root/share/mnt164/huangrulin/")):out.append(dict(asset_id=r["asset_id"],stat=meta(p)))\nprint(json.dumps(out))'
 save('evidence/LEGACY_ARCHIVE_'+which+'_LOCATOR_CURRENT_STAT.json',remote(alias,code,60))
