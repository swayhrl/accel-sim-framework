import pathlib,json,subprocess,sys
D=pathlib.Path(__file__).parent;W=pathlib.Path('D:/repo/direct-native-takeover-v2-20261023-v1');R=W/'docs/ep_l2/operations/174new_direct_native_takeover_20261023_v2';info=json.loads((D/'EXACT_INPUT_AND_RUNTIME_DISCOVERY.json').read_bytes());scope=json.loads((D/'TRACE_AND_ELF_SCOPE.json').read_bytes());ep=info['EP_vector_candidates']['E013_33cffb17'];dtc=info['DTC']['INPUT_RUNTIME_IDENTITY.json']
source=r'''
import pathlib,json,os,struct,hashlib,time,fcntl,sys
P=pathlib.Path;request=json.loads(sys.stdin.buffer.readline());m=request['manifest'];skip=request['skip'];lock=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def write(v):b=json.dumps(v).encode();sys.stdout.buffer.write(struct.pack('!Q',len(b))+b);sys.stdout.buffer.flush()
for row in m['files']:
 p=P(row['source']);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0));h=hashlib.sha256();offset=0
 with os.fdopen(fd,'rb',buffering=0) as f:
  s=os.fstat(f.fileno());assert s.st_dev==row['dev'] and s.st_ino==row['inode'] and s.st_size==row['size'] and s.st_mtime_ns==row['mtime_ns'] and s.st_ctime_ns==row['ctime_ns'];write({'event':'FILE_BEGIN','path':row['relative_path'],'size':row['size']})
  while True:
   b=f.read(128*1024**2)
   if not b:break
   h.update(b)
   if offset>=skip[row['relative_path']]:
    write({'event':'CHUNK','path':row['relative_path'],'offset':offset,'size':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    for start in range(0,len(b),1024**2):part=memoryview(b)[start:start+1024**2];time.sleep(len(part)/(30*1024**2));sys.stdout.buffer.write(part);sys.stdout.buffer.flush()
   offset+=len(b)
  after=os.fstat(f.fileno());assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
 if row['expected_sha256'] is not None:assert h.hexdigest()==row['expected_sha256'],'old accepted member SHA mismatch'
 write({'event':'FILE_END','path':row['relative_path'],'sha256':h.hexdigest(),'size':offset,'Source_keep':True})
write({'event':'SOURCE_DONE','Source_simulator_starts':0,'Source_action':'SOURCE_KEEP'})
'''
slug=sys.argv[1];project='EP' if slug=='EP_VECTORADD_S' else 'DTC';root=scope[project]['trace_root'];members=['kernelslist.g','kernel-1.traceg'];rows=[]
for name in members:
 row=next(dict(x) for x in scope[project]['trace_shallow_members'] if x['path']==root+'/'+name);row['source']=row.pop('path');row['relative_path']=name;row['expected_sha256']=(ep['readonly_manifest.json']['commandlist_sha256'] if name=='kernelslist.g' else ep['readonly_manifest.json']['kernels'][0]['sha256']) if False else None
 if project=='EP':row['expected_sha256']=scope['EP']['readonly_manifest']['commandlist_sha256'] if name=='kernelslist.g' else scope['EP']['readonly_manifest']['kernels'][0]['sha256']
 elif name=='kernelslist.g':row['expected_sha256']=dtc['trace_list_sha256']
 rows.append(row)
manifest={'schema':'INDEPENDENT_COLD_TRACE_MEMBER_INPUT_PROTOCOL_V1','asset_id':slug,'source_root':root,'owner_accepted_baseline':'E013_33cffb17_MAIN61_S' if project=='EP' else 'AD_GEMM_940981e5-61c4-4772-83a3-50593fd1ba3a','kind':'READONLY_SCIENTIFIC_TRACE_INPUT_NOT_RESULT_OUTBOX','ordered_files':members,'files':rows,'Source_action':'SOURCE_KEEP','old_composite_identity':ep['accepted']['identity']['trace_content_sha256'] if project=='EP' else dtc['trace_list_sha256'],'old_identity_definition':'EP ordered full content identity from original accepted spec' if project=='EP' else 'DTC old runtime trace_list SHA only; new full member-set SHA is recorded separately, never conflated','target_root':'/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_native_v2_inputs/'+slug}
code='MANIFEST='+repr(manifest)+'\nSOURCE='+repr(source)+'\n'+r'''
import pathlib,json,hashlib,os,struct,subprocess,shlex,fcntl,datetime
P=pathlib.Path;m=MANIFEST;root=P(m['target_root']);native=P('/root/data/ep_l2_dtc_l1_native_v2');assert os.uname().nodename=='huangrulin-sshfs-174';assert subprocess.check_output(['findmnt','-n','-T',str(root.parent.parent),'-o','TARGET,SOURCE,FSTYPE'],text=True).split()==['/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs']
def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
v=os.statvfs(root.parent.parent);assert v.f_bavail*v.f_frsize>=3*sum(r['size'] for r in m['files'])+64*1024**2
lock=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
root.mkdir(parents=True,exist_ok=True);record=root/'INPUT_SCOPE.json'
if record.exists():assert record.read_bytes()==canon(m),'input reservation changed'
else:record.write_bytes(canon(m))
chunkdir=root/'.partial/chunks';chunkdir.mkdir(parents=True,exist_ok=True);tree=root/'tree';tree.mkdir(exist_ok=True);skip={};allrecords={}
for r in m['files']:
 key=hashlib.sha256(r['relative_path'].encode()).hexdigest();records=[];offset=0
 for p in sorted(chunkdir.glob(key+'.*.json')):
  c=json.loads(p.read_bytes());assert c['offset']==offset and sha(chunkdir/c['name'])==c['sha256'];records.append(c);offset+=c['size']
 skip[r['relative_path']]=offset;allrecords[r['relative_path']]=records
if (root/'TRACE_COMMIT.json').exists():
 done=json.loads((root/'TRACE_COMMIT.json').read_bytes())
 for r in done['members']:assert sha(tree/r['relative_path'])==r['sha256']
 print(json.dumps({'event':'REUSED_EXISTING_VERIFIED_TRACE','receipt':done,'new_payload_bytes':0}),flush=True);sys.exit(0)
ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174'];boot='import sys,json;code=sys.stdin.buffer.readline();exec(compile(json.loads(code),"readonly_trace_export.py","exec"),globals())';p=subprocess.Popen(ssh+['python3 -B -c '+shlex.quote(boot)],stdin=subprocess.PIPE,stdout=subprocess.PIPE);p.stdin.write((json.dumps(SOURCE)+'\n'+json.dumps({'manifest':m,'skip':skip})+'\n').encode());p.stdin.close()
def exact(n):
 b=bytearray()
 while len(b)<n:
  x=p.stdout.read(n-len(b));assert x,'Source EOF';b.extend(x)
 return bytes(b)
def put(path,b):
 if path.exists():assert path.read_bytes()==b
 else:
  with path.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
newbytes=0;members=[]
while True:
 n=struct.unpack('!Q',exact(8))[0];event=json.loads(exact(n))
 if event['event']=='SOURCE_DONE':break
 if event['event']=='CHUNK':
  b=exact(event['size']);assert hashlib.sha256(b).hexdigest()==event['sha256'];key=hashlib.sha256(event['path'].encode()).hexdigest();name=key+'.'+str(event['offset']).zfill(20)+'.part';put(chunkdir/name,b);assert sha(chunkdir/name)==event['sha256'];c={'name':name,'offset':event['offset'],'size':event['size'],'sha256':event['sha256']};put(chunkdir/(name+'.json'),canon(c));allrecords[event['path']].append(c);newbytes+=event['size'];del b
  print(json.dumps({'event':'TRACE_RANGE_VERIFIED','asset':m['asset_id'],'file':event['path'],'verified_offset':event['offset']+event['size'],'new_payload_bytes':newbytes}),flush=True)
 elif event['event']=='FILE_END':members.append(event)
assert p.wait(timeout=30)==0
for member in members:
 dest=tree/member['path'];temp=tree/(member['path']+'.partial')
 if not dest.exists():
  if temp.exists():assert temp.stat().st_size==member['size'] and sha(temp)==member['sha256'],'incomplete assembly retained HOLD'
  else:
   with temp.open('xb') as out:
    offset=0
    for c in allrecords[member['path']]:
     assert c['offset']==offset
     with (chunkdir/c['name']).open('rb') as src:
      for b in iter(lambda:src.read(1024**2),b''):out.write(b)
     offset+=c['size']
    assert offset==member['size'];out.flush();os.fsync(out.fileno())
  assert sha(temp)==member['sha256'];os.link(temp,dest,follow_symlinks=False);temp.unlink()
 assert dest.stat().st_size==member['size'] and sha(dest)==member['sha256'];dest.chmod(0o444)
members=[{'relative_path':x['path'],'size':x['size'],'sha256':x['sha256']} for x in members];full={'schema':'READONLY_TRACE_INPUT_COMMIT_V1','status':'TRACE_MEMBERS_ARCHIVE_AND_CLOSED_REOPEN_SHA_VERIFIED','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'asset_id':m['asset_id'],'scope_sha256':hashlib.sha256(canon(m)).hexdigest(),'ordered_members':m['ordered_files'],'members':members,'ordered_member_set_sha256':hashlib.sha256(canon(members)).hexdigest(),'old_identity':m['old_composite_identity'],'old_identity_definition':m['old_identity_definition'],'source_root':m['source_root'],'native_mirror_mount_path':str(tree),'true164_tree':str(tree).replace('/root/share/mnt164','/home/shared',1),'raw_bytes':sum(r['size'] for r in members),'new_payload_bytes':newbytes,'Source_action':'SOURCE_KEEP','Source_simulator_starts':0,'Share_new_bytes':0,'not_a_result_outbox_qualification':True}
put(root/'TRACE_COMMIT.json',canon(full));assert json.loads((root/'TRACE_COMMIT.json').read_bytes())==full;(native/'control').mkdir(exist_ok=True);(native/'control'/(m['asset_id']+'_TRACE_RECEIPT.json')).write_bytes(canon(full));print(json.dumps({'event':'DONE','receipt':full}),flush=True)
'''
p=subprocess.Popen(['ssh','-o','BatchMode=yes','hrl-174-new','python3 -B -'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);p.stdin.write(code.encode());p.stdin.close();events=[]
for line in p.stdout:print(line.decode(errors='replace').rstrip(),flush=True);events.append(json.loads(line))
err=p.stderr.read();rc=p.wait();(D/(slug+'_TRANSFER_EVENTS.json')).write_bytes((json.dumps(events,indent=2)+'\n').encode());assert rc==0,err.decode(errors='replace');(R/(slug+'_TRACE_RECEIPT.json')).write_bytes((json.dumps(events[-1]['receipt'],indent=2)+'\n').encode())
