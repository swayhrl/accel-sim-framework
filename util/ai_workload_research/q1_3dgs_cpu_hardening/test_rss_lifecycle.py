import unittest,os,subprocess,sys,time,tempfile
from types import SimpleNamespace as N
from unittest.mock import patch
import psutil
from rss_lifecycle import OwnLifecycle,SessionMemory,finalize_races
from resource_monitor import collect_snapshot,enforce_snapshot,MonitorStop
from test_supervision import FakeNV,info,config,services
from supervisor import Supervisor
class SimProc:
 def __init__(self,ps,pid,birth):self.ps=ps;self.pid=pid;self.birth=birth
 def create_time(self):return self.birth
 def children(self,recursive=True):return [SimProc(self.ps,p,self.ps.birth[p]) for p in self.ps.children]
 def memory_info(self):
  action=self.ps.actions.get(self.pid)
  if action=='exit':
   self.ps.alive.remove(self.pid);raise psutil.NoSuchProcess(self.pid)
  if action=='denied':raise psutil.AccessDenied(self.pid)
  if action=='reuse':
   self.ps.birth[self.pid]+=1;raise psutil.NoSuchProcess(self.pid)
  if action=='alive_missing':raise psutil.NoSuchProcess(self.pid)
  return N(rss=self.ps.rss)
 def is_running(self):return self.pid in self.ps.alive
 def status(self):return 'running'
class SimPS:
 NoSuchProcess=psutil.NoSuchProcess
 def __init__(self):
  self.alive={10,20,30};self.birth={10:1.,20:2.,30:3.};self.children=[20,30];self.actions={30:'exit'};self.rss=100
 def Process(self,p):
  if p not in self.alive:raise psutil.NoSuchProcess(p)
  return SimProc(self,p,self.birth[p])
 def pid_exists(self,p):return p in self.alive
class RaceTests(unittest.TestCase):
 def snap(self,ps=None,nv=None):
  ps=ps or SimPS();life=OwnLifecycle(ps,10);life.bind_worker(20)
  row=collect_snapshot(nv or FakeNV([info(20)]),'h',ps,10,{10,20},'WORKER',1,1,1,1,lifecycle=life)
  row['unqualified_external_gpu_pids']=row['external_gpu_pids']
  return row,life,ps
 def test_memory_read_NoSuchProcess_is_censored_not_zero(self):
  row,_,_=self.snap();self.assertFalse(row['monitor_gaps']);self.assertEqual(row['own_tree_RSS_bytes'],200)
  x=row['rss_censored_observations'][0];self.assertIsNone(x['rss_bytes'])
  finalize_races(row,True,True);self.assertEqual(x['classification'],'OWN_EXITED_CHILD_RSS_RACE')
 def test_natural_exit_after_valid_real_enumeration(self):
  child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(0.1)'])
  p=psutil.Process(child.pid);birth=p.create_time();child.wait()
  life=OwnLifecycle(psutil,os.getpid());life.bind_worker(os.getpid())
  realroot=psutil.Process(os.getpid())
  wrapper=N(create_time=realroot.create_time,children=lambda recursive=True:[p])
  original=psutil.Process
  def factory(pid):return wrapper if pid==os.getpid() else original(pid)
  # Use a proxy only for enumeration; root health uses real identity/status.
  class PS:
   NoSuchProcess=psutil.NoSuchProcess
   pid_exists=staticmethod(psutil.pid_exists)
   def Process(self,pid):
    if pid==os.getpid():
     rp=original(pid);rp.children=lambda recursive=True:[p];return rp
    return original(pid)
  life.ps=PS()
  live,rss,gaps,censored,observed=life.rss('WORKER')
  self.assertFalse(gaps);self.assertEqual(censored[0]['creation_time'],birth);self.assertIsNone(censored[0]['rss_bytes'])
 def test_AccessDenied_still_fatal(self):
  ps=SimPS();ps.actions[30]='denied';row,_,_=self.snap(ps);self.assertTrue(row['monitor_gaps'])
  with self.assertRaises(MonitorStop):enforce_snapshot(row,config('v7_denied'))
 def test_still_alive_NoSuchProcess_not_censored(self):
  ps=SimPS();ps.actions[30]='alive_missing';row,_,_=self.snap(ps)
  self.assertTrue(row['monitor_gaps']);self.assertFalse(row['rss_censored_observations'])
 def test_pid_reuse_is_fatal(self):
  ps=SimPS();ps.actions[30]='reuse';row,_,_=self.snap(ps)
  self.assertTrue(row['monitor_gaps']);self.assertFalse(row['rss_censored_observations'])
 def test_root_exit_fatal(self):
  ps=SimPS();ps.actions[10]='exit';row,_,_=self.snap(ps);self.assertTrue(row['monitor_gaps'])
 def test_worker_exit_fatal(self):
  ps=SimPS();ps.actions[20]='exit';row,_,_=self.snap(ps);self.assertTrue(row['monitor_gaps'])
 def test_unknown_external_remains_fatal(self):
  ps=SimPS();ps.alive.add(40);ps.birth[40]=4.
  row,_,_=self.snap(ps,FakeNV([info(20),info(40)]))
  with self.assertRaises(MonitorStop):enforce_snapshot(row,config('v7_unknown'))
  with self.assertRaises(RuntimeError):finalize_races(row,True,True)
 def test_GPU_identity_change_fatal(self):
  ps=SimPS();ps.actions={};row,life,ps=self.snap(ps);ps.birth[20]+=1
  row=collect_snapshot(FakeNV([info(20)]),'h',ps,10,{10,20},'WORKER',1,1,1,1,lifecycle=life)
  self.assertTrue(any('IDENTITY' in g or 'REUSE' in g for g in row['monitor_gaps']))
 def test_valid_race_plus_true_gap_never_finalizes(self):
  row,_,_=self.snap();row['monitor_gaps'].append('REAL_OTHER_GAP')
  with self.assertRaises(RuntimeError):finalize_races(row,True,True)
 def test_gate_or_runtime_absence_never_finalizes(self):
  for gate,runtime in [(False,True),(True,False)]:
   row,_,_=self.snap()
   with self.assertRaises(RuntimeError):finalize_races(row,gate,runtime)
 def test_resource_caps_still_apply_with_race(self):
  row,_,_=self.snap();cfg=config('v7_caps')
  for key,limit in [('own_tree_RSS_bytes','rss_bytes_max'),('own_NVML_bytes','own_vram_bytes_max'),('own_new_disk_bytes','disk_bytes_max')]:
   v=dict(row);v[key]=cfg[limit]+1
   with self.assertRaises(MonitorStop):enforce_snapshot(v,cfg)
 def test_snapshot_late_activity_failure_does_not_finalize_race(self):
  row,_,_=self.snap();s=services();x=Supervisor(config('v7_late'),s);x.held=0;x.lifecycle=N();x.shared=N(check=lambda r:r)
  with patch('supervisor.collect_snapshot',return_value=row),patch('supervisor.apply_desktop_policy',side_effect=lambda r,c,reader:r),patch('supervisor.runtime_activity',side_effect=MonitorStop('GPU_RESOURCE_DEFERRED','real activity')):
   with self.assertRaises(MonitorStop):x.snapshot('WORKER')
  self.assertEqual(row['rss_censored_observations'][0]['classification'],'PENDING_OWN_EXITED_CHILD_RSS_RACE')
 def test_shared_reservation_cleanup_on_worker_error(self):
  s=services(exit_code=2);cfg=config('v7_shared_cleanup');x=Supervisor(cfg,s);released=[]
  x.shared=N(reserve=lambda:{'mock':True},check=lambda row:row,release=lambda:released.append(True) or {'released':True})
  r=x.run();self.assertTrue(r['lock_released']);self.assertTrue(r['own_GPU_contexts_cleared']);self.assertEqual(released,[True]);self.assertEqual(r['status'],'NUMERIC_OR_RUNTIME_NO_GO')
 def test_actual_session_peak_is_read_only_observable(self):
  c=SessionMemory(os.getpid());v=c.read(None)
  self.assertGreaterEqual(v['kernel_charged_peak_bytes'],v['current_bytes']);self.assertFalse(os.access(c.path,os.W_OK))
 def test_session_peak_cap_safely_stops(self):
  s=services();x=Supervisor(config('v7_session_cap'),s);x.session_memory=N(read=lambda worker:{'kernel_charged_peak_bytes':16*1024**3+1})
  r=x.run();self.assertEqual(r['status'],'INCONCLUSIVE');self.assertTrue(r['lock_released']);self.assertEqual(s.counts['spawn'],0)
if __name__=='__main__':unittest.main()
