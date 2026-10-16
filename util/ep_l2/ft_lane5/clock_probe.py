"""Link a new observation-only test against retained R0 archives, never rebuild R0."""
import os
from pathlib import Path
import shlex
import subprocess
from registry import Registry, write_json
from run import digest


def main():
    core = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane5-v1')
    original = '/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane1-v1'
    build = Path('/workspace/build/ep-l2-ft20261016-lane1-v1/gpgpu-sim')
    out = Path('/workspace/results/ep_l2_ft20261016/lane5_memcpy_clock_probe_r1')
    out.mkdir(exist_ok=False)
    reg = Registry()
    lease = reg.build_lease('lane5', cpu=1, memory=4 * 1024**3)
    report = {'status': 'INCOMPLETE', 'lease': lease, 'tests': [],
        'core_test_source_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=core,text=True).strip(),
        'framework_probe_source_commit': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    try:
        assert digest(build.parent / 'accel-sim.out') == '0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698'
        flags = (build / 'CMakeFiles/ep_l2_ft_partition.dir/flags.make').read_text()
        options = []
        for line in flags.splitlines():
            if line.startswith(('CXX_DEFINES =', 'CXX_INCLUDES =', 'CXX_FLAGS =')):
                options += shlex.split(line.split('=',1)[1].replace(original,str(core)))
        command = ['/usr/bin/c++', *options, '-c', str(core/'tests/ep_l2/test_ft_memcpy_clock.cc'), '-o',str(out/'probe.o')]
        report['compile_command'] = command
        with (out/'compile.log').open('x') as log:
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        link = shlex.split((build/'CMakeFiles/ep_l2_ft_partition.dir/link.txt').read_text())
        archives = []
        for i, arg in enumerate(link):
            if arg.endswith('.cc.o'): link[i] = str(out/'probe.o')
            if arg == '-o': link[i+1] = str(out/'clock-probe.out')
            if arg.endswith('.a'):
                path = build/arg
                archives.append({'path':str(path),'sha256':digest(path)})
        report['link_command'] = link
        report['retained_R0_archives'] = archives
        with (out/'link.log').open('x') as log:
            subprocess.run(link,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        report['probe_binary_sha256'] = digest(out/'clock-probe.out')
        configs = [core/'configs/tested-cfgs/SM7_QV100/gpgpusim.config',core/'tests/ep_l2/ft_wbuf.config']
        report['configs'] = [{'path':str(p),'sha256':digest(p)} for p in configs]
        for mode in (1,2):
            for offset in (0,4096):
                command = [str(out/'clock-probe.out'), *map(str,configs),str(mode),'16',str(offset)]
                log = out/f'mode{mode}_offset{offset}.log'
                with log.open('x') as stream:
                    result = subprocess.run(command,cwd=out,stdout=stream,stderr=subprocess.STDOUT,timeout=120,
                        env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'))
                report['tests'].append({'mode':mode,'offset':offset,'command':command,'exit_code':result.returncode,
                    'log':str(log),'log_sha256':digest(log),
                    'audit_lines':[s for s in log.read_text().splitlines() if s.startswith(('CLOCK_','FT real'))]})
                print(mode,offset,result.returncode,report['tests'][-1]['audit_lines'],flush=True)
        assert all(digest(a['path'])==a['sha256'] for a in archives)
        report['status'] = 'PROBE_EXECUTED_REVIEW_OBSERVATIONS'
    finally:
        reg.release_build(lease,'lane5')
        write_json(out/'CLOCK_PROBE.json',report)


if __name__ == '__main__':
    main()
