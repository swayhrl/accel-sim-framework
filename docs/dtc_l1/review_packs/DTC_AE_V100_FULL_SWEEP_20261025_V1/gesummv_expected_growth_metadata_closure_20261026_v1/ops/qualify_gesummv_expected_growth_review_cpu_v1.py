"""Independent CPU-only qualification; production access is strictly read-only."""
import copy,hashlib,importlib.util,io,json,pathlib,tempfile,types,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');SRC=F/'ops/review_gesummv_expected_growth_v1.py';s=importlib.util.spec_from_file_location('gesu_review_cpu',SRC);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);checks=[]
def h(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,x):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(m.encoded(x))
def check(name,fn):fn();checks.append({'name':name,'status':'PASS'})
def reject(name,fn):
 try:fn()
 except (RuntimeError,AssertionError,KeyError,OSError):checks.append({'name':name,'status':'PASS'});return
 raise RuntimeError('negative accepted '+name)
baseline=m.review();plan=P(F/'ops/GESUMMV_EXPECTED_GROWTH_READ_ONLY_REVIEW_PLAN_V1.json');check('actual read-only full source/native/receipt/raw/progress/resource review equals frozen plan',lambda:m.require(baseline==m.read(plan),'review drift'))
check('original frozen classifier engineering error preserved and exact missing branch proved',lambda:m.require(m.read(baseline['old_RESULT_path'])['error']=="AssertionError('not a reviewed closed failure signature')" and 'abort or cap' in (m.T/'tools/sweep_failure_review_cap1m.py').read_text(),'wrong engineering cause'))
out=m.T/'DTC/run/results'/m.UUID;immutable={str(p):h(p) for p in [m.T/'control/qualification_ledger'/(m.CELL+'.INTENT.json'),m.T/'control/qualification_ledger'/(m.CELL+'.DONE.json'),out/'NATIVE_EXIT.json',P(baseline['old_RESULT_path'])]};manifest_before=m.load(m.T/'tools/sweep_outbox.py','gesu_cpu_readonly_outbox').manifest_for(m.CELL)
samples=[{'physical_RAM_pass':True,'physical_disk_pass':True} for _ in range(937)]+[copy.deepcopy(baseline['last_failing_sample'])];policies=[{'decision':{'decision':'CONTINUE','stop_reasons':[]}} for _ in range(937)]+[copy.deepcopy(baseline['last_policy_stop'])]
check('exact last disk negative with sole expected_growth and RAM CONTINUE accepted only as UNACCEPTED',lambda:m.validate_samples(samples,policies))
for name,mutation in [('RAM false',lambda a:a[0].update(physical_RAM_pass=False)),('earlier second disk false',lambda a:a[0].update(physical_disk_pass=False)),('no final disk false',lambda a:a[-1].update(physical_disk_pass=True)),('shortfall differs',lambda a:a[-1].update(required_free_bytes=a[-1]['required_free_bytes']+1)),('inodes shortage different cause',lambda a:a[-1].update(free_inodes=1)),('wrong old peer reservation',lambda a:a[-1]['peer_reservations'][0].update(reserved_write_bytes=1))]:
 a=copy.deepcopy(samples);mutation(a);reject(name+' rejected',lambda a=a:m.validate_samples(a,policies))
for name,mutation in [('other STOP reason',lambda a:a[-1]['decision'].update(stop_reasons=['MEMORY_HEADROOM'])),('host domain STOP',lambda a:a[-1]['decision']['domains']['host'].update(decision='STOP')),('earlier STOP',lambda a:a[0]['decision'].update(decision='STOP',stop_reasons=['other'])),('policy population gap',lambda a:a.pop())]:
 a=copy.deepcopy(policies);mutation(a);reject(name+' rejected',lambda a=a:m.validate_samples(samples,a))
savedread=m.read;savedsha=m.sha;savedalive=m.alive;savedgzip=m.gzip.open
def override_read_for(path,edit):
 def altered(p):
  x=savedread(p)
  if P(p)==path:x=copy.deepcopy(x);edit(x)
  return x
 return altered
try:
 m.read=override_read_for(m.T/'control/qualification_ledger'/(m.CELL+'.DONE.json'),lambda x:x.update(uuid='wrong'));reject('wrong DONE UUID rejected before archive',m.review);m.read=savedread
 m.alive=lambda _:True;reject('live exact generation rejected before archive',m.review);m.alive=savedalive
 m.sha=lambda p:'0'*64 if P(p)==m.PROOF else savedsha(p);reject('published diagnosis SHA mismatch rejected',m.review);m.sha=savedsha
 m.sha=lambda p:'0'*64 if P(p)==out/'raw.log.gz' else savedsha(p);reject('compressed raw SHA mismatch rejected',m.review);m.sha=savedsha
 first=m.json.loads(m.gzip.open(out/'progress.jsonl.gz','rt').readline());first['seq']=2;m.gzip.open=lambda p,*a,**k:io.StringIO(json.dumps(first)+'\n') if P(p)==out/'progress.jsonl.gz' else savedgzip(p,*a,**k);reject('progress first sequence gap rejected',m.review);m.gzip.open=savedgzip
finally:m.read=savedread;m.sha=savedsha;m.alive=savedalive;m.gzip.open=savedgzip
fixture=P(tempfile.mkdtemp(prefix='GESU_EXPECTED_GROWTH_CPU_',dir=F/'control'));oldroots=(m.F,m.T,m.D);savedreview=m.review;savedload=m.load
def scenario(kind):
 base=fixture/kind;m.F=base/'F';m.T=base/'T';m.D=base/'metadata';original=m.T/'analysis'/(m.CELL+'.RESULT.json');put(original,{'state':'ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','cohort':m.CELL,'error':'old preserved CPU'});fakeout=m.T/'DTC/run/results'/m.UUID;fakeout.mkdir(parents=True);(fakeout/'raw.keep').write_bytes(b'CPU immutable source');before=(fakeout/'raw.keep').read_bytes();manifest={'txid':'cpu-tx','entries':[{'path':'raw.keep','type':'file'}],'scientific_status':'STOP_UNACCEPTED'};canon=lambda x:(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode();digest=lambda b:hashlib.sha256(b).hexdigest();nas=base/'164';bundle=nas/m.CELL/manifest['txid'];ap=m.T/'control'/(m.CELL+'_ARCHIVE_RECEIPT.json');receipt={'cohort':m.CELL,'status':'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','scientific_status':'STOP_UNACCEPTED','target_mount_path':str(bundle),'native_restore':str(base/'native_restore'),'archive_sha256':'a'*64};calls={'COPY':0,'verify':0,'restorecheck':0}
 def create_archive():put(bundle/'SOURCE_MANIFEST.json',manifest);put(bundle/'COMMIT.json',{'fake':True});put(ap,receipt)
 if kind=='existing':create_archive()
 fresh=dict(baseline,old_RESULT_path=str(original),old_RESULT_sha256=h(original),manifest_sha256=digest(canon(manifest)),archive_already_exists=kind=='existing',archive=None)
 def archive(c):
  assert c==m.CELL;calls['COPY']+=1
  if kind=='receiver_hold':raise BlockingIOError(11,'CPU receiver HOLD')
  create_archive();return {'receipt':receipt}
 def verify(*a):calls['verify']+=1;return {'archive_sha256':'a'*64}
 def nativecheck(*a):calls['restorecheck']+=1;return [] if kind=='bad_restore' else [{'path':'raw.keep'}]
 lib=types.SimpleNamespace(verify_archive=verify,check_native=nativecheck);ob=types.SimpleNamespace(NAS=nas,archive=archive,manifest_for=lambda c:manifest,libraries=lambda *a:(lib,None),sha=digest,canon=canon)
 m.review=lambda:fresh;m.load=lambda *a:ob;pp=base/'PLAN.json';put(pp,fresh);qualification=m.F/'ops/GESUMMV_EXPECTED_GROWTH_REVIEW_CPU_QUALIFICATION_V1.json';put(qualification,{'CPU':True});pub=base/'PUBLICATION.json';put(pub,dict(verified=kind!='wrong_publication',tool_sha256=h(SRC),qualification_sha256=h(qualification),commit='CPU_FAKE_PUBLICATION'))
 if kind=='plan_drift':bad=copy.deepcopy(fresh);bad['DONE_sha256']='0'*64;put(pp,bad)
 if kind in ['wrong_publication','plan_drift','receiver_hold','bad_restore']:
  reject('actual apply fakeRoot '+kind+' rejects without independent result',lambda:m.apply(pp,pub));assert not(m.D/m.UUID/'POSTPROCESS.RESULT.json').exists()
  if kind in ['wrong_publication','plan_drift']:assert calls['COPY']==0 and not m.D.exists()
  if kind=='receiver_hold':assert not m.D.exists()
 else:
  closed=m.apply(pp,pub);assert closed['state']=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY' and closed['accepted_cycles'] is None and closed['scientific_acceptance'] is False and closed['models_started']==closed['model_retries']==closed['signals']==closed['authority_changes']==0;assert calls['COPY']==(0 if kind=='existing' else 1) and calls['verify']>0 and calls['restorecheck']>0;assert h(original)==fresh['old_RESULT_sha256'] and(m.D/m.UUID/'OLD_ENGINEERING_RESULT.PREIMAGE.json').read_bytes()==original.read_bytes();assert(fakeout/'raw.keep').read_bytes()==before and len(list(fakeout.iterdir()))==1;check('actual apply fakeRoot '+kind+' preserves old result/output and closes only UNACCEPTED after independent archive+restore verify',lambda:None);reject('repeat closure '+kind+' cannot overwrite or COPY again',lambda:m.apply(pp,pub))
 return {'scenario':kind,'calls':calls,'real_COPIES':0,'real_models':0}
try:scenarios=[scenario(k) for k in ['new_archive','existing','wrong_publication','plan_drift','receiver_hold','bad_restore']]
finally:m.F,m.T,m.D=oldroots;m.review=savedreview;m.load=savedload
check('all original INTENT/DONE/EXIT/engineering RESULT exact bytes unchanged',lambda:m.require(all(h(p)==v for p,v in immutable.items()),'immutable drift'))
check('production native source manifest exact unchanged and no archive receipt created',lambda:m.require(m.load(m.T/'tools/sweep_outbox.py','gesu_cpu_final_readonly_outbox').manifest_for(m.CELL)==manifest_before and not(m.T/'control'/(m.CELL+'_ARCHIVE_RECEIPT.json')).exists(),'source/archive drift'))
report=dict(schema='GESUMMV_EXPECTED_GROWTH_METADATA_REVIEW_CPU_QUALIFICATION_V1',status='PASS',utc=m.now(),tool_path=str(SRC),tool_sha256=h(SRC),driver_path=str(P(__file__)),driver_sha256=h(__file__),checks=checks,check_count=len(checks),fakeRoot_scenarios=scenarios,fixture_root=str(fixture),read_only_plan_path=str(plan),read_only_plan_sha256=h(plan),published_diagnosis_sha256=m.PROOF_SHA,old_engineering_result_sha256=baseline['old_RESULT_sha256'],immutable_native_evidence=immutable,real_archive_COPY_calls=0,real_out_writes=0,real_authority_changes=0,scientific_models_started=0,signals=0,scope='Actual production read-only evidence review plus CPU fakeRoot future apply branches using mocked original outbox payload operations. No production COPY, restore, postprocess closure or ledger/authority mutation was executed.')
dest=F/'ops/GESUMMV_EXPECTED_GROWTH_REVIEW_CPU_QUALIFICATION_V1.json';m.exclusive(dest,m.encoded(report));print(json.dumps(dict(status='PASS',checks=len(checks),qualification=str(dest),sha256=h(dest),tool_sha256=h(SRC),driver_sha256=h(__file__),plan_sha256=h(plan))))
