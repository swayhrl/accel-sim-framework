"""Single exact serialization, spool then immutable publish. Pure artifact IO only.
No pretty-vs-default estimate mismatch; all semantic JSON population retained.
"""
import hashlib,json,os,pathlib,tempfile
P=pathlib.Path
class BundleError(ValueError):pass
def canonical_keys(obj):
 if isinstance(obj,dict):
  out={}
  for k,v in obj.items():
   if type(k)not in(str,int):raise BundleError('non-JSON dictionary key')
   key=str(k)
   if key in out:raise BundleError('semantic key collision after JSON serialization')
   out[key]=canonical_keys(v)
  return out
 if isinstance(obj,(list,tuple)):return [canonical_keys(v)for v in obj]
 return obj
class CompactBundle:
 def __init__(self,spool_path,sha256,bytes,semantic):self.spool_path=P(spool_path);self.sha256=sha256;self.bytes=bytes;self.semantic=semantic;self.published=None
 def check_budget(self,remaining_bytes):
  if type(remaining_bytes)is not int or remaining_bytes<self.bytes:raise BundleError('exact compact spool exceeds actual remaining bytes')
  return self.bytes
 def publish(self,destination):
  p=P(destination)
  if p.absolute()==self.spool_path.absolute():raise BundleError("publish destination is the spool")
  if p.exists():
   if p.is_symlink()or _sha(p)!=self.sha256 or p.stat().st_size!=self.bytes:raise BundleError('immutable bundle collision')
   self.published=p;return self.receipt()
  if self.spool_path.parent.stat().st_dev!=p.parent.stat().st_dev:raise BundleError('publish requires same native filesystem; do not copy uncounted temporary')
  os.link(self.spool_path,p);_fsync(p.parent);self.published=p
  return self.receipt()
 def receipt(self):return {'schema':'EP_PERF_EXACT_COMPACT_BUNDLE_V1','spool_path':str(self.spool_path),'published_path':str(self.published)if self.published else None,'sha256':self.sha256,'bytes':self.bytes,'serialization':'UTF8_CANONICAL_JSON_COMPACT_ONE_PASS','integer_key_normalization':'string keys with collision rejection','same_serialization_for_budget_and_write':True,'population_dropped':False}
 def release_spool_after_publish(self):
  if self.published is None or _sha(self.published)!=self.sha256:raise BundleError('cannot release unverified/unpublished spool')
  self.spool_path.unlink();_fsync(self.spool_path.parent)
def _sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def _fsync(p):
 fd=os.open(p,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def spool_bundle(value,directory):
 directory=P(directory);semantic=canonical_keys(value);fd,name=tempfile.mkstemp(prefix='.COMPACT_BUNDLE.',suffix='.spool',dir=directory);h=hashlib.sha256();n=0
 # This is the ONLY serialization. A failed spool is deliberately preserved.
 with os.fdopen(fd,'wb')as f:
  for text in json.JSONEncoder(sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).iterencode(semantic):
   b=text.encode('utf-8');f.write(b);h.update(b);n+=len(b)
  f.write(b'\n');h.update(b'\n');n+=1;f.flush();os.fsync(f.fileno())
 _fsync(directory);return CompactBundle(name,h.hexdigest(),n,semantic)
def exact_bundle(value,destination,remaining_bytes=None):
 p=P(destination);bundle=spool_bundle(value,p.parent)
 if remaining_bytes is not None:bundle.check_budget(remaining_bytes)
 receipt=bundle.publish(p);bundle.release_spool_after_publish();return receipt
