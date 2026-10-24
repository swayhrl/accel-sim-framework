from audit_local import *
from collect_audit import SNAP
x=json.loads((P/'SOURCE_C16_PACKAGE_DUPLICATE_EVIDENCE.json').read_text(encoding='utf8'))
code=SNAP[:SNAP.index('x=dict(')]+ '\nreq='+repr(x['shards'])+r'''
import hashlib
out=[]
for r in req:
 p=r['source'];s=meta(p);old=r['source_stat'];s['historical_model_sha256']=r['prior_payload_sha256'];s['source_exact_identity_match']=all(s.get(k)==old.get({'dev':'device','allocated':'allocated_bytes'}.get(k,k)) for k in ['dev','inode','size','mtime_ns','ctime_ns'])
 f=r['source_receipt']
 if os.path.isfile(f) and os.path.getsize(f)<131072:
  b=Path(f).read_bytes();s['immutable_receipt_sha256']=hashlib.sha256(b).hexdigest();s['immutable_receipt_matches_census']=s['immutable_receipt_sha256']==r['source_receipt_sha256']
 s['outbound_current']=meta(r['destination']);out.append(s)
print(json.dumps(out))
'''
save('evidence/C16_CANONICAL_SOURCE_MODELS_CURRENT_IDENTITY_AND_IMMUTABLE_RECEIPTS.json',remote('hrl',code,60))
