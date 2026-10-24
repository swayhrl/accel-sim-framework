"""Independent whole archive/member and all174 original-path view restoration."""
from pathlib import Path
import sys,json,tarfile,os,time,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy_v8 as e
T=e.NAS/'rtx4080_sm89/bulk_20261024_v1/objects/stage_evidence_ada9_native_consumer_174new_20261024_v1'
D=Path('/root/data/ada9_consumer_parent_cold_restore_20261024_v1');assert not D.exists()
pins={'payload.tar':'afd70bbd3af62d16aa9d70ccf6719b08545e46ba82bb2d41d4019250726af0a3','MANIFEST.json':'42eee19d6d9cec1884fa8d1a8a07c40b85c65fccff656147e773a6f443009dc4','COMMIT.json':'26ed2c9a00f0679c56d5b03ab8e0c99ec5bfe716474a4e12588e5825f20a9551'}
gate=e.Resources();before=gate(True)
for name,want in pins.items():assert e.hash_file(T/name,rate=15*e.MIB,gate=gate)==want
m=e.read(T/'MANIFEST.json');c=e.read(T/'COMMIT.json');assert m['kind']==c['kind']=='ENGINEERING_STAGE_NOT_FORMAL_WORKLOAD'and m['source_keep']
assert c['archive_sha256']==pins['payload.tar']and c['manifest_sha256']==pins['MANIFEST.json']and e.hash_file(T/'CLOSED_READBACK.json',rate=0)==c['readback_sha256']
rows={v['member']:v for v in m['files']};assert len(rows)==len(m['files'])==205
assert sum(v['identity']['size']for v in rows.values())==111099493
D.mkdir(mode=0o700);seen=set()
class Limited:
 def __init__(self,f):self.f=f;self.n=0;self.start=time.monotonic()
 def read(self,n=-1):
  b=self.f.read(n);self.n+=len(b);time.sleep(max(0,self.n/(15*e.MIB)-(time.monotonic()-self.start)));gate();return b
with(T/'payload.tar').open('rb')as raw:
 with tarfile.open(fileobj=Limited(raw),mode='r|',ignore_zeros=True,errorlevel=2)as tf:
  for ti in tf:
   assert ti.isfile()and ti.name in rows and ti.name not in seen;r=rows[ti.name];assert ti.size==r['identity']['size']
   out=e.safe(D,ti.name);out.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();size=0
   with tf.extractfile(ti)as inp,out.open('xb')as f:
    for b in iter(lambda:inp.read(e.MIB),b''):f.write(b);h.update(b);size+=len(b)
    f.flush();os.fsync(f.fileno())
   assert size==ti.size and h.hexdigest()==r['sha256']==e.hash_file(out,rate=0)and out.stat().st_dev==2128
   ident=r['identity'];os.chown(out,ident['uid'],ident['gid']);out.chmod(ident['mode']&0o7777);os.utime(out,ns=(ident['mtime_ns'],ident['mtime_ns']));seen.add(ti.name)
assert seen==set(rows)
P=D/'174new/ada9_native_result_engineering_pack_20261024_v1';mapping=e.read(P/'FROZEN_PATH_MAP.json');S=e.read(P/'native_root/control/FROZEN_SPEC.json')
assert mapping['spec_sha256']=='7ec0074f3286b3d13fc846c2bc9a6d4c799fb0423fca7eb96565d543646a4596'
assert e.hash_file(P/'native_root/control/FROZEN_SPEC.json',rate=0)==mapping['spec_sha256']
assert {r['source']:r['sha256']for r in mapping['pins']}==S['pinned_files']and len(mapping['pins'])==174
assert sum(r['bytes']for r in mapping['pins'])==101401136
restored=[]
for r in mapping['pins']:
 src=e.safe(P,r['member']);assert src.stat().st_size==r['bytes']and e.hash_file(src,rate=0)==r['sha256']
 assert r['source'].startswith('/');out=e.safe(D/'original_path_views',r['source'][1:]);out.parent.mkdir(parents=True,exist_ok=True)
 with src.open('rb')as inp,out.open('xb')as f:
  for b in iter(lambda:inp.read(e.MIB),b''):f.write(b)
  f.flush();os.fsync(f.fileno())
 os.chown(out,r['uid'],r['gid']);out.chmod(r['mode']);assert out.stat().st_size==r['bytes']and e.hash_file(out,rate=0)==r['sha256']and out.stat().st_dev==2128
 assert out.stat().st_mode&0o7777==r['mode'];restored.append({'original_path':r['source'],'native_path':str(out),'sha256':r['sha256'],'bytes':r['bytes'],'mode':r['mode']})
O=P/'native_root/run/5553b55c08224280afefe139c9c9333c';live=Path('/root/data/ep_l2_main_ada_tex37_ada9_compat_20261024_v1/run/5553b55c08224280afefe139c9c9333c')
assert e.hash_file(O/'raw.log',rate=0)==e.hash_file(live/'raw.log',rate=0)=='f80dcae774251b1a90f471fc6fe5d2461c72acd9c7d24b2a95b50d0bc873b33a'
assert e.hash_file(O/'PARENT_INDEPENDENT_TERMINAL_JOIN.json',rate=0)==e.hash_file(live/'PARENT_INDEPENDENT_TERMINAL_JOIN.json',rate=0)
u=e.read(O/'MAP_OBSERVATIONS/UNION.json');assert len(u['mapped_dependency_union'])==8
for name,r in u['mapped_dependency_union'].items():assert e.hash_file(e.safe(D/'original_path_views',name[1:]),rate=0)==r['sha256']==S['pinned_files'][name]
allocated=sum(p.lstat().st_blocks*512 for p in D.rglob('*'));assert allocated<256*e.MIB
proof={'status':'PARENT_FULL_ADA9_ARCHIVE_ALL205_MEMBERS_AND174_PIN_PATHS_NATIVE_COLD_RESTORE_PASS','target':str(T),'archive_SHA_pins':pins,'regular_members':205,'regular_archive_bytes':111099493,'full_tar_and_every_member_SHA_reopen':True,'strict_full_tar_headers_ignore_zeros_to_EOF':True,'native_root':str(D),'native_device':D.stat().st_dev,'native_allocated_bytes':allocated,'all174_original_path_views':restored,'pinned_path_view_bytes':101401136,'all_actual_eight_runtime_mapping_paths_restored':True,'original_runtime_paths_modified':False,'GPU_or_simulator_or_restored_ELF_execution':False,'campaign_consumed':8,'campaign_ceiling':8,'source_keep':True,'resources_before':before,'resources_after':gate(True),'verifier_sha256':e.hash_file(Path(__file__),rate=0),'unix':time.time()}
p=R/'control/ADA9_CONSUMER_PARENT_FULL_ARCHIVE_READBACK.json';assert not p.exists();p.write_text(json.dumps(proof,indent=2)+'\n');e.publish_bytes(T/'PARENT_FULL_NATIVE_READBACK.json',p.read_bytes(),e.v9());assert e.hash_file(T/'PARENT_FULL_NATIVE_READBACK.json',rate=0)==e.hash_file(p,rate=0)
print(json.dumps({'status':proof['status'],'members':205,'original_path_views':174,'native_allocated_bytes':allocated}))
