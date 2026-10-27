"""Lossless bounded-buffer raw output. No actor, admission, or registry operations.
Logical canonical raw identity and physical gzip identity are distinct.
No truncation or legacy96MiB/400MiB cap. Real IO failure is raised, preserved, never accepted.
"""
import gzip,hashlib,io,os,pathlib,zlib
P=pathlib.Path;CHUNK=1<<20
class OutputIntegrityError(RuntimeError):pass
class _Sink:
 def __init__(self,disk):self.disk=disk;self.sha=hashlib.sha256();self.bytes=0
 def write(self,b):
  view=memoryview(b);n=0
  while n<len(view):
   k=self.disk.write(view[n:])
   if not k:raise OutputIntegrityError('compressed output made no forward progress')
   self.sha.update(view[n:n+k]);self.bytes+=k;n+=k
  return n
 def flush(self):self.disk.flush()
 def tell(self):return self.bytes
class RawGzipWriter:
 def __init__(self,path,compresslevel=1):
  self.path=P(path);self.disk=self.path.open('xb',buffering=0);self.sink=_Sink(self.disk);self.gz=gzip.GzipFile(filename='',mode='wb',fileobj=self.sink,compresslevel=compresslevel,mtime=0);self.logical_sha=hashlib.sha256();self.logical_bytes=0;self.crc32=0;self.closed=False;self.failed=None;self._receipt=None
 def __enter__(self):return self
 def write(self,data):
  if self.closed or self.failed:raise OutputIntegrityError('raw stream is closed/failed')
  data=memoryview(data);n=0
  try:
   for start in range(0,len(data),CHUNK):
    b=data[start:start+CHUNK];k=self.gz.write(b)
    if k!=len(b):raise OutputIntegrityError('partial logical gzip write')
    self.logical_sha.update(b);self.logical_bytes+=k;self.crc32=zlib.crc32(b,self.crc32);n+=k
   return n
  except BaseException as e:self.failed=repr(e);raise
 def flush(self):
  if not self.closed:self.gz.flush();self.sink.flush()
 def fileno(self):return self.disk.fileno()
 @property
 def stored_bytes(self):return self.sink.bytes
 @property
 def receipt(self):
  if not self.closed or self.failed:raise OutputIntegrityError('raw receipt requires successful closed stream')
  return dict(self._receipt)
 def close(self):
  if self.closed:return self.receipt
  try:
   self.gz.close();self.disk.flush();os.fsync(self.disk.fileno())
  except BaseException as e:self.failed=repr(e);raise
  finally:self.disk.close();self.closed=True
  if self.failed:raise OutputIntegrityError('preserved failed output '+self.failed)
  self._receipt={'schema':'EP_PERF_LOSSLESS_RAW_STREAM_V1','storage':'GZIP_LOSSLESS_1','path':str(self.path),'stored_sha256':self.sink.sha.hexdigest(),'stored_bytes':self.sink.bytes,'raw_sha256':self.logical_sha.hexdigest(),'raw_bytes':self.logical_bytes,'raw_crc32':self.crc32&0xffffffff,'complete_compressed_stream':True,'truncated':False,'source_keep':True}
  return self.receipt
 def __exit__(self,typ,value,tb):
  if typ is not None:self.failed=self.failed or 'producer_scope_exception:'+repr(value)
  try:self.close()
  except BaseException:
   if typ is None:raise
  return False

def open_raw(path,mode='rb',encoding='utf-8',errors='strict'):
 p=P(path)
 if mode not in('rb','rt'):raise ValueError('read-only raw interface')
 return gzip.open(p,mode,encoding=encoding,errors=errors)if mode=='rt'else gzip.open(p,'rb')
def open_raw_lines(path):return open_raw(path,'rb')
def verify_raw(path,expected=None):
 """Always consume to gzip EOF/CRC; reject truncated/trailing-invalid gzip.
 Two hashes are checked separately; no logical truncation bound is invented.
 """
 h=hashlib.sha256();size=0;crc=0
 with open_raw(path)as f:
  for b in iter(lambda:f.read(CHUNK),b''):h.update(b);size+=len(b);crc=zlib.crc32(b,crc)
 disk=hashlib.sha256();stored=0
 with P(path).open('rb')as f:
  for b in iter(lambda:f.read(CHUNK),b''):disk.update(b);stored+=len(b)
 result={'raw_sha256':h.hexdigest(),'raw_bytes':size,'raw_crc32':crc&0xffffffff,'stored_sha256':disk.hexdigest(),'stored_bytes':stored,'complete_compressed_stream':True}
 if expected:
  for k,v in result.items():
   if k in expected and expected[k]!=v:raise OutputIntegrityError('raw integrity mismatch '+k)
 return result
