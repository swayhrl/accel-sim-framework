"""Engineering-only scoped Client storage adapter. No action on import.
No runtime/parser/controller callbacks or production/registry mutation.
"""
from contextlib import contextmanager
from pathlib import Path
import inspect,hashlib,os,re,stat
CC_SOURCE_SHA256='5c75173225ff002f2dcabc2f0b3b150d56d31d5bf1139ebf89baae2ab3eda34f'
E2_EVENT=re.compile(r'E2-[0-9]{8}-[0-9a-f]{12}\.json\Z')
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sink_paths(client):
 need(client.lane=='E2','only own E2 Client transport')
 event=client.path('events',event_id='E2-00000000-000000000000').parent
 cache=client.cache('local_owner_events',event_id='E2-00000000-000000000000').parent
 cursor=client.path('cursor');status=client.path('status')
 need(event==client.base/'events/E2' and cursor==client.base/'state/E2/cursor.json' and status==client.base/'status/E2.json','actual E2 contract projection differs')
 need(cache==client.mailbox/'E2/events' and client.mailbox.is_absolute(),'exact actual own mailbox cache differs')
 return {'event_dir':event,'cache_event_dir':cache,'cursor':cursor,'status':status}
@contextmanager
def coordination_sink(cc,client,writer,*,expected_source_sha256=CC_SOURCE_SHA256):
 source=Path(cc.__file__).resolve();need(hashlib.sha256(source.read_bytes()).hexdigest()==expected_source_sha256,'fixed coordination source differs')
 need(tuple(inspect.signature(cc.immutable).parameters)==('path','raw') and tuple(inspect.signature(cc.atomic).parameters)==('path','raw'),'actual storage API signature differs')
 need(not getattr(cc,'_e2_bounded_sink_active',False),'no nested global storage adapters')
 paths=sink_paths(client)
 transport_lock=client.mailbox/'E2/state/transport.lock'
 need(transport_lock.is_file() and not transport_lock.is_symlink() and transport_lock.stat().st_size==0,'existing original zero-byte transport lock required; no unmetered mkdir/create in Client.lock')
 def exact(path,kind):
  p=Path(path).absolute();writer.allowed_path(p)
  if kind=='immutable':need(p.parent in (paths['event_dir'],paths['cache_event_dir']) and E2_EVENT.fullmatch(p.name),'only own immutable E2 event/cache paths')
  else:need(p in (paths['cursor'],paths['status']),'only own mutable E2 cursor/status paths')
  return p
 original_immutable=cc.immutable;original_atomic=cc.atomic;prior_flag_present=hasattr(cc,'_e2_bounded_sink_active');prior_flag=getattr(cc,'_e2_bounded_sink_active',False)
 def immutable(path,raw):
  need(type(raw)is bytes,'preserve exact encoded bytes');p=exact(path,'immutable')
  if p.exists():need(cc.small_bytes(p,max(len(raw),65536))==raw,'conflicting immutable event: '+str(p));return False
  body=writer._body(raw,'control');writer.before_alias(p,hashlib.sha256(raw).hexdigest());p.parent.mkdir(parents=True,exist_ok=True)
  need(p.parent.stat().st_dev==body.stat().st_dev,'no unaccounted cross-device event copy')
  try:os.link(body,p) # destination O_EXCL semantics, never replace immutable path.
  except FileExistsError:
   need(cc.small_bytes(p,max(len(raw),65536))==raw,'conflicting immutable event: '+str(p));return False
  fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
  return True
 def atomic(path,raw):
  need(type(raw)is bytes,'preserve exact encoded bytes');p=exact(path,'atomic');writer.write_bytes(p,raw,'control');return None
 cc.immutable=immutable;cc.atomic=atomic;cc._e2_bounded_sink_active=True
 try:yield {'paths':{k:str(v) for k,v in paths.items()},'coordination_source_sha256':expected_source_sha256,'immutable_return':'True new, False existing-identical; conflict rejected','atomic_return':None,'original_Client_ownership_CAS_transport_locks_unchanged':True}
 finally:
  cc.immutable=original_immutable;cc.atomic=original_atomic
  if prior_flag_present:cc._e2_bounded_sink_active=prior_flag
  else:del cc._e2_bounded_sink_active

def actual_allocmeasure(writer):
 """Read-only snapshot: actual bodystore+journal+declared current aliases.
 No receipt is created/accounted here; the caller's later receipt bytes are not
 included or fabricated as a self-referential exact total.
 """
 state=writer.state();root=writer.root;store=writer.store;entries=list(root.iterdir());bodies=list(store.iterdir());need(len(entries)<=8 and len(bodies)<=128,'bounded owned store stat inventory')
 paths=[root,store,writer.journal]+[p for p in entries if p.is_file() and p!=writer.journal]+bodies
 for aliases in state['aliases'].values():paths.extend(Path(p) for p in aliases)
 seen_paths=set();seen_inodes=set();rows=[];missing=[];regular=directories=logical=0
 for p in paths:
  p=Path(p)
  if str(p) in seen_paths:continue
  seen_paths.add(str(p))
  need(not p.is_symlink(),'measurement must not follow alias symlinks')
  if not p.exists():missing.append(str(p));continue
  st=p.lstat();need(not p.is_symlink() and (stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode)),'measurement only exact owned regular metadata/dirs')
  key=(st.st_dev,st.st_ino);fresh=key not in seen_inodes
  if fresh:
   seen_inodes.add(key)
   if stat.S_ISDIR(st.st_mode):directories+=st.st_blocks*512
   else:regular+=st.st_blocks*512;logical+=st.st_size
  rows.append({'path':str(p),'device':st.st_dev,'inode':st.st_ino,'nlink':st.st_nlink,'bytes':st.st_size,'allocated_bytes':st.st_blocks*512,'kind':'directory' if stat.S_ISDIR(st.st_mode) else 'regular','counted_unique':fresh})
 return {'schema':'E2_R5_BOUNDED_WRITER_ACTUAL_METADATA_ALLOCATION_SNAPSHOT_V1','status':'ACTUAL_READONLY_STAT_SNAPSHOT_NOT_CLOSURE','condition_id':writer.cid,'actual_metadata_allocated_bytes':regular+directories,'regular_metadata_allocated_bytes':regular,'owned_root_directory_allocated_bytes':directories,'logical_regular_bytes_unique':logical,'unique_dev_inode_count':len(seen_inodes),'journal_head_at_snapshot':state['head'],'files':rows,'missing_prior_alias_paths':missing,'scope':'Owned bodystore/journal/direct root controls and registered current aliases; dev/inode deduplicated. Git infrastructure and shared alias parent directories excluded. Original runtime/raw/summary already OUTPUT, not copied/measured here.','receipt_self_bytes_included':False,'no_generation_refund_or_registry_write':True}
