"""CPU-only fakeRoot safety cases plus six real read-only terminal replays."""
import pathlib,json,hashlib,importlib.util,tempfile,types,copy,gzip,ast,datetime
P=pathlib.Path;O=P('/root/data/dtc_failure_repair_20261025_v1/ops');R=O.parent/'validation';C=O/'repair_metadata_consumer_v2.py'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_text(json.dumps(v))
def load():
 s=importlib.util.spec_from_file_location('consumer_cpu_instance',C);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
checks=[]
def check(name,fn):fn();checks.append({'case':name,'PASS':True})
def reject(fn):
 try:fn()
 except (AssertionError,KeyError,FileNotFoundError):return
 raise AssertionError('negative incorrectly accepted')
tree=ast.parse(C.read_text());calls=[ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n,ast.Call)]
assert not any(x.endswith(('.run_native','.finish_cell','.prepare','.assert_parent_lease','.run','.Popen','.kill','.killpg','.system','.execv')) for x in calls)
checks.append({'case':'AST_no_native_start_subprocess_signal_or_parent_lease_API','PASS':True})
with tempfile.TemporaryDirectory(prefix='repair_v2_metadata_cpu_') as td:
 m=load();m.R=P(td)/'R';m.O=P(td)/'ops';m.BINDING=m.O/'binding.json';m.O.mkdir();cell='E2-AEREPAIR-SENT-cpu-BASE-V1';uid='fake-only-uuid';out=m.R/'DTC/run/results'/uid;out.mkdir(parents=True)
 ip=m.R/'control/qualification_ledger'/(cell+'.INTENT.json');dp=ip.with_name(cell+'.DONE.json');rp=m.R/'analysis'/(cell+'.RESULT.json')
 intent={'uuid':uid,'output':str(out)};done={'uuid':uid,'stop_reason':None,'launcher_wait_returncode':0};put(ip,intent);put(dp,done);put(out/'NATIVE_EXIT.json',done);put(rp,{'state':'ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','cohort':cell})
 q={'admitted_specs':{cell:'fake'},'consumed':{cell:{'uuid':uid,'intent_sha256':sha(ip),'execution_receipt':done}}};spec={'validation_kind':'COMPONENT_SENTINEL_NOT_FORMAL'}
 engine=types.SimpleNamespace(registered=lambda:(None,None,q,None),spec_for=lambda c:spec)
 proof={'uuid':uid,'accepted_cycles':None,'correctness_validation_passed':True,'registered_v1_sentinel_population_unmodified_PASS':False};strict=types.SimpleNamespace(terminal=lambda c:copy.deepcopy(proof));events=[]
 receipt={'cohort':cell,'status':'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'};archive={'receipt':receipt,'independently_verified_restored_entries':1}
 ap=m.R/'control'/(cell+'_ARCHIVE_RECEIPT.json')
 def verify(c):events.append('verify');return copy.deepcopy(archive)
 def archive_fn(c):events.append('archive');put(ap,receipt)
 outbox=types.SimpleNamespace(verify=verify,archive=archive_fn)
 check('ready_requires_three_independent_closure_receipts',lambda: m.ready(cell,engine))
 saved=copy.deepcopy(q['consumed'][cell]);del q['consumed'][cell]['execution_receipt'];assert m.ready(cell,engine) is None;q['consumed'][cell]=saved;checks.append({'case':'missing_execution_receipt_waits_zero_mutation','PASS':True})
 b=rp.read_bytes();rp.unlink();assert m.ready(cell,engine) is None;rp.write_bytes(b);checks.append({'case':'missing_R14_result_waits_zero_mutation','PASS':True})
 b=dp.read_bytes();dp.unlink();assert m.ready(cell,engine) is None;dp.write_bytes(b);checks.append({'case':'missing_DONE_waits_zero_mutation','PASS':True})
 saved=copy.deepcopy(q['consumed'][cell]);q['consumed'][cell]['execution_receipt']={'uuid':'wrong'};check('mismatched_execution_receipt_rejected',lambda:reject(lambda:m.ready(cell,engine)));q['consumed'][cell]=saved
 before={str(p):sha(p) for p in m.R.rglob('*') if p.is_file()};item=m.inspect_point(cell,engine,outbox,strict);assert item['action'].startswith('APPEND_') and not events and before=={str(p):sha(p) for p in m.R.rglob('*') if p.is_file()};checks.append({'case':'sentinel_dryrun_no_out_qualification_copy_or_registry_writes','PASS':True})
 put(ap,receipt);before={str(p):sha(p) for p in m.R.rglob('*') if p.is_file()};item=m.inspect_point(cell,engine,outbox,strict);assert item['action']=='VERIFY_EXISTING_ARCHIVE_ONLY' and events==['verify'] and before=={str(p):sha(p) for p in m.R.rglob('*') if p.is_file()};checks.append({'case':'already_archived_branch_read_only_verify_no_manifest_drift','PASS':True});ap.unlink();events.clear()
 spec.clear();check('ordinary_without_R14_archive_rejected',lambda:reject(lambda:m.inspect_point(cell,engine,outbox,strict)));spec['validation_kind']='COMPONENT_SENTINEL_NOT_FORMAL'
 proof['correctness_validation_passed']=False;check('unqualified_sentinel_rejected',lambda:reject(lambda:m.inspect_point(cell,engine,outbox,strict)));proof['correctness_validation_passed']=True
 # Exercise complete source-mutation/COPY path only inside disposable fakeRoot.
 put(m.BINDING,{'engine_path':'fake-engine','registered_v1_strict_sha256':'frozenV1','reviewer_path':str(C)});oldload=m.load;m.load=lambda name,path:engine if str(path)=='fake-engine' else oldload(name,path)
 result=m.execute_point(cell,engine,outbox,strict);assert result['accepted_cycles'] is None and events==['archive','verify'] and read(rp)['state']=='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS';assert (out/'REPAIR_STRICT_POSTPROCESS_V2.json').exists();assert read(m.R/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json'))['registered_v1_terminal_PASS'] is False;checks.append({'case':'fakeRoot_append_copy_verify_separate_RESULT_preserves_R14_ENGINEERING','PASS':True})
 events.clear();assert m.existing_result(cell,outbox)==result and events==['verify'];checks.append({'case':'completed_V2_resume_reverifies_native_archive_and_proof_hash','PASS':True})
 pp=P(result['proof_path']);original=pp.read_bytes();pp.write_text('{}');check('modified_saved_V2_proof_rejected',lambda:reject(lambda:m.existing_result(cell,outbox)));pp.write_bytes(original)
 # Failed-native evidence never reaches strict terminal or metadata acceptance.
 raw=b'actual stop evidence\n';gzip.open(out/'raw.log.gz','wb').write(raw);failed=dict(done,stop_reason='RESOURCE_MEMORY',launcher_wait_returncode=-15,raw_sha256=sha(out/'raw.log.gz'),raw_uncompressed_sha256=hashlib.sha256(raw).hexdigest(),raw_uncompressed_bytes=len(raw));put(dp,failed);put(out/'NATIVE_EXIT.json',failed);q['consumed'][cell]['execution_receipt']=failed
 count=[0]
 def forbidden(c):count[0]+=1;raise AssertionError('native failure reached success strict')
 strict.terminal=forbidden;item=m.inspect_point(cell,engine,outbox,strict);assert item['failed'] and item['proof']['accepted_cycles'] is None and not item['proof']['correctness_validation_passed'] and count==[0];checks.append({'case':'native_failure_raw_replay_only_never_success_strict_or_cycles','PASS':True})
 ap.unlink();check('native_failure_missing_R14_archive_rejected_no_COPY',lambda:reject(lambda:m.inspect_point(cell,engine,outbox,strict)))
 # Exact closure mutation contract with all 23 fake verified results, peers unchanged.
 cohorts=['fake'+str(i) for i in range(23)];q2={'budget':23,'remaining':0,'consumed':{c:{'uuid':c,'execution_receipt':{'fake':True}} for c in cohorts},'state':'RUNNING','reserved_write_bytes':8724152320,'extra':'muststay'};reg={'registered_future_requests':{m.REQ:q2,'peer':{'immutable':'yes'}}};prior=copy.deepcopy(reg)
 m.existing_result=lambda c,o:{'uuid':c,'failed':c=='fake0'}
 for c in cohorts:put(m.result_path(c),{'fake':c})
 e2=types.SimpleNamespace(registered=lambda:(None,None,q2,None),update_authority=lambda fn:fn(reg));closed=m.close_all({'cohorts':cohorts},e2,outbox)
 assert q2['state']=='CLOSED' and q2['reserved_write_bytes']==1024**3 and q2['validation_status']=='CLOSED_WITH_ARCHIVED_FAILURES' and reg['registered_future_requests']['peer']==prior['registered_future_requests']['peer'] and q2['consumed']==prior['registered_future_requests'][m.REQ]['consumed'] and q2['budget']==23 and q2['remaining']==0 and q2['extra']=='muststay';checks.append({'case':'fake23_closure_only_three_authorized_q_fields_and_1GiB_floor','PASS':True})
# Live readonly qualification; no executing consumer mutation paths here.
m=load();binding=read(m.BINDING);_,engine,outbox,strict=m.bound(False)
cells=['E2-AEREPAIR-SENT-a24dde1bad963516-'+mode+'-V1' for mode in ['LEGACY','BASE','IO','OO','SECTOR']]+['E2-AEREPAIR-1df9d5479504d9c7-DH-V1']
live=[]
for cell in cells:
 ctx=m.ready(cell,engine);assert ctx
 before={str(p):sha(p) for p in ctx['out'].rglob('*') if p.is_file()};qual=R/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json');qp=sha(qual) if qual.exists() else None;old_result_sha=sha(ctx['old_result_path'])
 item=m.inspect_point(cell,engine,outbox,strict)
 assert before=={str(p):sha(p) for p in ctx['out'].rglob('*') if p.is_file()} and old_result_sha==sha(ctx['old_result_path']) and qp==(sha(qual) if qual.exists() else None)
 live.append({'cohort':cell,'uuid':item['uuid'],'action':item['action'],'native_failed':item['failed'],'instructions':item['proof'].get('instructions'),'accepted_cycles':item['proof']['accepted_cycles'],'output_files_and_R14_result_and_science_qualification_unchanged':True,'existing_archive_independent_verification':item['archive']})
result={'schema':'REPAIR_METADATA_CONSUMER_V2_ZERO_MODEL_CPU_AND_READONLY_QUALIFICATION','status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'consumer_path':str(C),'consumer_sha256':sha(C),'binding_sha256':sha(m.BINDING),'qualification_source_path':str(P(__file__).resolve()),'qualification_source_sha256':sha(__file__),'CPU_checks':checks,'live_readonly_cases':live,'scientific_model_starts':0,'scientific_model_retries':0,'live_out_appends':0,'live_COPY164_calls':0,'live_authority_mutations':0,'background_consumer_started':False}
target=O/'METADATA_CONSUMER_V2_CPU_QUALIFICATION.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'readonly_live_points':len(live),'receipt':str(target),'sha256':sha(target)}))
