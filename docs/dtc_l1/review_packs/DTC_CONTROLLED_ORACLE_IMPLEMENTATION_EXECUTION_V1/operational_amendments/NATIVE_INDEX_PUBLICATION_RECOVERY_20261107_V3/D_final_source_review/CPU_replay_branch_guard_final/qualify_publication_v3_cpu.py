"""No real Git, remote, model, owner, or production lock operation."""
from pathlib import Path
import copy,fcntl,hashlib,importlib.util,json,os,tempfile,time,types
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1')
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/D_independent_review_v1/unified_publication_native_index_transaction_source_review_v3/CPU_replay_branch_guard_final');P=O/'unified_watch_publish_v3.py'
s=importlib.util.spec_from_file_location('CPU_V3',P);w=importlib.util.module_from_spec(s);s.loader.exec_module(w);m=w.source_module()
checks=[]
def check(name,ok):assert ok,name;checks.append({'name':name,'pass':True})
def bad(name,fn):
 try:fn()
 except (ValueError,PermissionError,FileNotFoundError,TimeoutError):checks.append({'name':name,'pass':True});return
 raise AssertionError('expected HOLD '+name)
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def b(x):return json.dumps(x,sort_keys=True,indent=2).encode()+b'\n'
def sha(x):return hashlib.sha256(x).hexdigest()
with tempfile.TemporaryDirectory(dir='/root/data',prefix='M_CPU_PUBLICATION_V3_')as td:
 t=Path(td);w.NATIVE_INDEX_ROOT=t/'native';index=w.NATIVE_INDEX_ROOT/'private/CLEAN_UNIFIED_BACKGROUND_INDEX';index.parent.mkdir(parents=True);index.write_bytes(b'CPU INDEX')
 base=t/'base';lockpath=base/'control/publication_v1/LOCK';lockpath.parent.mkdir(parents=True);lockpath.write_text('CPU ONLY')
 with lockpath.open('a+')as fd:
  fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);check('actual_CPU_only_publock_parser',w.require_publock(base)['exclusive_FLOCK_observed'])
 bad('missing_current_publock_HOLD',lambda:w.require_publock(base))
 def safe(*a):return {'no_potential_writer':True,'no_index_or_lock_open_fd':True,'CPU_MOCK_ONLY':True}
 def guard(*a):return {'CPU_MOCK_ONLY_NO_PRODUCTION_LOCK':True}
 lock=Path(str(index)+'.lock');journal=t/'journal'
 def make_lock(payload=b'CPU LOCK'):
  lock.write_bytes(payload);os.utime(lock,(time.time()-120,time.time()-120))
 check('no_lock_is_noop',w.quarantine_own_lock(index,journal,base,'CPU','CPU',probe=safe,lock_guard=guard)['status']=='NO_PRIVATE_INDEX_LOCK')
 make_lock();before=w.fingerprint(lock)
 q=w.quarantine_own_lock(index,journal,base,'CPU','CPU',probe=safe,lock_guard=guard)
 check('abandoned_lock_preserved_rename_not_delete',not lock.exists()and Path(q['quarantine_path']).read_bytes()==b'CPU LOCK'and q['fingerprint']==before)
 check('private_index_bytes_unchanged',index.read_bytes()==b'CPU INDEX')
 make_lock(b'');q=w.quarantine_own_lock(index,journal,base,'CPU','CPU',probe=safe,lock_guard=guard);check('zero_byte_lock_still_preserved',Path(q['quarantine_path']).exists())
 make_lock();bad('active_writer_HOLD',lambda:w.quarantine_own_lock(index,journal,base,'CPU','CPU',probe=lambda*a:{'no_potential_writer':False,'no_index_or_lock_open_fd':True},lock_guard=guard));lock.unlink()
 make_lock();bad('open_FD_HOLD',lambda:w.quarantine_own_lock(index,journal,base,'CPU','CPU',probe=lambda*a:{'no_potential_writer':True,'no_index_or_lock_open_fd':False},lock_guard=guard));lock.unlink()
 make_lock();bad('unknown_probe_HOLD',lambda:w.quarantine_own_lock(index,journal,base,'CPU','CPU',probe=lambda*a:(_ for _ in()).throw(PermissionError('CPU UNKNOWN')),lock_guard=guard));lock.unlink()
 make_lock();mutated={'n':0}
 def changing(*a):mutated['n']+=1;lock.write_bytes(b'CHANGED');return safe()
 bad('lock_mutation_HOLD',lambda:w.quarantine_own_lock(index,journal,base,'CPU','CPU',probe=changing,lock_guard=guard));lock.unlink()
 make_lock();os.utime(lock,None);bad('fresh_lock_HOLD',lambda:w.quarantine_own_lock(index,journal,base,'CPU','CPU',probe=safe,lock_guard=guard));lock.unlink()
 outside=t/'outside/CLEAN_UNIFIED_BACKGROUND_INDEX';outside.parent.mkdir();bad('foreign_index_HOLD',lambda:w.quarantine_own_lock(outside,journal,base,'CPU','CPU',probe=safe,lock_guard=guard))
 lock.symlink_to(index);bad('symlink_lock_HOLD',lambda:w.quarantine_own_lock(index,journal,base,'CPU','CPU',probe=safe,lock_guard=guard));lock.unlink()
 for arg,sec in [('commit',900),('read-tree',300),('add',300),('update-index',300),('push',180),('fetch',180),('ls-remote',180),('show',120)]:check('bounded_timeout_'+arg,w.timeout_for([arg])==sec)
 check('V3_payload_module_file',m.__file__==str(P))
 cfg={'schema':'DTC_ORACLE_MAIN_PUBLICATION_ENABLE_V1','enabled':False,'coordinator':'DTC-MAIN'}
 bad('default_enable_false_before_any_Git',lambda:m.GitPublication(base,cfg,runner=lambda*a,**k:(_ for _ in()).throw(AssertionError('NO GIT'))))
 # Exercise the real process-reader code with an explicitly isolated fake /proc.
 realPath=w.Path;proc=t/'CPU_PROC';proc.mkdir();pid=proc/'999999990';pid.mkdir();(pid/'fd').mkdir()
 fields=['0']*22;fields[18]='777';(pid/'stat').write_text('999999990 (CPU) S '+' '.join(fields));(pid/'cmdline').write_bytes(b'CPU\0');(pid/'environ').write_bytes(b'')
 def fakePath(v):return proc if str(v)=='/proc'else realPath(v)
 w.Path=fakePath
 try:
  check('process_reader_clean_CPU_backend',w.no_writer_proof(index,lock,'/cpu/repo','/cpu/work')['no_potential_writer'])
  (pid/'environ').write_bytes(b'GIT_INDEX_FILE='+str(index.resolve()).encode()+b'\0')
  bad('process_reader_index_environment_writer_HOLD',lambda:w.no_writer_proof(index,lock,'/cpu/repo','/cpu/work'))
  (pid/'environ').write_bytes(b'');(pid/'fd/9').symlink_to(index)
  bad('process_reader_open_index_FD_HOLD',lambda:w.no_writer_proof(index,lock,'/cpu/repo','/cpu/work'));(pid/'fd/9').unlink()
  (pid/'cmdline').write_bytes(b'git\0--git-dir=/cpu/repo\0')
  bad('process_reader_related_Git_HOLD',lambda:w.no_writer_proof(index,lock,'/cpu/repo','/cpu/work'))
 finally:w.Path=realPath
 # Reconcile old108 even if the current consumer later sees127. No current-view
 # fingerprint is used in this routine; no commit/reset/read-tree command occurs.
 matrix=json.loads((A/'control/authority/FUTURE_DH_ORACLE_MATRIX.json').read_bytes());planids={x['plan_id']for x in matrix['rows']}
 pins=[{'plan_id':x['plan_id'],'uuid':'CPU_UUID_'+str(i),'result_path':'/CPU_APPROVED/'+str(i)+'.RESULT.json','result_sha256':hashlib.sha256(str(i).encode()).hexdigest()}for i,x in enumerate(matrix['rows'][:108])]
 oldwatch='2efc2e63b0b13fcccc979b4fe94b163220eab8e8366b29e5f3e85aa461e8dd59';bridge='ab11e9fe773f5213572c593800ef0c0f051d4836583a5b99a395759c8e35238d'
 scope={'authority':m.AUTHORITY,'matrix_sha256':m.MATRIX_SHA,'PLAN_population':128,'program_population':32,'closed_RESULT_source_pins':pins,'closed_RESULT_count':108,'closed_fingerprint_sha256':'a'*64,'consumer_implementation_sha256':bridge,'watcher_implementation_sha256':oldwatch}
 sb=b(scope);manifest={'members':[{'path':'PUBLICATION_SCOPE.json','sha256':sha(sb)}],'source_RESULT_pins':pins};mb=b(manifest)
 latest={'snapshot':'20261107T080000Z_aaaaaaaaaaaaaaaa','manifest_sha256':sha(mb),'closed_RESULT_count':108,'closed_fingerprint_sha256':'a'*64}
 rel=m.REL+'/live_results/'+latest['snapshot'];head='3'*40;pre='2'*40
 w.require_publock=guard;quarantine_calls=[]
 def CPU_quarantine(*a,**k):quarantine_calls.append('CPU');return {'status':'CPU_NO_LOCK'}
 w.quarantine_own_lock=CPU_quarantine
 class Pub:
  def __init__(self):
   self.base=base;self.index=index;self.gitdir='CPU';self.work='CPU';self.cfg={'approved_consumer_bridge_sha256':bridge,'approved_prior_watcher_sha256':[oldwatch]};self.allowed_plan_ids=planids;self.result_roots=[Path('/CPU_APPROVED')];self.calls=[];self.remote=head;self.head=head;self.branch=m.BRANCH
  def remote_sha(self):return self.remote
  def run(self,args):
   self.calls.append(args)
   if args==['symbolic-ref','--short','HEAD']:return self.branch.encode()+b'\n'
   if args==['rev-parse','HEAD']:return self.head.encode()+b'\n'
   if args==['rev-parse','FETCH_HEAD']:return self.remote.encode()+b'\n'
   if args==['rev-parse',head+'^']:return pre.encode()+b'\n'
   if args[0]=='fetch':return b''
   if args[0]=='push':self.remote=self.head;return b''
   if args[0]=='diff-tree':return ('\n'.join(['CPU_EXPECTED_PATH'])+'\n').encode()
   if args[0]=='show':
    if args[1].endswith('/LATEST.json'):return b(latest)
    if args[1].endswith('/PUBLICATION_SCOPE.json'):return sb
    if args[1].endswith('/MANIFEST.json'):return mb
   raise AssertionError('Unexpected fake Git '+repr(args))
 st=t/'state';st.mkdir();put(st/'WATCH_STATE.json',{'last_commit':'1'*40,'last_closed_RESULT_count':103,'last_published_fingerprint':'b'*64})
 before_state=(st/'WATCH_STATE.json').read_bytes();before_quarantines=len(quarantine_calls)
 pub=Pub();pub.branch='WRONG_BRANCH'
 bad('actual_wrong_branch_HOLD_before_recovery',lambda:m._V3_reconcile(pub,st,10000))
 check('wrong_branch_zero_push_zero_state_update',not any(x[0]=='push'for x in pub.calls)and(st/'WATCH_STATE.json').read_bytes()==before_state)
 check('wrong_branch_zero_quarantine',len(quarantine_calls)==before_quarantines)
 pub=Pub();r=m._V3_reconcile(pub,st,10000)
 check('remote108_adopted_over_stale103',read_state:=json.loads((st/'WATCH_STATE.json').read_bytes())['last_closed_RESULT_count']==108)
 check('adoption_no_commit_reset_or_restage',not any(x[0]in('commit','reset','read-tree','add')for x in pub.calls))
 check('adoption_preserves30min_gate',m.due({'closed_RESULT_count':127,'closed_fingerprint_sha256':'c'*64},json.loads((st/'WATCH_STATE.json').read_bytes()),10001)[0]is False)
 # Wrong provenance, scope, source root and duplicate source pins remain HOLD.
 for key,value,label in [('watcher_implementation_sha256','unknown','watcher'),('consumer_implementation_sha256','unknown','consumer'),('PLAN_population',127,'scope')]:
  previous=scope[key];scope[key]=value;sb=b(scope);manifest['members'][0]['sha256']=sha(sb);mb=b(manifest);latest['manifest_sha256']=sha(mb)
  bad('remote_'+label+'_ambiguity_HOLD',lambda:m._V3_reconcile(Pub(),st,10000));scope[key]=previous
 sb=b(scope);manifest['members'][0]['sha256']=sha(sb);mb=b(manifest);latest['manifest_sha256']=sha(mb)
 prior=latest['manifest_sha256'];latest['manifest_sha256']='0'*64;bad('remote_manifest_SHA_HOLD',lambda:m._V3_reconcile(Pub(),st,10000));latest['manifest_sha256']=prior
 pub=Pub();pub.remote=pre
 bad('different_HEAD_remote_without_own_intent_HOLD',lambda:m._V3_reconcile(pub,st,10000))
 put(st/'LAST_PUBLICATION_INTENT.json',{'precommit_head':pre,'payload_manifest_sha256':sha(mb),'snapshot_relative':rel,'expected_staged_paths':['CPU_EXPECTED_PATH']})
 pub=Pub();pub.remote=pre;r=m._V3_reconcile(pub,st,10000)
 check('known_exact_local_commit_completed_by_push_not_recommit',any(x[0]=='push'for x in pub.calls)and not any(x[0]=='commit'for x in pub.calls))
 intent=json.loads((st/'LAST_PUBLICATION_INTENT.json').read_bytes());intent['expected_staged_paths']=['FOREIGN'];put(st/'LAST_PUBLICATION_INTENT.json',intent)
 pub=Pub();pub.remote=pre;bad('pending_local_foreign_staged_paths_HOLD',lambda:m._V3_reconcile(pub,st,10000))
 # Real run method with a CPU fake runner only.
 obj=m.GitPublication.__new__(m.GitPublication);obj.prefix=['CPU_NOT_EXECUTABLE'];obj.env={};obj.index=index;obj.state=st
 calls=[]
 def runner(args,**kw):calls.append(kw['timeout']);return types.SimpleNamespace(returncode=0,stdout=b'CPU',stderr=b'')
 obj.runner=runner;obj.run(['commit','-m','CPU']);check('run_commit900_journal_success',calls==[900]and json.loads((st/'LAST_GIT_COMMAND.json').read_bytes())['status']=='RETURNED_SUCCESS')
 def failure(*a,**kw):raise TimeoutError('CPU NO ACTUAL GIT')
 obj.runner=failure;bad('run_timeout_journal_no_retry',lambda:obj.run(['commit','-m','CPU']))
 check('timeout_uncertainty_preserved',json.loads((st/'PUBLICATION_RECOVERY_REQUIRED.json').read_bytes())['status']=='OUTCOME_UNCERTAIN_RECONCILE_BEFORE_NEW_PUBLICATION')
out={'status':'PASS_V3_CPU_ONLY','cases':len(checks),'checks':checks,'actual_Git_commands':0,'actual_network_calls':0,'production_lock_or_index_mutations':0,'publisher_started':False,'models_started':0,'registrations':0,'CPU_only_private_temp_lock_rename':True,'fake_proc_and_Git_backends_explicit':True,'source_sha256':w.sha(P)}
(O/'CPU_QUALIFICATION.fixed.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':'PASS','cases':len(checks),'source_sha256':w.sha(P)}))
