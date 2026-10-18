"""Single AA5 authority, four fixed UUIDs, sequential one-launch attempts. No retries."""
from pathlib import Path
import sys
ORIGINAL_PACK=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-lane-aa5-gaussian-convergence-174-v1/docs/dtc_l1/review_packs/DTC_LANE_AA5_GAUSSIAN_V1')
sys.path.append(str(ORIGINAL_PACK/'scripts'))
from common import *
PACK=Path(__file__).resolve().parents[1]
RESUME_RAW=ROOT/'user_recheck_20261018T030133Z'
import fcntl
import signal
import sys
from strict_matrix import require,input_check,collect
import audit_current_cpu_only as audit


def registration_check():
    receipt=json.loads((RESUME_RAW/'CONTINUATION_PUBLICATION_READBACK.json').read_text())
    commit=receipt['commit'];require(receipt['fetched_commit']==commit,'continuation_push_fetch_back')
    require(git(FW,'rev-parse','refs/aa5-bindings/USER_RECHECK_20261018T030133Z')==commit,'continuation_fetched_ref')
    require(subprocess.run(['git','-C',str(FW),'merge-base','--is-ancestor',commit,'HEAD']).returncode==0,'continuation_ancestor')
    require(sha(PACK/'CONTINUATION_PREREGISTRATION.json')==receipt['manifest_sha256'],'continuation_manifest_SHA')
    new=json.loads((PACK/'CONTINUATION_PREREGISTRATION.json').read_text())
    for n,h in new['files'].items():require(sha(PACK/n)==h,'continuation_file_changed:'+n)
    old=json.loads((ORIGINAL_PACK/'EXECUTABLE_PREREGISTRATION.json').read_text())
    for n,h in old['files'].items():require(sha(ORIGINAL_PACK/n)==h,'old_registration_changed:'+n)
    require(sha(ORIGINAL_PACK/'EXECUTABLE_PREREGISTRATION.json')==new['original_registration_sha256'],'old_registration_manifest')
    auth=json.loads((PACK/'USER_CONTINUATION_AUTHORIZATION.json').read_text())
    require(auth['user_request']=='重新试试' and auth['actual_starts_before']==0 and auth['aggregate_budget_total']==4,'user_continuation_scope')
    require(sha(ROOT/'SCIENCE_STOP.json')==auth['previous_STOP_sha256'],'previous_STOP_not_preserved')
    require(all(json.loads((PACK/'RESOURCE_AUDIT.json').read_text())['checks'].values()),'published_current_resource_recheck')
    require(all(json.loads((PACK/'AUTHORITY_AND_FLOCK_AUDIT.json').read_text())['checks'].values()),'published_current_authority_recheck')
    require(not (RESUME_RAW/'MATRIX_EXECUTION_TERMINAL.json').exists(),'continuation_already_terminal_NO_AUTOMATIC_RESTART')
    require(json.loads((ORIGINAL_PACK/'NORMAL_TERMINAL_EXPORT_GATE.json').read_text())['status']=='PASS_NORMAL_TERMINAL_EXPORT_GATE','normal_export_gate')
    require(git(FW,'rev-parse','refs/aa5-bindings/GATE_PUBLISHED')=='5c3a40ff81b366bc6fe362518ae4adc23f0597cc','independent_gate_published')
    return receipt


def check_budget():
    uuids={p[1] for p in POINTS};hits=[]
    # Metadata files only; original raw retained. Archived pre-registration drafts are not launch receipts.
    for root in [p for pattern in ['dtc-*','fast64-*'] for p in Path('/workspace').glob(pattern) if p.is_dir()]:
        for p in root.rglob('RUN_START.json'):
            if 'pre_X2_unpublished_draft' in p.parts:continue
            try:data=json.loads(p.read_text())
            except (OSError,ValueError):continue
            if any(u in json.dumps(data) or u in str(p) for u in uuids):hits.append(dict(path=str(p),uuids=[u for u in uuids if u in json.dumps(data) or u in str(p)]))
    require(len(hits)<=4 and sum(len(p['uuids']) for p in hits)==len(hits),'aggregate_attempt_budget_or_multiple_UUID_receipt')
    return hits


def admission(label):
    dest=RESUME_RAW/'admissions'/label;dest.mkdir(parents=True)
    audit.ROOT=dest;audit.PACK=dest;audit.main()
    resource=json.loads((dest/'RESOURCE_AUDIT.json').read_text());authority=json.loads((dest/'AUTHORITY_AND_FLOCK_AUDIT.json').read_text())
    require(all(resource['checks'].values()),'CURRENT_RESOURCE_ADMISSION_FAIL:'+str(dest))
    # Own AA5 lock is recorded separately; read-only old DTC lock enumerator must remain output-only.
    require(all(authority['checks'].values()),'CURRENT_AUTHORITY_ADMISSION_FAIL:'+str(dest))
    return dict(path=str(dest),resource_sha256=sha(dest/'RESOURCE_AUDIT.json'),authority_sha256=sha(dest/'AUTHORITY_AND_FLOCK_AUDIT.json'))


def emergency(first,current,low_psi_samples):
    cg=current['cgroup'];head=int(cg['memory.max'])-int(cg['memory.current']) if cg['memory.max']!='max' else current['host_MemAvailable_bytes']
    if current['host_MemAvailable_bytes']<8*1024**3 or head<8*1024**3:return 'EMERGENCY_MEMORY_BELOW_8G'
    if current['disk_free_bytes']<2*1024**3:return 'EMERGENCY_DISK_BELOW_2G'
    if any(first[k]!=current[k] for k in ['pswpin','pswpout']):return 'NEW_SYSTEM_SWAP_ACTIVITY'
    old=dict(l.split() for l in first['cgroup']['memory.events'].splitlines());new=dict(l.split() for l in cg['memory.events'].splitlines())
    if any(old[k]!=new[k] for k in ['oom','oom_kill']):return 'NEW_CGROUP_OOM'
    if low_psi_samples>=3:return 'MEMORY_FULL_PSI_GT10_THREE_SAMPLES'
    return None


def run_one(spec,publication,owner):
    label,uid=spec['point'],spec['attempt_uuid'];require(not any(uid in p['uuids'] for p in check_budget()),'UUID_HAS_ACTUAL_RUN_START_STOP:'+uid)
    registration_check();inp=input_check(spec)
    for c in spec['configs']:require(sha(c['path'])==c['sha256'],'config_SHA')
    for p,h in [(spec['runtime_path'],spec['runtime_sha256']),(spec['runtime_library_path'],spec['runtime_library_sha256'])]:require(sha(p)==h,'runtime_SHA')
    adm=admission(label);registration_check();require(not any(uid in p['uuids'] for p in check_budget()),'UUID_LATE_CONFLICT')
    run=ROOT/'attempts'/(label+'_'+uid);run.mkdir(parents=True)
    cfg=[]
    for i,c in enumerate(spec['configs']):
        p=run/f'config-{i}.config';shutil.copy2(c['path'],p);p.chmod(0o444);cfg.append(dict(path=str(p),sha256=sha(p)))
    shutil.copy2(PACK/'scripts/run_matrix.py',run/'immutable_runner.py');shutil.copy2(PACK/'scripts/strict_matrix.py',run/'immutable_strict.py');write(run/'SPEC.json',spec)
    args=[spec['runtime_path'],'-trace',spec['trace_list']]
    for c in cfg:args.extend(['-config',c['path']])
    # Mark actual attempt conservatively immediately before the single Popen; failure consumes the attempt.
    write(run/'RUN_START.json',dict(utc=now(),attempt_uuid=uid,point=label,authority=owner,publication=publication,admission=adm,input=inp,argv=args,config_copies=cfg,timeout_seconds=7200,launch_policy='SINGLE_POPEN_NO_RETRY',environment=spec['runtime_environment']))
    started=time.monotonic();forced=None;identity=False;maps_text='';pidrecord=None;rusage=None;rc=None
    first=snapshot();write(run/'RESOURCE_START.json',first)
    try:
        with (run/'simulator.stdout').open('xb') as out,(run/'simulator.stderr').open('xb') as err:
            env=dict(spec['runtime_environment'])
            child=subprocess.Popen(args,cwd=run,env=env,stdout=out,stderr=err,close_fds=True,start_new_session=False)
            ownpid=child.pid
            # Allow dynamic loader to enter userspace, then bind real PID/start ticks/exe/maps.
            for _ in range(200):
                p=proc(ownpid)
                try:
                    maps_text=Path('/proc',str(ownpid),'maps').read_text()
                    if spec['runtime_library_path'] in maps_text:break
                except OSError:pass
                time.sleep(.01)
            p=proc(ownpid);require(p is not None,'simulator_identity_process_missing')
            pidrecord=dict(**p,exe=os.readlink(f'/proc/{ownpid}/exe'),exe_sha256=sha(f'/proc/{ownpid}/exe'),library_path=spec['runtime_library_path'],library_sha256=sha(spec['runtime_library_path']))
            write(run/'PID.json',pidrecord);(run/'PROCESS_MAPS.txt').write_text(maps_text)
            identity=(pidrecord['exe_sha256']==spec['runtime_sha256'] and spec['runtime_library_path'] in maps_text and pidrecord['library_sha256']==spec['runtime_library_sha256'])
            # All loaded filesystem-backed ELF mappings, including system dynamic libraries, recorded/hashes.
            libs=sorted(set(l.split(None,5)[5] for l in maps_text.splitlines() if len(l.split(None,5))==6 and l.split(None,5)[5].startswith('/')))
            write(run/'LOADED_FILES_SHA256.json',[dict(path=p,sha256=sha(p)) for p in libs])
            write(run/'PROCESS_IDENTITY.json',dict(status='PASS_EXACT_LOADED_BINARY_AND_LIBRARY' if identity else 'FAIL',identity=pidrecord,normal_export_gate_sha256=sha(ORIGINAL_PACK/'NORMAL_TERMINAL_EXPORT_GATE.json')))
            pidfd=os.pidfd_open(ownpid);nextsample=started;psi=0
            with (run/'RESOURCE_MONITOR.jsonl').open('x') as log:
                while True:
                    got,status,usage=os.wait4(ownpid,os.WNOHANG)
                    if got:
                        rc=os.waitstatus_to_exitcode(status);child.returncode=rc
                        rusage={k:getattr(usage,k) for k in ['ru_utime','ru_stime','ru_maxrss','ru_minflt','ru_majflt','ru_inblock','ru_oublock','ru_nvcsw','ru_nivcsw']};break
                    if time.monotonic()>=nextsample:
                        cur=snapshot();psi=psi+1 if float(cur['pressure']['memory']['full']['avg10'])>10 else 0
                        log.write(json.dumps(dict(snapshot=cur,own=proc(ownpid)))+'\n');log.flush();nextsample=time.monotonic()+30
                        reason=emergency(first,cur,psi)
                        if not identity:reason='PROCESS_IDENTITY_FAILURE'
                        if time.monotonic()-started>=7200:reason='TIMEOUT_7200_SECONDS'
                        if reason and forced is None:
                            forced=reason;signal.pidfd_send_signal(pidfd,signal.SIGTERM)
                        print(label,'elapsed',round(time.monotonic()-started),'ownPID',ownpid,'host_available_GiB',round(cur['host_MemAvailable_bytes']/1024**3,2),'forced',forced,flush=True)
                    time.sleep(.5)
            os.close(pidfd)
    except Exception as exc:
        # Engineering failure is retained and never permits another Popen under this UUID.
        forced=forced or 'RUNNER_EXCEPTION:'+repr(exc)
        if 'child' in locals() and child.returncode is None:
            try:
                current=proc(child.pid)
                if current and (pidrecord is None or current['start_ticks']==pidrecord['start_ticks']):
                    fd=os.pidfd_open(child.pid);signal.pidfd_send_signal(fd,signal.SIGTERM);os.close(fd)
                _,status,usage=os.wait4(child.pid,0);rc=os.waitstatus_to_exitcode(status);child.returncode=rc
            except ChildProcessError:pass
    write(run/'RUN_TERMINAL.json',dict(utc=now(),returncode=rc,forced_reason=forced,natural_exit=rc==0 and forced is None,identity_pass=identity,host_wall_seconds_noncomparative=time.monotonic()-started,resource_usage=rusage,PID=pidrecord))
    write(run/'RESOURCE_FINAL.json',snapshot());result=collect(run,spec)
    # Hash only after simulator and receipt writers have closed.
    table(run/'FILES_SHA256.tsv',[dict(path=str(p.relative_to(run)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='FILES_SHA256.tsv'])
    return result


def main():
    ROOT.mkdir(exist_ok=True)
    with (ROOT/'AA5_execution.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        publication=registration_check();hits=check_budget();require(not hits,'PREEXISTING_FIXED_UUID_START_NO_AUTOMATIC_RESUME:'+str(hits))
        owner=proc(os.getpid());owner.update(utc=now(),lock=str(ROOT/'AA5_execution.lock'),max_concurrency=1)
        write(RESUME_RAW/'AUTHORITY_ACTIVE.json',owner)
        results=[]
        try:
            for label,uid,k,sets,ways,cal in POINTS:
                spec=json.loads((PACK/'specs'/f'{label}.json').read_text());result=run_one(spec,publication,owner);results.append(result)
                print('TERMINAL',label,result['status'],result.get('cycles'),flush=True)
                if not result['performance_accepted']:raise RuntimeError('STOP_AFTER_FAILED_STRICT_OR_CONTROL:'+label)
            write(RESUME_RAW/'MATRIX_EXECUTION_TERMINAL.json',dict(utc=now(),status='FOUR_POINTS_TERMINAL',actual_starts=len(check_budget()),results=[dict(point=r['point'],status=r['status'],cycles=r.get('cycles')) for r in results]))
        except Exception as exc:
            write(RESUME_RAW/'MATRIX_EXECUTION_TERMINAL.json',dict(utc=now(),status='STOP',reason=repr(exc),actual_starts=len(check_budget()),completed_results=[dict(point=r['point'],status=r['status'],cycles=r.get('cycles')) for r in results]));print('STOP',repr(exc),flush=True)
        finally:write(RESUME_RAW/'AUTHORITY_TERMINAL.json',dict(utc=now(),owner=owner,status='COORDINATOR_TERMINAL_LOCK_RELEASE_ON_RETURN',actual_starts=len(check_budget())))

if __name__=='__main__':main()
