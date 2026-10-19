"""Bounded offline full-epoch oracle using C's immutable producer, not a simulator.

The relocated C CLI retains a historical source-binding path. This wrapper binds
its actual new Git path/bytes before calling the unchanged public build API.
Only this operation's process group/output is owned here. Production resource
floors and E launch/qualification authority are untouched.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import unittest

REPO = Path(__file__).resolve().parents[3]
DOC = REPO/'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d'
SHARED = Path('/workspace/ep_l2_ft20261016_shared/mechanism_study_20261019_v1/lane_d')
C_COMMIT = 'aabc7d80f576ee7e412a60c5af0cc4d32278fbea'
C_PATH = 'util/ep_l2/mechanism_study_c/ro_oracle.py'
OUTPUT_ROOT = Path('/workspace/ep_l2_ms20261019_e_results/D_OFFLINE_INPUT_ANALYSIS')
MEMORY = 256*2**20
OUTPUT_CAP = 256*2**20
TIMEOUT = 1800

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(path, obj):
    tmp=path.with_suffix('.tmp'); tmp.write_text(json.dumps(obj,indent=2)+'\n'); tmp.replace(path)
def frozen(path): return subprocess.check_output(['git','show',C_COMMIT+':'+path],cwd=REPO)
def identity(pid):
    stat=(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()
    return {'pid':pid,'start_ticks':int(stat[19]),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}

def worker(out, registration):
    os.nice(10)
    allowed=os.sched_getaffinity(0); os.sched_setaffinity(0,{max(allowed)})
    resource.setrlimit(resource.RLIMIT_AS,(MEMORY,MEMORY))
    resource.setrlimit(resource.RLIMIT_FSIZE,(OUTPUT_CAP,OUTPUT_CAP))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    sys.dont_write_bytecode=True
    sys.path.insert(0,str(out/'producer'))
    # Both files were copied from exact immutable C Git blobs, never live edits.
    import test_ro_oracle
    tests=unittest.defaultTestLoader.loadTestsFromModule(test_ro_oracle)
    with (out/'ORACLE_TOOL_TESTS.txt').open('x') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(tests)
    if not result.wasSuccessful(): raise RuntimeError('frozen C offline oracle unit tests failed')
    spec=importlib.util.spec_from_file_location('frozen_C_oracle',out/'producer/ro_oracle.py')
    oracle=importlib.util.module_from_spec(spec); spec.loader.exec_module(oracle)
    entry=registration['full_input_identity']['runtime_independent_input_source']['entry_trace_path']
    manifest=oracle.build(entry,out/'oracle',oracle.SCOPE,C_COMMIT)
    assets=[{'name':Path(entry).name,'sha256':manifest['commandlist_sha256'],'bytes':Path(entry).stat().st_size}]
    assets += [{'name':Path(r['path']).name,'sha256':r['sha256'],'bytes':Path(r['path']).stat().st_size}
               for r in manifest['kernels']]
    composite=hashlib.sha256(json.dumps(sorted(assets,key=lambda r:r['name']),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    expected=registration['full_input_identity']['trace_content_sha256']
    if composite!=expected:raise RuntimeError('actual full input differs from D preregistration')
    report={'status':'OFFLINE_ORACLE_CANDIDATE_COMPLETE_PENDING_C_E_REVIEW',
            'oracle_status':manifest['status'],'scope':manifest['scope'],'oracle':True,
            'complete_epoch':'whole_commandlist','kernel_count':manifest['kernel_count'],
            'trace_content_sha256':composite,'expected_trace_content_sha256':expected,
            'manifest':str(out/'oracle/manifest.json'),'manifest_sha256':sha(out/'oracle/manifest.json'),
            'tool_source_commit':C_COMMIT,'tool_source_path':C_PATH,
            'tool_source_sha256':sha(out/'producer/ro_oracle.py'),
            'closed_world_assumptions':manifest['assumptions'],'counts':manifest['counts'],
            'unresolved_opcodes':manifest['unresolved_opcodes'],'tool_unit_tests':result.testsRun,
            'new_simulations':0,'runtime_qualification':False,'application_performance_evidence':False,
            'trace_reuse_order_inference':False}
    save(out/'CANDIDATE.json',report)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workload',choices=['convolutionSeparable','FWT_7_21','btree','dwt2d'],default='convolutionSeparable')
    p.add_argument('--revision',default='r1');p.add_argument('--execute',action='store_true')
    p.add_argument('--worker',type=Path)
    a=p.parse_args()
    registration=json.loads((DOC/'input_registrations'/f'{a.workload}.json').read_text())
    if a.worker:worker(a.worker,registration);return
    out=OUTPUT_ROOT/(a.workload+'_'+a.revision)
    plan={'operation':'OFFLINE_FULL_TRACE_RO_INPUT_ANALYSIS_NOT_SIMULATION',
          'campaign_id':'EPL2_MECHANISM_STUDY_20261019_V1','workload':a.workload,
          'C_producer_commit':C_COMMIT,'C_producer_path':C_PATH,'model_scope':'TRACE_MODEL_CLOSED_WORLD',
          'registration_sha256':sha(DOC/'input_registrations'/f'{a.workload}.json'),
          'input_expected':registration['full_input_identity']['trace_content_sha256'],
          'output':str(out),'output_cap_bytes':OUTPUT_CAP,'worker_address_space_cap_bytes':MEMORY,
          'worker_CPUs':1,'maximum_seconds':TIMEOUT,'new_simulations':0,
          'production_resource_floors':'UNCHANGED; this is the expressly allowed bounded offline old-input analysis',
          'oracle_scope_change':False,'scientific_RO_qualification':'NOT_GRANTED_BY_D',
          'hashing_scope':'producer integrity before/after the necessary full-epoch address scan; no repository/body-wide repeated audit',
          'output_accounting':'D namespace inside E new-result root, visible to canonical6GiB/20GiB accounting; all failures retained'}
    if not a.execute:print(json.dumps(plan,indent=2));return
    SHARED.mkdir(parents=True,exist_ok=True)
    lock=(SHARED/'OFFLINE_RO_ANALYSIS.lock').open('a+')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    out.mkdir(parents=True,exist_ok=False);(out/'producer').mkdir();(out/'tmp').mkdir()
    for name in ['ro_oracle.py','test_ro_oracle.py']:
        (out/'producer'/name).write_bytes(frozen('util/ep_l2/mechanism_study_c/'+name))
    report=dict(plan,status='STARTING_OFFLINE_ONLY',driver_sha256=sha(__file__),
                driver_framework_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
                controller_process=identity(os.getpid()),started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                peak_worker_RSS_bytes=0,peak_output_bytes=0,observations=0)
    report['frozen_source_sha256']={p.name:sha(p) for p in (out/'producer').iterdir()}
    save(out/'RECEIPT.json',report)
    child=None;start=time.monotonic()
    try:
        with (out/'worker.log').open('x') as log:
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(out/'tmp'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(out),'--workload',a.workload],
                                   cwd=REPO,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            report.update(status='RUNNING_OFFLINE_ONLY',worker_process=identity(child.pid));save(out/'RECEIPT.json',report)
            save(SHARED/'OFFLINE_RO_ACTIVITY_r1.json',report)
            while child.poll() is None:
                rss=0
                try:
                    for line in (Path('/proc')/str(child.pid)/'status').read_text().splitlines():
                        if line.startswith('VmRSS:'):rss=int(line.split()[1])*1024
                except FileNotFoundError:pass
                size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
                report['observations']+=1;report['peak_worker_RSS_bytes']=max(report['peak_worker_RSS_bytes'],rss)
                report['peak_output_bytes']=max(report['peak_output_bytes'],size)
                if size>OUTPUT_CAP or rss>MEMORY or time.monotonic()-start>TIMEOUT:
                    raise RuntimeError('owned offline resource/time cap reached')
                save(out/'RECEIPT.json',report);time.sleep(2)
        if child.returncode:raise RuntimeError('offline oracle worker exited '+str(child.returncode))
        report['candidate']=json.loads((out/'CANDIDATE.json').read_text())
        report['status']='OFFLINE_CANDIDATE_READY_PENDING_C_E_REVIEW'
    except BaseException as error:
        report.update(status='OFFLINE_INCOMPLETE_NO_CERTIFICATE',error=repr(error))
        raise
    finally:
        if child is not None:
            if child.poll() is None:
                os.killpg(child.pid,signal.SIGTERM)
                try:child.wait(timeout=3)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
            report['worker_exit_code']=child.returncode
        report['elapsed_seconds']=time.monotonic()-start
        report['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
        report['worker_log_sha256']=sha(out/'worker.log') if (out/'worker.log').exists() else None
        save(out/'RECEIPT.json',report);save(SHARED/'OFFLINE_RO_ACTIVITY_r1.json',report)
        lock.close()
    print(json.dumps({'status':report['status'],'receipt':str(out/'RECEIPT.json')}))

if __name__=='__main__':main()
