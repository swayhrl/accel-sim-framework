from closure_local import *
import urllib.request
ref='46de0c35e2c26fdabd9fc691370bedf0cc5974f5';base='docs/vm_tlb/review_packs/C12_C15_174NEW_CANONICAL_INHERITANCE_V2/'
out=[]
for name in ['NODE164_ARCHIVE_MANIFEST.tsv','NODE164_ARCHIVE_RECEIPTS.tsv','SOURCE_DESTINATION_HASH_CLOSURE.tsv','PRIVATE_EXPORT_INGEST_STATUS.md','HISTORICAL_RESULT_STATUS.tsv','MIGRATION_SUMMARY.md']:
 url='https://raw.githubusercontent.com/swayhrl/accel-sim-framework/'+ref+'/'+base+name
 try:
  with urllib.request.urlopen(url,timeout=25) as r:b=r.read(2*1024**2+1)
  assert len(b)<=2*1024**2
  out.append(dict(commit=ref,path=base+name,sha256=hashlib.sha256(b).hexdigest(),text=b.decode()));print(name,b.decode()[:2000])
 except Exception as e:out.append(dict(path=base+name,error=str(e)))
save('owner/LEGACY_C12_C15_CANONICAL_ARCHIVE_OWNER_PROOFS.json',out)
