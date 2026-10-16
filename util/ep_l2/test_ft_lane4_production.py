#!/usr/bin/env python3
"""Compile real Core tests against the pinned isolated CMake libraries."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--core',type=Path,required=True)
    p.add_argument('--build',type=Path,required=True)
    p.add_argument('--build-manifest',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads(a.build_manifest.read_text())
    subprocess.run(['git','-C',str(a.core),'diff','--exit-code',manifest['core_source_commit'],
                    'HEAD','--','src','libcuda','libopencl'],check=True)
    client=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
    sys.path.insert(0,str(Path(client['registry_client']).parent))
    from registry import Registry
    reg=Registry(client['canonical_root']);lease=reg.build_lease('lane4',cpu=1,memory=2*1024**3)
    libs=[]
    for x in shlex.split((a.build/'CMakeFiles/accel-sim.out.dir/link.txt').read_text()):
        if x.endswith('.a') and x not in libs and not x.startswith(('trace-driven/','trace-parser/')):libs.append(x)
    cases={'test_ideal_read_hit':['ideal_read_hit.config'],
           'test_ideal_meta_integrated':['ideal_meta_integrated.config'],
           'test_ideal_meta':[],
           'test_descriptor_mshr_integrated':['integrated.config','integrated_exhaustion.config','integrated_stats_off.config','integrated_banked.config'],
           'test_wad':['wad.config']}
    rows=[]
    try:
        for name,configs in cases.items():
            source=a.core/'tests/ep_l2'/f'{name}.cc';exe=a.out/name
            command=['g++','-std=c++17','-O2','-I/usr/local/cuda-11.8/include',
                     '-I'+str(a.core/'src'),'-I'+str(a.core),str(source),'-Wl,--start-group',
                     *[str(a.build/x) for x in libs],'-Wl,--end-group','-lz','-lpthread','-ldl',
                     '-lssl','-lcrypto','-lGL','-o',str(exe)]
            row={'test':name,'compile_command':command,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
            with (a.out/f'{name}_compile.log').open('w') as log:
                result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
            row['compile_returncode']=result.returncode
            if result.returncode:rows.append(row);break
            args=[str(exe)]
            if configs:args += [str(a.core/'configs/tested-cfgs/SM7_QV100/gpgpusim.config'),
                                *[str(a.core/'tests/ep_l2'/c) for c in configs]]
            row['run_command']=args
            with (a.out/f'{name}.log').open('w') as log:
                result=subprocess.run(args,cwd=a.out,stdout=log,stderr=subprocess.STDOUT,timeout=180)
            row['returncode']=result.returncode;rows.append(row)
            print(name,result.returncode,flush=True)
            if result.returncode:break
    finally:
        reg.release_build(lease,'lane4')
        output={'core_test_commit':subprocess.check_output(['git','-C',str(a.core),'rev-parse','HEAD'],text=True).strip(),
                'compiled_production_manifest':manifest,'lane5_client':client,'tests':rows}
        (a.out/'TEST_MANIFEST.json').write_text(json.dumps(output,indent=2)+'\n')
    if len(rows)!=len(cases) or any(r.get('returncode')!=0 for r in rows):raise SystemExit(1)


if __name__=='__main__':main()
