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
    payload=cache['m_ep_l2_payload'];row['payload_cycle']=int(payload['m_cycle']);row['bank_services']=[int(payload['m_bank_services'][b]) for b in range(4)]
    row['landing_id']=int(p['landing_id']);row['request_uid']=int(p['request'].dereference()['m_request_uid'])
    row['arbiter']={}
    for group in ['m_pending','m_granted']:
     row['arbiter'][group]=[]
     for bank in range(4):
      vec=payload[group][bank]['_M_impl'];start=vec['_M_start'];count=int(vec['_M_finish']-start)
      if count<0 or count>8:raise RuntimeError('unexpected arbiter vector length')
      ops=[]
      for i in range(count):
       op=start[i];ops.append({field:str(op[field]) for field in ['id','write','client','token','generation','sequence']})
      row['arbiter'][group].append(ops)
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
emit('ACTUAL_FRONTDOOR_ENTRY_ARBITER')
gdb.execute('finish',to_string=True)
emit('ACTUAL_FRONTDOOR_RETURN_ARBITER')
end
continue
python
emit('STOP_SIGNAL')
with open('OBSERVED_ROLLBACK.json','w') as stream:json.dump({'schema':'E_R42_ROLLBACK_READ_ONLY_ARBITER_V4','observations':observations,'inferior_function_calls':False,'inferior_state_edits':False},stream,indent=2)
end
bt 15
quit
