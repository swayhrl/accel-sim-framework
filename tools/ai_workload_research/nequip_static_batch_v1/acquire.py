import urllib.request,pathlib,os,hashlib,json,zipfile,tarfile,time,subprocess
root=pathlib.Path(os.environ['TASK_DATA']); records=[]
files=[('model','https://zenodo.org/records/18775904/files/NequIP-OAM-S-0.1.nequip.zip?download=1','inputs/NequIP-OAM-S-0.1.nequip.zip',12*2**20),('input','https://raw.githubusercontent.com/mir-group/nequip-tutorial/8f90935ba42fd9e03df323cf03428c456d87b881/sitraj.xyz','inputs/sitraj.xyz',12*2**20),('nequip','https://codeload.github.com/mir-group/nequip/tar.gz/27d9d2182da918ab7be0017d8300e53278f5e00e','sources/nequip.tar.gz',256*2**20),('oeq','https://codeload.github.com/PASSIONLab/OpenEquivariance/tar.gz/62aacc47557e9cdfc6dd370f410b684be1ee0a3f','sources/oeq.tar.gz',256*2**20),('alchemi','https://codeload.github.com/NVIDIA/nvalchemi-toolkit-ops/tar.gz/32445c5f00e83fccd475589f1a6f5ac9e81e6b02','sources/alchemi.tar.gz',256*2**20)]
try:
 for name,url,rel,cap in files:
  p=root/rel;n=0;start=time.monotonic()
  if not (p.exists() and ((name=='model' and hashlib.md5(p.read_bytes()).hexdigest()=='399a98bf36fc4550bc85d48f35451c6c') or (name=='input' and hashlib.sha256(p.read_bytes()).hexdigest()=='c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770'))):
   subprocess.run(['curl','--fail','--location','--retry','2','--retry-all-errors','--retry-delay','1','--retry-max-time','120','--connect-timeout','15','--max-time','120','--max-filesize',str(cap),'--output',str(p),url],check=True)
  n=p.stat().st_size
  data=p.read_bytes();rec={'name':name,'url':url,'path':str(p),'size':n,'sha256':hashlib.sha256(data).hexdigest(),'md5':hashlib.md5(data).hexdigest(),'seconds':time.monotonic()-start};records.append(rec);print(rec,flush=True)
  if name=='model':
   assert rec['md5']=='399a98bf36fc4550bc85d48f35451c6c','MODEL_IDENTITY_FAIL'
   with zipfile.ZipFile(p) as z:(root/'raw/model_zip_members.json').write_text(json.dumps([{'name':i.filename,'size':i.file_size,'compressed':i.compress_size} for i in z.infolist()],indent=2))
  elif name=='input':assert n==784661 and rec['sha256']=='c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770','INPUT_IDENTITY_FAIL'
  else:
   with tarfile.open(p) as t:t.extractall(root/'sources',filter='data')
 assert sum(r['size'] for r in records if r['name'] in ('model','input'))<=12*2**20
finally:(root/'raw/downloads.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
