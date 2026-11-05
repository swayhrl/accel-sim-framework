"""Serial V10 controller; no counter task without independently audited pilot."""
from pathlib import Path
import subprocess,time,json,csv
from persistence import save_json
from resource_monitor import MonitorStop
from v9_runtime import bind_actual,own_gpu,alive
from terminal_drain import terminal_phase
PAIR=['dram__bytes_read.sum','gpu__time_duration.sum']
def audit_csv(path,log=None):
 with path.open() as f:rows=list(csv.reader(f))
 starts=[i for i,r in enumerate(rows) if 'Kernel Name' in r and 'profiler__replayer_passes' in r]
 if not starts:raise ValueError('Missingexplicitreplayauditcolumns')
 i=starts[0];header,units,data=rows[i:i+3]
 def num(key):
  v=data[header.index(key)];return float(v.replace(',',''))
 passes=num('profiler__replayer_passes')
 backup=num('profiler__replayer_bytes_mem_backed_up.sum') if 'profiler__replayer_bytes_mem_backed_up.sum' in header else None
 log_one=log is not None and '100% - 1 pass' in log and 'Backing up' not in log
 justified=backup==0 if backup is not None else log_one
 return dict(passes=passes,backup_bytes=backup,safe_single_pass=passes==1 and justified,backup_counter_emitted=backup is not None,backup_interpretation='DIRECT_COUNTER' if backup is not None else 'NOT_EMITTED:singlepass_log+installedguide_no_save_restore;notzero-filled',metrics={k:dict(unit=units[j],value=data[j]) for j,k in enumerate(header) if k.startswith(('dram__','gpu__','profiler__'))},kernel=data[header.index('Kernel Name')],grid=data[header.index('Grid Size')],block=data[header.index('Block Size')])
def export(x,task):
 out=Path(x.cfg['out']);state=x.s.v9state;csvpath=out/'raw'/(task+'_BASE.csv')
 report=state['context']/'metrics.ncu-rep'
 if not report.exists():return dict(safe_single_pass=False,error='No completed counter report')
 with csvpath.open('w') as f,(out/'raw'/(task+'_EXPORT_LOG.txt')).open('w') as err:
  p=subprocess.Popen([x.cfg['ncu'],'--import',str(report),'--page','raw','--csv','--print-units','base'],stdout=f,stderr=err,start_new_session=True)
  start=time.monotonic()
  while p.poll() is None:
   x.snapshot('COUNTER_EXPORT_CPU')
   if time.monotonic()-start>25:p.terminate();p.wait(timeout=3);raise RuntimeError('CPUexporttimeout')
   x.s.sleep(.2)
  if p.returncode:return dict(safe_single_pass=False,error='Counterexportfailed')
 try:return audit_csv(csvpath,log=(state['context']/'worker.log').read_text(errors='replace'))
 except Exception as e:return dict(safe_single_pass=False,error=type(e).__name__+':'+str(e))
def execute_v10(x):
 cfg=x.cfg;s=x.s
 if cfg.get('v11_dispatch'):
  from v11_dispatch import execute_v11
  return execute_v11(x)
 approved=cfg.get('preapproved_metric_plan');profile_aborted=False
 for task in cfg.get('tasks_exact',['PILOT_PAIR','PILOT_DRAM','NCU_B1','NCU_B2','MICRO','NUMERIC']):
  if task=='PILOT_DRAM' and approved is not None:continue
  if task.startswith('NCU') and (approved is None or profile_aborted):
   x.r.setdefault('optional_skips',[]).append(dict(task=task,reason='No audited singlepass scheme or preemptive profile abort'));continue
  if s.mono()-x.held>cfg['held_seconds_max']-180:
   x.r.setdefault('optional_skips',[]).append(dict(task=task,reason='GPUbudgetreserve'));break
  s.v9state['metric_plan']=dict(selected=PAIR if task=='PILOT_PAIR' else ['dram__bytes_read.sum'] if task=='PILOT_DRAM' else approved or PAIR)
  s.v9state['next_task']=task;x.child=s.spawn();x.owned.add(x.child.pid);x.lifecycle.bind_worker(x.child.pid)
  x.r['worker_launches']+=1;x.r['children'].append(dict(task=task,launcher_pid=x.child.pid,start_epoch=s.wall(),launch=s.v9state['launch']))
  start=s.mono();bound=False;aborted=False
  while x.child.poll() is None:
   state=s.v9state
   if not bound:bound=bind_actual(x)
   finish=state['context']/'WORKER_FINISHED.json';finished=False
   if finish.exists():
    v=json.loads(finish.read_text());finished=v.get('nonce')==state['nonce'] and v.get('task')==task
   if finished and bound:
    if 'finished_seen' not in state:state['finished_seen']=s.mono()
    contexts=own_gpu(x)
    drain_phase=terminal_phase(v,x.r['children'][-1]['actual_worker'],contexts,s.mono(),state['finished_seen'])
    if not contexts:x.lifecycle.bind_worker(x.child.pid if alive(s.ps,x.child.pid) else s.pid)
    row=x.snapshot(drain_phase)
   else:row=x.snapshot('WORKER' if bound else 'WORKER_BOOTSTRAP')
   if not bound and row['own_NVML_bytes']:raise MonitorStop('GPU_RESOURCE_DEFERRED','CUDA before actual identity binding')
   if not bound and s.mono()-start>90:raise MonitorStop('INCONCLUSIVE','Worker bootstrap timeout')
   charged=row.get('session_memory',{}).get('current_bytes',0)
   if (task.startswith('NCU') or task.startswith('PILOT')) and charged>10*1024**3:
    s.terminate(x.child);aborted=True;profile_aborted=True;x.r.setdefault('preemptive_profile_stops',[]).append(dict(task=task,charged_bytes=charged,soft_subtask_guard_bytes=10*1024**3,contract_limit_unchanged=16*1024**3));break
   s.sleep(.1)
  x.r['children'][-1].update(exit_code=x.child.poll(),finish_epoch=s.wall(),preemptive_profile_stop=aborted)
  if own_gpu(x):raise MonitorStop('GPU_RESOURCE_DEFERRED','Own context not drained')
  x.lifecycle.bind_worker(s.pid);x.snapshot('WORKER_EXIT');result=s.worker_result()
  x.r['children'][-1].update(model_initializations=result.get('model_initializations',0),result_status=result.get('status'),error=result.get('error'))
  if result.get('validity_stop'):raise MonitorStop('NUMERIC_OR_RUNTIME_NO_GO','Actual model/input/backend validity failure')
  if x.child.returncode!=0 or result.get('status')!='V9_WORKER_COMPLETE':
   x.r.setdefault('optional_failures',[]).append(dict(task=task,result_status=result.get('status'),error=result.get('error'),preemptive=aborted));x.save();continue
  if task.startswith('NCU') or task.startswith('PILOT'):
   audit=export(x,task);x.r['children'][-1]['counter_audit']=audit
   save_json(Path(cfg['out'])/'raw'/(task+'_AUDIT.json'),audit)
   if task.startswith('PILOT') and audit.get('safe_single_pass'):approved=list(s.v9state['metric_plan']['selected'])
   if task.startswith('NCU') and not audit.get('safe_single_pass'):profile_aborted=True
  x.r['GPU_model_initializations']=sum(v.get('model_initializations',0) for v in x.r['children']);x.save()
 x.r['status']='V10_STUDY_COMPLETE'
