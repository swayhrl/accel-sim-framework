"""IO/sampling adapter only. Frozen derive/consume/verification bodies are not edited."""
import io,os,fcntl,hashlib,lzma,pathlib,types,contextlib,importlib.util
MAX_READ=2**20
class BoundIO:
 def __init__(self,parent,work,guard,pace,lock):
  self.parent=pathlib.Path(parent);self.work=pathlib.Path(work);self.guard=guard;self.pace=pace;self.lock=lock;self.low_reads=0;self.read_bytes=0;self.max_requested=0;self.events=0;self.blocks_original=None
 def is_source(self,p):return pathlib.Path(p)==self.parent or self.parent in pathlib.Path(p).parents
 def reader(self,path):
  owner=self
  class Raw(io.RawIOBase):
   def __init__(self):super().__init__();self.raw=io.FileIO(os.fspath(path),'r')
   def readable(self):return True
   def readinto(self,b):
    owner.guard();n=min(len(b),MAX_READ);assert 0<=n<=MAX_READ
    fcntl.flock(owner.lock,fcntl.LOCK_EX)
    try:
     data=self.raw.read(n);owner.low_reads+=1;owner.read_bytes+=len(data);owner.max_requested=max(owner.max_requested,n)
     if data:owner.pace(len(data))
    finally:fcntl.flock(owner.lock,fcntl.LOCK_UN)
    b[:len(data)]=data;return len(data)
   def close(self):
    if not self.closed:self.raw.close()
    super().close()
  return io.BufferedReader(Raw(),buffer_size=MAX_READ)
 def parent_path(self):
  owner=self
  class SourcePath(type(pathlib.Path())):
   def open(self,mode='r',buffering=-1,encoding=None,errors=None,newline=None):
    assert owner.is_source(self) and mode in ['r','rb'],'parent is read-only'
    raw=owner.reader(self)
    return raw if mode=='rb'else io.TextIOWrapper(raw,encoding=encoding,errors=errors,newline=newline)
  return SourcePath(self.parent)
 def digest(self,p):
  p=pathlib.Path(p);h=hashlib.sha256()
  with(self.reader(p)if self.is_source(p)else p.open('rb'))as f:
   while True:
    self.guard();b=f.read(MAX_READ)
    if not b:break
    h.update(b)
  return h.hexdigest()
 def copyfile(self,source,dest):
  source=pathlib.Path(source);dest=pathlib.Path(dest);assert self.work in dest.parents
  with(self.reader(source)if self.is_source(source)else source.open('rb'))as inp,dest.open('wb')as out:
   while True:
    self.guard();b=inp.read(MAX_READ)
    if not b:break
    out.write(b)
   out.flush();os.fsync(out.fileno())
  return dest
 def install(self,d,parser_cache):
  original_lzma=lzma.open;original_spec=d.importlib.util.spec_from_file_location;original_module=d.importlib.util.module_from_spec
  @contextlib.contextmanager
  def source_lzma(path,mode='rb',**kw):
   if not self.is_source(path):
    with original_lzma(path,mode,**kw)as f:yield f
   else:
    assert mode in ['r','rb','rt'] and not kw
    with self.reader(path)as raw,lzma.LZMAFile(raw,'rb')as uncompressed:
     if mode=='rt':
      with io.TextIOWrapper(uncompressed)as text:yield text
     else:yield uncompressed
  d.lzma=types.SimpleNamespace(open=source_lzma,LZMAFile=lzma.LZMAFile)
  d.sha=self.digest;d.shutil=types.SimpleNamespace(copyfile=self.copyfile)
  def parser_spec(name,path):
   assert pathlib.Path(path)==self.parent/'contract/validate_v7.py'
   return original_spec(name,parser_cache)
  d.importlib=types.SimpleNamespace(util=types.SimpleNamespace(spec_from_file_location=parser_spec,module_from_spec=original_module))
  self.blocks_original=d.blocks
  def sampled_blocks(path):
   for n,event in enumerate(self.blocks_original(path)):
    self.events+=1
    if n%4096==0:self.guard()
    yield event
   self.guard()
  d.blocks=sampled_blocks
 def receipt(self):return dict(low_level_NAS_reads=self.low_reads,NAS_bytes=self.read_bytes,max_low_level_read_request_bytes=self.max_requested,CPU_events=self.events,guard_every_at_most_events=4096,Source_metadata_hash_XZ_tool_copies_share_one_low_read_adapter=True)
