from pathlib import Path
import sys,json,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy as e
src=R/'synthetic';p=src/'kernelslist.g';r=e.identity(p);r.update(relative_path='kernelslist.g',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),header_prefix_hex=p.read_bytes().hex())
m={'payload_kind':'CAS_FILES_V1','source_backend':'native','freeze_status':'FROZEN_SYNTHETIC_QUALIFICATION','primary_asset_id':'NATIVE_BACKEND_PROTOCOL_V3','object_id':hashlib.sha256(e.canon(r)).hexdigest(),'source_root':str(src),'source_root_identity':e.identity(src),'members':[r],'source_data_bytes':r['size'],'ordered_kernel_members':[],'entry_name':'NOT_AN_APPLICATION_INPUT','commandlist_bytes_hex':'','new_true164_bundle':'/home/shared/huangrulin/traces/inbox/qualification/NATIVE_BACKEND_PROTOCOL_V3','reuse':False}
proof=e.migrate(m);e.verify_committed(Path(proof['bundle']),rehash=True)
(R/'control/NATIVE_BACKEND_QUALIFICATION.json').write_text(json.dumps({'status':'PASS','receipt':proof,'source_lease_used':True,'scientific_starts':0},indent=2)+'\n');print('NATIVE_BACKEND_PASS',flush=True)
