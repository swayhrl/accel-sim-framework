"""Resolve official distribution metadata for author requirements without installs."""
import collections,hashlib,json,pathlib,re,sys,urllib.parse
sys.path.insert(0,'/usr/lib/python3/dist-packages')
from pip._vendor.packaging.requirements import Requirement
from pip._vendor.packaging.version import Version,InvalidVersion
from pip._vendor.packaging.specifiers import SpecifierSet
from control import ROOT,http,check
PINS={'torch':'2.2.0','torchvision':'0.17.0','intel-extension-for-pytorch':'2.2.0','numpy':'1.26.4','viser':'0.2.23','nerfview':'0.0.3','imageio':'2.34.2','imageio-ffmpeg':'0.5.1','scikit-learn':'1.5.2','scipy':'1.14.1','tqdm':'4.66.5','torchmetrics':'1.3.2','opencv-python':'4.10.0.84','tyro':'0.8.8','pillow':'10.4.0','plyfile':'1.1','tensorboard':'2.17.1','tensorly':'0.8.1','pyyaml':'6.0.2','matplotlib':'3.9.2','ninja':'1.11.1.1','jaxtyping':'0.2.34','rich':'13.8.1','packaging':'24.1','setuptools':'70.3.0','pybind11':'2.13.6','psutil':'6.0.0','protobuf':'4.25.5'}
ENV={'python_version':'3.10','python_full_version':'3.10.12','implementation_name':'cpython','implementation_version':'3.10.12','os_name':'posix','sys_platform':'linux','platform_machine':'x86_64','platform_python_implementation':'CPython','platform_release':'','platform_system':'Linux','platform_version':''}
def norm(n):return re.sub('[-_.]+','-',n).lower()
def wheel_ok(f,allow_yanked=False):
 n=f['filename']
 if not n.endswith('.whl') or (f.get('yanked') and not allow_yanked):return False
 py,abi,plat=n[:-4].split('-')[-3:]
 if not (plat=='any' or (plat.endswith('x86_64') and ('linux' in plat))):return False
 if 'cp310' in py or any(x in py.split('.') for x in ['py3','py310','py2.py3']):return True
 if abi=='abi3':
  m=re.match(r'cp(\d)(\d+)',py)
  return bool(m and tuple(map(int,m.groups()))<=(3,10))
 return False
cache={};constraints=collections.defaultdict(list);extras=collections.defaultdict(set);selected={};pending=collections.deque()
rootreq=['torch==2.2.0','torchvision==0.17.0','intel-extension-for-pytorch==2.2.0','numpy<2.0.0','ninja','jaxtyping','rich>=12','setuptools==70.3.0','pybind11==2.13.6']
for line in (ROOT/'source/examples/requirements.txt').read_text().splitlines():
 if line and not line.startswith('#') and not line.startswith('git+'):rootreq.append(line)
for q in rootreq:pending.append(Requirement(q))
def getmeta(name,version=None):
 key=(name,version)
 if key not in cache:
  target=ROOT/'registry_metadata'/(name+'_'+str(version)+'.json');target.parent.mkdir(exist_ok=True)
  if target.exists():b=target.read_bytes()
  else:
   rec,b=http('https://pypi.org/pypi/'+name+('/'+version if version else '')+'/json',limit=64*1024**2)
   if rec.get('status')!=200:raise RuntimeError('OFFICIAL_METADATA_UNAVAILABLE '+name+' '+str(version))
   target.write_bytes(b)
  cache[key]=json.loads(b)
 return cache[key]
def choose(name):
 specs=SpecifierSet(','.join(str(x) for x in constraints[name] if str(x)))
 if name in PINS:
  v=PINS[name]
  if Version(v) not in specs:raise RuntimeError('FIXED_VERSION_CONFLICT '+name+' '+str(specs))
  j=getmeta(name,v)
 else:
  allmeta=getmeta(name); candidates=[]
  for ver,dist in allmeta['releases'].items():
   try:v=Version(ver)
   except InvalidVersion:continue
   if v.is_prerelease or v not in specs:continue
   if not any(wheel_ok(f) and Version('3.10.12') in SpecifierSet(f.get('requires_python') or '') for f in dist):continue
   candidates.append(v)
  if not candidates:raise RuntimeError('NO_COMPATIBLE_OFFICIAL_WHEEL '+name+' '+str(specs))
  j=getmeta(name,str(max(candidates)))
 if Version('3.10.12') not in SpecifierSet(j['info'].get('requires_python') or ''):raise RuntimeError('PYTHON_REQUIREMENT_CONFLICT '+name)
 wh=[f for f in j['urls'] if wheel_ok(f,allow_yanked=name in {'torch','torchvision','intel-extension-for-pytorch','numpy'})]
 if not wh:raise RuntimeError('NO_MATCHING_WHEEL '+name)
 f=sorted(wh,key=lambda f:(not ('cp310' in f['filename']),f['size']))[0]
 return {'name':name,'version':j['info']['version'],'filename':f['filename'],'url':f['url'],'sha256':f['digests']['sha256'],'bytes':f['size'],'license_metadata':(j['info'].get('license_expression') or (j['info'].get('license') or '')[:100]),'requires_dist':j['info'].get('requires_dist') or [],'publisher_yanked':f.get('yanked',False),'publisher_yanked_reason':f.get('yanked_reason'),'exact_author_pin_retained':name in {'torch','torchvision','intel-extension-for-pytorch','numpy'}}
seen=set()
while pending:
 req=pending.popleft();name=norm(req.name)
 constraints[name].append(req.specifier);extras[name]|=req.extras
 v=choose(name); selected[name]=v
 key=(name,v['version'],tuple(sorted(extras[name])))
 if key in seen:continue
 seen.add(key)
 print('METADATA',name,v['version'],v['bytes'],flush=True)
 for ds in v['requires_dist']:
  dep=Requirement(ds)
  if dep.marker and not any(dep.marker.evaluate({**ENV,'extra':e}) for e in ({''}|extras[name])):continue
  pending.append(dep)
 check()
lock={'status':'PARTIAL_UNTIL_VCS_AND_SPECIAL_TORCH_METADATA','python_target':'CPython 3.10.12 Linux x86_64','official_registry_wheels':sorted(selected.values(),key=lambda x:x['name']),'required_vcs_sources':[line for line in (ROOT/'source/examples/requirements.txt').read_text().splitlines() if line.startswith('git+')],'scientific_core_versions_fixed':True}
(ROOT/'distribution_closure.json').write_text(json.dumps(lock,indent=2)+'\n');print('DISTRIBUTION_CLOSURE',len(selected),'TOTAL_WHEEL_BYTES',sum(x['bytes'] for x in selected.values()))
