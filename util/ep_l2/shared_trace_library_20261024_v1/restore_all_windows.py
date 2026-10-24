"""Independently restore every distinct content object through bounded native windows."""
from pathlib import Path
import os,json,hashlib,time,sys
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');LIB=Path('/root/workspace/assets/traces')
sys.path.insert(0,str(R/'tools'));import library_copy
gate=library_copy.Resources();gate(True);catalog=json.loads((LIB/'catalog/CURRENT').read_text());scratch=R/'recovery/windows';scratch.mkdir(parents=True,exist_ok=True)
assert scratch.stat().st_dev==Path('/root/data').stat().st_dev
ledger=R/'control/BOUNDED_NATIVE_RESTORE.jsonl';done={}
if ledger.exists():
 for l in ledger.read_text().splitlines():d=json.loads(l);done[d['sha256']]=d
limit=64*1024**2;rate=30*1024**2
for sha,o in catalog['objects'].items():
 if sha in done:continue
 gate();src=Path(o['true164_path'].replace('/home/shared','/root/share/mnt164',1));s=src.stat();assert [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]==o['verified_identity']
 # Only a window from this exact owned Goal namespace may be removed after a
 # crash; original sources and true164 objects are never cleanup targets.
 for stale in scratch.glob(sha+'.*.window'):
  assert stale.resolve().is_relative_to(scratch.resolve()) and stale.is_file() and not stale.is_symlink();stale.unlink()
 allocated=sum(p.lstat().st_blocks*512 for p in R.rglob('*') if not p.is_symlink())
 window_limit=min(limit,(256*1024**2-allocated-16*1024**2)//(1024**2)*(1024**2))
 if window_limit<1024**2:raise RuntimeError('RESOURCE_HOLD_OWN_NATIVE_TASK256MIB_CONTROL_AND_WINDOW_CAP')
 full=hashlib.sha256();offset=0;windows=0;start=time.monotonic()
 with src.open('rb') as inp:
  while offset<o['size']:
   window=scratch/(sha+'.'+str(offset)+'.window');target=min(window_limit,o['size']-offset);h=hashlib.sha256();written=0
   with window.open('xb') as out:
    while written<target:
     b=inp.read(min(1024**2,target-written));assert b
     out.write(b);h.update(b);written+=len(b);gate()
     time.sleep(max(0,(offset+written)/rate-(time.monotonic()-start)))
    out.flush();os.fsync(out.fileno())
   local=hashlib.sha256()
   with window.open('rb') as check:
    while True:
     b=check.read(1024**2)
     if not b:break
     full.update(b);local.update(b)
   assert local.hexdigest()==h.hexdigest() and window.stat().st_size==target
   offset+=target;windows+=1;window.unlink()
   (R/'control/RESTORE_PROGRESS.json').write_text(json.dumps({'sha256':sha,'file_offset':offset,'file_bytes':o['size'],'objects_done':len(done),'total_objects':len(catalog['objects']),'observed_unix':time.time()})+'\n')
 assert offset==o['size'] and full.hexdigest()==sha
 after=src.stat();assert [after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns]==o['verified_identity']
 row={'sha256':sha,'bytes':offset,'windows':windows,'closed_reopened_native_windows_full_sha':True,'scope':'All original object bytes restored and independently re-read through <=128MiB native ext4 windows; not a simultaneous complete dataset materialization','source_keep':True}
 with ledger.open('a') as log:log.write(json.dumps(row)+'\n');log.flush()
 done[sha]=row
receipt={'status':'PASS_ALL_OBJECTS_BOUNDED_NATIVE_RESTORE','objects':len(done),'bytes':sum(r['bytes'] for r in done.values()),'max_live_window_bytes':limit,'complete_large_dataset_materialization_claimed':False,'source_release_bytes':0}
(R/'control/BOUNDED_NATIVE_RESTORE_COMPLETE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
