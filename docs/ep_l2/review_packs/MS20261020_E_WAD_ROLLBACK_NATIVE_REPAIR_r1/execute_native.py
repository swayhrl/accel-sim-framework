"""E independent finite-test compilation and replay; never builds/publishes a producer or runs applications."""
import os,sys,json,time,resource,importlib.util
from pathlib import Path
ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c
from run import process_tree_rss
PACK=Path(__file__).resolve().parent

def main():
 spec=json.loads((PACK/'SPEC.json').read_text());out=Path(spec['output']);assert not out.exists(),'Preserve old test attempt; do not replay'
 coord=c.Coordinator();c.tooling_binding();before=coord.snapshot();assert before['actual_starts']==7
 for path,sha in spec['pins'].items():assert c.digest(path)==sha,'preimage changed: '+path
 snap={path:(Path(path).stat().st_ino,Path(path).stat().st_size,Path(path).stat().st_mtime_ns) for path in spec['pins']}
 sm=importlib.util.spec_from_file_location('e_retained_owned_supervisor',spec['supervisor']);guard=importlib.util.module_from_spec(sm);sm.loader.exec_module(guard)
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));out.mkdir();(out/'tmp').mkdir()
 report={'schema':'E_INDEPENDENT_WAD_TEST_REPAIR_NATIVE_RECEIPT_V1','status':'PREPARING','campaign_id':c.CAMPAIGN,'scope':spec['scope'],'runtime_Core':spec['runtime_Core'],'fixture_Core':spec['fixture_Core'],'fixture_source_sha256':c.digest(PACK/'test_potential_a1_injected_read.cc'),'production_archive':spec['production_archive'],'production_archive_sha256':spec['production_archive_sha256'],'candidate_main':spec['candidate_main'],'candidate_main_sha256':spec['candidate_main_sha256'],'commands':[],'tests':[],'actual_full_application_starts':0,'actual_starts_before':before['actual_starts'],'producer_release_or_application_qualification':False,'pins':spec['pins']}
 save=lambda:c.write_json(out/'RECEIPT.json',report)
 lease=None;started=False;deadline=time.monotonic()+spec['maximum_seconds']
 try:
  alloc=coord.reserve_work('E','test',spec['CPU'],spec['memory_bytes'],spec['growth_bytes'],out)
  lease=alloc['lease_id'];report.update(lease_id=lease,allocation=alloc,disk_floor_bytes=alloc['disk_floor_bytes']+alloc['monitor_reserve_bytes'],memory_floor_bytes=64*c.GIB,E_runtime_source=c.verify_extension_binding(c.HANDOFF/'CLIENT_CONTRACT.json'))
  env=dict(os.environ,TMPDIR=str(out/'tmp'),TMP=str(out/'tmp'),TEMP=str(out/'tmp'),XDG_CACHE_HOME=str(out/'tmp/cache'),PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(out/'tmp/pycache'),CUDA_INSTALL_PATH='/usr/local/cuda-11.8',CCACHE_DISABLE='1',CUDA_CACHE_DISABLE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
  def resources():
   live=c.local_resources();written=c.retained_tree_bytes(out);rss=process_tree_rss(report['commands'][-1]['process']['pid']) if report['commands'] and report['commands'][-1].get('process') else 0
   reasons=[]
   if time.monotonic()>deadline:reasons.append('BOUNDED_900S_DEADLINE')
   if live['disk_free_bytes']<=report['disk_floor_bytes']:reasons.append('WORKSPACE5G_PLUS_MONITOR')
   if live['share_disk_free_bytes']<40*c.GIB:reasons.append('SHARE40')
   if live['available_memory_bytes']<64*c.GIB:reasons.append('RAM64')
   if rss>spec['memory_bytes']:reasons.append('OWN_RAM8')
   if written>=spec['growth_bytes']:reasons.append('OWN_TEST_OUTPUT512M')
   for path,st in snap.items():
    cur=Path(path).stat()
    if (cur.st_ino,cur.st_size,cur.st_mtime_ns)!=st:reasons.append('RETAINED_PIN_CHANGED '+path)
   report['peak_output_bytes']=max(written,report.get('peak_output_bytes',0));report['peak_tree_RSS_bytes']=max(rss,report.get('peak_tree_RSS_bytes',0))
   if reasons:
    c.write_json(out/'RESOURCE_LIMIT.json',{'status':'RESOURCE_LIMIT_OR_IDENTITY_HOLD','reasons':reasons,'resources':live,'own_output_bytes':written,'own_RSS_bytes':rss});raise RuntimeError(str(reasons))
   return live
  def bind(pid):
   nonlocal started
   started=True;return coord.bind_work_process(lease,'E',pid)
  def run(command,name,timeout=120):
   resources();row=guard.run_owned(command,name,out,env,report,save,resources,bind,timeout);resources();return row
  report['status']='COMPILING_ONLY_E_FINITE_FIXTURE';save();run(spec['compile_command'],'independent_fixture_compile');run(spec['link_command'],'independent_fixture_link')
  elf=spec['test_executables']['ep_l2_potential_a1'];report['independent_fixture_ELF_sha256']=c.digest(elf)
  report['status']='REAL_INDEPENDENT_NATIVE_CHECKS';save()
  for case in spec['cases']:
   command=[spec['test_executables'][case['target']]]+case['arguments'];receipt=out/(case['id']+'.json')
   run([sys.executable,'-B',spec['checker'],'--case-json',json.dumps(case),'--receipt',str(receipt),'--']+command,case['id'],120)
   result=json.loads(receipt.read_text());assert result['actual_exit']==case['expected_exit'] and result['expectation_verified']
   result['receipt_path']=str(receipt);result['receipt_sha256']=c.digest(receipt);report['tests'].append(result);save()
  for path,sha in spec['pins'].items():assert c.digest(path)==sha,'retained identity changed: '+path
  report.update(status='INDEPENDENT_AFFECTED_NATIVE_PASS_PENDING_FORMAL_PRODUCER',retained_assets_unchanged=True)
 except BaseException as error:
  report.update(status='FAILED_INDEPENDENT_NATIVE_OR_TEST_REPAIR',error=repr(error));raise
 finally:
  if lease:coord.release_work(lease,'E',report['status'],no_child_started=not started);report['lease_released']=True
  report.update(actual_starts_after=coord.snapshot()['actual_starts'],finished_unix=time.time());assert report['actual_starts_after']==7;save()
if __name__=='__main__':main()
