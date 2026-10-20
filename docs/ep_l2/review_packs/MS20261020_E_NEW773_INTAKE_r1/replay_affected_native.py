"""E-owned 24 affected native cases on frozen Core27 archive; no full applications."""
import sys
from pathlib import Path
sys.path.insert(0,'/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
import json,os,subprocess,time,resource
import coordinator as c
import run as legacy

def execute():
    pack=Path(__file__).resolve().parent
    admission=json.loads((pack/'AFFECTED_NATIVE_ADMISSION.json').read_text())
    out=c.OUTPUT/'E_INDEPENDENT_NEW773_AFFECTED_NATIVE_r1'
    c.require(not out.exists(),'fresh revision only')
    c.require(admission['prepared_by']=='E' and len(admission['cases'])==24,'exact finite admission')
    assets={}
    for row in admission['cases']:
        c.require(c.digest(row['command'][0])==row['native_binary_sha256'],'native ELF changed')
        for arg in row['command']:
            if Path(arg).is_file():assets[arg]=c.digest(arg)
    for a in admission['frozen_artifacts']:c.require(c.digest(a['path'])==a['sha256'],'producer artifact changed')
    resource.setrlimit(resource.RLIMIT_CORE,(0,0));coord=c.Coordinator();lease=None;proc=None
    report=dict(campaign_id=c.CAMPAIGN,qualified_by='E',source_identity=admission['source_identity'],
                status='RUNNING_NOT_QUALIFIED',tests=[],full_application_starts=0,frozen_command_assets=assets,
                admission_sha256=c.digest(pack/'AFFECTED_NATIVE_ADMISSION.json'))
    try:
        lease=coord.reserve_work('E','test',1,4*c.GIB,64*2**20,out)
        out.mkdir(exist_ok=False);(out/'tmp').mkdir();report['lease']=lease
        c.write_json(out/'RECEIPT.json',report)
        for row in admission['cases']:
            log=out/(row['case']+'.log');start=time.monotonic();peak=0
            with log.open('xb') as stream:
                proc=subprocess.Popen(row['command'],stdout=stream,stderr=subprocess.STDOUT,cwd=out,
                    env=dict(os.environ,TMPDIR=str(out/'tmp'),TMP=str(out/'tmp'),TEMP=str(out/'tmp'),
                             OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'),start_new_session=True)
                identity=coord.bind_work_process(lease['lease_id'],'E',proc.pid)
                while proc.poll() is None:
                    live=c.local_resources();usage=c.output_usage();peak=max(peak,legacy.process_tree_rss(proc.pid))
                    incident=c.disk_policy.stop_detail(live,lease)
                    if (incident or live['share_disk_free_bytes']<40*c.GIB or live['available_memory_bytes']<64*c.GIB
                        or peak>4*c.GIB or c.retained_tree_bytes(out)>=64*2**20 or usage['new_bytes']>=6*c.GIB or usage['total_bytes']>=20*c.GIB):
                        report['RESOURCE_LIMIT']=dict(incident or {},resources=live,usage=usage,process=identity)
                        c.write_json(out/'RESOURCE_LIMIT.json',report['RESOURCE_LIMIT']);raise RuntimeError('resource guard')
                    c.require(time.monotonic()-start<120,'finite native timeout')
                    time.sleep(lease['monitor_interval_seconds'])
            text=log.read_text(errors='replace')
            test=dict(case=row['case'],command=row['command'],process=identity,exit_code=proc.returncode,
                required_terminal=row['required_terminal'],native_binary_sha256=c.digest(row['command'][0]),
                raw_log=str(log),raw_log_sha256=c.digest(log),peak_rss_bytes=peak,wall_seconds=time.monotonic()-start,
                execution_expectation='PASS' if proc.returncode==row['expected_exit'] and row['required_terminal'] in text else 'FAIL',
                semantic_lines=[x for x in text.splitlines() if any(s in x for s in ['SEMANTIC|','RO detailed DRAM','C_FULL_V2|','RO_PHYSICAL_CLOCK|'])])
            report['tests'].append(test);c.write_json(out/'RECEIPT.json',report)
            c.require(test['execution_expectation']=='PASS','affected native failure: '+row['case']);proc=None
        for p,h in assets.items():c.require(c.digest(p)==h,'frozen command asset changed during replay')
        for a in admission['frozen_artifacts']:c.require(c.digest(a['path'])==a['sha256'],'producer artifact changed during replay')
        report['status']='E_24_AFFECTED_NATIVE_EXECUTIONS_PASS_PENDING_GATE_REVIEW'
    except BaseException as e:
        report.update(status='RESOURCE_LIMIT' if 'RESOURCE_LIMIT' in report else 'FAILED_NO_QUALIFICATION',error=repr(e));raise
    finally:
        if proc is not None:legacy.terminate_owned(proc)
        if lease:coord.release_work(lease['lease_id'],'E','E affected24 finite replay ended; all raw retained',no_child_started=not bool(report['tests']) and proc is None)
        report['ended_unix']=time.time()
        if out.exists():c.write_json(out/'RECEIPT.json',report)
    print(json.dumps(dict(status=report['status'],tests=len(report['tests']),lease_id=lease['lease_id'])))
if __name__=='__main__':execute()
