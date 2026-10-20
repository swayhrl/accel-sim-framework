"""Single <=90s/2MiB pure CPU role; ONLY host-IO admission has approved warning."""
import dataclasses
from datetime import datetime,timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import time
import unittest

P=Path(__file__).resolve().parent
E=Path('/workspace/dtc-ag7-policyb-integrated-174-v1/evidence')
A=E/'w1_cpu_once'
G=E/'w0_frozen_authority'
LIMIT=2*1024**2
WRITTEN=0


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(name,value):
    global WRITTEN
    data=(json.dumps(value,indent=2)+'\n').encode();WRITTEN+=len(data)
    assert WRITTEN<=LIMIT,'CPU_OUTPUT_BOUND'
    with (A/name).open('xb') as f:f.write(data)


def images():
    found={}
    for line in Path('/proc/self/maps').read_text().splitlines():
        v=line.split(None,5)
        if len(v)==6 and v[5].startswith('/'):
            p=Path(v[5]);assert not str(p).endswith(' (deleted)')
            key=str(p.resolve());st=p.stat()
            if key not in found:
                found[key]=dict(device=st.st_dev,inode=st.st_ino,size=st.st_size,
                    mtime_ns=st.st_mtime_ns,ctime_ns=st.st_ctime_ns,sha256=sha(p))
    return found


def identity():
    stat=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()
    status=Path('/proc/self/status').read_text()
    assert next(int(v.split()[1]) for v in status.splitlines() if v.startswith('TracerPid:'))==0
    return dict(pid=os.getpid(),start_ticks=int(stat[19]),
        boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip())


def main():
    started=time.monotonic();A.mkdir(exist_ok=False)
    reg=json.loads((P/'W1_CPU_REGISTRATION.json').read_text());role=reg['role']
    assert sys.argv==[str(P/'w1_cpu_entry.py')]
    assert role['argvs']==[[sys.executable,'-I','-B',sys.argv[0]]]
    assert role['cwd']==os.getcwd() and sha(sys.executable)==role['executable_sha256']
    for path,digest in role['source_sha256'].items():assert sha(path)==digest,path
    ident=identity()
    write('ENTRY_START.json',dict(identity=ident,role=role,utc=datetime.now(timezone.utc).isoformat(),
        approved_exception='W1_HOST_IO_WARNING_ONLY_NOT_HEAVY_PHASES',max_seconds=90,max_output_bytes=LIMIT))
    sys.path[:0]=[str(G/'vendor'),str(G)]
    from cpu_admission_v2 import CPUAdmission
    gate=CPUAdmission(reg,[role])
    before_images=images()
    samples=[];all_checks={};warnings=[]
    for index in range(2):
        if index:time.sleep(10.1)
        s=gate.sample();samples.append(s)
        write('FIRST.json' if index==0 else 'SECOND.json',s)
        c=gate.checks(s)
        if not c['host_io']:warnings.append(dict(sample=index+1,reason='APPROVED_W1_HOST_IO_GT25_WARNING'))
        c['host_io_warning_exception_authorized_for_this_role']=True
        del c['host_io']
        c['actual_output_device']=os.stat(E).st_dev==s['output_filesystem_device']
        c['projected_output_remains_gt5GiB']=s['disk_free']-LIMIT>5*1024**3
        c['own_instance_unchanged']=identity()==ident
        c['loaded_images_bound_and_unchanged']=images()==before_images
        all_checks.update({str(index+1)+'_'+k:v for k,v in c.items()})
        if not all(c.values()):
            write('RESULT.json',dict(status='W1_HOLD_HARD_PREDICATE',checks=all_checks,warnings=warnings,
                test_methods_executed=0,simulator_starts=0,entry_seconds=time.monotonic()-started))
            print('W1_HOLD_HARD_PREDICATE');return 0
    a,b=samples
    all_checks.update(gap_ge10s=b['monotonic_ns']-a['monotonic_ns']>=10*10**9,
        output_device_unchanged=a['output_filesystem_device']==b['output_filesystem_device'],
        host_oom_unchanged=a['host_oom_kill']==b['host_oom_kill'],
        cgroup_oom_unchanged=all(a['cgroup_events'][k]==b['cgroup_events'][k] for k in ['oom','oom_kill']))
    if not all(all_checks.values()):
        write('RESULT.json',dict(status='W1_HOLD_PAIR',checks=all_checks,warnings=warnings,test_methods_executed=0))
        print('W1_HOLD_PAIR');return 0
    for path,digest in role['source_sha256'].items():assert sha(path)==digest,path
    sys.path.insert(0,str(P))
    import test_policy_b_offline
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_policy_b_offline)
    output=io.StringIO();result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
    after=images();same_images=after==before_images
    final=dict(status='W1_PASS_PURE_CPU_ONLY' if result.wasSuccessful() and same_images else 'W1_FAIL_CPU_OR_IMAGE',
        tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
        checks=all_checks,warnings=warnings,loaded_images_initial=before_images,loaded_images_final=after,
        loaded_image_closure_unchanged=same_images,identity=ident,source_sha256=role['source_sha256'],
        transcript=output.getvalue(),entry_seconds=time.monotonic()-started,
        provenance='DECLARED_SYNTHETIC',simulator_starts=0,fixture_starts=0,process_signals=0,
        production_IO_gate_modified=False,exception_transfers_to_heavy_build_or_simulator=False)
    assert final['entry_seconds']<=90
    write('RESULT.json',final);print(output.getvalue());print(json.dumps({k:v for k,v in final.items() if k in ['status','tests_run','failures','errors','entry_seconds']}))
    return 0 if final['status']=='W1_PASS_PURE_CPU_ONLY' else 1


if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:
        write('EXCEPTION.json',dict(error=repr(exc),simulator_starts=0))
        raise
