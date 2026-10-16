from common import *
import subprocess,zipfile,csv,base64,io,sys
OLD=pathlib.Path('/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014');SITE=OLD/'venv/lib/python3.10/site-packages';BASE=pathlib.Path('/data/c16/env/cpython-3.10.12/bin/python3.10');V=R/'venv';env=os.environ.copy();env.update(LD_LIBRARY_PATH='/data/c16/env/cpython-3.10.12/lib',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PIP_NO_CACHE_DIR='1',HOME=str(R/'cache/home'),TMPDIR=str(R/'tmp'),XDG_CACHE_HOME=str(R/'cache'),TORCH_HOME=str(R/'cache/torch'),A61_TASK_ID='AIARCH_A61_109_V1');env.pop('PYTHONPATH',None)
assert not V.exists();subprocess.run([str(BASE),'-m','venv',str(V)],env=env,check=True);target=V/'lib/python3.10/site-packages'
# Explicitly bind only immutable official Torch/CUDA/Triton distributions, not the old environment namespace.
selected=[p for p in SITE.glob('*.dist-info') if p.name.startswith(('torch-','triton-','nvidia_'))];checks=[];bound=set()
accepted=json.loads((OLD/'wheel_download_receipts.json').read_text())['files'];accepted={x['filename']:x for x in accepted if x.get('status')=='PASS'}
for dist in selected:
 meta=(dist/'METADATA').read_text();name=next(x.split(': ',1)[1] for x in meta.splitlines() if x.startswith('Name:'));version=next(x.split(': ',1)[1] for x in meta.splitlines() if x.startswith('Version:'));needle=name.replace('-','_')+'-'+version+'-';candidates=list((OLD/'wheels').glob(needle+'*.whl'));assert len(candidates)==1,(name,candidates);wheel=candidates[0];record=accepted.get(wheel.name)
 # Torch's official local-version wheel was frozen separately by original accepted run.
 if record:assert sha(wheel)==record['sha256']
 with zipfile.ZipFile(wheel) as z:
  rec=z.read(next(n for n in z.namelist() if n.endswith('.dist-info/RECORD'))).decode();nchecked=0;actual=[]
  for path,digest,size in csv.reader(io.StringIO(rec)):
   if not digest or '.data/' in path or path.endswith('.pyc'):continue
   oldp=SITE/path;assert oldp.is_file(),str(oldp);algo,b64=digest.split('=',1);assert algo=='sha256';s=oldp.stat();h=sha(oldp);assert base64.urlsafe_b64encode(bytes.fromhex(h)).decode().rstrip('=')==b64,(name,path);assert oldp.stat().st_mtime_ns==s.st_mtime_ns;actual.append({'path':path,'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':h});nchecked+=1
  top={path.split('/')[0] for path,_,_ in csv.reader(io.StringIO(rec)) if '/' in path and '.dist-info' not in path.split('/')[0] and '.data' not in path.split('/')[0]}
 for namepart in top|{dist.name}:
  p=SITE/namepart
  if p.exists() and namepart not in bound:assert not (target/namepart).exists();(target/namepart).symlink_to(p,target_is_directory=p.is_dir());bound.add(namepart)
 checks.append({'name':name,'version':version,'wheel':str(wheel),'wheel_sha256':sha(wheel),'prior_accepted_receipt':record,'verified_installed_files':actual,'files_checked':nchecked,'binding':'new venv explicit package symlink to immutable read-only old distribution; no old sys.path/pip install or bytecode/cache writes'});print('READONLY_DISTRIBUTION_PASS',name,version,nchecked,flush=True);check()
save('readonly_runtime_bindings.json',{'status':'PASS','distributions':checks,'explicit_top_level_bindings':sorted(bound),'new_venv':str(V),'old_assets_no_write':True})
# Official DGL and PyG chosen before any training/measurement; all package installs target this venv only.
dglurl='https://data.dgl.ai/wheels/torch-2.2/cu121/dgl-2.4.0%2Bcu121-cp310-cp310-manylinux1_x86_64.whl';dglname='dgl-2.4.0+cu121-cp310-cp310-manylinux1_x86_64.whl'
r,b=request(dglurl,'downloads/'+dglname,kind='dependency',limit=600*1024**2);assert r.get('status')==200 and not r.get('error'),r
with zipfile.ZipFile(R/'downloads'/dglname) as z:
 save('dgl_wheel_metadata.json',{'URL':dglurl,'sha256':sha(R/'downloads'/dglname),'expanded_member_bytes':sum(x.file_size for x in z.infolist()),'METADATA':z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))).decode(),'graphbolt_libraries':[n for n in z.namelist() if 'graphbolt' in n and n.endswith('.so')]})
for name,version in [('torch-geometric','2.6.1'),('sympy','1.12')]:
 r,b=request('https://pypi.org/pypi/'+name+'/'+version+'/json');assert r['status']==200;d=json.loads(b);wheel=next(x for x in d['urls'] if x['filename'].endswith('py3-none-any.whl'));r,b=request(wheel['url'],'downloads/'+wheel['filename'],kind='dependency',limit=32*1024**2);assert not r.get('error') and sha(R/'downloads'/wheel['filename'])==wheel['digests']['sha256']
constraints=R/'environment_constraints.txt';constraints.write_text('torch==2.2.0+cu121\ntriton==2.2.0\nnumpy==1.26.4\nscipy==1.14.1\nsympy==1.12\ndgl==2.4.0+cu121\ntorch-geometric==2.6.1\n')
cmd=[str(V/'bin/python'),'-m','pip','install','--no-index','--find-links',str(OLD/'wheels'),'--find-links','/data/c16/wheelhouse/c16-g-cp310-cu124','--find-links',str(R/'downloads'),'-c',str(constraints),'dgl==2.4.0+cu121','torch-geometric==2.6.1','numpy==1.26.4','scipy==1.14.1','sympy==1.12']
subprocess.run(cmd+['--dry-run','--report',str(R/'environment_dry_run.json')],env=env,check=True)
subprocess.run(cmd+['--report',str(R/'environment_install_report.json')],env=env,check=True)
subprocess.run([str(V/'bin/python'),'-m','pip','check'],env=env,check=True)
subprocess.run([str(V/'bin/python'),'-m','pip','freeze','--all'],env=env,stdout=(R/'environment_freeze.txt').open('w'),check=True)
save('environment_prepared.json',{'status':'PASS_INSTALLED_OFFICIAL_METADATA_ONLY_GPU_ABI_NOT_RUN','python':'3.10.12','runtime_binding_policy':'explicit selected immutable Torch/CUDA/Triton distributions only','DGL':'2.4.0+cu121','Torch':'2.2.0+cu121','PyG':'2.6.1','numpy':'1.26.4','sympy':'1.12','new_disk_bytes':check(),'GPU_initialization':0});print('ENVIRONMENT_PREPARED_NO_CUDA_IMPORT',flush=True)
