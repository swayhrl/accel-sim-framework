#!/usr/bin/env python3
"""Root-reviewed engineering candidate; default plan only. Never launches any process.
Only a currently accepted paid exact new r5 DWT/Vector/Conv snapshot may be shared.
All history, raw, original failed ELF and per-path logical generation stay intact.
"""
from pathlib import Path
import argparse,fcntl,hashlib,json,os,stat,sys,time
E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
SHARED=Path('/workspace/ep_l2_ft20261016_shared')
HOME=SHARED/'mechanism_study_20261019_v1'
PACK=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_r5_joint_r1'
RESULTS=Path('/workspace/ep_l2_ms20261019_e_results')
CANONICAL=Path('/workspace/build/ep-l2-ms20261022-e2-tagpressure-observer-r5/accel-sim.out')
ALLOWED_TARGETS={'V8_TAGPRESSURE_dwt2d_F','V8_TAGPRESSURE_vectorAdd_4M_F','V8_TAGPRESSURE_convolutionSeparable_F'}
UNCHANGED=('path','device','size','mode','uid','gid','mtime_ns','xattrs')
def require(ok,message):
 if not ok:raise ValueError(message)
def digest(p):
 h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def small(p,cap=4*2**20):
 p=Path(p);require(p.is_file() and p.stat().st_size<=cap,'metadata absent/oversized: '+str(p));return json.loads(p.read_bytes())
def bound(ref,cap=4*2**20):
 require(digest(ref['path'])==ref['sha256'],'bound metadata changed: '+ref['path']);return small(ref['path'],cap)
def desc(p):
 p=Path(p);s=p.lstat();require(stat.S_ISREG(s.st_mode) and not p.is_symlink(),'regular non-symlink required: '+str(p))
 return dict(path=str(p),device=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,size=s.st_size,allocated=s.st_blocks*512,mode=stat.S_IMODE(s.st_mode),uid=s.st_uid,gid=s.st_gid,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,xattrs={n:os.getxattr(p,n).hex() for n in os.listxattr(p)})
def physical_alive(identity):
 require(set(('pid','start_ticks','boot_id'))<=set(identity),'process identity absent')
 if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=identity['boot_id']:return False
 try:
  fields=Path('/proc',str(identity['pid']),'stat').read_text().rsplit(')',1)[1].split()
  return int(fields[19])==identity['start_ticks'] and fields[0] not in ('Z','X')
 except (FileNotFoundError,ProcessLookupError):return False

def reader_check(targets):
 readers=[];errors=[];seen=fdcount=mapcount=0
 for proc in sorted(Path('/proc').iterdir()):
  if not proc.name.isdigit():continue
  seen+=1
  if seen>4096:errors.append('process ceiling exceeded');break
  try:
   s=(proc/'exe').stat();key=(s.st_dev,s.st_ino)
   if key in targets:readers.append({'pid':int(proc.name),'kind':'exe','paths':targets[key]})
  except (FileNotFoundError,ProcessLookupError):pass
  except PermissionError:errors.append('exe permission:'+proc.name)
  try:
   for f in (proc/'fd').iterdir():
    fdcount+=1
    if fdcount>131072:errors.append('fd ceiling exceeded');break
    try:s=f.stat();key=(s.st_dev,s.st_ino)
    except (FileNotFoundError,ProcessLookupError):continue
    except PermissionError:errors.append('fd permission:'+str(f));continue
    if key in targets:readers.append({'pid':int(proc.name),'kind':'fd','fd':f.name,'paths':targets[key]})
  except (FileNotFoundError,ProcessLookupError):pass
  except PermissionError:errors.append('fd dir permission:'+proc.name)
  try:
   with (proc/'maps').open() as stream:
    for line in stream:
     mapcount+=1
     if mapcount>1048576:errors.append('maps ceiling exceeded');break
     fields=line.split(None,5)
     if len(fields)<5:continue
     dev=fields[3].split(':');key=(os.makedev(int(dev[0],16),int(dev[1],16)),int(fields[4]))
     if key in targets:readers.append({'pid':int(proc.name),'kind':'mapped','paths':targets[key]})
  except (FileNotFoundError,ProcessLookupError):pass
  except PermissionError:errors.append('maps permission:'+proc.name)
 require(not readers and not errors,'reader inspection not closed: '+json.dumps({'readers':readers,'errors':errors}))
 return dict(readers=readers,errors=errors,seen=seen,fdcount=fdcount,mapcount=mapcount)

def accepted(attempt,item,manifest):
 cid=attempt['condition_id'];cond=manifest['conditions'][cid]
 require('qualification:'+attempt['qualification_id'] not in item.get('scientific_holds',{}),'accepted qualification now on scientific hold')
 require(attempt['actual_start'] is True and attempt['state']=='COMPLETE_VALID' and attempt.get('immutable_started_marker'),'paid COMPLETE_VALID with start witness required')
 require(attempt['identity']==cond['identity'] and attempt['qualification_id']==cond['qualification']['sha256'] and attempt['diagnostic_spec_sha256']==cond['spec_sha256'],'exact manifest/spec/Q identity required')
 ar=item['accepted_results'][attempt['attempt_id']]
 require(ar['identity']==attempt['identity'] and ar['qualification_id']==attempt['qualification_id'] and ar['run_key']==attempt['run_key'] and ar['scientific_scope']==manifest['validation_scope']['scientific_scope'],'accepted exact diagnostic identity required')
 directory=RESULTS/attempt['attempt_id'];require(Path(attempt['result_directory'])==directory and Path(ar['path'])==directory/'run_status.json','exact direct results path required')
 require(attempt['receipt_path']==ar['path'] and attempt['receipt_sha256']==ar['sha256'],'attempt/accepted receipt differs');
 import tagpressure_metadata as metadata
 receipt=metadata.read_accepted_result({'path':ar['path'],'sha256':ar['sha256']},attempt)
 require(receipt['status']=='COMPLETE_VALID' and receipt['independent_acceptance']=='PASS' and receipt['complete_input_verified'] is True and receipt['exit_code']==0 and type(receipt['exit_code']) is int,'formal terminal acceptance required')
 for field in ('identity','run_key','qualification_id','attempt_id'):require(receipt[field]==attempt[field],'receipt identity mismatch '+field)
 native_path=directory/'NATIVE_EXIT.json';require(digest(native_path)==receipt['native_exit_receipt_sha256'],'native durable exit changed');native=small(native_path)
 require(native==receipt['native_exit_evidence'] and native['exit_code']==native['wait_status']==0 and native['exited_normally'] is True and native['stop_reason'] is None and native['released_to_native'] is True,'true native wait0 required')
 require(native['native_process']==attempt['process'] and native['guardian_process']==attempt['exit_collector_process'],'native owner identity differs')
 for field in ('attempt_id','identity','run_key','qualification_id'):require(native['binding'][field]==attempt[field],'durable native binding differs '+field)
 for identity in (attempt['process'],attempt['exit_collector_process']):require(not physical_alive(identity),'accepted native/collector still active')
 return directory/'accel-sim.out'

def validate_aliases(rows,target,canonical,expected):
 can=desc(canonical);snap=desc(target);require(2<=can['nlink']<=5,'canonical must retain previously accepted CFD alias; maximum approved aliases5')
 aliases=[can]
 for path,approved in rows:
  d=desc(path)
  if (d['device'],d['inode'])==(can['device'],can['inode']):
   require(approved,'shared canonical alias must be a currently accepted r5 endpoint');aliases.append(d)
 require(len(aliases)==can['nlink'],'unknown canonical hardlink or missing known approved alias')
 require(all(all(d[k]==can[k] for k in UNCHANGED if k!='path') for d in aliases),'existing canonical alias metadata differs')
 require(all(snap[k]==can[k] for k in UNCHANGED if k!='path'),'snapshot metadata differs from frozen canonical')
 same=(snap['device'],snap['inode'])==(can['device'],can['inode'])
 require(same or snap['nlink']==1,'new snapshot has unknown alias')
 require(digest(target)==digest(canonical)==expected,'actual byte identity differs')
 return snap,can,aliases,same

def df():
 s=os.statvfs('/workspace');return s.f_bavail*s.f_frsize

def syncdir(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)

def write_new(p,value):
 with Path(p).open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 syncdir(Path(p).parent)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--attempt',required=True);ap.add_argument('--execute',action='store_true');ap.add_argument('--receipt-dir');args=ap.parse_args()
 require(not args.execute or args.receipt_dir,'execute requires append-only new receipt directory')
 sys.path.insert(0,str(E/'util/ep_l2/mechanism_e'));import coordinator as c;import tagpressure_successor as r5
 # Original exact controller then registry locks; never create a lock/controller.
 with (HOME/'CONTROLLER.lock').open('r+') as lc,(SHARED/'REGISTRY.lock').open('r+') as lr:
  fcntl.flock(lc,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(lr,fcntl.LOCK_EX|fcntl.LOCK_NB)
  c.tooling_binding();reg=(SHARED/'RUN_REGISTRY.json').read_bytes();data=json.loads(reg);item=c.ledger(data);manifest=r5.scope().manifest()
  require(item['controller']['state']=='STOPPED','original controller must be STOPPED')
  if item['controller'].get('process'):require(not physical_alive(item['controller']['process']),'old controller process still alive')
  require(not any(r.get('experiment_id')==c.CAMPAIGN and r.get('status') in c.ACTIVE for group in ('runs','resource_leases') for r in data[group].values()),'active E scientific/resource lease')
  alltail=[a for a in item['attempts'] if a.get('condition_id') in manifest['conditions']];matches=[a for a in alltail if a['attempt_id']==args.attempt]
  require(len(matches)==1,'exact unique approved r5 attempt required');attempt=matches[0];require(attempt['condition_id'] in ALLOWED_TARGETS,'only remaining DWT/Vector/Conv targets allowed')
  target=accepted(attempt,item,manifest);rows=[]
  for a in alltail:
   path=RESULTS/a['attempt_id']/'accel-sim.out'
   if not path.exists():continue
   approved=a.get('state')=='COMPLETE_VALID' and a['attempt_id'] in item['accepted_results']
   if approved:require(accepted(a,item,manifest)==path,'accepted alias identity mismatch')
   rows.append((path,approved))
  spec=bound(manifest['conditions'][attempt['condition_id']]['spec_ref']);r5.scope().check_spec(spec);require(Path(spec['binary'])==CANONICAL,'canonical production binary path changed')
  expected=manifest['source_identity']['binary_sha256'];snap,can,aliases,same=validate_aliases(rows,target,CANONICAL,expected)
  targets={}
  for d in [snap,can]+aliases:targets.setdefault((d['device'],d['inode']),[]).append(d['path'])
  check=reader_check(targets);usage=c.output_usage();before_df=df()
  plan=dict(schema='E2_R5_ACCEPTED_SNAPSHOT_BYTE_PRESERVING_SHARING_PLAN_V2',status='ALREADY_SHARED_NO_OP' if same else 'READ_ONLY_PLAN_NO_RELEASE_EXECUTED',attempt_id=attempt['attempt_id'],condition_id=attempt['condition_id'],actual_starts=item['actual_starts'],manifest_ref=r5.FINAL_SUCCESSOR_REF,qualified_sha256=expected,before=[snap,can],known_canonical_aliases=aliases,reader_check=check,generation_before=usage,df_before=before_df,registry_sha256=hashlib.sha256(reg).hexdigest(),hypothetical_recoverable_allocated_bytes=0 if same else snap['allocated'],scientific_content_path_mode_mtime_preserved=True,canonical_source_frozen=True,inode_nlink_ctime_change_disclosed=True,original_per_path_generation_charge_retained=True,no_raw_history_original_failed_ELF_or_registry_change=True,storage_contract='Root E056 byte sharing precedent only; refuse if future source/Q requires inode/write isolation. No launch or qualification authority.')
  if not args.execute or same:print(json.dumps(plan,indent=2));return
  D=Path(args.receipt_dir);require(D.is_absolute() and D.parent.resolve().is_relative_to((PACK/'engineering').resolve()),'receipt must be new under approved r5 engineering')
  require(not D.exists(),'receipt directory already exists; never overwrite');D.mkdir(mode=0o700);syncdir(D.parent);write_new(D/'PLAN_BEFORE.json',plan)
  tmp=target.with_name('.e2-byte-identical-r5-main-link-'+attempt['attempt_id']);require(not tmp.exists(),'previous partial link evidence present')
  # Under the original locks, reread registry + source inode identity immediately before replace.
  require((SHARED/'RUN_REGISTRY.json').read_bytes()==reg and desc(target)==snap and desc(CANONICAL)==can,'pre-mutation state drift')
  try:
   os.link(CANONICAL,tmp);require(digest(tmp)==expected,'temporary hardlink byte check failed');os.replace(tmp,target);syncdir(target.parent)
   after=[desc(target),desc(CANONICAL)];require(after[0]['inode']==after[1]['inode'] and all(d['nlink']==can['nlink']+1 for d in after),'shared inode/count differs')
   require(all(after[k][f]==old[f] for k,old in enumerate((snap,can)) for f in UNCHANGED),'scientific path/bytes/metadata changed')
   require(digest(target)==digest(CANONICAL)==expected,'postsharing bytes differ');require(c.output_usage()==usage,'logical generation changed');require((SHARED/'RUN_REGISTRY.json').read_bytes()==reg,'registry changed')
   final=dict(schema='E2_R5_ACCEPTED_SNAPSHOT_BYTE_PRESERVING_SHARING_RECEIPT_V2',status='EXACT_BYTES_RETAINED_LOGICAL_GENERATION_UNCHANGED',attempt_id=attempt['attempt_id'],condition_id=attempt['condition_id'],actual_starts=item['actual_starts'],qualified_sha256=expected,before=[snap,can],after=after,actual_df_before=before_df,actual_df_after=df(),generation_before=usage,generation_after=c.output_usage(),registry_unchanged=True,no_raw_or_history_or_production_bytes_changed=True,known_aliases_before=aliases)
   final['measured_df_increase_bytes']=final['actual_df_after']-before_df;write_new(D/'ACTUAL_RECEIPT.json',final);print(json.dumps(final,indent=2))
  except BaseException as exc:
   write_new(D/'FAILED_ENGINEERING_REVIEW_REQUIRED.json',dict(status='REVIEW_REQUIRED_NO_AUTOMATIC_RETRY',reason=repr(exc),temporary_link_path=str(tmp),target=str(target),canonical=str(CANONICAL),at_unix=time.time()));raise
if __name__=='__main__':main()
