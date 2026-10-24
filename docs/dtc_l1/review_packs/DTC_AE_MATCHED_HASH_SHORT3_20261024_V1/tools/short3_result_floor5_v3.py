"""Postprocess-only adapter: current peer reservations plus 1 GiB unknown headroom.

Preserves the frozen outbox, its own 1 GiB reserve, 128 MiB monitor, 7 GiB
floor, RAM/mount checks, immutable bundle verification and independent restore.
No simulator launch, science ledger mutation, retry or source release API.
"""
import pathlib,json,hashlib,importlib.util,os
T=pathlib.Path('/root/data/dtc_main_short3_20261024_v1')
N=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2')
D=T/'control/release_floor5_v3'
REQUEST='DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1'
GIB=1024**3
def require(x,why):
 if not x:raise RuntimeError(why)
def read(p):return json.loads(pathlib.Path(p).read_bytes())
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def peer_basis(reg):
 rows=reg['registered_future_requests'];own=rows[REQUEST]
 require(type(own['reserved_write_bytes']) is int and 0<=own['reserved_write_bytes']<=GIB,'own writes exceed frozen 1GiB outbox reserve')
 peers=[]
 for name,row in rows.items():
  if name==REQUEST or row.get('state') in ['COMPLETE','CLOSED','STOP_UNACCEPTED']:continue
  amount=row.get('reserved_write_bytes')
  require(type(amount) is int and amount>=0,'unknown active peer reservation:'+name)
  peers.append({'request':name,'reserved_write_bytes':amount})
 return {'peer_reservations':peers,'registered_peer_bytes':sum(r['reserved_write_bytes'] for r in peers),'unregistered_headroom_bytes':0,'other_outstanding_write_reservations_bytes':sum(r['reserved_write_bytes'] for r in peers),'own_reservation_bytes_preserved':GIB,'monitor_bytes_included_in_floor':128*1024**2,'disk_floor_bytes_preserved':5*GIB}
def current_basis():
 p=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';raw=p.read_bytes();epoch=read(N/'control/CURRENT_SCIENCE_EPOCH.json')
 require(hashlib.sha256(raw).hexdigest()==epoch['native_registry_sha256'],'registry/epoch hash mismatch')
 require(epoch['epoch']==2 and epoch['state']=='NATIVE_SCIENCE_ACTIVE','current native epoch required')
 basis=peer_basis(json.loads(raw));basis['native_registry_sha256']=hashlib.sha256(raw).hexdigest();return basis
def bind_gate(outbox):
 original=outbox.gate
 def gate(reservation=0,other_reservation=None):
  basis=current_basis();other=basis['other_outstanding_write_reservations_bytes']
  if other_reservation is not None:
   require(type(other_reservation) is int and other_reservation>=other,'explicit reservation may only increase current peer/headroom requirement');other=other_reservation
  result=original(reservation,other_reservation=other)
  require(os.statvfs(T).f_favail>=100000,'native inode floor HOLD')
  result['current_peer_reservation_basis']=basis
  result['postprocess_only_profile']='AEFAIR_OUTBOX_USER_5GiB_SHARED_POOL_V3'
  return result
 outbox.gate=gate
def archive(cohort):
 proof=read(D/'PUBLICATION_READBACK.json')
 require(proof['verified'] and proof['adapter_sha256']==sha(__file__),'published postprocess adapter binding required')
 source=T/'tools/short3_result_base_floor5_v3.py';require(sha(source)==proof['original_outbox_sha256'],'frozen outbox changed')
 spec=importlib.util.spec_from_file_location('frozen_aefair_outbox_under_current_peer_gate',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 # This also checks terminal identity and that the original model is gone.
 closed=m.manifest_for(cohort);out=pathlib.Path(closed['source_root'])
 profile={'schema':'AEFAIR_POSTPROCESS_CURRENT_PEER_PROFILE_V2','source_release':proof,'no_model_or_scientific_configuration_change':True,'no_retry_refund_or_ledger_change':True,'original_outbox_preserved':str(source),'initial_current_peer_basis':current_basis(),'resource_policy':'Frozen outbox checks remain; user-authorized5GiB exclusive local safety floor includes monitor and unknown headroom; separately reserve bounded own writes and current registered peers. No model/config/input or scientific budget change.'}
 for name,data in [('OUTBOX_GATE_ADAPTER_V2.py',pathlib.Path(__file__).read_bytes()),('OUTBOX_GATE_PROFILE_V2.json',(json.dumps(profile,sort_keys=True,indent=2)+'\n').encode())]:
  p=out/name
  if p.exists():
   if name.endswith('.py'):require(p.read_bytes()==data,'closed adapter source changed')
   else:require(read(p)['source_release']==proof,'closed postprocess release changed')
  else:
   with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 bind_gate(m)
 return m.archive(cohort)
