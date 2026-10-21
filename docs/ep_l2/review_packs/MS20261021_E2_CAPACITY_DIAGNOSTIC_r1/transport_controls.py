"""Bounded engineering validation of newly carried durable collector policy, no simulator."""
from pathlib import Path
import json,os,resource,subprocess,sys,time
from unittest.mock import patch
P=Path(__file__).resolve().parent;ROOT=P.parents[3];sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,capacity_policy as policy,durable_exit as d

def child(out):
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));limits=policy.effective_limits(c.Coordinator().snapshot());cases=[]
 for mode,code,expected in [('exit0','import os;os._exit(0)',0),('exit7','import os;print("GPGPU-Sim: *** exit detected ***",flush=True);os._exit(7)',7),('timeout','import time;time.sleep(10)',-15)]:
  directory=out/mode;directory.mkdir();bounds=dict(c.Coordinator().work_disk_policy(),maximum_result_bytes=2*2**20,memory_bytes=128*2**20,timeout_seconds=.4 if mode=='timeout' else 8,**{k:limits[k] for k in ['intake_deadline_unix','additional_results_max_bytes','old_plus_new_results_max_bytes']})
  with (directory/'raw.log').open('xb') as log:
   p=d.NativeProcess([sys.executable,'-c',code],directory,log,os.environ.copy(),bounds,dict(engineering_control=mode,full_application=False));p.release();p.wait(timeout=12);e=p.exit_evidence()
  assert e['exit_code']==expected and os.waitstatus_to_exitcode(e['wait_status'])==expected
  assert e['native_process']==p.ready['native_process'] and e['guardian_process']==p.guardian_identity
  assert (e['stop_reason'] is None) if mode!='timeout' else e['stop_reason']['kind']=='TIMEOUT'
  if mode=='exit7':assert 'exit detected' in (directory/'raw.log').read_text() and e['exit_code']!=0
  request=json.loads((directory/'NATIVE_EXECUTION_REQUEST.json').read_text());assert request['bounds']==bounds
  cases.append(dict(case=mode,status='PASS',exit_code=e['exit_code'],wait_status=e['wait_status'],request_carried_limits=json.loads(json.dumps(bounds)),receipt=dict(path=str(directory/'NATIVE_EXIT.json'),sha256=c.digest(directory/'NATIVE_EXIT.json'))))
 # Meaningful policy boundaries: approved extension works, real safety still stops.
 request=dict(bounds=bounds,directory=str(directory));safe=dict(available_memory_bytes=100*c.GIB,disk_free_bytes=20*c.GIB,share_disk_free_bytes=41*c.GIB)
 with patch.object(c,'local_resources',return_value=safe),patch.object(c,'retained_tree_bytes',return_value=0),patch('run.process_tree_rss',return_value=1),patch.object(c,'output_usage',return_value=dict(old_bytes=14*c.GIB,new_bytes=7*c.GIB,total_bytes=21*c.GIB)):
  request['bounds']['timeout_seconds']=10
  assert d.resource_stop(request,os.getpid(),time.monotonic()) is None
  cases.append(dict(case='new7_total21_with_approved10_24',status='PASS'))
  with patch.object(c,'output_usage',return_value=dict(old_bytes=14*c.GIB,new_bytes=10*c.GIB,total_bytes=24*c.GIB)):
   assert d.resource_stop(request,os.getpid(),time.monotonic())['kind']=='RESOURCE_LIMIT'
  cases.append(dict(case='exact_new10_total24_stops',status='PASS'))
  with patch.object(c,'local_resources',return_value=dict(safe,disk_free_bytes=7*c.GIB)):
   assert d.resource_stop(request,os.getpid(),time.monotonic())['kind']=='RESOURCE_LIMIT'
  cases.append(dict(case='original_workspace_floor_monitor_stops',status='PASS'))
 c.write_json(out/'CASES.json',dict(status='PASS',cases=cases,full_application_starts=0,simulator_native_tests=0))

def main():
 coord=c.Coordinator();before=coord.snapshot();assert before['actual_starts']==36 and before['controller']['state']=='STOPPED'
 out=c.OUTPUT/'E2_CAPACITY_TRANSPORT_CONTROLS_20261021_r1';assert not out.exists(),'Bounded transport controls already retained; review, never overwrite'
 lease=coord.reserve_work('E','test',1,128*2**20,16*2**20,out);c.write_json(P/'TRANSPORT_CONTROL_LEASE.json',lease);out.mkdir();proc=None;code=None
 try:
  with (out/'driver.log').open('xb') as log:proc=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--child',str(out)],stdout=log,stderr=-2)
  coord.bind_work_process(lease['lease_id'],'E',proc.pid);code=proc.wait(timeout=40)
 finally:
  if proc is not None and proc.poll() is None:proc.terminate();proc.wait(timeout=5)
  coord.release_work(lease['lease_id'],'E','Bounded non-simulator collector policy controls exit '+str(code),no_child_started=proc is None)
 assert code==0,(out/'driver.log').read_text()
 after=coord.snapshot();assert after['attempts']==before['attempts'] and after['accepted_pairs']==before['accepted_pairs'] and after['actual_starts']==36
 report=dict(status='PASS',cases=json.loads((out/'CASES.json').read_text())['cases'],full_application_starts=0,simulator_native_tests=0,actual_starts=36,remaining=10,T0=after['t0_unix'],lease_id=lease['lease_id'],source_publication=c.verify_extension_binding(c.HANDOFF/'CLIENT_CONTRACT.json'),retained_result_bytes=c.retained_tree_bytes(out),result_directory=str(out),at_unix=time.time())
 c.write_json(P/'TRANSPORT_CONTROL_RESULT.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='--child':child(Path(sys.argv[2]))
 else:main()
