"""Activate user storage profile only after the current model exits; no fork API."""
import pathlib,json,hashlib,os,signal,fcntl,datetime,importlib.util
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');cell='E2-AEF3-MRIQ-DH'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def gone(row):
 p=P('/proc')/str(row['pid']);return not p.exists() or int((p/'stat').read_text().rsplit(')',1)[1].split()[19])!=row['start_ticks']
def activate():
 assert not (T/'control/STORAGE_FLOOR5_ACTIVATED_V3.json').exists()
 pub=read(T/'control/STORAGE_FLOOR5_PUBLICATION_V3.json');assert pub['verified']
 qual=read(T/'control/STORAGE_FLOOR5_QUALIFICATION_V3.json');assert qual['status']=='PASS_ZERO_NEW_MODEL_STARTS'
 for name,h in qual['source_SHA256'].items():assert sha(T/'tools'/name)==h
 assert sha(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')==qual['original_spec_request_sha256']
 assert sha(T/'control/SCIENCE_AUTHORIZATION.json')==qual['original_science_authorization_sha256']
 done=read(T/'control/qualification_ledger'/(cell+'.DONE.json'));intent=read(T/'control/qualification_ledger'/(cell+'.INTENT.json'));out=P(intent['output'])
 assert done['stop_reason'] is None and done['launcher_wait_returncode']==0 and gone(read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'))
 controller=read(T/'control/CONTROLLER_LAUNCH_R3.json');proc=P('/proc')/str(controller['pid'])
 assert int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])==controller['start_ticks'] and (proc/'stat').read_text().rsplit(')',1)[1].split()[0]=='T'
 lock=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 m=load('original_authority_writer_unchanged',T/'tools/short3_native.py');reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');before=reg['registered_future_requests'][m.REQUEST]
 assert before['state']=='RUNNING' and len(before['consumed'])==10 and before['remaining']==2 and before['budget']==12
 assert before['consumed'][cell]['execution_receipt']==done
 for c in before['consumed']:
  i=read(T/'control/qualification_ledger'/(c+'.INTENT.json'));assert gone(read(P(i['output'])/'NATIVE_SIMULATOR_PID_AND_MAPS.json'))
 wrapper=N/'bin/native';old=wrapper.read_bytes();needle=str(T/'tools/short3_frontend.py').encode();replacement=str(T/'tools/short3_frontend_floor5_v3.py').encode();assert old.count(needle)==1
 new=old.replace(needle,replacement)
 record={'schema':'DTC_SHORT3_USER_STORAGE_PROFILE_ACTIVATION_V3','status':'ACTIVATED_AT_CLOSED_MODEL_BOUNDARY_NO_MODEL_RESTART','user_policy_path':str(T/'control/USER_STORAGE_POLICY_FLOOR5_V3.json'),'user_policy_sha256':sha(T/'control/USER_STORAGE_POLICY_FLOOR5_V3.json'),'qualification_sha256':sha(T/'control/STORAGE_FLOOR5_QUALIFICATION_V3.json'),'publication':pub,'old_native_source_sha256':before['controller_sha256'],'new_native_source_sha256':sha(T/'tools/short3_native_floor5_v3.py'),'new_native_source_file':'short3_native_floor5_v3.py','old_frontend':'short3_frontend.py','new_frontend':'short3_frontend_floor5_v3.py','native_entry_preimage_sha256':hashlib.sha256(old).hexdigest(),'native_entry_sha256':hashlib.sha256(new).hexdigest(),'starts_consumed':10,'remaining':2,'total_budget':12,'current_closed_model_uuid':done['uuid'],'remaining_cells':['E2-AEF3-MRIQ-CM','E2-AEF3-MRIQ-CH'],'same_science_auth_spec_configs_inputs_and_runtime':True,'same_BA_runtime_decision_class':True,'source_released_bytes':0,'new_model_starts_by_activation':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with (T/'control/STORAGE_FLOOR5_NATIVE_ENTRY_PREIMAGE.sh').open('xb') as f:f.write(old)
 tmp=wrapper.with_name('.native.SHORT3_FLOOR5.writing')
 with tmp.open('xb') as f:f.write(new);f.flush();os.fsync(f.fileno())
 tmp.chmod(wrapper.stat().st_mode&0o777);assert wrapper.read_bytes()==old;os.replace(tmp,wrapper)
 def revise(r):
  q=r['registered_future_requests'][m.REQUEST];assert q==before
  q['controller_sha256']=record['new_native_source_sha256'];q['operational_storage_revision']=record
 m.update_authority(revise)
 after=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
 assert all(after['registered_future_requests'][k]==v for k,v in reg['registered_future_requests'].items() if k!=m.REQUEST)
 assert after['qualification_history']==reg['qualification_history'] and after['old_source_history']==reg['old_source_history']
 release=T/'control/release_floor5_v3';release.mkdir()
 with (release/'PUBLICATION_READBACK.json').open('x') as f:json.dump(dict(pub,adapter_sha256=sha(T/'tools/short3_result_floor5_v3.py'),original_outbox_sha256=sha(T/'tools/short3_result_base_floor5_v3.py')),f,indent=2);f.write('\n')
 with (T/'control/STORAGE_FLOOR5_ACTIVATED_V3.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
 fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
 # Resume only the same finite metadata controller. The closed model is never signaled.
 fd=os.pidfd_open(controller['pid']);signal.pidfd_send_signal(fd,signal.SIGCONT);os.close(fd)
 print(json.dumps({'status':record['status'],'consumed':10,'remaining':2,'local_floor_bytes':5*1024**3,'new_model_starts':0},indent=2))
if __name__=='__main__':activate()
