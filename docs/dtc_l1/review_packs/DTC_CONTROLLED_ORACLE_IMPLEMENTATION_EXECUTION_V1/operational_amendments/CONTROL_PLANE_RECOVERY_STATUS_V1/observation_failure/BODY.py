import sys,os,json,threading
assert os.getpid()==1498278 and threading.current_thread()is threading.main_thread()
_rv_s=getattr(sys.modules['__main__'],'DTC_CONTROLLED_ORACLE_SHARED_POOL_V1');_rv_g=_rv_s['DTC_ORACLE_OPERATIONAL_RECOVERY_GENERATION_V1'];_rv_t=_rv_g['thread'];_rv_frames=sys._current_frames()
def _rv_chain(tid):
 f=_rv_frames.get(tid);a=[]
 while f is not None:
  a.append(dict(file=f.f_code.co_filename,fn=f.f_code.co_name,line=f.f_lineno));f=f.f_back
 return a[:15]
_rv_cap=_rv_g['environment']['_RECOVERY']['cap'];_rv_locks=[]
for _rv_fd in[3,4,_rv_cap['held'].fileno(),_rv_cap['held_duplicate'].fileno()]:
 _rv_locks.append(dict(fd=_rv_fd,inode=os.fstat(_rv_fd).st_ino,fdinfo=open('/proc/self/fdinfo/'+str(_rv_fd)).read()))
_rv_value=dict(schema='DTC_ORACLE_ACTUAL_RECOVERY_READONLY_VERIFICATION_V1',owner_pid=os.getpid(),owner_start_ticks=977758783,recovery_thread=dict(ident=_rv_t.ident,native_id=_rv_t.native_id,name=_rv_t.name,alive=_rv_t.is_alive(),daemon=_rv_t.daemon),matching_recovery_threads=[dict(name=t.name,ident=t.ident,native_id=t.native_id)for t in threading.enumerate()if t.name=='DTC_ORACLE_ONE_OPERATIONAL_RECOVERY'],original_thread_ident=_rv_s['thread_ident'],old_chain=_rv_chain(_rv_s['thread_ident']),recovery_chain=_rv_chain(_rv_t.ident),original_exception=repr(sys._current_exceptions().get(_rv_s['thread_ident'])),locks=_rv_locks,contexts=list(_rv_s['contexts']),futures_global_shutdown=getattr(sys.modules.get('concurrent.futures.thread'),'_shutdown',None),threading_shutdown=getattr(threading,'_SHUTTING_DOWN',None),loop_observed=_rv_g.get('loop_observed'),reservation_sync_pending=_rv_g.get('reservation_sync_pending'),model_starts=0,model_signals=0,registry_writes=0,thread_starts=0)
with open('/root/data/dtc_controlled_oracle_20261106_v1/control/owner_recovery_readonly_verification_v1/VERIFICATION.fixed.json','x')as _rv_h:json.dump(_rv_value,_rv_h,sort_keys=True,indent=2);_rv_h.flush();os.fsync(_rv_h.fileno())
