"""Self-contained public trace runtime. Data migration/reading only, never science launch."""
from pathlib import Path
import os,sys,json,hashlib,importlib.util,stat,time,fcntl,contextlib,gzip,zlib
def bounded_metadata_raw(path,limit=128*2**20,consume=None):
 p=Path(path);link=p.lstat()
 ident=lambda v:(v.st_dev,v.st_ino,v.st_size,v.st_mtime_ns,v.st_ctime_ns,v.st_mode)
 physical=p.resolve(strict=True)if stat.S_ISLNK(link.st_mode)else p
 before=physical.lstat()
 if not stat.S_ISREG(before.st_mode)or before.st_size>limit:raise RuntimeError('RESOURCE_HOLD_METADATA_ENVELOPE_LIMIT_OR_TYPE')
 fd=os.open(physical,os.O_RDONLY|os.O_NOFOLLOW);parts=[];count=0
 with os.fdopen(fd,'rb',buffering=0)as f:
  if ident(os.fstat(f.fileno()))!=ident(before):raise RuntimeError('RESOURCE_HOLD_METADATA_FD_PATH_CHANGED')
  while True:
   raw=f.read(min(2**20,limit-count+1))
   if not raw:break
   count+=len(raw)
   if count>limit:raise RuntimeError('RESOURCE_HOLD_METADATA_ENVELOPE_GROWTH_LIMIT')
   parts.append(raw)
   if consume:consume(len(raw))
  if ident(os.fstat(f.fileno()))!=ident(before):raise RuntimeError('RESOURCE_HOLD_METADATA_FD_CHANGED')
 if ident(physical.lstat())!=ident(before)or ident(p.lstat())!=ident(link):raise RuntimeError('RESOURCE_HOLD_METADATA_PATH_CHANGED')
 return b''.join(parts)
PACKAGE=Path(__file__).resolve().parent
P=Path(json.loads(bounded_metadata_raw(PACKAGE/'PROFILE.json',4*2**20))['native_work_root'])
MIB=2**20;GIB=2**30;PROFILE='SM70_TARGET_BOUND_RESTORE_V3'
def load_verified(name):
 manifest=json.loads(bounded_metadata_raw(PACKAGE/'CODE_MANIFEST.json',4*2**20))
 row=manifest['files'][name+'.py'];path=PACKAGE/(name+'.py');raw=bounded_metadata_raw(path,8*MIB)
 if hashlib.sha256(raw).hexdigest()!=row['sha256']:raise RuntimeError('public helper manifest SHA: '+name)
 spec=importlib.util.spec_from_file_location('public_'+name+'_'+str(time.monotonic_ns()),path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def profile():
 value=json.loads(bounded_metadata_raw(PACKAGE/'PROFILE.json',4*2**20))
 return value
def need(x,msg):
 if not x:raise RuntimeError(msg)

def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()

def digest(x):return hashlib.sha256(x).hexdigest()

def raw_hash(p,consume=None):
 h=hashlib.sha256()
 with Path(p).open('rb',buffering=0)as f:
  while True:
   z=f.read(MIB)
   if not z:break
   h.update(z)
   if consume:consume(len(z))
 return h.hexdigest()

def token(s):return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_uid,s.st_gid)

def read_exact(stream,n,consume=None):
 """Legal short reads aggregate exactly; empty before n is a real truncation."""
 parts=[];left=n
 while left:
  z=stream.read(min(MIB,left));need(bool(z),'true EOF before exact requested byte count')
  need(len(z)<=left,'invalid stream oversized read')
  if consume:consume(z)
  else:parts.append(z)
  left-=len(z)
 return b''.join(parts)if consume is None else n

def allocated_tree(root):
 root=Path(root);total=root.lstat().st_blocks*512 if root.exists()else 0
 def err(e):
  if e.errno!=2:raise e
 for base,dirs,files in os.walk(root,onerror=err,followlinks=False):
  for n in dirs+files:
   try:s=os.lstat(Path(base)/n)
   except OSError as e:
    if e.errno==2:continue
    raise
   if not stat.S_ISLNK(s.st_mode):total+=s.st_blocks*512
 return total

class Relocation:
 def __init__(self,root,mapping,production=False,strict=None):
  self.root=Path(root).resolve();self.mapping=mapping;self.production=production;self.strict=production if strict is None else strict
  if production:need(str(self.root).startswith(profile()['nas_mount_root']+'/'),'production proof root must be public true164 mount')
 def resolve(self,original):
  key=str(Path(original).absolute())
  if key not in self.mapping:
   need(not self.strict,'unrelocated persistent metadata dependency: '+key)
   return Path(key),None
  row=self.mapping[key];rel=Path(row['relative_path'])
  need(not rel.is_absolute()and '..'not in rel.parts,'unsafe relocation')
  p=self.root/rel;need(p.resolve().is_relative_to(self.root)and not p.is_symlink(),'relocation path escape')
  need(p.name.split('.')[0]==row['sha256'],'proof CAS leaf must be content SHA')
  return p,row['sha256']

class Operation:
 """Own imported module per operation: no process-global cache or cross-operation reuse."""
 def __init__(self,resolver=None,resources=None,verify_close=True):
  self.resolver=resolver;self.resources=resources;self.verify_close=verify_close
  self.cache={};self.chains={};self.proof_indexes={};self.ledgers={};self.catalog_context=None;self.pointer_guards=[]
  self.stats=dict(envelope_reads=0,envelope_parses=0,envelope_bytes=0,exit_digest_reads=0,chain_builds=0,member_lookups=0,ledger_loads=0,ledger_rows_parsed=0)
  c=load_verified('core')
  c.NS=P;c.PROFILE=PROFILE;c.native_parent=native_destination_parent
  self.original_full_proof=c.current_proof_from_ref;self.original_put=c.put;self.original_builder=c.build_overlay;self.original_fast=c.fast
  self.c=c;c.read=self.read;c.sha=self.sha;c.ref=self.ref;c.historical=self.historical;c.current_proof_from_ref=self.proof;c.checked_ref=self.checked_ref;c.put=self.put;c.build_overlay=self.build_overlay;c.fast=self.fast
  c.full_target=lambda path,expected,config:full_target(self,path,expected,config)
  c.materialize=lambda catalog,binding,config,dest,max_bytes:materialize_object(self,catalog,binding,config,dest,max_bytes)
  c.window_restore=lambda catalog,binding,config,dest,ledger_path,window=64*MIB,max_bytes=None,resume=False:restore_object(self,catalog,binding,config,dest,ledger_path,max_bytes,window,resume)
  # Every such method now sees this operation's isolated globals.
 def __enter__(self):
  self.lease=None
  if self.resources:
   self.resources.check(True)
   self.lease=(P/'.NATIVE_BOUND_OPERATION.lock').open('a+b')
   try:
    fcntl.flock(self.lease,fcntl.LOCK_EX|fcntl.LOCK_NB);self.resources.check(True)
   except BaseException:self.lease.close();self.lease=None;raise
  return self
 def __exit__(self,typ,value,tb):
  try:
   if typ is None and self.verify_close:
    for path,identity,target in self.pointer_guards:
     need(token(path.lstat())==identity and path.resolve(strict=True)==target,'catalog pointer changed during operation')
    for ledger in self.ledgers.values():ledger.finish()
    for row in self.cache.values():
     p=row['physical'];before=p.stat();need(stat.S_ISREG(before.st_mode),'metadata type')
     need(raw_hash(p,(lambda n:self.resources.account(n,'read'))if self.resources else None)==row['sha256']and token(before)==token(p.stat()),'metadata changed during operation')
     self.stats['exit_digest_reads']+=1
  finally:
   if self.lease is not None:fcntl.flock(self.lease,fcntl.LOCK_UN);self.lease.close();self.lease=None
  return False
 def envelope(self,name):
  key=str(Path(name).absolute())
  if key in self.cache:return self.cache[key]
  native_proof=False;public_proof=False;path=Path(key)
  try:relative=path.relative_to(P/'integrations')
  except ValueError:relative=None
  if relative is not None and len(relative.parts)==4 and relative.parts[1]=='native_objects'and relative.parts[3]=='RESTORE_RECEIPT.json'and len(relative.parts[2])==64 and all(x in '0123456789abcdef'for x in relative.parts[2]):
   need(self.catalog_context is not None,'Native proof needs loaded catalog context')
   load_verified('primitive').no_symlinks(path)
   need(path.stat().st_dev==Path('/root/data').stat().st_dev and path.stat().st_size<=32*MIB,'controlled Native proof device/size')
   physical,expected=path,None;native_proof=True
  else:
   try:pubrel=path.relative_to(library_root()/'receipts/v3_native')
   except ValueError:pubrel=None
   if pubrel is not None and len(pubrel.parts)==3 and pubrel.parts[1]=='sha256'and len(pubrel.parts[2])==64 and all(x in '0123456789abcdef'for x in pubrel.parts[2]):
    need(self.catalog_context is not None,'public Native proof needs loaded catalog')
    load_verified('primitive').no_symlinks(path)
    need(path.stat().st_size<=32*MIB,'public Native proof compressed32MiB limit')
    physical,expected=path,pubrel.parts[2];public_proof=True
   else:physical,expected=self.resolver.resolve(key)if self.resolver else(Path(key),None)
  before=physical.lstat();need(stat.S_ISREG(before.st_mode)and not physical.is_symlink(),'metadata regular/no symlink')
  need(before.st_size<=128*MIB,'public metadata128MiB encoded envelope limit')
  fd=os.open(physical,os.O_RDONLY|os.O_NOFOLLOW)
  with os.fdopen(fd,'rb',buffering=0)as f:
   need(token(os.fstat(f.fileno()))==token(before),'metadata path/FD mismatch');raw_parts=[];read_bytes=0
   while True:
    part=f.read(MIB)
    if not part:break
    raw_parts.append(part);read_bytes+=len(part)
    need(read_bytes<=128*MIB,'metadata growth128MiB limit')
    if self.resources:self.resources.account(len(part),'read')
   raw=b''.join(raw_parts)
   need(token(os.fstat(f.fileno()))==token(before),'metadata FD changed')
  need(token(physical.stat())==token(before),'metadata path changed')
  h=digest(raw);need(expected is None or h==expected,'relocated metadata SHA mismatch')
  logical=raw;encoding='plain'
  if native_proof or public_proof:
   if raw.startswith(b'\x1f\x8b'):
    decoder=zlib.decompressobj(31)
    logical=decoder.decompress(raw,64*MIB+1)
    need(len(logical)<=64*MIB and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,'complete bounded Native proof gzip/CRC')
    encoding='gzip'
  doc=json.loads(logical)
  if native_proof:
   sha_key=relative.parts[2];binding=self.catalog_context['overlay']['bindings'][sha_key]
   need(doc.get('status')=='PASS_COMPLETE_SOURCE_AND_NATIVE_WINDOWS_SHA'and doc['context']==self.c.context_key(self.catalog_context,binding),'controlled Native proof exact context')
  if public_proof:
   need(encoding=='gzip','public Native CAS requires actual gzip container')
   sha_key=doc['context']['sha256'];binding=self.catalog_context['overlay']['bindings'][sha_key]
   need(doc.get('status')=='PASS_COMPLETE_SOURCE_AND_NATIVE_WINDOWS_SHA'and doc['context']==self.c.context_key(self.catalog_context,binding),'public Native proof exact context')
  row=dict(physical=physical,sha256=h,doc=doc,bytes=len(raw),controlled_public_native_proof=public_proof,encoding=encoding,logical_sha256=digest(logical),logical_bytes=len(logical))
  self.cache[key]=row;self.stats['envelope_reads']+=1;self.stats['envelope_parses']+=1;self.stats['envelope_bytes']+=len(raw)
  return row
 def fast(self,b,config,base_sha=None):
  if self.resources:self.resources.check(False)
  result=self.original_fast(b,config,base_sha)
  if self.resources:self.resources.account(result['bounded_open_reopen_sample_bytes'],'read')
  return result
 def put(self,path,doc):
  if self.resources:
   q=self.resources.check(True);size=len(self.c.canon(doc));need(q['own_allocated_bytes']+((size+4095)//4096)*4096+4096<=256*MIB,'metadata publication256MiB allocated budget')
  self.original_put(path,doc)
  if self.resources:self.resources.account(len(self.c.canon(doc)),'write');self.resources.check(True)
 def build_overlay(self,base,proofs,config,expected_reused,prepare_only=False):
  self.envelope(base)  # Validate/cache the original logical key; physical CAS is not a new resolver key.
  return self.original_builder(base,proofs,config,expected_reused,prepare_only)
 def read(self,p):return self.envelope(p)['doc']
 def sha(self,p):return self.envelope(p)['sha256']
 def ref(self,p):
  row=self.envelope(p);out=dict(path=str(Path(p).absolute()),sha256=row['sha256'])
  if row.get('encoding')=='gzip':out.update(encoding='gzip',uncompressed_sha256=row['logical_sha256'],uncompressed_bytes=row['logical_bytes'])
  return out
 def checked_ref(self,r):
  need(self.sha(r['path'])==r['sha256'],'proof envelope SHA')
  row=self.envelope(r['path'])
  if row['encoding']=='gzip'or row.get('controlled_public_native_proof')or r.get('encoding')=='gzip':
   need(r.get('encoding')=='gzip'and row['encoding']=='gzip'and row['logical_sha256']==r.get('uncompressed_sha256')and row['logical_bytes']==r.get('uncompressed_bytes'),'Native proof actual gzip requires dual physical/uncompressed SHA')
  return self.read(r['path'])
 def historical(self,key,obj):
  path=Path(obj['storage']['path']).absolute();tree=next((x for x in path.parents if x.name=='tree'),None);need(tree is not None,'tree ancestor absent')
  bundle=tree.parent;bid=str(bundle)
  if bid not in self.chains:
   cp,mp,rp,tp=[bundle/n for n in ['COMMIT.json','SOURCE_MANIFEST.json','RECEIPT.json','TREE_VERIFICATION.json']]
   commit,manifest,receipt,verification=[self.read(x)for x in [cp,mp,rp,tp]]
   need(commit['manifest_sha256']==self.sha(mp)and commit['object_id']==manifest['object_id']==receipt['object_id'],'COMMIT manifest/object mismatch')
   need(receipt['manifest_sha256']==commit['manifest_sha256']and receipt['Source_full_SHA_matches']is True and receipt['true164_closed_reopen_whole_SHA_matches']is True,'closed full SHA receipt chain')
   need(commit['tree_verification_sha256']==self.sha(tp),'tree proof SHA')
   def index(rows):
    out={}
    for r in rows:need(r['relative_path']not in out,'duplicate historical member');out[r['relative_path']]=r
    return out
   refs=[self.ref(x)for x in [cp,mp,rp,tp]]
   if commit.get('range_index_sha256'):
    rr=bundle/'RANGE_INDEX.json';need(self.sha(rr)==commit['range_index_sha256'],'range index SHA');refs.append(self.ref(rr))
   self.chains[bid]=dict(commit=commit,members=index(manifest['members']),verified=index(verification),references=refs,commit_sha=self.sha(cp),manifest_sha=self.sha(mp))
   self.stats['chain_builds']+=1
  q=self.chains[bid];rel=str(path.relative_to(tree));self.stats['member_lookups']+=1
  need(q['members'][rel]['sha256']==q['verified'][rel]['sha256']==key and q['members'][rel]['size']==q['verified'][rel]['size']==obj['size'],'member closed-chain mismatch')
  st=obj['storage']
  need(not st.get('commit_sha256')or st['commit_sha256']==q['commit_sha'],'old COMMIT SHA')
  need(not st.get('manifest_sha256')or st['manifest_sha256']==q['manifest_sha'],'old manifest SHA')
  refs=list(q['references'])
  if st.get('proof_reference'):
   r=st['proof_reference'];d=self.read(r)
   if Path(r).name=='COMMIT.json':need(self.sha(r)==q['commit_sha'],'prior COMMIT ref')
   else:need(d['object_id']==q['commit']['object_id']and d['manifest_sha256']==q['manifest_sha']and d['Source_full_SHA_matches']is True and d['true164_closed_reopen_whole_SHA_matches']is True,'prior receipt ref')
   refs.append(self.ref(r))
  return dict(status='ORIGINAL_CLOSED_FULL_SHA_CHAIN_BOUND',canonical_path=str(path),member=rel,content_sha256=key,bytes=obj['size'],references=refs,commit_object_id=q['commit']['object_id'])
 def proof(self,reference,key,size,obs):
  doc=self.read(reference['path']);need(self.sha(reference['path'])==reference['sha256'],'current proof envelope SHA')
  if doc.get('status')=='PASS_CURRENT_REUSED_PATH_FULL_SHA_BINDING':
   need(doc.get('read_mode')=='FRESH_FULL_CURRENT_PATH_SHA','only actual fresh503 proof accepted')
   need(doc.get('NAS_readback_not_Native_restore')is True and doc.get('inode_diagnostic_only')is True and doc.get('scientific_qualification_changed')is False,'503 declared scope')
   need(doc['object_sha256']==doc['actual_full_sha256']==key and doc['size']==doc['full_bytes_read_this_phase']==size,'503 whole SHA bytes')
   need(doc['path']==doc['canonical_path']==obs['canonical_path'],'503 exact canonical path')
   snapshots=[doc[k]for k in ['current_before','fd_before','fd_after','current_after']]
   need(all(x==snapshots[0]for x in snapshots),'503 FD/path before-after')
   need(snapshots[0]['type']=='file'and snapshots[0]['size']==size and snapshots[0]['mtime_ns']==obs['mtime_ns'],'503 stable metadata')
   return dict(status='VALIDATED_ORIGINAL_503_PATH_EXACT_FULL_SHA',original_receipt=reference,mode_baseline_is_admission_not_old_proof=True)
  if doc.get('schema')=='ORIGINAL20_CURRENT_TRUE164_NAS_READBACK_V1':
   ident=reference['sha256']
   if ident not in self.proof_indexes:
    need(self.sha(doc['catalog_path'])==doc['catalog_sha256'],'old20 original catalog SHA')
    idx={}
    for r in doc['members']:
     k=(str(Path(r['path']).absolute()),r['expected_sha256']);need(k not in idx,'duplicate old20 proof member');idx[k]=r
    self.proof_indexes[ident]=idx
   need(doc['status']=='PASS_CURRENT_NAS_FULL_SHA_ALL_MEMBERS','old20 status')
   r=self.proof_indexes[ident][(obs['canonical_path'],key)]
   need(r['matched']is True and r['actual_full_sha256']==key and r['full_bytes_read_this_pass']==size and not r['deduplicated_prior_same_path_full_read'],'old20 exact full read')
   fields=['dev','ino','size','mtime_ns','type'];identity=lambda z:tuple(z[k]for k in fields)
   need(all(identity(r[k])==identity(r['before'])for k in ['fd_before','fd_after','after']),'old20 live FD proof')
   need(r['before']['size']==size and r['after']['mtime_ns']==obs['mtime_ns']and r['before']['type']=='regular','old20 metadata')
   return dict(status='VALIDATED_ORIGINAL20_PATH_EXACT_FULL_SHA',original_receipt=reference,mode_baseline_is_admission_not_old_proof=True)
  return self.original_full_proof(reference,key,size,obs)
 def ledger(self,path,catalog):
  key=str(Path(path).absolute())
  need(self.catalog_context is None or self.catalog_context['catalog_id']==catalog['catalog_id'],'operation catalog identity conflict')
  self.catalog_context=catalog
  if key not in self.ledgers:self.ledgers[key]=Ledger(self,path,catalog)
  need(self.ledgers[key].catalog['catalog_id']==catalog['catalog_id'],'ledger reused with another catalog')
  return self.ledgers[key]

class Ledger:
 def __init__(self,op,path,catalog):
  self.op=op;self.path=Path(path);self.catalog=catalog;self.rows={};self.offset=0;self.identity=None;self.expected_hash=hashlib.sha256()
  op.stats['ledger_loads']+=1
  if self.path.exists():
   before=self.path.stat();need(before.st_size<=128*MIB,'ledger physical128MiB metadata cap')
   with self.path.open('rb',buffering=0)as f:
    total=0
    while True:
     line=f.readline(2*MIB+1)
     if not line:break
     total+=len(line)
     need(total<=128*MIB and len(line)<=2*MIB and line.endswith(b'\n'),'ledger cumulative128MiB/line2MiB/completeLF cap')
     self.expected_hash.update(line)
     if op.resources:op.resources.account(len(line),'read')
     row=json.loads(line);self.validate(row);need(row['key']not in self.rows,'duplicate ledger key');self.rows[row['key']]=row;op.stats['ledger_rows_parsed']+=1
    need(token(os.fstat(f.fileno()))==token(before),'ledger changed during load')
   need(token(self.path.stat())==token(before),'ledger path changed during load')
   self.offset=before.st_size;self.identity=token(before)
 def validate(self,row):
  c=self.catalog;core=self.op.c;need(row.get('schema')=='SM70_BOUND_RESTORE_LEDGER_V2','old sha-only ledger refused')
  ctx=row['context'];binding=c['overlay']['bindings'][ctx['sha256']]
  actual=self.op.envelope(row['receipt']['path'])
  if actual['encoding']=='gzip'or actual.get('controlled_public_native_proof'):
   need(row.get('code_version_id')==code_manifest()['code_version_id']and row.get('integration_id')==self.path.parent.name,'public proof code/integration context')
   need(Path(row['receipt']['path']).is_relative_to(library_root()/'receipts/v3_native'/row['integration_id']/'sha256'),'public proof controlled integration CAS')
  need(ctx==core.context_key(c,binding)and row['key']==core.ledger_key(ctx),'ledger exact catalog/binding/profile/canonical context')
  r=core.checked_ref(row['receipt'])
  need(r['status']=='PASS_COMPLETE_SOURCE_AND_NATIVE_WINDOWS_SHA'and r['context']==ctx and not r.get('prebinding_only',False),'ledger receipt context/provisional')
  need(r['source_sha256']==r['native_sha256']==ctx['sha256']and r['source_bytes']==ctx['size']and r['EOF_checked']is True and r['source_KEEP']is True and r['science_changed']is False,'whole Native receipt')
  core.validate_full_proof(r['current_target_proof'],ctx['sha256'],ctx['size'],binding['stable_metadata'])
  offset=0
  for w in r['windows']:
   need(w['offset']==offset and 0<w['bytes']<=64*MIB and w['source_sha256']==w['closed_sha256'],'window chain')
   if 'native_closed_identity'in w:
    need(w['Native_write_and_closed_reopen_FD_path_stable']is True and len(w['native_closed_identity'])==8 and w['native_closed_identity'][2]==w['bytes']and stat.S_ISREG(w['native_closed_identity'][5]),'Native window observation identity')
   offset+=w['bytes']
  need(offset==ctx['size'],'window completeness')
 def lookup(self,context):return self.rows.get(self.op.c.ledger_key(context))
 def append(self,row):
  self.validate(row);need(row['key']not in self.rows,'duplicate ledger append')
  self.path.parent.mkdir(parents=True,exist_ok=True)
  with self.path.open('a+b',buffering=0)as f:
   fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   now=os.fstat(f.fileno());need(now.st_size==self.offset and(self.identity is None or token(now)==self.identity),'ledger external append/change')
   data=canon(row);need(len(data)<=2*MIB and self.offset+len(data)<=128*MIB,'ledger append128MiB/line2MiB metadata cap');need(f.write(data)==len(data),'short ledger append');os.fsync(f.fileno());self.offset+=len(data);self.expected_hash.update(data);self.identity=token(os.fstat(f.fileno()))
  self.rows[row['key']]=row
  if self.op.resources:self.op.resources.account(len(data),'write');self.op.resources.check(True)
 def finish(self):
  if self.path.exists():need(raw_hash(self.path,(lambda n:self.op.resources.account(n,'read'))if self.op.resources else None)==self.expected_hash.hexdigest(),'ledger end-operation digest mismatch')

def restore_object(op,catalog,binding,config,dest,ledger_path,logical_max=None,window_max=64*MIB,resume=False,stream_factory=None):
 """Complete logical object; bounded disk windows, no whole-window RAM allocation."""
 c=op.c;ctx=c.context_key(catalog,binding);ledger=op.ledger(ledger_path,catalog)
 old=ledger.lookup(ctx)
 if old:
  need(resume,'explicit exact-bound resume required')
  return dict(status='RESUMED_EXACT_BOUND_PRIOR_NATIVE_RESTORE_NOT_FRESH_THIS_CALL',context=ctx,fresh_full_SHA_this_call=False,receipt=old['receipt'])
 need(logical_max is None or binding['size']<=logical_max,'explicit logical object cap')
 need(0<window_max<=64*MIB,'Native window limit')
 dest=Path(dest);need(dest.resolve().is_relative_to(P)and not dest.exists(),'absent private destination')
 c.fast(binding,config,catalog['base_all_objects_sha256']);native=c.native_parent(dest)
 resources=op.resources;need(resources is not None,'resource gate required')
 resources.check(True);dest.mkdir()
 before=c.observed(ctx['canonical_path'],config);fd=os.open(ctx['canonical_path'],os.O_RDONLY|os.O_NOFOLLOW)
 source_hash=hashlib.sha256();native_hash=hashlib.sha256();offset=0;windows=[]
 with os.fdopen(fd,'rb',buffering=0)as raw:
  fb=c.fd_observed(raw.fileno(),ctx['canonical_path'],config);need(c.live(before)==c.live(fb),'initial FD/path')
  source=stream_factory(raw)if stream_factory else raw
  while offset<binding['size']:
   target=min(resources.window(window_max),binding['size']-offset);path=dest/(str(offset)+'.window');wh=hashlib.sha256()
   with path.open('xb',buffering=0)as out:
    native_open=os.fstat(out.fileno());need(native_open.st_dev==Path('/root/data').stat().st_dev and stat.S_ISREG(native_open.st_mode),'Native window write FD device/type')
    def consume(z):
     source_hash.update(z);wh.update(z);resources.account(len(z),'read')
     view=memoryview(z)
     while view:
      n=out.write(view);need(n>0,'short/zero local write');resources.account(n,'write');view=view[n:]
    read_exact(source,target,consume);os.fsync(out.fileno());native_closed=token(os.fstat(out.fileno()))
   need(token(path.lstat())==native_closed,'Native window write FD/path identity')
   closed=hashlib.sha256();n=0;localfd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
   with os.fdopen(localfd,'rb',buffering=0)as f:
    need(token(os.fstat(f.fileno()))==native_closed,'Native closed reopen FD/path identity')
    while True:
     z=f.read(MIB)
     if not z:break
     closed.update(z);native_hash.update(z);n+=len(z);resources.account(len(z),'read')
    need(token(os.fstat(f.fileno()))==native_closed,'Native reopened FD changed')
   need(token(path.lstat())==native_closed,'Native reopened path changed')
   need(n==target and closed.hexdigest()==wh.hexdigest(),'closed complete Native window SHA')
   windows.append(dict(offset=offset,bytes=target,source_sha256=wh.hexdigest(),closed_sha256=closed.hexdigest(),native_closed_identity=list(native_closed),Native_write_and_closed_reopen_FD_path_stable=True));offset+=target
   path.unlink();resources.check(True)
  need(source.read(1)==b'','source trailing bytes');fa=c.fd_observed(raw.fileno(),ctx['canonical_path'],config)
 after=c.observed(ctx['canonical_path'],config)
 need(c.live(before)==c.live(fb)==c.live(fa)==c.live(after),'live FD/path changed')
 need(source_hash.hexdigest()==native_hash.hexdigest()==binding['sha256'],'complete source/Native SHA')
 proof=dict(schema='CURRENT_TARGET_FULL_SHA_V2',status='CURRENT_TARGET_FULL_SHA_VERIFIED',path_before=before,fd_before=fb,fd_after=fa,path_after=after,expected_sha256=binding['sha256'],actual_sha256=source_hash.hexdigest(),bytes_read=offset,EOF_checked=True,science_changed=False)
 r=dict(native_filesystem=native,current_target_proof=proof,status='PASS_COMPLETE_SOURCE_AND_NATIVE_WINDOWS_SHA',context=ctx,source_bytes=offset,source_sha256=source_hash.hexdigest(),native_sha256=native_hash.hexdigest(),windows=windows,window_limit=window_max,EOF_checked=True,path_before=before,fd_before=fb,fd_after=fa,path_after=after,source_KEEP=True,fresh_full_SHA_this_call=True,science_changed=False)
 rp=dest/'RESTORE_RECEIPT.json';c.put(rp,r);resources.check(True)
 recover_completed_native_receipt(op,catalog,binding,rp,ledger_path)
 return r

def full_target(op,path,expected,config):
 c=op.c;need(op.resources is not None,'resource gate required')
 before=c.observed(path,config);h=hashlib.sha256();n=0;fd=os.open(before['canonical_path'],os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb',buffering=0)as f:
  fb=c.fd_observed(f.fileno(),path,config);need(c.live(fb)==c.live(before),'initial full FD/path')
  while True:
   z=f.read(MIB)
   if not z:break
   h.update(z);n+=len(z);op.resources.account(len(z),'read')
  fa=c.fd_observed(f.fileno(),path,config)
 after=c.observed(path,config);need(c.live(before)==c.live(fb)==c.live(fa)==c.live(after),'full FD/path changed')
 need(n==before['size']and h.hexdigest()==expected,'complete full SHA')
 return dict(schema='CURRENT_TARGET_FULL_SHA_V2',status='CURRENT_TARGET_FULL_SHA_VERIFIED',path_before=before,fd_before=fb,fd_after=fa,path_after=after,expected_sha256=expected,actual_sha256=h.hexdigest(),bytes_read=n,EOF_checked=True,science_changed=False)

def materialize_object(op,catalog,binding,config,dest,max_bytes):
 c=op.c;resources=op.resources;need(resources is not None,'resource gate required')
 dest=Path(dest);need(not os.path.lexists(dest)and binding['size']<=max_bytes,'explicit materialization cap');native_destination_parent(dest)
 q=resources.check(True);need((q['own_allocated_bytes']+binding['size']+16*MIB<=256*MIB)if dest.resolve().is_relative_to(P)else q['free']>=q['required_free']+binding['size'],'complete materialization own/control or external shared headroom')
 c.fast(binding,config,catalog['base_all_objects_sha256']);native=c.native_parent(dest);before=c.observed(binding['stable_metadata']['canonical_path'],config)
 fd=os.open(before['canonical_path'],os.O_RDONLY|os.O_NOFOLLOW);h=hashlib.sha256();n=0
 with os.fdopen(fd,'rb',buffering=0)as source,dest.open('xb',buffering=0)as out:
  fb=c.fd_observed(source.fileno(),before['canonical_path'],config);need(c.live(fb)==c.live(before),'materialize FD/path')
  while True:
   z=source.read(MIB)
   if not z:break
   h.update(z);n+=len(z);resources.account(len(z),'read')
   view=memoryview(z)
   while view:
    k=out.write(view);need(k>0,'local short write');resources.account(k,'write');view=view[k:]
  os.fsync(out.fileno());fa=c.fd_observed(source.fileno(),before['canonical_path'],config)
 local=hashlib.sha256();localn=0
 with dest.open('rb',buffering=0)as f:
  while True:
   z=f.read(MIB)
   if not z:break
   local.update(z);localn+=len(z);resources.account(len(z),'read')
 after=c.observed(before['canonical_path'],config);need(c.live(before)==c.live(fb)==c.live(fa)==c.live(after),'materialization live change')
 need(n==localn==binding['size']and h.hexdigest()==local.hexdigest()==binding['sha256'],'complete materialization whole SHA')
 resources.check(True)
 return dict(status='PASS_COMPLETE_MATERIALIZATION_SHA',context=c.context_key(catalog,binding),native_filesystem=native,source_sha256=h.hexdigest(),closed_local_sha256=local.hexdigest(),bytes=n,source_KEEP=True,science_changed=False)

def legacy_declaration(op,key,obj,route,obs):
 """Link genuine legacy declarations and current exact-path SHA; never invent V9 fields."""
 need(key in route['objects']and obj['sha256']==key,'legacy object/base identity outside frozen route')
 refs=route['legacy_refs']
 for r in refs:need(op.sha(r['path'])==r['sha256'],'legacy raw envelope SHA')
 root=Path(route['root']);path=Path(obj['storage']['path']).absolute();rel=str(path.relative_to(root/'tree'))
 byname={Path(r['path']).name:r for r in refs}
 if route['profile']=='LEGACY_NN_ROWS_CLOSED_SHA_V1':
  commit=op.read(byname['COMMIT.json']['path']);mref=byname['SOURCE_MANIFEST.json'];manifest=op.read(mref['path'])
  need(commit['manifest_sha256']==op.sha(mref['path'])and commit['originals']=='SOURCE_KEEP','legacy NN declaration manifest')
  need(manifest['schema']=='LEGACY_NN_EXACT_TWO_TRACE_MEMBERS_COPY_ONLY_V1'and manifest['originals']=='SOURCE_KEEP','legacy NN schema')
  rows={r['name']:r for r in manifest['rows']};need(len(rows)==len(manifest['rows'])==commit['files']and sum(r['bytes']for r in rows.values())==commit['bytes'],'legacy NN file cardinality/bytes')
  row=rows[rel];need(row['sha256']==row['closed_reopened_sha256']==key and row['bytes']==obj['size'],'legacy NN member SHA/bytes')
  need(row['true164_path']==str(path).replace('/root/share/mnt164','/home/shared',1),'legacy NN true164 path')
  scope=dict(schema=manifest['schema'],cohort=manifest['cohort'])
 elif route['profile']=='READONLY_TRACE_INPUT_COMMIT_AND_SCOPE_V1':
  cref=byname['TRACE_COMMIT.json'];sref=byname['INPUT_SCOPE.json'];commit=op.read(cref['path']);scope_doc=op.read(sref['path'])
  need(commit['schema']=='READONLY_TRACE_INPUT_COMMIT_V1'and commit['status']=='TRACE_MEMBERS_ARCHIVE_AND_CLOSED_REOPEN_SHA_VERIFIED','legacy trace commit')
  need(commit['scope_sha256']==op.sha(sref['path'])and scope_doc['schema']=='INDEPENDENT_COLD_TRACE_MEMBER_INPUT_PROTOCOL_V1','legacy raw scope SHA/schema')
  need(commit['asset_id']==scope_doc['asset_id']and scope_doc['Source_action']==commit['Source_action']=='SOURCE_KEEP','legacy asset/source scope')
  need(commit['native_mirror_mount_path']==str(root/'tree')and scope_doc['target_root']==str(root),'legacy scoped path')
  members={r['relative_path']:r for r in commit['members']};files={r['relative_path']:r for r in scope_doc['files']}
  need(len(members)==len(commit['members'])and len(files)==len(scope_doc['files'])and set(members)==set(files),'legacy scope exact member set')
  row=members[rel];decl=files[rel]
  need(row['sha256']==key and row['size']==decl['size']==obj['size'],'legacy member SHA/size')
  need(decl['expected_sha256']is None or decl['expected_sha256']==key,'legacy scope expected SHA')
  scope=dict(schema=scope_doc['schema'],owner_accepted_baseline=scope_doc['owner_accepted_baseline'],old_identity_definition=scope_doc['old_identity_definition'],original_scope_expected_SHA=decl['expected_sha256'],null_expected_SHA_not_filled=True)
 else:raise RuntimeError('unknown legacy route')
 proof=route['original_current_proofrefs'][key];op.proof(proof,key,obj['size'],obs)
 return dict(status='LEGACY_DECLARATION_LINK_AND_CURRENT_FULL_SHA_BOUND',canonical_path=str(path),member=rel,content_sha256=key,bytes=obj['size'],references=[dict(path=r['path'],sha256=r['sha256'])for r in refs]+[proof],legacy_profile=route['profile'],legacy_scope=scope,historical_Source_full_SHA_claim_not_created=True,historical_Native_restore_claim_not_created=True,current_path_full_SHA_reference=proof)

def attach_legacy(op,routes,config):
 """Per-operation explicit routes frozen in future overlay, no global registry."""
 op.legacy_routes={r['root']:r for r in routes}
 standard=op.c.historical
 def historical(key,obj):
  path=Path(obj['storage']['path']).absolute();root=next((x.parent for x in path.parents if x.name=='tree'),None)
  route=op.legacy_routes.get(str(root))
  if route:return legacy_declaration(op,key,obj,route,op.c.observed(path,config))
  return standard(key,obj)
 op.c.historical=historical
 original=op.c.recheck_history
 def recheck(h,key,size,path):
  if h['status']!='LEGACY_DECLARATION_LINK_AND_CURRENT_FULL_SHA_BOUND':return original(h,key,size,path)
  need(h['content_sha256']==key and h['bytes']==size and h['canonical_path']==str(Path(path).resolve()),'legacy binding context')
  for r in h['references']:op.checked_ref(r)
  need(h['historical_Source_full_SHA_claim_not_created']is True and h['historical_Native_restore_claim_not_created']is True,'legacy scope flags')
 op.c.recheck_history=recheck

def binding_set_sha(c):
 return digest(canon({k:v['binding_id']for k,v in c['overlay']['bindings'].items()}))

def gate_pins(c):
 return dict(catalog_id=c['catalog_id'],overlay_id=c['overlay_id'],binding_set_sha256=binding_set_sha(c),profile=PROFILE)

def validate_gate(receipt,pins,require_full=False,require_native=False):
 need(receipt.get('schema')=='SM70_BOUND_PUBLIC_OPERATION_V3','legacy/unknown Gate schema refused')
 need(receipt['pins']==pins and pins['profile']==PROFILE,'exact Gate pins mismatch')
 need(receipt['scientific_qualification_granted']is False,'science upgrade')
 accepted=['PASS_BOUND_METADATA_ACCESS_NOT_FRESH_SHA_V3','PASS_BOUND_CURRENT_FULL_SHA_V3','PASS_BOUND_NATIVE_WHOLE_RESTORE_V3','PASS_BOUND_COMPLETE_MATERIALIZATION_V3']
 need(receipt['status']in accepted,'unqualified status')
 if require_full:need(receipt['fresh_all_SHA_this_call']is True and receipt['status']!='PASS_BOUND_METADATA_ACCESS_NOT_FRESH_SHA_V3','Gate requires fresh full SHA')
 if require_native:need(receipt['status']=='PASS_BOUND_NATIVE_WHOLE_RESTORE_V3'and receipt['all_bound_objects_complete']is True,'finish Gate whole Native proof required')
 return dict(status='PASS_EXACT_V3_GATE_SCOPE_ONLY',pins=pins,scientific_qualification_granted=False)

def public_operation(op,c,operation,asset=None,suite=None,kind='all',full=False,dest=None,max_bytes=256*MIB,dry=False,all_assets=False):
 """Retains user-facing operation names/filters/aliases; emits a new exact-pin receipt."""
 assets=[a for a in c['assets']if(not suite or a['suite']==suite)and(kind=='all'or a['kind']==kind)]
 if operation=='list':
  return dict(catalog_id=c['catalog_id'],access_scope='ALL_PROJECTS',assets=assets,issues_path=c.get('issues_path'),coverage_path=c.get('coverage_path'),scientific_qualification_granted=False)
 if not all_assets:
  hits=[a for a in assets if a['bundle_id']==asset or(a['bundle_id'].startswith(asset or '')and asset)or asset in a.get('aliases',[])]
  need(len(hits)==1,'unknown/ambiguous asset');assets=hits
 need(assets,'empty asset selection')
 if operation=='show':return assets[0]
 if operation=='verify':
  rows=[op.c.verify_asset(c,a,full)for a in assets]
  return dict(schema='SM70_BOUND_PUBLIC_OPERATION_V3',status='PASS_BOUND_CURRENT_FULL_SHA_V3'if full else'PASS_BOUND_METADATA_ACCESS_NOT_FRESH_SHA_V3',pins=gate_pins(c),fresh_all_SHA_this_call=full,assets=rows,scientific_qualification_granted=False)
 need(operation=='materialize'and dest,'explicit materialization destination')
 need(len(assets)==1,'materialize one complete asset')
 a=assets[0];destination=Path(dest)
 need(destination.is_absolute()and '..'not in destination.parts and not os.path.lexists(destination),'materialize absolute ABSENT destination')
 native_destination_parent(destination)
 op.c.native_parent(destination)
 total=sum(m['size']for m in a['members']);q=op.resources.check(True)
 admitted=total<=max_bytes and((q['own_allocated_bytes']+total+16*MIB<=256*MIB)if destination.resolve().is_relative_to(P)else q['free']>=q['required_free']+total)
 if dry:return dict(admitted=admitted,logical_bytes=total,max_bytes=max_bytes,total_task_cap=256*MIB,source_KEEP=True,scientific_qualification_granted=False)
 need(admitted,'complete materialization total/control budget')
 result=materialize_asset(op,c,a,Path(dest),max_bytes)
 return dict(schema='SM70_BOUND_PUBLIC_OPERATION_V3',status='PASS_BOUND_COMPLETE_MATERIALIZATION_V3',pins=gate_pins(c),fresh_all_SHA_this_call=True,result=result,scientific_qualification_granted=False)

def finish_receipt(op,catalog,ledger_path):
 need(catalog['catalog_id']==op.c.catalog_id(catalog),'finish frozen catalog ID')
 ledger=op.ledger(ledger_path,catalog);ledger.finish();core=op.c
 expected={core.ledger_key(core.context_key(catalog,b))for b in catalog['overlay']['bindings'].values()}
 need(set(ledger.rows)==expected,'finish requires exact ALL-object Native receipt coverage')
 return dict(schema='SM70_BOUND_PUBLIC_OPERATION_V3',status='PASS_BOUND_NATIVE_WHOLE_RESTORE_V3',pins=gate_pins(catalog),all_bound_objects_complete=True,objects=len(expected),logical_bytes=sum(b['size']for b in catalog['overlay']['bindings'].values()),ledger_sha256=ledger.expected_hash.hexdigest(),fresh_all_SHA_this_call=False,source_KEEP=True,scientific_qualification_granted=False)

def validate_finish_gate(op,catalog,receipt,pins,ledger_path):
 validate_gate(receipt,pins,require_native=True)
 need(finish_receipt(op,catalog,ledger_path)==receipt,'finish summary must match freshly validated exact bound ledger')
 return dict(status='PASS_EXACT_V3_NATIVE_LEDGER_GATE_SCOPE_ONLY',pins=pins,scientific_qualification_granted=False)

def enrich_assets(bundles,architecture_by_sha=None,public_root='/root/workspace/assets/traces'):
 import re
 architecture_by_sha=architecture_by_sha or{}
 slug=lambda x:re.sub('[^A-Za-z0-9_.+-]+','_',x).strip('_')or'unknown'
 out=[]
 for b in bundles:
  kind='fraction'if b['extent']=='FRACTION_OR_TRIM_PATH'else'regular'
  version='3.1'if b['version']=='3.1'else'2.0-ft'if b['version']=='2.0-ft'else'unconfirmed'if b['version']=='unconfirmed'else'9.1-capture'if b['suite']=='CUDA Samples'else'1.0-mapped'if b['suite']=='PolyBench/GPU'else'suite11'
  bid=b['bundle_id'];view=Path('views')/slug(b['suite'])/version/slug(b['program'])/kind/bid
  architecture=','.join(sorted({architecture_by_sha.get(m['sha256'],'UNKNOWN')for m in b['members']if m['relative_path']!='kernelslist.g'}))or'UNKNOWN'
  out.append(dict(b,kind=kind,architecture=architecture,source_version_evidence=b['version'],version=version,kernel_launches=len(b['ordered_kernel_members']),logical_bytes=sum(m['size']for m in b['members']),view_path=str(Path(public_root)/view),relative_view_path=str(view),relative_tree_path=str(Path('bundles')/bid/'tree'),availability='DECLARED_REQUIRES_COMPLETE_BINDING_OVERLAY',scientific_qualification_granted=False,aliases=sorted(set(b.get('prior_asset_aliases',[])))))
 return sorted(out,key=lambda a:(a['suite'],a['version'],a['program'],a['kind'],a['bundle_id']))

def validate_cross_reports(c,reports,expected_cwds):
 need(c['catalog_id']==digest(canon({k:v for k,v in c.items()if k!='catalog_id'})),'cross frozen catalog ID')
 need(len(reports)==len(expected_cwds)==3 and{r['cwd']for r in reports}==set(expected_cwds),'three exact project cwd receipts')
 expected={a['bundle_id']:{m['relative_path']for m in a['members']}for a in c['assets']}
 for report in reports:
  r=report['verify'];validate_gate(r,gate_pins(c))
  need(r['status']=='PASS_BOUND_METADATA_ACCESS_NOT_FRESH_SHA_V3'and r['fresh_all_SHA_this_call']is False,'cross fast scope')
  actual={}
  for a in r['assets']:
   need(a['bundle_id']not in actual,'cross duplicate bundle')
   names=[m['relative_path']for m in a['members']];need(len(names)==len(set(names)),'cross duplicate member');actual[a['bundle_id']]=set(names)
  need(actual==expected,'cross all declared members exact')
  byasset={a['bundle_id']:a for a in c['assets']}
  for observed_asset in r['assets']:
   declared=byasset[observed_asset['bundle_id']]
   membermap={x['relative_path']:x for x in declared['members']}
   need(observed_asset['status']=='PASS_METADATA_ACCESS_WITH_BOUND_HISTORICAL_SHA_NOT_FRESH_BODY'and observed_asset['full_sha_recomputed']is False,'cross per-asset scope')
   for observed_member in observed_asset['members']:
    binding=c['overlay']['bindings'][membermap[observed_member['relative_path']]['sha256']]
    result=observed_member['result']
    need(result['binding_id']==binding['binding_id']and result['status']=='PASS_METADATA_ACCESS_WITH_BOUND_HISTORICAL_SHA_NOT_FRESH_BODY'and result['full_sha_recomputed']is False and result['fresh_body_sha_verified']is False,'cross per-member binding/scope')
 return dict(schema='SM70_CROSS_PROJECT_V3',status='PASS_EXACT_V3_ALL_ASSET_METADATA_ACCESS_NOT_FRESH_SHA',pins=gate_pins(c),project_cwds=sorted(expected_cwds),projects_tested=3,all_declared_members_checked=True,project_activation_required=False,scientific_starts=0,scientific_qualification_granted=False,reports=reports)

def validate_finish_metadata(op,c,cross,native_receipt,ledger,expected_cwds,expected_aliases,prior20,protected_before,protected_after,archive_proofs,archive_expectations=None,archive_receipt_sha256s=None):
 need(cross['schema']=='SM70_CROSS_PROJECT_V3'and cross['pins']==gate_pins(c),'cross version/exact pins')
 validate_cross_reports(c,cross['reports'],expected_cwds)
 validate_finish_gate(op,c,native_receipt,gate_pins(c),ledger)
 seen={(x.get('host'),x.get('path'),a['extent'])for a in c['assets']for x in a['source_aliases']}
 need(all((x['host'],x['path'],x['extent'])in seen for x in expected_aliases),'missing original input aliases')
 need(len(prior20)==20 and all(any(set(p['aliases'])&set(a['aliases'])for a in c['assets'])for p in prior20),'all20 prior asset aliases')
 need(protected_before and set(protected_before)==set(protected_after)and all(protected_after[k]==v for k,v in protected_before.items()),'all declared protected scientific hashes unchanged')
 if profile()['execution_scope']=='PRODUCTION':
  need(all(isinstance(k,str)and k.startswith('/')and isinstance(v,str)and len(v)==64 and all(ch in '0123456789abcdef'for ch in v)for k,v in protected_before.items()),'Root protected map exact nonempty absolute SHA fields')
  need(isinstance(archive_expectations,list)and len(archive_expectations)==4 and isinstance(archive_receipt_sha256s,list)and len(archive_receipt_sha256s)==4 and len(set(archive_receipt_sha256s))==4,'Root four archive identity expectations and raw receipt pins')
  expected={x['receipt_sha256']:x for x in archive_expectations};need(set(expected)==set(archive_receipt_sha256s)and len(expected)==4,'exact Root archive receipt set')
  actual_paths=set();actual_identities=set()
  def select(doc,fields):
   need(isinstance(fields,list)and fields,'Root archive selector nonempty')
   for field in fields:doc=doc[field]
   return doc
  for receipt_sha,doc in zip(archive_receipt_sha256s,archive_proofs):
   e=expected[receipt_sha];path=select(doc,e['archive_path_field']);identity=select(doc,e['identity_field'])
   need(path==e['archive_path']and identity==e['archive_identity']and isinstance(path,str)and path.startswith('/')and isinstance(identity,dict)and identity,'actual archive identity matches Root declaration')
   actual_paths.add(path);actual_identities.add(digest(canon(identity)))
  need(len(actual_paths)==len(actual_identities)==4,'four unique actual archive path and identity sets')
 need(len(archive_proofs)==4 and all(a['source_before_after_unchanged']and a['compressed_bytes_read']==a['archive_identity']['size']and a.get('inventory_format')=='V2_FULL_DECODED_EOF_IGNORE_ZEROS'and a['decoded_compression_EOF_integrity_checked']for a in archive_proofs),'all4 complete archive integrity receipts')
 return dict(status='PASS_V3_FINISH_METADATA_AND_WHOLE_NATIVE_GATES',pins=gate_pins(c),objects=len(c['overlay']['bindings']),assets=len(c['assets']),source_KEEP=True,production_goal_complete_claimed=False,scientific_qualification_granted=False)

def validate_all_asset_full(c,receipt):
 need(c['catalog_id']==digest(canon({k:v for k,v in c.items()if k!='catalog_id'})),'full frozen catalog ID')
 validate_gate(receipt,gate_pins(c),require_full=True)
 need(receipt['status']=='PASS_BOUND_CURRENT_FULL_SHA_V3','whole-assets full status')
 expected={a['bundle_id']:{m['relative_path']:m for m in a['members']}for a in c['assets']}
 need(len(receipt['assets'])==len(expected)and len({a['bundle_id']for a in receipt['assets']})==len(expected),'full all-assets exact denominator')
 for a in receipt['assets']:
  members=expected[a['bundle_id']];need(a['full_sha_recomputed']is True and len(a['members'])==len(members)and{r['relative_path']for r in a['members']}==set(members),'full all declared members')
  for observed in a['members']:
   b=c['overlay']['bindings'][members[observed['relative_path']]['sha256']];r=observed['result']
   need(r['binding_id']==b['binding_id']and r['fresh_body_sha_verified']is True and r['full_sha_recomputed']is True,'full member binding/freshness')
 return dict(status='PASS_EXACT_ALL_ASSETS_CURRENT_FULL_SHA_V3',pins=gate_pins(c),assets=len(expected),scientific_qualification_granted=False)


class Resources:
 def __init__(self,work=None,extra_budget_roots=()):
  need(work is None or Path(work).resolve()==P.resolve(),'platform Native work root mismatch')
  self.module=load_verified('resources');self.inner=self.module.Resources(profile(),extra_budget_roots)
 def check(self,force=False):return self.inner.check(force)
 def window(self,n):return self.inner.window(n)
 def account(self,n,direction):return self.inner.account(n,direction)
 @property
 def counters(self):return self.inner.counters
 @property
 def samples(self):return self.inner.samples
def native_destination_parent(dest):
 dest=Path(dest);need(dest.is_absolute()and '..'not in dest.parts and not os.path.lexists(dest),'absolute ABSENT materialization destination')
 primitive=load_verified('primitive');primitive.no_symlinks(dest)
 native=Path('/root/data');parent=dest.parent
 while not parent.exists():parent=parent.parent
 need(dest.resolve().is_relative_to(native.resolve())and parent.stat().st_dev==native.stat().st_dev,'Native destination outside verified data device')
 lib=library_root();need(not dest.resolve().is_relative_to(lib.resolve())and not str(dest.resolve()).startswith(('/root/share/','/home/shared/')),'cannot write public/NAS tree')
 return dict(native_root='/root/data',native_device=parent.stat().st_dev,hostname=os.uname().nodename)
def library_root():
 return (PACKAGE/profile()['library_root_relative']).resolve()
def materialize_asset(op,c,asset,dest,max_bytes):
 dest=Path(dest);native_destination_parent(dest);total=sum(m['size']for m in asset['members'])
 q=op.resources.check(True);need(total<=max_bytes,'explicit whole-asset byte cap')
 if dest.resolve().is_relative_to(P):need(q['own_allocated_bytes']+total+16*MIB<=256*MIB,'platform256MiB complete materialization cap')
 else:need(q['free']>=q['required_free']+total,'external project full materialization shared headroom')
 dest.mkdir();rows=[]
 for member in asset['members']:
  out=op.c.safe_member(dest,member['relative_path']);out.parent.mkdir(parents=True,exist_ok=True)
  rows.append(dict(relative_path=member['relative_path'],receipt=materialize_object(op,c,c['overlay']['bindings'][member['sha256']],c['overlay']['config'],out,max_bytes)))
 receipt=dict(schema='SM70_BOUND_COMPLETE_BUNDLE_MATERIALIZATION_V3',bundle_id=asset['bundle_id'],pins=gate_pins(c),profile=PROFILE,status='PASS_COMPLETE_LOCAL_BUNDLE_SHA',logical_bytes=total,members=rows,source_KEEP=True,scientific_qualification_granted=False)
 path=dest.with_name(dest.name+'.MATERIALIZATION_RECEIPT.json')
 need(not os.path.lexists(path),'materialization receipt must be absent')
 raw=canon(receipt)
 with path.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 need(bounded_metadata_raw(path)==raw,'closed materialization receipt bytes')
 return receipt

def code_manifest():
 value=json.loads(bounded_metadata_raw(PACKAGE/'CODE_MANIFEST.json',4*2**20))
 expected=digest(canon({k:v for k,v in value.items()if k!='code_version_id'}))
 need(value['code_version_id']==expected and PACKAGE.name==expected,'immutable public code-version identity')
 return value
def verify_package():
 manifest=code_manifest()
 for name,row in manifest['files'].items():
  rel=Path(name);need(not rel.is_absolute()and '..'not in rel.parts,'unsafe code member')
  raw=bounded_metadata_raw(PACKAGE/rel,8*MIB);need(len(raw)==row['bytes']and digest(raw)==row['sha256'],'public package file SHA: '+name)
 return manifest
def load_public_catalog(op):
 need(not op.cache,'catalog loader needs a fresh operation cache')
 lib=library_root();path=lib/'catalog/CURRENT';identity=token(path.lstat());target=path.resolve(strict=True)
 need(target.is_relative_to(lib/'catalog/versions')and path.is_symlink(),'public catalog pointer controlled namespace')
 envelope=op.read(target)
 need(token(path.lstat())==identity and path.resolve(strict=True)==target,'catalog pointer changed while loading')
 op.pointer_guards.append((path,identity,target))
 need(envelope['schema']=='SHARED_SM70_TRACE_LIBRARY_V3','old catalog schema requires explicit migration')
 need(envelope['publication_id']==digest(canon({k:v for k,v in envelope.items()if k!='publication_id'})),'catalog publication body ID')
 need(envelope['code_version_id']==code_manifest()['code_version_id'],'catalog requires another immutable public code version')
 relocation=envelope['relocation'];op.resolver=Relocation(lib/relocation['relative_root'],relocation['mapping'],strict=True)
 c=envelope['catalog'];base=envelope['base_all_objects_ref'];bundles=envelope['base_all_bundles_ref']
 need(op.sha(base['path'])==base['sha256']==c['base_all_objects_sha256'],'frozen ALL_OBJECTS public snapshot')
 need(op.sha(bundles['path'])==bundles['sha256']==c['base_all_bundles_sha256'],'frozen ALL_BUNDLES public snapshot')
 need(c['schema']=='SHARED_SM70_TRACE_LIBRARY_V3'and c['catalog_id']==op.c.catalog_id(c)and c['profile']==PROFILE and c['science_acceptance_granted']is False,'catalog content/profile/science')
 need(envelope['catalog_id']==c['catalog_id']and envelope['pins']==gate_pins(c),'public exact catalog/binding/profile pins')
 attach_legacy(op,envelope['legacy_routes'],c['overlay']['config'])
 op.c.validate_overlay(c['overlay'],base['path'])
 op.catalog_context=c
 return c,envelope
def public_main(argv=None):
 import argparse
 verify_package()
 parser=argparse.ArgumentParser(description='All-project shared trace assets, immutable public V3')
 parser.add_argument('operation',choices=['list','show','verify','materialize']);parser.add_argument('asset',nargs='?')
 parser.add_argument('--suite');parser.add_argument('--kind',choices=['regular','fraction','all'],default='all')
 parser.add_argument('--all',action='store_true');parser.add_argument('--full',action='store_true');parser.add_argument('--destination')
 parser.add_argument('--max-bytes',type=int,default=256*MIB);parser.add_argument('--dry-run',action='store_true')
 args=parser.parse_args(argv)
 resources=Resources()
 with Operation(resources=resources)as op:
  c,envelope=load_public_catalog(op)
  result=public_operation(op,c,args.operation,args.asset,args.suite,args.kind,args.full,args.destination,args.max_bytes,args.dry_run,args.all)
  if isinstance(result,dict):result['code_version_id']=envelope['code_version_id']
 print(json.dumps(result,indent=2))

def recover_completed_native_receipt(op,catalog,binding,local_path,ledger_path):
 """Commit compressed public proof+dual SHA ledger before releasing only an owned temporary."""
 local=Path(local_path);ledger_path=Path(ledger_path);ctx=op.c.context_key(catalog,binding)
 relative=local.relative_to(P/'integrations')
 need(len(relative.parts)==4 and relative.parts[1]=='native_objects'and relative.parts[2]==binding['sha256']and relative.parts[3]=='RESTORE_RECEIPT.json','owned complete Native receipt path')
 integration=relative.parts[0]
 need(ledger_path.parent==P/'integrations'/integration,'Native ledger integration root')
 ledger=op.ledger(ledger_path,catalog)
 local_ref=op.ref(local);doc=op.checked_ref(local_ref)
 candidate=dict(schema='SM70_BOUND_RESTORE_LEDGER_V2',key=op.c.ledger_key(ctx),context=ctx,receipt=local_ref)
 ledger.validate(candidate)
 raw=bounded_metadata_raw(local,32*MIB);need(digest(raw)==local_ref['sha256'],'local proof changed before CAS')
 logical=gzip.decompress(raw)if local_ref.get('encoding')=='gzip'else raw
 need(json.loads(logical)==doc and len(logical)<=64*MIB,'exact logical proof bytes')
 packed=gzip.compress(logical,compresslevel=6,mtime=0);uncompressed_sha=digest(logical)
 writer=load_verified('storage').Writer(library_root(),op.resources,load_verified('primitive'))
 public=writer.cas(packed,'receipts/v3_native/'+integration)
 proofref=dict(path=public['path'],sha256=public['sha256'],encoding='gzip',uncompressed_sha256=uncompressed_sha,uncompressed_bytes=len(logical))
 need(op.checked_ref(proofref)==doc,'closed public Native proof full decode/CRC/equality')
 row=dict(schema='SM70_BOUND_RESTORE_LEDGER_V2',key=op.c.ledger_key(ctx),context=ctx,receipt=proofref,code_version_id=code_manifest()['code_version_id'],integration_id=integration)
 existing=ledger.lookup(ctx)
 if existing is None:ledger.append(row)
 else:
  ledger.validate(existing)
  need(existing['receipt'].get('uncompressed_sha256',op.envelope(existing['receipt']['path'])['logical_sha256'])==uncompressed_sha,'existing exact observation differs')
 # append validates exact prior offset/FD identity and fsyncs the canonical row.
 # Full ledger digest is checked once at operation close/final, never N times.
 if existing is not None and Path(existing['receipt']['path']).absolute()==local.absolute():
  # A frozen historical ledger row may not be rewritten merely to reclaim bytes.
  return dict(status='PRESERVED_LEGACY_LOCAL_LEDGER_PROOF_NO_RELEASE',context=ctx,public_CAS_copy=proofref,original_local_reference=existing['receipt'],native_local_proof_released=False,Source_KEEP=True)
 # No user materialization path or original target can reach this exact controlled subtree.
 need(local.is_file()and not local.is_symlink()and digest(bounded_metadata_raw(local,32*MIB))==local_ref['sha256'],'owned local proof cleanup identity')
 need(set(x.name for x in local.parent.iterdir())=={'RESTORE_RECEIPT.json'},'unexpected object scratch entries')
 local.unlink();op.cache.pop(str(local.absolute()),None);local.parent.rmdir()
 return dict(status='PASS_PUBLIC_NATIVE_PROOF_CAS_AND_FSYNCED_LEDGER',context=ctx,receipt=proofref,uncompressed_sha256=uncompressed_sha,native_local_proof_released=True,Source_KEEP=True,observation_not_simultaneous_full_file_residency=True)
