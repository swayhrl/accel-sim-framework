"""Minimal three-input entry for explicitly approved frozen cold batches.

This does not grant permission to migrate an arbitrary path. Current Source
admission is deliberately the two BA-approved V3 roots; TLS, E2 and C16 refuse.
"""
import argparse,hashlib,json,pathlib,shlex,subprocess,sys
D=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('source_root');p.add_argument('target164_root');p.add_argument('manifest');p.add_argument('--binding',default=str(D/'SOURCE_HANDOFF.json'));p.add_argument('--execute',action='store_true');p.add_argument('--reference-only',action='store_true');p.add_argument('--existing-receipt');a=p.parse_args()
b=json.loads(pathlib.Path(a.binding).read_bytes())
matches=[x for x in b['batches'] if x['source_root']==a.source_root and x['target_native164_root_PROPOSED_NOT_RESERVED']==a.target164_root]
assert len(matches)==1,'exact approved cold Source/true164 binding required; protected workflows cannot use this entry'
x=matches[0];assert x['batch'] in ['V3_463600cb','V3_46bf3a69']
assert hashlib.sha256(pathlib.Path(a.manifest).read_bytes()).hexdigest()==x['manifest_sha256']
print(json.dumps({'source_root':a.source_root,'target164_root':a.target164_root,'manifest_sha256':x['manifest_sha256'],
                  'outputs':['postcheck.tar.zst OR verified existing164 reference','SOURCE_MANIFEST','PATH_MAP','ARCHIVE_SHA256SUMS','RESTORE.sh','DONE.json'],
                  'source_release_by_target':False,'execute':a.execute}),flush=True)
if a.execute or a.reference_only:
 trusted=json.loads(pathlib.Path(a.existing_receipt).read_bytes()) if a.existing_receipt else None
 if trusted:
  assert trusted['source_root']==a.source_root and trusted['native164_root']==a.target164_root
  assert trusted['BA_frozen_metadata_gzip_sha256']==x['manifest_sha256']
 code=r'''
import pathlib,json,hashlib,os,subprocess,time,fcntl
root=pathlib.Path(__ROOT__);assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'
proof=__TRUSTED__
parent=root if root.exists() else root.parent.parent.parent
m=json.loads(subprocess.check_output(['findmnt','-J','-T',str(parent),'-o','TARGET,SOURCE,FSTYPE']))['filesystems'][0]
assert (m['target'],m['source'],m['fstype'])==('/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs')
p=root/'DONE.json'
if not p.exists():print(json.dumps({'verified_reference_exists':False,'partial_or_reservation_exists':root.exists()}))
else:
 assert proof is not None,'existing object requires the immutable Git-readback receipt; never restream'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==proof['DONE_sha256']
 d=json.loads(p.read_bytes());assert d['source_root']==__SOURCE__ and d['BA_frozen_metadata_gzip_sha256']==__PIN__ and d['persistent_copy_is_genuine164'] is True
 assert d['archive_sha256']==proof['archive_sha256']
 lock=os.open('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock',os.O_RDONLY|os.O_NOFOLLOW);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 archive=root/'postcheck.tar.zst';h=hashlib.sha256();n=0;start=time.monotonic()
 with archive.open('rb') as f:
  while chunk:=f.read(1024**2):
   h.update(chunk);n+=len(chunk);time.sleep(max(0,n/(8*1024**2)-(time.monotonic()-start)))
 assert n==d['archive_bytes'] and h.hexdigest()==d['archive_sha256']
 os.close(lock)
 print(json.dumps({'verified_reference_exists':True,'native164_root':d['native164_root'],'archive_sha256':h.hexdigest(),'archive_bytes':n,'source_transferred_bytes':0,'source_originals':'UNCHANGED'}))
'''
 for key,value in [('__ROOT__',a.target164_root.replace('/home/shared','/root/share/mnt164',1)),('__SOURCE__',a.source_root),('__PIN__',x['manifest_sha256']),('__TRUSTED__',trusted)]:code=code.replace(key,repr(value))
 result=subprocess.run(['ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','hrl-174-new','timeout 120s python3 -B -'],input=code.encode(),capture_output=True,timeout=135,check=True)
 reference=json.loads(result.stdout);print(json.dumps(reference),flush=True)
 if reference['verified_reference_exists']:raise SystemExit(0)
 assert not a.reference_only,'no complete existing reference; no data sent'
 assert not reference['partial_or_reservation_exists'],'owned partial requires validation-only reconciliation; never restream automatically'
if a.execute:
 assert pathlib.Path(a.manifest).resolve()==(D/(x['batch']+'_METADATA.jsonl.gz')).resolve(),'use exact cached BA manifest, no implicit copy'
 subprocess.run([sys.executable,str(D/'run_cold_batch.py'),x['batch'].split('_',1)[1]],check=True)
