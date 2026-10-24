"""Vendored data-binding core; no private code/proof import. Source engine is never modified."""
from pathlib import Path
import os,stat,json,hashlib,time,shutil
NS=Path('/root/data/shared_trace_assets_platform_v3')
PROFILE='SM70_TARGET_BOUND_RESTORE_V3'
MAX_WINDOW=64*2**20
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def digest(x):return hashlib.sha256(x).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def put(p,x):
 p=Path(p);assert p.resolve().is_relative_to(NS)and not p.exists();p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(canon(x));f.flush();os.fsync(f.fileno())
def read(p):
 with Path(p).open('rb')as f:raw=f.read(128*2**20+1)
 assert len(raw)<=128*2**20,'metadata128MiB'
 return json.loads(raw)
def ref(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def checked_ref(r):
 p=Path(r['path']);assert p.is_file()and not p.is_symlink()and sha(p)==r['sha256'],'proof envelope SHA';return read(p)
def location(path,config):
 mount=Path(config['mount_root']).resolve();p=Path(path);real=p.resolve(strict=True)
 assert real.is_relative_to(mount)and p.is_file()and not p.is_symlink(),'unapproved target/type/symlink'
 return dict(endpoint=config['endpoint'],remote_path=str(Path(config['remote_root'])/real.relative_to(mount)),canonical_path=str(real))
def observed(path,config):
 loc=location(path,config);s=Path(loc['canonical_path']).lstat()
 assert stat.S_ISREG(s.st_mode)
 return dict(**loc,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,mode=stat.S_IMODE(s.st_mode),uid=s.st_uid,gid=s.st_gid,nlink=s.st_nlink,type='file',dev=s.st_dev,inode=s.st_ino)
def stable(o):return {k:o[k]for k in ['endpoint','remote_path','canonical_path','type','size','mtime_ns','mode']}
def live(o):return tuple(o[k]for k in ['canonical_path','dev','inode','size','mtime_ns','ctime_ns','mode','uid','gid','type'])
def fd_observed(fd,path,config):
 s=os.fstat(fd);loc=location(path,config)
 return dict(**loc,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,mode=stat.S_IMODE(s.st_mode),uid=s.st_uid,gid=s.st_gid,nlink=s.st_nlink,type='file'if stat.S_ISREG(s.st_mode)else'other',dev=s.st_dev,inode=s.st_ino)
def validate_full_proof(doc,expected_sha,size,obs):
 assert doc['schema']=='CURRENT_TARGET_FULL_SHA_V2'and doc['status']=='CURRENT_TARGET_FULL_SHA_VERIFIED'
 assert doc['actual_sha256']==doc['expected_sha256']==expected_sha and doc['bytes_read']==size
 assert stable(doc['path_before'])==stable(obs)==stable(doc['path_after'])
 assert live(doc['path_before'])==live(doc['fd_before'])==live(doc['fd_after'])==live(doc['path_after'])
 assert doc['EOF_checked']is True and doc['science_changed']is False
def full_target(path,expected_sha,config,hook=None,chunk=2**20):
 before=observed(path,config);h=hashlib.sha256();n=0
 fd=os.open(before['canonical_path'],os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb',buffering=0)as f:
  fb=fd_observed(f.fileno(),path,config);assert live(fb)==live(before)
  while True:
   b=f.read(chunk)
   if not b:break
   h.update(b);n+=len(b)
   if hook:hook();hook=None
  fa=fd_observed(f.fileno(),path,config)
 after=observed(path,config);assert live(before)==live(fb)==live(fa)==live(after),'target changed during full read'
 assert n==before['size']and h.hexdigest()==expected_sha,'whole target SHA mismatch'
 return dict(schema='CURRENT_TARGET_FULL_SHA_V2',status='CURRENT_TARGET_FULL_SHA_VERIFIED',path_before=before,fd_before=fb,fd_after=fa,path_after=after,expected_sha256=expected_sha,actual_sha256=h.hexdigest(),bytes_read=n,EOF_checked=True,ended_unix=time.time(),science_changed=False)
def historical(object_sha,obj):
 """Authenticate the original closed COMMIT/source/receipt/tree proof, never payload body."""
 path=Path(obj['storage']['path']).resolve();tree=next((x for x in [path.parent,*path.parents]if x.name=='tree'),None);assert tree
 bundle=tree.parent;cp=bundle/'COMMIT.json';mp=bundle/'SOURCE_MANIFEST.json';rp=bundle/'RECEIPT.json';tp=bundle/'TREE_VERIFICATION.json'
 c=read(cp);m=read(mp);r=read(rp);t=read(tp)
 assert c['manifest_sha256']==sha(mp)and c['object_id']==m['object_id']==r['object_id']
 assert r['manifest_sha256']==c['manifest_sha256']and r['Source_full_SHA_matches']is True and r['true164_closed_reopen_whole_SHA_matches']is True
 assert c['tree_verification_sha256']==sha(tp)
 rel=str(path.relative_to(tree));member=next(x for x in m['members']if x['relative_path']==rel)
 assert member['sha256']==object_sha and member['size']==obj['size']
 entry=next(x for x in t if x['relative_path']==rel);assert entry['sha256']==object_sha and entry['size']==obj['size']
 storage=obj['storage']
 if storage.get('commit_sha256'):assert sha(cp)==storage['commit_sha256']
 if storage.get('manifest_sha256'):assert sha(mp)==storage['manifest_sha256']
 refs=[ref(x)for x in [cp,mp,rp,tp]]
 if c.get('range_index_sha256'):
  rr=bundle/'RANGE_INDEX.json';assert sha(rr)==c['range_index_sha256'];refs.append(ref(rr))
 if storage.get('proof_reference'):
  original=Path(storage['proof_reference']);a=read(original)
  if original.name=='COMMIT.json':assert sha(original)==sha(cp)
  else:assert a['manifest_sha256']==c['manifest_sha256']and a['object_id']==c['object_id']and a['Source_full_SHA_matches']is True and a['true164_closed_reopen_whole_SHA_matches']is True
  refs.append(ref(original))
 return dict(status='ORIGINAL_CLOSED_FULL_SHA_CHAIN_BOUND',canonical_path=str(path),member=rel,content_sha256=object_sha,bytes=obj['size'],references=refs,commit_object_id=c['object_id'])
def recheck_history(h,object_sha,size,path):
 assert h['status']=='ORIGINAL_CLOSED_FULL_SHA_CHAIN_BOUND'and h['canonical_path']==str(Path(path).resolve())and h['content_sha256']==object_sha and h['bytes']==size
 for r in h['references']:checked_ref(r)
def current_proof_from_ref(reference,expected_sha,size,obs):
 doc=checked_ref(reference)
 if doc.get('schema')=='CURRENT_TARGET_FULL_SHA_V2':
  validate_full_proof(doc,expected_sha,size,obs);return doc
 if doc.get('status')=='PASS_COMPLETE_SOURCE_AND_NATIVE_WINDOWS_SHA':
  validate_full_proof(doc['current_target_proof'],expected_sha,size,obs);return doc['current_target_proof']
 # Existing original20 receipt: no invented mode/ctime fields are added.
 assert doc.get('schema')=='ORIGINAL20_CURRENT_TRUE164_NAS_READBACK_V1'and doc.get('status')=='PASS_CURRENT_NAS_FULL_SHA_ALL_MEMBERS'
 assert sha(doc['catalog_path'])==doc['catalog_sha256']
 rows=[r for r in doc['members']if str(Path(r['path']).resolve())==obs['canonical_path']and r['expected_sha256']==expected_sha]
 assert len(rows)==1;r=rows[0]
 assert r['matched']is True and r['actual_full_sha256']==expected_sha and r['full_bytes_read_this_pass']==size
 assert not r['deduplicated_prior_same_path_full_read'],'dedup requires first actual full path receipt'
 keys=['dev','ino','size','mtime_ns','type']
 assert all(tuple(r[x][k]for k in keys)==tuple(r['before'][k]for k in keys)for x in ['fd_before','fd_after','after'])
 assert r['before']['size']==size and r['after']['mtime_ns']==obs['mtime_ns']and r['before']['type']=='regular'
 return dict(status='EXISTING_CURRENT_FULL_SHA_PATH_EXACT_RECEIPT_VALIDATED',original_receipt=reference,mode_baseline_observed_at_binding_admission_not_forged_into_old_receipt=True)
def binding_id(b):return digest(canon({k:v for k,v in b.items()if k not in ['binding_id','inode_diagnostics']}))
def validate_binding(b,base_sha=None):
 assert b['schema']=='SM70_TARGET_BINDING_V2'and b['binding_id']==binding_id(b)
 if base_sha is not None:assert b['base_all_objects_sha256']==base_sha,'wrong base ALL_OBJECTS hash'
 recheck_history(b['historical'],b['sha256'],b['size'],b['stable_metadata']['canonical_path'])
 return b
def fast(b,config,base_sha=None):
 validate_binding(b,base_sha);now=observed(b['stable_metadata']['canonical_path'],config)
 assert stable(now)==b['stable_metadata'],'current target stable metadata/path drift'
 samples=[]
 for attempt in range(2):
  fd=os.open(now['canonical_path'],os.O_RDONLY|os.O_NOFOLLOW)
  with os.fdopen(fd,'rb',buffering=0)as f:
   fb=fd_observed(f.fileno(),now['canonical_path'],config);assert live(fb)==live(now)
   first=f.read(min(128,now['size']));f.seek(max(0,now['size']-32));tail=f.read(32)
   fa=fd_observed(f.fileno(),now['canonical_path'],config);assert live(fb)==live(fa)
  assert live(observed(now['canonical_path'],config))==live(now);samples.append((first,tail))
 assert samples[0]==samples[1]
 return dict(status='PASS_METADATA_ACCESS_WITH_BOUND_HISTORICAL_SHA_NOT_FRESH_BODY',full_sha_recomputed=False,fresh_body_sha_verified=False,bounded_open_reopen_sample_bytes=sum(len(x)for pair in samples for x in pair),binding_id=b['binding_id'],current_inode_diagnostic=now['inode'],science_changed=False)
def verify_binding(b,config,full=False,base_sha=None):
 a=fast(b,config,base_sha)
 if not full:return a
 proof=full_target(b['stable_metadata']['canonical_path'],b['sha256'],config);a.update(status='PASS_CURRENT_TARGET_FULL_SHA',full_sha_recomputed=True,fresh_body_sha_verified=True,proof=proof);return a
def overlay_id(o):return digest(canon({k:v for k,v in o.items()if k!='overlay_id'}))
def build_overlay(base_path,proof_index,config,expected_reused,prepare_only=False):
 objects=read(base_path);base_sha=sha(base_path)  # Per-operation verified cache supplies both, no second raw read.
 reused={k:o for k,o in objects.items()if'expected_identity'in o['storage']}
 assert len(reused)==expected_reused,'reused denominator mismatch'
 missing=sorted(set(reused)-set(proof_index))
 if missing and prepare_only:
  return dict(schema='SM70_STORAGE_BINDING_OVERLAY_V2_DRAFT',status='HOLD_REQUIRED_CURRENT_FULL_SHA_INCOMPLETE',base_all_objects_sha256=base_sha,expected_reused=expected_reused,current_full_proof_index_entries=len(set(reused)&set(proof_index)),missing_reused=missing,all_objects=len(objects),new_CAS_commit_chains_not_yet_claimed=True,complete=False,science_changed=False)
 assert not missing,'incomplete required reused proof coverage'
 assert set(proof_index)<=set(reused),'unknown proof index objects'
 bindings={}
 for key,obj in objects.items():
  assert obj['sha256']==key and len(key)==64
  h=historical(key,obj);obs=observed(obj['storage']['path'],config);assert obs['size']==obj['size']
  proof=None
  if key in reused:
   proofref=proof_index[key];proof=current_proof_from_ref(proofref,key,obj['size'],obs)
  else:proofref=None
  b=dict(schema='SM70_TARGET_BINDING_V2',base_all_objects_sha256=base_sha,sha256=key,size=obj['size'],storage_kind=obj['storage']['kind'],stable_metadata=stable(obs),historical=h,current_full_SHA_reference=proofref,current_full_SHA_scope='PATH_EXACT_REUSED_REQUALIFICATION'if proofref else'ORIGINAL_NEW_CAS_CLOSED_COMMIT_CHAIN',science_context_unchanged=True,inode_diagnostics=dict(frozen_expected_identity=obj['storage'].get('expected_identity'),admission_observed_inode=obs['inode'],dev=obs['dev']))
  b['binding_id']=binding_id(b);bindings[key]=b
 o=dict(schema='SM70_STORAGE_BINDING_OVERLAY_V2',status='PASS_COMPLETE_TARGET_BINDINGS',base_all_objects_sha256=base_sha,endpoint=config['endpoint'],config=config,all_objects=len(objects),expected_reused=expected_reused,verified_reused=len(reused),bindings=bindings,complete=True,source_engine_same_source_unchanged=True,science_changed=False)
 o['overlay_id']=overlay_id(o);return o
def validate_overlay(o,base_path):
 assert o['schema']=='SM70_STORAGE_BINDING_OVERLAY_V2'and o['status']=='PASS_COMPLETE_TARGET_BINDINGS'and o['complete']is True
 assert o['overlay_id']==overlay_id(o)and o['base_all_objects_sha256']==sha(base_path)
 objects=read(base_path);assert set(o['bindings'])==set(objects)and o['all_objects']==len(objects)
 reused=[k for k,v in objects.items()if'expected_identity'in v['storage']]
 assert len(reused)==o['verified_reused']==o['expected_reused']
 for k,b in o['bindings'].items():
  validate_binding(b,o['base_all_objects_sha256']);assert b['sha256']==k and b['size']==objects[k]['size']
  assert b['stable_metadata']['canonical_path']==str(Path(objects[k]['storage']['path']).resolve())
  assert b['storage_kind']==objects[k]['storage']['kind']
  assert b['stable_metadata']['endpoint']==o['config']['endpoint']
  assert location(b['stable_metadata']['canonical_path'],o['config'])=={x:b['stable_metadata'][x]for x in ['endpoint','remote_path','canonical_path']}
  if k in reused:current_proof_from_ref(b['current_full_SHA_reference'],k,b['size'],b['stable_metadata'])
 return o
def catalog_id(c):return digest(canon({k:v for k,v in c.items()if k!='catalog_id'}))
def publish_private(base_path,bundles_path,overlay,dest):
 validate_overlay(overlay,base_path)
 assets=read(bundles_path);assert isinstance(assets,list)
 for asset in assets:
  assert asset.get('scientific_qualification_granted',False)is False
  for member in asset['members']:
   safe_member(Path('/synthetic'),member['relative_path'])
   binding=overlay['bindings'][member['sha256']];assert binding['size']==member['size']
 dest=Path(dest);assert dest.resolve().is_relative_to(NS)and not dest.exists(),'private ABSENT candidate only'
 c=dict(schema='SHARED_SM70_TRACE_LIBRARY_FUSE_BINDING_V2_CANDIDATE',base_all_objects_sha256=sha(base_path),base_all_bundles_sha256=sha(bundles_path),overlay_id=overlay['overlay_id'],overlay=overlay,assets=read(bundles_path),science_acceptance_granted=False,deployed=False,profile=PROFILE)
 c['catalog_id']=catalog_id(c);put(dest,c);return c
def load_catalog(path,base_path):
 c=read(path);assert c['schema']=='SHARED_SM70_TRACE_LIBRARY_FUSE_BINDING_V2_CANDIDATE'and c['catalog_id']==catalog_id(c)and c['science_acceptance_granted']is False
 assert c['profile']==PROFILE and c['base_all_objects_sha256']==sha(base_path)
 validate_overlay(c['overlay'],base_path);assert c['overlay_id']==c['overlay']['overlay_id']
 return c
def context_key(c,b,profile=None):
 profile=PROFILE if profile is None else profile
 assert profile==PROFILE==c['profile'],'exact current context profile required'
 return dict(catalog_id=c['catalog_id'],overlay_id=c['overlay_id'],binding_id=b['binding_id'],base_all_objects_sha256=c['base_all_objects_sha256'],profile=profile,canonical_path=b['stable_metadata']['canonical_path'],sha256=b['sha256'],size=b['size'])
def ledger_key(ctx):return digest(canon(ctx))
def headroom():
 reserve=6*2**30+MAX_WINDOW
 registry=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
 if registry.exists():reserve+=sum(x.get('reserved_write_bytes',0)for x in read(registry).get('registered_future_requests',{}).values())
 return reserve

def native_parent(dest):
 dest=Path(dest);assert dest.resolve().is_relative_to(NS)
 parent=dest.parent
 while not parent.exists():parent=parent.parent
 assert parent.stat().st_dev==NS.stat().st_dev==Path('/root/data').stat().st_dev,'Native destination device mismatch'
 return dict(native_root='/root/data',native_device=parent.stat().st_dev,hostname=os.uname().nodename)
def window_restore(c,b,config,dest,ledger_path,window=MAX_WINDOW,max_bytes=MAX_WINDOW,resume=False,free_floor=None,hook=None,corrupt_window=False):
 assert 0<window<=MAX_WINDOW and max_bytes>=b['size'];ctx=context_key(c,b);key=ledger_key(ctx);ledger_path=Path(ledger_path);old={};seen=set()
 if ledger_path.exists():
  for line in ledger_path.read_text().splitlines():
   row=json.loads(line);assert row.get('schema')=='SM70_BOUND_RESTORE_LEDGER_V2'and 'context'in row,'legacy sha-only ledger refused'
   lc=row['context'];assert row['key']==ledger_key(lc)
   assert all(lc[k]==ctx[k]for k in ['catalog_id','overlay_id','base_all_objects_sha256','profile']),'restore ledger catalog/profile mismatch'
   lb=c['overlay']['bindings'][lc['sha256']]
   assert lc==context_key(c,lb),'restore ledger binding/canonical path mismatch'
   receipt=checked_ref(row['receipt']);assert receipt['context']==lc and receipt['status']=='PASS_COMPLETE_SOURCE_AND_NATIVE_WINDOWS_SHA'
   assert receipt['source_sha256']==receipt['native_sha256']==lc['sha256']and receipt['source_bytes']==lc['size']
   assert receipt['source_KEEP']is True and receipt['science_changed']is False
   validate_full_proof(receipt['current_target_proof'],lc['sha256'],lc['size'],lb['stable_metadata'])
   assert receipt.get('prebinding_only',False)is False,'provisional proof cannot satisfy final ledger'
   assert row['key']not in seen,'duplicate ledger key refused';seen.add(row['key'])
   offset=0
   for w in receipt['windows']:
    assert w['offset']==offset and 0<w['bytes']<=MAX_WINDOW and w['source_sha256']==w['closed_sha256'];offset+=w['bytes']
   assert offset==lc['size']and receipt['EOF_checked']is True
   if row['key']==key:old[key]=receipt
 if old:
  assert resume,'explicit exact-ledger resume required'
  return dict(status='RESUMED_EXACT_BOUND_PRIOR_NATIVE_RESTORE_NOT_FRESH_THIS_CALL',fresh_full_SHA_this_call=False,context=ctx,receipt=old[key])
 fast(b,config,c['base_all_objects_sha256']);dest=Path(dest);native=native_parent(dest)
 assert dest.resolve().is_relative_to(NS)and not dest.exists(),'Native candidate destination must be ABSENT'
 assert shutil.disk_usage(dest.parent).free>=min(window,b['size'])+(headroom()if free_floor is None else free_floor),'restore budget/headroom'
 dest.mkdir();before=observed(ctx['canonical_path'],config);sourcehash=hashlib.sha256();nativehash=hashlib.sha256();offset=0;windows=[]
 fd=os.open(ctx['canonical_path'],os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb',buffering=0)as source:
  fb=fd_observed(source.fileno(),ctx['canonical_path'],config);assert live(fb)==live(before)
  while offset<b['size']:
   n=min(window,b['size']-offset);data=source.read(n);assert len(data)==n,'truncated source'
   sourcehash.update(data);p=dest/(str(offset)+'.window')
   with p.open('xb')as out:out.write(data);out.flush();os.fsync(out.fileno())
   if corrupt_window:p.write_bytes(bytes([data[0]^1])+data[1:]);corrupt_window=False
   closed=p.read_bytes();assert len(closed)==n and digest(closed)==digest(data),'closed Native window mismatch'
   nativehash.update(closed);p.unlink();windows.append(dict(offset=offset,bytes=n,source_sha256=digest(data),closed_sha256=digest(closed)));offset+=n
   if hook:hook();hook=None
  assert source.read(1)==b'','source trailing bytes';fa=fd_observed(source.fileno(),ctx['canonical_path'],config)
 after=observed(ctx['canonical_path'],config);assert live(before)==live(fb)==live(fa)==live(after),'FD/path changed during restore'
 assert sourcehash.hexdigest()==nativehash.hexdigest()==b['sha256'],'whole source/Native SHA mismatch'
 targetproof=dict(schema='CURRENT_TARGET_FULL_SHA_V2',status='CURRENT_TARGET_FULL_SHA_VERIFIED',path_before=before,fd_before=fb,fd_after=fa,path_after=after,expected_sha256=b['sha256'],actual_sha256=sourcehash.hexdigest(),bytes_read=offset,EOF_checked=True,science_changed=False)
 receipt=dict(native_filesystem=native,current_target_proof=targetproof,status='PASS_COMPLETE_SOURCE_AND_NATIVE_WINDOWS_SHA',context=ctx,source_bytes=offset,source_sha256=sourcehash.hexdigest(),native_sha256=nativehash.hexdigest(),windows=windows,window_limit=window,EOF_checked=True,path_before=before,fd_before=fb,fd_after=fa,path_after=after,source_KEEP=True,fresh_full_SHA_this_call=True,science_changed=False)
 rp=dest/'RESTORE_RECEIPT.json';put(rp,receipt)
 row=dict(schema='SM70_BOUND_RESTORE_LEDGER_V2',key=key,context=ctx,receipt=ref(rp))
 ledger_path.parent.mkdir(parents=True,exist_ok=True)
 with ledger_path.open('a')as f:f.write(canon(row).decode());f.flush();os.fsync(f.fileno())
 return receipt
def materialize(c,b,config,dest,max_bytes,hook=None):
 fast(b,config,c['base_all_objects_sha256']);dest=Path(dest);native=native_parent(dest);assert not dest.exists()and dest.resolve().is_relative_to(NS)and b['size']<=max_bytes
 assert shutil.disk_usage(dest.parent).free>=b['size']+headroom(),'materialize headroom'
 before=observed(b['stable_metadata']['canonical_path'],config);sourcehash=hashlib.sha256();n=0;dest.parent.mkdir(parents=True,exist_ok=True)
 fd=os.open(before['canonical_path'],os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb',buffering=0)as source,dest.open('xb')as out:
  fb=fd_observed(source.fileno(),before['canonical_path'],config);assert live(fb)==live(before)
  while True:
   data=source.read(1024)
   if not data:break
   sourcehash.update(data);n+=len(data);out.write(data)
   if hook:hook();hook=None
  out.flush();os.fsync(out.fileno());fa=fd_observed(source.fileno(),before['canonical_path'],config)
 after=observed(before['canonical_path'],config)
 assert live(before)==live(fb)==live(fa)==live(after)
 assert n==b['size']and sourcehash.hexdigest()==sha(dest)==b['sha256'],'complete materialized source/local SHA mismatch'
 return dict(native_filesystem=native,status='PASS_COMPLETE_MATERIALIZATION_SHA',context=context_key(c,b),bytes=n,source_sha256=sourcehash.hexdigest(),closed_local_sha256=sha(dest),source_KEEP=True,science_changed=False)
def qualify_target_windows(base_path,object_sha,config,dest,window=MAX_WINDOW,max_bytes=MAX_WINDOW):
 raw=Path(base_path).read_bytes();obj=json.loads(raw)[object_sha]
 history=historical(object_sha,obj);obs=observed(obj['storage']['path'],config)
 b=dict(schema='SM70_TARGET_BINDING_V2',base_all_objects_sha256=digest(raw),sha256=object_sha,size=obj['size'],storage_kind=obj['storage']['kind'],stable_metadata=stable(obs),historical=history,current_full_SHA_reference=None,current_full_SHA_scope='PREBINDING_ONLY',science_context_unchanged=True,inode_diagnostics=dict(inode=obs['inode']))
 b['binding_id']=binding_id(b)
 c=dict(catalog_id='PREBINDING_NOT_PUBLIC_CATALOG',overlay_id='PREBINDING_NOT_COMPLETE_OVERLAY',base_all_objects_sha256=digest(raw),overlay=dict(bindings={object_sha:b}))
 dest=Path(dest)
 receipt=window_restore(c,b,config,dest,dest.parent/(dest.name+'.private_provisional_ledger'),window,max_bytes)
 receipt=dict(receipt,prebinding_only=True,final_catalog_ledger_eligible=False)
 put(dest/'PREBINDING_RECEIPT.json',receipt)
 return receipt
def safe_member(root,name):
 q=Path(name);assert name and not q.is_absolute()and '..'not in q.parts and chr(92)not in name
 return Path(root)/q
def select_asset(c,ident):
 rows=[a for a in c['assets']if a['bundle_id']==ident or a['bundle_id'].startswith(ident)]
 assert ident and len(rows)==1,'unknown/ambiguous asset'
 return rows[0]
def verify_asset(c,asset,full=False):
 rows=[]
 for member in asset['members']:
  binding=c['overlay']['bindings'][member['sha256']];assert binding['size']==member['size']
  rows.append(dict(relative_path=member['relative_path'],result=verify_binding(binding,c['overlay']['config'],full,c['base_all_objects_sha256'])))
 return dict(bundle_id=asset['bundle_id'],catalog_id=c['catalog_id'],overlay_id=c['overlay_id'],status='PASS_CURRENT_TARGET_FULL_SHA'if full else'PASS_METADATA_ACCESS_WITH_BOUND_HISTORICAL_SHA_NOT_FRESH_BODY',members=rows,full_sha_recomputed=full,scientific_qualification_granted=False)
def materialize_asset(c,asset,dest,max_bytes):
 dest=Path(dest);total=sum(m['size']for m in asset['members'])
 assert dest.resolve().is_relative_to(NS)and not dest.exists()and total<=max_bytes
 assert shutil.disk_usage(dest.parent).free>=total+headroom()
 dest.mkdir();rows=[]
 for member in asset['members']:
  out=safe_member(dest,member['relative_path']);out.parent.mkdir(parents=True,exist_ok=True)
  rows.append(dict(relative_path=member['relative_path'],receipt=materialize(c,c['overlay']['bindings'][member['sha256']],c['overlay']['config'],out,max_bytes)))
 receipt=dict(schema='SM70_BOUND_COMPLETE_BUNDLE_MATERIALIZATION_V2',bundle_id=asset['bundle_id'],catalog_id=c['catalog_id'],overlay_id=c['overlay_id'],profile=PROFILE,status='PASS_COMPLETE_LOCAL_BUNDLE_SHA',logical_bytes=total,members=rows,source_KEEP=True,scientific_qualification_granted=False)
 put(dest/'CANDIDATE_MATERIALIZATION_RECEIPT.json',receipt);return receipt
