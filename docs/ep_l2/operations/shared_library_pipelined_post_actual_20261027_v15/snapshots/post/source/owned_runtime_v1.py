import pathlib,os,time,signal,json,hashlib,ctypes

def ident(pid):
 try:
  t=pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()
  return (int(pid),t[19],int(t[1]))
 except (FileNotFoundError,ProcessLookupError):return None

def children(root):
 out={root[0]:root};changed=True
 rows=[x for p in pathlib.Path('/proc').iterdir() if p.name.isdigit() and (x:=ident(int(p.name)))]
 while changed:
  changed=False
  for x in rows:
   if x[2] in out and x[0] not in out:out[x[0]]=x;changed=True
 return list(out.values())[1:]

def send(x,sig):
 # pidfd pins the process identity; ticks are checked after opening it.
 try:fd=os.pidfd_open(x[0],0)
 except ProcessLookupError:return False
 try:
  y=ident(x[0])
  if y is None or y[1]!=x[1]:return False
  signal.pidfd_send_signal(fd,sig,None,0);return True
 except ProcessLookupError:return False
 finally:os.close(fd)

def cleanup(me):
 # Subreaper retains orphans. Stop each known parent before enumerating descendants.
 frozen={}
 for _ in range(20):
  found=children(me)
  for x in found:send(x,signal.SIGSTOP);frozen[x[0]]=x
  current=children(me)
  if all(x[0] in frozen and frozen[x[0]][1]==x[1] for x in current):break
 else:raise RuntimeError('cannot stabilize owned descendants')
 for x in frozen.values():send(x,signal.SIGTERM)
 for x in frozen.values():send(x,signal.SIGCONT)
 until=time.monotonic()+3
 while time.monotonic()<until and children(me):
  try:
   while os.waitpid(-1,os.WNOHANG)[0]:pass
  except ChildProcessError:pass
  time.sleep(.05)
 # TERM handlers may spawn: stop parents, enumerate, then KILL exact identities.
 for _ in range(20):
  xs=children(me)
  if not xs:break
  for x in xs:send(x,signal.SIGSTOP)
  for x in children(me):send(x,signal.SIGSTOP);send(x,signal.SIGKILL)
  try:
   while os.waitpid(-1,os.WNOHANG)[0]:pass
  except ChildProcessError:pass
  time.sleep(.05)
 assert not children(me),'owned descendants survived cleanup'
 return [{'pid':x[0],'start_ticks':x[1]} for x in frozen.values()]

def need(x,m):
 if not x:raise RuntimeError(m)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def write(p,x):
 p=pathlib.Path(p);raw=(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
 temp=p.with_name('.owned_'+str(os.getpid())+'_'+str(time.time_ns()))
 with temp.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 try:os.link(temp,p)
 finally:temp.unlink()
def set_subreaper():need(ctypes.CDLL(None).prctl(36,1,0,0,0)==0,'subreaper')
def reap():
 try:
  while os.waitpid(-1,os.WNOHANG)[0]:pass
 except ChildProcessError:pass
def hold(path,error,fds):
 # A failed NAS diagnostic must never release the remaining OFD holders.
 for sig in (signal.SIGTERM,signal.SIGHUP,signal.SIGINT):signal.signal(sig,signal.SIG_IGN)
 try:write(path,dict(status='HOLD_OWNED_UNKNOWN_LEASES_RETAINED',error=repr(error),owner=ident(os.getpid()),owned=children(ident(os.getpid())),fds=fds))
 except BaseException:pass
 while True:
  try:time.sleep(1)
  except BaseException:pass
