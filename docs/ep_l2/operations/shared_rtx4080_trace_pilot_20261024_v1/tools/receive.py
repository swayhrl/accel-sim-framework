#!/usr/bin/env python3
import pathlib,fcntl,subprocess,hashlib,json,tarfile,os,time
BASE=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/pilot_20261024_v1')
expected='17e4fa4b946ccbd2e3472d37d821bcb5488ed939fc0e0e93cd7bf4dea94dcac3'
files=['/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TLS_V10_SOURCE_SENDER.lock','/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock']
locks=[]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
 return h.hexdigest()
try:
 for name in files:
  f=open(name,'a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 free=os.statvfs('/root/data').f_bavail*os.statvfs('/root/data').f_frsize
 assert free>=7*1024**3,('requires5GiB safety+2GiB foreign reserve',free)
 assert not BASE.exists(),'immutable target exists'
 BASE.mkdir(parents=True)
 a=BASE/'payload.tar.incoming'
 with a.open('xb') as out:
  p=subprocess.run(['ssh','-o','BatchMode=yes','gpu109','nice -n 15 ionice -c2 -n7 cat /data/c16/rtx4080_asset_pilot_20261024_v1.tar'],stdout=out,timeout=90)
  out.flush();os.fsync(out.fileno())
 assert p.returncode==0 and a.stat().st_size==13537280
 assert sha(a)==expected
 archive=BASE/'payload.tar';a.rename(archive)
 with tarfile.open(archive) as t:
  for x in t.getmembers():
   assert not x.issym() and not x.islnk()
   assert not pathlib.PurePosixPath(x.name).is_absolute() and '..' not in pathlib.PurePosixPath(x.name).parts
  t.extractall(BASE/'expanded')
 bundle=BASE/'expanded/rtx4080_asset_pilot_20261024_v1'
 manifest=bundle/'MANIFEST.json';assert sha(manifest)=='c04d34aa09a9642110727ab9e5bd57afbbf291b06767ac8bff36a632a4afc403'
 m=json.loads(manifest.read_text())
 for x in m['files']:
  p=bundle/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],x
 receipt={'status':'COMMITTED_VERIFIED','utc_unix':time.time(),'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':expected,'manifest_sha256':sha(manifest),'bundle':str(bundle),'verified_payload_files':len(m['files']),'verified_payload_bytes':sum(x['bytes'] for x in m['files']),'source_keep':True,'release_bytes':0,'architecture':'sm89','simulation_qualification':'HOLD','ssd_staging_bytes':0}
 (BASE/'COMMIT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt))
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
