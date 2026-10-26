"""Typed R5 public provider. All R4 implementations remain immutable siblings.
This provider is part of its new CodeID; no external shim inherits R4 acceptance.
"""
from pathlib import Path
import json,hashlib,os,sys,gzip,time,importlib.util,math,contextlib
MIB=2**20
def need(ok,msg):
 if not ok:raise RuntimeError('R5_ENTRY_HOLD_'+msg)
def module(r,name):return r.load_verified(name)
def resource_scope(r,args,kind):
 profile=r.profile()
 ref=lambda p,h:dict(path=p,sha256=h,bytes=Path(p).stat().st_size)
 return module(r,'bounded_resources_r5').Scope(profile,ref(args.resource_policy,args.policy_sha256),ref(args.root_approval,args.approval_sha256),r.code_manifest()['code_version_id'],kind)
def readonly_operation(r,scope,operation,asset=None,suite=None,kind='all',full=False,all_assets=False):
 requested='verify_full'if operation=='verify'and full else'verify_metadata'if operation=='verify'else operation
 need(requested in scope.policy['allowed_operations']and operation in ['list','show','verify'],'EXACT_READONLY_OPERATION')
 scope.check(True)
 # Enter with no resource writer so R4 does not create its Native lock.
 # All subsequent metadata/full-body accounting and operation-close digest checks remain.
 with r.Operation(resources=None)as op:
  op.resources=scope
  c,envelope=r.load_public_catalog(op)
  need(r.gate_pins(c)==scope.policy['catalog_pins'],'READONLY_CATALOG_EPOCH')
  result=r.public_operation(op,c,operation,asset,suite,kind,full,None,0,False,all_assets)
  if isinstance(result,dict):
   result.update(code_version_id=r.code_manifest()['code_version_id'],resource_provider='EXPLICIT_READ_ONLY_ZERO_NATIVE_R5',native_payload_writes=0,policy_sha256=scope.policy_ref['sha256'])
 return result

class SlotAccounting:
 """Private adapter for the typed readback routine, never selected by materialize CLI."""
 def __init__(self,scope):self.scope=scope
 @property
 def deadline(self):return self.scope.deadline
 def account(self,n,direction):return self.scope.account(n,direction)
 def check(self,force=False):
  if force:self.scope.observe(True)
  return self.scope.check_block(16*MIB)

def restore_one(r,op,scope,catalog,binding,config,ledger_path,resume=False):
 need(scope.kind=='EXACT_SINGLE_SLOT_READBACK','EXACT_SLOT_SCOPE')
 ctx=op.c.context_key(catalog,binding);scope.binding(binding,ctx)
 need(Path(ledger_path).resolve().is_relative_to(r.library_root().resolve()),'NAS_LEDGER_ONLY')
 ledger=op.ledger(ledger_path,catalog);old=ledger.lookup(ctx)
 if old:
  need(resume,'EXPLICIT_EXACT_RESUME')
  return dict(status='RESUMED_EXACT_BOUND_PRIOR_NATIVE_RESTORE_NOT_FRESH_THIS_CALL',context=ctx,receipt=old['receipt'],fresh_full_SHA_this_call=False)
 op.c.fast(binding,config,catalog['base_all_objects_sha256'])
 before=op.c.observed(ctx['canonical_path'],config);fd=os.open(ctx['canonical_path'],os.O_RDONLY|os.O_NOFOLLOW)
 source_sha=hashlib.sha256();native_sha=None;offset=0;windows=[]
 # The combined source/native digest is computed from actual closed Native reopen
 # bytes. Slot.finish returns it via the incremental readback callback below.
 native_sha=hashlib.sha256()
 with os.fdopen(fd,'rb',buffering=0)as source:
  fb=op.c.fd_observed(source.fileno(),ctx['canonical_path'],config);need(op.c.live(before)==op.c.live(fb),'SOURCE_OPEN_FD')
  while offset<binding['size']:
   target=min(64*MIB,binding['size']-offset);wh=hashlib.sha256();slot=scope.slot(binding,ctx,offset,target)
   try:
    left=target
    while left:
     part=source.read(min(MIB,left));need(bool(part)and len(part)<=left,'SOURCE_EOF_OR_OVERSIZE')
     source_sha.update(part);wh.update(part);scope.account(len(part),'read');slot.write(part);left-=len(part)
    proof=slot.finish(wh.hexdigest(),readback_consume=native_sha.update)
    windows.append(dict(offset=offset,bytes=target,source_sha256=wh.hexdigest(),closed_sha256=proof['closed_sha256'],native_closed_identity=proof['native_closed_identity'],Native_write_and_closed_reopen_FD_path_stable=True,R5_closed_window_ref=slot.proof_ref))
    slot.cleanup();offset+=target
   except BaseException as e:slot.preserve(e);raise
  need(source.read(1)==b'','SOURCE_TRAILING_BYTES');fa=op.c.fd_observed(source.fileno(),ctx['canonical_path'],config)
 after=op.c.observed(ctx['canonical_path'],config)
 need(op.c.live(before)==op.c.live(fb)==op.c.live(fa)==op.c.live(after),'SOURCE_FD_PATH_CHANGE')
 need(offset==binding['size']and source_sha.hexdigest()==native_sha.hexdigest()==binding['sha256'],'WHOLE_SOURCE_NATIVE_SHA')
 proof=dict(schema='CURRENT_TARGET_FULL_SHA_V2',status='CURRENT_TARGET_FULL_SHA_VERIFIED',path_before=before,fd_before=fb,fd_after=fa,path_after=after,expected_sha256=binding['sha256'],actual_sha256=source_sha.hexdigest(),bytes_read=offset,EOF_checked=True,science_changed=False)
 native=dict(native_root=str(scope.work),native_device=scope.work.stat().st_dev,hostname=os.uname().nodename,qualification_only=scope.testing)
 result=dict(native_filesystem=native,current_target_proof=proof,status='PASS_COMPLETE_SOURCE_AND_NATIVE_WINDOWS_SHA',context=ctx,source_bytes=offset,source_sha256=source_sha.hexdigest(),native_sha256=native_sha.hexdigest(),windows=windows,window_limit=64*MIB,EOF_checked=True,path_before=before,fd_before=fb,fd_after=fa,path_after=after,source_KEEP=True,fresh_full_SHA_this_call=True,science_changed=False,R5_resource_policy_sha256=scope.policy_ref['sha256'],qualification_only=scope.testing)
 logical=r.canon(result);need(len(logical)<=64*MIB,'PROOF_LOGICAL64MIB')
 packed=gzip.compress(logical,compresslevel=6,mtime=0)
 writer=module(r,'storage').Writer(r.library_root(),SlotAccounting(scope),module(r,'primitive'))
 integration=scope.policy['integration_id'];need(Path(ledger_path).parent.name==integration,'NAS_LEDGER_INTEGRATION')
 public=writer.cas(packed,'receipts/v3_native/'+integration)
 ref=dict(path=public['path'],sha256=public['sha256'],encoding='gzip',uncompressed_sha256=r.digest(logical),uncompressed_bytes=len(logical))
 need(op.checked_ref(ref)==result,'CLOSED_PUBLIC_CAS_DUAL_SHA')
 row=dict(schema='SM70_BOUND_RESTORE_LEDGER_V2',key=op.c.ledger_key(ctx),context=ctx,receipt=ref,code_version_id=r.code_manifest()['code_version_id'],integration_id=integration)
 ledger.append(row)
 return result

def post_commit_source2_guard(r,spec):
 """Current V13R2 exact metadata/restore-engine contract; no source body reads."""
 need('R5_source2_contract_ref'in spec,'SOURCE2_CURRENT_CONTRACT_REQUIRED')
 contract,_=module(r,'stages').ref_read(spec['R5_source2_contract_ref'])
 need(contract['schema']=='SM70_R5_SOURCE2_POST_COMMIT_CONTRACT_V1','SOURCE2_CONTRACT_SCHEMA')
 need(contract['source_manifest_raw_ref']['sha256']=='4f2e611e7b1a2e599005fc2160122eaf0f975c66a45757b0a1f7730713d630ba','SOURCE2_RAW_LINEAGE')
 need(contract['source_manifest_canonical_sha256']=='dacb7de64981e5a483a88e5a35b71f3c7e4273703d2bd2f862517eb243e045d5','SOURCE2_CANONICAL_LINEAGE')
 need(contract['restore_engine_sha256']=='dee749ef1f9b35779347d5d310b9d5f6b9b102b18b26737ce3aaad96d20a6b01','SOURCE2_ENGINE_LINEAGE')
 bundle=Path(contract['bundle']);need(str(bundle)=='/root/share/mnt164/huangrulin/traces/bundles/_payload/2dcf6422136b02adcc6d','SOURCE2_EXACT_BUNDLE')
 need((bundle/'COMMIT.json').is_file(),'SOURCE2_ACTUAL_COMMIT_REQUIRED')
 frozen,_=module(r,'stages').ref_read(contract['source_manifest_raw_ref'])
 canonical=r.canon(frozen);need(r.digest(canonical)==contract['source_manifest_canonical_sha256'],'SOURCE2_CANONICAL_BYTES')
 stored=r.bounded_metadata_raw(bundle/'SOURCE_MANIFEST.json')
 commit=json.loads(r.bounded_metadata_raw(bundle/'COMMIT.json'))
 need(stored==canonical and commit['manifest_sha256']==r.digest(stored)and commit['object_id']==frozen['object_id'],'SOURCE2_COMMIT_MANIFEST')
 need(r.digest(r.bounded_metadata_raw(bundle/'trace_copy.py',8*MIB))==contract['restore_engine_sha256'],'SOURCE2_CURRENT_RESTORE_ENGINE')
 return dict(source_manifest_raw_sha256=contract['source_manifest_raw_ref']['sha256'],source_manifest_canonical_sha256=commit['manifest_sha256'],restore_engine_sha256=contract['restore_engine_sha256'],COMMIT_sha256=r.digest(r.bounded_metadata_raw(bundle/'COMMIT.json')))

def _bounded_restore_stage_impl(r,scope,spec):
 """Future exact stage only: original archive and frozen graph guards remain hard."""
 stages=module(r,'stages');profile=r.profile()
 need(spec['code_version_id']==r.code_manifest()['code_version_id']and spec['integration_id']==scope.policy['integration_id'],'STAGE_CODE_INTEGRATION')
 need(spec['body_reads_authorized']is True and spec['suite_complete']is True and spec['scientific_starts_authorized']is False,'STAGE_DATA_ONLY')
 if profile['execution_scope']=='PRODUCTION':post_commit_source2_guard(r,spec)
 stages.closed_archives(r,spec,SlotAccounting(scope))
 objects,_=stages.ref_read(spec['base_all_objects_ref'],SlotAccounting(scope))
 bundles,_=stages.ref_read(spec['base_all_bundles_ref'],SlotAccounting(scope))
 stages.exact_frozen_scope(spec,objects,bundles,SlotAccounting(scope))
 ledger_path=r.library_root()/'receipts/v3_ledgers'/spec['integration_id']/'NATIVE_ALL_OBJECTS_V3.jsonl'
 counts={};results=[]
 with scope.operation():
  with r.Operation(resources=None)as op:
   op.resources=SlotAccounting(scope)
   c,envelope=r.load_public_catalog(op);need(r.gate_pins(c)==scope.policy['catalog_pins'],'RESTORE_CATALOG_EPOCH')
   need(set(scope.bindings)==set(c['overlay']['bindings']),'RESTORE_EXACT_BINDING_DENOMINATOR')
   for h,b in sorted(c['overlay']['bindings'].items()):
    result=restore_one(r,op,scope,c,b,c['overlay']['config'],ledger_path,resume=True);counts[result['status']]=counts.get(result['status'],0)+1
   final=r.finish_receipt(op,c,ledger_path)
 return dict(schema='SM70_TYPED_BOUNDED_RESTORE_STAGE_R5',status='PASS_EXACT_R5_BOUNDED_ALL_OBJECTS',result=final,counts=counts,ledger_path=str(ledger_path),source_KEEP=True,scientific_qualification_granted=False,production_goal_complete_claimed=False)

def exact_write_stage_admission(r,scope,spec):
 stages=module(r,'stages');profile=r.profile()
 need(spec['code_version_id']==r.code_manifest()['code_version_id']and spec['integration_id']==scope.policy['integration_id'],'STAGE_CODE_INTEGRATION')
 need(spec['body_reads_authorized']is True and spec['suite_complete']is True and spec['scientific_starts_authorized']is False,'STAGE_DATA_ONLY')
 if profile['execution_scope']=='PRODUCTION':post_commit_source2_guard(r,spec)
 stages.closed_archives(r,spec,SlotAccounting(scope))
 objects,_=stages.ref_read(spec['base_all_objects_ref'],SlotAccounting(scope));bundles,_=stages.ref_read(spec['base_all_bundles_ref'],SlotAccounting(scope))
 stages.exact_frozen_scope(spec,objects,bundles,SlotAccounting(scope))
 return profile

def _small_materialize_impl(r,scope,spec,asset_id,destination,cwd=None,dry=False,max_bytes=32*MIB):
 """Root exact-bound whole bundle <=32MiB; generic materialize is untouched."""
 need(scope.kind=='EXACT_SMALL_BUNDLE32','SMALL_SCOPE')
 profile=exact_write_stage_admission(r,scope,spec)
 rows=scope.policy['small_materializations'];dest=Path(destination);cwd=Path.cwd()if cwd is None else Path(cwd)
 matches=[x for x in rows if x['bundle_id']==asset_id and x['destination']==str(dest)and Path(x['cwd']).resolve()==cwd.resolve()]
 need(len(matches)==1,'SMALL_EXACT_BUNDLE_DEST_CWD')
 approved=matches[0];bm=module(r,'bounded_resources_r5');bm.no_links(dest)
 need(not os.path.lexists(dest)and not os.path.lexists(dest.with_name(dest.name+'.MATERIALIZATION_RECEIPT.json')),'SMALL_ABSENT_DEST_AND_RECEIPT')
 if not scope.testing:
  parent=dest.parent
  while not parent.exists():parent=parent.parent
  need(dest.is_relative_to(Path('/root/data'))and parent.stat().st_dev==profile['native_device'],'SMALL_NATIVE_DEVICE_PATH')
  fs=json.loads(__import__('subprocess').check_output(['/usr/bin/findmnt','-J','-T',str(parent)],text=True))['filesystems'][0]
  need(fs['fstype']=='ext4','SMALL_NATIVE_EXT4')
 with r.Operation(resources=None)as op:
  op.resources=SlotAccounting(scope);c,envelope=r.load_public_catalog(op)
  need(r.gate_pins(c)==scope.policy['catalog_pins'],'SMALL_CATALOG_EPOCH')
  assets=[a for a in c['assets']if a['bundle_id']==asset_id];need(len(assets)==1,'SMALL_EXACT_ASSET')
  asset=assets[0];need(r.digest(r.canon(asset))==approved['asset_sha256'],'SMALL_ASSET_BYTES')
  if 'verified_asset_gate_ref'in approved:
   gate=bm.load_ref(approved['verified_asset_gate_ref']);r.validate_gate(gate,r.gate_pins(c),require_full=True)
   need(any(a['bundle_id']==asset_id for a in gate['assets']),'SMALL_BUNDLE_VERIFIED_GATE')
  else:
   prior=approved['verified_native_ledger'];need(prior['schema']=='R5_EXACT_PRIOR_NATIVE_LEDGER_ASSET_ADMISSION'and prior['pins']==r.gate_pins(c),'SMALL_PRIOR_LEDGER_SCOPE')
   need(Path(prior['path'])==r.library_root()/'receipts/v3_ledgers'/scope.policy['integration_id']/'NATIVE_ALL_OBJECTS_V3.jsonl','SMALL_EXACT_LEDGER_PATH')
   r.finish_receipt(op,c,prior['path']) # complete immutable proof+context validation, no new/fresh body claim

  total=sum(m['size']for m in asset['members']);need(type(max_bytes)is int and 0<total<=min(32*MIB,max_bytes),'SMALL_TOTAL32MIB_OR_EXPLICIT_CAP')
  for member in asset['members']:
   b=c['overlay']['bindings'][member['sha256']];ctx=op.c.context_key(c,b)
   need(scope.bindings.get(ctx['sha256'])==dict(binding_id=b['binding_id'],size=b['size'],context=ctx),'SMALL_EXACT_MEMBER_BINDING')
   op.c.fast(b,c['overlay']['config'],c['base_all_objects_sha256'])
  scope.check_block(total+16*MIB)
  if dry:return dict(status='ADMITTED_ROOT_EXACT_SMALL_MATERIALIZATION_R5',logical_bytes=total,destination=str(dest),Native_written=False,qualification_only=scope.testing)
  results=[];created=[]
  with scope.operation():
   dest.parent.mkdir(parents=True,exist_ok=True);dest.mkdir(mode=0o700)
   try:
    # Reserve all payload extents before copying any source bytes.
    for member in asset['members']:
     path=op.c.safe_member(dest,member['relative_path']);bm.no_links(path);path.parent.mkdir(parents=True,exist_ok=True)
     fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_RDWR|os.O_NOFOLLOW,0o600)
     with os.fdopen(fd,'r+b',buffering=0)as out:
      if scope.testing:os.ftruncate(out.fileno(),member['size'])
      elif member['size']:os.posix_fallocate(out.fileno(),0,member['size'])
      need(os.fstat(out.fileno()).st_size==member['size']and(scope.testing or os.fstat(out.fileno()).st_blocks*512>=member['size']),'SMALL_PREALLOCATION')
      os.fsync(out.fileno());created.append(dict(path=str(path),identity=list(r.token(os.fstat(out.fileno())))))
    bm.immutable_json(scope.evidence/('SMALL_CREATED_'+r.digest(str(dest).encode())+'.json'),dict(destination=str(dest),created=created,logical_bytes=total,qualification_only=scope.testing,source_KEEP=True))
    for member,original in zip(asset['members'],created):
     path=Path(original['path']);b=c['overlay']['bindings'][member['sha256']];config=c['overlay']['config'];ctx=op.c.context_key(c,b)
     before=op.c.observed(ctx['canonical_path'],config);fd=os.open(ctx['canonical_path'],os.O_RDONLY|os.O_NOFOLLOW);localfd=os.open(path,os.O_RDWR|os.O_NOFOLLOW)
     h=hashlib.sha256();count=0
     with os.fdopen(fd,'rb',buffering=0)as source,os.fdopen(localfd,'r+b',buffering=0)as out:
      need(list(r.token(os.fstat(out.fileno())))==original['identity'],'SMALL_CREATED_FILE_IDENTITY')
      fb=op.c.fd_observed(source.fileno(),ctx['canonical_path'],config)
      while True:
       scope.check_block(16*MIB);part=source.read(MIB)
       if not part:break
       need(count+len(part)<=member['size'],'SMALL_SOURCE_GROWTH');scope.account(len(part),'read');h.update(part)
       need(out.write(part)==len(part),'SMALL_SHORT_WRITE');count+=len(part);scope.account(len(part),'write')
      os.fsync(out.fileno());closed=r.token(os.fstat(out.fileno()));fa=op.c.fd_observed(source.fileno(),ctx['canonical_path'],config)
     bm.no_links(path);need(r.token(path.lstat())==closed and path.lstat().st_nlink==1,'SMALL_CLOSED_PATH')
     rh=hashlib.sha256();rn=0;fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
     with os.fdopen(fd,'rb',buffering=0)as inp:
      need(r.token(os.fstat(inp.fileno()))==closed,'SMALL_REOPEN_IDENTITY')
      while True:
       scope.check_block(16*MIB);part=inp.read(MIB)
       if not part:break
       rh.update(part);rn+=len(part);scope.account(len(part),'read')
      need(r.token(os.fstat(inp.fileno()))==closed,'SMALL_REOPEN_FD')
     after=op.c.observed(ctx['canonical_path'],config)
     need(r.token(path.lstat())==closed and op.c.live(before)==op.c.live(fb)==op.c.live(fa)==op.c.live(after),'SMALL_SOURCE_OR_LOCAL_CHANGED')
     need(count==rn==member['size']and h.hexdigest()==rh.hexdigest()==member['sha256'],'SMALL_COMPLETE_SOURCE_LOCAL_SHA')
     receipt=dict(status='PASS_COMPLETE_MATERIALIZATION_SHA',context=ctx,native_filesystem=dict(native_root=str(scope.work),native_device=path.stat().st_dev,hostname=os.uname().nodename,qualification_only=scope.testing),source_sha256=h.hexdigest(),closed_local_sha256=rh.hexdigest(),bytes=count,source_KEEP=True,science_changed=False)
     results.append(dict(relative_path=member['relative_path'],receipt=receipt))
    receipt=dict(schema='SM70_BOUND_COMPLETE_BUNDLE_MATERIALIZATION_V3',bundle_id=asset['bundle_id'],pins=r.gate_pins(c),profile=r.PROFILE,status='PASS_COMPLETE_LOCAL_BUNDLE_SHA',logical_bytes=total,members=results,source_KEEP=True,scientific_qualification_granted=False,R5_resource_policy_sha256=scope.policy_ref['sha256'],qualification_only=scope.testing)
    proof=bm.immutable_json(scope.evidence/('SMALL_COMPLETE_'+r.digest(str(dest).encode())+'.json'),receipt)
    encoded=r.canon(receipt);need(len(encoded)<=MIB,'SMALL_NATIVE_RECEIPT1MIB')
    scope.check_block(len(encoded)+16*MIB);adjacent=dest.with_name(dest.name+'.MATERIALIZATION_RECEIPT.json')
    bm.immutable_json(adjacent,receipt);scope.account(len(encoded),'write');scope.check_block(16*MIB)
    return dict(schema='SM70_BOUND_PUBLIC_OPERATION_V3',status='PASS_BOUND_COMPLETE_MATERIALIZATION_V3',pins=r.gate_pins(c),fresh_all_SHA_this_call=True,result=receipt,NAS_proof_ref=proof,scientific_qualification_granted=False)
   except BaseException as error:
    bm.immutable_json(scope.evidence/('SMALL_FAILED_'+str(time.time_ns())+'.json'),dict(destination=str(dest),created=created,error=repr(error),source_KEEP=True,owned_partial_preserved=True),deadline_enforced=False)
    raise

@contextlib.contextmanager
def exact_operation_deadline(scope,spec,stage):
 # Direct typed APIs have the same Root-spec cap even without a phase parent.
 seconds=spec['stage_deadlines_seconds'][stage]
 need(type(seconds)is int and 0<seconds<=7*86400,'FINITE_EXACT_OPERATION_BUDGET')
 key='SM70_R5_STAGE_DEADLINE_MONOTONIC';prior=os.environ.get(key)
 parent=float('inf')if prior is None else float(prior)
 need(prior is None or(math.isfinite(parent)and parent>0),'INVALID_PARENT_DEADLINE')
 cutoff=min(scope.deadline,parent,time.monotonic()+seconds);scope.deadline=cutoff
 os.environ[key]=repr(cutoff)
 try:
  scope.check_deadline();yield;scope.check_deadline()
 finally:
  if prior is None:os.environ.pop(key,None)
  else:os.environ[key]=prior
def bounded_restore_stage(r,scope,spec):
 with exact_operation_deadline(scope,spec,'restore'):
  return _bounded_restore_stage_impl(r,scope,spec)
def small_materialize(r,scope,spec,asset_id,destination,cwd=None,dry=False,max_bytes=32*MIB):
 with exact_operation_deadline(scope,spec,'cross'):
  return _small_materialize_impl(r,scope,spec,asset_id,destination,cwd,dry,max_bytes)

def selected_readonly_defaults(r,args):
 """Root-owned selector makes the public readonly CLI usable without policy flags."""
 path=Path(r.profile()['native_work_root'])/'authority/PUBLIC_READONLY_R5.json';bm=module(r,'bounded_resources_r5')
 bm.no_links(path);st=path.lstat()
 if r.profile()['execution_scope']=='PRODUCTION':need(st.st_uid==0 and st.st_mode&0o022==0,'READONLY_SELECTOR_PERMISSIONS')
 doc=json.loads(bm.raw(path,4*MIB))
 need(doc['schema']=='SM70_R5_PUBLIC_READONLY_DEFAULT_V1'and doc['status']=='ROOT_SELECTED_EXACT_READONLY_POLICY'and doc['code_version_id']==r.code_manifest()['code_version_id'],'READONLY_SELECTOR_CODE_SCOPE')
 need(doc['kind']=='READ_ONLY_ZERO_NATIVE','READONLY_SELECTOR_KIND')
 args.resource_policy=doc['policy_ref']['path'];args.policy_sha256=doc['policy_ref']['sha256']
 args.root_approval=doc['approval_ref']['path'];args.approval_sha256=doc['approval_ref']['sha256']
 return doc

def public_main(r,argv=None):
 import argparse
 parser=argparse.ArgumentParser(description='Shared trace assets: typed read-only / bounded restore R5')
 parser.add_argument('operation',choices=['list','show','verify','materialize','materialize-small','restore']);parser.add_argument('asset',nargs='?')
 parser.add_argument('--suite');parser.add_argument('--kind',choices=['regular','fraction','all'],default='all')
 parser.add_argument('--all',action='store_true');parser.add_argument('--full',action='store_true')
 parser.add_argument('--destination');parser.add_argument('--max-bytes',type=int,default=256*MIB);parser.add_argument('--dry-run',action='store_true')
 parser.add_argument('--resource-policy');parser.add_argument('--policy-sha256');parser.add_argument('--root-approval');parser.add_argument('--approval-sha256')
 parser.add_argument('--integration-spec');parser.add_argument('--spec-sha256');args=parser.parse_args(argv)
 r.verify_package()
 if args.operation=='materialize':
  # Old broad resource gate, all foreign ceilings and explicit full allocation budget.
  need(not any([args.resource_policy,args.policy_sha256,args.root_approval,args.approval_sha256,args.integration_spec,args.spec_sha256]),'R5_POLICY_CANNOT_AUTHORIZE_MATERIALIZE')
  call=['materialize',args.asset or'']
  if args.destination:call+=['--destination',args.destination]
  call+=['--max-bytes',str(args.max_bytes)]
  if args.suite:call+=['--suite',args.suite]
  call+=['--kind',args.kind]
  if args.all:call+=['--all']
  if args.full:call+=['--full']
  if args.dry_run:call+=['--dry-run']
  return r.public_main(call)
 if args.operation in['list','show','verify']and not any([args.resource_policy,args.policy_sha256,args.root_approval,args.approval_sha256]):selected_readonly_defaults(r,args)
 need(all([args.resource_policy,args.policy_sha256,args.root_approval,args.approval_sha256]),'EXACT_ROOT_POLICY_REQUIRED')
 if args.operation=='materialize-small':
  need(args.integration_spec and args.spec_sha256 and args.asset and args.destination and not args.full and not args.all,'SMALL_EXACT_ARGUMENTS')
  rr,spec,profile=module(r,'stages').spec_load(args.integration_spec,args.spec_sha256)
  scope=resource_scope(r,args,'EXACT_SMALL_BUNDLE32');result=small_materialize(r,scope,spec,args.asset,args.destination,dry=args.dry_run,max_bytes=args.max_bytes)
 elif args.operation=='restore':
  need(args.integration_spec and args.spec_sha256 and not args.asset,'EXACT_RESTORE_SPEC_REQUIRED')
  # Reuse unchanged Root activation/spec loader. No private standalone driver bypass.
  rr,spec,profile=module(r,'stages').spec_load(args.integration_spec,args.spec_sha256)
  scope=resource_scope(r,args,'EXACT_SINGLE_SLOT_READBACK');result=bounded_restore_stage(r,scope,spec)
 else:
  need(not any([args.destination,args.dry_run,args.integration_spec,args.spec_sha256]),'READONLY_ARGUMENT_SCOPE')
  scope=resource_scope(r,args,'READ_ONLY_ZERO_NATIVE');result=readonly_operation(r,scope,args.operation,args.asset,args.suite,args.kind,args.full,args.all)
 scope.check_deadline();encoded=json.dumps(result,indent=2);scope.check_deadline();print(encoded);scope.check_deadline();return result
