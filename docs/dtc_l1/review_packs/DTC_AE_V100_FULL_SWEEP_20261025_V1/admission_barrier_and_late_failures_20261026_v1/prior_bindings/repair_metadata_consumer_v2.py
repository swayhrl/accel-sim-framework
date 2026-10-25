"""Finite, metadata-only V2 repair closure. Never starts or retries a model.

Dry-run is read-only. Execution requires a separately published exact-byte
binding plus explicit root activation receipt. Historical R14 results stay intact.
"""
import pathlib,json,hashlib,importlib.util,fcntl,os,time,gzip,copy,datetime,concurrent.futures,argparse
P=pathlib.Path
F=P('/root/data/dtc_failure_repair_20261025_v1'); R=F/'validation'; O=F/'ops'
REQ='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1'
BINDING=O/'POSTPROCESS_V2_CONSUMER_BINDING_V1.json'
ACTIVATION=O/'POSTPROCESS_V2_CONSUMER_ACTIVATION_V1.json'
def read(p): return json.loads(P(p).read_bytes())
def sha(p): return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def put_once(path,value):
 path=P(path);path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists(): assert read(path)==value,('existing V2 proof differs',str(path));return
 with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
def bound(execute=False):
 b=read(BINDING);assert b['schema']=='REPAIR_METADATA_CONSUMER_V2_EXACT_BINDING_V1' and b['request']==REQ and b['finite_budget']==23
 assert b['consumer_path']==str(P(__file__).resolve()) and b['consumer_sha256']==sha(__file__)
 assert b['maximum_metadata_workers']==4 and b['scientific_model_starts']==b['scientific_model_retries']==0
 for item in b['source_pins']:assert sha(item['path'])==item['sha256'],('V2 source pin changed',item['path'])
 for path in b['strict_qualification_paths']:assert read(path)['status']=='PASS'
 engine=load('v2_metadata_engine',b['engine_path']);outbox=load('v2_metadata_outbox',b['outbox_path']);strict=load('v2_metadata_strict',b['reviewer_path'])
 q=engine.registered()[2];assert q['budget']==23 and set(q['admitted_specs'])==set(b['cohorts']) and q['strict_sha256']==b['registered_v1_strict_sha256']
 if execute:
  a=read(ACTIVATION);assert a['schema']=='REPAIR_METADATA_CONSUMER_V2_ROOT_ACTIVATION_V1' and a['execute_metadata_only'] is True and a['request']==REQ
  assert a['binding_sha256']==sha(BINDING) and a['consumer_sha256']==sha(__file__)
  assert sha(a['publication_receipt_path'])==a['publication_receipt_sha256'] and a['publication_commit'] and a['publication_all_bytes_verified'] is True and a['authorization_basis']=='USER_AUTHORIZED_REPAIR_AND_VALIDATION_NO_NEW_STARTS'
  cq=read(a['consumer_qualification_path']);assert sha(a['consumer_qualification_path'])==a['consumer_qualification_sha256'] and cq['status']=='PASS' and cq['consumer_sha256']==sha(__file__) and cq['binding_sha256']==sha(BINDING)
 return b,engine,outbox,strict
def ready(cell,engine):
 q=engine.registered()[2];assert cell in q['admitted_specs']
 ip=R/'control/qualification_ledger'/(cell+'.INTENT.json'); dp=ip.with_name(cell+'.DONE.json');rp=R/'analysis'/(cell+'.RESULT.json')
 row=q['consumed'].get(cell)
 if not dp.exists() or not rp.exists() or not row or 'execution_receipt' not in row:return None
 intent=read(ip);done=read(dp);out=P(intent['output']);old_result=read(rp)
 assert sha(ip)==row['intent_sha256'] and done==row['execution_receipt']==read(out/'NATIVE_EXIT.json')
 assert done['uuid']==intent['uuid']==row['uuid'] and out==R/'DTC/run/results'/row['uuid'] and old_result['cohort']==cell
 assert old_result['state'] in ['PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE','FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY','ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS']
 failed=bool(done['stop_reason'] or done['launcher_wait_returncode'])
 return {'done':done,'intent':intent,'out':out,'old_result':old_result,'old_result_path':str(rp),'old_result_sha256':sha(rp),'DONE_path':str(dp),'DONE_sha256':sha(dp),'failed':failed}
def failed_proof(cell,ctx):
 d=ctx['done'];out=ctx['out'];assert ctx['failed'] and sha(out/'raw.log.gz')==d['raw_sha256'];h=hashlib.sha256();size=0
 with gzip.open(out/'raw.log.gz','rb') as stream:
  for part in iter(lambda:stream.read(1024**2),b''):h.update(part);size+=len(part)
 assert h.hexdigest()==d['raw_uncompressed_sha256'] and size==d['raw_uncompressed_bytes']
 return {'status':'NEW_REPAIR_NATIVE_STOP_UNACCEPTED_ROOT_CAUSE_REQUIRES_REVIEW','cohort':cell,'uuid':d['uuid'],'stop_reason':d['stop_reason'],'returncode':d['launcher_wait_returncode'],'accepted_cycles':None,'performance_accepted':False,'correctness_validation_passed':False,'raw_compressed_sha256':d['raw_sha256'],'raw_uncompressed_sha256':h.hexdigest(),'raw_uncompressed_bytes':size,'model_automatic_retries':0}
def inspect_point(cell,engine,outbox,strict):
 ctx=ready(cell,engine)
 if ctx is None:return {'state':'WAIT_FOR_R14_DONE_EXECUTION_RECEIPT_AND_RESULT','cohort':cell}
 archived=(R/'control'/(cell+'_ARCHIVE_RECEIPT.json')).exists();spec=engine.spec_for(cell)
 proof=failed_proof(cell,ctx) if ctx['failed'] else strict.terminal(cell)
 assert proof['accepted_cycles'] is None and proof['uuid']==ctx['done']['uuid']
 if archived:
  archive=outbox.verify(cell);assert archive['receipt']['cohort']==cell and archive['receipt']['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and archive['independently_verified_restored_entries']>0
  action='VERIFY_EXISTING_ARCHIVE_ONLY'
 else:
  assert not ctx['failed'],'native failure without R14 archive requires independent issue review'
  assert spec.get('validation_kind')=='COMPONENT_SENTINEL_NOT_FORMAL' and 'ENGINEERING' in ctx['old_result']['state']
  assert proof['correctness_validation_passed'] and proof['registered_v1_sentinel_population_unmodified_PASS'] is False
  archive=None;action='APPEND_V2_SENTINEL_PROOF_THEN_STANDARD_COPY164_AND_NATIVE_RESTORE'
 return {'state':'READY_METADATA_ONLY','cohort':cell,'uuid':ctx['done']['uuid'],'failed':ctx['failed'],'proof':proof,'archive':archive,'action':action,'R14_result_path':ctx['old_result_path'],'R14_result_sha256':ctx['old_result_sha256'],'DONE_path':ctx['DONE_path'],'DONE_sha256':ctx['DONE_sha256']}
def result_path(cell):return R/'analysis/postprocess_v2'/(cell+'.POSTPROCESS_V2.RESULT.json')
def existing_result(cell,outbox):
 path=result_path(cell)
 if not path.exists():return None
 result=read(path);assert result['cohort']==cell and result['consumer_sha256']==sha(__file__) and result['binding_sha256']==sha(BINDING)
 assert sha(result['R14_result_path'])==result['R14_result_sha256'] and sha(result['DONE_path'])==result['DONE_sha256']
 proof=read(result['proof_path']);assert sha(result['proof_path'])==result['proof_sha256'] and proof['uuid']==result['uuid'] and proof['accepted_cycles'] is None
 ctx=ready(cell,load('v2_resume_independent_engine',read(BINDING)['engine_path']));assert ctx and ctx['done']['uuid']==result['uuid'] and ctx['failed']==result['failed']
 assert outbox.verify(cell)==result['archive'];return result
def execute_point(cell,engine,outbox,strict):
 folder=R/'analysis/postprocess_v2';folder.mkdir(parents=True,exist_ok=True)
 with (folder/(cell+'.METADATA_CONSUMER.lock')).open('a+b') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  old=existing_result(cell,outbox)
  if old is not None:return old
  item=inspect_point(cell,engine,outbox,strict)
  if item['state']!='READY_METADATA_ONLY':return item
  if item['archive'] is None:
   ctx=ready(cell,engine);assert ctx and not ctx['failed']
   # Take the same closed-copy lock for source mutation; release it before
   # outbox.archive acquires its own descriptor (never recursively flock it).
   cp=R/'control/qualification_ledger'/(cell+'.CLOSED_COPY.lock')
   with cp.open('a+b') as closed:
    fcntl.flock(closed,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (R/'control'/(cell+'_ARCHIVE_RECEIPT.json')).exists()
    proofpath=ctx['out']/'REPAIR_STRICT_POSTPROCESS_V2.json';put_once(proofpath,item['proof'])
    qualification={'status':'REPAIR_CORRECTNESS_VALIDATED_NOT_ORIGINAL_PERFORMANCE','cohort':cell,'uuid':item['uuid'],'strict_sha256':sha(proofpath),'registered_v1_strict_sha256':read(BINDING)['registered_v1_strict_sha256'],'registered_v1_terminal_PASS':False,'postprocess_reviewer_path':read(BINDING)['reviewer_path'],'postprocess_reviewer_sha256':sha(read(BINDING)['reviewer_path']),'consumer_sha256':sha(__file__),'binding_sha256':sha(BINDING),'accepted_cycles':None,'correctness_validation_only':True,'SOURCE_KEEP':True,'original288_untouched':True}
    put_once(R/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json'),qualification)
   started=time.monotonic()
   while not (R/'control'/(cell+'_ARCHIVE_RECEIPT.json')).exists():
    try:outbox.archive(cell)
    except BlockingIOError:
     assert time.monotonic()-started<21600,'finite metadata COPY wait exhausted';time.sleep(10)
   item['archive']=outbox.verify(cell)
  proofpath=folder/(cell+'.POSTPROCESS_V2.PROOF.json');put_once(proofpath,item['proof'])
  result={k:v for k,v in item.items() if k not in ['proof','action','state']}
  result.update(state='FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY' if item['failed'] else 'PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE',consumer_sha256=sha(__file__),binding_sha256=sha(BINDING),proof_path=str(proofpath),proof_sha256=sha(proofpath),accepted_cycles=None,correctness_validation_only=True,original288_untouched=True,registered_R14_result_preserved=True,model_starts=0,model_retries=0)
  put_once(result_path(cell),result);return result
def issue(cell,error):
 folder=R/'analysis/postprocess_v2/issues';folder.mkdir(parents=True,exist_ok=True)
 put_once(folder/(cell+'.'+str(time.time_ns())+'.json'),{'schema':'REPAIR_METADATA_CONSUMER_V2_FAIL_CLOSED_ISSUE','cohort':cell,'error_type':type(error).__name__,'error':str(error),'consumer_sha256':sha(__file__),'model_retries':0,'automatic_retry':False})
def close_all(b,engine,outbox):
 results=[existing_result(c,outbox) for c in b['cohorts']];assert all(results)
 assert len(results)==23 and len({v['uuid'] for v in results})==23
 status='CLOSED_WITH_ARCHIVED_FAILURES' if any(v['failed'] for v in results) else 'ALL_PASS'
 q=engine.registered()[2];assert q['budget']==23 and q['remaining']==0 and set(q['consumed'])==set(b['cohorts'])
 receipt={'schema':'REPAIR_VALIDATION_CLOSED_V2','request':REQ,'validation_status':status,'finite_budget':23,'budget_consumed':23,'consumer_sha256':sha(__file__),'binding_sha256':sha(BINDING),'registered_R14_V1_closure_not_claimed':True,'original288_untouched':True,'model_retries':0,'accepted_cycles':None,'results':[{'cohort':c,'path':str(result_path(c)),'sha256':sha(result_path(c))} for c in b['cohorts']]}
 put_once(R/'control/REPAIR_VALIDATION_CLOSED_V2.json',receipt)
 def mutate(reg):
  q=reg['registered_future_requests'][REQ];before=copy.deepcopy(q)
  assert q['budget']==23 and q['remaining']==0 and set(q['consumed'])==set(b['cohorts']) and all('execution_receipt' in x for x in q['consumed'].values())
  q.update(state='CLOSED',reserved_write_bytes=1024**3,validation_status=status)
  assert {k:v for k,v in q.items() if k not in ['state','reserved_write_bytes','validation_status']}=={k:v for k,v in before.items() if k not in ['state','reserved_write_bytes','validation_status']}
 engine.update_authority(mutate);return receipt
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--workers',type=int,default=4);parser.add_argument('--poll-seconds',type=float,default=10);parser.add_argument('--cells',nargs='*');args=parser.parse_args();assert 1<=args.workers<=4 and 1<=args.poll_seconds<=60
 b,engine,outbox,strict=bound(args.execute);cells=args.cells or b['cohorts'];assert set(cells)<=set(b['cohorts'])
 if not args.execute:
  print(json.dumps([inspect_point(c,engine,outbox,strict) for c in cells],indent=2));return
 assert set(cells)==set(b['cohorts']),'execution is whole finite request only'
 assert not list((R/'analysis/postprocess_v2/issues').glob('*.json')),'prior unexpected issue requires explicit root review; no automatic restart'
 with (O/'POSTPROCESS_V2_CONSUMER_SINGLETON.lock').open('a+b') as singleton:
  fcntl.flock(singleton,fcntl.LOCK_EX|fcntl.LOCK_NB)
  started=time.monotonic()
  with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
   while True:
    bound(True);pending=[c for c in cells if not result_path(c).exists()]
    if not pending:print(json.dumps(close_all(b,engine,outbox)));return
    futures={pool.submit(execute_point,c,engine,outbox,strict):c for c in pending}
    errors=[]
    for future in concurrent.futures.as_completed(futures):
     cell=futures[future]
     try:future.result()
     except BlockingIOError:pass
     except Exception as error:issue(cell,error);errors.append(cell)
    if errors:raise RuntimeError('metadata issues require review; no automatic retry: '+','.join(errors))
    assert time.monotonic()-started<7*86400,'finite metadata wait expired'
    time.sleep(args.poll_seconds)
if __name__=='__main__':main()
