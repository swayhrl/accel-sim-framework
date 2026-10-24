#!/usr/bin/env python3
import urllib.request,json,pathlib,hashlib,tarfile,time
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1')
P=R/'toolchains/cuda11.8';P.mkdir(parents=True,exist_ok=False)
C=R/'toolchains/packages';C.mkdir(parents=True,exist_ok=True)
receipt=[]
for pkg in ['cuda-nvcc','cuda-cudart-dev','cuda-cudart','cuda-cudart-static','cuda-driver-dev']:
 d=json.load(urllib.request.urlopen('https://api.anaconda.org/package/nvidia/'+pkg,timeout=30))
 f=[x for x in d['files'] if x.get('version','').startswith('11.8') and x.get('attrs',{}).get('subdir')=='linux-64']
 assert f,pkg
 x=f[-1];url='https://conda.anaconda.org/nvidia/'+x['basename'];a=C/pathlib.Path(x['basename']).name
 with urllib.request.urlopen(url,timeout=90) as src,a.open('xb') as out:
  while True:
   chunk=src.read(1048576)
   if not chunk:break
   out.write(chunk)
 b=a.read_bytes();assert len(b)==x['size'];actual=hashlib.md5(b).hexdigest()
 expected=x.get('md5') or x.get('attrs',{}).get('md5')
 if expected:assert actual==expected,(pkg,actual,expected)
 with tarfile.open(a) as t:
  members=[m for m in t.getmembers() if not m.name.startswith('info/')]
  for m in members:assert not pathlib.PurePosixPath(m.name).is_absolute() and '..' not in pathlib.PurePosixPath(m.name).parts
  t.extractall(P,members=members)
 receipt.append({'package':pkg,'metadata':x,'download_url':url,'path':str(a),'sha256':hashlib.sha256(b).hexdigest(),'md5_verified':bool(expected),'prefix':str(P)})
 (R/'control/CUDA11_8_INSTALL_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(pkg,len(b),'installed',flush=True)

