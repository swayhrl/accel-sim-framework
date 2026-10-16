"""Relink retained production test objects with the isolated physical-clock fix."""
from pathlib import Path
import shlex
import subprocess
from registry import Registry, write_json
from run import digest


def main():
    root = Path('/workspace/results/ep_l2_ft20261016/lane5_memcpy_clock_probe_fixed_r1')
    out = root/'regression'
    out.mkdir(exist_ok=False)
    build = Path('/workspace/build/ep-l2-ft20261016-lane1-v1/gpgpu-sim')
    core = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane1-v1')
    reg = Registry()
    lease = reg.build_lease('lane5',cpu=1,memory=4*1024**3)
    report = {'status':'INCOMPLETE','tests':[],'fixed_cache_object_sha256':digest(root/'fixed-cache.o'),
              'runner_source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    try:
        for name in ['ep_l2_ft_directed','ep_l2_ft_partition']:
            command = shlex.split((build/f'CMakeFiles/{name}.dir/link.txt').read_text())
            command[command.index('-o')+1] = str(out/name)
            command.insert(command.index('-Wl,--start-group'),str(root/'fixed-cache.o'))
            subprocess.run(command,cwd=build,check=True,capture_output=True,timeout=120)
        base = str(core/'configs/tested-cfgs/SM7_QV100/gpgpusim.config')
        config = str(core/'tests/ep_l2/ft_wbuf.config')
        cases=[('directed',[str(out/'ep_l2_ft_directed'),base,config])]
        cases += [(f'partition_{m}_{c}',[str(out/'ep_l2_ft_partition'),base,config,str(m),str(c)])
                  for m in (1,2) for c in (8,16)]
        for name,command in cases:
            log=out/(name+'.log')
            with log.open('x') as stream:
                result=subprocess.run(command,cwd=out,stdout=stream,stderr=subprocess.STDOUT,timeout=120)
            row={'case':name,'command':command,'exit_code':result.returncode,
                 'binary_sha256':digest(command[0]),'log':str(log),'log_sha256':digest(log)}
            report['tests'].append(row)
            print(name,result.returncode,flush=True)
        report['status']='PASS' if all(r['exit_code']==0 for r in report['tests']) else 'FAILED_REVIEW_LOGS'
    finally:
        reg.release_build(lease,'lane5')
        write_json(out/'REGRESSION.json',report)


if __name__=='__main__':
    main()
