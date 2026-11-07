import types
"""Closed-result consumer and matched-population summaries; never starts a model."""
import pathlib,json,hashlib,importlib.util,os,time,math,statistics,datetime
P=pathlib.Path;R=P(__file__).resolve().parents[1]
PASS='PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE'
REUSE='REFERENCE_ACCEPTED_NO_NEW_START'

def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,f):
 p=R/'tools'/f;m=types.ModuleType(n);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def put(p,x,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if exclusive:
  with p.open('x')as h:json.dump(x,h,indent=2,sort_keys=True);h.write('\n');h.flush();os.fsync(h.fileno())
 else:
  tmp=p.with_name(p.name+'.'+str(os.getpid())+'.L2writing')
  tmp.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');tmp.replace(p)

def archive_closed(c):
 o=load('l2_results_archive','oracle_outbox.py');began=time.monotonic()
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
 e=load('l2_finish_engine','oracle_native.py');q=e.registered()[2]
 ip=R/'control/qualification_ledger'/(c+'.INTENT.json');i=read(ip);d=read(ip.with_name(c+'.DONE.json'));out=P(i['output'])
 assert d==q['consumed'][c]['execution_receipt']==read(out/'NATIVE_EXIT.json') and i['uuid']==d['uuid']
 assert q['consumed'][c]['intent_sha256']==sha(ip) and sha(out/'raw.log.gz')==d['raw_sha256']
 failed=bool(d['stop_reason']or d['launcher_wait_returncode']or not d['native_simulator_observed'])
 if failed:
  proof=dict(status='CONTROLLED_ORACLE_NATIVE_NEGATIVE_UNACCEPTED',stop_reason=d['stop_reason'],returncode=d['launcher_wait_returncode'],native_simulator_observed=d['native_simulator_observed'],failure_classification=load('R1_NEGATIVE_LIFECYCLE_CLASSIFIER','oracle_outbox.py').classification(d),accepted_cycles=None,raw_sha256=d['raw_sha256'],raw_uncompressed_sha256=d['raw_uncompressed_sha256'],performance_accepted=False)
 else:
  proof=load('l2_whole_input_strict','oracle_strict.py').terminal(c);p=out/'L2_STRICT.json'
  if p.exists():assert read(p)==proof
  else:put(p,proof,True)
  qual=dict(status='CONTROLLED_ORACLE_NATIVE_TRACE_PERFORMANCE_QUALIFIED',cohort=c,uuid=d['uuid'],strict_sha256=sha(p),performance_scope='CONTROLLED_ORACLE_DH_ONLY_NEVER_ORIGINAL',SOURCE_KEEP=True)
  p=R/'DTC/control'/('SCIENCE_QUALIFICATION_'+c+'.json')
  if p.exists():assert read(p)==qual
  else:put(p,qual,True)
 a=archive_closed(c)
 v=dict(state='FAIL_CONTROLLED_ORACLE_DH_ARCHIVED_NO_RETRY'if failed else PASS,cohort=c,uuid=d['uuid'],cycles=None if failed else proof['cycles'],proof=proof,archive=a,new_contract_only=True,original_or_repair_results_replaced=False,scientific_role='CONTROLLED_ORACLE_AUTHORIZED_DH',validated_union_authorized=False,union_scope='EXACT_REGISTERED_ORACLE_STAGE_ONLY',input_digest=e.spec_for(c)['input_digest'],cell='DH',profile=e.spec_for(c)['profile'],oracle_mode=e.spec_for(c)['oracle_mode'],program=e.spec_for(c)['program'],suite=e.spec_for(c)['suite'],plan_id=e.spec_for(c)['plan_id'],downstream_profile='P0')
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
 if v.get('state')!=PASS:return False
 p=v.get('proof',{})
 return p.get('performance_accepted')is True and type(v.get('cycles'))is int and v['cycles']>0 and p.get('cycles')==v['cycles'] and bool(v.get('archive'))
