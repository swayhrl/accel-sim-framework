"""Independent metadata/receipt closure after the finite exact retirement."""
from local_common import *
CODE=r'''
import sys, pathlib,json,hashlib,gzip,base64,time,os
sys.path.insert(0,'/root/data/research_asset_verified_offload_20261024_v1/tools')
import retire_174new_build_duplicates as r
r.q.mount_check(); raw=(r.OUT/'QUALIFIED.json').read_bytes();m=json.loads(raw)
names=['QUALIFIED.json','RESTORE.py','COMMIT.json','INTENT.json','DONE.json','RESTORE_TEST.json','RESTORE_TEST_DONE.json','USER_AUTHORIZATION_174NEW.md','OLD174_READER_AUDIT.json','RESTORE_TEST_ADMISSION_DEVIATION.json','EXECUTED_RETIRER.py']
controls={};payload={}
for n in names:
 b=(r.OUT/n).read_bytes();assert (r.DEST/n).read_bytes()==b,'durable control mismatch '+n
 controls[n]=hashlib.sha256(b).hexdigest()
 if n.endswith('.json') and n!='QUALIFIED.json':payload[n]=json.loads(b)
assert payload['COMMIT.json']['qualified_sha256']==hashlib.sha256(raw).hexdigest()
assert payload['INTENT.json']['qualification_sha256']==hashlib.sha256(raw).hexdigest()
done=payload['DONE.json']; records=[]
local_names={p.name for p in (r.OUT/'per_file').iterdir()}
nas_names={p.name for p in (r.DEST/'per_file').iterdir()}
expected={'%06d.%s.json'%(k,typ) for k in range(len(m['files'])) for typ in ['INTENT','DONE']}
assert local_names==nas_names==expected,'extra/missing per-file transaction receipt'
for k,x in enumerate(m['files']):
 pair={}
 for typ in ['INTENT','DONE']:
  n='%06d.%s.json'%(k,typ);b=(r.OUT/'per_file'/n).read_bytes()
  assert (r.DEST/'per_file'/n).read_bytes()==b,'per-file durable receipt mismatch'
  pair[typ]=json.loads(b)
 intent=pair['INTENT'];d=pair['DONE'];p=pathlib.Path(x['source']);a=pathlib.Path(x['archive']['path'])
 assert not os.path.lexists(p) and p.parent.is_dir(),'exact retired file reappeared or parent lost'
 assert intent['source']==d['source']==x['source'] and intent['sha256']==d['sha256']==x['sha256']
 assert intent['identity']==x['identity'] and intent['archive_identity']==x['archive']['identity']
 assert r.q.identity(a)==x['archive']['identity'],'archive identity changed since final full SHA'
 assert d['logical_bytes']==x['identity']['size'] and d['allocated_bytes']==x['identity']['blocks']*512
 assert d['absent_after_unlink'] and d['finished_unix']>=intent['created_unix']
 records.append(pair)
assert sum(z['DONE']['allocated_bytes'] for z in records)==done['allocated_bytes_unlinked']==m['allocated_bytes']
assert sum(z['DONE']['logical_bytes'] for z in records)==done['logical_bytes_unlinked']==m['logical_bytes']
assert done['files']==len(records)==len(m['files']) and done['all_whitelisted_paths_absent']
assert payload['RESTORE_TEST.json']['closed_native_full_SHA_and_numeric_metadata'] and payload['RESTORE_TEST_DONE.json']['absent']
assert not list(r.OUT.glob('FAILURE_*.json')),'execution failure retained: requires review'
j=b''.join((json.dumps(z,sort_keys=True,separators=(',',':'))+'\n').encode() for z in records)
proof={'schema':'INDEPENDENT_174NEW_EXACT_RETIREMENT_CLOSURE_V1','status':'PASS','status_scope':'exact content-reference, per-file retirement and durable receipt closure; not a claim of flawless execution admission','recorded_test_admission_deviation':'RESTORE_TEST_ADMISSION_DEVIATION.json','unix':time.time(),'files':len(records),'unclosed_file_intents':0,'genuine164_entry':str(r.DEST),'closed_control_sha256':controls,'per_file_journal_sha256':hashlib.sha256(j).hexdigest(),'per_file_journal_uncompressed_bytes':len(j),'archive_current_identity_matches_final_full_SHA_proof':True,'payload_bodies_rehashed_by_this_independent_audit':False,'all_local_whitelisted_files_absent_and_parents_preserved':True,'old_retirements_replayed':False,'old174_Source_files_unlinked':0,'new_frozen115_archive_bytes':0,'SSD_free_now':r.free(),'IO_now':pathlib.Path('/proc/pressure/io').read_text()}
r.pair('INDEPENDENT_CLOSURE.json',proof)
print(json.dumps({'proof':proof,'controls':payload,'restore_py':(r.DEST/'RESTORE.py').read_text(),'per_file_journal_gzip_b64':base64.b64encode(gzip.compress(j,mtime=0)).decode()}))
'''

def main():
    x=remote('hrl-174-new',CODE,240)
    target=R/'t2/reclaim_174new';target.mkdir(exist_ok=True)
    for n,v in x['controls'].items():save('t2/reclaim_174new/'+n,v)
    save('t2/reclaim_174new/INDEPENDENT_CLOSURE.json',x['proof'])
    (target/'RESTORE.py').write_text(x['restore_py'],encoding='utf-8')
    (target/'PER_FILE_INTENT_DONE.jsonl.gz').write_bytes(base64.b64decode(x['per_file_journal_gzip_b64']))
    accounting=load(R/'t2/RECLAIM_ACCOUNTING.json')
    accounting['additional_174new_verified_copy_retirement']=x['controls']['DONE.json']
    accounting['additional_174new_independent_closure']='reclaim_174new/INDEPENDENT_CLOSURE.json'
    save('t2/RECLAIM_ACCOUNTING.json',accounting)
    print(json.dumps({k:x['proof'][k] for k in ['status','files','unclosed_file_intents','SSD_free_now']}))

if __name__=='__main__':main()
