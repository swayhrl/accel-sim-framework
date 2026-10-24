"""Cold-place completed, immutable audit ledgers; preserve their original paths."""
from pathlib import Path
import sys,json,hashlib,os,time
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy as e
assert (R/'control/174_HASH_COMPLETE.json').exists() and (R/'control/174-new_HASH_COMPLETE.json').exists()
assert (R/'control/USER_BULK_4080_AND_IO_AUTHORIZATION_20261024.json').exists()
e.Resources()(True);v=e.v9();cold=e.NAS/'receipts/closed_control_objects_20261024_v1';cold.mkdir(exist_ok=True)
names=['174_HASH_COMPLETE.json','174-new_HASH_COMPLETE.json','174_FROZEN_METADATA.json','174-new_FROZEN_METADATA.json','174_FILE_SHA.jsonl','174-new_FILE_SHA.jsonl']
rows=[]
for name in names:
    source=R/'control'/name
    if source.is_symlink():
        assert source.resolve().is_relative_to(cold.resolve());continue
    before=e.identity(source);assert before['type']=='file'
    data=source.read_bytes();sha=hashlib.sha256(data).hexdigest();dest=cold/(sha+'_'+name)
    assert e.same_source(before,e.identity(source))
    e.publish_bytes(dest,data,v)
    s=dest.stat();assert e.hash_file(dest)==sha and [dest.stat().st_dev,dest.stat().st_ino,dest.stat().st_size,dest.stat().st_mtime_ns]==[s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]
    assert e.same_source(before,e.identity(source)) and hashlib.sha256(source.read_bytes()).hexdigest()==sha
    intent={'name':name,'sha256':sha,'bytes':len(data),'original_identity':before,'true164_path':str(dest).replace('/root/share/mnt164','/home/shared',1),'closed_reopen_full_SHA_verified':True,'source_payload_files_modified':0,'kind':'OWN_CLOSED_AUDIT_CONTROL_ONLY'}
    proof=cold/(name+'.OFFLOAD_PROOF.json');e.publish_bytes(proof,e.canon(intent),v)
    link=source.with_name(source.name+'.cold-link-writing')
    assert not os.path.lexists(link);link.symlink_to(dest)
    assert e.same_source(before,e.identity(source));os.replace(link,source)
    assert source.resolve()==dest and e.hash_file(source)==sha
    rows.append(intent);print(json.dumps({'cold_placed':name,'bytes':len(data)}),flush=True)
receipt={'status':'PASS_CLOSED_CONTROL_COLD_PLACEMENT','rows':rows,'original_paths_preserved_as_symlinks':True,'source_payload_files_modified':0,'other_project_files_modified':0,'observed_unix':time.time()}
(R/'control/CLOSED_CONTROL_OFFLOAD.json').write_text(json.dumps(receipt,indent=2)+'\n')
