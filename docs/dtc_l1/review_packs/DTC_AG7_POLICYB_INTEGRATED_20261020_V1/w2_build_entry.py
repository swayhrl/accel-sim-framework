"""Single-worker strict R2 admission and Framework-only build; never executes model."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

P=Path(__file__).resolve().parent
E=Path('/workspace/dtc-ag7-policyb-integrated-174-v1/evidence')
G=E/'w0_frozen_authority'
B=E.parent/'build'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def write(path,value):
    with path.open('x') as f:f.write(json.dumps(value,indent=2)+'\n')


def main():
    assert len(sys.argv)==2 and sys.argv[0]==str(P/'w2_build_entry.py') and sys.argv[1] in ('1','2')
    attempt=E/('w2_build_admission_'+sys.argv[1]);attempt.mkdir(exist_ok=False)
    reg=json.loads((P/'W2_BUILD_REGISTRATION.json').read_text());role=reg['role']
    assert role['cwd']==str(Path.cwd()) and sha(sys.executable)==role['executable_sha256']
    for path,h in role['source_sha256'].items():assert sha(path)==h,path
    sys.path[:0]=[str(G/'vendor'),str(G)]
    sys.path.insert(0,str(P))
    from w1_cpu_entry import images,identity
    from cpu_admission_v2 import CPUAdmission
    gate=CPUAdmission(reg,[role]);samples=[];checks={};image_binding=images();own=identity()
    for n in range(2):
        if n:time.sleep(10.1)
        s=gate.sample();samples.append(s);write(attempt/('FIRST.json' if n==0 else 'SECOND.json'),s)
        c=gate.checks(s)  # NO W1 host IO exception.
        c['actual_output_device']=os.stat(E).st_dev==s['output_filesystem_device']
        c['projected_build_margin']=s['disk_free']-reg['expected_write_bytes']>5*1024**3
        c['self_instance_unchanged']=identity()==own
        c['self_loaded_images_unchanged']=images()==image_binding
        checks.update({str(n+1)+'_'+k:v for k,v in c.items()})
        if not all(c.values()):
            write(attempt/'RESULT.json',dict(status='RESOURCE_HOLD',checks=checks,
                compiler_starts=0,simulator_starts=0,host_io_warning_exception=False))
            print('RESOURCE_HOLD',checks);return 0
    a,b=samples
    checks.update(gap_ge10s=b['monotonic_ns']-a['monotonic_ns']>=10*10**9,
        host_oom_unchanged=a['host_oom_kill']==b['host_oom_kill'],
        cgroup_oom_unchanged=all(a['cgroup_events'][k]==b['cgroup_events'][k] for k in ['oom','oom_kill']),
        same_device=a['output_filesystem_device']==b['output_filesystem_device'])
    if not all(checks.values()):
        write(attempt/'RESULT.json',dict(status='RESOURCE_HOLD',checks=checks,compiler_starts=0,simulator_starts=0));return 0
    write(attempt/'ADMISSION.json',dict(status='PASS_STRICT_HEAVY_R2_NO_EXCEPTION',checks=checks))
    for path,h in role['source_sha256'].items():assert sha(path)==h,path
    core=Path(reg['core_library']['path']);core_before=core.stat()
    assert sha(core)==reg['core_library']['sha256']
    B.mkdir(exist_ok=False)
    (B/'accelsim_version.h').write_text(reg['version_header'])
    objects=[]
    for r in reg['reused_objects']:
        objects.append(dict(path=r['path'],sha256=sha(r['path']),bytes=Path(r['path']).stat().st_size))
    commands=[]
    for index,argv in enumerate(reg['commands']):
        before=time.monotonic()
        # Explicit compiler/link commands only, no Core make or executable probe.
        with (attempt/('command'+str(index)+'.stdout')).open('xb') as out, (attempt/('command'+str(index)+'.stderr')).open('xb') as err:
            result=subprocess.run(argv,cwd=str(B),stdout=out,stderr=err,timeout=180,check=False)
        commands.append(dict(argv=argv,returncode=result.returncode,elapsed_s=time.monotonic()-before))
        if result.returncode:
            write(attempt/'RESULT.json',dict(status='BUILD_ENGINEERING_FAILURE',commands=commands,simulator_starts=0));return 1
    core_after=core.stat()
    assert (core_before.st_dev,core_before.st_ino,core_before.st_size,core_before.st_mtime_ns,core_before.st_ctime_ns)==(core_after.st_dev,core_after.st_ino,core_after.st_size,core_after.st_mtime_ns,core_after.st_ctime_ns)
    results={name:dict(path=str(B/name),sha256=sha(B/name),bytes=(B/name).stat().st_size)
             for name in ['accel-sim.out','ag7-progress-header-probe']}
    write(attempt/'RESULT.json',dict(status='FRAMEWORK_ONLY_BUILD_PASS_NOT_EXECUTED',commands=commands,
        binaries=results,original_core_library_unchanged=reg['core_library'],reused_main_and_parser_objects=objects,
        Core_compile_starts=0,simulator_starts=0,probe_execution_starts=0,
        host_io_warning_exception=False,utc=datetime.now(timezone.utc).isoformat()))
    print('FRAMEWORK_ONLY_BUILD_PASS_NOT_EXECUTED')
    return 0


if __name__=='__main__':raise SystemExit(main())
