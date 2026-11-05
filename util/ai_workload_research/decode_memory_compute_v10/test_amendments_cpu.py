"""Replay all13 dedicated CPU amendment cases; no CUDA/NVML imports."""
import sys,tempfile,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'native_b2'))
from v10_dispatch import audit_csv
from terminal_drain import terminal_phase
from resource_monitor import MonitorStop
def main():
 count=0
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/'x'
  def write(passes,backup=None):
   h=['Kernel Name','Grid Size','Block Size','profiler__replayer_passes']
   v=['gemv','1','1',str(passes)]
   if backup is not None:h.append('profiler__replayer_bytes_mem_backed_up.sum');v.append(str(backup))
   with p.open('w') as f:
    w=csv.writer(f);w.writerow(h);w.writerow(['']*len(h));w.writerow(v)
  write(1);assert not audit_csv(p)['safe_single_pass'];count+=1
  assert audit_csv(p,'100% - 1 pass')['safe_single_pass'];count+=1
  assert audit_csv(p,'100% - 1 pass')['backup_bytes'] is None;count+=1
  write(2);assert not audit_csv(p,'100% - 1 pass')['safe_single_pass'];count+=1
 b=dict(task='NCU_B2',nonce='n',supervisor_pid=1,identity={'pid':2,'start_ticks':'x'},worker_sha256='sha')
 m=dict(b,status='V9_WORKER_COMPLETE')
 assert terminal_phase(m,b,[2],10,9)=='FINISHED_CONTEXT_DRAIN';count+=1
 assert terminal_phase(m,b,[],10,9)=='PROFILER_CPU_DRAIN';count+=1
 for key in b:
  bad=dict(m);bad[key]='wrong'
  try:terminal_phase(bad,b,[2],10,9);raise AssertionError('notrejected')
  except MonitorStop:pass
  count+=1
 try:terminal_phase(m,b,[2],20,9);raise AssertionError('notrejected')
 except MonitorStop:pass
 count+=1
 try:terminal_phase(dict(m,status='V9_RUNTIME_ERROR'),b,[2],10,9);raise AssertionError('notrejected')
 except MonitorStop:pass
 count+=1;assert count==13;print('PASS13CPUAMENDMENTCASES;noCUDA/NVMLinitialization')
if __name__=='__main__':main()
