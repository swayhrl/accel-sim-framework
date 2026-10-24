from pathlib import Path
import json,subprocess,sys,os,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');LIB=Path('/root/workspace/assets/traces');command='/root/workspace/assets/bin/trace-assets'
catalog=json.loads((LIB/'catalog/CURRENT').read_text());env={k:v for k,v in os.environ.items() if not any(t in k.upper() for t in ['EP_L2','DTC','CUDA_INJECTION','LD_PRELOAD','TRACES_FOLDER'])};env['PYTHONDONTWRITEBYTECODE']='1'
dirs=['/root/data/ep_l2_main_20261023_v1/worktree','/root/data/dtc_main_20261023_v1','/root/workspace/offline-sim-v1']
reports=[]
for cwd in dirs:
 p=subprocess.run([command,'list'],cwd=cwd,env=env,capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stderr
 d=json.loads(p.stdout);assert len(d['assets'])==len(catalog['assets']) and d['catalog_id']==catalog['catalog_id'];reports.append({'cwd':cwd,'operation':'list_without_project_activation','status':'PASS','catalog_id':d['catalog_id'],'assets':len(d['assets'])})
p=subprocess.run([command,'verify','--all'],env=env,capture_output=True,text=True,timeout=600);assert p.returncode==0,p.stderr
checks=json.loads(p.stdout)['results'];assert len(checks)==len(catalog['assets']);reports.append({'operation':'all_bundles_all_declared_members_open_seek_reopen','status':'PASS','results':checks})
for a in catalog['assets']:
 tree=LIB/a['relative_view_path'];assert tree.is_dir()
 for m in a['members']:
  p=tree/m['relative_path'];assert p.is_file() and p.stat().st_size==m['size']
 entries=[m for m in a['members'] if m['relative_path']=='kernelslist.g'];assert len(entries)==1
 assert hashlib.sha256((tree/'kernelslist.g').read_bytes()).hexdigest()==entries[0]['sha256']
actual=sorted(catalog['assets'],key=lambda a:a['logical_bytes'])
for i,cwd in enumerate(dirs):
 a=actual[i%len(actual)];dest=R/'recovery'/('CROSS_PROJECT_'+str(i))
 if dest.exists():assert dest.is_dir() and dest.with_name(dest.name+'.MATERIALIZATION_RECEIPT.json').exists();continue
 p=subprocess.run([command,'materialize',a['bundle_id'],'--destination',str(dest),'--max-bytes',str(32*1024**2)],cwd=cwd,env=env,capture_output=True,text=True,timeout=180);assert p.returncode==0,p.stderr
 d=json.loads(p.stdout);assert d['status']=='PASS_COMPLETE_LOCAL_MATERIALIZATION';reports.append({'cwd':cwd,'operation':'complete_native_materialization','status':'PASS','receipt':d})
for args in [['show','NO_SUCH_ASSET'],['materialize',actual[0]['bundle_id'],'--destination',str(LIB/'FORBIDDEN_WRITE')],['materialize',actual[0]['bundle_id'],'--destination',str(R/'recovery/CROSS_PROJECT_0')]]:
 p=subprocess.run([command]+args,env=env,capture_output=True,text=True,timeout=30);assert p.returncode!=0;reports.append({'operation':'negative_case','args':args,'status':'PASS_EXPECTED_REFUSAL','stderr':p.stderr})
result={'status':'PASS_CROSS_PROJECT_ALL_ASSET_ACCESS','catalog_id':catalog['catalog_id'],'assets':len(catalog['assets']),'projects_tested':len(dirs),'project_activation_required':False,'scientific_starts':0,'reports':reports}
(R/'control/CROSS_PROJECT_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='reports'}),flush=True)
