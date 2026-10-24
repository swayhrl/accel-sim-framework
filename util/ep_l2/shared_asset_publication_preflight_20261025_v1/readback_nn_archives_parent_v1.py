"""Full true164 outer/inner archive and native member readback. No code executed."""
from pathlib import Path
import sys,json,tarfile,gzip,io,hashlib,os,time
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy_v8 as e
D=Path('/root/data/nn_parent_cold_review_20261025_v1');assert not D.exists();D.mkdir(mode=0o700)
cases=[
 ('base','stage_evidence_nn_ada8_observed_io_109_20261024_v1','b632d9c705d2d38d178aafbf892cfad4ba35522cf6061de4894e6623059abffb','fdba1d82654cbae7e0912114073b0ba1a3c844495e71dcf65821bb9071dfc2b1','766951ba6e8ea0fa23c02bc89691c8aa053ad43d6442c134a23bf9fae330b061',7,'NN_A3_COMPLETE_CODE_RAW_CONTROL_V1.tar.gz','1baeeca6872f5e0f92616157598960a25880486087b8a3120da13afd900dff11',480,'ada_call_snapshot_nn_20261024_v1','PACKAGE_MEMBER_MANIFEST_V1.json'),
 ('increment','stage_evidence_nn_ada8_observed_io_v4_increment_20261024_v1','b347bc0bac731b119bc1e8dfd9a6b4a59635ae97f25376ae80c65309f2c75741','e01f7d49cc1cc42e9756df0c67337b9d26fc2293b6f135d6f6b04f3854d6fe22','4f6552c3fb491c731e0a2ca1bf76741cd6c833ff87db69b1f5461b90a7cc04e8',5,'NN_A3_V4_ADMISSION_INCREMENT_V1.tar.gz','8b24e92d5c6df505d1c3baefe75fa65ecb5301018a265b7007a9191ddbc65e8d',133,'nn_A3_V4_admission_increment_20261024_v1','INCREMENT_MEMBER_MANIFEST_V1.json')]
gate=e.Resources();before=gate(True);reports=[]
def write_checked(path,b,want):
 assert hashlib.sha256(b).hexdigest()==want;path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 assert path.stat().st_dev==2128 and e.hash_file(path,rate=0)==want
for label,obj,tarsha,msha,csha,nouter,gzname,gzsha,ninner,prefix,manifestname in cases:
 T=e.NAS/'rtx4080_sm89/bulk_20261024_v1/objects'/obj
 for name,want in [('payload.tar',tarsha),('MANIFEST.json',msha),('COMMIT.json',csha)]:assert e.hash_file(T/name,rate=15*e.MIB,gate=gate)==want
 m=e.read(T/'MANIFEST.json');c=e.read(T/'COMMIT.json');assert c['archive_sha256']==tarsha and c['manifest_sha256']==msha and c['kind']==m['kind']=='ENGINEERING_STAGE_NOT_FORMAL_WORKLOAD'and m['source_keep']
 assert e.hash_file(T/'CLOSED_READBACK.json',rate=0)==c['readback_sha256']
 expected={x['member']:x for x in m['files']};assert len(expected)==nouter;seen=set();outer=D/(label+'_outer')
 with tarfile.open(T/'payload.tar','r:',ignore_zeros=True,errorlevel=2)as tf:
  for ti in tf:
   assert ti.isfile()and ti.name in expected and ti.name not in seen
   row=expected[ti.name];assert ti.size==row['identity']['size'];b=tf.extractfile(ti).read()
   write_checked(e.safe(outer,ti.name),b,row['sha256']);seen.add(ti.name)
 assert seen==set(expected)
 matches=list(outer.rglob(gzname));assert len(matches)==1;gz=matches[0];assert e.hash_file(gz,rate=0)==gzsha
 expanded=gzip.decompress(gz.read_bytes());assert len(expanded)<128*e.MIB
 inner=D/(label+'_inner')
 with tarfile.open(fileobj=io.BytesIO(expanded),mode='r:',ignore_zeros=True,errorlevel=2)as tf:
  members=tf.getmembers();regular=[x for x in members if x.isfile()];assert len(regular)==ninner and all(x.isfile()or x.isdir()for x in members)
  names={x.name for x in regular};assert len(names)==ninner
  manifestpath=prefix+'/'+manifestname;info=json.loads(tf.extractfile(manifestpath).read());rows={prefix+'/'+x['path']:x for x in info['files']}
  assert names==set(rows)|{manifestpath}
  for ti in regular:
   b=tf.extractfile(ti).read();h=hashlib.sha256(b).hexdigest()
   if ti.name!=manifestpath:assert len(b)==rows[ti.name]['bytes']and h==rows[ti.name]['sha256']
   write_checked(e.safe(inner,ti.name),b,h)
 reports.append({'object':str(T),'outer_tar_sha256':tarsha,'manifest_sha256':msha,'commit_sha256':csha,'outer_members':nouter,'inner_gzip_sha256':gzsha,'inner_members':ninner,'inner_root':str(inner/prefix),'full_gzip_CRC_through_EOF':True,'all_member_SHA_native_reopen':True})
allocated=sum(p.lstat().st_blocks*512 for p in D.rglob('*'));assert allocated<256*e.MIB
proof={'status':'PARENT_TRUE164_NN_BASE_AND_V4_ALL625_OUTER_INNER_MEMBERS_NATIVE_FULL_SHA_PASS','reports':reports,'total_regular_members':625,'native_root':str(D),'native_device':D.stat().st_dev,'native_allocated_bytes':allocated,'source_keep':True,'restored_code_or_ELF_executed':False,'GPU_or_simulator_execution':False,'formal_or_consumer_admission':'PENDING_PARENT_SOURCE_AND_CPU_REPLAY_REVIEW','resources_before':before,'resources_after':gate(True),'verifier_sha256':e.hash_file(Path(__file__),rate=0),'unix':time.time()}
p=R/'control/NN_BASE_V4_PARENT_TRUE164_COLD_READBACK.json';assert not p.exists();p.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'status':proof['status'],'members':625,'allocated_bytes':allocated}))
