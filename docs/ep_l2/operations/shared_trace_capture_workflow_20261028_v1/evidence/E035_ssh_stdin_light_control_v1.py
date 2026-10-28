"""Bounded SSH stdin control only. No filesystem, NAS logger, signal or process operations."""
import os,json,time,math,select,threading
MAX_FRAME=4096
MAX_AGE=20.0
class ChannelError(RuntimeError):pass
def need(v,m):
 if not v:raise ChannelError(m)
def number(v):return type(v)in(int,float)and math.isfinite(v)
def frame_check(v,scope,run,seq,now):
 need(type(v)is dict and set(v)=={'schema','scope_sha256','run_id','seq','sent_unix','kind','stop_reason','native_physics'}and v.get('schema')=='SSH_STDIN_LIGHT_CONTROL_V1','FRAME_SCHEMA')
 need(v.get('scope_sha256')==scope and v.get('run_id')==run,'FRAME_SCOPE_RUN')
 need(type(v.get('seq'))is int and v['seq']==seq,'FRAME_EXACT_NEXT_SEQ')
 need(v.get('kind')in ['BEAT','STOP'],'FRAME_KIND')
 need(v.get('stop_reason')is None if v['kind']=='BEAT'else type(v.get('stop_reason'))is str and len(v['stop_reason'])<=160,'FRAME_STOP_REASON')
 need(number(v.get('sent_unix'))and 0<=now-v['sent_unix']<MAX_AGE,'FRAME_SENT_AGE20')
 p=v.get('native_physics');need(type(p)is dict and set(p)=={'status','sample_unix','sample_seq'}and p.get('status')in ['PASS','HOLD','ERROR'],'FRAME_NATIVE_PHYSICS')
 need(number(p.get('sample_unix'))and 0<=now-p['sample_unix']<MAX_AGE,'FRAME_PHYSICS_AGE20')
 need(type(p.get('sample_seq'))is int and p['sample_seq']>=1,'FRAME_PHYSICS_SEQ')
 return v
class NativeChannel:
 def __init__(self,fd,scope_sha256,run_id,sample,deadline_unix,interval=2.0,sample_interval=5.0):
  need(.05<=interval<=2 and .05<=sample_interval<=5,'BOUNDED_CONTROL_INTERVALS')
  self.fd=fd;self.scope=scope_sha256;self.run=run_id;self.sample=sample;self.deadline=deadline_unix;self.interval=interval;self.sample_interval=sample_interval
  self.lock=threading.Lock();self.done=threading.Event();self.state=dict(seq=0,sample_seq=0,physics=None,physical_at=None,stop_reason=None,send_error=None)
 def stop(self,reason):
  with self.lock:
   if self.state['stop_reason']is None:self.state['stop_reason']=str(reason)[:160]
 def _sample(self):
  try:
   value=self.sample();need(type(value)is dict and value.get('status')in ['PASS','HOLD'],'PHYSICAL_SAMPLE_STATUS')
   status=value['status']
  except BaseException as e:
   status='ERROR'
   with self.lock:self.state['physical_error']=type(e).__name__+':'+str(e)[:160]
  with self.lock:
   self.state['sample_seq']+=1;self.state['physical_at']=time.monotonic();self.state['physics']=dict(status=status,sample_unix=time.time(),sample_seq=self.state['sample_seq'])
  if status!='PASS':self.stop('NATIVE_PHYSICS_'+status)
 def _physical_loop(self):
  while not self.done.wait(self.sample_interval):self._sample()
 def _sender_loop(self):
  while not self.done.is_set():
   if time.time()>=self.deadline:self.stop('NATIVE_ABSOLUTE_DEADLINE')
   with self.lock:
    if self.state['physical_at']is None or time.monotonic()-self.state['physical_at']>=MAX_AGE:
     if self.state['stop_reason']is None:self.state['stop_reason']='NATIVE_PHYSICS_STALE20'
    q=dict(self.state);physics=None if q['physics']is None else dict(q['physics'])
   frame=dict(schema='SSH_STDIN_LIGHT_CONTROL_V1',scope_sha256=self.scope,run_id=self.run,seq=q['seq']+1,sent_unix=time.time(),kind='STOP'if q['stop_reason']else'BEAT',stop_reason=q['stop_reason'],native_physics=physics)
   raw=(json.dumps(frame,sort_keys=True,separators=(',',':'))+'\n').encode()
   try:
    need(len(raw)<=MAX_FRAME,'NATIVE_FRAME_BOUND');until=time.monotonic()+1
    while True:
     need(time.monotonic()<until,'CONTROL_PIPE_WRITE_TIMEOUT1')
     if not select.select([], [self.fd], [], min(.1,max(0,until-time.monotonic())))[1]:continue
     try:count=os.write(self.fd,raw)
     except BlockingIOError:continue
     need(count==len(raw),'CONTROL_PIPE_ATOMIC_FRAME');break
    with self.lock:self.state['seq']=frame['seq']
   except BaseException as e:
    with self.lock:self.state['send_error']=type(e).__name__+':'+str(e)[:160]
    self.stop('CONTROL_PIPE_SEND_FAILED');return
   self.done.wait(self.interval)
 def start(self):
  os.set_blocking(self.fd,False);self._sample()
  self.physical_thread=threading.Thread(target=self._physical_loop,daemon=False);self.sender_thread=threading.Thread(target=self._sender_loop,daemon=False)
  self.physical_thread.start();self.sender_thread.start();return self
 def snapshot(self):
  with self.lock:return dict(self.state)
 def finish_after_owned_closed(self):
  self.done.set();self.sender_thread.join(2);self.physical_thread.join(6)
  need(not self.sender_thread.is_alive()and not self.physical_thread.is_alive(),'NATIVE_CONTROL_THREADS_CLOSED')
class RemoteReader:
 def __init__(self,fd,scope_sha256,run_id):
  self.fd=fd;self.scope=scope_sha256;self.run=run_id;self.lock=threading.Lock();self.done=threading.Event();self.latest=None;self.last_read=None;self.error=None;self.seq=0
 def _fail(self,reason):
  with self.lock:
   if self.error is None:self.error=str(reason)[:240]
 def _loop(self):
  pending=b''
  try:
   while not self.done.is_set():
    if not select.select([self.fd],[],[],.1)[0]:continue
    data=os.read(self.fd,MAX_FRAME)
    need(data,'CONTROL_PIPE_EOF')
    pending+=data
    while b'\n'in pending:
     raw,pending=pending.split(b'\n',1);need(len(raw)+1<=MAX_FRAME,'REMOTE_FRAME_BOUND')
     try:v=json.loads(raw)
     except (ValueError,UnicodeDecodeError):raise ChannelError('REMOTE_FRAME_MALFORMED_JSON')
     frame_check(v,self.scope,self.run,self.seq+1,time.time())
     with self.lock:old_physics=None if self.latest is None else dict(self.latest['native_physics'])
     if old_physics is not None:
      current=v['native_physics'];need(current['sample_seq']>=old_physics['sample_seq'],'PHYSICS_SAMPLE_SEQ_ROLLBACK')
      need(current==old_physics if current['sample_seq']==old_physics['sample_seq']else current['sample_unix']>=old_physics['sample_unix'],'PHYSICS_SAMPLE_REPLAY_OR_TIME_ROLLBACK')
     with self.lock:self.seq=v['seq'];self.latest=v;self.last_read=time.monotonic()
     if v['kind']=='STOP':raise ChannelError('NATIVE_STOP:'+str(v.get('stop_reason'))[:160])
     need(v['native_physics']['status']=='PASS','NATIVE_PHYSICS_NOT_PASS')
    need(len(pending)<MAX_FRAME,'REMOTE_UNTERMINATED_FRAME_BOUND')
  except BaseException as e:self._fail(type(e).__name__+':'+str(e))
 def start(self):
  self.thread=threading.Thread(target=self._loop,daemon=False);self.thread.start();return self
 def check(self):
  with self.lock:error=self.error;v=None if self.latest is None else dict(self.latest);stamp=self.last_read
  need(error is None,'REMOTE_CONTROL_FAILED:'+str(error));need(v is not None and stamp is not None,'NO_CONTROL_FRAME')
  need(time.monotonic()-stamp<MAX_AGE,'REMOTE_CONTROL_STALE20')
  frame_check(v,self.scope,self.run,v['seq'],time.time())
  need(v['kind']=='BEAT'and v['native_physics']['status']=='PASS','REMOTE_CONTROL_NOT_LIVE_PASS')
  return dict(seq=v['seq'],last_read_age_seconds=time.monotonic()-stamp,native_sent_unix=v['sent_unix'],native_physics=dict(v['native_physics']))
 def wait_ready(self):
  until=time.monotonic()+MAX_AGE
  while True:
   with self.lock:seen=self.latest is not None;error=self.error
   need(error is None,'REMOTE_CONTROL_FAILED:'+str(error))
   if seen:return self.check()
   need(time.monotonic()<until,'INITIAL_CONTROL_TIMEOUT20');time.sleep(.05)
 def finish_after_owned_closed(self):
  self.done.set();self.thread.join(2);need(not self.thread.is_alive(),'REMOTE_READER_CLOSED_BEFORE_INTERPRETER_EXIT')
