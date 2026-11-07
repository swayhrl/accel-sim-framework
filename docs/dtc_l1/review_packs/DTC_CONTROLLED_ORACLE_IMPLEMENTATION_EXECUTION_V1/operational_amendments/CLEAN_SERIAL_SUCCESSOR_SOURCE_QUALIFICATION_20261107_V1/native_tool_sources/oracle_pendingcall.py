"""Typed same-process once-only Main-thread handoff, no model/registry API."""
import ctypes,threading,traceback,signal,os
KEEP=[]
class OnceMainCallback:
 def __init__(self,callback,wake_blocked_main=True):
  assert callable(callback)
  self.callback=callback;self.lock=threading.RLock();self.state='ARMED';self.result=None;self.error=None;self.queued_count=0;self.delivered_count=0;self.wake_count=0;self.pid=os.getpid();self.main_ident=threading.main_thread().ident;self.wake_blocked_main=wake_blocked_main;self.wake_handler_restored=False
  if wake_blocked_main:
   assert threading.current_thread()is threading.main_thread(),'WAKE_INSTALL_MAIN_THREAD_ONLY'
   self.previous_wake_handler=signal.getsignal(signal.SIGWINCH)
   assert self.previous_wake_handler in[signal.SIG_DFL,signal.SIG_IGN],'EXISTING_MEANINGFUL_SIGWINCH_HANDLER_HOLD'
   def wake(signum,frame):
    # A rejected CPython queue has no callback to run its finally block. This
    # same Main-thread signal hook restores its own harmless handler instead.
    if self.state=='HOLD'and self.delivered_count==0:self.restore_wake_handler()
   self._wake_handler=wake
   signal.signal(signal.SIGWINCH,self._wake_handler)
  self._ctype=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_void_p);self._pointer=self._ctype(self._deliver)
  address=ctypes.cast(ctypes.pythonapi.Py_AddPendingCall,ctypes.c_void_p).value
  # A typed private API pointer never changes ctypes.pythonapi global argtypes.
  self._api=ctypes.PYFUNCTYPE(ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p)(address)
  KEEP.append(self) # owner lifetime: C callback/function must never be collected
 def _deliver(self,_):
  with self.lock:
   if self.state not in['ENQUEUING','QUEUED']:
    self.error='DUPLICATE_OR_UNARMED_PENDING_DELIVERY';self.state='HOLD';return 0
   self.state='EXECUTING';self.delivered_count+=1
  try:
   assert threading.current_thread()is threading.main_thread(),'PENDING_CALLBACK_NOT_MAIN_THREAD'
   self.result=self.callback()
   with self.lock:self.state='DONE'
  except BaseException:
   with self.lock:self.error=traceback.format_exc();self.state='HOLD'
  finally:
   if self.wake_blocked_main and threading.current_thread()is threading.main_thread():self.restore_wake_handler()
  return 0
 def restore_wake_handler(self):
  assert threading.current_thread()is threading.main_thread()
  if self.wake_blocked_main and not self.wake_handler_restored:
   if signal.getsignal(signal.SIGWINCH)is self._wake_handler:signal.signal(signal.SIGWINCH,self.previous_wake_handler);self.wake_handler_restored=True
   else:self.error='OWN_SIGWINCH_WAKE_HANDLER_CHANGED_EXTERNALLY';self.state='HOLD'
 def queue_once(self):
  with self.lock:
   if self.state!='ARMED':return dict(state=self.state,queued=False,queued_count=self.queued_count)
   self.state='ENQUEUING';code=self._api(ctypes.cast(self._pointer,ctypes.c_void_p),None)
   if code!=0:
    self.state='HOLD';self.error='PY_ADD_PENDING_CALL_QUEUE_REJECTED_NO_AUTO_REQUEUE'
    if self.wake_blocked_main:
     assert os.getpid()==self.pid
     signal.pthread_kill(self.main_ident,signal.SIGWINCH);self.wake_count+=1
    return dict(state=self.state,queued=False,returncode=code)
   self.queued_count+=1
   if self.state=='ENQUEUING':self.state='QUEUED'
   if self.wake_blocked_main and self.state in['ENQUEUING','QUEUED']:
    assert os.getpid()==self.pid,'WAKE_MUST_TARGET_ORIGINAL_PROCESS_ONLY'
    signal.pthread_kill(self.main_ident,signal.SIGWINCH);self.wake_count+=1
   return dict(state=self.state,queued=True,queued_count=self.queued_count)
 def snapshot(self):
  with self.lock:return dict(state=self.state,queued_count=self.queued_count,delivered_count=self.delivered_count,result=self.result,error=self.error,wake_count=self.wake_count,wake_handler_restored=self.wake_handler_restored,wake_method='SAME_PROCESS_MAIN_PTHREAD_SIGWINCH_NOOP'if self.wake_blocked_main else'DISABLED_CPU_NEGATIVE_CONTROL')
