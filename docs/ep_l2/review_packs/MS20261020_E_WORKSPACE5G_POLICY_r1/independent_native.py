"""E-owned finite native replay, not an application or automatic qualification.

Requires an actually successful A producer and its exact frozen case plan. Uses
one original central E test lease, actual PID identity, existing owned-process
monitor and independent retained raw files. Scientific review follows execution.
"""
import sys
sys.path.insert(0,'/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
import argparse
import json
import os
from pathlib import Path
import resource
import subprocess
import time
import coordinator as c
import run as legacy

GATE_CASES={
 'old_all_off_equivalence':['default_off'],
 'finite_wbuf':['S_observer0','U_observer0','native_dirty_boundaries'],
 'requester_exact_once':['b1-multi','combined_same_address','combined_shared_pool'],
 'sector_reference_data':['b1-read-first','b1-dirty','full_victim_sectors','full_victim_partial','combined_shared_pool'],
 'stale_fill':['stale_return_1','stale_return_2','combined_same_address'],
 'resource_closure':['combined_shared_pool','combined_fallback','GPU_epoch_API_64_R1'],
 'wb_lifecycle':['dirty_snapshot','dirty_pending','combined_pinned_wb'],
 'bank_service':['bank_identity_extended','ro_native_dram_warm_full'],
 'physical_bank_clock':['physical_clock_warm_1','physical_clock_warm_2','ro_native_dram_warm_full'],
 'memcpy_payload_identity':['host_prefill_1','host_prefill_2','GPU_epoch_API_64_R1'],
 'mode_legality':['combined_host_update','combined_fallback','combined_factor_tag_T0_M0'],
 'shared_payload_lifecycle':['combined_shared_pool','full_victim_cycle'],
 'shared_directory_cost_and_full':['native_dirty_boundaries','WV_observer'],
 'pinned_victim_wb_completion_identity':['combined_pinned_wb','dirty_pending'],
 'ro_tag_reuse_late_sector_identity':['combined_same_address','combined_factor_tag_T1_M1'],
 'ro_victim_same_address_and_host_invalidation':['combined_host_update','combined_same_address'],
 'backpressure_complete_quiescence':['combined_shared_pool','combined_native_ro_mux','GPU_epoch_API_64_R1'],
 'tm_trigger_default_off_and_illegal_combinations':['combined_factor_tag_T0_M0','combined_factor_tag_T1_M0',
   'combined_factor_tag_T0_M1','combined_factor_tag_T1_M1','combined_factor_line_T0_M0',
   'combined_factor_line_T1_M0','combined_factor_line_T0_M1','combined_factor_line_T1_M1','combined_host_update']}


def execute(admission_path,out):
    admission=json.loads(Path(admission_path).read_text());c.tooling_binding()
    c.require(admission['prepared_by']=='E' and admission['campaign_id']==c.CAMPAIGN,
              'exact E independent replay admission required')
    c.require(not out.exists() and out.parent.resolve()==c.OUTPUT.resolve(),'fresh E result directory required')
    c.require(admission['source_identity']['binary_sha256']==c.digest(admission['binary']), 'official binary changed')
    artifacts=admission['frozen_artifacts']
    c.require(bool(artifacts),'official source/compile/test/plan artifacts required')
    for item in artifacts:c.require(c.digest(item['path'])==item['sha256'],'official artifact changed')
    c.require(admission['producer_actual_pass'] is True and admission['producer_main_cases']==55,
              'official55 real producer cases must pass first; source plan is not producer')
    cases=admission['cases'];by_id={r['id']:r for r in cases}
    ids=sorted({name for values in GATE_CASES.values() for name in values})
    c.require(len(by_id)==len(cases) and set(ids)<=set(by_id),'missing/duplicate frozen native cases')
    for name in ids:
        row=by_id[name];cmd=row['native_command']
        c.require(Path(cmd[0]).name.startswith('ep_l2_') and row['expected_exit']==0 and
                  0<row['timeout_seconds']<=120,'bounded direct native fixture only')
        c.require(c.digest(cmd[0])==admission['native_binary_sha256'][cmd[0]],'native executable changed')
    # Check actual compiler assertions, not only the receipt declaration.
    c.require(bool(admission['assertion_flag_files']),'actual compile flag files required')
    for path,sha in admission['assertion_flag_files'].items():
        c.require(c.digest(path)==sha and '-DNDEBUG' not in Path(path).read_text(),'assertions disabled or flags changed')
    resource.setrlimit(resource.RLIMIT_CORE,(0,0));out.mkdir(exist_ok=False)
    report={'campaign_id':c.CAMPAIGN,'source_identity':admission['source_identity'],'tests':[],
      'status':'E_INDEPENDENT_NATIVE_RUNNING_NOT_QUALIFIED','full_application_starts':0,
      'admission_sha256':c.digest(admission_path),'gate_case_map':GATE_CASES}
    coord=c.Coordinator();lease=None;proc=None;path=out/'RECEIPT.json'
    try:
        lease=coord.reserve_work('E','test',1,4*c.GIB,128*2**20,out)
        report['lease_id']=lease['lease_id'];report['resource_policy']=lease;(out/'tmp').mkdir();c.write_json(path,report)
        for name in ids:
            case=by_id[name];command=case['native_command'];log=out/(name+'.log');start=time.monotonic();peak=0
            with log.open('xb') as stream:
                proc=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,cwd=out,
                    env=dict(os.environ,TMPDIR=str(out/'tmp'),TMP=str(out/'tmp'),TEMP=str(out/'tmp'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'),start_new_session=True)
                identity=coord.bind_work_process(lease['lease_id'],'E',proc.pid)
                while proc.poll() is None:
                    live=c.local_resources();peak=max(peak,legacy.process_tree_rss(proc.pid))
                    c.require(time.monotonic()-start<case['timeout_seconds'] and peak<=4*c.GIB,'independent native timeout/RAM')
                    disk_stop=c.disk_policy.stop_detail(live,lease)
                    if disk_stop:
                        report['resource_limit']=disk_stop;c.write_json(out/'RESOURCE_LIMIT.json',disk_stop)
                        report['status']='RESOURCE_LIMIT';raise RuntimeError('workspace stop reserve reached')
                    c.require(live['share_disk_free_bytes']>=40*c.GIB and
                        live['available_memory_bytes']>=64*c.GIB,'independent native Share/RAM floor')
                    c.require(c.retained_tree_bytes(out)<128*2**20,'native result reservation exceeded')
                    time.sleep(lease['monitor_interval_seconds'])
            text=log.read_text(errors='replace')
            c.require(proc.returncode==case['expected_exit'] and case['required_terminal'] in text,
                      'independent native failed: '+name)
            report['tests'].append({'case':name,'command':command,'process':identity,'exit_code':proc.returncode,
              'raw_log':str(log),'raw_log_sha256':c.digest(log),'native_binary_sha256':c.digest(command[0]),
              'peak_rss_bytes':peak,'wall_seconds':time.monotonic()-start,'execution_expectation':'PASS',
              'scientific_gate_status':'PENDING_E_REFERENCE_DATA_AND_SOURCE_REVIEW'})
            proc=None;c.write_json(path,report)
        for item in artifacts:c.require(c.digest(item['path'])==item['sha256'],'artifact changed during independent replay')
        report['status']='E_INDEPENDENT_NATIVE_EXECUTIONS_COMPLETE_PENDING_SCIENTIFIC_REVIEW'
    except BaseException as error:
        report.update(status=report['status'] if report['status']=='RESOURCE_LIMIT' else 'FAILED_FROZEN_NO_QUALIFICATION',error=repr(error));raise
    finally:
        if proc is not None:legacy.terminate_owned(proc)
        if lease:coord.release_work(lease['lease_id'],'E','bounded E independent native completed/failed; retained raw',
                                     no_child_started=not bool(report['tests']) and proc is None)
        c.write_json(path,report)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--admission',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path);parser.add_argument('--execute',required=True,action='store_true')
    args=parser.parse_args();print(json.dumps(execute(args.admission,args.out),indent=2))
