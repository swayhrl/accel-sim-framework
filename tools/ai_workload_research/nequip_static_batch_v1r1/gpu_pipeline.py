"""Run the original scientific sequence under one shared GPU lock, then STOP."""
import pathlib,os,json,subprocess,time,sys,hashlib,traceback,importlib.metadata as md,datetime
root=pathlib.Path(os.environ['TASK_DATA']);raw=root/'raw';controller={'status':'RUNNING','stage':'CHECK_A','executor':'Codex Lane M / node109'}
def save():(raw/'GPU_PIPELINE_RECEIPT.json').write_text(json.dumps(controller,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 assert 'TASK_GPU_LOCK_START_MONOTONIC' in os.environ
 if '--resume-native-canary' in sys.argv:
  expected={'nequip':'0.19.1','openequivariance':'0.7.0','nvalchemi-toolkit-ops':'0.4.1'}
  assert all(md.version(n)==v for n,v in expected.items())
  assert (raw/'CORE_SOURCE_INSTALL_REPORT.json').exists()
  os.environ['V1R1_RESUME_INSTALLED_CORE']='1'
 assert json.loads((raw/'CPU_ENVIRONMENT_GATE.json').read_text())['status']=='PASS_A_ALL82_WHEELS_CPU_IMPORTS_AND_PIP_CHECK'
 controller['stage']='OFFICIAL_SOURCE_BUILDS_IDENTITY_AND_CANARY';save()
 r=subprocess.run(['bash','tools/ai_workload_research/nequip_static_batch_v1r1/gpu_prepare.sh']);assert r.returncode==0,'GPU_PREPARATION_STOP'
 controller['stage']='FREEZE';save()
 subprocess.run(['git','add','tools/ai_workload_research/nequip_static_batch_v1r1'],check=True)
 subprocess.run(['git','-c','pack.threads=8','commit','-m','feat(ai-arch): freeze V1R1 qualified observation runner'],check=True)
 freeze={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runner_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'runner_tree':subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip(),'original_science_start':'06674a961632c107681ac146d735d932dde112d6','approval_commit':'bff12efa72a5d73e4358f9900229e779f5d8dc3e','compiled_sha256':sha(root/'OAM-S.nequip.pt2'),'model_sha256':sha(root/'inputs/NequIP-OAM-S-0.1.nequip.zip'),'input_sha256':sha(root/'inputs/sitraj.xyz'),'original82_versions':json.loads((raw/'CPU_ENVIRONMENT_GATE.json').read_text())['installed82_versions'],'all_installed_distributions':{d.metadata['Name']:d.version for d in md.distributions()},'source_files':{str(p):sha(p) for p in pathlib.Path('tools/ai_workload_research/nequip_static_batch_v1r1').glob('*') if p.is_file()},'gate_files':{p.name:sha(p) for p in raw.glob('*checks.json')},'conditions':['N-C2','N-G2','N-G4','N-G8'],'precision':'FP32 TF32-off autocast-off','atol':5e-5,'rtol':5e-5,'trial_mean_count':5,'formal_deadline_seconds':900,'formal_processes':3,'blocks_per_process':12,'samples_per_condition':36}
 (raw/'FROZEN_EXPERIMENT_MANIFEST.json').write_text(json.dumps(freeze,indent=2)+'\n')
 controller['stage']='FORMAL_OBSERVATION';save();start=time.monotonic();controller['formal_processes']=[]
 for i in range(3):
  remaining=900-(time.monotonic()-start);assert remaining>0,'BUDGET_STOP_FORMAL_15MIN'
  with (raw/f'FORMAL_PROCESS_{i}.log').open('w') as log:
   r=subprocess.run([str(root/'venv/bin/python'),'tools/ai_workload_research/nequip_static_batch_v1r1/observe.py','formal',str(i)],stdout=log,stderr=subprocess.STDOUT,timeout=remaining)
  controller['formal_processes'].append({'id':i,'returncode':r.returncode});controller['formal_seconds']=time.monotonic()-start;save();assert r.returncode==0,f'FORMAL_PROCESS_{i}_STOP'
 controller.update(status='PASS_COMPLETE_SCIENTIFIC_EXECUTION',stage='STOP_AFTER_OBSERVATION');save()
except Exception as e:
 controller.update(status='STOP',error=str(e),traceback=traceback.format_exc());save();print(controller['traceback'],flush=True);sys.exit(1)
print(json.dumps(controller),flush=True)
