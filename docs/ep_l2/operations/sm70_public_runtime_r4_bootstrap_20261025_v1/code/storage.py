"""Immutable public metadata/code publisher. All bodies are metadata, never trace producers."""
from pathlib import Path
import os,json,hashlib,uuid,importlib.util
MIB=2**20
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def safe(root,rel):
 rel=Path(rel);need(not rel.is_absolute()and '..'not in rel.parts,'unsafe public relative path')
 return Path(root)/rel
class Writer:
 def __init__(self,library,resources,primitive):
  self.root=Path(library).resolve();self.resources=resources;self.primitive=primitive
 def verify(self,path,expected,size=None):
  h=hashlib.sha256();n=0
  with Path(path).open('rb',buffering=0)as f:
   for z in iter(lambda:f.read(MIB),b''):h.update(z);n+=len(z);self.resources.account(len(z),'read')
  need(h.hexdigest()==expected and(size is None or n==size),'closed public metadata/code whole SHA')
  return n
 def raw(self,rel,raw):
  path=safe(self.root,rel);self.primitive.no_symlinks(path.parent);path.parent.mkdir(parents=True,exist_ok=True)
  expected=digest(raw)
  if path.exists():need(not path.is_symlink(),'immutable leaf symlink');self.verify(path,expected,len(raw));return dict(path=str(path),sha256=expected,bytes=len(raw))
  temp=path.with_name('.'+path.name+'.owned-'+uuid.uuid4().hex)
  with temp.open('xb',buffering=0)as f:
   for off in range(0,len(raw),MIB):
    z=memoryview(raw)[off:off+MIB];need(f.write(z)==len(z),'short metadata write');self.resources.account(len(z),'write')
   os.fsync(f.fileno())
  self.verify(temp,expected,len(raw))
  try:self.primitive.rename_noreplace(temp,path)
  except FileExistsError:self.verify(path,expected,len(raw));temp.unlink()
  self.verify(path,expected,len(raw));path.chmod(0o444)
  return dict(path=str(path),sha256=expected,bytes=len(raw))
 def json(self,rel,value):
  # Encoder streams to NAS; no giant control staging file on Native.
  path=safe(self.root,rel);self.primitive.no_symlinks(path.parent);path.parent.mkdir(parents=True,exist_ok=True)
  temp=path.with_name('.'+path.name+'.owned-'+uuid.uuid4().hex);h=hashlib.sha256();count=0;buffer=bytearray()
  encoder=json.JSONEncoder(sort_keys=True,separators=(',',':'))
  with temp.open('xb',buffering=0)as f:
   def emit(z):
    nonlocal count
    need(f.write(z)==len(z),'short JSON write');h.update(z);count+=len(z);self.resources.account(len(z),'write')
   for text in encoder.iterencode(value):
    buffer.extend(text.encode())
    if len(buffer)>=MIB:emit(buffer);buffer.clear()
   buffer.extend(b'\n')
   if buffer:emit(buffer)
   os.fsync(f.fileno())
  expected=h.hexdigest();self.verify(temp,expected,count)
  if path.exists():need(not path.is_symlink(),'JSON leaf symlink');self.verify(path,expected,count);temp.unlink()
  else:self.primitive.rename_noreplace(temp,path)
  self.verify(path,expected,count);path.chmod(0o444)
  return dict(path=str(path),sha256=expected,bytes=count)
 def cas(self,raw,kind='proofs'):
  h=digest(raw);return self.raw(Path(kind)/'sha256'/h,raw)
 def link(self,rel,target):
  path=safe(self.root,rel);target=Path(target);path.parent.mkdir(parents=True,exist_ok=True)
  self.primitive.no_symlinks(path.parent)
  if os.path.lexists(path):need(path.is_symlink()and path.resolve()==target.resolve(),'public view collision');return
  path.symlink_to(os.path.relpath(target,path.parent));self.primitive.fsync_dir(path.parent)
 def pointer(self,rel,target,expected_old_sha):
  """Only reviewed mutable pointer may replace; old body is persisted first."""
  path=safe(self.root,rel);target=Path(target);self.primitive.no_symlinks(path.parent);path.parent.mkdir(parents=True,exist_ok=True)
  old=None
  if os.path.lexists(path):
   need(path.stat().st_size<=128*MIB,'public pointer metadata128MiB')
   with path.open('rb')as f:raw=f.read(128*MIB+1)
   need(len(raw)<=128*MIB,'public pointer metadata growth128MiB');h=digest(raw)
   if path.is_symlink()and path.resolve()==target.resolve():return dict(status='ALREADY_EXACT_POINTER',path=str(path),target=str(target))
   need(expected_old_sha is not None and h==expected_old_sha,'unapproved previous public pointer')
   old=dict(raw_ref=self.cas(raw,'pointer_history'),link_target=os.readlink(path)if path.is_symlink()else None,old_sha256=h)
  else:need(expected_old_sha is None,'expected old public pointer absent')
  temp=path.with_name('.'+path.name+'.pointer-'+uuid.uuid4().hex)
  temp.symlink_to(os.path.relpath(target,path.parent));self.primitive.fsync_dir(path.parent)
  # Approved sole replacement is a metadata/code pointer, never an original/trace body.
  os.replace(temp,path);self.primitive.fsync_dir(path.parent)
  need(path.is_symlink()and path.resolve()==target.resolve(),'closed pointer target')
  return dict(status='ACTIVATED_EXACT_NEW_POINTER',path=str(path),target=str(target),old=old)
