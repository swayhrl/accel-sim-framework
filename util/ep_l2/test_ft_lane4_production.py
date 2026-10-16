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
    p.add_argument('--include-b16',action='store_true')
    p.add_argument('--include-partition',action='store_true')
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
    if a.include_b16:
        cases.update(test_ideal_wb=['ft_wbuf.config'],test_ft_wbuf=['ft_wbuf.config'])
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
        if a.include_b16 and len(rows)==len(cases) and all(r.get('returncode')==0 for r in rows):
            # The same read-service producer test also runs above real finite
            # WBUF16: its stores use the new allocation/copy/pin implementation.
            source_config=a.core/'tests/ep_l2/ideal_read_hit.config'
            overlay=a.out/'ideal_read_hit_b16.config'
            overlay.write_text(source_config.read_text()+'\n-gpgpu_ep_l2_ft_mode 1\n-gpgpu_ep_l2_wbuf_entries 16\n')
            args=[str(a.out/'test_ideal_read_hit'),str(a.core/'configs/tested-cfgs/SM7_QV100/gpgpusim.config'),str(overlay)]
            with (a.out/'test_ideal_read_hit_b16.log').open('w') as log:
                result=subprocess.run(args,cwd=a.out,stdout=log,stderr=subprocess.STDOUT,timeout=180)
            rows.append({'test':'test_ideal_read_hit_b16','run_command':args,'returncode':result.returncode})
            print('test_ideal_read_hit_b16',result.returncode,flush=True)
        if a.include_partition and all(r.get('returncode')==0 for r in rows):
            source=a.core/'tests/ep_l2/test_ft_partition.cc';exe=a.out/'test_ft_partition'
            command=['g++','-std=c++17','-O2','-I/usr/local/cuda-11.8/include','-I'+str(a.core/'src'),'-I'+str(a.core),str(source),'-Wl,--start-group',*[str(a.build/x) for x in libs],'-Wl,--end-group','-lz','-lpthread','-ldl','-lssl','-lcrypto','-lGL','-o',str(exe)]
            with (a.out/'test_ft_partition_compile.log').open('w') as log:
                subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
            for mode,c in [(1,8),(1,16),(2,8),(2,16)]:
                args=[str(exe),str(a.core/'configs/tested-cfgs/SM7_QV100/gpgpusim.config'),str(a.core/'tests/ep_l2/ft_wbuf.config'),str(mode),str(c)]
                name=f'test_ft_partition_m{mode}_c{c}'
                with (a.out/(name+'.log')).open('w') as log:
                    result=subprocess.run(args,cwd=a.out,stdout=log,stderr=subprocess.STDOUT,timeout=180)
                rows.append({'test':name,'compile_command':command,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'run_command':args,'returncode':result.returncode})
                print(name,result.returncode,flush=True)
    finally:
        reg.release_build(lease,'lane4')
        output={'core_test_commit':subprocess.check_output(['git','-C',str(a.core),'rev-parse','HEAD'],text=True).strip(),
                'compiled_production_manifest':manifest,'lane5_client':client,'tests':rows}
        (a.out/'TEST_MANIFEST.json').write_text(json.dumps(output,indent=2)+'\n')
    if len(rows)!=len(cases)+int(a.include_b16)+4*int(a.include_partition) or any(r.get('returncode')!=0 for r in rows):raise SystemExit(1)


if __name__=='__main__':main()
