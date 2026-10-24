from pathlib import Path
import subprocess,time,json
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');pid=381509;expected='344275422';start=time.monotonic()
while True:
 p=Path('/proc')/str(pid)/'stat'
 if p.exists():
  actual=p.read_text().split(') ',1)[1].split()[19]
  if actual!=expected:break
  if time.monotonic()-start>7200:raise RuntimeError('FINITE_CUDA104_WAIT_TIMEOUT_2H')
  time.sleep(10)
 else:break
marker=R/'native_control/COMPLETE_cuda104_v1.json'
if not marker.exists():raise RuntimeError('PRIOR_CUDA104_TERMINAL_WITHOUT_COMPLETE_NO_RESTART')
assert json.loads(marker.read_text())['tasks']==104
cmd=['/usr/bin/python3','-B',str(R/'build/run_cuda_native_v1.py'),str(R/'manifests/SDK42_REMAINING_DEFAULTS_45_QUEUE_V1.json'),'sdk42_defaults45_v1']
subprocess.run(cmd,check=True)
