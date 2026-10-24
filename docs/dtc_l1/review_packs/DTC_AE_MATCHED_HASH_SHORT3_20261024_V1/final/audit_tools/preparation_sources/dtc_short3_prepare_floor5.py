import pathlib,json,hashlib,ast
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1')
def put(p,x):
 with P(p).open('x') as f:f.write(x)
native=(T/'tools/short3_native.py').read_text()
assert native.count('required=7*GIB+GIB+peer_bytes+24*32*MIB+256*MIB')==1
native=native.replace('required=7*GIB+GIB+peer_bytes+24*32*MIB+256*MIB','required=5*GIB+peer_bytes+24*32*MIB+256*MIB')
native=native.replace("'other_outstanding_write_reservations_bytes':GIB+peer_bytes","'other_outstanding_write_reservations_bytes':peer_bytes")
native=native.replace("'physical_disk_pass':free>=required","'physical_disk_pass':free>required")
native=native.replace("if free<7*GIB:reason='NATIVE_DISK_FLOOR_PLUS_MONITOR'","if free<=5*GIB:reason='USER_LOCAL_OUTPUT_AT_OR_BELOW_5GiB'")
native=native.replace('from native_dtc_guard import native_admission','from short3_storage_guard_floor5 import native_admission').replace('from native_dtc_guard import NativeDTCGuard','from short3_storage_guard_floor5 import NativeDTCGuard')
native=native.replace("ROOT=P('/root/data/dtc_main_short3_20261024_v1')","ROOT=P('/root/data/dtc_main_short3_20261024_v1')\nsys.path.insert(0,str(ROOT/'tools'))")
native=native.replace('Current registered foreign requests plus1GiB unregistered-project headroom; no double count of overlay/ext4','User5GiB local safety floor includes monitor/unknown headroom; add exact bounded own writes and registered foreign writes only;164 and174-new are capacity tiers in one asset pool')
put(T/'tools/short3_native_floor5_v3.py',native)
guard='''"""Target admission-only disk rebinding; exact BA runtime class is re-exported."""
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
'''
put(T/'tools/short3_storage_guard_floor5.py',guard)
base=(T/'tools/short3_result_base.py').read_text()
start=base.index('def gate(');end=base.index('\nclass RangeWriter',start)
gate='''def gate(reservation=0,other_reservation=None):
 require(os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]','target identity')
 import subprocess
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(NAS.parent)],text=True))['filesystems'][0]
 require(fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared','genuine164 changed')
 available=os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize
 other=0 if other_reservation is None else other_reservation
 require(type(other) is int and other>=0 and type(reservation) is int and reservation>=0,'invalid bounded write reservations')
 require(available-reservation-GIB-other>5*GIB,'5GiB local safety floor after known writes HOLD')
 mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;require(mem>=64*GIB,'RAM HOLD')
 return {'SSD_available_bytes':available,'restore_reserved_bytes':reservation,'other_outstanding_write_reservations_bytes':other,'bounded_own_result_restore_spool_reserve_bytes':GIB,'local_safety_floor_bytes':5*GIB,'monitor_and_unknown_headroom_included_in_floor':True,'asset_pool':'174-new fast tier and genuine164 slow tier; do not double count identical assets','source_release_bytes':0,'MemAvailable_bytes':mem}
'''
base=base[:start]+gate+base[end:];put(T/'tools/short3_result_base_floor5_v3.py',base)
adapter=(T/'tools/short3_result.py').read_text().replace("T/'control/release'","T/'control/release_floor5_v3'").replace("T/'tools/short3_result_base.py'","T/'tools/short3_result_base_floor5_v3.py'")
adapter=adapter.replace("'unregistered_headroom_bytes':GIB","'unregistered_headroom_bytes':0").replace("'other_outstanding_write_reservations_bytes':GIB+sum(r['reserved_write_bytes'] for r in peers)","'other_outstanding_write_reservations_bytes':sum(r['reserved_write_bytes'] for r in peers)")
adapter=adapter.replace("'monitor_bytes_preserved':128*1024**2,'disk_floor_bytes_preserved':7*GIB","'monitor_bytes_included_in_floor':128*1024**2,'disk_floor_bytes_preserved':5*GIB")
adapter=adapter.replace('AEFAIR_OUTBOX_CURRENT_REGISTERED_PEERS_V2','AEFAIR_OUTBOX_USER_5GiB_SHARED_POOL_V3').replace('replace stale fixed 2GiB foreign guess with current registered peers plus1GiB unknown-project headroom, identical peer basis to the existing simulator guard.','user-authorized5GiB exclusive local safety floor includes monitor and unknown headroom; separately reserve bounded own writes and current registered peers. No model/config/input or scientific budget change.')
put(T/'tools/short3_result_floor5_v3.py',adapter)
front=(T/'tools/short3_frontend.py').read_text().replace("T/'tools/short3_native.py'","T/'tools/short3_native_floor5_v3.py'").replace("T/'tools/short3_result.py'","T/'tools/short3_result_floor5_v3.py'")
# Already archived points retain their original immutable outbox/profile handler.
original_archived=sorted(p.name.removesuffix('_ARCHIVE_RECEIPT.json') for p in (T/'control').glob('E2-AEF3-*_ARCHIVE_RECEIPT.json'))
front=front.replace("def main(argv):",'ORIGINAL_ARCHIVED='+repr(original_archived)+'\ndef main(argv):')
front=front.replace("if argv[0]=='result':", "if argv[0]=='result':\n   if argv[2] in ORIGINAL_ARCHIVED:return load('preserved_short3_original_frontend',T/'tools/short3_frontend.py').main(argv)")
put(T/'tools/short3_frontend_floor5_v3.py',front)
for name in ['short3_native_floor5_v3.py','short3_storage_guard_floor5.py','short3_result_base_floor5_v3.py','short3_result_floor5_v3.py','short3_frontend_floor5_v3.py']:ast.parse((T/'tools'/name).read_bytes())
policy={'schema':'DTC_MAIN_USER_5GiB_SHARED_ASSET_POOL_POLICY_V3','user_instruction':json.loads((T/'control/STORAGE_REVISION_METADATA_HOLD.json').read_text())['user_instruction'],'local_safety_floor_bytes':5*1024**3,'floor_semantics':'Exclusive>5GiB after known bounded writes; monitor and unknown-project cushion are part of this5GiB, not extra hardwired2GiB+1GiB guesses','known_own_write_reservation_bytes':1024**3,'known_own_basis':'Conservatively all12 result+restore caps32MiB each plus256MiB metadata/spool; current completed bytes are also in df','foreign_reservations':'Current active registered peer exact bytes only;unknown/negative values stillHOLD','asset_pool':'174-new is fast tier,genuine164 is slow tier. Keep one logical asset identity; support direct164 reads/on-demand local materialization, avoid capacity double count. Local output still uses nativeext4 with its own5GiB floor.','reclaim_authorized_when_needed':True,'safe_reclaim_prerequisites':['Our own closed assets only; do not interfere with live model/guard or peer assets','Genuine164 immutable full-member archive,whole-fileSHA reopen and independent restore qualification','Durable tier/custody path map and correct subsequent consumer references','Keep historical scientific ledger/accepted UUID/whole-input identities unchanged;restore on demand before a consumer that requires local native files','Delete only exact verified owned local objects after the slow-tier copy is usable'],'this_revision_local_source_deletions':0,'this_revision_new_scientific_starts':0,'new_budget':0,'activation_boundary':'After currently runningMRI-Q-DH model closes naturally, before its archive and before next model. Current model/guard source stays untouched.'}
put(T/'control/USER_STORAGE_POLICY_FLOOR5_V3.json',json.dumps(policy,indent=2,ensure_ascii=False)+'\n')
print('FIVE_GIB_PROFILE_PREPARED_NO_RUNTIME_MUTATION')
