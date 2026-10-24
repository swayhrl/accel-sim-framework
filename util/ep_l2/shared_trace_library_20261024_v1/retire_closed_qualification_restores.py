"""Reclaim only our completed synthetic restores after current NAS/full-SHA proof."""
from pathlib import Path
import sys,json,time,hashlib,os
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy_v8 as e
proof=R/'control/CLOSED_QUALIFICATION_RESTORE_RETIREMENT.json'
assert not proof.exists(),'one-time bounded retirement already recorded'
rows=[]
for rev in ['V3','ISOLATED_V5','ISOLATED_V6','ISOLATED_V7','ISOLATED_V8']:
 p=R/'control'/('PROTOCOL_QUALIFICATION_'+rev+'.json');q=json.loads(p.read_text());assert q['status']=='PASS'
 archives=[x['receipt'] for x in q['reports'] if x['test']=='archive_full_SHA_and_order'];restores=[x['receipt'] for x in q['reports'] if x['test']=='independent_native_full_restore'];assert len(archives)==len(restores)==1
 bundle=Path(archives[0]['bundle']);assert bundle.is_relative_to(e.NAS/'inbox/qualification') and not bundle.is_symlink()
 e.verify_committed(bundle,rehash=True);m=e.read(bundle/'SOURCE_MANIFEST.json');receipt=restores[0];dest=Path(receipt['destination'])
 assert dest.parent==R/'recovery' and dest.name=='PROTOCOL_FULL_NATIVE_'+rev and not dest.is_symlink() and dest.resolve()==dest
 expected={x['relative_path'] for x in m['members']};actual={x.relative_to(dest).as_posix() for x in dest.rglob('*') if x.is_file()};assert expected==actual
 assert all(not x.is_symlink() and (x.is_file() or x.is_dir()) for x in dest.rglob('*'))
 captured={x['relative_path']:x for x in receipt['rows']};members=[]
 for x in m['members']:
  native=e.safe(dest,x['relative_path']);back=e.safe(bundle/'tree',x['relative_path']);assert e.hash_file(native)==x['sha256']==e.hash_file(back)
  before=e.identity(native);assert e.same_source(before,captured[x['relative_path']]['identity'])
  members.append({'relative_path':x['relative_path'],'sha256':x['sha256'],'size':x['size'],'native_identity_before_retirement':before,'backing_true164_file':str(back),'both_current_full_SHA_match':True})
 rows.append({'qualification_revision':rev,'historical_native_restore':str(dest),'historical_receipt_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'backing_bundle':str(bundle),'COMMIT_sha256':hashlib.sha256((bundle/'COMMIT.json').read_bytes()).hexdigest(),'members':members,'planned_logical_bytes':sum(x['size'] for x in members)})
intent={'status':'ALL_SELECTED_CURRENT_NATIVE_AND_TRUE164_FULL_SHA_VERIFIED','rows':rows,'original_asset_source_mutations':0,'only_own_closed_synthetic_native_restores':True,'observed_unix':time.time()}
(R/'control/CLOSED_QUALIFICATION_RESTORE_RETIREMENT_INTENT.json').write_text(json.dumps(intent,indent=2)+'\n')
freed=0
for row in rows:
 dest=Path(row['historical_native_restore']);assert dest.resolve()==dest and dest.parent==R/'recovery'
 for x in row['members']:
  p=e.safe(dest,x['relative_path']);assert e.same_source(e.identity(p),x['native_identity_before_retirement']);freed+=p.stat().st_blocks*512;p.unlink()
 for directory in sorted((p for p in dest.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):directory.rmdir()
 dest.rmdir();row['native_restore_retired_after_current_full_SHA']=True
intent.update(status='PASS_OWN_CLOSED_SYNTHETIC_RESTORES_RETIRED',rows=rows,freed_native_allocated_bytes=freed,historical_ext4_restore_receipts_preserved=True,current_native_restore_present=False,full_bytes_currently_readable_from_true164=True)
proof.write_text(json.dumps(intent,indent=2)+'\n');print(json.dumps({'status':intent['status'],'restores':len(rows),'freed_native_allocated_bytes':freed}))
