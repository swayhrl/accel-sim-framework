from common import *
from event_snapshots import snapshot as decode,fixture_snapshots,QualificationError
import re

def main():
    run=ROOT/'normal-export-cpu/independent_v1';supp=run/'independent_old_compare';supp.mkdir()
    oldlib=Path('/workspace/builds/dtc-lane-x2-baseline-fresh-174-v1/libcudart.so');assert sha(oldlib)=='e94c2e247a602ce019219593d2834ff68155e960abacd386e29e619b07aa2aa3'
    src=Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-y2-source-c0a5e2c3');assert git(src,'rev-parse','HEAD')==CANDIDATE_CORE and not git(src,'status','--porcelain','--untracked-files=no')
    exe=supp/'reference_cpu_fixture';cmd=['/usr/bin/g++','-std=c++17','-fno-access-control','-UNDEBUG','-DY2_HAS_K1=1','-DCUDART_VERSION=11080','-I'+str(src/'src'),'-I'+str(src/'libcuda'),'-I/usr/local/cuda-11.8/include',str(PACK/'scripts/normal_export_fixture.cc'),'-L'+str(oldlib.parent),'-Wl,-rpath,'+str(oldlib.parent),'-lcudart','-ldl','-o',str(exe)]
    env={'PATH':'/usr/bin:/bin','LANG':'C','LD_LIBRARY_PATH':str(oldlib.parent)}
    receipts=[]
    def call(args,label):
        r=subprocess.run(args,env=env,cwd=supp,capture_output=True,text=True,timeout=180)
        for k in ['stdout','stderr']:(supp/(label+'.'+k)).write_text(getattr(r,k))
        receipts.append(dict(label=label,argv=args,returncode=r.returncode,stdout_sha256=sha(supp/(label+'.stdout')),stderr_sha256=sha(supp/(label+'.stderr'))));assert r.returncode==0,r.stderr[-1000:];return r.stdout
    call(cmd,'compile_old')
    def bodies(text):return [(m[1],m[3]) for m in re.finditer(r'^AA5_EXPORT_SNAPSHOT_BEGIN label=(\S+) expected_cycle=(\d+)\n(.*?)^AA5_EXPORT_SNAPSHOT_END label=\1\s*$',text,re.M|re.S)]
    def normalize(body):
        body=re.sub(r'^DTC_INVALIDATE_V1_SNAPSHOT_BEGIN .*?^DTC_INVALIDATE_V1_SNAPSHOT_END[^\n]*\n?','',body,flags=re.M|re.S)
        return '\n'.join(l for l in body.splitlines() if not re.match(r'^(AA5_NORMAL_ENTRY_LIBRARY |gpu_total_sim_rate|gpgpu_simulation_time|gpgpu_simulation_rate|gpgpu_silicon_slowdown)',l))
    comparisons=[]
    for name,K in [('off',0),('on',1)]:
        old=call([str(exe),str(PACK/'inputs/CPU_EXPORT_FIXTURE_BASE.config'),K_OPTION,str(K)],name)
        loaded=re.findall(r'^Y2_LIBRARY (.*)$',old,re.M);assert len(loaded)==1 and Path(loaded[0]).resolve()==oldlib
        new=(run/(name+'.stdout')).read_text();a=bodies(old);b=bodies(new);assert len(a)==len(b)==4
        for (la,ba),(lb,bb) in zip(a,b):
            assert la==lb
            x,y=normalize(ba),normalize(bb)
            if x!=y:
                (supp/(name+'_'+la+'_old_public.txt')).write_text(x);(supp/(name+'_'+la+'_new_public.txt')).write_text(y)
                raise AssertionError(name+' '+la+' PUBLIC_OUTPUT_CHANGED')
            comparisons.append(dict(case=name,label=la,status='PASS_PUBLIC_BYTE_IDENTICAL_AFTER_ONLY_NEW_FRAME_AND_DECLARED_HOST_IDENTITY_FIELDS_REMOVED',sha256=hashlib.sha256(x.encode()).hexdigest()))
        if K:
            try:fixture_snapshots(old,1)
            except QualificationError:pass
            else:raise AssertionError('old c0 unexpectedly qualified as new normal export')
    text=(run/'on.stdout').read_text();body=dict(bodies(text))['terminal43'];negatives=[]
    def reject(name,value,K=1):
        try:decode(value,K,43)
        except QualificationError as e:negatives.append(dict(case=name,rejected=True,reason=str(e)));return
        raise AssertionError(name+' accepted')
    reject('missing_frame_begin',body.replace('DTC_INVALIDATE_V1_SNAPSHOT_BEGIN','PRIVATE_BEGIN',1));reject('missing_frame_end',body.replace('DTC_INVALIDATE_V1_SNAPSHOT_END','PRIVATE_END',1));reject('frame_cycle_disagrees_public',body.replace('sms=64 cycle=43','sms=64 cycle=42',1));reject('frame_claims_63SM',body.replace('sms=64','sms=63',1));reject('bad_frame_sentinel',body.replace('no_event_cycle_sentinel=18446744073709551615','no_event_cycle_sentinel=0',1));reject('K0_unexpected_export',body,0);reject('missing_public_cycle',re.sub(r'^gpu_tot_sim_cycle[^\n]*\n','',body,flags=re.M))
    receipt=PACK/'normal_export_gate_receipts/independent_v1/NORMAL_TERMINAL_EXPORT_GATE.json';gate=json.loads(receipt.read_text());assert gate['status']=='PASS_NORMAL_TERMINAL_EXPORT_GATE'
    gate['independent_old_Core_public_comparisons']=comparisons;gate['additional_actual_frame_negatives']=negatives;gate['old_comparison_receipts']=receipts;gate['old_reference_library_sha256']=sha(oldlib);gate['scope']='INDEPENDENT_REAL_PRODUCTION_NORMAL_ENTRY_EXPORT_AND_PUBLIC_NONMUTATION; BOUNDED_CPU_FIXTURE_NOT_GAUSSIAN_PERFORMANCE'
    write(PACK/'NORMAL_TERMINAL_EXPORT_GATE.json',gate)
    print('PASS: actual X2 normal output, real64SM, independent old/new public byte comparisons8, rejecting actual frame negatives7; no full simulations.')

if __name__=='__main__':main()
