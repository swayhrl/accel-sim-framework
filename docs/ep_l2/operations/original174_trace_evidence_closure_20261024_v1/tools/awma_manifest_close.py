from closure_local import *
from closure_resources import UTIL
old=load(B/'evidence/AWMA_C16_IMMUTABLE_RUN_MANIFEST_METADATA_CROSSCHECK.json')
six=[r for r in old if r.get('raw_path') and not any(m['equals_catalog_raw_manifest'] for m in r['manifest_checks'])]
code=UTIL+'\nreq='+repr(six)+r'''
import hashlib
out=[]
for r in req:
 root=r['raw_path'];p=root+'/RUN_MANIFEST.json';before=meta(p)
 o=dict(run_id=r['run_id'],manifest_path=p,catalog_expected=r['raw_manifest_sha256'],before=before,previous_read_bound=131072)
 if not root.startswith('/root/share/mnt164/huangrulin/c16_ai_workload/raw/') or '..' in Path(root).parts or before.get('size',10**10)>2*1024**2:o['status']='IDENTITY_OR_METADATA_SIZE_HOLD';out.append(o);continue
 b=Path(p).read_bytes();h=hashlib.sha256(b).hexdigest();j=json.loads(b);art=j.get('artifacts',[])
 checks=[];mismatches=[]
 for a in art:
  rel=a.get('relative_path')
  if not rel or Path(rel).is_absolute() or '..' in Path(rel).parts:mismatches.append(dict(path=rel,why='INVALID_RELATIVE'));continue
  s=meta(root+'/'+rel)
  expected=a.get('size_bytes',a.get('size'))
  if s.get('type')!='file' or s.get('size')!=expected:mismatches.append(dict(path=rel,expected_size=expected,actual=s))
 after=meta(p)
 o.update(actual_sha256=h,exact_catalog_digest_match=h==r['raw_manifest_sha256'],after=after,manifest_identity_stable=all(before.get(k)==after.get(k) for k in ['dev','inode','size','mtime_ns','ctime_ns']),artifact_count=len(art),artifact_declared_bytes=sum(int(a.get('size_bytes',a.get('size',0))) for a in art),artifact_metadata_mismatches=mismatches,manifest_keys=list(j),raw_data_payload_SHA_recomputed=False,reason='PREVIOUS_AUDIT_SKIPPED_FILE_ABOVE_128KiB_NOT_A_DIGEST_MISMATCH',status='MANIFEST_DIGEST_CLOSED' if h==r['raw_manifest_sha256'] else 'ACTUAL_DIGEST_MISMATCH_HOLD')
 out.append(o)
print(json.dumps(dict(utc=time.time(),records=out,six_small_metadata_bytes_read=sum(r.get('before',{}).get('size',0) for r in out),data_copied_bytes=0)))
'''
x=remote('hrl-174-new',code,90);save('evidence/AWMA_SIX_MANIFEST_EXACT_DIGEST_AND_CURRENT_ARTIFACT_STAT_CLOSURE.json',x)
print([(r['run_id'],r.get('exact_catalog_digest_match'),r.get('artifact_count'),len(r.get('artifact_metadata_mismatches',[]))) for r in x['records']])
