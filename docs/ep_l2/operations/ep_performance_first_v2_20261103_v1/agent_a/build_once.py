from pathlib import Path
import subprocess,os,time,json
A=Path(__file__).resolve().parent
env=dict(os.environ,GPGPUSIM_ROOT=str(A/'core_candidate'),CUDA_INSTALL_PATH='/root/data/dtc_main_20261023_v1/ae_fair_v1/toolchain',CUDA_VISIBLE_DEVICES='',ACCELSIM_CONFIG='release')
t=time.time()
with (A/'BUILD.stdout').open('w') as o,(A/'BUILD.stderr').open('w') as e:
 p=subprocess.run(['cmake','--build',str(A/'build'),'--parallel','2'],env=env,stdout=o,stderr=e,timeout=2400)
(A/'BUILD_RESULT.json').write_text(json.dumps({'returncode':p.returncode,'seconds':time.time()-t,'model_starts':0,'source':'independent CLEAN cap candidate','parallelism':2},indent=2)+'\n')
