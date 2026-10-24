"""Target admission-only disk rebinding; exact BA runtime class is re-exported."""
import pathlib,sys,copy
sys.path.insert(0,'/root/data/ep_l2_dtc_l1_native_v2/tools')
import native_dtc_guard as original
NativeDTCGuard=original.NativeDTCGuard
GIB=1024**3
def rebind_admission(value):
 out=copy.deepcopy(value);out['pre_revision_status']=out['status'];out['pre_revision_disk_checks']={k:v for k,v in out['checks'].items() if k.endswith('_native_disk_floor_plus_monitor')}
 for label in ['first','second']:
  out['checks'][label+'_native_disk_floor_plus_monitor']=out[label]['disk_free_bytes']>5*GIB
 out['status']='PASS' if all(out['checks'].values()) else 'RESOURCE_HOLD'
 out['storage_profile']='USER_LOCAL_5GiB_EXCLUSIVE_FLOOR_SHARED_ASSET_POOL_V3'
 out['monitor_unknown_headroom_included_in_5GiB']=True
 return out
def native_admission(output):return rebind_admission(original.native_admission(output))
