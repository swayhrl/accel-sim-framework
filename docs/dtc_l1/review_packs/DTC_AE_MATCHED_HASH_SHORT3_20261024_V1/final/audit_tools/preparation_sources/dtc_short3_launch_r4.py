import pathlib,json,importlib.util,fcntl,subprocess,time,hashlib
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');pending='E2-AEF3-MRIQ-CH'
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('user5GiB_current_native',T/'tools/short3_native_floor5_v3.py');strict=load('unchanged_complete_strict',T/'tools/short3_strict_r2.py')
assert not (T/'control/CONTROLLER_LAUNCH_R4.json').exists() and not (T/'control/qualification_ledger'/(pending+'.INTENT.json')).exists()
assert m.read(T/'control/R4_PUBLICATION_READBACK.json')['verified']
reg=m.read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');q=reg['registered_future_requests'][m.REQUEST]
assert len(q['consumed'])==11 and q['sealed_unused']==1 and q['remaining']==0 and q['state']=='STOP_UNACCEPTED' and '[Errno 11]' in q['failure']
for c in q['consumed']:
 x=strict.terminal(c);assert m.read(T/'control'/(c+'_ARCHIVE_RECEIPT.json'))['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
for name,h in m.read(T/'control/STORAGE_FLOOR5_QUALIFICATION_V3.json')['source_SHA256'].items():assert m.sha(T/'tools'/name)==h
lock=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def continue_one(r):
 row=r['registered_future_requests'][m.REQUEST];assert row==q
 row['outbox_lock_contention_history']=[{'state':row['state'],'sealed_unused':1,'remaining':0,'failure':row['failure'],'evidence':str(T/'control/OUTBOX_CONTENTION_CHECKPOINT_R3.json'),'spent_models':11,'existing_model_reruns':0}]
 row['state']='RUNNING';row['remaining']=1;row['sealed_unused']=0;del row['failure']
 row['final_unused_continuation']='Only original never-startedMRI-Q-CH after existingCM COPY_ONLY archive/restore;budget12 unchanged,11consumed. Metadata outbox waits on transient lockEAGAIN;models are never retried.'
m.update_authority(continue_one);fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
with (T/'control/CONTROLLER_R4.log').open('xb') as log:
 p=subprocess.Popen(['/usr/bin/python3','-B',str(T/'tools/short3_controller_r4.py')],cwd=T,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
 time.sleep(.2);tick=int(P('/proc',str(p.pid),'stat').read_text().rsplit(')',1)[1].split()[19])
 proof={'pid':p.pid,'start_ticks':tick,'controller_sha256':m.sha(T/'tools/short3_controller_r4.py'),'archive_wait_sha256':m.sha(T/'tools/short3_archive_wait.py'),'max_total_budget':12,'already_consumed_and_accepted_archived':11,'max_unused_new_model_starts':1,'only_unused_cell':pending,'scope':'R4 finite continuation;all11spent original model UUIDs skipped permanently;no model retry'}
 with (T/'control/CONTROLLER_LAUNCH_R4.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps(proof))
