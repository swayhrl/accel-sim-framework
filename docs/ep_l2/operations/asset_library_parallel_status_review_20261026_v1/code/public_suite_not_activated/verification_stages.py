"""Data-only public V3 cross-project, whole-Native and final verification handlers.

No migration engine imports, activation, scientific execution or private project helpers.
"""
from pathlib import Path
import os,json,hashlib,time,stat,signal,subprocess,uuid,collections
MIB=2**20
PRODUCTION_OBJECTS_SHA='85b0d7a4866d58852d8541f6d46bf95ed77c4c47983904ca687334527be7cb17'
PRODUCTION_BUNDLES_SHA='7ebb0949d9f81cd47d1d0cc4abab0596318babd6eafb2fb3295e8b0325182cc6'
PRODUCTION_OBJECT_SET_SHA='a007b5b9fd7e15bc06ca8a21421dcaa6d73e8aeaaa152611d9f291ed6a3ba11f'
PRODUCTION_GRAPH_SHA='dfce715212f36408b272d21a9b6f5c6d22d97caa686ef12c8f00ce692f2c5e6f'
def need(ok,message):
 if not ok:raise RuntimeError('RESOURCE_HOLD_V3_VERIFICATION_'+message)
def canon(value):return(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def token(s):return(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def _work(spec,profile):
 ident=spec['integration_id'];need(isinstance(ident,str)and ident and ident not in ['.','..']and all(x.isalnum()or x in '-_.'for x in ident),'SAFE_INTEGRATION_ID')
 root=Path(profile['native_work_root']);need(root.is_absolute(),'ABSOLUTE_NATIVE_WORK_ROOT');path=root/'integrations'/ident
 path.mkdir(parents=True,exist_ok=True);need(not path.is_symlink()and path.resolve().is_relative_to(root.resolve()),'OWN_INTEGRATION_PATH')
 for parent in [path,*path.parents]:
  need(not parent.is_symlink(),'NO_OWN_WORK_SYMLINK_ANCESTORS')
  if parent==root:break
 return path

def _read_local(path,resources,limit=96*MIB):
 path=Path(path);before=path.lstat();need(stat.S_ISREG(before.st_mode)and before.st_size<=limit,'BOUNDED_REGULAR_METADATA')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW);parts=[]
 with os.fdopen(fd,'rb',buffering=0)as f:
  need(token(os.fstat(f.fileno()))==token(before),'METADATA_FD_IDENTITY')
  for part in iter(lambda:f.read(MIB),b''):parts.append(part);resources.account(len(part),'read')
  need(token(os.fstat(f.fileno()))==token(before),'METADATA_FD_CHANGED')
 need(token(path.lstat())==token(before),'METADATA_PATH_CHANGED');raw=b''.join(parts);need(len(raw)==before.st_size,'METADATA_BYTE_COUNT');return raw

def _write_local(path,value,resources):
 path=Path(path);raw=canon(value);path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():need(_read_local(path,resources)==raw,'DIFFERENT_CLOSED_REPORT_REQUIRES_REVIEW');return dict(path=str(path),sha256=digest(raw),bytes=len(raw))
 q=resources.check(True);need(q['own_allocated_bytes']+((len(raw)+4095)//4096)*4096+4096<=256*MIB,'CONTROL_WRITE_TOTAL256MIB')
 temp=path.with_name('.'+path.name+'.owned-'+uuid.uuid4().hex)
 with temp.open('xb',buffering=0)as f:
  for off in range(0,len(raw),MIB):part=raw[off:off+MIB];need(f.write(part)==len(part),'CONTROL_SHORT_WRITE');resources.account(len(part),'write')
  os.fsync(f.fileno())
 try:os.link(temp,path)
 except FileExistsError:need(_read_local(path,resources)==raw,'REPORT_PUBLICATION_RACE')
 temp.unlink();fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
 need(_read_local(path,resources)==raw,'REPORT_CLOSED_BYTES');resources.check(True);return dict(path=str(path),sha256=digest(raw),bytes=len(raw))

def _scope(r,c,envelope,spec,profile):
 production=profile['execution_scope']=='PRODUCTION';need(profile['execution_scope']in ['PRODUCTION','QUALIFICATION'],'EXECUTION_SCOPE')
 if production:
  need('test_dimensions'not in spec,'NO_TEST_DIMENSIONS_IN_PRODUCTION');assets,objects,members,total=125,22769,25149,972603859656
  need(c['base_all_objects_sha256']==PRODUCTION_OBJECTS_SHA and c['base_all_bundles_sha256']==PRODUCTION_BUNDLES_SHA,'FROZEN_BASE_RAW_SHA')
 else:
  dims=spec['test_dimensions'];assets=dims['expected_assets'];objects=dims['expected_objects'];members=dims.get('expected_declared_members',spec['expected_declared_members']);total=dims.get('expected_unique_bytes',spec['expected_unique_bytes'])
 need(spec['expected_assets']==assets and spec['expected_objects']==objects and spec['expected_declared_members']==members and spec['expected_unique_bytes']==total,'DECLARED_DIMENSIONS')
 need(envelope['code_version_id']==spec['code_version_id'],'CODE_VERSION')
 bindings=c['overlay']['bindings'];need(len(c['assets'])==assets and len(bindings)==objects,'FULL_ASSET_OBJECT_COUNT');ids=set();used=set();edges=[]
 for a in c['assets']:
  bid=a['bundle_id'];need(bid not in ids,'DUPLICATE_BUNDLE');ids.add(bid);rels=set()
  for m in a['members']:
   rel=m['relative_path'];path=Path(rel);need(rel and not path.is_absolute()and '..'not in path.parts and chr(92)not in rel and rel not in rels,'UNIQUE_SAFE_MEMBER');rels.add(rel)
   h=m['sha256'];b=bindings[h];need(b['sha256']==h and b['size']==m['size'],'MEMBER_OBJECT_SHA_SIZE');used.add(h);edges.append([bid,rel,h,m['size']])
 need(used==set(bindings)and len(edges)==members and sum(b['size']for b in bindings.values())==total,'ALL_OBJECT_REFERENTIAL_CLOSURE')
 graph=digest(canon(sorted(edges)));objectset=digest(('\n'.join(sorted(bindings))+'\n').encode())
 suites=dict(collections.Counter(a['suite']for a in c['assets']));kinds=dict(collections.Counter(a['kind']for a in c['assets']))
 if production:
  need(graph==PRODUCTION_GRAPH_SHA and objectset==PRODUCTION_OBJECT_SET_SHA,'EXACT_FROZEN_MEMBER_GRAPH')
  need(suites=={'Rodinia':64,'CUDA Samples':18,'PolyBench/GPU':29,'Parboil':14}and kinds=={'regular':100,'fraction':25},'FULL_SUITE_KIND_COUNTS')
  uncertain=[a for a in c['assets']if a['suite']=='Rodinia'and a['source_version_evidence']=='unconfirmed'];need(len(uncertain)==6 and all(a['version']=='unconfirmed'for a in uncertain),'RODINIA_VERSION_UNCERTAINTY_PRESERVED')
 return dict(assets=assets,objects=objects,declared_members=members,unique_bytes=total,member_graph_sha256=graph,object_id_set_sha256=objectset,by_suite=suites,by_kind=kinds)

def _load(r,spec,profile,resources):
 with r.Operation(resources=resources)as op:
  c,envelope=r.load_public_catalog(op);scope=_scope(r,c,envelope,spec,profile)
 return c,envelope,scope

def _identity(pid):
 try:row=Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split();return dict(pid=int(pid),state=row[0],pgid=int(row[2]),sid=int(row[3]),start_ticks=int(row[19]))
 except (FileNotFoundError,ProcessLookupError):return None

def _owned(owner):
 rows=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  q=_identity(int(p.name))
  if q and q['pgid']==owner['pgid']and q['sid']==owner['sid']and q['start_ticks']>=owner['start_ticks']and q['state']!='Z':rows.append(q)
 return rows

def _cleanup(child,owner):
 seen=[]
 for sig,seconds in [(signal.SIGTERM,2),(signal.SIGKILL,2)]:
  end=time.monotonic()+seconds
  while True:
   rows=_owned(owner)
   if not rows:break
   for q in rows:
    now=_identity(q['pid'])
    if now and all(now[k]==q[k]for k in ['pid','start_ticks','pgid','sid']):
     try:os.kill(q['pid'],sig);seen.append(dict(pid=q['pid'],start_ticks=q['start_ticks'],signal=int(sig)))
     except ProcessLookupError:pass
   if time.monotonic()>=end:break
   time.sleep(.1)
  if not _owned(owner):break
 unresolved=_owned(owner)
 try:child.wait(timeout=.25)
 except subprocess.TimeoutExpired:pass
 need(not unresolved,'OWN_CLI_PROCESSES_UNRESOLVED');return seen

def _run_cli(command,args,cwd,folder,resources,timeout):
 """Exact sealed command, bounded metadata output, catchable-signal safe private session."""
 folder.mkdir();outpath=folder/'stdout.json';errpath=folder/'stderr.txt';stopped=[False];old={};child=None;owner=None;launched=None;cleanup=[]
 def stop(sig,frame):stopped[0]=True
 env={k:v for k,v in os.environ.items()if k not in ['LD_PRELOAD','LD_LIBRARY_PATH','CUDA_INJECTION64_PATH','TRACES_FOLDER','PYTHONHOME','PYTHONPATH','VIRTUAL_ENV','CONDA_PREFIX']and not k.startswith(('EP_L2','DTC_'))};env['PYTHONDONTWRITEBYTECODE']='1'
 try:
  for sig in [signal.SIGTERM,signal.SIGINT]:old[sig]=signal.signal(sig,stop)
  need(not stopped[0],'CLI_STOP_BEFORE_SPAWN');resources.check(True)
  with outpath.open('xb')as out,errpath.open('xb')as err:
   child=subprocess.Popen([str(command),*args],cwd=str(cwd),env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True)
   owner=_identity(child.pid);launched=owner;need(owner and owner['pid']==owner['pgid']==owner['sid'],'PRIVATE_CLI_SESSION')
   _write_local(folder/'PROCESS_START.json',dict(command=[str(command),*args],cwd=str(cwd),identity=owner),resources);deadline=time.monotonic()+timeout
   while True:
    need(not stopped[0],'CLI_STOP_REQUESTED');need(time.monotonic()<deadline,'CLI_FINITE_DEADLINE');resources.check(False)
    need(outpath.stat().st_size<=64*MIB and errpath.stat().st_size<=MIB,'CLI_OUTPUT_BOUNDS')
    event=os.waitid(os.P_PID,child.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT)
    if event is not None:rc=event.si_status if event.si_code==os.CLD_EXITED else-event.si_status;break
    time.sleep(.25)
   cleanup=_cleanup(child,owner);owner=None;out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
  need(not stopped[0],'CLI_STOP_BEFORE_RESULT')
 finally:
  if child is not None and owner is not None:cleanup=_cleanup(child,owner)
  for sig,handler in old.items():signal.signal(sig,handler)
 raw=_read_local(outpath,resources,64*MIB);errors=_read_local(errpath,resources,MIB)
 try:value=json.loads(raw)if rc==0 else None
 except ValueError as e:raise RuntimeError('RESOURCE_HOLD_V3_VERIFICATION_CLI_BAD_JSON')from e
 return dict(argv=[str(command),*args],cwd=str(cwd),returncode=rc,value=value,stdout=raw,stderr=errors,stdout_path=outpath,stderr_path=errpath,identity=launched,cleanup=cleanup)

def _cli_evidence(record,writer,kind):
 refs={key:writer.cas(record[key],kind=kind)for key in ['stdout','stderr']}
 for key in ['stdout_path','stderr_path']:
  path=record[key];need(path.is_file()and not path.is_symlink(),'OWN_CLI_OUTPUT_REGULAR');path.unlink()
 return dict(argv=record['argv'],cwd=record['cwd'],returncode=record['returncode'],process_identity=record['identity'],stdout_ref=refs['stdout'],stderr_ref=refs['stderr'],cleanup=record['cleanup'])

def _check_cli_value(record,spec,c):
 need(record['returncode']==0,'PUBLIC_CLI_FAILED');v=record['value'];need(v['code_version_id']==spec['code_version_id'],'PUBLIC_CLI_CODE_VERSION');return v

def _verify_materialized(r,op,c,asset,dest,result,resources):
 r.validate_gate(result,r.gate_pins(c),require_full=True);receipt=result['result'];need(result['status']=='PASS_BOUND_COMPLETE_MATERIALIZATION_V3'and receipt['status']=='PASS_COMPLETE_LOCAL_BUNDLE_SHA'and receipt['source_KEEP']is True and receipt['pins']==r.gate_pins(c),'MATERIALIZATION_SCOPE')
 expected={m['relative_path']:m for m in asset['members']};actual={m['relative_path']:m for m in receipt['members']};need(len(actual)==len(receipt['members'])and set(actual)==set(expected),'WHOLE_MATERIALIZATION_MEMBER_SET')
 for rel,m in expected.items():
  proof=actual[rel]['receipt'];binding=c['overlay']['bindings'][m['sha256']]
  need(proof['status']=='PASS_COMPLETE_MATERIALIZATION_SHA'and proof['source_sha256']==proof['closed_local_sha256']==m['sha256']and proof['bytes']==m['size']and proof['context']==op.c.context_key(c,binding)and proof['source_KEEP']is True and proof['science_changed']is False,'MATERIALIZED_FULL_SHA_PROOF')
  p=Path(dest)/rel;s=p.lstat();need(stat.S_ISREG(s.st_mode)and s.st_size==m['size'],'MATERIALIZED_LOCAL_TYPE_SIZE');h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
  with os.fdopen(fd,'rb',buffering=0)as f:
   need(token(os.fstat(f.fileno()))==token(s),'MATERIALIZED_FD')
   for z in iter(lambda:f.read(MIB),b''):h.update(z);resources.account(len(z),'read')
   need(token(os.fstat(f.fileno()))==token(s),'MATERIALIZED_FD_CHANGED')
  need(token(p.lstat())==token(s)and h.hexdigest()==m['sha256'],'MATERIALIZED_PARENT_REOPEN_FULL_SHA')
 side=Path(dest).with_name(Path(dest).name+'.MATERIALIZATION_RECEIPT.json');need(json.loads(_read_local(side,resources))==receipt,'MATERIALIZATION_ADJACENT_RECEIPT')
 return dict(bundle_id=asset['bundle_id'],destination=str(dest),members=len(expected),bytes=sum(m['size']for m in expected.values()),parent_native_full_SHA_reopen=True,adjacent_receipt_sha256=digest(canon(receipt)))

def _verify_public_views(r,c,resources):
 results=[];lib=r.library_root()
 for a in c['assets']:
  view=lib/a['relative_view_path'];tree=lib/a['relative_tree_path']
  need(view.is_dir()and tree.is_dir(),'ALL_PUBLIC_VIEWS_PRESENT')
  for m in a['members']:
   expected=Path(c['overlay']['bindings'][m['sha256']]['stable_metadata']['canonical_path'])
   for root in [view,tree]:
    p=root/m['relative_path'];need(p.is_file()and p.stat().st_size==m['size']and p.resolve()==expected,'PUBLIC_VIEW_EXACT_TARGET_MEMBER')
  lists=[m for m in a['members']if m['relative_path']=='kernelslist.g'];need(len(lists)==1,'ONE_REAL_KERNELSLIST_MEMBER')
  m=lists[0];path=(tree/'kernelslist.g').resolve();before=path.lstat();h=hashlib.sha256();n=0;fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
  with os.fdopen(fd,'rb',buffering=0)as f:
   need(token(os.fstat(f.fileno()))==token(before),'COMMANDLIST_FD')
   for z in iter(lambda:f.read(MIB),b''):h.update(z);n+=len(z);resources.account(len(z),'read')
   need(token(os.fstat(f.fileno()))==token(before),'COMMANDLIST_FD_CHANGED')
  need(token(path.lstat())==token(before)and n==m['size']and h.hexdigest()==m['sha256'],'WHOLE_COMMANDLIST_SHA')
  results.append(dict(bundle_id=a['bundle_id'],sha256=h.hexdigest(),bytes=n,full_SHA_recomputed=True,public_tree_and_view_all_members_exact=True))
 return results

def cross(r,spec,profile,resources):
 need(spec['body_reads_authorized']is True,'BODY_READ_AUTHORIZATION');work=_work(spec,profile);c,envelope,scope=_load(r,spec,profile,resources);pins=r.gate_pins(c)
 cwds=spec['project_cwds'];need(len(cwds)==len(set(cwds))==3 and all(Path(x).is_absolute()and Path(x).is_dir()for x in cwds),'THREE_EXACT_PROJECT_CWDS')
 command=r.library_root()/'tools/trace-assets';need(command.is_file(),'SEALED_PUBLIC_CLI');storage=r.load_verified('storage');writer=storage.Writer(r.library_root(),resources,r.load_verified('primitive'))
 root=work/'cross_attempts';root.mkdir(exist_ok=True);attempt=root/('attempt_'+uuid.uuid4().hex);attempt.mkdir();count=[0];extras=[]
 def invoke(args,cwd):
  count[0]+=1;rec=_run_cli(command,args,cwd,attempt/('call_'+str(count[0])),resources,1800);return rec
 def success(args,cwd):
  rec=invoke(args,cwd);value=_check_cli_value(rec,spec,c);evidence=_cli_evidence(rec,writer,'receipts/v3_cli/'+spec['integration_id']);return value,evidence
 def negative(args,cwd,reason_tokens):
  rec=invoke(args,cwd);text=rec['stderr'].decode(errors='replace')+rec['stdout'].decode(errors='replace');need(rec['returncode']!=0 and 'RESOURCE_HOLD_'not in text and any(t in text for t in reason_tokens),'NEGATIVE_MUST_REFUSE_FOR_EXPECTED_REASON');ev=_cli_evidence(rec,writer,'receipts/v3_cli/'+spec['integration_id']);ev['expected_refusal']=True;extras.append(ev)
 reports=[];materialized=[];small=sorted(c['assets'],key=lambda a:(sum(m['size']for m in a['members']),a['bundle_id']))
 for index,cwd in enumerate(cwds):
  listed,lev=success(['list'],cwd);need(listed['catalog_id']==c['catalog_id']and{a['bundle_id']for a in listed['assets']}=={a['bundle_id']for a in c['assets']}and len(listed['assets'])==scope['assets'],'PUBLIC_LIST_EXACT_ASSETS')
  verified,vev=success(['verify','--all'],cwd)
  a=small[index%len(small)];size=sum(m['size']for m in a['members']);need(size<=32*MIB,'AT_LEAST_THREE_SMALL_NATIVE_MATERIALIZATIONS');dest=attempt/('materialized_'+str(index))
  dry,dev=success(['materialize',a['bundle_id'],'--destination',str(dest),'--max-bytes',str(size),'--dry-run'],cwd);need(dry['admitted']is True and dry['logical_bytes']==size,'MATERIALIZE_DRY_ADMISSION')
  whole,wev=success(['materialize',a['bundle_id'],'--destination',str(dest),'--max-bytes',str(size)],cwd)
  reports.append(dict(cwd=cwd,verify=verified,list_evidence=lev,verify_evidence=vev,materialize_evidence=wev,dry_evidence=dev));materialized.append((a,dest,whole))
 first=cwds[0]
 for suite in sorted({a['suite']for a in c['assets']}):
  value,ev=success(['list','--suite',suite],first);need({a['bundle_id']for a in value['assets']}=={a['bundle_id']for a in c['assets']if a['suite']==suite},'PUBLIC_SUITE_FILTER');extras.append(ev)
 for kind in ['regular','fraction']:
  value,ev=success(['list','--kind',kind],first);need({a['bundle_id']for a in value['assets']}=={a['bundle_id']for a in c['assets']if a['kind']==kind},'PUBLIC_KIND_FILTER');extras.append(ev)
 shown,ev=success(['show',small[0]['bundle_id']],first);need(shown['bundle_id']==small[0]['bundle_id'],'PUBLIC_SHOW_EXACT');extras.append(ev)
 aliases=[a for a in c['assets']if a.get('aliases')];need(aliases,'AT_LEAST_ONE_ORIGINAL_ALIAS')
 shown,ev=success(['show',aliases[0]['aliases'][0]],first);need(shown['bundle_id']==aliases[0]['bundle_id'],'PUBLIC_ALIAS_EXACT');extras.append(ev)
 negative(['show','NO_SUCH_FROZEN_SM70_ASSET'],first,['unknown/ambiguous asset'])
 negative(['materialize',small[0]['bundle_id'],'--destination',str(r.library_root()/'FORBIDDEN_V3_VERIFY_WRITE')],first,['cannot write public/NAS tree','verified174-new native local filesystem','Native destination outside verified data device'])
 negative(['materialize',small[0]['bundle_id'],'--destination',str(materialized[0][1])],first,['ABSENT'])
 with r.Operation(resources=resources)as op:
  current,current_envelope=r.load_public_catalog(op);need(r.gate_pins(current)==pins and current_envelope['publication_id']==envelope['publication_id'],'CATALOG_CHANGED_DURING_CROSS');_scope(r,current,current_envelope,spec,profile)
  result=r.validate_cross_reports(current,reports,cwds);commandproof=_verify_public_views(r,current,resources);wholeproof=[_verify_materialized(r,op,current,a,dest,whole,resources)for a,dest,whole in materialized]
 result.update(integration_id=spec['integration_id'],code_version_id=spec['code_version_id'],scope=scope,commandlist_full_SHA_proofs=commandproof,public_cli_extra_evidence=extras,whole_small_native_materializations=wholeproof,Source_payload_writes_or_deletions=0)
 ref=_write_local(work/'CROSS_PROJECT_V3.json',result,resources)
 return dict(status=result['status'],pins=pins,report_ref=ref,scope=scope,projects_tested=3,whole_small_materializations=wholeproof,source_KEEP=True,scientific_qualification_granted=False)

def _recover_native(r,op,c,b,dest,ledger,resources):
 if not os.path.lexists(dest):return 'ABSENT'
 need(dest.is_dir()and not dest.is_symlink(),'NATIVE_OBJECT_DIRECTORY')
 root=Path(op.c.NS);need(dest.absolute().is_relative_to(root.absolute())and dest.resolve().is_relative_to(root.resolve())and dest.stat().st_dev==root.stat().st_dev,'OWN_NATIVE_DIRECTORY_BOUNDARY')
 for parent in [dest,*dest.parents]:
  need(not parent.is_symlink(),'NO_RECOVERY_SYMLINK_ANCESTORS')
  if parent==root:break
 children=list(dest.iterdir());need(all(p.is_file()and not p.is_symlink()for p in children),'OWN_NATIVE_OBJECT_FILES_ONLY');names={p.name for p in children};receipt=dest/'RESTORE_RECEIPT.json'
 context=op.c.context_key(c,b);key=op.c.ledger_key(context)
 if not children and ledger.lookup(context)is not None:
  resources.check(True);dest.rmdir();return 'EXACT_BOUND_LEDGER_COMPLETE_EMPTY_DIR_REMOVED'
 if receipt.exists():
  need(names=={'RESTORE_RECEIPT.json'},'COMPLETE_RECEIPT_WITH_UNEXPECTED_WINDOWS')
  if ledger.lookup(context)is None:
   result=r.recover_completed_native_receipt(op,c,b,receipt,ledger.path)
   need(result['status']=='PASS_PUBLIC_NATIVE_PROOF_CAS_AND_FSYNCED_LEDGER'and result['context']==context,'RECOVERED_COMPLETE_NATIVE_RECEIPT_CAS_LEDGER')
   return 'RECOVERED_PREVIOUS_COMPLETE_RECEIPT_TO_PUBLIC_CAS_NONFRESH'
  # Existing local/plain ledger evidence is preserved, never unlinked behind its old reference.
  row=dict(schema='SM70_BOUND_RESTORE_LEDGER_V2',key=key,context=context,receipt=op.c.ref(receipt));ledger.validate(row)
  return 'EXACT_BOUND_LEDGER_ALREADY_COMPLETE_LOCAL_PROOF_KEEP'
 need(ledger.lookup(context)is None,'LEDGER_RECEIPT_MISSING')
 for p in children:
  stem=p.name[:-7]if p.name.endswith('.window')else'';need(stem.isdecimal()and int(stem)<b['size']and p.stat().st_size<=min(64*MIB,b['size']-int(stem)),'ONLY_OWN_INCOMPLETE_NUMERIC_WINDOW')
 resources.check(True)
 for p in children:
  before=p.lstat();need(stat.S_ISREG(before.st_mode)and token(p.lstat())==token(before),'OWN_WINDOW_IDENTITY_BEFORE_UNLINK');p.unlink()
 dest.rmdir();return 'INCOMPLETE_OWN_WINDOWS_REMOVED_RESTART_WHOLE_OBJECT'

def restore(r,spec,profile,resources):
 need(spec['body_reads_authorized']is True,'BODY_READ_AUTHORIZATION');work=_work(spec,profile);ledgerpath=work/'NATIVE_ALL_OBJECTS_V3.jsonl';objects_dir=work/'native_objects';objects_dir.mkdir(exist_ok=True);need(not objects_dir.is_symlink()and objects_dir.resolve().is_relative_to(work.resolve()),'OWN_NATIVE_OBJECT_ROOT');stats=collections.Counter()
 with r.Operation(resources=resources)as op:
  c,envelope=r.load_public_catalog(op);scope=_scope(r,c,envelope,spec,profile);ledger=op.ledger(ledgerpath,c)
  for h,b in sorted(c['overlay']['bindings'].items()):
   resources.check(False);need(len(h)==64 and all(x in '0123456789abcdef'for x in h),'OBJECT_SHA_PATH');dest=objects_dir/h
   action=_recover_native(r,op,c,b,dest,ledger,resources);stats[action]+=1
   result=r.restore_object(op,c,b,c['overlay']['config'],dest,ledgerpath,logical_max=None,window_max=64*MIB,resume=True)
   need(result['context']==op.c.context_key(c,b),'WHOLE_OBJECT_CONTEXT');status=result['status'];need(status in ['PASS_COMPLETE_SOURCE_AND_NATIVE_WINDOWS_SHA','RESUMED_EXACT_BOUND_PRIOR_NATIVE_RESTORE_NOT_FRESH_THIS_CALL'],'WHOLE_OBJECT_COMPLETE_STATUS');stats[status]+=1
  native=r.finish_receipt(op,c,ledgerpath);need(native['objects']==scope['objects']and native['logical_bytes']==scope['unique_bytes'],'ALL_NATIVE_OBJECT_BYTES');pins=r.gate_pins(c)
 ref=_write_local(work/'NATIVE_ALL_OBJECTS_V3.json',native,resources)
 return dict(status='PASS_EXACT_V3_ALL_OBJECT_NATIVE_RESTORE',pins=pins,report_ref=ref,scope=scope,objects=scope['objects'],logical_bytes=scope['unique_bytes'],max_live_window_bytes=64*MIB,counts=dict(stats),fresh_all_this_call=stats['PASS_COMPLETE_SOURCE_AND_NATIVE_WINDOWS_SHA']==scope['objects'],source_KEEP=True,scientific_qualification_granted=False)

def _archive_inputs(reader,spec,profile,resources):
 refs=spec['archive_audit_refs'];need(len(refs)==4,'FOUR_ARCHIVE_AUDIT_REFS')
 if profile['execution_scope']=='PRODUCTION':need(len({ref['sha256']for ref in refs})==4,'FOUR_DISTINCT_ARCHIVE_AUDIT_REFS')
 return [reader(ref,resources)[0]for ref in refs]

def _archive_identity_kwargs(reader,spec,profile,resources):
 ref=spec.get('archive_identity_expectations_ref')
 if profile['execution_scope']=='PRODUCTION' or ref is not None:
  need(ref is not None,'ROOT_ARCHIVE_IDENTITY_EXPECTATIONS_REF_REQUIRED')
  expectations,_=reader(ref,resources)
  need(isinstance(expectations,list)and len(expectations)==4,'ROOT_FOUR_ARCHIVE_IDENTITY_EXPECTATIONS')
  return dict(archive_expectations=expectations,archive_receipt_sha256s=[x['sha256']for x in spec['archive_audit_refs']])
 return {}

def finish(r,spec,profile,resources):
 work=_work(spec,profile);reader=r.load_verified('stages').ref_read
 expected_aliases,_=reader(spec['expected_aliases_ref'],resources);prior20,_=reader(spec['prior20_ref'],resources);before,_=reader(spec['protected_before_ref'],resources);after,_=reader(spec['protected_after_ref'],resources)
 if isinstance(prior20,dict):prior20=prior20['assets']
 need(isinstance(before,dict)and isinstance(after,dict)and before and after,'ROOT_ATTESTED_PROTECTED_SNAPSHOTS')
 archives=_archive_inputs(reader,spec,profile,resources);archive_kwargs=_archive_identity_kwargs(reader,spec,profile,resources)
 cross_result=json.loads(_read_local(work/'CROSS_PROJECT_V3.json',resources));native=json.loads(_read_local(work/'NATIVE_ALL_OBJECTS_V3.json',resources));need(cross_result['integration_id']==spec['integration_id']and cross_result['code_version_id']==spec['code_version_id'],'CROSS_INTEGRATION_CODE_VERSION')
 need(len(cross_result['whole_small_native_materializations'])==3 and all(x['parent_native_full_SHA_reopen']is True for x in cross_result['whole_small_native_materializations']),'THREE_ACTUAL_SMALL_FULL_MATERIALIZATION_PROOFS')
 with r.Operation(resources=resources)as op:
  c,envelope=r.load_public_catalog(op);scope=_scope(r,c,envelope,spec,profile)
  lists={a['bundle_id']:next(m for m in a['members']if m['relative_path']=='kernelslist.g')for a in c['assets']};proofs=cross_result['commandlist_full_SHA_proofs'];need(len(proofs)==len(lists)and {x['bundle_id']for x in proofs}==set(lists)and all(x['full_SHA_recomputed']is True and x['sha256']==lists[x['bundle_id']]['sha256']and x['bytes']==lists[x['bundle_id']]['size']for x in proofs),'ALL_COMMANDLIST_FULL_SHA_PROOFS')
  gates=r.validate_finish_metadata(op,c,cross_result,native,work/'NATIVE_ALL_OBJECTS_V3.jsonl',spec['project_cwds'],expected_aliases,prior20,before,after,archives,**archive_kwargs);pins=r.gate_pins(c)
 result=dict(status='PASS_EXACT_V3_FINISH_VALIDATION',pins=pins,scope=scope,integration_id=spec['integration_id'],code_version_id=spec['code_version_id'],all_original_input_aliases_covered=len(expected_aliases),all20_prior_aliases_covered=True,archive_audits=4,protected_scientific_tools_unchanged=True,protected_audit_scope='ROOT_ATTESTED_IMMUTABLE_BEFORE_AFTER_SNAPSHOTS_NOT_PRIVATE_CODE_REOPEN',cross_ref=dict(path=str(work/'CROSS_PROJECT_V3.json'),sha256=digest(canon(cross_result))),native_ref=dict(path=str(work/'NATIVE_ALL_OBJECTS_V3.json'),sha256=digest(canon(native))),native_ledger_sha256=native['ledger_sha256'],native_receipt_scope='ALL_LOGICAL_OBJECT_BYTES_CLOSED_NATIVE_WINDOWS_NOT_SIMULTANEOUS_DATASET_MATERIALIZATION',gates=gates,source_KEEP=True,Source_payload_writes_or_deletions=0,scientific_starts=0,scientific_qualification_granted=False,overall_expanded_goal_complete_claimed=False)
 ref=_write_local(work/'FINAL_V3.json',result,resources)
 return dict(status=result['status'],pins=pins,report_ref=ref,scope=scope,source_KEEP=True,scientific_qualification_granted=False,overall_expanded_goal_complete_claimed=False)
