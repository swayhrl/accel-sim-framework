"""Bounded real local/SSH subprocess heartbeat; EOF is the remote cleanup signal."""
import subprocess,threading,time
def run(argv,deadline,err,floor_ok,heartbeat_seconds=2):
 chunks=[];size=[0];overflow=threading.Event();stop=threading.Event()
 p=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True)
 def drain():
  while True:
   x=p.stdout.read(8192)
   if not x:break
   size[0]+=len(x)
   if size[0]<=1048576:chunks.append(x)
   else:overflow.set()
 def pulse():
  try:
   while not stop.is_set():
    if not floor_ok() or time.time()>=deadline-20:break
    p.stdin.write('alive\n');p.stdin.flush()
    if stop.wait(heartbeat_seconds):break
  except (BrokenPipeError,OSError,ValueError):pass
  finally:
   try:p.stdin.close()
   except (BrokenPipeError,OSError,ValueError):pass
 reader=threading.Thread(target=drain,daemon=True);heart=threading.Thread(target=pulse,daemon=True);reader.start();heart.start();transport=None
 try:p.wait(timeout=max(1,deadline-time.time()-5))
 except BaseException as e:
  transport=repr(e);stop.set();heart.join(timeout=3)
  try:p.wait(timeout=45)
  except subprocess.TimeoutExpired:p.kill();p.wait()
 finally:stop.set();heart.join(timeout=3);reader.join(timeout=5)
 assert not reader.is_alive() and not overflow.is_set(),'stdout unknown/overflow'
 return p.returncode,''.join(chunks),transport
