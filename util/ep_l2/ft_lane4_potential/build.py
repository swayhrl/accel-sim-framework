"""One isolated, leased Lane4 module build. No full application launches."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def head(path):return subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--core',type=Path,required=True);p.add_argument('--build',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--targets',nargs='+',required=True)
    a=p.parse_args();fw=Path(__file__).resolve().parents[3]
    a.out.mkdir(parents=True,exist_ok=False)
    client_path=Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json')
    client=json.loads(client_path.read_text());path=Path(client['registry_client'])
    assert sha(path)==client['registry_client_sha256'],'current registry hash mismatch'
    spec=importlib.util.spec_from_file_location('lane4_build_registry',path)
    api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
    registry=api.Registry(client['canonical_root'])
    report=dict(status='PREFLIGHT',core_source_commit=head(a.core),framework_source_commit=head(fw),
        driver_sha256=sha(__file__),client_contract_sha256=sha(client_path),registry_sha256=sha(path),
        core=str(a.core),build=str(a.build),out=str(a.out),targets=a.targets,commands=[],full_application_starts=0)
    def save():(a.out/'BUILD_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n')
    def resources():
        live=api.local_resources();share=os.statvfs('/root/share')
        assert live['disk_free_bytes']>=48*1024**3,'workspace floor crossed'
        assert live['available_memory_bytes']>=64*1024**3,'RAM floor crossed'
        assert share.f_bavail*share.f_frsize>=40*1024**3,'Share floor crossed'
        return live
    lease=None
    try:
        for tree in [a.core,fw]:
            assert not subprocess.check_output(['git','-C',str(tree),'status','--porcelain','--untracked-files=no'])
        vendor=fw/'gpu-simulator/extern/pybind11'
        report['vendor_commit']=head(vendor)
        assert report['vendor_commit']=='f90c430c3a1ce8f08c09942a5a1c3a797bb2295b'
        assert not a.build.exists(),'immutable new build directory required'
        live=resources();report['resources_before']=live
        assert live['disk_free_bytes']>=50*1024**3,'build growth margin'
        lease=registry.build_lease('lane4',cpu=2,memory=8*1024**3)
        report['lease_id']=lease;resources();save()
        env=dict(os.environ,GPGPUSIM_ROOT=str(a.core),CUDA_INSTALL_PATH='/usr/local/cuda-11.8',
            ACCELSIM_CONFIG='release',PATH='/usr/local/cuda-11.8/bin:'+os.environ['PATH'],
            OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
        def run(name,cmd):
            row=dict(name=name,command=cmd,log=str(a.out/(name+'.log')));report['commands'].append(row);save()
            proc=None;start=time.monotonic()
            try:
                with Path(row['log']).open('x') as log:
                    proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
                    row['process']=api.process_identity(proc.pid);save()
                    while proc.poll() is None:
                        resources()
                        assert time.monotonic()-start<1800,'owned build timeout'
                        time.sleep(1)
                row['exit_code']=proc.returncode;row['log_sha256']=sha(row['log']);save()
                assert proc.returncode==0,name+' failed'
            finally:
                if proc is not None and proc.poll() is None:
                    os.killpg(proc.pid,signal.SIGTERM)
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
        report['status']='BUILDING';save()
        run('configure',['cmake','-S',str(fw/'gpu-simulator'),'-B',str(a.build),'-G','Unix Makefiles','-DCUDAToolkit_ROOT=/usr/local/cuda-11.8'])
        run('compile',['cmake','--build',str(a.build),'--target',*a.targets,'-j2'])
        assert head(a.core)==report['core_source_commit'] and head(fw)==report['framework_source_commit']
        report['binary_sha256']=sha(a.build/'accel-sim.out') if (a.build/'accel-sim.out').exists() else None
        report['status']='BUILT_NOT_INDEPENDENTLY_QUALIFIED'
    except BaseException as error:
        report.update(status='FAILED_OR_RESOURCE_HOLD',error=repr(error));raise
    finally:
        if lease is not None:registry.release_build(lease,'lane4')
        save()


if __name__=='__main__':main()
