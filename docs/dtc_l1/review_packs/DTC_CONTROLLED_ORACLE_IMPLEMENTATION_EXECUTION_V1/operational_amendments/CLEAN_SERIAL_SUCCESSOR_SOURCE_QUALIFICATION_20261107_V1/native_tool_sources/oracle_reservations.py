"""Local event-driven per-stage write reservation. No registry/FUSE/signal API."""
from pathlib import Path
import hashlib,json,os,stat
P=Path;M=1024**2;_CAPS={}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def logical_bytes(root):
 root=P(root)
 if not root.exists():return 0
 assert root.stat().st_dev==2128,'RESERVATION_NATIVE_ONLY'
 total=0;stack=[root]
 while stack:
  for e in os.scandir(stack.pop()):
   s=e.stat(follow_symlinks=False)
   if stat.S_ISDIR(s.st_mode):assert s.st_dev==2128;stack.append(P(e.path))
   elif stat.S_ISREG(s.st_mode):total+=s.st_size
 return total
def model_live(path):
 if not P(path).exists():return False
 p=read(path);s=P('/proc')/str(p['pid'])/'stat'
 try:v=s.read_text().rsplit(')',1)[1].split();return int(v[19])==p['start_ticks']and v[0]not in['Z','X']
 except(FileNotFoundError,ProcessLookupError):return False
def archived(root,c,row):
 root=P(root);a=root/'control'/(c+'_ARCHIVE_RECEIPT.json')
 if not a.exists()or not row.get('execution_receipt'):return False
 i=root/'control/qualification_ledger'/(c+'.INTENT.json');d=i.with_name(c+'.DONE.json');out=root/'DTC/run/results'/row['uuid']
 try:
  v=read(a);done=row['execution_receipt']
  if done.get('native_simulator_observed')is True and not(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json').exists():return False
  return bool(v['cohort']==c and v['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and v['source_disposition']=='SOURCE_KEEP'and row['intent_sha256']==sha(i)and read(i)['uuid']==row['uuid']==done['uuid']and read(d)==done==read(out/'NATIVE_EXIT.json')and not model_live(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'))
 except(OSError,KeyError,ValueError):return False
def compute_stage_reservation(root,q,claims,metadata_bytes=256*M):
 root=P(root);assert root.stat().st_dev==2128
 fingerprint=hashlib.sha256(json.dumps(q['admitted_specs'],sort_keys=True).encode()).hexdigest();key=(str(root),fingerprint)
 if key not in _CAPS:
  caps={}
  for c,d in q['admitted_specs'].items():
   p=root/'control/specs'/(c+'.json');assert sha(p)==d;caps[c]=read(p)['limits']['max_result_directory_bytes']
  _CAPS[key]=caps
 caps=_CAPS[key];assert set(claims)<=set(caps)and set(q['consumed'])<=set(caps)
 source=0;restore=0;rows=[]
 for c in sorted(set(claims)|set(q['consumed'])):
  cap=caps[c];row=q['consumed'].get(c)
  if c in claims:assert claims[c]['result_cap_bytes']==cap
  if row is not None and archived(root,c,row):continue
  used=logical_bytes(root/'DTC/run/results'/row['uuid'])if row is not None else 0
  done=bool(row and row.get('execution_receipt'))and not model_live(root/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
  future=16*M if done else max(0,cap-used)
  source+=future;restore=max(restore,cap)
  rows.append(dict(cohort=c,uuid=row['uuid']if row else None,observed_native_logical_bytes=used,result_cap_bytes=cap,closed_unarchived=done,remaining_source_write_bytes=future))
 value=source+restore+metadata_bytes
 assert value<=q['maximum_source_plus_restore_lifetime_bytes'],'DYNAMIC_PROJECTION_EXCEEDS_SEPARATE_TECHNICAL_MAX'
 return dict(schema='DTC_ORACLE_PER_STAGE_DYNAMIC_NATIVE_RESERVATION_V1',request=q['request'],execution_root=str(root),source_future_write_bytes=source,single_native_restore_window_bytes=restore,metadata_reserve_bytes=metadata_bytes,reserved_write_bytes=value,technical_maximum_source_plus_restore_lifetime_bytes=q['maximum_source_plus_restore_lifetime_bytes'],no_unclaimed_future_matrix_charge=True,archive_workers=1,entries=rows)
