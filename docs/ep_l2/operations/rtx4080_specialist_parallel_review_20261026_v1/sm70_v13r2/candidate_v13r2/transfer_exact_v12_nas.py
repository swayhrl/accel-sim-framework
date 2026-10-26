from pathlib import Path
import sys,json,hashlib,fcntl,os,resource
CODE=Path(__file__).resolve().parent
EXPECTED_ENGINE='dee749ef1f9b35779347d5d310b9d5f6b9b102b18b26737ce3aaad96d20a6b01'
assert hashlib.sha256((CODE/'library_copy_v12_nas.py').read_bytes()).hexdigest()==EXPECTED_ENGINE
sys.path.insert(0,str(CODE));import library_copy_v12_nas as e
a=e.root_approval();e.enable_nas_only()
run=Path(sys.argv[1]);assert run.is_relative_to(e.NAS/'receipts') and run.is_dir()
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
os.environ['TMPDIR']=str(run/'tmp')
held=(e.TASK/'control/TRANSFER_DRIVER.lock').open('a');fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
manifest=e.read(e.EXACT_MANIFEST);e.qualified_archive_request({'manifest':manifest,'skip':{}})
result=e.migrate(manifest)
bundle=Path(manifest['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1))
proof=e.verify_committed(bundle)
receipt={'status':'PASS_COMMITTED_BATCH','manifest_sha256':e.EXACT_MANIFEST_SHA,'selected_engine_sha256':EXPECTED_ENGINE,'committed_object_restore_engine_sha256':hashlib.sha256((bundle/'trace_copy.py').read_bytes()).hexdigest(),'proof':proof,'result':result,'historical_manifests_modified':False,'Native_new_payload_bytes':0,'Source_KEEP':True}
tmp=run/'EXACT_BATCH_COMPLETE.writing';tmp.write_text(json.dumps(receipt)+'\n');os.replace(tmp,run/'EXACT_BATCH_COMPLETE.json')
print(json.dumps({'status':'PASS_COMMITTED_BATCH','manifest_sha256':e.EXACT_MANIFEST_SHA}),flush=True)
