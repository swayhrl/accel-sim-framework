"""Pure CPU GPU-PID classifier. Never treats an unknown or reused PID as owned."""
def classify_snapshot(rows,known,proc_before,proc_after,child_terminal):
 out=[];reason=None
 for pid,memory in rows:
  birth=known.get(pid)
  a=proc_before.get(pid);b=proc_after.get(pid)
  if birth is None:
   state='FOREIGN_OR_UNKNOWN_PID';reason='EXTERNAL_GPU_TASK_STOP'
  elif any(x is not None and x['start_ticks']!=birth['start_ticks'] for x in [a,b]):
   state='PID_REUSED_OR_IDENTITY_CHANGED';reason='GPU_EXCLUSIVITY_UNRESOLVED'
  elif b is not None and b['state']!='Z':
   state='OWN_LIVE_PID'
  elif child_terminal:
   state='OWN_EXIT_NVML_LAG_PENDING_EMPTY_DRAIN'
  elif a is not None:
   state='OWN_CAPTURED_BEFORE_QUERY_EXIT_PENDING'
  else:
   state='UNPROVEN_KNOWN_PID_WITHOUT_PROCESS_OR_EXIT';reason='GPU_EXCLUSIVITY_UNRESOLVED'
  out.append({'pid':pid,'memory_MiB':memory,'classification':state,'known_identity':birth,'proc_before':a,'proc_after':b})
 return {'classification':out,'stop_reason':reason}


def parse_nvml_csv(raw):
 rows=[]
 for line in raw.splitlines():
  if not line.strip():continue
  fields=line.split(',')
  if len(fields)!=2:raise ValueError('NVML_FIELD_COUNT')
  pid=int(fields[0].strip());memory=int(fields[1].strip())
  if pid<=0 or memory<0:raise ValueError('NVML_INVALID_VALUE')
  rows.append((pid,memory))
 return rows
