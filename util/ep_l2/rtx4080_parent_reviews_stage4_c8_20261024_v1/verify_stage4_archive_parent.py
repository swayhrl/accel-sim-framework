"""Independent full archive/readback/native materialization; no ELF execution."""
from pathlib import Path
import sys,json,hashlib,tarfile,os,time,shutil
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy_v8 as e
T=e.NAS/'rtx4080_sm89/bulk_20261024_v1/objects/stage_evidence_ada_native_stage4_174new_20261024_v1'
D=Path('/root/data/ada_stage4_parent_cold_restore_20261024_v1')
resume_owned=D.exists();assert not D.is_symlink()
expected={'payload.tar':'ba7bd6c9005a884fdfd6b8ce19910518a3806a3a35846f2ce3ac5e1a26d9e83c','MANIFEST.json':'077a0285542c78004f9b3ab04b541274a185c638f22f89f5c280ee3ee01333c0','COMMIT.json':'ec5a3be37933c214215bbc8b9f0d9cf0eeaaec0f8cb9e56e61a043f23d339839'}
gate=e.Resources();before=gate(True)
for name,want in expected.items():assert not(T/name).is_symlink() and e.hash_file(T/name,rate=15*e.MIB,gate=gate)==want
c=e.read(T/'COMMIT.json');m=e.read(T/'MANIFEST.json');assert c['archive_sha256']==expected['payload.tar']and c['manifest_sha256']==expected['MANIFEST.json']and c['kind']==m['kind']=='ENGINEERING_STAGE_NOT_FORMAL_WORKLOAD'and m['source_keep']
assert e.hash_file(T/'CLOSED_READBACK.json',rate=0)==c['readback_sha256']
rows={x['member']:x for x in m['files']};assert len(rows)==len(m['files'])==468
regular_bytes=sum(x['identity']['size']for x in rows.values());assert regular_bytes==104906875
if resume_owned:
 assert {str(p.relative_to(D))for p in D.rglob('*')if p.is_file()}==set(rows),'owned partial membership drift'
 for name,row in rows.items():
  p=e.safe(D,name);assert not p.is_symlink()and p.stat().st_size==row['identity']['size']and e.hash_file(p,rate=0)==row['sha256']
else:D.mkdir(mode=0o700)
seen=set();verified=[]
class Limited:
 def __init__(self,f):self.f=f;self.n=0;self.t=time.monotonic()
 def read(self,n=-1):
  b=self.f.read(n);self.n+=len(b);time.sleep(max(0,self.n/(15*e.MIB)-(time.monotonic()-self.t)));gate();return b
with(T/'payload.tar').open('rb')as raw:
 with tarfile.open(fileobj=Limited(raw),mode='r|',ignore_zeros=True,errorlevel=2)as tf:
  for ti in tf:
   name=ti.name;assert ti.isfile()and name in rows and name not in seen;row=rows[name];assert ti.size==row['identity']['size']
   out=e.safe(D,name);out.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();size=0
   f=None if resume_owned else out.open('xb')
   try:
    with tf.extractfile(ti)as inp:
     for b in iter(lambda:inp.read(e.MIB),b''):
      if f:f.write(b)
      h.update(b);size+=len(b)
    if f:f.flush();os.fsync(f.fileno())
   finally:
    if f:f.close()
   assert size==ti.size and h.hexdigest()==row['sha256']and e.hash_file(out,rate=0)==row['sha256']
   ident=row['identity'];os.chown(out,ident['uid'],ident['gid']);out.chmod(ident['mode']&0o7777);os.utime(out,ns=(ident['mtime_ns'],ident['mtime_ns']))
   assert out.stat().st_dev==2128;verified.append({'member':name,'bytes':size,'sha256':row['sha256'],'native_ext4_full_SHA_reopen':True});seen.add(name)
assert seen==set(rows)
index={}
for row in verified:index.setdefault(row['sha256'],[]).append(D/row['member'])
refpath=D/'174new/ada_stage4_native_closeout_pack_20261024_v1/OBSERVED_DEPENDENCY_RESTORE_REFERENCES.json';refs=e.read(refpath)['files'];unique={}
for ref in refs:
 p=e.safe(D/'174new'/ref['archive_ref']['pack'],ref['archive_ref']['path']);assert p.stat().st_size==ref['bytes']and e.hash_file(p,rate=0)==ref['sha256']
 if ref['original_path']in unique:assert unique[ref['original_path']]['sha256']==ref['sha256']
 unique[ref['original_path']]=ref
cases=[('jit_maps_r3','3ca5327ee4124d99a6725644c1bf8b7c'),('warpsync_maps_r3','6de4f2ae916c4d9181c14d55d19f43ba'),('legacy65_r2','86b6f52282c943d69b377f4332a4246a')]
caseproof=[]
for label,uid in cases:
 bname='ep_l2_main_ada_'+label+'_compat_20261024_v1';matches=list(D.glob('174new/*/*/'+bname+'/run/'+uid+'/raw.log'));assert len(matches)==1;B=matches[0].parent.parent.parent
 s=e.read(B/'control/FROZEN_SPEC.json');O=B/'run'/uid;exit=e.read(O/'EXIT.json');live=Path('/root/data')/bname/'run'/uid
 assert e.hash_file(O/'raw.log',rate=0)==exit['raw_sha256']==e.hash_file(live/'raw.log',rate=0)
 assert e.hash_file(O/'PARENT_INDEPENDENT_TERMINAL_JOIN.json',rate=0)==e.hash_file(live/'PARENT_INDEPENDENT_TERMINAL_JOIN.json',rate=0)
 u=e.read(O/'MAP_OBSERVATIONS/UNION.json')
 for name,observed in u['mapped_dependency_union'].items():
  want=observed['sha256'];assert s['pinned_files'][name]==want and want in index,'missing archived mapped dependency blob '+name
  blob=index[want][0]
  if name not in unique:unique[name]={'original_path':name,'sha256':want,'bytes':blob.stat().st_size,'mode':Path(name).stat().st_mode&0o7777,'source_of_mode':'Current frozen mapped file mode; SHA bound by source spec and archived blob','archive_resolved_path':str(blob.relative_to(D))}
 caseproof.append({'root':bname,'run_uuid':uid,'raw_sha256':exit['raw_sha256'],'parent_join_sha256':e.hash_file(O/'PARENT_INDEPENDENT_TERMINAL_JOIN.json',rate=0),'mapped_paths':len(u['mapped_dependency_union']),'all_observed_paths_resolve_exact_archived_blobs':True})
restored=[]
for name,ref in sorted(unique.items()):
 assert name.startswith('/')and ref['sha256']in index;blob=index[ref['sha256']][0];dest=e.safe(D/'runtime_original_path_views',name[1:]);dest.parent.mkdir(parents=True,exist_ok=True)
 with blob.open('rb')as inp,dest.open('xb')as out:
  for b in iter(lambda:inp.read(e.MIB),b''):out.write(b)
  out.flush();os.fsync(out.fileno())
 dest.chmod(ref['mode']);assert dest.stat().st_size==ref['bytes']and e.hash_file(dest,rate=0)==ref['sha256'];restored.append({'original_path':name,'native_restored_path':str(dest),'sha256':ref['sha256'],'bytes':ref['bytes'],'mode':ref['mode'],'full_SHA_reopen':True})
allocated=sum(p.lstat().st_blocks*512 for p in D.rglob('*')if not p.is_symlink());assert allocated<=256*e.MIB
proof={'status':'PASS_PARENT_STAGE4_FULL_TAR_MEMBERS_NATIVE_RESTORE_AND_ACTUAL_MAPPING_BLOBS','target':str(T),'archive_SHA_pins':expected,'all_members':len(verified),'original_regular_bytes':regular_bytes,'ready_plan_payload_bytes':104803071,'additional_freeze_metadata_bytes':regular_bytes-104803071,'resumed_after_rehashing_exact_owned_partial_restore':resume_owned,'native_materialization':str(D),'native_device':D.stat().st_dev,'native_allocated_bytes_including_runtime_views':allocated,'members':verified,'cases':caseproof,'runtime_original_path_views':restored,'full_tar_and_every_member_SHA_reopen':True,'strict_full_tar_header_scan_through_zero_padding':True,'three_case_runtime_blobs_all_resolved':True,'source_keep':True,'original_runtime_paths_modified':False,'GPU_or_simulator_executed':False,'engineering_not_formal_workload':True,'campaign_consumed':7,'campaign_ceiling':8,'resources_before':before,'resources_after':gate(True),'observed_unix':time.time()}
p=R/'control/ADA_STAGE4_PARENT_ARCHIVE_FULL_READBACK.json';assert not p.exists();p.write_text(json.dumps(proof,indent=2)+'\n')
v=e.v9();e.publish_bytes(T/'PARENT_FULL_NATIVE_READBACK.json',p.read_bytes(),v);assert e.hash_file(T/'PARENT_FULL_NATIVE_READBACK.json',rate=0)==e.hash_file(p,rate=0)
print(json.dumps({'status':proof['status'],'members':len(verified),'mapped_runtime_paths_restored':len(restored),'native_allocated_bytes':allocated}))
