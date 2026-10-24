from pathlib import Path
import json,os,subprocess,ast,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');fixture=R/'synthetic/public_fixture'
for n in ['tools','catalog','bin']:(fixture/n).mkdir(parents=True,exist_ok=True)
tree=ast.parse((R/'tools/publish_library.py').read_text())
wrapper=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='wrapper' for t in n.targets))
(fixture/'tools/trace-assets').write_bytes(wrapper);(fixture/'tools/trace-assets').chmod(0o555)
(fixture/'tools/trace_assets.py').write_bytes((R/'tools/trace_assets_public.py').read_bytes())
link=fixture/'bin/trace-assets'
if not link.exists():link.symlink_to('../tools/trace-assets')
catalog={'schema':'SHARED_SM70_TRACE_LIBRARY_V1','assets':[],'objects':{},'synthetic_cpu_wrapper_qualification_only':True}
catalog['catalog_id']=hashlib.sha256((json.dumps(catalog,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()).hexdigest()
(fixture/'catalog/CURRENT').write_text(json.dumps(catalog)+'\n')
env=dict(os.environ,PATH='/invalid-project-path',PYTHONHOME='/invalid-project-python',PYTHONPATH='/invalid-project-imports',VIRTUAL_ENV='/invalid-project-venv',CONDA_PREFIX='/invalid-project-conda')
results=[]
for cwd in ['/root/data/ep_l2_main_20261023_v1/worktree','/root/data/dtc_main_20261023_v1','/root/workspace/offline-sim-v1']:
 cp=subprocess.run([str(link),'list'],cwd=cwd,env=env,capture_output=True,text=True,timeout=20);assert cp.returncode==0,(cwd,cp.stderr)
 d=json.loads(cp.stdout);assert d['catalog_id']==catalog['catalog_id'];results.append({'cwd':cwd,'status':'PASS','tainted_project_environment_ignored':True})
(R/'control/PUBLIC_WRAPPER_QUALIFICATION.json').write_text(json.dumps({'status':'PASS_CPU_ONLY','wrapper_sha256':hashlib.sha256(wrapper).hexdigest(),'script_sha256':hashlib.sha256((fixture/'tools/trace_assets.py').read_bytes()).hexdigest(),'results':results,'synthetic_catalog_only':True,'scientific_starts':0},indent=2)+'\n');print('PUBLIC_WRAPPER_QUALIFIED',flush=True)
