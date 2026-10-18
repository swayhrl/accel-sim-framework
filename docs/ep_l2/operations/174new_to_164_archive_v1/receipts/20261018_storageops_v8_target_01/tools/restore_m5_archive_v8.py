"""Exact18-member zstd/tar recovery, bounded writes and full reopened hashes."""
import ctypes as c,hashlib,json,os,tarfile,time,decimal
from pathlib import Path,PurePosixPath
RATE=30*1024**2;SEGMENT=512*1024**2
def need(v,msg):
 if not v:raise RuntimeError(msg)
class In(c.Structure):_fields_=[('src',c.c_void_p),('size',c.c_size_t),('pos',c.c_size_t)]
class Out(c.Structure):_fields_=[('dst',c.c_void_p),('size',c.c_size_t),('pos',c.c_size_t)]
class ZstdReader:
 def __init__(self,path):
  self.f=Path(path).open('rb');self.z=c.CDLL('libzstd.so.1');self.z.ZSTD_createDStream.restype=c.c_void_p;self.z.ZSTD_initDStream.argtypes=[c.c_void_p];self.z.ZSTD_initDStream.restype=c.c_size_t;self.z.ZSTD_freeDStream.argtypes=[c.c_void_p];self.z.ZSTD_decompressStream.argtypes=[c.c_void_p,c.POINTER(Out),c.POINTER(In)];self.z.ZSTD_decompressStream.restype=c.c_size_t;self.z.ZSTD_isError.argtypes=[c.c_size_t];self.z.ZSTD_isError.restype=c.c_uint
  self.ctx=self.z.ZSTD_createDStream();need(bool(self.ctx),'zstd context allocation');self.z.ZSTD_initDStream(self.ctx);self.ib=In(None,0,0);self.mem=None;self.pending=bytearray();self.last=1;self.finished=False;self.compressed_bytes=0
 def read(self,n):
  while len(self.pending)<n and not self.finished:
   if self.ib.pos==self.ib.size:
    raw=self.f.read(128*1024);self.compressed_bytes+=len(raw)
    if not raw and self.last==0:self.finished=True;break
    self.mem=c.create_string_buffer(raw);self.ib=In(c.cast(self.mem,c.c_void_p),len(raw),0)
   if self.last==0:self.z.ZSTD_initDStream(self.ctx)
   outmem=c.create_string_buffer(128*1024);ob=Out(c.cast(outmem,c.c_void_p),len(outmem),0);old=self.ib.pos;self.last=self.z.ZSTD_decompressStream(self.ctx,c.byref(ob),c.byref(self.ib));need(not self.z.ZSTD_isError(self.last),'zstd checksum/decode error');self.pending.extend(outmem.raw[:ob.pos]);need(ob.pos or self.ib.pos>old or self.last==0,'truncated/nonprogress zstd stream')
  raw=bytes(self.pending[:n]);del self.pending[:n];return raw
 def close(self):
  if self.ctx:self.z.ZSTD_freeDStream(self.ctx);self.ctx=None
  self.f.close()
def name(value):
 p=value.removeprefix('./').rstrip('/');p=p.removeprefix('gesu/')
 if p in ['.','gesu','']:return ''
 q=PurePosixPath(p);need(not q.is_absolute() and '..' not in q.parts and '\\' not in p,'unsafe tar member');return p
def pace(n,t):
 delay=n/RATE-(time.monotonic()-t)
 if delay>0:time.sleep(delay)
def extract(archive,manifest,destination):
 m=json.loads(Path(manifest).read_bytes());dest=Path(destination);need(dest.is_absolute() and dest.parent.is_dir() and dest.parent.resolve()==dest.parent and not os.path.lexists(dest),'new absent recovery destination required');expected={f['relative_path']:f for f in m['files']};dirs={d['relative_path']:d for d in m['directories']};need(len(expected)==18 and len(dirs)==2,'wrong exact scope');need(Path(archive).is_file() and Path(archive).resolve()==Path(archive),'unsafe archive');dest.mkdir(mode=0o700);reader=ZstdReader(archive);seen={};seen_dirs=set();work=0;started=time.monotonic()
 try:
  with tarfile.open(fileobj=reader,mode='r|') as tf:
   for member in tf:
    key=name(member.name)
    if not key:need(member.isdir(),'unexpected root member');continue
    if member.isdir():
     need(key in dirs and key not in seen_dirs,'extra/duplicate directory');d=dirs[key];need((member.uid,member.gid,member.mode,int(decimal.Decimal(str(member.mtime))*10**9))==(d['uid'],d['gid'],d['mode'],d['mtime_ns']),'tar directory numerical metadata mismatch');(dest/key).mkdir(parents=True,exist_ok=True,mode=0o700);seen_dirs.add(key);continue
    need(member.isfile() and not member.islnk() and not member.issym() and key in expected and key not in seen,'extra/duplicate/nonregular member');f=expected[key];need((member.size,member.uid,member.gid,member.mode,int(decimal.Decimal(str(member.mtime))*10**9))==(f['size_bytes'],f['uid'],f['gid'],f['mode'],f['mtime_ns']),'member size/numerical metadata mismatch');q=dest/key;q.parent.mkdir(parents=True,exist_ok=True,mode=0o700);fd=None;written=0;segment_start=0;segment_count=0;h=hashlib.sha256();reopened=hashlib.sha256();segments=[]
    with tf.extractfile(member) as source:
     while written<member.size:
      fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600) if written==0 else os.open(q,os.O_WRONLY|os.O_APPEND|os.O_NOFOLLOW);seg=hashlib.sha256();segment_count=0
      with os.fdopen(fd,'ab') as out:
       while segment_count<SEGMENT and written<member.size:
        data=source.read(min(4*1024**2,SEGMENT-segment_count,member.size-written));need(data,'short tar member');out.write(data);h.update(data);seg.update(data);written+=len(data);segment_count+=len(data);work+=len(data);pace(work,started)
       out.flush();os.fsync(out.fileno())
      verify=hashlib.sha256();left=segment_count
      with q.open('rb') as back:
       back.seek(segment_start)
       while left:
        data=back.read(min(left,4*1024**2));need(data,'short reopened segment');verify.update(data);reopened.update(data);left-=len(data);work+=len(data);pace(work,started)
      need(verify.hexdigest()==seg.hexdigest(),'closed reopened segment hash mismatch');segments.append(dict(offset=segment_start,bytes=segment_count,sha256=verify.hexdigest()));segment_start+=segment_count
    if not member.size:
     fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);os.close(fd)
     with q.open('rb') as back:need(back.read()==b'','zero marker mismatch')
    need(written==member.size and h.hexdigest()==reopened.hexdigest()==f['sha256'],'complete member reopened SHA mismatch');seen[key]=dict(size_bytes=written,sha256=reopened.hexdigest(),closed_reopened_segments=segments,numeric_metadata_matched_frozen_source=True)
  while True:
   tail=reader.read(4*1024**2)
   if not tail:break
   need(not any(tail),'nonzero extra content after tar end')
  need(reader.finished and set(seen)==set(expected) and seen_dirs==set(dirs),'missing scope or incomplete zstd frame')
  return dict(status='ALL18_MEMBERS_RESTORED_AND_REOPENED_SHA_VERIFIED',destination=str(dest),files=seen,directories=sorted(seen_dirs),restored_bytes=sum(f['size_bytes'] for f in seen.values()),compressed_bytes_read=reader.compressed_bytes,zstd_frame_checksum_and_eof_verified=True,all_tar_uid_gid_mode_mtime_match_frozen_source=True,max_closed_reopened_segment_bytes=max((s['bytes'] for f in seen.values() for s in f['closed_reopened_segments']),default=0),native164_metadata_not_claimed=True,source_files_modified=0)
 finally:reader.close()
