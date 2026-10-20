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
    row['m_ro']=str(cache['m_ro'])
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
class InjectedFrontDoor(gdb.Breakpoint):
 def stop(self):
  try:
   cache=gdb.newest_frame().read_var('this').dereference()
   return int(cache['m_config']['m_miss_queue_size'])==0
  except Exception:return False
InjectedFrontDoor('l2_cache::access')
end
run
python
emit('ACTUAL_FRONTDOOR_ENTRY_BEFORE_CALL')
steps=[]
seen_ft=False
for i in range(90):
    try:
        frame=gdb.newest_frame();sal=frame.find_sal();name=frame.name() or ''
        row={'i':i,'function':name,'source':sal.symtab.fullname() if sal.symtab else None,'line':sal.line}
        steps.append(row);gdb.write('E_ACTUAL_STEP|'+json.dumps(row,sort_keys=True)+'\n')
        if name=='l2_cache::ft_access':seen_ft=True
        if name=='main' and sal.line>=82:break
        if '__pthread_kill' in name:break
        if name=='l2_cache::ft_access':gdb.execute('next',to_string=True)
        elif name=='l2_cache::access':gdb.execute('step',to_string=True)
        else:gdb.execute('finish',to_string=True)
    except Exception as e:
        steps.append({'error':str(e)});break
emit('AFTER_ACTUAL_FRONTDOOR_ACCESS')
with open('ACTUAL_SOURCE_STEPS.json','w') as stream:json.dump({'steps':steps,'ft_access_seen':seen_ft},stream,indent=2)
end
continue
python
emit('STOP_SIGNAL')
with open('OBSERVED_ROLLBACK.json','w') as stream:json.dump({'schema':'E_R42_ROLLBACK_READ_ONLY_GDB_STEP_V3','observations':observations,'inferior_function_calls':False,'inferior_state_edits':False},stream,indent=2)
end
bt 15
quit
