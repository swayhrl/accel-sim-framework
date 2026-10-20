set pagination off
set confirm off
set debuginfod enabled off
set disable-randomization off
set index-cache enabled off
set history save off
maintenance set worker-threads 1
set print elements 8
set max-value-size 131072
handle SIGABRT stop print nopass
python
import gdb,json
phase=False
observations=[]
def emit(kind,extra=None):
 row={'kind':kind}
 if extra:row.update(extra)
 frame=gdb.newest_frame()
 while frame:
  if frame.name()=='main':
   try:
    f=frame.read_var('f');cache=f['cache'].dereference();p=cache['m_ft_pending']
    row['gpu_cycle']=int(f['gpu'].dereference()['gpu_sim_cycle'])
    row['total_cycle']=int(f['gpu'].dereference()['gpu_tot_sim_cycle'])
    row['pending']={k:str(p[k]) for k in ['request','dirty','wad','bound','phase','tag_index']}
    row['last_payload_request_result']=str(cache['m_ep_l2_last_payload_request_result'])
    row['tvd_lookup']=str(cache['m_tvd_lookup']);row['tvd_lookup_done']=bool(cache['m_tvd_lookup_done'])
    row['m_miss_queue_size']=int(cache['m_config']['m_miss_queue_size'])
    row['bank_block']=int(cache['m_ft_stats']['bank_block']);row['rollback_count']=int(cache['m_ft_stats']['rollback'])
   except Exception as e:row['read_error']=str(e)
   try:row['status_local']=str(frame.read_var('status'))
   except Exception as e:row['status_unavailable']=str(e)
   break
  frame=frame.older()
 observations.append(row);gdb.write('E_ROLLBACK_DIAG|'+json.dumps(row,sort_keys=True)+'\n')
class Mark(gdb.Breakpoint):
 def stop(self):
  global phase
  phase=True;emit('BEFORE_INJECTED_FRONTDOOR_ACCESS');return False
class Trace(gdb.Breakpoint):
 def __init__(self,symbol,label):self.label=label;super().__init__(symbol)
 def stop(self):
  if phase:emit(self.label)
  return False
class After(gdb.Breakpoint):
 def stop(self):
  if phase:emit('AFTER_INJECTED_FRONTDOOR_ACCESS')
  return False
Mark('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261020-a-r42-wad-fixtures-v1/tests/ep_l2/test_potential_a1.cc:81')
Trace('l2_cache::ft_access','FT_ACCESS_ENTERED')
Trace('data_cache::access','DATA_CACHE_ACCESS_ENTERED')
Trace('l2_cache::ft_rollback','FT_ROLLBACK_ENTERED')
After('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261020-a-r42-wad-fixtures-v1/tests/ep_l2/test_potential_a1.cc:83')
end
run
python
emit('STOP_SIGNAL',{'signal':gdb.selected_thread().stop_signal if hasattr(gdb.selected_thread(),'stop_signal') else 'see actual GDB signal text'})
with open('OBSERVED_ROLLBACK.json','w') as stream:json.dump({'schema':'E_R42_ROLLBACK_READ_ONLY_GDB_V1','observations':observations,'inferior_function_calls':False,'inferior_state_edits':False},stream,indent=2)
end
bt 15
quit
