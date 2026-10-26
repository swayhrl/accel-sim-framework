"""CPU qualification plus read-only exact two real native evidence chains."""
import pathlib,json,hashlib,copy,importlib.util,tempfile,types,io,ast
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');SRC=F/'ops/review_two_stencil_expected_growth_v1.py';s=importlib.util.spec_from_file_location('finite2_stencil_cpu',SRC);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);checks=[]
def h(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,value):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(m.encoded(value))
def check(name,fn):fn();checks.append({'name':name,'status':'PASS'})
def reject(name,fn):
 try:fn()
 except (RuntimeError,AssertionError,KeyError,OSError,ValueError):checks.append({'name':name,'status':'PASS'});return
 raise AssertionError('negative accepted: '+name)
calls=[ast.unparse(n.func) for n in ast.walk(ast.parse(SRC.read_text())) if isinstance(n,ast.Call)];assert not any(x.endswith(('.run_cell','.run_native','.prepare','.Popen','.kill','.killpg','.update_authority','.system')) for x in calls);checks.append({'name':'AST no scientific start/signal/authority API','status':'PASS'})
planpath=F/'ops/TWO_STENCIL_EXPECTED_GROWTH_READ_ONLY_PLAN_V1.json';baseline=m.review();assert baseline==m.read(planpath)
immutable={};manifests={};samples_by={};policies_by={};real_read=m.read
for point in baseline['points']:
 cell=point['cohort'];uid=point['uuid'];out=m.T/'DTC/run/results'/uid;ip=m.T/'control/qualification_ledger'/(cell+'.INTENT.json');dp=ip.with_name(cell+'.DONE.json');done=m.read(dp);intent=m.read(ip)
 for p in [ip,dp,out/'NATIVE_EXIT.json',P(point['old_RESULT_path'])]:immutable[str(p)]=h(p)
 ob=m.load(m.T/'tools/sweep_outbox.py','stencil_cpu_readonly_manifest');manifests[cell]=ob.manifest_for(cell)
 check(cell+' actual readonly source/real receipt/raw dualSHA/progress and288+288 streams PASS',lambda point=point:m.require(point['accepted_cycles'] is None and point['scientific_acceptance'] is False and point['outer_samples']==point['policy_samples']==288 and point['combined_record_count']==576,'incorrect acceptance/count'))
 samples=[{'physical_RAM_pass':True,'physical_disk_pass':True} for _ in range(287)]+[copy.deepcopy(point['last_failing_sample'])];policies=[{'decision':{'decision':'CONTINUE','stop_reasons':[]}} for _ in range(287)]+[copy.deepcopy(point['last_policy_stop'])];samples_by[cell]=samples;policies_by[cell]=policies
 check(cell+' exact historical reservation shortfall only UNACCEPTED',lambda cell=cell,samples=samples,policies=policies:m.validate_samples(cell,samples,policies))
 row={'uuid':uid,'intent_sha256':point['INTENT_sha256'],'execution_receipt':done};check(cell+' real DONE identity join',lambda cell=cell,i=intent,d=done,r=row,o=out:m.validate_identity(cell,i,d,r,d,o,i['spec_sha256'],r['intent_sha256']))
 for key,value in [('uuid','wrong'),('output','/different'),('stop_reason','MEMORY_HEADROOM'),('launcher_wait_returncode',0),('native_simulator_observed',False),('new_attempt_consumed',2),('actual_simulator_wait_and_file_evidence',None)]:
  changed=dict(done,**{key:value});reject(cell+' wrong '+key+' rejected',lambda cell=cell,i=intent,d=changed,r=row,o=out:m.validate_identity(cell,i,d,r,d,o,i['spec_sha256'],r['intent_sha256']))
 missing=copy.deepcopy(row);missing.pop('execution_receipt');reject(cell+' missing execution receipt cannot infer wait',lambda cell=cell,i=intent,d=done,r=missing,o=out:m.validate_identity(cell,i,d,r,d,o,i['spec_sha256'],r['intent_sha256']))
cell=next(iter(m.CELLS));samples=samples_by[cell];policies=policies_by[cell]
for name,edit in [('earlierRAMfalse',lambda a:a[0].update(physical_RAM_pass=False)),('earlierDiskfalse',lambda a:a[0].update(physical_disk_pass=False)),('lastDisktrue',lambda a:a[-1].update(physical_disk_pass=True)),('snapshotRequiredChanged',lambda a:a[-1].update(required_free_bytes=a[-1]['required_free_bytes']+1)),('loweredFloor',lambda a:a[-1].update(local_safety_floor_bytes=1)),('wrongOwnWriteArithmetic',lambda a:a[-1].update(bounded_own_remaining_write_and_restore_bytes=0)),('wrongPeerReservation',lambda a:a[-1]['peer_reservations'][0].update(reserved_write_bytes=1)),('inodeShortage',lambda a:a[-1].update(free_inodes=1)),('wrongSamplePopulation576',lambda a:a.extend(copy.deepcopy(a)))]:
 a=copy.deepcopy(samples);edit(a);reject(name,lambda a=a:m.validate_samples(cell,a,policies))
for name,edit in [('anotherStopCause',lambda a:a[-1]['decision'].update(stop_reasons=['OOM'])),('hostSTOP',lambda a:a[-1]['decision']['domains']['host'].update(decision='STOP')),('cgroupWarning',lambda a:a[-1]['decision']['domains']['cgroup'].update(warnings=['other'])),('earlierSTOP',lambda a:a[0]['decision'].update(decision='STOP')),('policyCountGap',lambda a:a.pop())]:
 a=copy.deepcopy(policies);edit(a);reject(name,lambda a=a:m.validate_samples(cell,samples,a))
saved=(m.read,m.sha,m.alive,m.gzip)
try:
 def wrong_read(target,edit):
  def read(p):
   value=saved[0](p)
   if P(p)==target:value=copy.deepcopy(value);edit(value)
   return value
  return read
 point=baseline['points'][0];out=m.T/'DTC/run/results'/point['uuid'];dp=m.T/'control/qualification_ledger'/(cell+'.DONE.json')
 m.read=wrong_read(dp,lambda d:d.update(uuid='wrong'));reject('actual review wrong DONE rejects before archive',lambda:m.review_point(cell));m.read=saved[0]
 m.alive=lambda _:True;reject('actual review live original generation rejects',lambda:m.review_point(cell));m.alive=saved[2]
 m.read=wrong_read(out/'NATIVE_LAUNCH.json',lambda d:d.update(launcher_pid=__import__('os').getpid()));reject('actual review live launcher PID rejects',lambda:m.review_point(cell));m.read=saved[0]
 m.sha=lambda p:'0'*64 if P(p)==m.DIAG else saved[1](p);reject('diagnosis SHA drift rejects',lambda:m.review_point(cell));m.sha=saved[1]
 m.sha=lambda p:'0'*64 if P(p)==out/'raw.log.gz' else saved[1](p);reject('raw compressed SHA drift rejects',lambda:m.review_point(cell));m.sha=saved[1]
 m.read=wrong_read(P(point['old_RESULT_path']),lambda d:d.update(state='PASS_STRICT_ARCHIVE_NATIVE_RESTORE'));reject('old canonical RESULT cannot be relabeled',lambda:m.review_point(cell));m.read=saved[0]
 first=json.loads(saved[3].open(out/'progress.jsonl.gz','rt').readline());first['seq']=2;m.gzip=types.SimpleNamespace(open=lambda p,*a,**k:io.StringIO(json.dumps(first)+'\n') if P(p)==out/'progress.jsonl.gz' else saved[3].open(p,*a,**k));reject('progress sequence gap rejects',lambda:m.review_point(cell))
finally:m.read,m.sha,m.alive,m.gzip=saved
fixture=P(tempfile.mkdtemp(prefix='TWO_STENCIL_NEGATIVE_CPU_',dir=F/'control'));saved_globals=(m.F,m.T,m.D,m.QUAL,m.review,m.review_point,m.load);scenarios=[]
def scenario(kind):
 base=fixture/kind;m.F=base/'F';m.T=base/'T';m.D=base/'negative_closure';m.QUAL=m.F/'ops/TWO_STENCIL_EXPECTED_GROWTH_REVIEW_CPU_QUALIFICATION_V1.json';fresh={};original_hash={};calls={'COPY':0,'archive_verify':0,'native_verify':0};man={};receipts={};nas=base/'164';canon=lambda x:(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode();digest=lambda b:hashlib.sha256(b).hexdigest()
 for n,point in enumerate(baseline['points']):
  c=point['cohort'];uid=point['uuid'];rp=m.T/'analysis'/(c+'.RESULT.json');put(rp,{'state':'RESOLVING_ISSUE_NO_MODEL_RETRY','cohort':c,'error':'fakeRoot original preserved'});original_hash[c]=h(rp);out=m.T/'DTC/run/results'/uid;out.mkdir(parents=True);(out/'raw.keep').write_bytes(b'CPU source must not be appended');manifest={'txid':'tx'+str(n),'entries':[{'path':'raw.keep','type':'file'}],'scientific_status':'STOP_UNACCEPTED'};man[c]=manifest;bundle=nas/c/manifest['txid'];receipts[c]={'cohort':c,'status':'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','scientific_status':'STOP_UNACCEPTED','target_mount_path':str(bundle),'native_restore':str(base/'restore'/c),'archive_sha256':'a'*64};fresh[c]=dict(point,old_RESULT_path=str(rp),old_RESULT_sha256=h(rp),source_manifest_sha256=digest(canon(manifest)),archive_already_exists=False,archive=None)
 def make(c):put(P(receipts[c]['target_mount_path'])/'SOURCE_MANIFEST.json',man[c]);put(P(receipts[c]['target_mount_path'])/'COMMIT.json',{'CPU':True});put(m.T/'control'/(c+'_ARCHIVE_RECEIPT.json'),receipts[c])
 if kind=='existing':
  for c in m.CELLS:make(c)
 def archive(c):
  calls['COPY']+=1
  if kind=='receiver_hold':raise BlockingIOError(11,'private fixture COPY HOLD')
  make(c)
 def verify(*a):calls['archive_verify']+=1;return {'archive_sha256':'a'*64}
 def native(*a):calls['native_verify']+=1;return [] if kind=='bad_restore' else [{'path':'raw.keep'}]
 lib=types.SimpleNamespace(verify_archive=verify,check_native=native);ob=types.SimpleNamespace(NAS=nas,manifest_for=lambda c:man[c],archive=archive,libraries=lambda *a:(lib,None),sha=digest,canon=canon);m.load=lambda *a:ob;m.review_point=lambda c:copy.deepcopy(fresh[c]);m.review=lambda:dict(baseline,points=[copy.deepcopy(fresh[c]) for c in m.CELLS]);pp=base/'PLAN.json';put(pp,m.review());qual={'status':'PASS','tool_sha256':h(SRC),'plan_sha256':h(pp),'diagnosis_sha256':m.DIAG_SHA};put(m.QUAL,qual)
 if kind=='bad_qualification':qual['status']='FAIL';put(m.QUAL,qual)
 pub=base/'PUBLICATION.json';put(pub,{'verified':kind!='wrong_publication','commit':'CPU_SYNTHETIC_NOT_PUBLISHED','tool_sha256':h(SRC),'qualification_sha256':h(m.QUAL),'plan_sha256':h(pp),'diagnosis_sha256':m.DIAG_SHA})
 if kind=='plan_drift':bad=read(pp);bad['points'][0]['DONE_sha256']='wrong';put(pp,bad);p=read(pub);p['plan_sha256']=h(pp);put(pub,p);qual['plan_sha256']=h(pp);put(m.QUAL,qual);p['qualification_sha256']=h(m.QUAL);put(pub,p)
 if kind in ['wrong_publication','bad_qualification','plan_drift','receiver_hold','bad_restore']:
  reject('actual finite2 apply fakeRoot '+kind,lambda:m.apply(pp,pub));assert not list(m.D.glob('*/POSTPROCESS.RESULT.json'))
  if kind in ['wrong_publication','bad_qualification','plan_drift']:assert calls['COPY']==0
 else:
  closed=m.apply(pp,pub);assert len(closed)==2 and all(x['state']=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY' and x['accepted_cycles'] is None and x['scientific_acceptance'] is False and x['resource_policy_relaxed'] is False and x['model_starts']==x['signals']==x['authority_changes']==0 for x in closed);assert calls['COPY']==(0 if kind=='existing' else 2) and calls['archive_verify']>=2 and calls['native_verify']>=2;count=calls['COPY'];m.apply(pp,pub);assert calls['COPY']==count;checks.append({'name':'actual fakeRoot '+kind+' finite2 closure+independent restore+idempotent no duplicate COPY','status':'PASS'})
  if kind=='new_archive':
   c=next(iter(m.CELLS));r=m.D/m.CELLS[c]['uuid']/'REVIEW.json';v=read(r);v['DONE_sha256']='tampered';put(r,v);reject('stored REVIEW tamper rejects no duplicate COPY',lambda:m.apply(pp,pub));assert calls['COPY']==count
 for c in m.CELLS:
  assert h(m.T/'analysis'/(c+'.RESULT.json'))==original_hash[c];out=m.T/'DTC/run/results'/m.CELLS[c]['uuid'];assert len(list(out.iterdir()))==1 and(out/'raw.keep').read_bytes()==b'CPU source must not be appended'
 scenarios.append({'kind':kind,'calls':calls,'real_COPIES':0,'real_models':0})
try:
 for kind in ['new_archive','existing','wrong_publication','bad_qualification','plan_drift','receiver_hold','bad_restore']:scenario(kind)
finally:m.F,m.T,m.D,m.QUAL,m.review,m.review_point,m.load=saved_globals
assert all(h(p)==v for p,v in immutable.items())
for c in m.CELLS:
 ob=m.load(m.T/'tools/sweep_outbox.py','stencil_cpu_final_outbox');assert ob.manifest_for(c)==manifests[c] and not(m.T/'control'/(c+'_ARCHIVE_RECEIPT.json')).exists()
checks.append({'name':'all production INTENT/DONE/EXIT/oldRESULT/out manifest unchanged; archive0','status':'PASS'})
report={'schema':'TWO_STENCIL_EXPECTED_GROWTH_NEGATIVE_METADATA_REVIEW_CPU_QUALIFICATION_V1','status':'PASS','tool_path':str(SRC),'tool_sha256':h(SRC),'driver_path':str(P(__file__).resolve()),'driver_sha256':h(__file__),'plan_path':str(planpath),'plan_sha256':h(planpath),'diagnosis_path':str(m.DIAG),'diagnosis_sha256':m.DIAG_SHA,'reference_published_GESUMMV_source_sha256':m.BASE_SHA,'checks':checks,'check_count':len(checks),'fakeRoot_scenarios':scenarios,'fixture_root':str(fixture),'immutable_production_evidence':immutable,'readonly_real_points':[{'cohort':p['cohort'],'uuid':p['uuid'],'shortfall_bytes':p['shortfall_bytes'],'raw_compressed_sha256':p['raw_compressed_sha256'],'raw_uncompressed_sha256':p['raw_uncompressed_sha256'],'outer':p['outer_samples'],'BA':p['policy_samples'],'progress':p['progress_records'],'old_RESULT_sha256':p['old_RESULT_sha256'],'source_manifest_sha256':p['source_manifest_sha256'],'archive_already_exists':p['archive_already_exists']} for p in baseline['points']],'real_COPY_calls':0,'real_out_or_RESULT_or_ledger_changes':0,'models_started':0,'signals':0,'resource_policy_relaxed':False,'utc':m.datetime.datetime.now(m.datetime.timezone.utc).isoformat()};dest=m.QUAL;m.exclusive(dest,m.encoded(report));print(json.dumps({'status':'PASS','checks':len(checks),'qualification':str(dest),'sha256':h(dest),'tool_sha256':h(SRC),'plan_sha256':h(planpath)}))
