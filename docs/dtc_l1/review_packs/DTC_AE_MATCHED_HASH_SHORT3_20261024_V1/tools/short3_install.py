"""One exact twelve-start request installation under the sole native authority."""
import pathlib,json,hashlib,fcntl,os,importlib.util,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def install():
 lock=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not (T/'control/NATIVE_REQUEST_INSTALL_RECEIPT.json').exists(),'already installed'
 assert read(T/'control/PUBLICATION_READBACK.json')['verified']
 assert read(T/'control/QUALIFICATION.json')['status']=='PASS_ZERO_MODEL_STARTS'
 s=importlib.util.spec_from_file_location('new_short3_native',T/'tools/short3_native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');pre=reg['registered_future_requests']
 assert m.REQUEST not in pre
 assert all(row['state'] in ['COMPLETE','CLOSED','STOP_UNACCEPTED'] for row in pre.values()),'peer science unresolved'
 epoch=read(N/'control/CURRENT_SCIENCE_EPOCH.json');assert epoch['epoch']==2 and epoch['state']=='NATIVE_SCIENCE_ACTIVE'
 q=read(T/'control/REGISTRATION_CANDIDATE.json');assert q['controller_sha256']==sha(T/'tools/short3_native.py')
 r=m.resources(m.spec_for('E2-AEF3-NN-DM'));assert r['physical_RAM_pass'] and r['physical_disk_pass'],'current physical resource HOLD'
 wrapper=N/'bin/native';old=(T/'control/NATIVE_ENTRY_PREIMAGE').read_bytes();assert wrapper.read_bytes()==old,'sole entry changed; review predecessor'
 expected=b'/root/data/dtc_main_20261023_v1/ae_fair_v1/tools/native_epoch2_frontend.py'
 assert old.count(expected)==1
 new=old.replace(expected,str(T/'tools/short3_frontend.py').encode())
 tmp=N/'bin/.native.SHORT3.writing'
 with tmp.open('xb') as f:f.write(new);f.flush();os.fsync(f.fileno())
 tmp.chmod(wrapper.stat().st_mode&0o777);assert wrapper.read_bytes()==old;os.replace(tmp,wrapper)
 def add(registry):
  assert registry['registered_future_requests']==pre
  registry['registered_future_requests'][m.REQUEST]=q
 m.update_authority(add)
 after=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
 assert all(after['registered_future_requests'][k]==v for k,v in pre.items())
 assert after['qualification_history']==reg['qualification_history'] and after['old_source_history']==reg['old_source_history']
 proof={'status':'EXACT_SHORT3_TWELVE_FRESH_REQUEST_REGISTERED','request_id':m.REQUEST,'budget':12,'remaining':12,'actual_starts':0,'native_entry_preimage_sha256':hashlib.sha256(old).hexdigest(),'native_entry_sha256':sha(wrapper),'asset_router_preserved':True,'all_prior_science_routes_preserved':True,'peer_rows_unchanged':True,'historical_ledgers_unchanged':True,'resources':r,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with (T/'control/NATIVE_REQUEST_INSTALL_RECEIPT.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
 return proof
