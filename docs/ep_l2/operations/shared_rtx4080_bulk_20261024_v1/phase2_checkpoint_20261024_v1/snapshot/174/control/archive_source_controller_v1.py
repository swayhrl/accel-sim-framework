#!/usr/bin/env python3
"""Finite, single-object source evidence transaction under the existing RTX leases."""
import pathlib,json,hashlib,os,time,fcntl,signal,subprocess,sys,traceback
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):
   t=time.monotonic();h.update(b);time.sleep(max(0,len(b)/(15*1048576)-(time.monotonic()-t)))
 return h.hexdigest()
def save(p,o):
 with p.open('x') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
jobpath=sys.argv[1];ident=sys.argv[2];locks=[];status={'pid':os.getpid(),'start_ticks':pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],'asset_id':ident,'wait_deadline_unix':time.time()+7200,'no_gpu_execution':True}
save(C/(ident+'_CONTROLLER_IDENTITY.json'),status)
try:
 def alarm(a,b):raise TimeoutError('RTX source evidence lease wait7200s')
 signal.signal(signal.SIGALRM,alarm);signal.alarm(7200)
 for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
  f=open(C/name,'a');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX)
 signal.alarm(0)
 p=subprocess.run(['ssh','-n','-o','BatchMode=yes','gpu109','env -u LD_PRELOAD -u CUDA_INJECTION64_PATH python3 /data/c16/rtx4080_suite_fill_20261024_v1/control/archive_source_members_v1.py '+jobpath],capture_output=True,text=True,timeout=7200)
 (C/(ident+'_SENDER.stdout.log')).write_text(p.stdout);(C/(ident+'_SENDER.stderr.log')).write_text(p.stderr);assert p.returncode==0,p.stderr
 result=json.loads(p.stdout);assert result['status']=='SOURCE_EVIDENCE_SENDER_COMPLETE',result
 root=B/result['inflight'];assert B in root.parents;assert sha(root/'SENDER_MANIFEST.json')==result['sender_manifest_sha256'];sender=json.loads((root/'SENDER_MANIFEST.json').read_text());assert sender['asset']['kind']=='SOURCE_EVIDENCE_NOT_FORMAL_WORKLOAD'
 declared=set()
 for x in sender['files']:
  rel=pathlib.PurePosixPath(x['path']);assert not rel.is_absolute() and '..' not in rel.parts and x['path'] not in declared;declared.add(x['path']);p=root/x['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
 assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}==declared|{'SENDER_MANIFEST.json'}
 actual=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()];save(root/'MANIFEST.json',{'asset_id':ident,'kind':'SOURCE_EVIDENCE_NOT_FORMAL_WORKLOAD','files':actual,'logical_bytes':sum(x['bytes'] for x in actual),'source_sender_manifest_sha256':result['sender_manifest_sha256']})
 commit={'schema':'RTX4080_SOURCE_EVIDENCE_COMMIT_V1','status':'COMMITTED_VERIFIED','kind':'SOURCE_EVIDENCE_NOT_FORMAL_WORKLOAD','asset_id':ident,'manifest_sha256':sha(root/'MANIFEST.json'),'source_KEEP':True,'release_bytes':0,'no_gpu_execution':True,'utc_unix':time.time()};save(root/'COMMIT.json',commit)
 dest=B/'objects'/ident;assert not dest.exists();root.rename(dest)
 assert sha(dest/'MANIFEST.json')==commit['manifest_sha256']
 for x in actual:assert sha(dest/x['path'])==x['sha256']
 save(B/'receipts'/(ident+'_NATIVE174_FULL_READBACK.json'),dict(commit,source_members=sender['asset']['members'],unique_payload_bytes=sender['asset']['unique_payload_bytes']))
 cat=B/'catalog/SOURCE_EVIDENCE.json';o=json.loads(cat.read_text()) if cat.exists() else {'schema':'SOURCE_EVIDENCE_CATALOG_V1','objects':[]};assert all(x['asset_id']!=ident for x in o['objects']);o['objects'].append(commit);temp=cat.with_name(cat.name+'.tmp');temp.write_text(json.dumps(o,indent=2)+'\n');os.replace(temp,cat)
 save(C/(ident+'_FINAL_RECEIPT.json'),dict(commit,source_asset=sender['asset']));print(json.dumps(commit))
except Exception as e:
 save(C/(ident+'_FAILURE.json'),{'error':repr(e),'traceback':traceback.format_exc(),'source_KEEP':True});raise
finally:
 signal.alarm(0)
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
