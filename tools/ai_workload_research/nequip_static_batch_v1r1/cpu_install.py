import pathlib,os,json,subprocess,sys,importlib.metadata as md,re,traceback
root=pathlib.Path(os.environ['TASK_DATA']);raw=root/'raw';state={'status':'RUNNING','cuda_allowed':False,'versions_changed':False}
def save():(raw/'CPU_ENVIRONMENT_GATE.json').write_text(json.dumps(state,indent=2)+'\n')
try:
 a=json.loads((raw/'LOCKED_WHEEL_DOWNLOADS.json').read_text());assert a['status']=='PASS_ALL82_ARTIFACT_BYTES_VERIFIED'
 cmd=[sys.executable,'-m','pip','install','--no-index','--no-deps','--require-hashes','--find-links',str(root/'wheelhouse'),'-r',str(root/'V1R1_INSTALL_ARTIFACT_LOCK.txt'),'--report',str(raw/'CPU_INSTALL_REPORT.json')];state['install_command']=cmd;save()
 with (raw/'CPU_INSTALL.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,'CPU_WHEEL_INSTALL_FAILED'
 expected={r['distribution']:r['version'] for r in json.loads((raw/'FROZEN_WHEEL_AVAILABILITY.json').read_text())['packages']}
 installed={n:md.version(n) for n in expected};assert installed==expected,'FROZEN82_VERSION_MISMATCH';state['installed82_versions']=installed;save()
 import antlr4
 from omegaconf import OmegaConf
 import hydra
 assert OmegaConf.to_container(OmegaConf.create({'approved_version':493}))=={'approved_version':493}
 assert hydra.utils.instantiate({'_target_':'builtins.dict','v':493})=={'v':493}
 assert 'torch' not in sys.modules and 'warp' not in sys.modules and 'openequivariance' not in sys.modules,'CPU_IMPORT_TOUCHED_CORE_GPU_LIBRARY'
 state['cpu_imports']={'antlr4':antlr4.__file__,'omegaconf':md.version('omegaconf'),'hydra-core':md.version('hydra-core'),'torch_imported':False,'warp_imported':False,'openequivariance_imported':False};save()
 with (raw/'CPU_PIP_CHECK.log').open('w') as log:r=subprocess.run([sys.executable,'-m','pip','check'],stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,'CPU_PIP_CHECK_FAILED'
 state['status']='PASS_A_ALL82_WHEELS_CPU_IMPORTS_AND_PIP_CHECK';save()
except Exception as e:state.update(status='ENVIRONMENT_BLOCKED',error=str(e),traceback=traceback.format_exc());save();print(state['traceback'],flush=True);sys.exit(1)
print(json.dumps({'status':state['status'],'packages':len(expected),'CPU_imports':state['cpu_imports']}),flush=True)
