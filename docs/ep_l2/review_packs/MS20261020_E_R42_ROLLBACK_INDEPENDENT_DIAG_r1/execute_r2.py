"""One bounded E native diagnostic using retained A ELF; never compiles or starts an application."""
import sys,os,json,time,hashlib,resource,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
# Locate the execution checkout without relying on symlink resolution or a second registry.
ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c
from run import process_tree_rss
PACK=Path(__file__).parent
OUT=c.OUTPUT/'E_R42_ROLLBACK_INDEPENDENT_DIAG_r2'
sha=c.digest

def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
 assert not OUT.exists(),'retain old diagnostic; do not replay'
 spec=json.loads((PACK/'SPEC_r2.json').read_text())
 for path,digest in spec['pins'].items():assert sha(path)==digest,path
 c.tooling_binding();coord=c.Coordinator();before=coord.snapshot();assert before['actual_starts']==7
 guard=load_module('retained_owned_guard',Path(spec['supervisor']))
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 OUT.mkdir();(OUT/'tmp').mkdir()
 report={'schema':'E_R42_ROLLBACK_NATIVE_DIAGNOSTIC_RECEIPT_V1','status':'PREPARING','campaign_id':c.CAMPAIGN,'pins':spec['pins'],'actual_full_applications_started':0,'actual_starts_before':before['actual_starts'],'commands':[],'native_performance_or_application_acceptance':False}
 save=lambda:c.write_json(OUT/'RECEIPT.json',report)
 lease=None;started=False
 try:
  allocation=coord.reserve_work('E','test',1,8*c.GIB,64*2**20,OUT)
  lease=allocation['lease_id'];report.update(lease_id=lease,allocation=allocation,disk_floor_bytes=allocation['disk_floor_bytes']+allocation['monitor_reserve_bytes'],memory_floor_bytes=64*c.GIB)
  env=dict(os.environ,TMPDIR=str(OUT/'tmp'),TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'),XDG_CACHE_HOME=str(OUT/'tmp'),PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
  for name in ['PYTHONHOME','PYTHONPATH']:env.pop(name,None)
  def resources():
   live=c.local_resources();rss=process_tree_rss(report['commands'][-1]['process']['pid']) if report.get('commands') and report['commands'][-1].get('process') else 0
   written=c.retained_tree_bytes(OUT)
   reasons=[]
   if live['disk_free_bytes']<=report['disk_floor_bytes']:reasons.append('WORKSPACE_MONITOR_MARGIN')
   if live['share_disk_free_bytes']<40*c.GIB:reasons.append('SHARE40')
   if live['available_memory_bytes']<64*c.GIB:reasons.append('RAM64')
   if rss>8*c.GIB:reasons.append('OWN_RAM8')
   if written>=64*2**20:reasons.append('OWN_OUTPUT64M')
   if reasons:
    c.write_json(OUT/'RESOURCE_LIMIT.json',{'status':'RESOURCE_LIMIT','reasons':reasons,'resources':live,'own_rss':rss,'own_written':written});raise RuntimeError('RESOURCE_LIMIT '+str(reasons))
   return live
  def bind(pid):
   nonlocal started
   started=True;return coord.bind_work_process(lease,'E',pid)
  command=['/usr/bin/gdb','-q','-nx','-batch','-x',str(PACK/'capture_rollback_r2.gdb'),'--args']+spec['native_command']
  guard.run_owned(command,'actual_gdb',OUT,env,report,save,resources,bind,120)
  text=(OUT/'actual_gdb.log').read_text(errors='replace')
  report['actual_SIGABRT_captured']='Program received signal SIGABRT' in text
  report['status']='CAPTURED_NATIVE_FAILURE_NOT_PASS' if report['actual_SIGABRT_captured'] else 'NO_ABORT_CAPTURE_REVIEW_REQUIRED'
 except BaseException as e:report.update(status='STOPPED_OR_FAILED_DIAGNOSTIC',error=repr(e));raise
 finally:
  if lease:coord.release_work(lease,'E',report['status'],no_child_started=not started);report['lease_released']=True
  report['actual_starts_after']=coord.snapshot()['actual_starts'];assert report['actual_starts_after']==7
  report['finished_unix']=time.time();save()
if __name__=='__main__':main()
