#!/usr/bin/env python3
"""One leased, bounded tiny C++ build/run. Not the RO production19 or an app."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import subprocess
import sys


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def limits():
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024**2,32*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(60,60))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--core',type=Path,required=True);p.add_argument('--source',required=True)
    p.add_argument('--store-source');p.add_argument('--runtime-source');p.add_argument('--output',type=Path,required=True)
    p.add_argument('--expect-a2',type=int,default=0);p.add_argument('--expect-a3',type=int,default=0)
    p.add_argument('--controls',action='store_true');a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);out=a.output.resolve()
    contract_path=Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json');contract=json.loads(contract_path.read_text())
    client=Path(contract['registry_client']);assert sha(client)==contract['registry_client_sha256']
    spec=importlib.util.spec_from_file_location('lane5_central_registry',client);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    registry=module.Registry();pre=module.local_resources();assert pre['disk_free_bytes']>=50*1024**3
    def output_space():
        st=os.statvfs(out);minimum=(50 if os.stat(out).st_dev==os.stat('/workspace').st_dev else 42)*1024**3
        available=st.f_bavail*st.f_frsize;assert available>=minimum
        return {'path':str(out),'available_bytes':available,'required_bytes':minimum,'scope':'workspace50GiB or existing Share40GiB protection plus2GiB growth'}
    output_before=output_space()
    snap=registry.snapshot();active={k:r for k,r in snap.get('resource_leases',{}).items() if r['status'] in module.ACTIVE}
    assert not any(r['owner']=='lane1' for r in active.values()),'Yield to an already active official producer'
    lease=registry.build_lease('lane3',cpu=1,memory=2*1024**3)
    receipt={'schema':'LANE3_TINY_RO_BANK_CPP_RUN_R16','started_at':now(),'source':a.source,
      'store_source':a.store_source or a.source,'runtime_source':a.runtime_source or a.source,
      'registry_client_sha256':sha(client),'lease':lease,'cpu_units':1,'reserved_memory_bytes':2*1024**3,
      'resources_before':pre,'compile_attempts':0,'runs':[],'status':'STARTED','scope':'SOURCE_BOUND_CPP_NOT_FULL_CACHE_PRODUCTION_OR_SCIENTIFIC_QUALIFICATION'}
    try:
        after=module.local_resources();assert after['disk_free_bytes']>=50*1024**3
        assert after['available_memory_bytes']-2*1024**3>=64*1024**3
        receipt['resources_after_lease']=after
        receipt['output_filesystem_before']=output_before
        receipt['output_filesystem_after_lease']=output_space()
        gen=[sys.executable,str(a.core/'tests/ep_l2/prepare_ro_bank_progress.py'),'--source',a.source,'--output',str(out/'inputs')]
        for flag,value in [('--store-source',a.store_source),('--runtime-source',a.runtime_source)]:
            if value:gen += [flag,value]
        subprocess.run(gen,check=True,timeout=30)
        receipt['source_binding_sha256']=sha(out/'inputs/SOURCE_BINDING.json')
        cmd=['g++','-std=c++11','-O0','-g','-Wall','-Wextra','-Wno-unused-parameter',
             '-ffunction-sections','-fdata-sections','-fsanitize=undefined','-fno-sanitize-recover=all',
             '-I'+str(out/'inputs'),'-I'+str(a.core/'src/gpgpu-sim'),'-I'+str(a.core/'src'),'-I'+str(a.core),
             '-I/usr/local/cuda-11.8/include','-MMD','-MF',str(out/'DEPENDENCIES.d'),
             str(out/'inputs/test_ro_bank_progress.cc'),'-Wl,--gc-sections','-o',str(out/'ro_bank_progress')]
        receipt['compile_command']=cmd;receipt['compile_attempts']=1
        receipt['compiler_version']=subprocess.check_output(['g++','--version'],text=True,timeout=10).splitlines()[0]
        with (out/'BUILD.log').open('x') as f:
            r=subprocess.run(['/usr/bin/time','-v','-o',str(out/'BUILD_TIME.txt')]+cmd,stdout=f,stderr=subprocess.STDOUT,timeout=75,preexec_fn=limits)
        receipt['compile_exit']=r.returncode
        if r.returncode:raise RuntimeError('tiny fixture compile failed; see BUILD.log')
        receipt['binary_sha256']=sha(out/'ro_bank_progress')
        for case,expected in [('a2',a.expect_a2),('a3',a.expect_a3)]+([('controls',0)] if a.controls else []):
            for entries in [8,16]:
                command=[str(out/'ro_bank_progress'),case,str(entries)];log=out/f'{case}_C{entries}.log'
                with log.open('x') as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=10,preexec_fn=limits)
                row={'case':case,'entries':entries,'command':command,'expected_exit':expected,'actual_exit':r.returncode,'log_sha256':sha(log)}
                row['status']='PASS' if r.returncode==expected else 'FAIL'
                receipt['runs'].append(row)
                if r.returncode!=expected:raise RuntimeError('unexpected '+case+' C'+str(entries)+' exit '+str(r.returncode))
        receipt['status']='EXPECTED_MATRIX_PASS_NOT_PRODUCTION_QUALIFICATION'
    except BaseException as error:
        receipt['status']='FAILED_ATTEMPT_RETAINED';receipt['error']=str(error);raise
    finally:
        registry.release_build(lease,'lane3');receipt['lease_released']=True;receipt['finished_at']=now()
        receipt['resources_after']=module.local_resources()
        (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps({'status':receipt['status'],'lease':lease,'released':True,'compile_exit':receipt.get('compile_exit'),'runs':receipt['runs']},indent=2),flush=True)


if __name__=='__main__':main()
