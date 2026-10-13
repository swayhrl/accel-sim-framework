#!/bin/bash
set -euo pipefail
bash "$TASK_DATA/environment_steps.sh"
export MAX_JOBS=8 CMAKE_BUILD_PARALLEL_LEVEL=8 OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
export CUDA_HOME=/usr/local/cuda-12.6 PATH="$TASK_DATA/venv/bin:/usr/local/cuda-12.6/bin:$PATH"
export TORCH_EXTENSIONS_DIR="$TASK_DATA/cache/torch_extensions" TORCHINDUCTOR_CACHE_DIR="$TASK_DATA/cache/torchinductor" WARP_CACHE_PATH="$TASK_DATA/cache/warp" XDG_CACHE_HOME="$TASK_DATA/cache/xdg" NEQUIP_CACHE_DIR="$TASK_DATA/cache/nequip" TMPDIR="$TASK_DATA/cache/tmp"
python tools/ai_workload_research/nequip_static_batch_v1/observe.py compiled_canary > "$TASK_DATA/raw/compiled_canary.log" 2>&1
# Freeze software, data, product, and prerequisite evidence before formal observation.
git add tools/ai_workload_research/nequip_static_batch_v1
git commit -m 'feat(ai-arch): freeze V1 static-batch observation runner'
python - <<'PY2'
import pathlib,json,os,hashlib,subprocess,importlib.metadata as m,datetime
p=pathlib.Path(os.environ['TASK_DATA'])
def sh(f):return hashlib.sha256(f.read_bytes()).hexdigest()
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runner_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'runner_tree':subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip(),'starting_commit':'cb1081328303f2655cbf1a3f3042cc01abe83b2c','compiled_sha256':sh(p/'OAM-S.nequip.pt2'),'model_sha256':sh(p/'inputs/NequIP-OAM-S-0.1.nequip.zip'),'input_sha256':sh(p/'inputs/sitraj.xyz'),'files':{str(f):sh(f) for f in pathlib.Path('tools/ai_workload_research/nequip_static_batch_v1').glob('*') if f.is_file()},'installed_distributions':{d.metadata['Name']:d.version for d in m.distributions()},'qualification_receipts':{f.name:sh(f) for f in (p/'raw').glob('*checks.json')},'conditions':['N-C2','N-G2','N-G4','N-G8'],'observation_limit_seconds':900}
(p/'raw/FROZEN_EXPERIMENT_MANIFEST.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
PY2
# One shared 15-minute deadline covers all three fresh formal processes and diagnostics.
python - <<'PY2'
import subprocess,os,time,json,pathlib,datetime
p=pathlib.Path(os.environ['TASK_DATA']);start=time.monotonic();receipt={'utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'limit_seconds':900,'processes':[]}
try:
 for i in range(3):
  remaining=900-(time.monotonic()-start)
  if remaining<=0:raise TimeoutError('BUDGET_STOP_FORMAL_15MIN')
  with (p/'raw'/f'formal_process_{i}.log').open('w') as log:
   r=subprocess.run([str(p/'venv/bin/python'),'tools/ai_workload_research/nequip_static_batch_v1/observe.py','formal',str(i)],stdout=log,stderr=subprocess.STDOUT,timeout=remaining)
  receipt['processes'].append({'id':i,'returncode':r.returncode})
  if r.returncode:raise RuntimeError(f'formal process {i} stopped')
 receipt['status']='PASS'
except Exception as e:
 receipt.update(status='STOP',error=str(e));raise
finally:
 receipt['seconds']=time.monotonic()-start;(p/'raw/formal_phase_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
PY2
