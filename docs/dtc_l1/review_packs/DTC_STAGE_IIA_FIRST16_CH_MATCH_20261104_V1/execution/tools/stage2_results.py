"""Closed-result consumer and matched-population summaries; never starts a model."""
import pathlib,json,hashlib,importlib.util,os,time,math,statistics,datetime
P=pathlib.Path;R=P('/root/data/dtc_stage_iia_first16_20261104_v1')
PASS='PASS_STAGEII_CH_STRICT_ARCHIVE_NATIVE_RESTORE'
REUSE='REFERENCE_ACCEPTED_NO_NEW_START'

def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,f):
 s=importlib.util.spec_from_file_location(n,R/'tools'/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,x,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if exclusive:
  with p.open('x')as h:json.dump(x,h,indent=2,sort_keys=True);h.write('\n');h.flush();os.fsync(h.fileno())
 else:
  tmp=p.with_name(p.name+'.'+str(os.getpid())+'.L2writing')
  tmp.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');tmp.replace(p)

def archive_closed(c):
 o=load('l2_results_archive','stage2_outbox.py');began=time.monotonic()
 while True:
  if(R/'control'/(c+'_ARCHIVE_RECEIPT.json')).exists():return o.verify(c)
  try:o.archive(c)
  except BlockingIOError:
   assert time.monotonic()-began<21600;time.sleep(10)
  except RuntimeError as x:
   if 'HOLD'not in str(x)or time.monotonic()-began>=21600:raise
   time.sleep(10)

def finish_evidence(c):
 """Postprocess one DONE, preserving raw failures and never resubmitting it."""
 rp=R/'analysis'/(c+'.RESULT.json')
 if rp.exists():return read(rp)
 e=load('l2_finish_engine','stage2_native.py');q=e.registered()[2]
 ip=R/'control/qualification_ledger'/(c+'.INTENT.json');i=read(ip);d=read(ip.with_name(c+'.DONE.json'));out=P(i['output'])
 assert d==q['consumed'][c]['execution_receipt']==read(out/'NATIVE_EXIT.json') and i['uuid']==d['uuid']
 assert q['consumed'][c]['intent_sha256']==sha(ip) and sha(out/'raw.log.gz')==d['raw_sha256']
 failed=bool(d['stop_reason']or d['launcher_wait_returncode'])
 if failed:
  proof=dict(status='L2_MLP_NATIVE_NEGATIVE_UNACCEPTED',stop_reason=d['stop_reason'],returncode=d['launcher_wait_returncode'],accepted_cycles=None,raw_sha256=d['raw_sha256'],performance_accepted=False)
 else:
  proof=load('l2_whole_input_strict','stage2_strict.py').terminal(c);p=out/'L2_STRICT.json'
  if p.exists():assert read(p)==proof
  else:put(p,proof,True)
  qual=dict(status='STAGEII_FIRST16_NATIVE_TRACE_PERFORMANCE_QUALIFIED',cohort=c,uuid=d['uuid'],strict_sha256=sha(p),performance_scope='STAGEII_FIRST16_CH_ONLY_NEVER_ORIGINAL',SOURCE_KEEP=True)
  p=R/'DTC/control'/('SCIENCE_QUALIFICATION_'+c+'.json')
  if p.exists():assert read(p)==qual
  else:put(p,qual,True)
 a=archive_closed(c)
 v=dict(state='FAIL_STAGEII_CH_ARCHIVED_NO_RETRY'if failed else PASS,cohort=c,uuid=d['uuid'],cycles=None if failed else proof['cycles'],proof=proof,archive=a,new_contract_only=True,original_or_repair_results_replaced=False,scientific_role='STAGEII_AUTHORIZED_CH',validated_union_authorized=False,input_digest=e.spec_for(c)['input_digest'],cell='CH',profile=e.spec_for(c)['profile'])
 if rp.exists():assert read(rp)==v
 else:put(rp,v,True)
 return v

def safe_finish(c):
 try:return finish_evidence(c)
 except BaseException as x:
  v=dict(state='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,error=repr(x),model_retries=0,accepted_cycles=None)
  # A distinct engineering event is retained. It is not a performance result and
  # does not prevent a later engineering-only completion of the same raw UUID.
  p=R/'analysis'/(c+'.POSTPROCESS_ENGINEERING.'+str(time.time_ns())+'.json');put(p,v,True);return v

def accepted(v):
 if v.get('state')not in[PASS,REUSE]:return False
 p=v.get('proof',{})
 if p.get('performance_accepted')is not True or type(v.get('cycles'))is not int or v['cycles']<=0:return False
 if v.get('state')==REUSE:
  r=v.get('reuse_verification',{})
  # Main coordinator emits this only after independently checking source strict,
  # natural DONE, archive/native restore, complete option and build equality.
  return all(r.get(k)is True for k in['strict_verified','natural_done_verified','archive_native_restore_verified','complete_effective_options_equal','core_framework_binary_equal','input_scope_equal'])
 return p.get('cycles')==v['cycles'] and bool(v.get('archive'))

