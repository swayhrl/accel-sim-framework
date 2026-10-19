"""Bounded original unrun cases only. No app, producer PASS or qualification."""
import sys
sys.path.insert(0,'/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
import json,os,time,subprocess
from pathlib import Path
import coordinator as c
import run as legacy

ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
OUT=c.OUTPUT/'E_REMAINING_NATIVE_DIAGNOSTICS_r1'
PRIOR=c.OUTPUT/'A_COMMON_WVTM_NATIVE_r1/RECEIPT.json'
BUILD=c.OUTPUT/'A_COMMON_WVTM_BUILD_r3/BUILD_ONLY_RECEIPT.json'
LIMIT=2*c.GIB

def main():
    c.tooling_binding();prior=json.loads(PRIOR.read_text());build=json.loads(BUILD.read_text())
    c.require(prior['native_invocations_completed']==18 and prior['native_invocations_attempted']==19,
              'exact failed producer boundary required, no reset or rerun')
    rows=prior['planned_tests'][19:];c.require(len(rows)==45,'original remaining45 only')
    c.require(not OUT.exists(),'retain old attempt; never overwrite')
    binaries=dict(build['test_binary_sha256']);binaries[build['binary']]=build['binary_sha256']
    for name,sha in binaries.items():c.require(c.digest(name)==sha,'retained ELF changed')
    needed=sum(Path(name).stat().st_size for name in binaries)
    c.require(needed+64*2**20<LIMIT,'all retained ELF snapshots plus conservative64MiB logs must fit')
    coord=c.Coordinator();lease=coord.reserve_work('E','test',1,8*c.GIB,LIMIT,OUT)
    OUT.mkdir();(OUT/'tmp').mkdir();(OUT/'cache').mkdir();(OUT/'retained_elf').mkdir()
    report=dict(status='ENGINEERING_REMAINING_NATIVE_RUNNING_NOT_QUALIFIED',campaign_id=c.CAMPAIGN,
        lease_id=lease['lease_id'],policy={k:lease[k] for k in ('policy_id','disk_floor_bytes','monitor_reserve_bytes','monitor_interval_seconds')},
        source_identity=dict(core_source_commit=build['core_source_commit'],framework_source_commit=build['framework_source_commit'],vendor_pybind11_commit=build['vendor_commit'],binary_sha256=build['binary_sha256']),
        producer_receipt_sha256=c.digest(PRIOR),build_receipt_sha256=c.digest(BUILD),
        old_passes_reused=0,old_failed_case_rerun=False,tests=[],retained_binaries=[],
        scientific_acceptance=False,full_application_starts=0)
    proc=None;ever_started=False;started=time.monotonic();wall_limit=7200
    def save():c.write_json(OUT/'RECEIPT.json',report)
    def guard():
        live=c.local_resources();usage=c.output_usage();incident=c.disk_policy.stop_detail(live,lease)
        own_bytes=c.retained_tree_bytes(OUT)
        if (incident or live['share_disk_free_bytes']<40*c.GIB or live['available_memory_bytes']<64*c.GIB
             or own_bytes>=LIMIT or usage['new_bytes']>=6*c.GIB or usage['total_bytes']>=20*c.GIB
             or (proc is not None and legacy.process_tree_rss(proc.pid)>8*c.GIB)):
            incident=incident or dict(status='RESOURCE_LIMIT',reason='SHARE_RAM_OR_OUTPUT')
            incident.update(lease_id=lease['lease_id'],source_identity=report['source_identity'],actual_resources=live,
                            output_usage=usage,own_result_bytes=own_bytes,scope='OWNED_GROUP_ONLY')
            report.update(status='RESOURCE_LIMIT',resource_limit=incident);c.write_json(OUT/'RESOURCE_LIMIT.json',incident)
            raise RuntimeError('resource protection')
        c.require(time.monotonic()-started<wall_limit and time.time()<c.INTAKE_DEADLINE,'bounded native intake deadline')
    try:
        save();guard()
        # Archive EVERY existing actual executable before any future A compile.
        for name,sha in binaries.items():
            dest=OUT/'retained_elf'/Path(name).name
            with Path(name).open('rb') as src,dest.open('xb') as dst:
                while True:
                    guard();chunk=src.read(4*2**20)
                    if not chunk:break
                    dst.write(chunk)
            c.require(c.digest(dest)==sha,'retained binary copy changed')
            report['retained_binaries'].append(dict(original=name,path=str(dest),sha256=sha,bytes=dest.stat().st_size));save()
        env=dict(os.environ,TMPDIR=str(OUT/'tmp'),TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'),XDG_CACHE_HOME=str(OUT/'cache'),
                 OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        for case in rows:
            guard();command=case['native_command'];raw=OUT/(case['id']+'.log')
            c.require(c.digest(command[0])==binaries[command[0]],'current fixture changed before invocation')
            t0=time.monotonic();timed_out=False
            with raw.open('xb') as stream:
                proc=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,cwd=OUT,env=env,start_new_session=True)
                ever_started=True;identity=coord.bind_work_process(lease['lease_id'],'E',proc.pid)
                while proc.poll() is None:
                    guard()
                    if time.monotonic()-t0>case['timeout_seconds']:
                        timed_out=True;legacy.terminate_owned(proc);break
                    time.sleep(lease['monitor_interval_seconds'])
            text=raw.read_text(errors='replace');passed=not timed_out and proc.returncode==case['expected_exit'] and case['required_terminal'] in text
            report['tests'].append(dict(case=case['id'],suite=case['suite'],native_command=command,process=identity,
                expected_exit=case['expected_exit'],actual_exit=proc.returncode,required_terminal=case['required_terminal'],
                status='ENGINEERING_NATIVE_EXPECTATION_PASS' if passed else 'FAILED_RETAINED_NOT_QUALIFIED',
                raw_log=str(raw),raw_log_sha256=c.digest(raw),native_binary_sha256=binaries[command[0]],wall_seconds=time.monotonic()-t0,timed_out=timed_out))
            proc=None;save()
        for name,sha in binaries.items():c.require(c.digest(name)==sha,'A changed source-bound binary during native diagnostic')
        report.update(status='ENGINEERING_REMAINING_NATIVE_COMPLETE_NOT_QUALIFIED',completed=len(report['tests']),
            passed=sum(r['status']=='ENGINEERING_NATIVE_EXPECTATION_PASS' for r in report['tests']),
            failed=sum(r['status']!='ENGINEERING_NATIVE_EXPECTATION_PASS' for r in report['tests']))
    except BaseException as error:
        if report['status']!='RESOURCE_LIMIT':report['status']='FAILED_RETAINED_NOT_QUALIFIED'
        report['error']=repr(error);raise
    finally:
        if proc is not None:legacy.terminate_owned(proc)
        coord.release_work(lease['lease_id'],'E','bounded remaining native diagnostics; all old/new raw retained',no_child_started=not ever_started)
        report.update(lease_released=True,wall_seconds=time.monotonic()-started,actual_result_bytes=c.retained_tree_bytes(OUT));save()
    print(report['status'],report['passed'],report['failed'])

if __name__=='__main__':main()
