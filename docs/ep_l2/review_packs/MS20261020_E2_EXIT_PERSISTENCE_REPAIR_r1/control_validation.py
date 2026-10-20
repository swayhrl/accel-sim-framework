"""Finite low-resource process-lifecycle checks under original E test lease."""
from pathlib import Path
import sys,os,json,time,signal,subprocess
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'));import coordinator as c

def wait_file(p,timeout=6):
 until=time.monotonic()+timeout
 while not p.exists():
  if time.monotonic()>until:raise TimeoutError(str(p))
  time.sleep(.01)
 return json.loads(p.read_text())
def run_all(out):
 cases=[]
 for mode,expected in [('exit0',0),('exit7',7),('abort',-6),('native_sigterm',-15),('timeout',-15),('parent_sigterm',-15),('parent_sigkill',-15),('collector_sigkill',None)]:
  directory=out/mode
  with (out/(mode+'_parent.log')).open('xb') as log:parent=subprocess.Popen([sys.executable,'-B',str(P/'control_parent.py'),str(directory),mode],stdout=log,stderr=-2)
  ready=wait_file(directory/'PARENT_CONTROL_READY.json')
  if mode=='native_sigterm':os.kill(ready['native']['pid'],signal.SIGTERM)
  if mode=='parent_sigterm':os.kill(parent.pid,signal.SIGTERM)
  if mode=='parent_sigkill':os.kill(parent.pid,signal.SIGKILL)
  if mode=='collector_sigkill':os.kill(ready['guardian']['pid'],signal.SIGKILL)
  parent.wait(timeout=10)
  if mode=='collector_sigkill':
   result=wait_file(directory/'PARENT_CONTROL_RESULT.json');assert result['status']=='INCOMPLETE' and result['success_inferred'] is False;assert not (directory/'NATIVE_EXIT.json').exists()
   cases.append(dict(case=mode,status='PASS',missing_native_wait_status='INCOMPLETE_NEVER_PASS',parent_returncode=parent.returncode));continue
  exit=wait_file(directory/'NATIVE_EXIT.json');assert exit['exit_code']==expected and exit['native_process']==ready['native'] and exit['guardian_process']==ready['guardian'] and exit['native_ppid']==ready['guardian']['pid'];assert exit['exit_code']==os.waitstatus_to_exitcode(exit['wait_status'])
  if mode=='parent_sigkill':assert parent.returncode==-9 and exit['stop_reason']['kind']=='SUPERVISION_INCOMPLETE'
  else:
   result=wait_file(directory/'PARENT_CONTROL_RESULT.json');assert result['wrong_binding_rejected']
  if mode=='timeout':assert exit['stop_reason']['kind']=='TIMEOUT'
  if mode=='exit7':assert 'exit detected' in (directory/'raw.log').read_text() and exit['exit_code']==7
  try:assert c.process_identity(ready['native']['pid'])!=ready['native']
  except FileNotFoundError:pass
  cases.append(dict(case=mode,status='PASS',exit_code=exit['exit_code'],wait_status=exit['wait_status'],native_process=exit['native_process'],guardian_process=exit['guardian_process'],parent_returncode=parent.returncode,stop_reason=exit['stop_reason'],durable_exit=dict(path=str(directory/'NATIVE_EXIT.json'),sha256=c.digest(directory/'NATIVE_EXIT.json'))))
 return cases

def main():
 coord=c.Coordinator();before=coord.snapshot();assert before['actual_starts']==12 and before['controller']['state']=='STOPPED'
 out=c.OUTPUT/'E2_EXIT_CONTROL_20261020_r1';lease=coord.reserve_work('E','test',1,128*2**20,16*2**20,out);c.write_json(P/'CONTROL_TEST_LEASE.json',lease)
 # Test driver is a real owned work child; original E lease API tracks it.
 out.mkdir();status='FAILED';detail='control validation interrupted'
 try:
  with (out/'driver.log').open('xb') as log:child=subprocess.Popen([sys.executable,'-B',str(P/'control_validation.py'),'--child',str(out)],stdout=log,stderr=-2)
  coord.bind_work_process(lease['lease_id'],'E',child.pid);code=child.wait(timeout=50);assert code==0,(out/'driver.log').read_text()
  cases=json.loads((out/'CASES.json').read_text());assert len(cases)==8 and all(x['status']=='PASS' for x in cases);status='PASS';detail='8 bounded non-application exit lifecycle cases passed; no complete application or production test replay'
 finally:coord.release_work(lease['lease_id'],'E',detail)
 after=coord.snapshot();assert after['actual_starts']==before['actual_starts']==12 and after['remaining_start_capacity']==28 and after['t0_unix']==before['t0_unix'];assert before['accepted_pairs']==after['accepted_pairs']
 report=dict(schema='E2_DURABLE_NATIVE_EXIT_CONTROL_VALIDATION_V1',status=status,at_unix=time.time(),cases=cases,passed=8,full_application_starts=0,native_scientific_tests_replayed=0,actual_starts=12,remaining=28,lease_id=lease['lease_id'],cpu_units=1,memory_bytes=128*2**20,max_output_growth_bytes=16*2**20,retained_control_bytes=c.retained_tree_bytes(out),collector_guard_code_sha256=c.digest(ROOT/'util/ep_l2/mechanism_e/durable_exit.py'),native_input_protocol_changed=False,source_binary_qualification_changed=False)
 c.write_json(P/'CONTROL_VALIDATION.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='--child':
  c.write_json(Path(sys.argv[2])/'CASES.json',run_all(Path(sys.argv[2])))
 else:main()
