"""Shared byte-rate and FD identity guard, including parser and SHA reads."""
import os,io,builtins,pathlib,fcntl,struct,time,hashlib,stat
MIB=2**20
def token(st):return(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns,st.st_mode,st.st_uid,st.st_gid)
def need(x,m):
 if not x:raise RuntimeError(m)
def ticks(pid):
 try:
  state=pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()
  return None if state[0]in ('Z','X','x')else state[19]
 except FileNotFoundError:return None
def verify_lease(fd,owner,start,expected_path):
 need(ticks(owner)==str(start),'LEASE_OWNER_CHANGED')
 seen=os.getpid()
 for _ in range(64):
  if seen==owner:break
  need(seen>1,'LEASE_OWNER_NOT_ANCESTOR')
  a=pathlib.Path('/proc',str(seen),'stat').read_text().split(') ',1)[1].split();seen=int(a[1])
 else:raise RuntimeError('LEASE_ANCESTRY_BOUND')
 expected=pathlib.Path(expected_path).stat();actual=os.fstat(fd)
 need(token(expected)==token(actual)and stat.S_ISREG(actual.st_mode),'INHERITED_LEASE_FD_IDENTITY')
 parentfd=pathlib.Path('/proc',str(owner),'fd',str(fd))
 need(parentfd.exists()and token(parentfd.stat())==token(actual),'MOTHER_FD_NOT_INHERITED')
 found=False
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  a=line.split()
  if len(a)<6 or a[1:4]!=['FLOCK','ADVISORY','WRITE']or a[4]!=str(owner):continue
  dev=a[5].split(':')
  if len(dev)==3 and int(dev[0],16)==os.major(actual.st_dev)and int(dev[1],16)==os.minor(actual.st_dev)and int(dev[2])==actual.st_ino:found=True
 need(found,'MOTHER_WHOLEJOB_LEASE_NOT_HELD')
 # Never flock/unlock the inherited whole-job description.
class Pace:
 def __init__(self,path,rate,deadline,lease):
  self.path=pathlib.Path(path);self.rate=rate;self.deadline=deadline;self.lease=lease
  self.fd=os.open(self.path,os.O_RDWR|os.O_NOFOLLOW);self.actual=0;self.reads=0
 def check(self):
  need(time.monotonic()<self.deadline,'VALIDATOR_DEADLINE')
  verify_lease(*self.lease)
 def charge(self,n):
  self.check();fcntl.flock(self.fd,fcntl.LOCK_EX)
  try:
   b=os.pread(self.fd,16,0);need(len(b)==16,'PACE_STATE')
   next_ns,total=struct.unpack('<QQ',b);now=time.monotonic_ns();slot=max(now,next_ns)
   need(os.pwrite(self.fd,struct.pack('<QQ',slot+(n*10**9+self.rate-1)//self.rate,total+n),0)==16,'PACE_WRITE')
  finally:fcntl.flock(self.fd,fcntl.LOCK_UN)
  delay=slot/1e9-time.monotonic()
  if delay>0:time.sleep(min(delay,max(0,self.deadline-time.monotonic())))
  self.check()
class Raw(io.RawIOBase):
 def __init__(self,path,pace):
  self.path=pathlib.Path(path);self.pace=pace;self.before=token(self.path.lstat())
  need(stat.S_ISREG(self.before[5]),'SOURCE_NOT_REGULAR')
  self.fd=os.open(self.path,os.O_RDONLY|os.O_NOFOLLOW)
  need(token(os.fstat(self.fd))==self.before,'SOURCE_OPEN_FD')
 def readable(self):return True
 def seekable(self):return True
 def fileno(self):return self.fd
 def tell(self):return os.lseek(self.fd,0,os.SEEK_CUR)
 def seek(self,offset,whence=os.SEEK_SET):return os.lseek(self.fd,offset,whence)
 def readinto(self,b):
  n=min(len(b),MIB);remaining=max(0,self.before[2]-self.tell());n=min(n,remaining)if remaining else 1
  self.pace.charge(n);part=os.read(self.fd,n);self.pace.actual+=len(part);self.pace.reads+=1
  b[:len(part)]=part
  need(token(os.fstat(self.fd))==self.before,'SOURCE_FD_CHANGED')
  return len(part)
 def close(self):
  if not self.closed:
   try:need(token(os.fstat(self.fd))==self.before==token(self.path.lstat()),'SOURCE_CLOSE_FD_PATH_CHANGED')
   finally:os.close(self.fd)
  super().close()
def read_bytes(path,pace,limit):
 p=pathlib.Path(path);need(p.stat().st_size<=limit,'METADATA_LIMIT')
 with io.BufferedReader(Raw(p,pace),buffer_size=MIB)as f:b=f.read(limit+1)
 need(len(b)<=limit,'METADATA_GROWTH');return b
class OpenGuard:
 def __init__(self,targets,pace):self.targets=targets;self.pace=pace
 def __enter__(self):
  self.old_builtin=builtins.open;self.old_io=io.open;self.old_path=pathlib.Path.open
  def opened(file,mode='r',buffering=-1,encoding=None,errors=None,newline=None,closefd=True,opener=None):
   try:key=os.path.abspath(os.fspath(file))
   except TypeError:return self.old_io(file,mode,buffering,encoding,errors,newline,closefd,opener)
   if key not in self.targets or any(x in mode for x in 'wax+'):return self.old_io(file,mode,buffering,encoding,errors,newline,closefd,opener)
   need(opener is None,'CUSTOM_SOURCE_OPENER')
   raw=io.BufferedReader(Raw(self.targets[key],self.pace),buffer_size=MIB)
   return raw if'b'in mode else io.TextIOWrapper(raw,encoding=encoding or'utf-8',errors=errors,newline=newline)
  builtins.open=opened;io.open=opened;pathlib.Path.open=lambda path,*a,**kw:opened(path,*a,**kw);return self
 def __exit__(self,*args):builtins.open=self.old_builtin;io.open=self.old_io;pathlib.Path.open=self.old_path
