"""Finite exact DTC registration; uses existing shared epoch2 authority lock."""
import pathlib,json,hashlib,fcntl,importlib.util,os,subprocess,datetime
N=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2');T=pathlib.Path('/root/data/dtc_main_20261023_v1/ae_fair_v1');P=pathlib.Path('/root/data/dtc_main_20261023_v1/accel-sim-framework/docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_EPOCH2_20261023_V1')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(pathlib.Path(p).read_text())
def install():
 held=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
 evidence=read(T/'control/PUBLICATION_READBACK.json');assert evidence['remote_exact_sources_and_release_verified']
 assert not (T/'control/NATIVE_REQUEST_INSTALL_RECEIPT.json').exists(),'already installed; no duplicate request'
 s=importlib.util.spec_from_file_location('new_exact_dtc_adapter',T/'tools/aefair_native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 q=read(T/'control/REGISTRATION_CANDIDATE.json');assert q['controller_sha256']==sha(T/'tools/aefair_native.py')
 resources=m.resources(m.spec_for('E2-AEFAIR-DM'));assert resources['physical_RAM_pass'] and resources['physical_disk_pass'],'current native resource admission pending'
 reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');peer_preimages={k:v for k,v in reg['registered_future_requests'].items()}
 assert m.REQUEST not in peer_preimages,'request already registered'
 for name,row in peer_preimages.items():
  assert row['state'] in ['COMPLETE','CLOSED','STOP_UNACCEPTED'],'peer science unresolved'
  if name=='EP_NATIVE_TAGPRESSURE_VECTOR_HOLDOUT_V1':
   rec=pathlib.Path('/root/data/ep_l2_main_vector_r5_20261023_v1/control')/(name+'_ARCHIVE_RECEIPT.json')
   assert rec.exists() and read(rec)['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','peer outbox/restore pending'
 wrapper=N/'bin/native';before=wrapper.read_bytes();assert b'ep_l2_main_vector_r5_20261023_v1/native_dispatch.py' in before,'sole current entry changed; review new predecessor'
 (T/'control/NATIVE_ENTRY_PREIMAGE').write_bytes(before)
 for name in ['native_epoch2_frontend.py','aefair_native.py','aefair_strict.py','aefair_result.py']:
  assert (T/'tools'/name).read_bytes()==(P/'tools'/name).read_bytes()
 replacement=b'#!/bin/sh\nset -eu\nexec /usr/bin/python3 -B /root/data/dtc_main_20261023_v1/ae_fair_v1/tools/native_epoch2_frontend.py "$@"\n'
 temp=wrapper.with_name('native.AEFAIR.writing')
 with temp.open('xb') as f:f.write(replacement);f.flush();os.fsync(f.fileno())
 temp.chmod(wrapper.stat().st_mode&0o777);assert wrapper.read_bytes()==before;os.replace(temp,wrapper)
 def register(r):
  assert r['registered_future_requests']==peer_preimages
  r['registered_future_requests'][m.REQUEST]=q
 m.update_authority(register)
 after=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
 assert all(after['registered_future_requests'][k]==v for k,v in peer_preimages.items())
 proof={'status':'EXACT_DTC_FOUR_FRESH_REQUEST_REGISTERED','request_id':m.REQUEST,'new_budget':4,'actual_starts':0,'native_entry_preimage_sha256':hashlib.sha256(before).hexdigest(),'native_entry_sha256':sha(wrapper),'peer_router_preserved':'/root/data/ep_l2_main_vector_r5_20261023_v1/native_dispatch.py','peer_rows_unchanged':True,'old_qualification_history_unchanged':after['qualification_history']==reg['qualification_history'],'old_source_history_unchanged':after['old_source_history']==reg['old_source_history'],'single_central_registry':str(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'),'request_ledger':str((T/'control/qualification_ledger').resolve()),'global_science_lock':str(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock'),'epoch':read(N/'control/CURRENT_SCIENCE_EPOCH.json'),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (T/'control/NATIVE_REQUEST_INSTALL_RECEIPT.json').write_text(json.dumps(proof,indent=2)+'\n')
 return proof
if __name__=='__main__':print(json.dumps(install(),indent=2))
