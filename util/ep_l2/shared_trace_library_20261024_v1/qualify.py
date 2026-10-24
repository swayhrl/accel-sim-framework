from pathlib import Path
import os,json,hashlib,tarfile,sys,importlib.util
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));e=__import__(os.environ.get('COPY_ENGINE_MODULE','library_copy'))
REV=os.environ.get('QUALIFY_REVISION','V1')
src=R/'synthetic';src.mkdir(exist_ok=True)
data=b'SM70_SHARED_ASSET_PROTOCOL\n'+bytes(range(256))*40000
f=src/'payload.bin'
if not f.exists():f.write_bytes(data)
entry=src/'kernelslist.g'
if not entry.exists():entry.write_text('payload.bin\n')
def manifest(root,members,name):
 rows=[]
 for p,rel in members:
  r=e.identity(p);r.update(relative_path=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),header_prefix_hex=p.read_bytes()[:128].hex());rows.append(r)
 m={'schema':'SHARED_SM70_CAS_PAYLOAD_PROTOCOL_V1','payload_kind':'CAS_FILES_V1','freeze_status':'FROZEN_SYNTHETIC_QUALIFICATION','primary_asset_id':name,'object_id':hashlib.sha256(e.canon(rows)).hexdigest(),'source_root':str(root),'source_root_identity':e.identity(root),'members':rows,'source_data_bytes':sum(r['size'] for r in rows),'ordered_kernel_members':[],'entry_name':'NOT_AN_APPLICATION_INPUT','commandlist_bytes_hex':'','new_true164_bundle':'/home/shared/huangrulin/traces/inbox/qualification/'+name,'reuse':False}
 return m
reports=[]
m=manifest(src,[(f,'payload.bin'),(entry,'kernelslist.g')],'REGULAR_PROTOCOL_'+REV)
try:e.migrate(m,testing=True,inject_after_ranges=1)
except RuntimeError as x:
 assert str(x)=='INJECTED_BOUNDED_OWN_RANGE_CRASH';reports.append({'test':'durable_interruption','status':'PASS_EXPECTED_UNCOMMITTED'})
else:raise AssertionError('interruption did not occur')
r=e.migrate(m,testing=True);assert r['source_disposition']=='SOURCE_KEEP';reports.append({'test':'resume_regular_and_full_SHA','status':'PASS','receipt':r})
r=e.migrate(m,testing=True);assert r['completed_transaction_reused'];reports.append({'test':'idempotent_commit_reuse','status':'PASS'})
e.verify_committed(Path(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1)),rehash=True)
arc=src/'source.tar.gz'
if not arc.exists():
 with tarfile.open(arc,'w:gz') as tf:tf.add(f,arcname='safe/payload.bin');tf.add(entry,arcname='safe/kernelslist.g')
m2=manifest(src,[(f,'safe/payload.bin'),(entry,'safe/kernelslist.g')],'ARCHIVE_PROTOCOL_'+REV)
m2.update(source_backend='archive',archive_path=str(arc),archive_identity=e.identity(arc))
for row in m2['members']:row['archive_member']=row['relative_path']
r=e.migrate(m2,testing=True);reports.append({'test':'archive_full_SHA_and_order','status':'PASS','receipt':r})
bundle=Path(m2['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1));e.verify_committed(bundle,rehash=True)
reports.append({'test':'path_traversal_rejection','status':'PENDING'})
try:e.safe(src,'../escape')
except RuntimeError:reports[-1]['status']='PASS'
else:raise AssertionError('unsafe path accepted')
res=e.restore_native(bundle/'tree',m2,R/('recovery/PROTOCOL_FULL_NATIVE_'+REV));reports.append({'test':'independent_native_full_restore','status':'PASS','receipt':res})
receipt=json.dumps({'status':'PASS','reports':reports,'synthetic_only':True,'scientific_starts':0},indent=2)+'\n'
(R/'control'/('PROTOCOL_QUALIFICATION_'+REV+'.json')).write_text(receipt)
(R/'control/PROTOCOL_QUALIFICATION.json').write_text(receipt)
print('PROTOCOL_QUALIFIED',flush=True)
