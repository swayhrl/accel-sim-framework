#!/usr/bin/env python3
"""Freeze a declared source/input evidence set to NAS. No GPU, no source deletion."""
import pathlib,json,hashlib,time,os,fcntl,sys,traceback
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');N=R/'nas_rtx4080'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,o):
 with p.open('x') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
job=json.loads(pathlib.Path(sys.argv[1]).read_text());source=pathlib.Path(job['source_manifest']);assert sha(source)==job['source_manifest_sha256'];members=json.loads(source.read_text())['members'];root=N/'inflight'/job['asset_id'];root.mkdir(exist_ok=False);lock=open(R/'control/RTX4080_LOCAL_IO.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:
 physical={};aliases=[]
 for index,m in enumerate(members):
  src=pathlib.Path(m['path']);assert src.is_file() and not src.is_symlink() and src.stat().st_size==m['bytes'];before=src.stat();digest=m['sha256'];h=hashlib.sha256();target=root/'files'/digest
  if digest not in physical:
   target.parent.mkdir(exist_ok=True)
   with src.open('rb') as inp,target.open('xb') as out:
    for b in iter(lambda:inp.read(65536),b''):h.update(b);out.write(b)
    out.flush();os.fsync(out.fileno())
   assert h.hexdigest()==digest and sha(target)==digest
   physical[digest]={'path':'files/'+digest,'bytes':m['bytes'],'sha256':digest}
  else:assert sha(src)==digest
  after=src.stat();assert (before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns),'source changed during archive'
  aliases.append(dict(m,member='files/'+digest,source_stat={'inode':before.st_ino,'bytes':before.st_size,'mtime_ns':before.st_mtime_ns}))
  progress=R/'control'/(job['asset_id']+'_PROGRESS.json');tmp=progress.with_suffix('.tmp');tmp.write_text(json.dumps({'members_complete':index+1,'members_total':len(members),'unique_bytes':sum(x['bytes'] for x in physical.values()),'utc_unix':time.time()}));os.replace(tmp,progress)
 save(root/'SOURCE_MEMBERS.json',{'schema':'SOURCE_EVIDENCE_LOGICAL_MEMBERS_V1','source_manifest_sha256':job['source_manifest_sha256'],'members':aliases,'logical_bytes':sum(x['bytes'] for x in members),'source_KEEP':True,'release_bytes':0})
 (root/'SOURCE_ORIGINAL_MANIFEST.json').write_bytes(source.read_bytes());(root/'archive_source_members_v1.py').write_bytes(pathlib.Path(__file__).read_bytes())
 asset={'schema':'SOURCE_EVIDENCE_ASSET_V1','kind':'SOURCE_EVIDENCE_NOT_FORMAL_WORKLOAD','asset_id':job['asset_id'],'members':len(aliases),'logical_bytes':sum(x['bytes'] for x in aliases),'unique_payload_files':len(physical),'unique_payload_bytes':sum(x['bytes'] for x in physical.values()),'source_manifest_sha256':job['source_manifest_sha256'],'writer_sha256':sha(pathlib.Path(__file__)),'no_gpu_execution':True,'source_KEEP':True,'release_bytes':0,'channel':'dedicated RTX Native174 leases +109 localIO +private V2 SSHFS;64KiB transfer blocks','source_note':job.get('source_note')};save(root/'ASSET.json',asset)
 files=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()];save(root/'SENDER_MANIFEST.json',{'asset':asset,'files':files})
 print(json.dumps({'status':'SOURCE_EVIDENCE_SENDER_COMPLETE','asset_id':job['asset_id'],'inflight':str(root.relative_to(N)),'sender_manifest_sha256':sha(root/'SENDER_MANIFEST.json')}))
except Exception as e:
 save(root/'FAILURE.json',{'status':'FAILED_RETAINED','error':repr(e),'traceback':traceback.format_exc(),'source_KEEP':True});print(json.dumps({'status':'FAILED_RETAINED','error':repr(e)}))
finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
