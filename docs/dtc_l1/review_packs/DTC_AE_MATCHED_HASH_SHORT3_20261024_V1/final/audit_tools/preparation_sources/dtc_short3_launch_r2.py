import pathlib,importlib.util,json,fcntl,subprocess,time,os,hashlib
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
s=importlib.util.spec_from_file_location('short3_native',T/'tools/short3_native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert not (T/'control/CONTROLLER_LAUNCH_R2.json').exists()
assert not list((T/'control/qualification_ledger').glob('*.INTENT.json')) and not list((T/'DTC/run/results').iterdir())
assert (T/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').resolve()==(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').resolve()
assert json.loads((T/'control/R2_PUBLICATION_READBACK.json').read_text())['verified']
guard=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
def rearm(r):
 q=r['registered_future_requests'][m.REQUEST]
 assert q['state']=='STOP_UNACCEPTED' and q['remaining']==0 and q['consumed']=={} and q['sealed_unused']==q['budget']==12
 q['pre_fork_engineering_history']=[{'state':q['state'],'remaining':0,'sealed_unused':12,'failure':q['failure'],'evidence':str(T/'control/PRELAUNCH_ENGINEERING_STOP_R1.json'),'scientific_starts':0}]
 q['remaining']=12;q['state']='ARMED';q['sealed_unused']=0;q['prelaunch_correction']='Exact central registry path mapping; all12 cells never started; no refund/additional starts'
 del q['failure']
m.update_authority(rearm);fcntl.flock(guard,fcntl.LOCK_UN);guard.close()
prep=m.prepare('E2-AEF3-NN-DM');assert prep['source_and_runtime_checked']
with (T/'control/R2_PREPARE_PATH_QUALIFICATION.json').open('x') as f:json.dump({'status':'PASS_ZERO_STARTS','exact_central_registry_realpath':str((T/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').resolve()),'prepare':prep},f,indent=2);f.write('\n')
with (T/'control/CONTROLLER_R2.log').open('xb') as log:
 p=subprocess.Popen(['/usr/bin/python3','-B',str(T/'tools/short3_controller_r2.py')],cwd=T,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
 time.sleep(.2);tick=int(P('/proc',str(p.pid),'stat').read_text().rsplit(')',1)[1].split()[19])
 proof={'pid':p.pid,'start_ticks':tick,'controller_sha256':hashlib.sha256((T/'tools/short3_controller_r2.py').read_bytes()).hexdigest(),'max_new_model_starts':12,'scope':'R2 finite controller for original12 unconsumed cells after zero-fork engineering path correction','predecessor_preserved':str(T/'control/CONTROLLER_LAUNCH.json')}
 with (T/'control/CONTROLLER_LAUNCH_R2.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps(proof))
