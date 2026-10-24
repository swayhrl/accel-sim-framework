"""Read-only consistent epoch/registry snapshot; never changes authority."""
import pathlib,json,hashlib,time,socket
REG=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
EPOCH=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json')
def snapshot():
 deadline=time.monotonic()+10;last=None
 while time.monotonic()<deadline:
  try:
   before=EPOCH.read_bytes();rb=REG.read_bytes();after=EPOCH.read_bytes()
   if before!=after:raise ValueError('concurrent epoch change')
   epoch=json.loads(after);registry=json.loads(rb);h=hashlib.sha256(rb).hexdigest()
   if epoch['native_registry_sha256']!=h:raise ValueError('registry/epoch CAS transition')
   assert epoch['epoch']==registry['epoch']==2 and epoch['holder']==socket.gethostname(),'native authority identity mismatch'
   rows=registry['registered_future_requests'];values=[v['reserved_write_bytes']for v in rows.values()]
   assert all(type(v)is int and v>=0 for v in values)
   return {'registry_path':str(REG),'registry_sha256':h,'epoch_path':str(EPOCH),'epoch_sha256':hashlib.sha256(after).hexdigest(),'epoch':2,'holder':epoch['holder'],'sum_all_records_reserved_write_bytes':sum(values),'record_count':len(values),'filtering':'NONE: every registered_future_requests record regardless of state/consumed/owner','read_only_double_epoch_consistency':True,'unix':time.time()}
  except (ValueError,KeyError)as e:last=repr(e);time.sleep(.1)
 raise RuntimeError('Could not read consistent authority within10s: '+str(last))
if __name__=='__main__':print(json.dumps(snapshot(),indent=2))
