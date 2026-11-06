"""CPU-only candidate: exact Remaining24 owner-image operational extension.

Import is inert. Only DTC-MAIN's separately reviewed Main-thread management
release may call apply(). No CLI or test invokes actual apply/registration/model.
The 29a dispatcher is privately derived, not installed over historical tools.
"""
from pathlib import Path
import contextlib,copy,fcntl,hashlib,json,os,sys,threading,time,types

BASE=Path('/root/data/dtc_controlled_oracle_20261106_v1')
N=Path('/root/data/ep_l2_dtc_l1_native_v2')
T=Path('/root/data/dtc_main_v100_sweep_20261025_v1')
OWNER=1498278;START=977758783
REQUEST8='DTC_ORACLE_INITIAL8_20261106_V1'
REQUEST24='DTC_ORACLE_REMAINING24_20261106_V1'
OLD_OPS_SHA='29a97d55dc2acc4e84c3fa228025f7d2f619ef7d1fbc1af867645ec279047fb4'
S6_SHA='f4b3338510b4c89ca16977c2f1fc13fcde262f8d8b3b21681946b177f2016778'
ALIAS_SHA='5525945a40de4b28a9c28382bdb5829747d277413518f7250c74606c78c8c3f3'
SPARSE_SHA='dc00fb7a0435c85dd0b377ead470df58ce9127d6bc1ef32b7ec69ad5a5885c6d'
RAW_EXEC_HELPER_SHA='3c0a592fe2e15a8b6f2f39801765b9a26e1f1dc5fc9203408a9a33666db5806e'
MARKER='DTC_ORACLE_REAL_OWNER_IMAGE_B_POOL_V1'
GOV=BASE/'control/OWNER_RECOVERY_AND_CLOSEOUT.lock'

class Hold(RuntimeError):pass
def need(x,reason):
 if not x:raise Hold(reason)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def encoded(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def pinned(ref):
 p=Path(ref['path']);need(sha(p)==ref['sha256'],'PIN_DRIFT:'+str(p));return p
def load(p,name):
 p=Path(p);m=types.ModuleType(name);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as h:h.write(encoded(v));h.flush();os.fsync(h.fileno())
def proc_start(pid):return int(Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19])

def receipt_proof(root,c,row):
 """Read only: a claim may retire only after real consumed/DONE/EXIT/raw proof."""
 root=Path(root);ledger=root/'control/qualification_ledger';ip=ledger/(c+'.INTENT.json')
 i=rd(ip);need(sha(ip)==row['intent_sha256'],'ORIGINAL_INTENT_PIN')
 out=root/'DTC/run/results'/row['uuid']
 need(i['uuid']==row['uuid']and i['cohort']==c and Path(i['output'])==out,'ORIGINAL_UUID_OUTPUT')
 pidfile=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
 pid=rd(pidfile)if pidfile.exists()else None
 live=False
 if pid is not None:
  try:live=proc_start(pid['pid'])==pid['start_ticks']
  except FileNotFoundError:pass
 dpath=ledger/(c+'.DONE.json')
 if row.get('execution_receipt') is None or not dpath.exists():
  return dict(state='LIVE_OR_UNCERTAIN_RETAIN_CLAIM',actual_simulator_live=live,pid=pid,uuid=row['uuid'])
 d=rd(dpath)
 need(d==row['execution_receipt']==rd(out/'NATIVE_EXIT.json'),'ORIGINAL_DONE_EXIT_RECEIPT')
 need(d['uuid']==row['uuid']and d['cohort']==c and d['new_attempt_consumed']==1
      and d['automatic_retry']is False,'ORIGINAL_ONCE_ONLY_RECEIPT')
 need(sha(out/'raw.log.gz')==d['raw_sha256'],'ORIGINAL_CLOSED_RAW_PIN')
 need(not live,'RECEIPT_WITH_LIVE_SIMULATOR_HOLD')
 return dict(state='EXACT_CLOSED_NONLIVE_RETAIN_ARCHIVE_BACKLOG',uuid=row['uuid'],
             done_sha256=sha(dpath),raw_sha256=d['raw_sha256'],actual_simulator_live=False,
             original_stop_reason=d['stop_reason'],original_returncode=d['launcher_wait_returncode'])

def resource_hold(error):
 return isinstance(error,RuntimeError)and str(error).startswith(('RESOURCE_HOLD','REGISTRY_SHARED_LOCK_BUSY','REGISTRY_EX_BUSY','REGISTRY_BUSY'))

def unused_identity(ctx,c):
 q=ctx['e'].registered()[2]
 need(c not in q['consumed'],'CONSUMED_IDENTITY_NEVER_RESUBMIT')
 need(not(Path(ctx['root'])/'control/qualification_ledger'/(c+'.INTENT.json')).exists(),
      'UNCERTAIN_INTENT_RETAIN_CLAIM')
 return True

def closed_receipt(ctx,c):
 q=ctx['e'].registered()[2];proof=receipt_proof(ctx['root'],c,q['consumed'][c])
 need(proof['state']=='EXACT_CLOSED_NONLIVE_RETAIN_ARCHIVE_BACKLOG','EXACT_CLOSED_RECEIPT_REQUIRED')
 return proof

def launch_phase_ready(running):
 """Admission may overlap execution, not another incomplete launch phase."""
 for future,(ctx,c)in list(running.items()):
  finished=future.done();q=ctx['e'].registered()[2]
  if c not in q['consumed']:
   if finished:unused_identity(ctx,c);continue
   return False
  row=q['consumed'][c]
  if row.get('execution_receipt'):closed_receipt(ctx,c);continue
  need(not finished,'FINISHED_FRONTEND_WITHOUT_CLOSED_RECEIPT_RETAIN_CLAIM')
  ip=Path(ctx['root'])/'control/qualification_ledger'/(c+'.INTENT.json')
  if not ip.exists():return False
  intent=rd(ip);need(sha(ip)==row['intent_sha256']and intent['uuid']==row['uuid'],'REAL_CONSUMED_INTENT_PHASE')
  pp=Path(intent['output'])/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
  if not pp.exists():return False
  pid=rd(pp);spec=ctx['e'].spec_for(c)
  need(type(pid['pid'])is int and pid['pid']>0 and type(pid['start_ticks'])is int and pid['start_ticks']>0,
       'REAL_NATIVE_PID_START_PHASE')
  need(pid['oracle_execution_binding']==intent['oracle_execution_binding']
       and spec['native_simulator_argv'][0]in pid['maps'],'REAL_NATIVE_MAPS_BINDING_PHASE')
 return True

def cleanup_unused_claims(state,running,post,reviews,on_error):
 busy={ctx['request']+':'+c for ctx,c in list(running.values())+list(post.values())+list(reviews.values())}
 by_request={ctx['request']:ctx for ctx in state['contexts'].values()}
 with state['lock']:
  for key,claim in list(state['claims'].items()):
   if key in busy or claim['request']==REQUEST8:continue # adopted32 uses stronger reconciliation
   try:
    ctx=by_request[claim['request']];c=claim['cohort'];q=ctx['e'].registered()[2]
    if c in q['consumed']:
     if not q['consumed'][c].get('execution_receipt'):continue
     closed_receipt(ctx,c)
    else:unused_identity(ctx,c)
    state['claims'].pop(key);state['B_reservation_sync_pending']=True
   except BaseException as error:on_error(error)
 if state.get('B_reservation_sync_pending'):
  try:state['saveclaims']()
  except BaseException as error:on_error(error)

def adoption_claims(q,old_claims,specs,bindings,inspect):
 """Pure projection; unknown/live consumed work cannot vanish at handoff."""
 need(q['request']==REQUEST8 and q['budget']==32 and q['remaining']==0
      and len(q['consumed'])==32,'EXACT_ORIGINAL32_ALREADY_CONSUMED_REQUIRED')
 claims={};proofs={}
 for c,row in q['consumed'].items():
  spec=specs[c];binding=bindings[c];proof=inspect(c,row);proofs[c]=proof
  need(spec['cohort']==c and binding['cohort']==c and type(binding['host_cpu'])is int,'EXACT_DISPATCH_BINDING')
  spec_sha=hashlib.sha256(encoded(spec)).hexdigest()
  need(q['admitted_specs'][c]==spec_sha==binding['canonical_spec_sha256'], 'ADOPTED_CANONICAL_SPEC_PIN')
  need(binding['resolved_spec_sha256']==hashlib.sha256(encoded(dict(spec,host_cpu=binding['host_cpu']))).hexdigest(),
       'ADOPTED_RESOLVED_CPU_BINDING_PIN')
  need(proof['uuid']==row['uuid'],'ADOPTION_UUID')
  if proof['state']=='EXACT_CLOSED_NONLIVE_RETAIN_ARCHIVE_BACKLOG':continue
  need(proof['state']=='LIVE_OR_UNCERTAIN_RETAIN_CLAIM','UNKNOWN_ADOPTION_CLASS')
  old=old_claims.get(c,{})
  if old:
   need(old['cohort']==c and old['host_cpu']==binding['host_cpu']
        and old.get('uuid')in[None,row['uuid']], 'PRIOR_CLAIM_IDENTITY_CONFLICT')
  cap=spec['limits']['max_process_tree_rss_bytes']
  claims[REQUEST8+':'+c]=dict(request=REQUEST8,execution_root=str(BASE/'initial8'),cohort=c,
      uuid=row['uuid'],host_cpu=binding['host_cpu'],workload=spec['workload'],
      predicted_peak_RAM_bytes=max(old.get('predicted_peak_RAM_bytes',cap),proof.get('observed_RSS_bytes',0)),
      result_cap_bytes=spec['limits']['max_result_directory_bytes'],RAM_cap_bytes=cap,
      observed_model=proof.get('actual_simulator_live',False),
      adopted_existing_consumed_generation=True,adoption_classification=proof['state'])
 return claims,proofs

def derive_ops_source(source):
 """Every delta is one exact anchor; all other 29a source bytes stay unchanged."""
 need(hashlib.sha256(source.encode()).hexdigest()==OLD_OPS_SHA,'EXACT_29A_DISPATCHER_SOURCE_REQUIRED')
 replacements=[
  ("MARKER='DTC_CONTROLLED_ORACLE_SHARED_POOL_V1'","MARKER='"+MARKER+"'"),
  ("for ctx in state['contexts'].values():sync_stage_reservation(ctx,{v['cohort']:v for v in state['claims'].values()if v['request']==ctx['request']})",
   "for ctx in state['contexts'].values():\n    if ctx['plan']['stage']=='remaining24':sync_stage_reservation(ctx,{v['cohort']:v for v in state['claims'].values()if v['request']==ctx['request']})"),
  ("with(BASE/'control/SHARED_DISPATCH_OWNER.lock').open('a+b')as held:",
   "with _B_inherited_shared_scope(state)as held:"),
  ("fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);put(BASE/'control/SHARED_DISPATCH_STARTED.json',dict(UTC=stamp(),pid=os.getpid(),start_ticks=977758783,thread_ident=threading.get_ident(),CPU_allowance=sorted(mask),single_dispatcher=True),True);saveclaims()",
   "_B_verify_shared_scope(state,held);put(_B_generation_root/'DISPATCH_STARTED.fixed.json',dict(UTC=stamp(),pid=os.getpid(),start_ticks=977758783,thread_ident=threading.get_ident(),CPU_allowance=sorted(mask),single_dispatcher=True,truthful_new_owner_image_generation=_B_generation),True);saveclaims()"),
  ("with state['lock']:contexts=list(state['contexts'].values())\n    for ctx in contexts:ctx['e'].assert_parent_lease()",
   "with state['lock']:contexts=list(state['contexts'].values())\n    _B_reconcile_inherited_claims(state,contexts)\n    for ctx in contexts:ctx['e'].assert_parent_lease()"),
  ("with state['lock']:state['claims'].pop(key(ctx,c),None);saveclaims()\n      post[archives.submit(ctx['consumer'].safe_finish,c)]=(ctx,c)",
   "with state['lock']:state['claims'].pop(key(ctx,c),None);saveclaims()\n      post[archives.submit(ctx['consumer'].safe_finish,c)]=(ctx,c)")
 ]
 # The last identity anchor documents the intentionally unchanged model-close
 # transition. It is not counted as a semantic delta.
 changed=source;counts=[]
 for old,new in replacements:
  need(changed.count(old)==1,'DISPATCH_TRANSFORMATION_ANCHOR_COUNT')
  changed=changed.replace(old,new,1);counts.append(dict(anchor_sha256=hashlib.sha256(old.encode()).hexdigest(),count=1,semantic_delta=old!=new))
 # Serialize the original independent CPU review subprocess with the separate
 # pre-B review watch, using the same real inherited child-held job OFD.
 import ast
 tree=ast.parse(changed)
 review=next(x for x in ast.walk(tree)if isinstance(x,ast.FunctionDef)and x.name=='review')
 lines=changed.splitlines(keepends=True);old=''.join(lines[review.lineno-1:review.end_lineno])
 body=''.join(' '+x for x in lines[review.lineno:review.end_lineno])
 need(body.count('timeout=1800)')==1,'EXACT_REVIEW_SUBPROCESS_ANCHOR')
 body=body.replace('timeout=1800)','timeout=1800,pass_fds=(_B_review_held.fileno(),))',1)
 new=lines[review.lineno-1]+"  with _B_review_scope()as _B_review_held:\n"+body
 need(changed.count(old)==1,'EXACT_REVIEW_FUNCTION_ANCHOR')
 changed=changed.replace(old,new,1)
 counts.append(dict(anchor_sha256=hashlib.sha256(old.encode()).hexdigest(),count=1,semantic_delta=True,
                    purpose='Shared CPU-review-only job lock; no model semantics change'))
 def replace_once(old,new,purpose):
  nonlocal changed
  need(changed.count(old)==1,'RECOVERY_BEHAVIOR_EXACT_ANCHOR:'+purpose)
  changed=changed.replace(old,new,1);counts.append(dict(anchor_sha256=hashlib.sha256(old.encode()).hexdigest(),count=1,semantic_delta=True,purpose=purpose))
 replace_once(" def saveclaims():\n  with state['lock']:"," def saveclaims():\n  state['B_reservation_sync_pending']=True\n  with state['lock']:", 'Mark reservation sync pending before any control writes')
 anchor="if ctx['plan']['stage']=='remaining24':sync_stage_reservation(ctx,{v['cohort']:v for v in state['claims'].values()if v['request']==ctx['request']})"
 replace_once(anchor,anchor+"\n  state['B_reservation_sync_pending']=False",'Clear pending only after successful new96 qsync')
 replace_once("truthful_new_owner_image_generation=_B_generation),True);saveclaims()",
              "truthful_new_owner_image_generation=_B_generation),True);state['B_reservation_sync_pending']=True",
              'First reservation sync inside guarded cycle, not outside executor lifetime')
 replace_once("value=future.result();running.pop(future);event(ctx,'MODEL_WORKER_RETURN',cohort=c,result=value)",
              "value=_B_harvest(future,running,ctx,c,'MODEL')\n     if value is None:continue\n     event(ctx,'MODEL_WORKER_RETURN',cohort=c,result=value)", 'Harvest model exceptions without losing healthy futures')
 replace_once("value=future.result();post.pop(future);event(ctx,'RESULT_CONSUMED',cohort=c,state=value['state']);saveclaims()",
              "value=_B_harvest(future,post,ctx,c,'POST')\n     if value is None:continue\n     event(ctx,'RESULT_CONSUMED',cohort=c,state=value['state']);saveclaims()",'Harvest postprocess exceptions without executor unwind')
 replace_once("if value['state']=='EXECUTION_CLOSED':\n      with state['lock']:",
              "if value['state']=='EXECUTION_CLOSED':\n      _B_closed_receipt(ctx,c)\n      with state['lock']:",'Only real closed proof may retire model claim')
 replace_once("elif c not in ctx['e'].registered()[2]['consumed']:\n      with state['lock']:",
              "elif c not in ctx['e'].registered()[2]['consumed']:\n      _B_unused_identity(ctx,c)\n      with state['lock']:",'Never release uncertain intent on worker error')
 replace_once("for _ in range(min(128,len(mask))-len(running)):",
              "if state.get('B_reservation_sync_pending')or not _B_launch_phase_ready(running):all_pending=[]\n    for _ in range(min(1,max(0,min(128,len(mask))-len(running)))):",
              'One admission per cycle; real consumed PID/maps launch phase barrier')
 replace_once("ctx,spec=next((k,s)for k,s in all_pending if s['cohort']==decision['cohort']);c=spec['cohort'];fresh=ctx['res'].resources(spec,True)",
              "ctx,spec=next((k,s)for k,s in all_pending if s['cohort']==decision['cohort']);c=spec['cohort'];fresh=_B_resource(ctx,spec,False)\n     if fresh is None:continue",
              'Typed preclaim resource hold is defer, not pool unwind')
 replace_once("charged=ctx['res'].resources(spec,True)",
              "charged=_B_resource(ctx,spec,True)\n     if charged is None:\n      _B_unused_identity(ctx,c)\n      with state['lock']:state['claims'].pop(key(ctx,c),None);saveclaims()\n      continue",
              'Typed postclaim hold cleans only proved-unused claim and resynchronizes')
 replace_once("if not all(charged[k]for k in ['physical_RAM_pass','physical_disk_pass','admission_disk_pass','admission_pressure_pass']):\n      with state['lock']:",
              "if not all(charged[k]for k in ['physical_RAM_pass','physical_disk_pass','admission_disk_pass','admission_pressure_pass']):\n      _B_unused_identity(ctx,c)\n      with state['lock']:", 'Postclaim false admission cannot erase consumed/uncertain identity')
 replace_once("running[workers.submit(work,ctx,c)]=(ctx,c)",
              "_B_unused_identity(ctx,c);running[workers.submit(work,ctx,c)]=(ctx,c)",'Final unused identity check before real frontend submission')
 replace_once("if not(BASE/'control/ENGINEERING_PAUSE_NEW.json').exists()and not(BASE/'control/POOL_STOP_NEW.json').exists():",
              "if not state.get('B_admission_paused_in_memory')and not(BASE/'control/ENGINEERING_PAUSE_NEW.json').exists()and not(BASE/'control/POOL_STOP_NEW.json').exists():",
              'In-memory failclosed latch gates candidate admission even when pause-file logging fails')
 replace_once("if not all_pending or(BASE/'control/ENGINEERING_PAUSE_NEW.json').exists()or(BASE/'control/POOL_STOP_NEW.json').exists():break",
              "if state.get('B_admission_paused_in_memory')or not all_pending or(BASE/'control/ENGINEERING_PAUSE_NEW.json').exists()or(BASE/'control/POOL_STOP_NEW.json').exists():break",
              'In-memory failclosed latch gates actual submit loop')
 replace_once("with state['lock']:contexts=list(state['contexts'].values())\n    _B_reconcile_inherited_claims(state,contexts)",
              "with state['lock']:contexts=list(state['contexts'].values())\n    _B_refresh_RSS_history(state,contexts)\n    _B_reconcile_inherited_claims(state,contexts)",
              'Capture closed exact-input RSS snapshot outside registry EX and before admission')
 replace_once("decision=first['res'].choose_dispatch([s for _,s in all_pending],sample,state['claims'],policy=rd(first['root']/'control/RESOURCE_POLICY.json'),dispatch_index=dispatch_index)",
              "decision=_B_choose_with_RSS_history(first['res'],[s for _,s in all_pending],sample,state['claims'],policy=rd(first['root']/'control/RESOURCE_POLICY.json'),dispatch_index=dispatch_index)",
              'Picker consumes the same immutable snapshot as fresh and claimed forecast')
 replace_once("observed_model=False);saveclaims()", "observed_model=False,RSS_history_snapshot_sha256=decision['RSS_history_snapshot_sha256']);saveclaims()",
              'Actual RAM claim records exact history snapshot provenance')
 lines=changed.splitlines();wi=next(i for i,l in enumerate(lines)if l=='   while True:')
 # Only this function's top scheduler cycle is protected; normal terminal return
 # still exits after all work, never on routine HOLD. No private flags reset.
 end=next((i for i in range(wi+1,len(lines))if lines[i]and not lines[i].startswith(' ')),len(lines))
 body=lines[wi+1:end]
 lines=lines[:wi+1]+['    try:',"     _B_cleanup(running,post,reviews)"]+[' '+l for l in body]+[
  '    except BaseException as cycle_error:', '     _B_cycle_error(cycle_error)', '     time.sleep(2)']+lines[end:]
 changed='\n'.join(lines)+'\n'
 counts.append(dict(kind='Guard full scheduler cycle: expected typed defer, unexpected no-new pause, retain executors'))
 compile(changed,'<CPU_29A_OWNER_IMAGE_B_DERIVATION>','exec')
 return changed,dict(original_source_sha256=OLD_OPS_SHA,derived_source_sha256=hashlib.sha256(changed.encode()).hexdigest(),anchors=counts,
                     lifecycle_modes_and_resource_admission_original_bytes_preserved=True)

def shared_fd_verify(fd,expected):
 s=os.fstat(fd)
 need((s.st_dev,s.st_ino)==(expected['device'],expected['inode']),'INHERITED_SHARED_OFD_IDENTITY')
 need(os.readlink('/proc/self/fd/'+str(fd))==expected['target'],'INHERITED_SHARED_OFD_TARGET')
 info=Path('/proc/self/fdinfo',str(fd)).read_text()
 need('FLOCK'in info and 'WRITE'in info,'INHERITED_SHARED_EX_LOCK_REQUIRED')
 return dict(fd=fd,device=s.st_dev,inode=s.st_ino,target=expected['target'],lock_observed=True,no_new_open_or_flock=True)

def shared_scope_references(rows,expected_target):
 """Validate every inherited duplicate without creating/relocking an OFD.

    Distinct opens of the same native file cannot each own an exclusive flock.
    Each reference must show the same WRITE flock record, in addition to matching
    native target/device/inode. Thus FD6/7 dup references are not mistaken for
    two competing scopes or silently dropped from the lifetime keeper.
    """
 need(rows and len({x['fd']for x in rows})==len(rows),'UNIQUE_INHERITED_SHARED_REFS_REQUIRED')
 need(all(x['role']=='shared_lock'and x['target']==str(expected_target)for x in rows),
      'ONLY_EXPECTED_INHERITED_SHARED_SCOPE')
 need(len({(x['device'],x['inode'],x['target'])for x in rows})==1,'MULTIPLE_SHARED_LOCK_SCOPES_FORBIDDEN')
 proofs=[];records=[]
 for row in rows:
  proofs.append(shared_fd_verify(row['fd'],row))
  text=Path('/proc/self/fdinfo',str(row['fd'])).read_text()
  locklines=[line.split('FLOCK',1)[1].strip()for line in text.splitlines()if'FLOCK'in line]
  need(len(locklines)==1 and 'WRITE'in locklines[0],'EXACT_ONE_SHARED_EX_FLOCK_PER_REF')
  records.append(locklines[0])
 need(len(set(records))==1,'SHARED_DUP_REFERENCES_MUST_SHOW_SAME_EX_FLOCK')
 selected=min(rows,key=lambda x:x['fd'])
 return dict(selected=selected,all_references=rows,all_reference_proofs=proofs,
             same_exclusive_native_flock_record=records[0],no_open_dup_flock_unlock_or_close=True)

def verify_actual_entry_manifest(entry):
 path=Path(entry['manifest_path'])
 need(sha(path)==entry['manifest_sha256']and rd(path)==entry['manifest'],
      'FRESH_ACTUAL_ENTRY_MANIFEST_FILE_AND_DICT_REQUIRED')
 return dict(path=str(path),sha256=entry['manifest_sha256'],actual_ENTRY_dict_exact=True)

def reviewed_RSS_adapter_path(config,review):
 path=pinned(config['RSS_history_adapter'])
 need(review['RSS_history_adapter_sha256']==config['RSS_history_adapter']['sha256'],
      'RSS_ADAPTER_MUST_BE_THE_INDEPENDENTLY_REVIEWED_SOURCE')
 return path

def load_reviewed_RSS_adapter(config,review):
 # Validation MUST precede any helper exec. Used again immediately at load,
 # not just the earlier real-Main preflight.
 return load(reviewed_RSS_adapter_path(config,review),'B_EXACT_INPUT_CLOSED_RSS_HISTORY')

def fresh_pool_preflight():
 """One pure CPU task in the genuine fresh image, before any registration."""
 import concurrent.futures
 need(not sys.is_finalizing()and not getattr(threading,'_SHUTTING_DOWN',False),
      'FRESH_IMAGE_INTERPRETER_NOT_NORMAL')
 with concurrent.futures.ThreadPoolExecutor(max_workers=1,thread_name_prefix='DTC_B_CPU_PREFLIGHT')as pool:
  result=pool.submit(lambda:dict(pid=os.getpid(),worker_is_main=threading.current_thread()is threading.main_thread(),
                                scientific_model=False)).result(timeout=5)
 need(result['pid']==os.getpid()and result['worker_is_main']is False,'FRESH_IMAGE_CPU_POOL_UNAVAILABLE')
 return dict(status='PURE_CPU_PREFLIGHT_PASS',actual=result,private_flags_written=False)

def transition_projection(once,resolution,ack,journal,outcome,*,once_sha,ack_sha,image_sha,manifest_sha,cmdline_sha,environment_sha,preserve_fds):
 """Pure cross-artifact checks; CPU mocks never confer actual admission."""
 need(resolution['status']=='RESOLVED_BY_FULLY_VALIDATED_NEW_IMAGE_ACK'
      and resolution['once_sha256']==once_sha and resolution['ACK_sha256']==ack_sha,
      'GLOBAL_ONCE_UNRESOLVED_OR_ACK_BINDING')
 need(resolution['release_sha256']==once['release_sha256']
      and resolution['image_source_sha256']==image_sha and resolution['manifest_sha256']==manifest_sha,
      'GLOBAL_ONCE_RELEASE_IMAGE_MANIFEST_BINDING')
 need(once['image_manifest_sha256']==manifest_sha and once['actual_image_PID']==OWNER
      and once['actual_image_start']==START,'ONCE_ACTUAL_OWNER_BINDING')
 need(ack['schema']=='DTC_OWNER_IMAGE_CLOSEOUT_A_STATUS_V1'and ack['phase']=='BOOTSTRAPPED_NO_CLOSURE_ADMISSION_YET'
      and ack['pid']==OWNER and ack['start_ticks']==START and ack['image_source_sha256']==image_sha
      and ack['manifest_sha256']==manifest_sha and ack['entry_threads']==1
      and ack['new_scientific_starts']==ack['registrations']==ack['model_signals']==0,
      'REAL_ZERO_START_NEW_IMAGE_ACK_REQUIRED')
 need(journal['schema']=='DTC_PRODUCTION_NATIVE_RAW_EXEC_JOURNAL_V1'
      and journal['status']=='EXECVE_ACCEPTED_AWAIT_NEW_IMAGE_BOOTSTRAP'
      and journal['owner_pid']==OWNER and journal['owner_start_ticks']==START
      and 'KERNEL_REPLACED_IMAGE_SAME_PID_START'in journal['stages']
      and journal['inferior_C_or_Python_function_calls']==0
      and journal['post_exec_cmdline_sha256']==cmdline_sha
      and journal['environment_sha256']==environment_sha,'FULL_RAW_NATIVE_EXEC_JOURNAL_REQUIRED')
 expected={x['fd']:(x['device'],x['inode'])for x in preserve_fds}
 observed={x['fd']:(x['device'],x['inode'])for x in journal['selected_fd_journal']}
 need(len(observed)==len(journal['selected_fd_journal'])and observed==expected,'EXEC_INHERITED_SELECTED_FD_JOURNAL_BINDING')
 need(all(x['after_FD_flags']==x['before_FD_flags']&~1 for x in journal['selected_fd_journal']),
      'EXEC_CLOEXEC_CLEAR_ONLY_NO_LOCK_REPLACEMENT')
 need(outcome['status']=='VALIDATED_NEW_OWNER_IMAGE_BOOTSTRAP_ACK'
      and outcome['validated_ACK_sha256']==ack_sha and outcome['image_source_sha256']==image_sha
      and outcome['manifest_sha256']==manifest_sha and outcome['tracer_killed']is False
      and outcome['automatic_retry']is False,'VALIDATED_DRIVER_OUTCOME_REQUIRED')
 return dict(status='PASS_BOUND_RAW_EXEC_RESOLUTION_ACK',zero_inferior_function_calls=True)

def transition_preflight(config,entry):
 import re
 need(config['raw_exec_helper']['sha256']==RAW_EXEC_HELPER_SHA,'FIXED_NATIVE_TRANSPORT_SEMANTICS_REQUIRED')
 pinned(config['raw_exec_helper'])
 need(re.search(r'^TracerPid:\s*0$',Path('/proc/self/status').read_text(),re.M), 'OWNER_STILL_TRACED_HOLD')
 once=BASE/'control'/('OWNER_NATIVE_EXEC_'+str(OWNER)+'_'+str(START)+'.ONCE.json')
 resolution=once.with_name(once.name+'.RESOLUTION.json')
 need(once.exists()and resolution.exists(),'GLOBAL_NATIVE_EXEC_ONCE_NOT_FULLY_RESOLVED')
 ackpath=Path(entry['manifest']['image_evidence_root'])/'BOOTSTRAP_ACK.fixed.json'
 journal=rd(pinned(config['raw_native_exec_journal']));outcome=rd(pinned(config['validated_driver_outcome']))
 proof=transition_projection(rd(once),rd(resolution),rd(ackpath),journal,outcome,
    once_sha=sha(once),ack_sha=sha(ackpath),image_sha=entry['manifest']['image']['sha256'],
    manifest_sha=entry['manifest_sha256'],cmdline_sha=hashlib.sha256(Path('/proc/self/cmdline').read_bytes()).hexdigest(),
    environment_sha=hashlib.sha256(Path('/proc/self/environ').read_bytes()).hexdigest(),
    preserve_fds=entry['manifest']['preserve_fds'])
 need(not Path('/proc',str(outcome['tracer_pid'])).exists(),'ORIGINAL_TRANSITION_TRACER_NOT_FULLY_EXITED')
 return dict(proof,once_sha256=sha(once),resolution_sha256=sha(resolution),ACK_sha256=sha(ackpath),
             raw_journal=config['raw_native_exec_journal'],validated_driver_outcome=config['validated_driver_outcome'])

def phase_preflight(config,owner_context):
 need(threading.current_thread()is threading.main_thread(),'REAL_MAIN_THREAD_ONLY')
 need(os.getpid()==OWNER and proc_start(OWNER)==START,'REAL_EXISTING_OWNER_PID_START')
 need(sys.dont_write_bytecode and not sys.is_finalizing()
      and not getattr(threading,'_SHUTTING_DOWN',False),'FRESH_NORMAL_IMAGE_INTERPRETER_REQUIRED')
 main=sys.modules['__main__'];entry=getattr(main,'_ENTRY',None)
 need(entry is not None and Path(main.__file__).resolve()==pinned(config['owner_image']).resolve(),
      'REAL_NEW_IMAGE_MAIN_REQUIRED_NO_OLD_MARKERS')
 verify_actual_entry_manifest(entry)
 need(entry['entry_pid']==OWNER and entry['entry_start']==START and entry['entry_thread_count']==1,
      'REAL_NEW_IMAGE_BOOTSTRAP_ENTRY')
 need(owner_context['owner_pid']==OWNER and owner_context['owner_start_ticks']==START
      and owner_context['Main_thread']is True,'REAL_MANAGEMENT_MAIN_CONTEXT')
 need(not any(t.name=='DTC_OWNER_IMAGE_CLOSEOUT_ONLY'and t.is_alive()for t in threading.enumerate()),
      'A_SOLE_CONSUMER_MUST_QUIESCE_AND_EXIT')
 need(not hasattr(main,MARKER),'B_GENERATION_ALREADY_PRESENT_FORWARD_RECONCILE')
 transition_preflight(config,entry)
 need(not(BASE/'control/ENGINEERING_PAUSE_NEW.json').exists()
      and not(BASE/'control/POOL_STOP_NEW.json').exists(),
      'EXISTING_ADMISSION_PAUSE_REQUIRES_EXPLICIT_FORWARD_RECONCILIATION')
 review=rd(pinned(config['independent_review']))
 need(review['status']=='PASS'and review['scope']=='OWNER_IMAGE_MAIN_OPERATIONAL_EXTENSION'
      and review['subject_source_sha256']==sha(__file__)
      and review['host_image_source_sha256']==sha(main.__file__),'B_INDEPENDENT_LIVE_IMAGE_REVIEW_REQUIRED')
 reviewed_RSS_adapter_path(config,review)
 shared=[x for x in entry['manifest']['preserve_fds']if x['role']=='shared_lock']
 group=shared_scope_references(shared,BASE/'control/SHARED_DISPATCH_OWNER.lock')
 for role in ['owner_lock','qualification_lock']:
  rows=[x for x in entry['manifest']['preserve_fds']if x['role']==role]
  need(len(rows)==1,'REAL_RETAINED_'+role.upper())
  shared_fd_verify(rows[0]['fd'],rows[0])
 fresh_pool_preflight()
 return main,entry,group['selected']

def _prepare_remaining(config,generation_root):
 """CPU artifact finalization from real Gate2; no hidden actual canary."""
 R8=BASE/'initial8';plan=rd(R8/'control/EXECUTION_PLAN.json')
 auto=rd(pinned(plan['extension_automation']))
 for key in ['builder','build_release_template','matrix','final_artifact_qualifier']:pinned(auto[key])
 resources=load(R8/'tools/oracle_resources.py','B_REAL_GATE2_READONLY')
 released=[];states={};witness=[]
 for mode in plan['qualified_modes']:
  try:
   ev=resources.verify_mode_extension_receipt(plan,mode);released.append(mode);states[mode]=dict(status='PASS',evidence=ev);witness.append(ev)
  except resources.WaitInitialRuntimeGate as error:states[mode]=dict(status='WAIT',reason=str(error))
  except (AssertionError,KeyError,OSError,ValueError)as error:states[mode]=dict(status='HOLD',reason=repr(error))
 need(released,'NO_REAL_MODE_PLUS_SHARED_OFF8_GATE2_NO_96_REGISTRATION')
 release=rd(auto['build_release_template']['path'])
 need(set(release['qualified_modes'])==set(plan['qualified_modes'])and len(plan['qualified_modes'])==3,
      'EXACT_FROZEN_Q3_96_NOT_EXPANDED')
 gate=dict(schema='DTC_ORACLE_GATE2_REGISTRATION_RELEASE_V1',status='PASS',released_modes=released,
           mode_releases=states,fixed8_matched_OFF_and_mode_strict_archive_restore_independently_reviewed=True,
           independent_mode_witnesses=witness,all_other_modes_remain_individually_gated=True)
 gp=generation_root/'GATE2_REGISTRATION_RELEASE.fixed.json';put(gp,gate)
 release['Gate2_mode_releases']=states;release['Gate2_release']=dict(path=str(gp),sha256=sha(gp))
 put(generation_root/'REGISTRATION_BUILD_INPUT.FROM_REAL_GATE2.fixed.json',release)
 builder=load(auto['builder']['path'],'B_FROZEN_S6_BUILDER')
 built=builder.build(release,auto['matrix']['path'],'remaining24',phase='final',finalize_draft=True)
 qualifier=load(auto['final_artifact_qualifier']['path'],'B_FROZEN_CPU_FINAL_ARTIFACT_QUALIFIER')
 qualification=getattr(qualifier,auto['final_artifact_qualifier']['function'])(str(BASE/'remaining24'))
 need(qualification['status']=='PASS','FINAL96_CPU_ARTIFACT_QUALIFICATION_HOLD')
 return built,qualification,released

def _reconcile(state,contexts,generation_root):
 """Only retire adopted claims after actual same-UUID closed proof; no signals."""
 ctx=next(c for c in contexts if c['request']==REQUEST8)
 q=ctx['e'].registered()[2]
 need(q['budget']==32 and q['remaining']==0 and set(q['consumed'])==set(state['adopted_original_UUIDs']),
      'ORIGINAL32_IDENTITY_OR_BUDGET_CHANGED')
 for c,u in state['adopted_original_UUIDs'].items():
  need(q['consumed'][c]['uuid']==u,'ORIGINAL32_UUID_CHANGED')
  key=REQUEST8+':'+c
  if key not in state['claims']:continue
  proof=receipt_proof(ctx['root'],c,q['consumed'][c])
  if proof['state']=='EXACT_CLOSED_NONLIVE_RETAIN_ARCHIVE_BACKLOG':
   put(generation_root/'adoption_closed'/(c+'.'+proof['done_sha256']+'.json'),proof)
   with state['lock']:state['claims'].pop(key,None);state['saveclaims']()

def apply(configuration,owner_context):
 """Dormant Main-only actual entry; CPU tests never call this function.

    Root management already checks its exact authorization/config/source. This
    function additionally verifies the real new image, inherited OFDs, Main,
    D-reviewed source and genuine mode+OFF8 Gate2. Any partial scientific mutation
    is forward-only HOLD, never rollback/refund/retry of a model identity.
    """
 config=copy.deepcopy(configuration)
 main,entry,shared=phase_preflight(config,owner_context)
 need(config.get('actual_execution_authorized')is True,'CPU_PREPARATION_NOT_ACTUAL_RELEASE')
 need(config['remaining_budget']==96 and config['old32_new_starts']==0,'EXACT96_ONLY_NO_OLD_RESTART')
 need(config['source_ops']['sha256']==OLD_OPS_SHA and config['S6_addon']['sha256']==S6_SHA,'FROZEN_ENGINEERING_BASE_REQUIRED')
 for key in ['source_ops','S6_addon','alias_hook','sparse_hook','RSS_history_adapter','frozen_matrix']:pinned(config[key])
 need(config['alias_hook']['sha256']==ALIAS_SHA and config['sparse_hook']['sha256']==SPARSE_SHA,'ONLY_FROZEN_POSTPROCESS_HOOKS')
 generation=hashlib.sha256(encoded(dict(owner_image=entry['manifest']['image'],B_source_sha256=sha(__file__),configuration=config))).hexdigest()
 generation_root=BASE/'control/owner_image_B_generations'/generation
 generation_root.mkdir(parents=True,exist_ok=False) # entered once; never blind reapply
 put(generation_root/'BEGIN.fixed.json',dict(schema='DTC_OWNER_IMAGE_B_GENERATION_V1',generation=generation,configuration=config,
     owner_context=owner_context,old_request=REQUEST8,new_request=REQUEST24,old_request_new_scientific_starts=0,
     new_request_maximum_once_only_starts=96,new_generation_source_sha256=sha(__file__),truthful_new_image=entry['manifest']['image']))
 governor=GOV.open('a+b')
 try:
  fcntl.flock(governor,fcntl.LOCK_EX|fcntl.LOCK_NB)
  built,qualification,released=_prepare_remaining(config,generation_root)
  R24=BASE/'remaining24';plan=rd(R24/'control/EXECUTION_PLAN.json');candidate=rd(R24/'control/REGISTRY_REQUEST_CANDIDATE.json')
  s6=load(config['S6_addon']['path'],'B_PURE_S6_REGISTRATION_PROJECTIONS');s6.validate_candidate(candidate,plan)
  need(plan['request']==REQUEST24 and candidate['budget']==96 and candidate['remaining']==96 and candidate['consumed']=={},'EXACT_NEW96_REQUEST')
  engine=load(R24/'tools/oracle_native.py','B_NEW96_SCIENTIFIC_ENGINE')
  reg,epoch=engine.authority();need(REQUEST24 not in reg['registered_future_requests'],'96_REQUEST_ALREADY_EXISTS_FORWARD_RECONCILE')
  oldq=reg['registered_future_requests'][REQUEST8]
  specs={c:rd(BASE/'initial8/control/specs'/(c+'.json'))for c in oldq['consumed']}
  bindings={c:rd(BASE/'initial8/control/dispatch_bindings'/(c+'.json'))for c in oldq['consumed']}
  oldclaims=rd(BASE/'initial8/control/POOL_DISPATCH_RESERVATIONS.json')['claims']
  claims,adoption=adoption_claims(oldq,oldclaims,specs,bindings,lambda c,row:receipt_proof(BASE/'initial8',c,row))
  put(generation_root/'ORIGINAL32_ADOPTION.fixed.json',dict(claims=claims,proofs=adoption,old_request_sha256=hashlib.sha256(encoded(oldq)).hexdigest()))
  resources=load(R24/'tools/oracle_resources.py','B_NEW96_REGISTRATION_RESOURCES')
  evidence=resources.verify_registration_release(plan,candidate)
  text,transformation=derive_ops_source(Path(config['source_ops']['path']).read_text())
  put(generation_root/'OPS_TRANSFORMATION.fixed.json',transformation)
  evidence['actual_operational_owner_generation']=dict(generation=generation,image=entry['manifest']['image'],
       extension_source_sha256=sha(__file__),inherited_shared_OFD=shared_fd_verify(shared['fd'],shared),
       phase='B_ORIGINAL32_ADOPTION_PLUS_NEW96',old32_new_starts=0,
       RSS_history_adapter=config['RSS_history_adapter'],RSS_collection_scope='Outside registry EX before admission; same captured snapshot for picker and claim')
  leasepath=T/'control/BATCH_LEASE.json';lease=rd(leasepath)
  newlease=s6.lease_projection(lease,plan) # append only the genuine new request
  native=N/'bin/native';before=native.read_bytes();block=(R24/'control/NATIVE_ROUTE_BLOCK.sh').read_bytes()
  after=s6.exact_native_route(before,block,'remaining24')
  put(generation_root/'LEASE_BEFORE.fixed.json',lease)
  put(generation_root/'NATIVE_ROUTE_PREIMAGE.fixed.json',dict(path=str(native),sha256=hashlib.sha256(before).hexdigest(),UTF8_bytes=before.decode()))
  for p in [BASE/'control/SHARED_POOL_DISPATCH_RESERVATIONS.json',BASE/'initial8/control/POOL_DISPATCH_RESERVATIONS.json']:
   put(generation_root/(p.name+'.PREIMAGE.json'),dict(path=str(p),sha256=sha(p),value=rd(p)))
  # Pure passed-snapshot mutator: no nested SH/EX or FUSE/authority reads.
  engine.update_authority(lambda current:s6.register_exact_request(current,candidate,plan,evidence))
  put(generation_root/'REGISTERED_NEW96.fixed.json',dict(request=REQUEST24,budget=96,real_Gate2_modes=released))
  need(native.read_bytes()==before and rd(leasepath)==lease,'CONCURRENT_ROUTE_OR_LEASE_CHANGE_FORWARD_HOLD')
  tmp=native.with_name('.native.OWNER_IMAGE_B.writing')
  with tmp.open('xb')as h:h.write(after);h.flush();os.fsync(h.fileno())
  tmp.chmod(native.stat().st_mode&0o777);os.replace(tmp,native);s6.atomic(leasepath,newlease)
  engine.assert_parent_lease();engine.registered()
  ops=types.ModuleType('REAL_OWNER_IMAGE_B_PRIVATE_DISPATCHER');ops.__file__=str(BASE/'initial8/tools/oracle_ops.py')
  exec(compile(text,str(Path(__file__).resolve())+':DERIVED_29A','exec'),ops.__dict__)
  original_load=ops.load;alias=load(config['alias_hook']['path'],'B_EXACT_ALIAS552');sparse=load(config['sparse_hook']['path'],'B_PROVEN_SPARSE_DC00')
  def private_load(name,path):
   module=original_load(name,path)
   if Path(path).name=='oracle_results.py':
    root=Path(path).resolve().parents[1];module=alias.wrap_consumer(module,root);module=sparse.wrap_consumer(module,root)
   return module
  ops.load=private_load
  ops.attach_registered_request(str(BASE/'initial8'))
  state=getattr(main,MARKER);state['claims']=claims;state['adopted_original_UUIDs']={c:r['uuid']for c,r in oldq['consumed'].items()}
  state['generation']=generation;state['governor']=governor;state['shared_inherited_fd']=shared['fd']
  ops.attach_registered_request(str(R24))
  @contextlib.contextmanager
  def inherited_scope(state):
   shared_fd_verify(shared['fd'],shared);yield shared['fd'] # never open/flock/unlock/close it
  ops._B_inherited_shared_scope=inherited_scope
  ops._B_verify_shared_scope=lambda state,fd:shared_fd_verify(fd,shared)
  ops._B_reconcile_inherited_claims=lambda state,contexts:_reconcile(state,contexts,generation_root)
  ops._B_generation_root=generation_root;ops._B_generation=generation
  @contextlib.contextmanager
  def review_scope():
   with(BASE/'control/ORACLE_INDEPENDENT_ACTUAL_REVIEW_JOB.lock').open('a+b')as held:
    fcntl.flock(held,fcntl.LOCK_EX);yield held
  ops._B_review_scope=review_scope
  history=load_reviewed_RSS_adapter(config,rd(pinned(config['independent_review'])))
  frozen_matrix=rd(config['frozen_matrix']['path'])
  need(config['frozen_matrix']['sha256']=='11d5bfc7642a6262fde719119603c940ca64eb98de69d2554124f24b2302a3ee',
       'ORIGINAL_FULL_INPUT_DOMAIN_MATRIX_REQUIRED')
  allowed_inputs={r['input_digest']for r in frozen_matrix['rows']}
  need(len(allowed_inputs)==32,'EXACT_CORE32_INPUT_DOMAIN_FOR_RSS_HISTORY')
  def refresh_RSS_history(state,contexts):
   snapshot=history.capture(contexts,allowed_inputs) # only at top-of-cycle, outside registry EX
   p=generation_root/'RSS_history_snapshots'/(snapshot['snapshot_sha256']+'.json')
   if p.exists():need(rd(p)==snapshot,'CLOSED_RSS_SNAPSHOT_CONFLICT')
   else:put(p,snapshot)
   state['B_exact_RSS_snapshot']=snapshot
   for context in contexts:history.bind_forecast(context['res'],lambda:state.get('B_exact_RSS_snapshot'))
  def choose_with_RSS_history(resource,pending,sample,claims,**kwargs):
   return history.choose(resource,state['B_exact_RSS_snapshot'],pending,sample,claims,**kwargs)
  ops._B_refresh_RSS_history=refresh_RSS_history;ops._B_choose_with_RSS_history=choose_with_RSS_history
  def cycle_error(error):
   typed=resource_hold(error)
   # The in-memory latch precedes all filesystem work. A broken diagnostic
   # directory must never allow a new model or unwind healthy executor pools.
   if not typed:state['B_admission_paused_in_memory']=True
   record=dict(status='EXPECTED_RESOURCE_DEFERRAL'if typed else'UNEXPECTED_ENGINEERING_PAUSE_NEW',error=repr(error),healthy_workers_not_signaled=True)
   try:put(generation_root/(str(time.time_ns())+'.CYCLE_ERROR.json'),record)
   except BaseException as logging_error:
    state['B_diagnostic_IO_errors']=state.get('B_diagnostic_IO_errors',0)+1
    state['B_last_diagnostic_IO_error']=repr(logging_error)
   if not typed:
    pause=BASE/'control/ENGINEERING_PAUSE_NEW.json'
    try:
     if not pause.exists():put(pause,dict(reason='OWNER_IMAGE_B_UNEXPECTED_ENGINEERING',generation=generation,error=repr(error),model_retries=0,healthy_model_signals=0))
    except BaseException as logging_error:
     state['B_diagnostic_IO_errors']=state.get('B_diagnostic_IO_errors',0)+1
     state['B_last_diagnostic_IO_error']=repr(logging_error)
  def fresh(ctx,spec,postclaim):
   try:return ctx['res'].resources(spec,True)
   except BaseException as error:
    if not resource_hold(error):raise
    ctx['cool'][spec['cohort']]=time.monotonic()+30
    put(generation_root/(str(time.time_ns())+'.RESOURCE_DEFER.json'),dict(cohort=spec['cohort'],postclaim=postclaim,error=repr(error)))
    return None
  def harvest(future,mapping,ctx,c,kind):
   try:
    value=future.result();need(isinstance(value,dict)and'state'in value,'FUTURE_RESULT_SCHEMA')
    return value
   except BaseException as error:
    ctx['errors'][c]=dict(reason=kind+'_FUTURE_ENGINEERING',error=repr(error));ctx['cool']['post:'+c]=time.monotonic()+60
    cycle_error(error);return None
   finally:mapping.pop(future,None)
  ops._B_resource=fresh;ops._B_harvest=harvest;ops._B_cycle_error=cycle_error
  ops._B_unused_identity=unused_identity;ops._B_closed_receipt=closed_receipt;ops._B_launch_phase_ready=launch_phase_ready
  ops._B_cleanup=lambda running,post,reviews:cleanup_unused_claims(state,running,post,reviews,cycle_error)
  def run():
   try:ops.run_scheduler()
   except BaseException as error:put(generation_root/'POOL_ERROR_FORWARD_HOLD.fixed.json',dict(error=repr(error),no_model_retries=True))
   finally:governor.close()
  worker=threading.Thread(target=run,name='DTC_OWNER_IMAGE_B_UNIQUE_DISPATCH_POOL',daemon=False)
  state['worker']=worker;state['ops']=ops
  receipt=dict(status='NEW96_REGISTERED_REAL_IMAGE_UNIQUE_POOL_READY',generation=generation,
      request=REQUEST24,budget=96,initial_registration_Gate2_modes=released,all_other_modes_individually_gated=True,
      old32_adopted_unchanged=True,old32_new_starts=0,original_shared_OFD_retained=True,
      sole_archive_workers=1,new_real_generation_marker=MARKER,source_sha256=sha(__file__))
  put(generation_root/'MAIN_ACK.fixed.json',receipt);worker.start();return receipt
 except BaseException:
  governor.close();raise # entered generation retained; Root forward reconciliation only

if __name__=='__main__':print(json.dumps(dict(status='CPU_PREPARATION_ONLY',actual_register_models=False)))
