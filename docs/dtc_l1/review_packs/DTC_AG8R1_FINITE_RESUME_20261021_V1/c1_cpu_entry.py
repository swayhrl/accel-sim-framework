"""Exactly one <=90s/2MiB C1 CPU role, externally source-pinned; no launch/signal.

Only this entry's host-IO check has the explicit user exception. Frozen CPU
admission code is unchanged. No heavy/runtime gate imports this handler.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
import types

PACK=Path(__file__).resolve().parent
REPO=PACK.parents[3]
E=Path('/workspace/dtc-ag8r1-finite-resume-174-v1/evidence')
A=E/'c1_cpu_once'
G=E/'w0_frozen_authority'
REG=PACK/'C1_CPU_REGISTRATION.json'
ROLE='AG8R1_C1_PURE_CPU_WALL_ONLY_HOST_IO_WARNING'
LIMIT=2*1024**2
WRITTEN=0

def require(value,reason):
    if not value:raise ValueError(reason)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,value):
    global WRITTEN
    raw=(json.dumps(value,indent=2,sort_keys=True)+'\n').encode();WRITTEN+=len(raw)
    require(WRITTEN<=LIMIT,'C1_OUTPUT_EXCEEDS_2MiB')
    with (A/name).open('xb') as stream:stream.write(raw)
def images():
    out={}
    for line in Path('/proc/self/maps').read_text().splitlines():
        fields=line.split(None,5)
        if len(fields)==6 and fields[5].startswith('/'):
            require(not fields[5].endswith(' (deleted)'),'DELETED_OWN_IMAGE')
            p=Path(fields[5]).resolve();s=p.stat()
            out.setdefault(str(p),dict(device=s.st_dev,inode=s.st_ino,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,sha256=sha(p)))
    return out
def scoped_cpu_checks(checks,*,role_name,exception_opt_in):
    require(role_name==ROLE and exception_opt_in is True,'HOST_IO_EXCEPTION_NOT_THIS_EXACT_C1_ROLE')
    checks=dict(checks);warnings=[]
    require('host_io' in checks,'MISSING_ORIGINAL_HOST_IO_CHECK')
    if checks['host_io'] is False:
        warnings.append('HOST_IO_WARNING_CPU_ONLY_USER_EXCEPTION')
        checks['host_io']=True
    return checks,warnings

def main():
    began=time.monotonic_ns()
    require(len(sys.argv)==2 and len(sys.argv[1])==64,'EXACT_C1_REGISTRATION_SHA_ARGV')
    pin=sys.argv[1]
    require(sys.argv[0]==str(PACK/'c1_cpu_entry.py') and Path.cwd()==REPO,'EXACT_C1_ENTRY_AND_CWD')
    require(socket.gethostname()=='huangrulin-174' and os.getuid()==0,'ORIGINAL174_ONLY_NOT_AUTHORITY_PROOF')
    require(sha(REG)==pin,'EXTERNAL_ROOT_C1_REGISTRATION_PIN')
    reg=json.loads(REG.read_text())
    require(reg['schema']=='DTC_AG8R1_C1_CPU_ROLE_V1' and reg['goal_commit']=='ae2e9c6f1ce7a0bb3e043c7a251f3f9dd1f86304' and
        reg['canonical_task']=='/root' and reg['role']['name']==ROLE and reg['host_io_exception_only_this_role'] is True and
        reg['maximum_execution_seconds']==90 and reg['maximum_output_bytes']==LIMIT,'EXPLICIT_C1_USER_SCOPE_REQUIRED')
    proof=json.loads((E/'C1_RELEASE_READBACK.json').read_text())
    require(proof['status']=='PASS_EXACT_GITHUB_HEAD_TREE_BLOBS_CLEAN' and proof['registration_sha256']==pin and
        proof['canonical_task']=='/root' and proof['goal_commit']==reg['goal_commit'],'EXTERNAL_ROOT_PUBLICATION_RELEASE_REQUIRED')
    for path,digest in reg['role']['source_sha256'].items():require(sha(path)==digest,'C1_SOURCE_CHANGED:'+path)
    require(sha(reg['role']['executable'])==reg['role']['executable_sha256'],'C1_INTERPRETER_CHANGED')
    for relative,binding in proof['files'].items():require(sha(REPO/relative)==binding['sha256'],'C1_PUBLISHED_FILE_CHANGED')
    runtime_role=dict(reg['role'],argvs=[['/usr/bin/python3.10','-I','-B',str(PACK/'c1_cpu_entry.py'),pin]])
    require(runtime_role['argvs'][0]==[sys.executable,'-I','-B',*sys.argv] and runtime_role['cwd']==str(REPO),'C1_LITERAL_ARGV_NOT_WILDCARD')
    sys.path[:0]=[str(PACK/'prepared_ag8r1'),str(G/'vendor'),str(G)]
    from cpu_admission_v2 import CPUAdmission
    from ownership import identity
    from shared_authority import fresh_process
    from wall_contract_qualification import qualify_wall_contract
    # Warm all actual test imports before freezing own loaded images.
    sampler=CPUAdmission(dict(admission=dict(disk_floor_exclusive_bytes=5*1024**3)),[runtime_role])
    owner=identity(os.getpid());loaded=images()
    A.mkdir(exist_ok=False)
    write('BEGIN.json',dict(registration_sha256=pin,owner=owner,loaded_images=loaded,
        role=runtime_role,external_readback_head=proof['head'],model_permission=False))
    snapshots=[];all_checks={};warnings=[];tests_started=False;tests_completed=False;wall=None;failure=None
    def current_self():
        live=fresh_process(os.getpid(),identity)
        require(live['pid']==owner['pid'] and live['start_ticks']==owner['start_ticks'] and live['tracer_pid']==0 and
            live['argv']==runtime_role['argvs'][0] and live['cwd']==str(REPO) and live['exe']==runtime_role['executable'],'C1_ACTUAL_SELF_INSTANCE_CHANGED')
        require(images()==loaded,'C1_LOADED_IMAGE_CLOSURE_CHANGED')
        require(all(sha(p)==digest for p,digest in runtime_role['source_sha256'].items()),'C1_SOURCE_CLOSURE_CHANGED')
        require(time.monotonic_ns()-began<=90*10**9,'C1_EXECUTION_DEADLINE_90S')
    try:
        for index in range(2):
            if index:time.sleep(10.1)
            current_self()
            # Clone only the frozen sampler's output-root lookup; original code
            # and the production/heavy admission module remain untouched.
            original=CPUAdmission.sample
            sample_fn=types.FunctionType(original.__code__,dict(original.__globals__,RAW=A),original.__name__,original.__defaults__,original.__closure__)
            sample=sample_fn(sampler)
            stat=A.stat();v=os.statvfs(A);sample['disk_free']=v.f_bavail*v.f_frsize
            sample['output_filesystem_device']=stat.st_dev
            sample['self_cgroup']=Path('/proc/self/cgroup').read_text().strip()
            write('FIRST.json' if index==0 else 'SECOND.json',sample)
            original_checks=sampler.checks(sample)
            original_checks.update(own_current_role=any(r['role']==ROLE and r['pid']==owner['pid'] for r in sample['authority'].get('exact_external_CPU_controls',[])),
                source_and_images=True,known_self_cgroup=sample['self_cgroup']=='0::/',
                projected_writes_gt5GiB=sample['disk_free']-LIMIT>5*1024**3)
            effective,warning=scoped_cpu_checks(original_checks,role_name=ROLE,exception_opt_in=True)
            all_checks.update({str(index+1)+'_'+k:v for k,v in effective.items()});warnings+=warning
            snapshots.append(sample)
            write('CHECK_FIRST.json' if index==0 else 'CHECK_SECOND.json',dict(original_checks=original_checks,hard_effective_checks=effective,warnings=warning))
            require(all(effective.values()),'C1_NONEXEMPT_HARD_ADMISSION_FAILURE')
        first,second=snapshots
        pair=dict(gap_ge10s=second['monotonic_ns']-first['monotonic_ns']>=10*10**9,
            host_oom_unchanged=first['host_oom_kill']==second['host_oom_kill'],
            cgroup_oom_unchanged=all(first['cgroup_events'][k]==second['cgroup_events'][k] for k in ['oom','oom_kill']),
            output_device_same=first['output_filesystem_device']==second['output_filesystem_device'])
        all_checks.update(pair);write('ADMISSION.json',dict(status='PASS_C1_SCOPED_CPU_R2_ONLY',checks=all_checks,warnings=warnings))
        require(all(pair.values()),'C1_PAIRED_HARD_FAILURE')
        current_self();tests_started=True
        wall=qualify_wall_contract(A)
        require(wall['status']=='PASS_AD8_NARROW_WALL_CONTRACT','C1_ACTUAL_WALL_CHECKS_FAILED')
        # Four tiny declared-synthetic scope/negative cases; do not rerun W1/W2.
        high=dict(host_io=False,cgroup_io=True,memory=True,authority=True)
        result,w=scoped_cpu_checks(high,role_name=ROLE,exception_opt_in=True);assert all(result.values()) and w==['HOST_IO_WARNING_CPU_ONLY_USER_EXCEPTION']
        bad=dict(high,cgroup_io=False);result,w=scoped_cpu_checks(bad,role_name=ROLE,exception_opt_in=True);assert result['cgroup_io'] is False
        rejected=False
        try:scoped_cpu_checks(high,role_name='HEAVY_SIMULATOR',exception_opt_in=True)
        except ValueError:rejected=True
        assert rejected
        result,w=scoped_cpu_checks(dict(high,host_io=True),role_name=ROLE,exception_opt_in=True);assert all(result.values()) and not w
        tests_completed=True;current_self()
        host_oom=next(int(s.split()[1]) for s in Path('/proc/vmstat').read_text().splitlines() if s.startswith('oom_kill '))
        cg_events=dict((k,int(v)) for k,v in (line.split() for line in Path('/sys/fs/cgroup/memory.events').read_text().splitlines()))
        require(host_oom==second['host_oom_kill'] and all(cg_events[k]==second['cgroup_events'][k] for k in ['oom','oom_kill']),'C1_NEW_OOM_AFTER_TEST')
    except Exception as error:failure=repr(error)
    result=dict(status='PASS_AG8R1_C1_CPU_WALL_CONTRACT' if failure is None else 'HOLD_AG8R1_C1_CPU_NOT_QUALIFIED',
        failure=failure,registration_sha256=pin,external_readback_head=proof['head'],owner=owner,
        actual_wall_seconds=(time.monotonic_ns()-began)/1e9,tests_started=tests_started,tests_completed=tests_completed,
        narrow_source_bound_checks=0 if wall is None else len(wall['checks']),cpu_exception_scope_cases=4 if tests_completed else 0,
        synthetic_resource_samples=0 if wall is None else wall['synthetic_resource_samples'],actual_wall_result=wall,
        warnings=warnings,hard_checks=all_checks,resource_samples=[dict(monotonic_ns=s['monotonic_ns'],utc=s['utc'],pressure=s['pressure'],
            host_available=s['host_available'],cgroup_headroom=s['cgroup_headroom'],cgroup_events=s['cgroup_events'],host_oom_kill=s['host_oom_kill'],
            disk_free=s['disk_free'],output_device=s['output_filesystem_device'],authority_status=s['authority']['status']) for s in snapshots],
        loaded_image_closure_unchanged=failure is None,raw_receipts_local_only=True,
        provenance='DECLARED_SYNTHETIC_CLOCK_RESOURCE_AND_ALTERED_TERMINAL_CASES; REAL_CPU_ROLE_ADMISSION_IDENTITY_AND_EXECUTION',
        old_W1_W2_tests_reexecuted=0,D0_reexecuted=False,simulator_starts=0,fixture_starts=0,process_signals=0,
        C1_exception_transferred_to_heavy_or_runtime=False,bytes_before_final_receipt=WRITTEN,maximum_output_bytes=LIMIT)
    write('RESULT.json',result)
    require(sum(p.stat().st_size for p in A.iterdir() if p.is_file())<=LIMIT,'C1_FINAL_TOTAL_OUTPUT_BOUND')
    print(json.dumps({k:result[k] for k in ['status','failure','narrow_source_bound_checks','cpu_exception_scope_cases','synthetic_resource_samples','warnings','actual_wall_seconds','simulator_starts']}),flush=True)
    return 0 if failure is None else 2

if __name__=='__main__':raise SystemExit(main())
