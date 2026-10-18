"""CPU-only fixed-X2 OFF equivalence. Never starts a simulator workload."""
import argparse, hashlib, json, os, re, subprocess
from pathlib import Path
p=argparse.ArgumentParser()
for name in ('build','x2_build','config','raw'):
    p.add_argument('--'+name.replace('_','-'),required=True,type=Path)
a=p.parse_args(); a.raw.mkdir(parents=True,exist_ok=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
env=dict(os.environ); env.pop('LD_PRELOAD',None); env['CUDA_VISIBLE_DEVICES']=''
receipts=[]
def run(exe,args,label,library=None):
    work=a.raw/label; work.mkdir()
    e=dict(env)
    if library: e['LD_LIBRARY_PATH']=str(library.parent.resolve())
    command=[str(exe.resolve()),*args]
    with (work/'stdout').open('w') as out,(work/'stderr').open('w') as err:
        proc=subprocess.run(command,env=e,cwd=work,stdout=out,stderr=err,timeout=60)
    receipts.append(dict(case=label,argv=command,returncode=proc.returncode,
                         executable_sha256=sha(exe),stdout_sha256=sha(work/'stdout'),
                         stderr_sha256=sha(work/'stderr'),
                         library_sha256=sha(library) if library else None))
    assert proc.returncode==0,(label,proc.returncode,(work/'stderr').read_text()[-2000:])
    return (work/'stdout').read_text()
comparisons=[]
for name in ('off','modes'):
    left=run(a.build/('dtc_l1_ad_'+name+'_candidate'),[],name+'_candidate')
    right=run(a.build/('dtc_l1_ad_'+name+'_x2'),[],name+'_x2')
    assert left==right,name
    comparisons.append(dict(case=name,status='BYTE_IDENTICAL',sha256=hashlib.sha256(left.encode()).hexdigest()))
def boundaries(s):
    result=[]; active=None
    for line in s.splitlines(keepends=True):
        if line.startswith('X2_CPU_NORMAL_BOUNDARY_BEGIN '):
            assert active is None; active=[]
        elif line.startswith('X2_CPU_NORMAL_BOUNDARY_END '):
            assert active is not None; result.append(''.join(active)); active=None
        elif active is not None: active.append(line)
    assert active is None and len(result)==3
    return result
cases=[('omitted','events','1'),('0','events','1'),('1','no_event','1'),('1','events','1'),('1','events','8')]
outputs={}
for variant,root in [('candidate',a.build),('x2',a.x2_build)]:
    lib=root/'libcudart.so'; probe=root/'dtc_l1_normal_export_probe'
    for flag,events,topology in cases:
        label='_'.join((variant,flag,events,topology))
        text=run(probe,[str(a.config.resolve()),flag,events,topology],label,lib)
        assert re.findall(r'^X2_CPU_LOADED_LIBRARY path=(.*)$',text,re.M)==[str(lib.resolve())]
        assert 'DTC_PROGRESSIVE_WAKE_V1' not in text
        assert 'print_state_unchanged=1' in text
        outputs[(variant,flag,events,topology)]=boundaries(text)
for flag,events,topology in cases:
    left=outputs[('candidate',flag,events,topology)]; right=outputs[('x2',flag,events,topology)]
    assert left==right,(flag,events,topology)
    for n,part in enumerate(left):
        comparisons.append(dict(flag=flag,events=events,cores_per_cluster=topology,boundary=n,
            status='ALL_PUBLIC_LINES_BYTE_IDENTICAL',sha256=hashlib.sha256(part.encode()).hexdigest()))
assert outputs[('candidate','omitted','events','1')]==outputs[('candidate','0','events','1')]
zero_config=a.raw/'explicit_progressive_zero.config'
zero_config.write_text(a.config.read_text()+'\n-gpgpu_dtc_l1_progressive_wakeup 0\n')
text=run(a.build/'dtc_l1_normal_export_probe',[str(zero_config.resolve()),'1','events','1'],
         'candidate_explicit_progressive_zero',a.build/'libcudart.so')
assert 'DTC_PROGRESSIVE_WAKE_V1' not in text
assert boundaries(text)==outputs[('candidate','1','events','1')]
comparisons.append(dict(case='progressive_omitted_vs_explicit_zero',
                        status='ALL_THREE_PUBLIC_BOUNDARIES_BYTE_IDENTICAL'))
result=dict(status='PASS_CPU_OFF_DIFFERENTIAL_ONLY',processes=receipts,comparisons=comparisons,
    progressive_default_omitted=True,explicit_progressive_zero='actual parser config override 0 compared at all three normal boundaries',
    baseline_library_path=str((a.x2_build/'libcudart.so').resolve()),
    config_sha256=sha(a.config),full_simulators_started=0,GPU_cycle_calls=0,
    scope='deterministic CPU metadata traces and 15 actual normal-print boundaries; no workload/value or universal equivalence proof')
(a.raw/'OFF_DIFFERENTIAL.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],processes=len(receipts),comparisons=len(comparisons))))
