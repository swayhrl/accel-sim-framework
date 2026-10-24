import pathlib,importlib.util,json,fcntl,subprocess,time,hashlib
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');cell='E2-AEF3-NN-DM'
s=importlib.util.spec_from_file_location('short3_native',T/'tools/short3_native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert not (T/'control/CONTROLLER_LAUNCH_R3.json').exists()
assert m.read(T/'control/R3_PUBLICATION_READBACK.json')['verified']
assert m.read(T/'control'/(cell+'_ARCHIVE_RECEIPT.json'))['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
qual=m.read(T/'control/QUALIFICATION_R2.json')
for name,h in qual['tool_sha256'].items():assert m.sha(T/'tools'/name)==h
lock=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def continue_unused(r):
 q=r['registered_future_requests'][m.REQUEST]
 assert q['state']=='STOP_UNACCEPTED' and q['remaining']==0 and q['sealed_unused']==11 and set(q['consumed'])=={cell} and q['budget']==12
 assert len(list((T/'control/qualification_ledger').glob('*.INTENT.json')))==1
 q['pre_fork_engineering_history'].append({'state':q['state'],'remaining':0,'sealed_unused':11,'failure':q['failure'],'evidence':str(T/'control/EXPECTATION_METADATA_CORRECTION_R2.json'),'model_starts':1,'model_retries':0,'accepted_closed_uuid':q['consumed'][cell]['uuid']})
 q['state']='RUNNING';q['remaining']=11;q['sealed_unused']=0;del q['failure']
 q['continuation']='Exactly11 original never-started cells after existing spent NN-DM postprocess correction/archive/restore; no refund or added start'
m.update_authority(continue_unused);fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
with (T/'control/CONTROLLER_R3.log').open('xb') as log:
 p=subprocess.Popen(['/usr/bin/python3','-B',str(T/'tools/short3_controller_r3.py')],cwd=T,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
 time.sleep(.2);tick=int(P('/proc',str(p.pid),'stat').read_text().rsplit(')',1)[1].split()[19])
 proof={'pid':p.pid,'start_ticks':tick,'controller_sha256':m.sha(T/'tools/short3_controller_r3.py'),'max_total_budget':12,'already_consumed_and_accepted':1,'max_unused_new_model_starts':11,'scope':'R3 finite continuation only; skip closed NN-DM permanently'}
 with (T/'control/CONTROLLER_LAUNCH_R3.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps(proof))
