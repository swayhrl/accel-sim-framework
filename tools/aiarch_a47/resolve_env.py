"""CPU-only official PyPI metadata closure; payload freeze precedes wheel transfer."""
import concurrent.futures,json,pathlib,sys,hashlib,subprocess
from pip._vendor.packaging.requirements import Requirement
from pip._vendor.packaging.version import Version,InvalidVersion
from pip._vendor.packaging.tags import sys_tags,parse_tag
from pip._vendor.packaging.utils import canonicalize_name,parse_wheel_filename
from pip._vendor.packaging.markers import default_environment
from budget_io import ROOT,get_small,download,check_disk
allowed=set(sys_tags());env=default_environment();constraints={};extras={};selected={};expanded=set()
def add(s):
 req=Requirement(s);name=canonicalize_name(req.name)
 constraints.setdefault(name,set()).add(str(req.specifier));extras.setdefault(name,set()).update(req.extras)
for s in ['cuvs-cu12==26.10.0','cupy-cuda12x[ctk]==14.0.1','numpy>=2.0,<2.6','h5py'] :add(s)
def choose(name):
 raw=get_small(f'https://pypi.org/pypi/{name}/json',name+'-all.json');allmeta=json.loads(raw)
 versions=[]
 for v in allmeta['releases']:
  try:
   parsed=Version(v)
   if not parsed.is_prerelease:versions.append(parsed)
  except InvalidVersion:pass
 for ver in sorted(versions,reverse=True):
  if not all(ver in Requirement(name+spec).specifier for spec in constraints[name]):continue
  files=[]
  for x in allmeta['releases'][str(ver)]:
   if x.get('yanked') or not x['filename'].endswith('.whl'):continue
   if x.get('requires_python') and Version(env['python_full_version']) not in Requirement('python'+x['requires_python']).specifier:continue
   try:tags=parse_wheel_filename(x['filename'])[3]
   except Exception:continue
   if tags&allowed:files.append(x)
  if not files:continue
  chosen=min(files,key=lambda x:x['size']);detail=json.loads(get_small(f'https://pypi.org/pypi/{name}/{ver}/json',f'{name}-{ver}.json'))
  return {'name':name,'version':str(ver),'filename':chosen['filename'],'bytes':chosen['size'],'sha256':chosen['digests']['sha256'],'url':chosen['url'],'requires_python':detail['info']['requires_python'],'requires_dist':detail['info']['requires_dist'] or []}
 raise RuntimeError('NO_OFFICIAL_COMPATIBLE_WHEEL '+name+' '+str(constraints[name]))
for rounds in range(80):
 changed=False
 for name in list(constraints):
  prev=selected.get(name)
  if prev is None or not all(Version(prev['version']) in Requirement(name+spec).specifier for spec in constraints[name]):selected[name]=choose(name);changed=True
  row=selected[name];key=(name,row['version'],tuple(sorted(extras[name])))
  if key not in expanded:
   for s in row['requires_dist']:
    req=Requirement(s)
    if req.marker is None or any(req.marker.evaluate({**env,'extra':extra}) for extra in ['']+list(extras[name])):add(s)
   expanded.add(key);changed=True
 if not changed:break
else:raise RuntimeError('DEPENDENCY_CLOSURE_NOT_CONVERGED')
rows=list(selected.values());total=sum(x['bytes'] for x in rows);lock={'status':'RESOLVED_BEFORE_PAYLOAD_DOWNLOAD','python':sys.version,'packages':rows,'payload_bytes':total,'constraints':{k:sorted(v) for k,v in constraints.items()},'extras':{k:sorted(v) for k,v in extras.items()},'source':'official PyPI JSON URL/digest/platform metadata only'}
assert total+485413888+json.loads((ROOT/'download_budget.json').read_text())['total_bytes']<6*1024**3
(ROOT/'resolved_env_lock.json').write_text(json.dumps(lock,indent=2)+'\n');print('CLOSURE',len(rows),'WHEEL_BYTES',total,[(x['name'],x['version']) for x in rows],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 def fetch(x):
  p=ROOT/'downloads'/x['filename'];rec=download(x['url'],p,x['bytes'],x['sha256']);print('WHEEL',x['name'],x['bytes'],flush=True);return rec
 receipts=list(pool.map(fetch,rows))
(ROOT/'wheel_download_receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
subprocess.run([sys.executable,'-m','pip','install','--no-index','--no-deps','--no-cache-dir',*[str(ROOT/'downloads'/x['filename']) for x in rows]],check=True,stdout=(ROOT/'logs/install.log').open('w'),stderr=subprocess.STDOUT)
cp=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True);(ROOT/'logs/pip_check.log').write_text(cp.stdout+cp.stderr);assert cp.returncode==0
lock['status']='INSTALLED_OFFLINE_PIP_CHECK_PASS';(ROOT/'resolved_env_lock.json').write_text(json.dumps(lock,indent=2)+'\n');print('ENV_PASS',check_disk(),flush=True)
