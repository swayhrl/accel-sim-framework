"""Main-owned publisher candidate: native private index and preserved recovery.
No scientific/owner/dispatcher capabilities. Author never starts this module.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,stat,time
V2_PATH='/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/M_unified_publication_proposal_v2/unified_watch_publish_source_proposal.py'
V2_SHA='2efc2e63b0b13fcccc979b4fe94b163220eab8e8366b29e5f3e85aa461e8dd59'
NATIVE_INDEX_ROOT=Path('/root/data/dtc_oracle_publication_v3')
def need(x,why):
 if not x:raise ValueError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def fingerprint(p):
 s=Path(p).lstat();need(stat.S_ISREG(s.st_mode)and s.st_nlink==1,'LOCK_NOT_SINGLE_REGULAR_FILE')
 return {'dev':s.st_dev,'ino':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'sha256':sha(p)}
def require_publock(base):
 p=Path(base)/'control/publication_v1/LOCK';s=p.stat();identity=f'{os.major(s.st_dev):x}:{os.minor(s.st_dev):x}:{s.st_ino}'
 for line in Path('/proc/locks').read_text().splitlines():
  a=line.split()
  if len(a)>5 and a[1]=='FLOCK'and a[3]=='WRITE'and a[4]==str(os.getpid()):
   b=a[5].split(':');normalized=f'{int(b[0],16):x}:{int(b[1],16):x}:{int(b[2])}'
   if normalized==identity:return {'pid':os.getpid(),'lock_identity':identity,'exclusive_FLOCK_observed':True}
 raise ValueError('CURRENT_PROCESS_MUST_HOLD_COMMON_PUBLOCK')
def no_writer_proof(index,lock,gitdir,work):
 """Fail closed on unreadable process state. No env content is recorded."""
 index=str(Path(index).resolve());lock=str(Path(lock).resolve());targets={index,lock};seen=0
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  pid=int(proc.name)
  if pid==os.getpid():continue
  try:
   initial=(proc/'stat').read_text();start=initial.rsplit(')',1)[1].split()[19]
   command=(proc/'cmdline').read_bytes();env=(proc/'environ').read_bytes()
   indexed=(b'GIT_INDEX_FILE='+index.encode())in env.split(b'\0')
   git_command=command.split(b'\0')[0].rsplit(b'/',1)[-1].startswith(b'git')
   repo_related=(str(gitdir).encode()in command or str(work).encode()in command)
   need(not indexed and not(git_command and repo_related),'POTENTIAL_PRIVATE_INDEX_OR_REPO_WRITER:'+str(pid))
   for fd in (proc/'fd').iterdir():
    try:target=os.readlink(fd)
    except FileNotFoundError:continue
    need(target.removesuffix(' (deleted)')not in targets,'INDEX_OR_LOCK_OPEN_FD:'+str(pid))
   final=(proc/'stat').read_text().rsplit(')',1)[1].split()[19]
   need(final==start,'PROCESS_IDENTITY_CHANGED_DURING_PROOF')
   seen+=1
  except (FileNotFoundError,ProcessLookupError):continue
  except PermissionError as e:raise ValueError('UNREADABLE_PROCESS_STATE_HOLD:'+str(pid))from e
 return {'no_potential_writer':True,'no_index_or_lock_open_fd':True,'processes_checked':seen}
def quarantine_own_lock(index,journal,base,gitdir,work,*,probe=no_writer_proof,lock_guard=require_publock,now=None):
 """Only the exact native V3 index; same PUBLOCK; preserve rather than delete."""
 index=Path(index);journal=Path(journal);now=time.time()if now is None else now
 need(index.parent.resolve().is_relative_to(NATIVE_INDEX_ROOT.resolve()),'NOT_OWN_NATIVE_PRIVATE_INDEX')
 lock=Path(str(index)+'.lock')
 if not lock.exists():return {'status':'NO_PRIVATE_INDEX_LOCK'}
 lock_guard(base);first=fingerprint(lock);index_before=fingerprint(index)if index.exists()else None
 need(now-lock.stat().st_mtime>=60,'LOCK_TOO_RECENT_HOLD')
 one=probe(index,lock,gitdir,work);two=probe(index,lock,gitdir,work)
 need(one.get('no_potential_writer')and one.get('no_index_or_lock_open_fd')and two.get('no_potential_writer')and two.get('no_index_or_lock_open_fd'),'NO_WRITER_PROOF_FAILED')
 need(fingerprint(lock)==first,'LOCK_CHANGED_DURING_PROOF')
 need((fingerprint(index)if index.exists()else None)==index_before,'INDEX_CHANGED_DURING_PROOF');lock_guard(base)
 journal.mkdir(parents=True,exist_ok=True)
 quarantine_dir=index.parent/'abandoned_lock_quarantine';quarantine_dir.mkdir(exist_ok=True)
 target=quarantine_dir/('INDEX.lock.'+str(time.time_ns())+'.quarantined')
 need(not target.exists(),'QUARANTINE_TARGET_ALREADY_EXISTS')
 pre={'status':'ABANDONED_PRIVATE_INDEX_LOCK_QUARANTINE_INTENT','lock_path':str(lock),'quarantine_path':str(target),'fingerprint':first,'index_fingerprint':index_before,'proofs':[one,two]}
 record=journal/(target.name+'.json');record.write_text(json.dumps(pre,sort_keys=True,indent=2)+'\n')
 need(fingerprint(lock)==first,'LOCK_CHANGED_BEFORE_RENAME')
 os.rename(lock,target)
 after=fingerprint(target)
 need(all(after[k]==first[k]for k in ('dev','ino','size','mtime_ns','sha256')),'QUARANTINE_INODE_OR_CONTENT_CHANGED')
 need(not lock.exists(),'LOCK_REAPPEARED_HOLD')
 pre.update(status='ABANDONED_PRIVATE_INDEX_LOCK_QUARANTINED_PRESERVED',quarantined_sha256=sha(target))
 record.write_text(json.dumps(pre,sort_keys=True,indent=2)+'\n');return pre
def timeout_for(args):
 if args and args[0]=='commit':return 900
 if args and args[0]in('read-tree','add','update-index','diff'):return 300
 if args and args[0]in('push','fetch','ls-remote'):return 180
 return 120
def source_module():
 p=Path(V2_PATH);need(sha(p)==V2_SHA,'FROZEN_V2_SOURCE_DRIFT')
 spec=importlib.util.spec_from_file_location('V3_FROZEN_V2_SOURCE',p);w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
 m=w.source_module();m.__file__=__file__;Base=m.GitPublication;oldcycle=m.cycle;first={'needed':True}
 class PublicationV3(Base):
  def __init__(self,base,config,runner=None):
   super().__init__(base,config,runner)
   raw=Path(config['native_private_index']);need(raw.is_absolute()and not raw.is_symlink(),'PRIVATE_INDEX_MUST_BE_ABSOLUTE_NONSYMLINK')
   native=raw.resolve()
   need(native.parent.is_relative_to(NATIVE_INDEX_ROOT.resolve())and native.name=='CLEAN_UNIFIED_BACKGROUND_INDEX','EXPLICIT_NATIVE_PRIVATE_INDEX_REQUIRED')
   native.parent.mkdir(parents=True,exist_ok=True)
   need(native.parent.stat().st_dev==Path('/root/data').stat().st_dev,'PRIVATE_INDEX_NOT_NATIVE_FILESYSTEM')
   need(not native.is_symlink()and not Path(str(native)+'.lock').is_symlink(),'PRIVATE_INDEX_SYMLINK_FORBIDDEN')
   self.index=native;self.env['GIT_INDEX_FILE']=str(native)
   self.prefix[1:1]=['-c','gc.auto=0','-c','maintenance.auto=false']
   self.state=Path(m._V3_STATE_DIR)
   binding_ref=config['caller_bindings'];need(sha(binding_ref['path'])==binding_ref['sha256'],'CALLER_BINDING_PIN_DRIFT')
   bindings=read(binding_ref['path']);self.result_roots=[Path(bindings[k]['root']).resolve()for k in ('initial8_data_only','remaining24_private')]
   matrix_path=Path(bindings['fixed_matrix']['path']);need(sha(matrix_path)==m.MATRIX_SHA,'FIXED_MATRIX_PIN_DRIFT')
   self.allowed_plan_ids={x['plan_id']for x in read(matrix_path)['rows']}
  def run(self,args,input_bytes=None):
   # No detached Git process or retry: timeout propagates into the preserved journal.
   record={'args':list(args),'timeout_seconds':timeout_for(args),'started_epoch':time.time(),'status':'RUNNING','private_index':str(self.index)}
   if args and args[0]in('commit','push','read-tree','add','update-index'):m.atomic(self.state/'LAST_GIT_COMMAND.json',record)
   try:
    r=self.runner(self.prefix+list(args),input=input_bytes,env=self.env,capture_output=True,check=False,timeout=timeout_for(args))
    need(r.returncode==0,'Git command failed: '+str(args[:2])+' '+r.stderr.decode(errors='replace')[:500])
    record.update(status='RETURNED_SUCCESS',finished_epoch=time.time())
    if args and args[0]in('commit','push','read-tree','add','update-index'):m.atomic(self.state/'LAST_GIT_COMMAND.json',record)
    return r.stdout
   except Exception as e:
    record.update(status='OUTCOME_UNCERTAIN_RECONCILE_BEFORE_NEW_PUBLICATION',error=type(e).__name__+': '+str(e),finished_epoch=time.time())
    m.atomic(self.state/'PUBLICATION_RECOVERY_REQUIRED.json',record);raise
  def commit_snapshot(self,source_payload,view,now):
   head=self.validate_head();stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime(now));leaf=stamp+'_'+view['closed_fingerprint_sha256'][:16]
   relative=m.REL+'/live_results/'+leaf
   expected_paths=[relative+'/'+p.name for p in sorted(Path(source_payload).iterdir())if p.is_file()]+[m.REL+'/live_results/LATEST.json']
   m.atomic(self.state/'LAST_PUBLICATION_INTENT.json',{'precommit_head':head,'payload_manifest_sha256':sha(Path(source_payload)/'MANIFEST.json'),'expected_staged_paths':expected_paths,
    'snapshot_relative':m.REL+'/live_results/'+leaf,'fingerprint':view['closed_fingerprint_sha256'],'closed_count':view['closed_RESULT_count'],'created_epoch':now})
   return super().commit_snapshot(source_payload,view,now)
 def reconcile(pub,state_dir,now):
  require_publock(pub.base)
  quarantine=quarantine_own_lock(pub.index,state_dir/'lock_quarantine',pub.base,pub.gitdir,pub.work)
  head=pub.run(['rev-parse','HEAD']).decode().strip();remote=pub.remote_sha()
  intent_path=state_dir/'LAST_PUBLICATION_INTENT.json'
  if head!=remote:
   need(intent_path.exists(),'LOCAL_REMOTE_DIFFER_WITHOUT_OWN_TRANSACTION_HOLD');intent=read(intent_path)
   need(remote==intent['precommit_head'],'REMOTE_ADVANCED_OR_DIVERGED_HOLD')
   parent=pub.run(['rev-parse',head+'^']).decode().strip();need(parent==remote,'NOT_OWN_SINGLE_PENDING_COMMIT_HOLD')
   manifest=pub.run(['show',head+':'+intent['snapshot_relative']+'/MANIFEST.json'])
   need(hashlib.sha256(manifest).hexdigest()==intent['payload_manifest_sha256'],'PENDING_LOCAL_MANIFEST_DIFFERS_HOLD')
   changed=pub.run(['diff-tree','--no-commit-id','--name-only','-r',head]).decode().splitlines()
   need(set(changed)==set(intent['expected_staged_paths']),'PENDING_LOCAL_COMMIT_PATHS_DIFFER_HOLD')
   pub.run(['push','origin',head+':refs/heads/'+m.BRANCH]);need(pub.remote_sha()==head,'EXACT_EXISTING_COMMIT_PUSH_NOT_VERIFIED')
  pub.run(['fetch','--no-tags','origin','refs/heads/'+m.BRANCH]);need(pub.run(['rev-parse','FETCH_HEAD']).decode().strip()==head,'REMOTE_CHANGED_DURING_RECOVERY_HOLD')
  latest=json.loads(pub.run(['show','FETCH_HEAD:'+m.REL+'/live_results/LATEST.json']))
  name=latest['snapshot'];need(m.re.fullmatch(r'\d{8}T\d{6}Z_[0-9a-f]{16}',name)is not None,'INVALID_REMOTE_LEAF')
  rel=m.REL+'/live_results/'+name;manifest_bytes=pub.run(['show','FETCH_HEAD:'+rel+'/MANIFEST.json'])
  need(hashlib.sha256(manifest_bytes).hexdigest()==latest['manifest_sha256'],'REMOTE_MANIFEST_DIGEST_MISMATCH')
  manifest=json.loads(manifest_bytes);scope_bytes=pub.run(['show','FETCH_HEAD:'+rel+'/PUBLICATION_SCOPE.json']);scope=json.loads(scope_bytes)
  need(scope['authority']==m.AUTHORITY and scope['matrix_sha256']==m.MATRIX_SHA and scope['PLAN_population']==128 and scope['program_population']==32,'REMOTE_FIXED_SCIENTIFIC_SCOPE_MISMATCH')
  need(scope['consumer_implementation_sha256']==pub.cfg['approved_consumer_bridge_sha256'],'REMOTE_CONSUMER_PROVENANCE_NOT_APPROVED')
  need(scope['watcher_implementation_sha256']in pub.cfg['approved_prior_watcher_sha256']+[sha(__file__)],'REMOTE_WATCHER_PROVENANCE_NOT_APPROVED')
  member=next(x for x in manifest['members']if x['path']=='PUBLICATION_SCOPE.json')
  need(hashlib.sha256(scope_bytes).hexdigest()==member['sha256'],'REMOTE_SCOPE_DIGEST_MISMATCH')
  need(scope['closed_RESULT_source_pins']==manifest['source_RESULT_pins']and scope['closed_RESULT_count']==latest['closed_RESULT_count'],'REMOTE_SOURCE_PINS_MISMATCH')
  pins=scope['closed_RESULT_source_pins'];need(len(pins)==scope['closed_RESULT_count']and len({x['plan_id']for x in pins})==len(pins),'REMOTE_SOURCE_PIN_COUNT_OR_DUPLICATE')
  need(all(x['plan_id']in pub.allowed_plan_ids and m.re.fullmatch('[0-9a-f]{64}',x['result_sha256'])and isinstance(x.get('uuid'),str)and bool(x['uuid'])
   and any(Path(x['result_path']).resolve().is_relative_to(r)for r in pub.result_roots)for x in pins),'REMOTE_RESULT_IDENTITY_OR_ROOT_NOT_APPROVED')
  need(scope['closed_fingerprint_sha256']==latest['closed_fingerprint_sha256'],'REMOTE_PUBLICATION_FINGERPRINT_MISMATCH')
  current=read(state_dir/'WATCH_STATE.json')if(state_dir/'WATCH_STATE.json').exists()else{}
  current.update(last_commit=head,last_published_fingerprint=scope['closed_fingerprint_sha256'],last_publication_epoch=now,
   last_closed_RESULT_count=scope['closed_RESULT_count'],last_action='ADOPTED_VERIFIED_EXISTING_REMOTE_COMMIT_NO_RECOMMIT')
  m.atomic(state_dir/'WATCH_STATE.json',current)
  receipt={'status':'PASS_EXISTING_REMOTE_TRANSACTION_ADOPTED','commit':head,'manifest_sha256':latest['manifest_sha256'],
   'closed_count':scope['closed_RESULT_count'],'lock_recovery':quarantine,'new_commit_created':False,'no_reset_or_force_push':True,'epoch':now}
  m.atomic(state_dir/'RECOVERY_RECONCILIATION_LATEST.json',receipt)
  marker=state_dir/'PUBLICATION_RECOVERY_REQUIRED.json'
  if marker.exists():os.rename(marker,state_dir/('RECOVERED_ERROR.'+str(time.time_ns())+'.json'))
  return receipt
 def cycle(base,matrix_path,consumer,consumer_pin,state_dir,config_path=None,now=None,native_base=None):
  now=time.time()if now is None else now;state_dir=Path(state_dir);state_dir.mkdir(parents=True,exist_ok=True);m._V3_STATE_DIR=str(state_dir)
  if config_path:
   require_publock(base);cfg=m.load(config_path);pub=PublicationV3(base,cfg)
   if first['needed']or(state_dir/'PUBLICATION_RECOVERY_REQUIRED.json').exists()or Path(str(pub.index)+'.lock').exists():
    reconcile(pub,state_dir,now);first['needed']=False
  try:return oldcycle(base,matrix_path,consumer,consumer_pin,state_dir,config_path,now,native_base)
  except Exception as e:
   if config_path:m.atomic(state_dir/'PUBLICATION_RECOVERY_REQUIRED.json',{'status':'CYCLE_INCOMPLETE_RECONCILE','error':type(e).__name__+': '+str(e),'epoch':now})
   raise
 m.GitPublication=PublicationV3;m.cycle=cycle;m._V3_reconcile=reconcile
 return m
if __name__=='__main__':source_module().main()
