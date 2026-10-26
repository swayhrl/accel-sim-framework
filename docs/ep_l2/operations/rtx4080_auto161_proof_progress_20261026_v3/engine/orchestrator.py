#!/usr/bin/env python3
"""Finite exact161 private CPU stage engine. Root approval required for execute."""
import pathlib,sys,os,json,time,uuid,fcntl,subprocess,traceback,signal
sys.dont_write_bytecode=True
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import core as c
MAX_ATTEMPTS=3
_EVENT_CACHE=None
FILES=['core.py','worker.py','orchestrator.py','ALLOWLIST.json','FROZEN_ADMISSIONS.json']
def prepare():
 rows=c.load_scope();ad=[c.admission(r,i)for i,r in enumerate(rows)]
 obj={'schema':'AUTO161_FROZEN_ADMISSIONS_V1','scope_ref':c.file_ref(c.SCOPE),'count':161,'rows':ad}
 p=c.D/'FROZEN_ADMISSIONS.json'
 if p.exists():c.need(c.load(p)==obj,'admissions already differ')
 else:c.save(p,obj,True)
 for name in ['rows','runs','events','inbox']:(c.D/name).mkdir(exist_ok=True)
 for item in ad:
  directory=c.D/'rows'/item['admission_sha256'];directory.mkdir(exist_ok=True)
  if(directory/'ADMISSION.json').exists():c.need(c.load(directory/'ADMISSION.json')==item,'row admission collision')
  else:c.save(directory/'ADMISSION.json',item,True)
  if not(directory/'STATE.json').exists():c.save(directory/'STATE.json',{'schema':'AUTO161_ROW_STATE_V1','queue_id':item['queue_id'],'admission_sha256':item['admission_sha256'],'status':'ADMITTED_NOT_EXECUTED','attempt_count':0,'stage_execution_complete':False,'exact_trace_qualified':False},True)
 return obj
def event(kind,**fields):
 global _EVENT_CACHE
 if _EVENT_CACHE is None:
  files=sorted((c.D/'events').glob('*.json'));previous=None
  for i,p in enumerate(files):
   x=c.load(p);c.need(x['sequence']==i and x['prev_sha256']==previous,'event chain corrupted');previous=c.rawsha(p)
  _EVENT_CACHE=[len(files),previous]
 sequence,previous=_EVENT_CACHE
 obj={'schema':'AUTO161_EVENT_V1','sequence':sequence,'prev_sha256':previous,'kind':kind,'unix':time.time(),**fields}
 p=c.D/'events'/f'{sequence:012d}.json';c.save(p,obj,True);_EVENT_CACHE=[sequence+1,c.rawsha(p)]
def approved():
 p=c.D/'ROOT_APPROVAL.json';a=c.load(p);c.need(a['schema']=='AUTO161_ROOT_APPROVAL_V1'and a['status']=='APPROVED_PRIVATE_CPU_ONLY_EXACT161','Root approval absent')
 c.need(a['scope_sha256']==c.SCOPE_SHA and a['root_acceptance_sha256']==c.ROOT_ACCEPT_SHA,'approval scope')
 c.need(a['max_workers']==2 and a['max_attempts_per_fingerprint']==MAX_ATTEMPTS,'approval resource limits')
 for f in FILES:c.need(c.rawsha(c.D/f)==a['pins'][f],'code/config pin changed '+f)
 c.need(c.rawsha(c.ROOT_ACCEPT)==c.ROOT_ACCEPT_SHA,'Root acceptance changed')
 reg=c.load(c.D/'ALLOWLIST.json');m=reg['metadata_adapter']
 c.need(m['profile']=='AUTO161_READONLY_CPU_METADATA_V1','metadata profile')
 c.secure_file(m['path']);c.need(c.rawsha(m['path'])==m['sha256'],'adapter changed')
 return a,reg
def artifacts(row,reg):
 p=c.D/'inbox/INDEX.json'
 if not p.exists():return [],[],None
 index=c.load(p);c.need(index['schema']=='AUTO161_ARTIFACT_INDEX_V1'and isinstance(index['artifacts'],list)and len(index['artifacts'])<=1024,'artifact index schema')
 refs=index['artifacts'];bysha={}
 for ref in refs:
  f=c.verify_ref(ref);a=c.load(f);c.need(a['schema']=='AUTO161_ARTIFACT_V1','artifact schema')
  producer=reg.get('artifact_producers',{}).get(a['producer_id']);c.need(producer is not None,'unapproved artifact producer')
  c.need(a['profile']==producer['profile']and a['producer_source_sha256']==producer['source_sha256'],'artifact producer/profile mismatch')
  c.need(c.rawsha(producer['source_path'])==producer['source_sha256'],'artifact producer source drift')
  c.need(a.get('qualification_granted')is False and a.get('gpu_executed')is False and a.get('historical_queue_mutated')is False,'artifact overclaim')
  c.need(a['status']in ['PASS','HOLD']and a['next_stage']in producer['allowed_next_stages']and a['next_stage']in c.WAIT,'artifact stage')
  for e in a['evidence']:c.verify_ref(e)
  c.need(a['evidence']and set(a['provided_gates'])<=set(producer['allowed_gates']),'artifact evidence/gates')
  c.need(ref['sha256']not in bysha,'duplicate artifact digest');bysha[ref['sha256']]=(ref,a)
 relevant=[]
 for ref,a in bysha.values():
  targets=a.get('target_queue_ids',[]);families=a.get('family_keys',[])
  if row['queue_id']in targets or set(families)&set(row.get('profile_families_nonexclusive',[])):relevant.append((ref,a))
 # Reject cycles; missing dependency remains a real wait and cannot unlock a stage.
 def walk(h,stack):
  c.need(h not in stack,'artifact dependency cycle')
  if h not in bysha:return
  for q in bysha[h][1].get('requires',[]):walk(q,stack|{h})
 for h in bysha:walk(h,set())
 ready=[];missing=[];next_state=None
 for ref,a in relevant:
  deps=a.get('requires',[])
  def unresolved(h):
   if h not in bysha or bysha[h][1]['status']!='PASS':return [h]
   return [z for q in bysha[h][1].get('requires',[])for z in unresolved(q)]
  absent=[z for x in deps for z in unresolved(x)]
  if absent:missing.extend(absent);continue
  ready.append(ref)
  if a['status']=='PASS':
   binding=a.get('row_bindings',{}).get(row['queue_id'])
   if a['next_stage'].startswith('WAIT_ROOT_GPU'):c.need(binding==c.digest(row),'GPU-admission wait requires exact row static binding')
   if binding==c.digest(row):next_state=a['next_stage']
 # V3 derives progress from exact proved CPU gates, never last-writer hints.
 if reg['metadata_adapter']['id']=='auto161_metadata_identity_static_v3':next_state=None
 return sorted(ready,key=lambda x:x['sha256']),sorted(set(missing)),next_state
def statepath(ad):return c.D/'rows'/ad['admission_sha256']/'STATE.json'
def all_attempts(ad):
 return sorted((c.D/'runs').glob('*/rows/'+ad['admission_sha256']+'/attempts/*'))
def execution_accept(attempt,ctx):
 ep=attempt/'EXECUTION.json';sp=attempt/'PROCESS_START.json';rp=attempt/'RESULT.json'
 e=c.load(ep);s=c.load(sp);intent=c.load(attempt/'INTENT.json');launch=c.load(attempt/'LAUNCH.json')
 approval=c.load(c.verify_ref(ctx['approval_ref']));allowfile=c.verify_ref(ctx['allowlist_ref']);allow=c.load(allowfile)['metadata_adapter']
 c.need(approval['status']=='APPROVED_PRIVATE_CPU_ONLY_EXACT161'and approval['scope_sha256']==ctx['scope_sha256'],'parent approval binding')
 c.need(c.rawsha(allowfile)==approval['pins']['ALLOWLIST.json'],'parent frozen allowlist binding')
 for key,field in [('adapter_id','id'),('adapter_profile','profile'),('adapter_path','path'),('adapter_source_sha256','sha256')]:c.need(ctx[key]==allow[field],'parent adapter allowlist binding')
 c.need(c.rawsha(ctx['adapter_path'])==ctx['adapter_source_sha256'],'parent reopens adapter source')

 for who in ['worker','parent']:
  for key in ['pid','start_ticks','boot_id']:c.need(e[who][key]==launch[who][key],'launch/execution identity '+who+key)
 c.need(s['context_ref']==intent['context_ref']==c.file_ref(attempt/'CONTEXT.json'),'START context binding')
 c.need(intent['adapter_id']==ctx['adapter_id']and intent['adapter_profile']==ctx['adapter_profile'],'intent adapter profile')
 for k in ['attempt_id','nonce']:c.need(e[k]==s[k]==ctx[k],'execution binding '+k)
 for k in ['worker','parent','slot_id','started_monotonic_ns','adapter_source_sha256','runner_source_sha256']:c.need(e[k]==s[k],'execution/start identity '+k)
 c.need(e['slot_id']==ctx['slot_id']and e['adapter_source_sha256']==ctx['adapter_source_sha256'],'execution slot/adapter')
 c.need(e['runner_source_sha256']==intent['runner_source_sha256']==c.rawsha(c.D/'worker.py'),'execution runner')
 c.need(e['returncode']==0 and e['ended_monotonic_ns']>e['started_monotonic_ns'],'worker exit/time')
 c.need(e['cpu_user_seconds']>=0 and e['cpu_system_seconds']>=0,'CPU accounting')
 c.need(e['worker']['boot_id']==e['parent']['boot_id'],'worker parent boot')
 c.need(e['result_ref']==c.file_ref(rp),'execution result not bound')
 c.check_result(c.load(rp),ctx,c.file_ref(attempt/'CONTEXT.json'))
 return e,s,c.load(rp)
def ack_attempt(attempt,ctx,artifact_next=None):
 e,s,r=execution_accept(attempt,ctx)
 next_state=artifact_next if artifact_next and r['status']!='FAILED'and all(x['passed']for x in r['checks'])else r['next_stage']
 c.need(next_state in c.WAIT,'invalid next state')
 obj={'schema':'AUTO161_ACK_V1','attempt_id':ctx['attempt_id'],'queue_id':ctx['queue_id'],'admission_sha256':ctx['admission_sha256'],'input_fingerprint':ctx['input_fingerprint'],'stage':c.STAGE,'accepted_result_status':r['status'],'next_stage':next_state,'execution_ref':c.file_ref(attempt/'EXECUTION.json'),'process_start_ref':c.file_ref(attempt/'PROCESS_START.json'),'result_ref':c.file_ref(attempt/'RESULT.json'),'intent_ref':c.file_ref(attempt/'INTENT.json'),'context_ref':c.file_ref(attempt/'CONTEXT.json'),'stdout_ref':c.file_ref(attempt/'stdout.log'),'stderr_ref':c.file_ref(attempt/'stderr.log'),'worker':e['worker'],'parent':e['parent'],'slot_id':e['slot_id'],'started_monotonic_ns':e['started_monotonic_ns'],'ended_monotonic_ns':e['ended_monotonic_ns'],'qualification_granted':False,'exact_trace_qualified':False,'ack_unix':time.time()}
 p=attempt/'ACK.json'
 if p.exists():
  old=c.load(p)
  for k in obj:
   if k!='ack_unix':c.need(old[k]==obj[k],'ACK collision')
 else:c.save(p,obj,True);event('ACK_REOPEN_VERIFIED',attempt_id=ctx['attempt_id'],queue_id=ctx['queue_id'],ack_ref=c.file_ref(p))
 return c.file_ref(p),obj
def recover(ad,fp):
 accepted=[];attempts=[]
 for p in all_attempts(ad):
  if not (p/'INTENT.json').exists():continue
  intent=c.load(p/'INTENT.json');ctx=c.load(p/'CONTEXT.json')
  c.need(intent['context_ref']==c.file_ref(p/'CONTEXT.json')and ctx['admission_sha256']==ad['admission_sha256'],'recovery intent/context')
  if (p/'PROCESS_START.json').exists()and c.live(c.load(p/'PROCESS_START.json')['worker']):return None,len(attempts),'LIVE_PRIVATE_WORKER'
  if ctx['input_fingerprint']!=fp:continue
  attempts.append(p)
  if (p/'ACK.json').exists():
   a=c.load(p/'ACK.json');execution_accept(p,ctx)
   for k in ['attempt_id','queue_id','admission_sha256','input_fingerprint','stage','slot_id']:c.need(a[k]==ctx[k],'recovered ACK binding '+k)
   c.need(a['next_stage']in c.WAIT,'recovered ACK stage')
   for f in ['execution_ref','process_start_ref','result_ref','intent_ref','context_ref','stdout_ref','stderr_ref']:c.verify_ref(a[f])
   c.need(a['qualification_granted']is False and a['exact_trace_qualified']is False,'recovery ACK overclaim')
   ackref=c.file_ref(p/'ACK.json');events=[c.load(x)for x in(c.D/'events').glob('*.json')];matches=[x for x in events if x['kind']=='ACK_REOPEN_VERIFIED'and x.get('attempt_id')==a['attempt_id']]
   c.need(len(matches)<=1 and all(x['ack_ref']==ackref for x in matches),'ACK event collision')
   if not matches:event('ACK_REOPEN_VERIFIED',attempt_id=a['attempt_id'],queue_id=a['queue_id'],ack_ref=ackref,recovered_missing_event=True)
   accepted.append((ackref,a));continue
  if (p/'EXECUTION.json').exists()and(p/'RESULT.json').exists():
   try:accepted.append(ack_attempt(p,ctx));continue
   except (ValueError,KeyError,OSError):pass
  if (p/'PROCESS_START.json').exists()and c.live(c.load(p/'PROCESS_START.json')['worker']):return None,len(attempts),'LIVE_PRIVATE_WORKER'
  if (p/'LAUNCH.json').exists()and c.live(c.load(p/'LAUNCH.json')['worker']):return None,len(attempts),'LIVE_PRIVATE_WORKER'
 for p in attempts:
  if (p/'ACK.json').exists():continue
  ctx=c.load(p/'CONTEXT.json');proof=c.load(p/'PROCESS_START.json')['worker']if(p/'PROCESS_START.json').exists()else(c.load(p/'LAUNCH.json')['worker']if(p/'LAUNCH.json').exists()else None)
  c.need(not(proof and c.live(proof)),'incomplete worker still live')
  record={'schema':'AUTO161_RECOVERY_CLOSURE_V1','attempt_id':ctx['attempt_id'],'context_ref':c.file_ref(p/'CONTEXT.json'),'process_start_ref':c.file_ref(p/'PROCESS_START.json')if(p/'PROCESS_START.json').exists()else None,'launch_ref':c.file_ref(p/'LAUNCH.json')if(p/'LAUNCH.json').exists()else None,'execution_ref':c.file_ref(p/'EXECUTION.json')if(p/'EXECUTION.json').exists()else None,'worker_proof':proof,'worker_live':False,'closed_monotonic_ns':time.monotonic_ns(),'reason':'DEAD_INCOMPLETE_ATTEMPT_NOT_STAGE_EXECUTED','stage_execution_complete':False}
  if not(p/'RECOVERY_CLOSED.json').exists():
   c.save(p/'RECOVERY_CLOSED.json',record,True)
   if not(p/'FAILURE.json').exists():c.save(p/'FAILURE.json',{'error':'DEAD_INCOMPLETE_ATTEMPT_NOT_STAGE_EXECUTED','retry_allowed':len(attempts)<MAX_ATTEMPTS,'unix':time.time()},True)
   event('RECOVERY_DEAD_INCOMPLETE_CLOSED',attempt_id=ctx['attempt_id'],closure_ref=c.file_ref(p/'RECOVERY_CLOSED.json'))
 c.need(len(accepted)<=1,'duplicate effective ACK for one fingerprint')
 return accepted[0]if accepted else None,len(attempts),None
def run_once():
 a,reg=approved();rows=c.load_scope();frozen=c.load(c.D/'FROZEN_ADMISSIONS.json')
 c.need(frozen['rows']==[c.admission(r,i)for i,r in enumerate(rows)],'admission manifest drift')
 held=(c.D/'ORCHESTRATOR.lock').open('a');fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
 prior_live=[]
 for sp in (c.D/'runs').glob('*/rows/*/attempts/*/PROCESS_START.json'):
  if c.live(c.load(sp)['worker']):prior_live.append(str(sp))
 contexts={str(p)for p in(c.D/'runs').glob('*/rows/*/attempts/*/CONTEXT.json')}
 for proc in pathlib.Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:args=(proc/'cmdline').read_bytes().split(b'\0')
  except (FileNotFoundError,ProcessLookupError):continue
  if any(arg.decode(errors='replace')in contexts for arg in args):
   proof=c.identity(int(proc.name))
   if proof and proof['state']not in ['Z','X']:prior_live.append(proof)
 c.need(not prior_live,'LIVE_PRIVATE_WORKERS_REQUIRE_LATER_RECOVERY: '+repr(prior_live))
 runid='run_'+str(time.time_ns())+'_'+uuid.uuid4().hex[:8];run=c.D/'runs'/runid;run.mkdir(parents=True)
 for source,target in [(c.D/'ROOT_APPROVAL.json',run/'ROOT_APPROVAL_FROZEN.json'),(c.D/'ALLOWLIST.json',run/'ALLOWLIST_FROZEN.json')]:
  with target.open('xb')as out:out.write(source.read_bytes());out.flush();os.fsync(out.fileno())
 c.need(c.load(run/'ROOT_APPROVAL_FROZEN.json')==a and c.rawsha(run/'ALLOWLIST_FROZEN.json')==a['pins']['ALLOWLIST.json'],'approval/config changed while freezing')
 approval_ref=c.file_ref(run/'ROOT_APPROVAL_FROZEN.json');allowlist_ref=c.file_ref(run/'ALLOWLIST_FROZEN.json')
 frozen_pins={};(run/'PINS_FROZEN').mkdir()
 for name in FILES:
  target=run/'PINS_FROZEN'/name
  with target.open('xb')as out:out.write((c.D/name).read_bytes());out.flush();os.fsync(out.fileno())
  c.need(c.rawsha(target)==a['pins'][name],'source/config changed while freezing '+name);frozen_pins[name]=c.file_ref(target)

 parent=c.identity(os.getpid());start=time.monotonic_ns();deadline=start+3600*10**9
 c.save(run/'RUN_IDENTITY.json',{'schema':'AUTO161_RUN_IDENTITY_V1','run_id':runid,'orchestrator':parent,'started_unix':time.time(),'started_monotonic_ns':start,'deadline_monotonic_ns':deadline,'approval_ref':approval_ref,'root_approval_original_ref':c.file_ref(c.D/'ROOT_APPROVAL.json'),'allowlist_ref':allowlist_ref,'pins':a['pins'],'pins_frozen':frozen_pins},True)
 event('FINITE_ROUND_START',run_id=runid)
 todo=[];accepted_count=0;attention=[]
 for i,row in enumerate(rows):
  ad=frozen['rows'][i];deps,missing,artifact_next=artifacts(row,reg);adapter=reg['metadata_adapter']
  fp=c.digest({'admission':ad['admission_sha256'],'stage':c.STAGE,'adapter_sha256':adapter['sha256'],'artifacts':deps,'missing_dependencies':missing})
  prior,count,blocked=recover(ad,fp)
  if prior:
   ref,ack=prior;c.save(statepath(ad),{'schema':'AUTO161_ROW_STATE_V1','queue_id':row['queue_id'],'admission_sha256':ad['admission_sha256'],'status':ack['next_stage'],'attempt_id':ack['attempt_id'],'input_fingerprint':fp,'latest_ack_ref':ref,'attempt_count':count,'stage_execution_complete':True,'exact_trace_qualified':False});accepted_count+=1;continue
  if blocked or count>=MAX_ATTEMPTS:
   reason=blocked or 'RETRY_BUDGET_EXHAUSTED';attention.append({'queue_id':row['queue_id'],'reason':reason});continue
  todo.append((row,ad,fp,deps,missing,artifact_next,count))
 active={};completed=0
 def launch(item,slot):
  row,ad,fp,deps,missing,next_state,count=item
  attemptid=ad['admission_sha256'][:12]+'_'+fp[:12]+'_'+str(count+1);attempt=run/'rows'/ad['admission_sha256']/'attempts'/attemptid;attempt.mkdir(parents=True)
  ctx={'schema':'AUTO161_CONTEXT_V1','attempt_id':attemptid,'nonce':uuid.uuid4().hex,'queue_id':row['queue_id'],'row_index':ad['row_index'],'scope_path':str(c.SCOPE),'scope_sha256':c.SCOPE_SHA,'frozen_row_sha256':ad['frozen_row_sha256'],'admission_sha256':ad['admission_sha256'],'input_fingerprint':fp,'stage':c.STAGE,'adapter_id':adapter['id'],'adapter_profile':adapter['profile'],'adapter_path':adapter['path'],'adapter_source_sha256':adapter['sha256'],'dependency_artifacts':deps,'missing_dependency_sha256':missing,'attempt_directory':str(attempt),'output_path':str(attempt/'RESULT.json'),'slot_id':slot,'approval_ref':approval_ref,'allowlist_ref':allowlist_ref}
  c.save(attempt/'CONTEXT.json',ctx,True)
  intent={'schema':'AUTO161_INTENT_V1','attempt_id':attemptid,'nonce':ctx['nonce'],'queue_id':row['queue_id'],'row_index':ad['row_index'],'admission_sha256':ad['admission_sha256'],'stage':c.STAGE,'input_fingerprint':fp,'adapter_id':adapter['id'],'adapter_profile':adapter['profile'],'adapter_source_sha256':adapter['sha256'],'runner_source_sha256':c.rawsha(c.D/'worker.py'),'slot_id':slot,'context_ref':c.file_ref(attempt/'CONTEXT.json'),'created_unix':time.time()}
  c.save(attempt/'INTENT.json',intent,True)
  out=(attempt/'stdout.log').open('xb');err=(attempt/'stderr.log').open('xb')
  p=subprocess.Popen(['/usr/bin/python3','-B',str(c.D/'worker.py'),str(attempt/'CONTEXT.json')],stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True);out.close();err.close()
  own=c.identity(p.pid);c.need(own is not None,'worker identity disappeared')
  c.save(attempt/'LAUNCH.json',{'worker':own,'parent':parent,'attempt_id':attemptid},True)
  c.save(statepath(ad),{'schema':'AUTO161_ROW_STATE_V1','queue_id':row['queue_id'],'admission_sha256':ad['admission_sha256'],'status':'RUNNING_CPU_GATE','attempt_id':attemptid,'input_fingerprint':fp,'attempt_count':count+1,'exact_trace_qualified':False})
  event('CPU_WORKER_LAUNCHED',run_id=runid,attempt_id=attemptid,queue_id=row['queue_id'],worker=own,slot_id=slot)
  active[slot]={'p':p,'path':attempt,'ctx':ctx,'item':item,'start':time.monotonic()}
 try:
  while todo or active:
   c.need(time.monotonic_ns()<deadline,'finite round deadline')
   for slot in range(2):
    if slot not in active and todo:launch(todo.pop(0),slot)
   for slot,data in list(active.items()):
    p=data['p']
    if p.poll()is None and time.monotonic()-data['start']>90:
     p.terminate()
     try:p.wait(timeout=3)
     except subprocess.TimeoutExpired:p.kill();p.wait()
    if p.poll()is None:continue
    row,ad,fp,deps,missing,next_state,count=data['item']
    try:
     c.need(p.returncode==0,'worker exit '+str(p.returncode));ref,ack=ack_attempt(data['path'],data['ctx'],next_state if not missing else None)
     c.save(statepath(ad),{'schema':'AUTO161_ROW_STATE_V1','queue_id':row['queue_id'],'admission_sha256':ad['admission_sha256'],'status':ack['next_stage'],'attempt_id':ack['attempt_id'],'input_fingerprint':fp,'latest_ack_ref':ref,'attempt_count':count+1,'stage_execution_complete':True,'exact_trace_qualified':False});accepted_count+=1
    except (ValueError,KeyError,OSError)as exc:
     event('ATTEMPT_FAILED_RETAINED',attempt_id=data['ctx']['attempt_id'],queue_id=row['queue_id'],error=repr(exc))
     c.save(data['path']/'FAILURE.json',{'error':repr(exc),'unix':time.time(),'retry_allowed':count+1<MAX_ATTEMPTS},True)
     c.save(statepath(ad),{'schema':'AUTO161_ROW_STATE_V1','queue_id':row['queue_id'],'admission_sha256':ad['admission_sha256'],'status':'FAILED_RETAINED'if count+1<MAX_ATTEMPTS else'RETRY_BUDGET_EXHAUSTED','attempt_id':data['ctx']['attempt_id'],'input_fingerprint':fp,'attempt_count':count+1,'error':repr(exc),'exact_trace_qualified':False})
     if count+1<MAX_ATTEMPTS:todo.append((row,ad,fp,deps,missing,next_state,count+1))
     else:attention.append({'queue_id':row['queue_id'],'reason':repr(exc)})
    completed+=1;del active[slot]
   if active:time.sleep(.05)
 finally:
  for data in active.values():
   p=data['p']
   if p.poll()is None:
    p.terminate()
    try:p.wait(timeout=3)
    except subprocess.TimeoutExpired:p.kill();p.wait()
 summary={'schema':'AUTO161_FINITE_ROUND_SUMMARY_V1','run_id':runid,'frozen_rows':161,'accepted_stage_receipts':accepted_count,'new_attempts_finished':completed,'attention':attention,'exact_trace_qualified':0,'GPU_executions':0,'historical_queue_mutations':0,'status':'FINITE_ROUND_COMPLETE'if accepted_count==161 else'FINITE_ROUND_ATTENTION','finished_unix':time.time()}
 c.save(run/'SUMMARY.json',summary,True);event('FINITE_ROUND_END',run_id=runid,summary_ref=c.file_ref(run/'SUMMARY.json'));print(json.dumps(summary))
def main():
 c.need(sys.argv[1:]in [['--prepare'],['--run-once']],'only --prepare or --run-once')
 if sys.argv[1]=='--prepare':prepare();print('prepared exact161 admissions; no worker executed')
 else:run_once()
if __name__=='__main__':main()
