from pathlib import Path
import subprocess,json,hashlib,os
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');D=R/'toolchains/gl_debs';P=R/'toolchains/gl';D.mkdir(parents=True,exist_ok=False);P.mkdir(exist_ok=False);rows=[]
for pkg in ['libglut-dev','freeglut3-dev','libglew-dev','libx11-dev','libxext-dev','libxmu-dev','libxi-dev','libxfixes-dev','libxrandr-dev','x11proto-dev','libxau-dev','libxdmcp-dev','libxcb1-dev','libglut3.12','libglew2.2']:
 cp=subprocess.run(['apt-get','download',pkg],cwd=D,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90);rows.append({'package':pkg,'exit':cp.returncode,'log':cp.stdout});print(pkg,cp.returncode,flush=True)
for f in sorted(D.glob('*.deb')):
 cp=subprocess.run(['dpkg-deb','-x',str(f),str(P)],capture_output=True,text=True);assert cp.returncode==0
 rows.append({'deb':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
(R/'manifests/PRIVATE_GRAPHICS_DEPS.json').write_text(json.dumps(rows,indent=2)+'\n')
