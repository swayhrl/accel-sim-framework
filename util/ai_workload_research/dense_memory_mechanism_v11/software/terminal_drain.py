"""Terminal marker proves completion, never grants an unknown GPU process identity."""
from resource_monitor import MonitorStop
def terminal_phase(marker,binding,own_gpu,now,first_seen):
 for k in ['task','nonce','supervisor_pid','identity','worker_sha256']:
  if marker.get(k)!=binding.get(k):raise MonitorStop('GPU_RESOURCE_DEFERRED','Finished marker identity mismatch:'+k)
 if marker.get('status') not in ['V9_WORKER_COMPLETE','V9_OPTIONAL_UNAVAILABLE']:
  raise MonitorStop('NUMERIC_OR_RUNTIME_NO_GO','Worker finished with runtime failure')
 if own_gpu and now-first_seen>6:
  raise MonitorStop('GPU_RESOURCE_DEFERRED','Finished own CUDA context failed bounded drain')
 return 'FINISHED_CONTEXT_DRAIN' if own_gpu else 'PROFILER_CPU_DRAIN'
