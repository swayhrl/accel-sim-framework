"""Finite COPY_ONLY ordered trace receiver; never a scientific launcher.

Adapts the qualified native V2 length-framed input protocol to exact multi-member
manifests. Uses the original sender/receiver locks and pinned V9 publication
primitives. Data buffers are bounded; no source modification or Share staging.
"""
import pathlib,os,sys,json,hashlib,struct,time,fcntl,subprocess,shlex,importlib.util,stat
P=pathlib.Path;MIB=1024**2;GIB=1024**3;CHUNK=128*MIB;RATE=15*MIB
TASK=P('/root/data/shared_sm70_trace_library_20261024_v1')
NATIVE=P('/root/data/ep_l2_dtc_l1_native_v2')
NAS=P('/root/share/mnt164/huangrulin/traces')
BRIDGE=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
BASELINE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_full_result_offload_v1/EP_L2_E057/aadbbab26f921819e7e24f3bb2187d1955eccd79381a38d475e7eed4e0f36e7d')
V9_SHA='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe'
sys.dont_write_bytecode=True
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def safe(root,name):
 p=P(name);need(not p.is_absolute() and '..' not in p.parts and '\\' not in name,'unsafe relative member');dest=P(root)/p
 for parent in [dest.parent,*dest.parent.parents]:
  if parent==P(root).parent:break
  need(not parent.is_symlink(),'symlink member ancestor')
 return dest
def identity(p):
 s=P(p).lstat();return {'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'uid':s.st_uid,'gid':s.st_gid,'mode':s.st_mode&0o7777,'nlink':s.st_nlink,'type':'file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'special'}
def same_source(a,b):return all(a[k]==b[k] for k in ['dev','inode','size','mtime_ns','ctime_ns','uid','gid','mode','type'])
def emit(x):print(json.dumps(x),flush=True)
def v9():
 raw=(BASELINE/'v9_transaction.py').read_bytes();need(digest(raw)==V9_SHA,'qualified V9 primitive changed');s=importlib.util.spec_from_file_location('trace_copy_pinned_v9',BASELINE/'v9_transaction.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def publish_bytes(path,b,v):
 path=P(path)
 if path.exists():need(path.read_bytes()==b,'immutable object collision '+str(path));return
 temp=path.with_name(path.name+'.writing')
 if temp.exists():need(temp.read_bytes()==b,'owned metadata partial collision')
 else:
  with temp.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 v.rename_noreplace(temp,path);need(path.read_bytes()==b,'closed-reopen metadata mismatch')
def hash_file(p,rate=30*MIB,gate=None):
 h=hashlib.sha256();start=time.monotonic();count=0
 with P(p).open('rb') as f:
  while True:
   b=f.read(MIB)
   if not b:break
   h.update(b);count+=len(b)
   if rate:time.sleep(max(0,count/rate-(time.monotonic()-start)))
   if gate:gate()
 return h.hexdigest()

class Resources:
 def __init__(self,testing=False):self.last=0;self.last_value=None;self.testing=testing;self.samples=[]
 def __call__(self,force=False):
  if not force and self.last_value and time.monotonic()-self.last<10:return self.last_value
  need(os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]' and NATIVE.stat().st_dev==2128,'Target identity changed')
  fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(NAS.parent)],text=True))['filesystems'][0];need(fs['source']=='admin-wcx@10.208.130.164:/home/shared' and fs['fstype']=='fuse.sshfs','not genuine164')
  registry=read(NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');reserved=sum(x.get('reserved_write_bytes',0) for x in registry.get('registered_future_requests',{}).values());disk=os.statvfs(NATIVE);free=disk.f_bavail*disk.f_frsize;required=5*GIB+reserved+GIB+64*MIB
  need(free>=required and disk.f_favail>=100000,'RESOURCE_HOLD_SHARED_SSD_ALL_PROJECT_RESERVATIONS')
  mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;cur=int(P('/sys/fs/cgroup/memory.current').read_text());maxval=P('/sys/fs/cgroup/memory.max').read_text().strip();need(mem>=64*GIB and (maxval=='max' or int(maxval)-cur>=GIB),'RESOURCE_HOLD_HOST_OR_CGROUP_RAM')
  pressure={line.split()[0]:{a.split('=')[0]:float(a.split('=')[1]) for a in line.split()[1:]} for line in P('/proc/pressure/io').read_text().splitlines()};active=[]
  ae=P('/root/data/dtc_main_20261023_v1/ae_fair_v1/control/qualification_ledger')
  pending_intents=set(ae.glob('*.INTENT.json'))
  for registered in registry.get('registered_future_requests',{}).values():
   consumed=registered.get('consumed',{})
   if not isinstance(consumed,dict):continue
   for record in consumed.values():
    if isinstance(record,dict) and not record.get('execution_receipt') and record.get('intent'):pending_intents.add(P(record['intent']))
  for f in sorted(pending_intents):
   if f.with_name(f.name.replace('.INTENT.','.DONE.')).exists():continue
   i=read(f);out=P(i['output']);proof=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
   if not proof.exists():continue
   p=read(proof);proc=P('/proc')/str(p['pid'])
   if not proc.exists():continue
   ticks=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])
   if ticks!=p['start_ticks']:continue
   progress=out/'progress.jsonl'
   with progress.open('rb') as stream:stream.seek(max(0,progress.stat().st_size-4096));lines=stream.read().splitlines()
   decoded=[]
   for line in lines:
    try:decoded.append(json.loads(line))
    except json.JSONDecodeError:pass
   need(bool(decoded),'RESOURCE_HOLD_ACTIVE_PROGRESS_UNREADABLE');last=decoded[-1];age=(time.monotonic_ns()-last['mono_ns'])/1e9
   need(age<=30,'RESOURCE_HOLD_ACTIVE_AEFAIR_PROGRESS_FRESHNESS')
   active.append({'cohort':i['cohort'],'pid':p['pid'],'start_ticks':ticks,'completed':last['completed'],'phase':last['phase'],'progress_age_seconds':age})
  # This COPY_ONLY task uses a conservative low-pressure window while science
  # is active; it never alters the scientific controller's IO warning policy.
  if active:need(pressure.get('some',{}).get('avg10',0)<=5 and pressure.get('full',{}).get('avg10',0)<=1,'RESOURCE_HOLD_ACTIVE_SCIENCE_IO_HEADROOM')
  value={'observed_unix':time.time(),'SSD_free_bytes':free,'required_SSD_bytes':required,'registered_foreign_write_reservations_bytes':reserved,'unregistered_other_project_headroom_bytes':GIB,'task_controls_reserve_bytes':64*MIB,'host_MemAvailable_bytes':mem,'cgroup_current':cur,'host_IO_pressure':pressure,'active_AEFAIR':active,'Share_new_bytes':0,'all_policy_gates_pass':True};self.last=time.monotonic();self.last_value=value;self.samples.append(value);return value

def source_send(request,testing=False):
 manifest=request['manifest'];skip=request['skip']
 if manifest.get('source_backend')=='archive':return source_archive_send(request,testing)
 if testing:need(P(manifest['source_root']).is_relative_to(TASK/'synthetic'),'test source outside own synthetic namespace')
 else:need((os.uname().nodename=='huangrulin-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]') or (manifest.get('source_backend')=='native' and os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'),'wrong frozen source namespace')
 lock=((TASK/'synthetic/.SOURCE_TEST.lock') if testing else (BRIDGE/'.TLS_V10_SOURCE_SENDER.lock')).open('a' if testing else 'rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:os.nice(19)
 except OSError:pass
 def frame(obj):b=canon(obj);sys.stdout.buffer.write(struct.pack('!Q',len(b))+b);sys.stdout.buffer.flush()
 for row in manifest['members']:
  path=safe(manifest['source_root'],row['relative_path']);before=identity(path);need(same_source(before,row),'Source exact frozen identity changed '+str(path));need(row['type']=='file','nonregular producer member');h=hashlib.sha256();offset=0;need(skip[row['relative_path']]<=row['size'],'invalid resume range')
  fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0))
  with os.fdopen(fd,'rb',buffering=0) as f:
   while True:
    b=f.read(CHUNK)
    if not b:break
    h.update(b)
    if offset>=skip[row['relative_path']]:
     frame({'event':'CHUNK','path':row['relative_path'],'offset':offset,'size':len(b),'sha256':digest(b)})
     for i in range(0,len(b),MIB):part=memoryview(b)[i:i+MIB];time.sleep(len(part)/RATE);sys.stdout.buffer.write(part);sys.stdout.buffer.flush()
    offset+=len(b)
  need(same_source(before,identity(path)) and offset==row['size'],'Source changed during readonly stream');need(h.hexdigest()==row['sha256'],'Source full SHA differs from frozen evidence '+str(path));frame({'event':'FILE_END','path':row['relative_path'],'size':offset,'sha256':h.hexdigest(),'source_before_after_identity_unchanged':True,'source_disposition':'SOURCE_KEEP'})
 frame({'event':'SOURCE_DONE','Source_simulator_starts':0,'source_disposition':'SOURCE_KEEP'})

def spawn_sender(manifest,skip,testing=False):
 request={'manifest':manifest,'skip':skip}
 if testing or manifest.get('source_backend')=='native':
  p=subprocess.Popen(['/usr/bin/python3','-B',str(P(__file__)),('source-native' if manifest.get('source_backend')=='native' else 'source-synthetic')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);p.stdin.write(canon(request));p.stdin.close();return p
 source=P(__file__).read_text();boot='import sys,json;code=sys.stdin.buffer.readline();exec(compile(json.loads(code),"frozen_readonly_trace_export.py","exec"),{"__name__":"trace_source"})';payload=source+'\nsource_send(json.loads(sys.stdin.buffer.readline()))\n'
 ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174'];p=subprocess.Popen(ssh+['python3 -B -c '+shlex.quote(boot)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);p.stdin.write((json.dumps(payload)+'\n').encode()+canon(request));p.stdin.close();return p

def migrate(manifest,testing=False,inject_after_ranges=None):
 need(manifest['freeze_status'].startswith('FROZEN'),'source scope held');g=Resources(testing);before=g(True);bundle=P(manifest['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1));need(bundle.is_relative_to(NAS),'wrong new NAS scope');need(not manifest.get('reuse'),'reuse must not enter new payload path')
 available=os.statvfs(NAS.parent).f_bavail*os.statvfs(NAS.parent).f_frsize;need(available>=3*manifest['source_data_bytes']+64*MIB,'RESOURCE_HOLD_NAS_CAPACITY')
 lock=(BRIDGE/'.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);v=v9();bundle.mkdir(parents=True,exist_ok=True);publish_bytes(bundle/'SOURCE_MANIFEST.json',canon(manifest),v);(bundle/'chunks').mkdir(exist_ok=True);(bundle/'tree').mkdir(exist_ok=True)
 if (bundle/'COMMIT.json').exists():return verify_committed(bundle,g,rehash=False)
 skip={};ranges={};newbytes=0;resumed=0
 for row in manifest['members']:
  name=row['relative_path'];key=digest(name.encode());folder=bundle/'chunks'/key;folder.mkdir(exist_ok=True);chunks=[];offset=0
  for orphan in folder.glob('*.part'):
   if orphan.with_name(orphan.name+'.json').exists():continue
   header=orphan.with_name(orphan.name+'.frame');need(header.exists(),'unbound orphan range retained HOLD');c=read(header);need(orphan.stat().st_size==c['size'] and hash_file(orphan,gate=g)==c['sha256'],'orphan range SHA mismatch');publish_bytes(orphan.with_name(orphan.name+'.json'),canon(c),v)
  for p in sorted(folder.glob('*.json')):
   c=read(p);need(c['offset']==offset and 0<c['size']<=CHUNK,'resume coverage gap');data=folder/c['name'];need(data.stat().st_size==c['size'] and hash_file(data,gate=g)==c['sha256'],'resume chunk damaged');chunks.append(c);offset+=c['size'];resumed+=c['size']
  need(offset<=row['size'],'resume beyond source EOF');skip[name]=offset;ranges[name]=chunks
 p=spawn_sender(manifest,skip,testing);ends=[];count_ranges=0
 def exact(n):
  out=bytearray()
  while len(out)<n:
   b=p.stdout.read(n-len(out));need(b,'Source EOF before complete verification');out.extend(b)
  return bytes(out)
 try:
  while True:
   length=struct.unpack('!Q',exact(8))[0];need(length<=1024**2,'header bound');event=json.loads(exact(length));g()
   if event['event']=='SOURCE_DONE':break
   if event['event']=='FILE_END':ends.append(event);continue
   need(event['event']=='CHUNK' and event['path'] in ranges,'unknown frame');name=event['path'];need(event['offset']==sum(c['size'] for c in ranges[name]) and 0<event['size']<=CHUNK,'range offset/size changed');folder=bundle/'chunks'/digest(name.encode());leaf=str(event['offset']).zfill(20)+'.part';dest=folder/leaf;partial=folder/(leaf+'.writing');h=hashlib.sha256();left=event['size']
   if partial.exists():
    # Owned uncommitted partial may only be removed if its prefix matches this
    # exact incoming immutable range. No scientific/source path is involved.
    previous=partial.read_bytes();need(len(previous)<=left,'partial larger than range')
   else:previous=b''
   c={'name':leaf,'offset':event['offset'],'size':event['size'],'sha256':event['sha256']};publish_bytes(folder/(leaf+'.frame'),canon(c),v)
   with partial.open('ab' if previous else 'xb') as f:
    pos=0
    while left:
     b=exact(min(MIB,left));h.update(b)
     overlap=min(len(b),max(0,len(previous)-pos))
     if overlap:need(b[:overlap]==previous[pos:pos+overlap],'owned partial prefix collision')
     if overlap<len(b):f.write(b[overlap:])
     pos+=len(b);left-=len(b);g()
    f.flush();os.fsync(f.fileno())
   need(h.hexdigest()==event['sha256'] and hash_file(partial,gate=g)==event['sha256'],'closed chunk full SHA mismatch');v.rename_noreplace(partial,dest);need(hash_file(dest,gate=g)==event['sha256'],'published range reopen SHA');publish_bytes(folder/(leaf+'.json'),canon(c),v);ranges[name].append(c);newbytes+=event['size'];count_ranges+=1;emit({'event':'RANGE_VERIFIED','asset':manifest['primary_asset_id'],'file':name,'verified_end':event['offset']+event['size'],'new_payload_bytes':newbytes})
   if inject_after_ranges is not None and count_ranges>=inject_after_ranges:raise RuntimeError('INJECTED_BOUNDED_OWN_RANGE_CRASH')
  rc=p.wait(timeout=30);need(rc==0,'Source readonly export failed: '+p.stderr.read().decode(errors='replace')[-1000:])
 finally:
  if p.poll() is None:p.terminate();p.wait(timeout=10)
  p.stdout.close();p.stderr.close()
 need([x['path'] for x in ends]==[x['relative_path'] for x in manifest['members']],'incomplete/unordered source EOF proof')
 for row,end in zip(manifest['members'],ends):
  need((end['sha256'],end['size'])==(row['sha256'],row['size']),'source member proof mismatch');dest=safe(bundle/'tree',row['relative_path']);dest.parent.mkdir(exist_ok=True,parents=True);partial=dest.with_name(dest.name+'.writing')
  if dest.exists():need(dest.stat().st_size==row['size'] and hash_file(dest,gate=g)==row['sha256'],'existing tree file collision');continue
  if partial.exists():need(partial.stat().st_size==row['size'] and hash_file(partial,gate=g)==row['sha256'],'owned tree partial needs range recovery; retained')
  else:
   offset=0;h=hashlib.sha256();start=time.monotonic();done=0
   with partial.open('xb') as f:
    for c in ranges[row['relative_path']]:
     need(c['offset']==offset,'assembly gap');chunk=bundle/'chunks'/digest(row['relative_path'].encode())/c['name']
     with chunk.open('rb') as src:
      while True:
       b=src.read(MIB)
       if not b:break
       f.write(b);h.update(b);done+=len(b);time.sleep(max(0,done/RATE-(time.monotonic()-start)));g()
     offset+=c['size']
    f.flush();os.fsync(f.fileno())
   need(offset==row['size'] and h.hexdigest()==row['sha256'],'materialized whole content mismatch')
  need(hash_file(partial,gate=g)==row['sha256'],'closed-reopened materialized whole SHA');v.rename_noreplace(partial,dest);dest.chmod(0o444)
 treeproof=verify_tree(bundle/'tree',manifest,g,rehash=False);publish_bytes(bundle/'SOURCE_CURRENT_EOF_SHA_PROOFS.json',canon(ends),v);publish_bytes(bundle/'RANGE_INDEX.json',canon(ranges),v);publish_bytes(bundle/'TREE_VERIFICATION.json',canon(treeproof),v)
 result={'status':'TRUE164_DIRECT_READ_READY','asset_id':manifest['primary_asset_id'],'object_id':manifest['object_id'],'bundle':str(bundle),'true164_bundle':manifest['new_true164_bundle'],'true164_tree':manifest['new_true164_bundle']+'/tree','mount_tree':str(bundle/'tree'),'manifest_sha256':digest(canon(manifest)),'original_bytes':manifest['source_data_bytes'],'members':len(manifest['members']),'kernels':len(manifest['ordered_kernel_members']),'new_payload_bytes':newbytes,'reused_verified_range_bytes':resumed,'Source_full_SHA_matches':True,'true164_closed_reopen_whole_SHA_matches':True,'RESTORE_VERIFIED_NATIVE_TARGET':'NOT_PERFORMED_BY_TRANSFER; independent bounded check is separate','before':before,'after':g(True),'resource_samples':g.samples,'source_disposition':'SOURCE_KEEP','Source_simulator_starts':0,'Share_new_bytes':0}
 publish_bytes(bundle/'RECEIPT.json',canon({k:x for k,x in result.items() if k not in ['before','after','resource_samples','new_payload_bytes','reused_verified_range_bytes']}),v)
 publish_bytes(bundle/'trace_copy.py',P(__file__).read_bytes(),v);publish_bytes(bundle/'RESTORE.sh',b'#!/bin/sh\nset -eu\n: "${1:?Pass a NEW ABSENT task-native recovery directory}"\nHERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\nexec /usr/bin/python3 -B "$HERE/trace_copy.py" restore "$HERE" "$1"\n',v)
 commit={'schema':'IMMUTABLE_MULTI_MEMBER_TRACE_INPUT_COMMIT_V1','object_id':manifest['object_id'],'manifest_sha256':digest(canon(manifest)),'range_index_sha256':digest(canon(ranges)),'tree_verification_sha256':digest(canon(treeproof)),'Source_disposition':'SOURCE_KEEP','scientific_acceptance_granted':False};publish_bytes(bundle/'COMMIT.json',canon(commit),v)
 return result

def verify_tree(tree,manifest,gate,rehash=False):
 tree=P(tree);need(tree.is_dir() and not tree.is_symlink(),'missing physical true164 tree');rows=[]
 expected=set(x['relative_path'] for x in manifest['members']);actual={x.relative_to(tree).as_posix() for x in tree.rglob('*') if x.is_file()};need(actual==expected,'complete tree membership mismatch')
 for row in manifest['members']:
  p=safe(tree,row['relative_path']);need(p.is_file() and not p.is_symlink() and p.stat().st_size==row['size'],'tree file type/size');gate()
  if rehash:need(hash_file(p,gate=gate)==row['sha256'],'current whole tree SHA mismatch')
  with p.open('rb') as f:
   first=f.read(min(1024,p.stat().st_size));f.seek(max(0,p.stat().st_size-64));tail=f.read(64)
  with p.open('rb') as f:need(f.read(len(first))==first,'reopen mismatch')
  if manifest.get('payload_kind')=='CAS_FILES_V1':
   if row.get('header_prefix_hex'):need(first[:128].hex()==row['header_prefix_hex'],'CAS prefix differs from frozen source')
  elif row['relative_path']==manifest['entry_name']:need(p.read_bytes().hex()==manifest['commandlist_bytes_hex'],'commandlist bytes/order drift')
  else:need(first[:128].hex()==row['header_prefix_hex'],'kernel header differs from source')
  rows.append({'relative_path':row['relative_path'],'size':row['size'],'sha256':row['sha256'],'actual_tree_identity':identity(p),'open_seek_reopen':True,'header_matches_source':True,'last_read_bytes':len(tail),'full_hash_recomputed_in_this_call':rehash})
 return rows

def verify_committed(bundle,gate=None,rehash=False):
 gate=gate or Resources();m=read(P(bundle)/'SOURCE_MANIFEST.json');c=read(P(bundle)/'COMMIT.json');need(c['manifest_sha256']==digest(canon(m)) and c['object_id']==m['object_id'],'committed selector changed');proof=verify_tree(P(bundle)/'tree',m,gate,rehash=rehash);r=read(P(bundle)/'RECEIPT.json');need(r['object_id']==m['object_id'],'committed receipt mismatch');return dict(r,new_payload_bytes=0,reused_verified_range_bytes=m['source_data_bytes'],completed_transaction_reused=True,current_tree_validation=proof)

def restore_native(tree,manifest,destination,gate=None):
 gate=gate or Resources();gate(True);dest=P(destination);need(dest.is_absolute() and dest.is_relative_to(TASK/'recovery') and '..' not in dest.parts,'restore outside dedicated native namespace');need(not os.path.lexists(dest),'ABSENT restore destination required');need(manifest['source_data_bytes']<=240*MIB,'NOT_PERFORMED_NATIVE_RESTORE_EXCEEDS_BOUNDED240MIB_WINDOW')
 allocated=sum(p.lstat().st_blocks*512 for p in TASK.rglob('*') if not p.is_symlink());need(allocated+manifest['source_data_bytes']<=256*MIB,'RESOURCE_HOLD_NATIVE_TASK256MIB_SCRATCH_CAP');dest.parent.mkdir(parents=True,exist_ok=True);dest.mkdir(mode=0o700);rows=[]
 for row in manifest['members']:
  src=safe(tree,row['relative_path']);p=safe(dest,row['relative_path']);p.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();start=time.monotonic();count=0
  with src.open('rb') as f,p.open('xb') as out:
   while True:
    b=f.read(MIB)
    if not b:break
    out.write(b);h.update(b);count+=len(b);time.sleep(max(0,count/(30*MIB)-(time.monotonic()-start)));gate()
   out.flush();os.fsync(out.fileno())
  need(count==row['size'] and h.hexdigest()==row['sha256'],'restored original bytes mismatch');os.chown(p,row['uid'],row['gid']);p.chmod(row['mode']);os.utime(p,ns=(row['mtime_ns'],row['mtime_ns']));a=identity(p);need(all(a[k]==row[k] for k in ['size','uid','gid','mode','mtime_ns']) and hash_file(p,rate=0)==row['sha256'],'closed restored SHA/numeric metadata mismatch');rows.append({'relative_path':row['relative_path'],'sha256':row['sha256'],'identity':a})
 d=manifest['source_root_identity'];os.chown(dest,d['uid'],d['gid']);dest.chmod(d['mode']);os.utime(dest,ns=(d['mtime_ns'],d['mtime_ns']));need(all(identity(dest)[k]==d[k] for k in ['uid','gid','mode','mtime_ns']),'root directory restored metadata mismatch')
 return {'status':'RESTORE_VERIFIED_NATIVE_TARGET','destination':str(dest),'scope':'Dedicated174-new native ext4, not native164','regular_files':len(rows),'rows':rows,'root_directory_original_numeric_metadata':manifest.get('payload_kind')!='CAS_FILES_V1','root_directory_manifest_numeric_metadata':True,'original_bytes':manifest['source_data_bytes'],'Source_mutations':0}


def source_archive_send(request,testing=False):
 import tarfile,gzip,threading
 m=request['manifest'];archive=P(m['archive_path']);skip=request['skip']
 if testing:need(archive.is_relative_to(TASK/'synthetic'),'archive test outside owned source')
 else:need(os.uname().nodename=='huangrulin-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]','archive source identity')
 need(same_source(identity(archive),m['archive_identity']),'archive identity changed before stream')
 lock=((TASK/'synthetic/.SOURCE_TEST.lock') if testing else (BRIDGE/'.TLS_V10_SOURCE_SENDER.lock')).open('a' if testing else 'rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:os.nice(19)
 except OSError:pass
 def frame(o):b=canon(o);sys.stdout.buffer.write(struct.pack('!Q',len(b))+b);sys.stdout.buffer.flush()
 wanted={r['archive_member']:r for r in m['members']};found=[];decoder=None;feeder=None;errors=[];started=time.monotonic();physical=[0]
 fd=os.open(archive,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0));raw=os.fdopen(fd,'rb')
 class RateReader:
  def read(self,n=-1):
   b=raw.read(n);physical[0]+=len(b);time.sleep(max(0,physical[0]/(30*MIB)-(time.monotonic()-started)));return b
 reader=RateReader()
 if str(archive).endswith('.zst'):
  decoder=subprocess.Popen([('/usr/bin/zstd' if P('/usr/bin/zstd').is_file() else str(TASK/'tools/zstd')),'-dc'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  def feed():
   try:
    while True:
     b=reader.read(MIB)
     if not b:break
     decoder.stdin.write(b)
    decoder.stdin.close()
   except Exception as x:errors.append(str(x))
  feeder=threading.Thread(target=feed);feeder.start();tf=tarfile.open(fileobj=decoder.stdout,mode='r|')
 else:tf=tarfile.open(fileobj=reader,mode='r|gz')
 try:
  for ti in tf:
   name=ti.name
   if name not in wanted or name in found:continue
   row=wanted[name];need(ti.isfile() and ti.size==row['size'],'archive member type/size drift');f=tf.extractfile(ti);h=hashlib.sha256();offset=0
   while True:
    b=f.read(CHUNK)
    if not b:break
    h.update(b)
    if offset>=skip[row['relative_path']]:
     frame({'event':'CHUNK','path':row['relative_path'],'offset':offset,'size':len(b),'sha256':digest(b)})
     for i in range(0,len(b),MIB):part=memoryview(b)[i:i+MIB];time.sleep(len(part)/RATE);sys.stdout.buffer.write(part);sys.stdout.buffer.flush()
    offset+=len(b)
   need(offset==row['size'] and h.hexdigest()==row['sha256'],'archive member full SHA drift');found.append(name)
   frame({'event':'FILE_END','path':row['relative_path'],'size':offset,'sha256':h.hexdigest(),'source_before_after_identity_unchanged':True,'source_disposition':'SOURCE_KEEP'})
  need(found==[r['archive_member'] for r in m['members']],'archive member order or EOF mismatch')
  need(same_source(identity(archive),m['archive_identity']),'archive changed during stream')
 finally:
  tf.close()
  if decoder:
   while decoder.stdout.read(MIB):pass
   feeder.join();need(not errors,'zstd input stream error');need(decoder.wait()==0,'zstd decoder failed')
  raw.close()
 need(same_source(identity(archive),m['archive_identity']),'archive changed before final source close')
 frame({'event':'SOURCE_DONE','Source_simulator_starts':0,'source_disposition':'SOURCE_KEEP'})

if __name__=='__main__':
 try:
  if sys.argv[1:] in [['source-synthetic']]:source_send(json.loads(sys.stdin.buffer.readline()),testing=True)
  elif sys.argv[1:] in [['source-native']]:source_send(json.loads(sys.stdin.buffer.readline()),testing=False)
  elif sys.argv[1]=='migrate':emit(migrate(read(sys.argv[2])))
  elif sys.argv[1]=='verify':emit(verify_committed(P(sys.argv[2]),rehash='--full' in sys.argv[3:]))
  elif sys.argv[1]=='restore':
   bundle=P(sys.argv[2]);m=read(bundle/'SOURCE_MANIFEST.json');verify_committed(bundle);emit(restore_native(bundle/'tree',m,P(sys.argv[3])))
  else:raise RuntimeError('finite trace-copy operation required')
 except (RuntimeError,OSError,ValueError,KeyError) as error:print(json.dumps({'status':'HOLD_EXACT_ASSET_NO_SCIENTIFIC_ACTION','reason':str(error)}),file=sys.stderr);sys.exit(2)
