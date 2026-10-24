from pathlib import Path
import subprocess,json,hashlib
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');D=R/'toolchains/mpi_debs';P=R/'toolchains/mpi';D.mkdir(exist_ok=False);P.mkdir(exist_ok=False);rows=[]
for pkg in ['libopenmpi-dev','libopenmpi3t64','openmpi-bin','openmpi-common','libpmix2t64','libhwloc15','libevent-pthreads-2.1-7t64','libevent-core-2.1-7t64','libibverbs1','libfabric1','libucx0','libpsm2-2','libnl-3-200','libnl-route-3-200']:
 cp=subprocess.run(['apt-get','download',pkg],cwd=D,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90);rows.append({'package':pkg,'exit':cp.returncode,'log':cp.stdout});print(pkg,cp.returncode,flush=True)
for f in sorted(D.glob('*.deb')):
 cp=subprocess.run(['dpkg-deb','-x',str(f),str(P)],capture_output=True,text=True);assert cp.returncode==0;rows.append({'deb':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
(R/'manifests/PRIVATE_MPI_DEPS.json').write_text(json.dumps(rows,indent=2)+'\n')
