"""Finite8 negative metadata CPU qualification; no real COPY/start/authority mutation."""
import pathlib,json,hashlib,copy,importlib.util,tempfile,types,io,ast,gzip
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');SRC=F/'ops/review_eight_original_expected_growth_v1.py';s=importlib.util.spec_from_file_location('syrk_negative_cpu',SRC);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);checks=[]
def h(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,value):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(m.encoded(value))
def reject(name,fn):
 try:fn()
 except (RuntimeError,AssertionError,KeyError,OSError,ValueError):checks.append({'name':name,'status':'PASS'});return
 raise AssertionError('negative accepted: '+name)
calls=[ast.unparse(n.func) for n in ast.walk(ast.parse(SRC.read_text())) if isinstance(n,ast.Call)];assert not any(x.endswith(('.run_cell','.run_native','.prepare','.Popen','.kill','.killpg','.update_authority','.system')) for x in calls);checks.append({'name':'AST no model/signal/authority API','status':'PASS'})
planpath=F/'ops/EIGHT_ORIGINAL_EXPECTED_GROWTH_READ_ONLY_PLAN_V1.json';baseline=m.review();assert baseline==read(planpath);point=baseline['points'][0];cell=point['cohort'];out=m.T/'DTC/run/results'/point['uuid'];ip=m.T/'control/qualification_ledger'/(cell+'.INTENT.json');dp=ip.with_name(cell+'.DONE.json');intent=read(ip);done=read(dp);immutable={str(p):h(p) for p in [ip,dp,out/'NATIVE_EXIT.json',P(point['old_RESULT_path'])]};original_manifest=m.load(m.T/'tools/sweep_outbox.py','syrk_cpu_outbox').manifest_for(cell)
assert point['outer_samples']==point['policy_samples']==3066 and point['progress_records']==3151 and point['combined_record_count']==6132 and point['shortfall_bytes']==11715 and point['accepted_cycles'] is None and not point['scientific_acceptance'];checks.append({'name':'real full read-only source/rawdualSHA/3151progress/3066outer+3066BA exact PASS','status':'PASS'})
records=[json.loads(x) for x in gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt')];samples=[x for x in records if 'physical_RAM_pass'in x];policies=[x['DTC_exact_original_policy'] for x in records if 'DTC_exact_original_policy'in x];row={'uuid':point['uuid'],'intent_sha256':point['INTENT_sha256'],'execution_receipt':done};m.validate_identity(cell,intent,done,row,done,out,intent['spec_sha256'],row['intent_sha256']);m.validate_samples(cell,samples,policies);checks.append({'name':'real exact receipt and effective R19 sample validators PASS','status':'PASS'})
for key,value in [('uuid','wrong'),('output','/wrong'),('stop_reason','OOM'),('launcher_wait_returncode',0),('native_simulator_observed',False),('new_attempt_consumed',2),('actual_simulator_wait_and_file_evidence',None)]:
 changed=dict(done,**{key:value});reject('wrong receipt '+key,lambda d=changed:m.validate_identity(cell,intent,d,row,d,out,intent['spec_sha256'],row['intent_sha256']))
for name,edit in [('earlier_RAM_fail',lambda a:a[0].update(physical_RAM_pass=False)),('earlier_disk_fail',lambda a:a[0].update(physical_disk_pass=False)),('effective_sourcewrong',lambda a:a[-1]['live_resource_accounting_correction_R19']['effective_resource_sample'].update(resource_module_sha256='bad')),('effective_thresholdwrong',lambda a:a[-1]['live_resource_accounting_correction_R19']['effective_resource_sample'].update(required_free_bytes=1)),('effective_floor_lowered',lambda a:a[-1]['live_resource_accounting_correction_R19']['effective_resource_sample'].update(local_safety_floor_bytes=1)),('effective_other_knownwrites',lambda a:a[-1]['live_resource_accounting_correction_R19']['effective_resource_sample']['known_remaining_writes_by_request'].update(foreign=1)),('missing_population',lambda a:a.pop())]:
 a=copy.deepcopy(samples);edit(a);reject(name,lambda a=a:m.validate_samples(cell,a,policies))
for name,edit in [('wrong_BA_cause',lambda a:a[-1]['decision'].update(stop_reasons=['OOM'])),('earlier_STOP',lambda a:a[0]['decision'].update(decision='STOP')),('hostwarning',lambda a:a[-1]['decision']['domains']['host'].update(warnings=['other'])),('policycount',lambda a:a.pop())]:
 a=copy.deepcopy(policies);edit(a);reject(name,lambda a=a:m.validate_samples(cell,samples,a))
saved=(m.read,m.sha,m.alive)
try:
 m.alive=lambda _:True;reject('real evidence review rejects live model',lambda:m.review_point(cell));m.alive=saved[2]
 m.sha=lambda p:'0'*64 if P(p)==m.DIAG else saved[1](p);reject('diagnosisSHA drift',lambda:m.review_point(cell));m.sha=saved[1]
 m.sha=lambda p:'0'*64 if P(p)==out/'raw.log.gz' else saved[1](p);reject('actual rawSHA drift',lambda:m.review_point(cell));m.sha=saved[1]
 def changedread(p):
  d=saved[0](p)
  if P(p)==P(point['old_RESULT_path']):d=dict(d,state='PASS_STRICT_ARCHIVE_NATIVE_RESTORE')
  return d
 m.read=changedread;reject('canonicalpositiveoverwrite cannot be admitted',lambda:m.review_point(cell))
finally:m.read,m.sha,m.alive=saved
# All eight actual source/receipt/raw/progress/resource paths have passed review().
immutable={};original_manifests={}
for realpoint in baseline['points']:
 c=realpoint['cohort'];u=realpoint['uuid'];rout=m.T/'DTC/run/results'/u;rip=m.T/'control/qualification_ledger'/(c+'.INTENT.json');rdp=rip.with_name(c+'.DONE.json')
 for path in [rip,rdp,rout/'NATIVE_EXIT.json',P(realpoint['old_RESULT_path'])]:immutable[str(path)]=h(path)
 original_manifests[c]=m.load(m.T/'tools/sweep_outbox.py','six_cpu_manifest').manifest_for(c)
 assert realpoint['outer_samples']==realpoint['policy_samples']==m.CELLS[c]['outer'] and realpoint['combined_record_count']==2*m.CELLS[c]['outer'] and realpoint['progress_records']==m.CELLS[c]['progress'] and not realpoint['scientific_acceptance']
 checks.append({'name':c+' actual read-only full native evidence and exact population PASS','status':'PASS'})
reject('out-of-scope seventh cell rejected',lambda:m.review_point('E2-AEV100-NOT-AUTHORIZED-CM'))
fixture=P(tempfile.mkdtemp(prefix='SYRK_NEGATIVE_CPU_',dir=F/'control'));saved_globals=(m.F,m.T,m.D,m.QUAL,m.review,m.review_point,m.load);scenarios=[]
def scenario(kind):
 base=fixture/kind;m.F=base/'F';m.T=base/'T';m.D=base/'negative_closure';m.QUAL=m.F/'ops/EIGHT_ORIGINAL_EXPECTED_GROWTH_REVIEW_CPU_QUALIFICATION_V1.json';fresh={};original_hash={};calls={'COPY':0,'archive_verify':0,'native_verify':0};man={};receipts={};nas=base/'164';canon=lambda x:(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode();digest=lambda b:hashlib.sha256(b).hexdigest()
 for n,point in enumerate(baseline['points']):
  c=point['cohort'];uid=point['uuid'];rp=m.T/'analysis'/(c+'.RESULT.json');put(rp,{'state':'ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','cohort':c,'error':'fakeRoot original preserved'});original_hash[c]=h(rp);out=m.T/'DTC/run/results'/uid;out.mkdir(parents=True);(out/'raw.keep').write_bytes(b'CPU source must not be appended');manifest={'txid':'tx'+str(n),'entries':[{'path':'raw.keep','type':'file'}],'scientific_status':'STOP_UNACCEPTED'};man[c]=manifest;bundle=nas/c/manifest['txid'];receipts[c]={'cohort':c,'status':'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','scientific_status':'STOP_UNACCEPTED','target_mount_path':str(bundle),'native_restore':str(base/'restore'/c),'archive_sha256':'a'*64};fresh[c]=dict(point,old_RESULT_path=str(rp),old_RESULT_sha256=h(rp),source_manifest_sha256=digest(canon(manifest)),archive_already_exists=False,archive=None)
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
  reject('actual finite8 apply fakeRoot '+kind,lambda:m.apply(pp,pub));assert not list(m.D.glob('*/POSTPROCESS.RESULT.json'))
  if kind in ['wrong_publication','bad_qualification','plan_drift']:assert calls['COPY']==0
 else:
  closed=m.apply(pp,pub);assert len(closed)==8 and all(x['state']=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY' and x['accepted_cycles'] is None and x['scientific_acceptance'] is False and x['resource_policy_relaxed'] is False and x['model_starts']==x['signals']==x['authority_changes']==0 for x in closed);assert calls['COPY']==(0 if kind=='existing' else 8) and calls['archive_verify']>=8 and calls['native_verify']>=8;count=calls['COPY'];m.apply(pp,pub);assert calls['COPY']==count;checks.append({'name':'actual fakeRoot '+kind+' finite8 closure+independent restore+idempotent no duplicate COPY','status':'PASS'})
  if kind=='new_archive':
   c=next(iter(m.CELLS));r=m.D/m.CELLS[c]['uuid']/'REVIEW.json';v=read(r);v['DONE_sha256']='tampered';put(r,v);reject('stored REVIEW tamper rejects no duplicate COPY',lambda:m.apply(pp,pub));assert calls['COPY']==count
 for c in m.CELLS:
  assert h(m.T/'analysis'/(c+'.RESULT.json'))==original_hash[c];out=m.T/'DTC/run/results'/m.CELLS[c]['uuid'];assert len(list(out.iterdir()))==1 and(out/'raw.keep').read_bytes()==b'CPU source must not be appended'
 scenarios.append({'kind':kind,'calls':calls,'real_COPIES':0,'real_models':0})
try:
 for kind in ['new_archive','existing','wrong_publication','bad_qualification','plan_drift','receiver_hold','bad_restore']:scenario(kind)
finally:m.F,m.T,m.D,m.QUAL,m.review,m.review_point,m.load=saved_globals

assert all(h(p)==v for p,v in immutable.items());assert all(m.load(m.T/'tools/sweep_outbox.py','six_cpu_final_manifest').manifest_for(c)==mf and not(m.T/'control'/(c+'_ARCHIVE_RECEIPT.json')).exists() for c,mf in original_manifests.items());checks.append({'name':'production INTENT DONE EXIT oldRESULT and outmanifest unchanged; realarchive0','status':'PASS'})
report={'schema':'EIGHT_ORIGINAL_EXPECTED_GROWTH_FINITE8_NEGATIVE_METADATA_REVIEW_CPU_QUALIFICATION_V1','status':'PASS','tool_path':str(SRC),'tool_sha256':h(SRC),'driver_path':str(P(__file__).resolve()),'driver_sha256':h(__file__),'plan_path':str(planpath),'plan_sha256':h(planpath),'diagnosis_path':str(m.DIAG),'diagnosis_sha256':m.DIAG_SHA,'checks':checks,'check_count':len(checks),'fakeRoot_scenarios':scenarios,'fixture_root':str(fixture),'immutable_production_evidence':immutable,'real_COPY_calls':0,'real_out_or_RESULT_or_ledger_changes':0,'models_started':0,'signals':0,'resource_policy_relaxed':False};m.exclusive(m.QUAL,m.encoded(report));print(json.dumps({'status':'PASS','checks':len(checks),'qualification':str(m.QUAL),'sha256':h(m.QUAL),'tool_sha256':h(SRC),'plan_sha256':h(planpath)}))
