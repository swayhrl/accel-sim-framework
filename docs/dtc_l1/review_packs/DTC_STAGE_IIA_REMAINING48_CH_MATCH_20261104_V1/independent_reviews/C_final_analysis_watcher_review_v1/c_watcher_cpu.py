from pathlib import Path
import sys,importlib.util,json,hashlib,copy,gzip,datetime,ast
sys.dont_write_bytecode=True
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');S=A/'agents/A_final_analysis_watcher_preparation_v1/analysis_waiter.py';O=A/'agents/C_final_analysis_watcher_review_v1';assert not O.exists();O.mkdir();F=O/'private_cpu_fixtures';F.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sourcepin='7e67b4d50cbcd1e37006a438daca8c618ae353b26696d2975e27b9cca2a93a1c';assert sha(S)==sourcepin
spec=importlib.util.spec_from_file_location('c_only_watcher_fixture',S);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);checks=[]
def ck(n,v):assert v,n;checks.append({'check':n,'pass':True})
def rejected(n,fn):
 try:fn()
 except (AssertionError,ValueError,KeyError,FileExistsError):ck(n,True);return
 raise AssertionError(n)
provider=json.loads(m.OFFICIAL.read_bytes());ck('real current provider is metadata-only incomplete',not m.light_gate(provider)['ready'])
rejected('full gate refuses actual partial provider before downstream reads',lambda:m.full_gate(json.dumps(provider).encode()))
# Isolated synthetic provider metadata; never written into a science directory.
p=copy.deepcopy(provider);summary=p['summary'];summary.update(expected_CH=48,registered_consumed=48,registered_remaining=0,accepted_CH=48,archived_negative_CH=0,verification_hold=0,await_result=0,all_registered48_terminal_verified=True,source_qualified=True,request=m.REQ,core32_fixed_input_n=32,expected_six_source_slots=192);p.update(source_qualified=True,all_registered48_terminal_verified=True);ck('exact48 synthetic terminal light gate',m.light_gate(p)['ready'])
for field,value in [('registered_remaining',1),('accepted_CH',47),('await_result',1),('verification_hold',1),('source_qualified',False),('all_registered48_terminal_verified',False),('expected_CH',True)]:
 q=copy.deepcopy(p);q['summary'][field]=value
 try:g=m.light_gate(q);bad=not g['ready']
 except (ValueError,AssertionError):bad=True
 ck('light gate rejects '+field,bad)
q=copy.deepcopy(p);q['summary']['expected_CH']=49;rejected('wrong total budget is hard error',lambda:m.light_gate(q));q=copy.deepcopy(p);q['summary']['core32_fixed_input_n']=31;rejected('wrong population is hard error',lambda:m.light_gate(q));q=copy.deepcopy(p);q['request']='OLD_REQUEST';rejected('wrong request is hard error',lambda:m.light_gate(q))
for negative in [1,5,48]:
 q=copy.deepcopy(p);q['summary'].update(accepted_CH=48-negative,archived_negative_CH=negative);ck('terminal negative permitted '+str(negative),m.light_gate(q)['ready'])
# Exercise full metadata join with private in-memory SHA-qualified objects only.
original={k:getattr(m,k)for k in ['OFFICIAL','rd','checked','verify_manifest']};m.OFFICIAL=F/'official/PUBLICATION_PROVIDER.json';snap=m.OFFICIAL.parent/'snapshots/synthetic';p['snapshot']=str(snap);mfpath=snap/'MANIFEST.json';p['manifest']={'path':str(mfpath),'sha256':'synthetic_manifest_pin'};p['qualification_manifest']={'path':str(F/'qualification.json'),'sha256':m.QUAL_SHA};expected=json.loads(m.STAGE_PINS[-1][0].read_bytes())['points'];rows=[{'cohort':x['cohort'],'input_digest':x['input_digest'],'profile':x['profile'],'design':'CH','status':m.PASS,'accepted':True,'cycles':i+1,'uuid':'EXPLICIT_CPU_FIXTURE_ONLY_'+str(i)}for i,x in enumerate(expected)]
def full_inputs(base,rr):
 s=base['summary'];obs={'source_qualified':True,'registration_granted':True,'registered_consumed':48,'registered_remaining':0,'request':m.REQ,'observations':rr};items={'SUMMARY.json.gz':s,'OBSERVATIONS.json.gz':obs,'CORE32_RESULTS.json.gz':{'explicit_CPU_fixture_not_science':True}};blob={str(snap/name):gzip.compress(json.dumps(value).encode())for name,value in items.items()};base['files']=[{'path':path,'sha256':hashlib.sha256(b).hexdigest()}for path,b in blob.items()];mf={'source_qualified':True,'schema':'DTC_REMAINING48_READONLY_ANALYSIS_SNAPSHOT_V1','adapter':{'sha256':m.ADAPTER_SHA},'runtime_plan':{'sha256':m.PLAN_SHA},'files':base['files']};blob[str(mfpath)]=json.dumps(mf).encode();m.rd=lambda path: {'points':expected}if Path(path)==m.STAGE_PINS[-1][0]else original['rd'](path);m.checked=lambda path,want:blob[str(path)];m.verify_manifest=lambda path,want=None:{'CPU_fixture':True};return json.dumps(base).encode()
q=copy.deepcopy(p);raw=full_inputs(q,copy.deepcopy(rows));_,proof=m.full_gate(raw);ck('full gate exact48 cohorts and unique identities',proof['unique_UUIDs']==48 and proof['accepted']==48)
q=copy.deepcopy(p);rr=copy.deepcopy(rows);rr[-1]['uuid']=rr[0]['uuid'];raw=full_inputs(q,rr);rejected('full gate rejects duplicate consumed UUID',lambda:m.full_gate(raw))
q=copy.deepcopy(p);rr=copy.deepcopy(rows);rr[-1]['cohort']='CPU_FIXTURE_FORBIDDEN_SUPPLEMENT';raw=full_inputs(q,rr);rejected('full gate rejects supplement cohort replacement',lambda:m.full_gate(raw))
q=copy.deepcopy(p);rr=copy.deepcopy(rows);rr[0]['input_digest']='0'*64;raw=full_inputs(q,rr);rejected('full gate rejects input mismatch',lambda:m.full_gate(raw))
q=copy.deepcopy(p);q['summary'].update(accepted_CH=43,archived_negative_CH=5);rr=copy.deepcopy(rows)
for row in rr[:5]:row.update(status=m.NEG,accepted=False,cycles=None)
raw=full_inputs(q,rr);_,proof=m.full_gate(raw);ck('full gate43accepted5archivednegative keeps missing cycles',proof['accepted']==43 and proof['archived_negative']==5)
rr[0]['cycles']=0;raw=full_inputs(q,rr);rejected('negative cycles cannot be imputed zero',lambda:m.full_gate(raw))
for k,v in original.items():setattr(m,k,v)
# No subprocess or watch service is invoked by these CPU fixtures.
stages=m.make_plan('C_CPU_FIXTURE_NONEXISTENT_'+datetime.datetime.now().strftime('%H%M%S'),F/'PROVIDER.synthetic.json');ck('fixed CPU-only ordered chain argv', [s['name']for s in stages]==['C_FINAL48','B_FINAL24','ROOT_MATH','ROOT_RENDERER_V2']and all(s['argv'][1]=='-B'for s in stages)and stages[0]['argv'][2]==str(m.STAGE_PINS[1][0])and stages[1]['argv'][2]==str(m.STAGE_PINS[3][0])and stages[2]['argv'][2]==str(m.STAGE_PINS[4][0])and stages[3]['argv'][2]==str(m.STAGE_PINS[5][0]))
for failstage in range(4):
 calls=[];validated=[]
 def runner(s):calls.append(s['name']);return{'returncode':2 if s==stages[failstage]else 0}
 ans=m.chain(stages,runner,lambda s:validated.append(s['name']),lambda:None);ck('CPU nonzero stops chain '+str(failstage),not ans['success']and len(calls)==failstage+1 and len(validated)==failstage)
calls=[];ans=m.chain(stages,lambda s:(calls.append(s['name'])or {'returncode':0}),lambda s:(_ for _ in ()).throw(AssertionError('SYNTHETIC_BAD_RESULT')),lambda:None);ck('result contract failure holds before next stage',not ans['success']and ans['reason']=='CPU_RESULT_CONTRACT_HOLD'and len(calls)==1)
calls=[];ans=m.chain(stages,lambda s:(calls.append(s['name'])or {'returncode':0}),lambda s:None,lambda:(_ for _ in ()).throw(AssertionError('SYNTHETIC_SHA_DRIFT')));ck('source drift prevents CPU stage start',not ans['success']and ans['reason']=='SOURCE_DRIFT_HOLD'and calls==[])
claim=F/'one_shot.json';m.claim_attempt(claim,{'CPU_fixture':True});before=claim.read_bytes();rejected('O_EXCL claim never overwrites or retries',lambda:m.claim_attempt(claim,{'overwrite':True}));ck('claim bytes preserved',claim.read_bytes()==before)
state=F/'holdstate';m.hold(state,'SYNTHETIC_FIXTURE_HOLD');old=(state/'ANALYSIS_HOLD.json').read_bytes();m.hold(state,'NEW_REASON');ck('first hold reason persists',old==(state/'ANALYSIS_HOLD.json').read_bytes());lockpath=F/'lock';lock=m.acquire_lock(lockpath);second=m.acquire_lock(lockpath);ck('single waiter flock excludes concurrent second handle',lock is not None and second is None);lock.close()
rejected('relative manifest parent escape rejected',lambda:m.safe_relative('../escape'));rejected('absolute manifest path rejected',lambda:m.safe_relative('/etc/passwd'));rejected('output outside approved164 root rejected before mount probe',lambda:m.verify_true164('/tmp/not-authorized-C-fixture'))
# Source-level authority boundary: actual model/owner/registration tools never appear.
tree=ast.parse(S.read_text());names={n.id for n in ast.walk(tree)if isinstance(n,ast.Name)};ck('no model dispatcher/native API or Git implementation in source',not ({'simulate','register_request','attach_new_request','update_authority','prepare','run_model','finish','kill','signal'}&names)and all(x not in S.read_text()for x in ['git push','reset_goal','Py_AddPendingCall','gdb','os.kill','shell=True']))
ck('completion remains Root review pending with no auto approval',all(x in S.read_text()for x in ['Goal_completed=False','Git_publication=False','D_fixed_figure_approval=False','visual_review=False','final_narrative_signoff=False','EXISTING_ATTEMPT_NOT_RETRIED','ANALYSIS_HOLD_NO_AUTO_CPU_OR_MODEL_RETRY']))
ck('source unchanged by CPU review',sha(S)==sourcepin)
(O/'CPU_REVIEW.json').write_text(json.dumps({'schema':'C_ANALYSIS_WAITER_ISOLATED_CPU_REVIEW_V1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','source_path':str(S),'source_sha256':sourcepin,'checks':checks,'check_count':len(checks),'full_gate_fixture_metadata_synthetic_not_scientific_results':True,'watch_called':False,'subprocess_stage_called':False,'real_partial_gate_metadata_only':True,'new_models_owner_registration_Git_or_signal_actions':0},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'sha256':sha(O/'CPU_REVIEW.json')}))
