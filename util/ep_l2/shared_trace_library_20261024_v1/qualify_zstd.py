from pathlib import Path
import sys,json,hashlib,tarfile,subprocess
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy as e
src=R/'synthetic';small=src/'zstd_payload.bin'
if not small.exists():small.write_bytes(bytes(range(256))*32)
tar=src/'zstd_test.tar';archive=src/'zstd_test_v3b.tar.zst'
if not tar.exists():
 with tarfile.open(tar,'w') as tf:tf.add(small,arcname='safe/zstd_payload.bin')
if not archive.exists():
 with archive.open('xb') as f:subprocess.run([str(R/'tools/zstd'),'-q','-c',str(tar)],stdout=f,check=True)
row=e.identity(small);row.update(relative_path='safe/zstd_payload.bin',archive_member='safe/zstd_payload.bin',sha256=hashlib.sha256(small.read_bytes()).hexdigest(),header_prefix_hex=small.read_bytes()[:128].hex())
m={'payload_kind':'CAS_FILES_V1','source_backend':'archive','freeze_status':'FROZEN_SYNTHETIC_QUALIFICATION','primary_asset_id':'ZSTD_PROTOCOL_V3','object_id':hashlib.sha256(e.canon(row)).hexdigest(),'source_root':str(src),'source_root_identity':e.identity(src),'archive_path':str(archive),'archive_identity':e.identity(archive),'members':[row],'source_data_bytes':row['size'],'ordered_kernel_members':[],'entry_name':'NOT_AN_APPLICATION_INPUT','commandlist_bytes_hex':'','new_true164_bundle':'/home/shared/huangrulin/traces/inbox/qualification/ZSTD_PROTOCOL_V3','reuse':False}
r=e.migrate(m,testing=True);e.verify_committed(Path(r['bundle']),rehash=True)
(R/'control/ZSTD_PROTOCOL_QUALIFICATION.json').write_text(json.dumps({'status':'PASS','receipt':r,'original_source_writes':0,'scientific_starts':0},indent=2)+'\n');print('ZSTD_PROTOCOL_PASS',flush=True)
