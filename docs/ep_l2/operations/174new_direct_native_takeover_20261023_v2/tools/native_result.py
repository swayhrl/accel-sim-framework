"""Finite native qualification evidence outbox over pinned V9 bundle primitives.

Does not assert scientific acceptance. Closed failed attempts may be archived as
STOP_UNACCEPTED evidence; this never grants a new science start or source release.
Only exact native intent roots and a new true164 increment are allowed.
"""
import pathlib,os,json,hashlib,io,tarfile,time,fcntl,stat,importlib.util,sys,uuid
P=pathlib.Path;ROOT=P('/root/data/ep_l2_dtc_l1_native_v2');MIB=1024**2;GIB=1024**3;CHUNK=128*MIB;RATE=30*MIB
NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_native_v2_results')
BASELINE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_full_result_offload_v1/EP_L2_E057/aadbbab26f921819e7e24f3bb2187d1955eccd79381a38d475e7eed4e0f36e7d')
COHORTS={'EP_NATIVE_MIGRATION_Q1':'EP','EP_NATIVE_MIGRATION_Q2':'EP','DTC_NATIVE_MIGRATION_Q1':'DTC','DTC_LEGACY_FAST64_NN_NATIVE_SHORT_Q1':'DTC_LEGACY'}
sys.dont_write_bytecode=True

def require(v,s):
 if not v:raise RuntimeError(s)
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def libraries(bundle=None):
 base=BASELINE if bundle is None else P(bundle)
 raw=(base/'full_result_bundle.py').read_bytes();pin=read((ROOT/'control/RESULT_ENGINE_PIN.json') if bundle is None else base/'RESULT_ENGINE_PIN.json');require(sha(raw)==pin['full_result_bundle_sha256'],'pinned result engine changed')
 s=importlib.util.spec_from_file_location('pinned_native_bundle_primitives',base/'full_result_bundle.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 v=m.import_v9((base/'v9_transaction.py').read_bytes());return m,v

def manifest_for(cohort):
 require(cohort in COHORTS,'unknown native cohort');project=COHORTS[cohort];intent=read(ROOT/'control/qualification_ledger'/(cohort+'.INTENT.json'));done=read(ROOT/'control/qualification_ledger'/(cohort+'.DONE.json'));src=P(intent['output'])
 require(src==ROOT/project/'run/results'/intent['uuid'] and read(src/'NATIVE_EXIT.json')==done,'closed exact native intent/DONE mismatch')
 require(intent['uuid']==done['uuid'] and done['new_attempt_consumed']==1,'native transaction identity')
 pid=read(src/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=P('/proc')/str(pid['pid'])
 if proc.exists():require(int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=pid['start_ticks'],'native simulator still active')
 f,v=libraries();entries=[]
 for p in [src,*sorted(src.rglob('*'))]:
  s=p.lstat();r=f.ident(s);r.update(path=p.relative_to(src).as_posix(),type='directory' if stat.S_ISDIR(s.st_mode) else 'file' if stat.S_ISREG(s.st_mode) else 'symlink' if cohort in ['DTC_NATIVE_MIGRATION_Q1','DTC_LEGACY_FAST64_NN_NATIVE_SHORT_Q1'] and stat.S_ISLNK(s.st_mode) else 'unsupported');require(r['type']!='unsupported','new evidence links/special files require explicit review')
  if r['type']=='file':r['sha256']=f.file_sha(p)
  if r['type']=='symlink':
   r['target']=os.readlink(p);require(r['path']=='perf_counter.csv.gz' and '/' not in r['target'] and r['target'].startswith('perf_counter_') and r['target'].endswith('.csv.gz') and not (src/r['target']).is_symlink() and (src/r['target']).is_file(),'only exact native internal perf alias permitted')
  entries.append(r)
 selector=sha(canon(entries));tx=sha(canon({'cohort':cohort,'uuid':intent['uuid'],'selector_sha256':selector,'source_root':str(src),'destination':str(NAS/cohort)}))
 qual=ROOT/project/'control'/('SCIENCE_QUALIFICATION_'+cohort+'.json');science='STOP_UNACCEPTED' if done['stop_reason'] or done['launcher_wait_returncode'] else read(qual)['status'] if qual.exists() and read(qual)['uuid']==done['uuid'] else 'PENDING_INDEPENDENT_SCIENTIFIC_QUALIFICATION'
 return {'schema':'NATIVE_QUALIFICATION_EVIDENCE_COPY_ONLY_MANIFEST_V1','cohort':cohort,'project':project,'txid':tx,'source_root':str(src),'selector_sha256':selector,'entries':entries,'reused_objects':{},'source_disposition':'SOURCE_KEEP','scientific_status':science,'native_execution_receipt_sha256':f.file_sha(src/'NATIVE_EXIT.json'),'source_filesystem_identity':{'host':os.uname().nodename,'mount_namespace':os.readlink('/proc/self/ns/mnt'),'device':src.stat().st_dev},'persistent164_root':str(NAS/cohort/tx).replace('/root/share/mnt164','/home/shared',1)}

def gate(reservation=0,other_reservation=None):
 require(os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]','target identity')
 import subprocess
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(NAS.parent)],text=True))['filesystems'][0]
 require(fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared','genuine164 changed')
 available=os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize
 # Preserve 1GiB for the unused DTC result+restore budget; failed EP has no
 # remaining output-writing authority. A new EP attempt requires new admission.
 if other_reservation is None:
  source=read(ROOT/'control/SOURCE_PREFLIGHT.json');other=source['other_outstanding_write_reservations_bytes']
 else:require(type(other_reservation) is int and other_reservation>=0,'invalid explicitly supplied current all-project reservation');other=other_reservation
 require(available-reservation-GIB-128*MIB-other>=7*GIB,'native restore/all-project reserve HOLD')
 mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;require(mem>=64*GIB,'RAM HOLD')
 return {'SSD_available_bytes':available,'restore_reserved_bytes':reservation,'other_outstanding_write_reservations_bytes':other,'unused_DTC_result_restore_reserve_bytes':GIB,'monitor_and_floor_bytes':7*GIB,'Share_new_bytes':0,'MemAvailable_bytes':mem}

class RangeWriter(io.RawIOBase):
 def __init__(self,bundle,m,v,f):self.bundle=bundle;self.m=m;self.v=v;self.f=f;self.buf=bytearray();self.offset=0;self.rows=[];self.hash=hashlib.sha256();self.newbytes=0
 def writable(self):return True
 def write(self,b):
  self.buf.extend(b)
  while len(self.buf)>=CHUNK:self.flush_range(bytes(self.buf[:CHUNK]));del self.buf[:CHUNK]
  return len(b)
 def flush_range(self,b):
  gate();name=str(self.offset).zfill(20)+'.part';p=self.bundle/'chunks'/name;h=sha(b);self.hash.update(b)
  if p.exists():require(p.stat().st_size==len(b) and self.f.file_sha(p)==h,'existing chunk mismatch')
  else:
   tmp=p.with_name(p.name+'.writing');start=0
   if tmp.exists():
    start=tmp.stat().st_size;require(start<=len(b) and tmp.read_bytes()==b[:start],'interrupted owned partial mismatch')
   with tmp.open('ab' if start else 'xb') as stream:
    for i in range(start,len(b),MIB):
     part=b[i:i+MIB];time.sleep(len(part)/RATE);stream.write(part);self.newbytes+=len(part)
    stream.flush();os.fsync(stream.fileno())
   require(self.f.file_sha(tmp)==h,'closed range SHA');self.v.rename_noreplace(tmp,p);require(self.f.file_sha(p)==h,'reopened published range SHA')
  self.rows.append({'txid':self.m['txid'],'name':name,'offset':self.offset,'size':len(b),'sha256':h});self.offset+=len(b)
 def finish(self):
  if self.buf:self.flush_range(bytes(self.buf));self.buf.clear()
  return {'archive_bytes':self.offset,'archive_sha256':self.hash.hexdigest(),'chunks':self.rows}

def archive(cohort):
 if cohort=='DTC_LEGACY_FAST64_NN_NATIVE_SHORT_Q1':
  # Exact user-approved completed auxiliary replay only. The main simulation
  # retains its primary lease; the data receiver remains globally exclusive.
  auth=read(ROOT/'control/SHORT_NN_PARALLEL_AUTHORIZATION.json');require(auth['explicit_user_approval'] and auth['one_bounded_parallel_exception'] and auth['approval_request_sha256']=='aa778d7b00f9cd194e10729aadfdcf4cb3590845a0c258efbbce620cbf62cdd3','short closed evidence exception not authorized');science_lock=(ROOT/'control/qualification_ledger/NATIVE_SHORT_NN_AUXILIARY.lock').open('rb')
 else:science_lock=(ROOT/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb')
 fcntl.flock(science_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 m=manifest_for(cohort);f,v=libraries();raw=sum(r['size'] for r in m['entries'] if r['type']=='file');before=gate(raw+16*MIB);lock=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);bundle=NAS/cohort/m['txid'];bundle.mkdir(parents=True,exist_ok=True);(bundle/'chunks').mkdir(exist_ok=True);v.exclusive_json(bundle/'SOURCE_MANIFEST.json',m)
 for name,b in [('full_result_bundle.py',(BASELINE/'full_result_bundle.py').read_bytes()),('v9_transaction.py',(BASELINE/'v9_transaction.py').read_bytes()),('native_result.py',P(__file__).read_bytes()),('RESULT_ENGINE_PIN.json',(ROOT/'control/RESULT_ENGINE_PIN.json').read_bytes())]:
  p=bundle/name
  if p.exists():
   if name=='native_result.py' and (bundle/'COMMIT.json').exists():continue
   require(p.read_bytes()==b,'immutable recovery tool collision')
  else:
   with p.open('xb') as stream:stream.write(b);stream.flush();os.fsync(stream.fileno())
 reused=False
 if not (bundle/'COMMIT.json').exists():
  w=RangeWriter(bundle,m,v,f)
  with tarfile.open(fileobj=w,mode='w|',format=tarfile.PAX_FORMAT) as tar:
   for r in m['entries']:
    p=f.safe(m['source_root'],r['path']);t=tarfile.TarInfo(r['path']);t.uid=r['uid'];t.gid=r['gid'];t.uname=t.gname='';t.mode=r['mode'];t.mtime=r['mtime_ns']//10**9;t.pax_headers={'mtime':str(r['mtime_ns']//10**9)+'.'+str(r['mtime_ns']%10**9).zfill(9)}
    if r['type']=='directory':t.type=tarfile.DIRTYPE;tar.addfile(t)
    elif r['type']=='symlink':t.type=tarfile.SYMTYPE;t.linkname=r['target'];tar.addfile(t)
    else:
     t.size=r['size']
     with p.open('rb') as stream:tar.addfile(t,stream)
  index=w.finish();require(manifest_for(cohort)==m,'native source drift during export');v.exclusive_json(bundle/'ARCHIVE_INDEX.json',index);v.exclusive_json(bundle/'COMMIT.json',{'txid':m['txid'],'manifest_sha256':sha(canon(m)),'archive_index_sha256':sha(canon(index)),'policy':'EXCLUSIVE_CREATE_COMMIT_MARKER_LAST'});newbytes=w.newbytes
 else:index=f.verify_archive(bundle,m);newbytes=0;reused=True
 f.verify_archive(bundle,m)
 dst=ROOT/m['project']/'run/recovery'/m['txid'];dst.parent.mkdir(exist_ok=True)
 if dst.exists():proof=f.check_native(dst,m)
 else:proof=f.restore(bundle,m,dst,v,gate=lambda:gate())
 v.exclusive_json(bundle/'RESTORE_VERIFIED_NATIVE_TARGET.json',{'scope':'174-new native ext4, not native164','txid':m['txid'],'rows':proof})
 pathmap=[{'source':str(P(m['source_root'])/r['path']),'archive_root':m['persistent164_root'],'archive_member':r['path'],'native_restore':str(dst/r['path']),'sha256':r.get('sha256')} for r in m['entries']];v.exclusive_json(bundle/'PATH_MAP.json',pathmap)
 receipt={'status':'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','scientific_status':m['scientific_status'],'cohort':cohort,'txid':m['txid'],'regular_files':sum(r['type']=='file' for r in m['entries']),'directories':sum(r['type']=='directory' for r in m['entries']),'original_bytes':raw,'archive_bytes':index['archive_bytes'],'archive_sha256':index['archive_sha256'],'true164_root':m['persistent164_root'],'target_mount_path':str(bundle),'native_restore':str(dst),'source_disposition':'SOURCE_KEEP','source_release_bytes':0,'scientific_acceptance_granted_by_archive':False,'manifest_sha256':sha(canon(m))}
 if cohort in ['DTC_NATIVE_MIGRATION_Q1','DTC_LEGACY_FAST64_NN_NATIVE_SHORT_Q1']:receipt['symlinks']=sum(r['type']=='symlink' for r in m['entries'])
 v.exclusive_json(bundle/'RECEIPT.json',receipt);local=ROOT/'control'/(cohort+'_ARCHIVE_RECEIPT.json');v.exclusive_json(local,receipt)
 return {'receipt':receipt,'this_call_new_payload_bytes':newbytes,'verified_reused_transaction':reused,'resources_before':before,'resources_after':gate(),'no_source_mutation':manifest_for(cohort)==m}

def restore(bundle,destination,other_reservation=None):
 bundle=P(bundle);destination=P(destination);require(bundle.resolve().is_relative_to(NAS),'outside new native result namespace');m=read(bundle/'SOURCE_MANIFEST.json');require(m['schema']=='NATIVE_QUALIFICATION_EVIDENCE_COPY_ONLY_MANIFEST_V1' and m['cohort'] in COHORTS,'unsupported native evidence type');require(destination.resolve().is_relative_to(ROOT/m['project']/'run/recovery'),'outside task native restore root');f,v=libraries(bundle);f.verify_archive(bundle,m);gate(sum(r['size'] for r in m['entries'] if r['type']=='file')+16*MIB,other_reservation);return f.restore(bundle,m,destination,v,gate=lambda:gate(other_reservation=other_reservation))

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['archive','restore']);p.add_argument('item');p.add_argument('--destination');p.add_argument('--other-write-reservation-bytes',type=int);a=p.parse_args()
 try:print(json.dumps(archive(a.item) if a.operation=='archive' else restore(a.item,a.destination,a.other_write_reservation_bytes),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError) as e:print(json.dumps({'status':'HOLD','reason':str(e)}),file=sys.stderr);sys.exit(2)
