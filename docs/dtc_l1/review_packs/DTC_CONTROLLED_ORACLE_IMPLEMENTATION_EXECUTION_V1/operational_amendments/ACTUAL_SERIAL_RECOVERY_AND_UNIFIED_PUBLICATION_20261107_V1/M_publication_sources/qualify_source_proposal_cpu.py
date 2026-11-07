from pathlib import Path
import copy,hashlib,importlib.util,json,tempfile,time
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1')
O=A/'agents/M_unified_publication_proposal_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=O/'unified_watch_publish_source_proposal.py'
spec=importlib.util.spec_from_file_location('proposal',p);w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
m=w.source_module();forbidden=[]
def deny(*args,**kwargs):forbidden.append(str(args));raise AssertionError('No real Git/process calls allowed in CPU qualification')
m.subprocess.run=deny
report=json.loads((A/'agents/M_clean_successor_unified_consumer_v2/qualified_actual_projection_v2/ORACLE_LIVE_RESULTS.json').read_bytes())
matrix=json.loads((A/'control/authority/FUTURE_DH_ORACLE_MATRIX.json').read_bytes())
tests=[]
def check(n,x):assert x,n;tests.append({'name':n,'pass':True})
v=m.publication_view(report,matrix);now=100000
check('valid_fixed128_with_same_frozen_sourcepins',v['PLAN_population']==128 and len(v['closed_RESULT_source_pins'])==32)
check('actual_scientific_result_digest_retained',v['scientific_closed_result_fingerprint_sha256']==report['closed_fingerprint_sha256'])
check('empty_state_initial_real_data_due',m.due(v,{},now)[0])
state={'last_published_fingerprint':v['closed_fingerprint_sha256'],'last_publication_epoch':0}
check('same_state_does_not_commit_after_interval',m.due(v,state,now)[0]is False)
changed=copy.deepcopy(report);row=next(x for x in changed['rows']if not x['initial_fixed8']);row['status']='UNSTARTED_OR_NOT_REGISTERED'
c=m.publication_view(changed,matrix)
check('status_only_changes_publication_trigger',c['closed_fingerprint_sha256']!=v['closed_fingerprint_sha256'])
check('status_only_retains_actual_source_digest',c['scientific_closed_result_fingerprint_sha256']==v['scientific_closed_result_fingerprint_sha256'])
check('changed_status_due_after_30min',m.due(c,state,now)[0])
check('changed_status_waits_30min',m.due(c,dict(state,last_publication_epoch=now-1799),now)[0]is False)
for key in ['generated_utc','live_progress']:
 x=copy.deepcopy(report);x[key]='different';check('noise_'+key+'_does_not_trigger',m.publication_view(x,matrix)['closed_fingerprint_sha256']==v['closed_fingerprint_sha256'])
for key,value in [('classification','HOLD'),('validation_error','CPU_FAKE_NO_REAL_RESULT'),('pair_status','HOLD_SAMEBUILD_OR_270_MISMATCH')]:
 x=copy.deepcopy(report);x['rows'][0][key]=value;check('actual_semantic_change_'+key,m.publication_view(x,matrix)['closed_fingerprint_sha256']!=v['closed_fingerprint_sha256'])
bad=copy.deepcopy(report);bad['rows']=bad['rows'][:-1]
try:m.publication_view(bad,matrix)
except ValueError:tests.append({'name':'reject_non128_scope','pass':True})
else:raise AssertionError('bad scope accepted')
bad=copy.deepcopy(report);bad['mock']=True
try:m.publication_view(bad,matrix)
except ValueError:tests.append({'name':'reject_mock_report','pass':True})
else:raise AssertionError('mock accepted')
with tempfile.TemporaryDirectory(dir=O,prefix='CPU_PAYLOAD_ONLY_')as d:
 r=Path(d);derived=r/'derived';derived.mkdir();(derived/'report.json').write_text(json.dumps({'CPU_PAYLOAD_NOT_ACTUAL_PUBLICATION':True}))
 payload=r/'leaf';view,manifest=m.build_payload(report,matrix,derived,payload,sha(O/'unified_consumer_publisher_bridge.py'))
 scope=json.loads((payload/'PUBLICATION_SCOPE.json').read_bytes())
 check('payload_labels_both_scientific_and_publication_fingerprints',scope['fingerprint_contract']and scope['scientific_closed_result_fingerprint_sha256']==report['closed_fingerprint_sha256'])
 try:m.build_payload(report,matrix,derived,payload,'x')
 except FileExistsError:tests.append({'name':'existing_leaf_cannot_be_overwritten','pass':True})
 else:raise AssertionError('overwrote leaf')
check('zero_subprocess_git_calls',not forbidden)
out={'status':'PASS_SOURCE_PROPOSAL_CPU_ONLY','cases':len(tests),'tests':tests,'subprocess_or_git_calls':0,'publisher_started':False,'models_started':0,'registrations':0,'owner_or_tracer_actions':0}
(O/'CPU_QUALIFICATION.fixed.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
files=[p for p in O.iterdir()if p.is_file()and p.name!='MANIFEST.fixed.json']
mf={'schema':'DTC_MINIMAL_UNIFIED_PUBLICATION_SOURCE_PROPOSAL_V1','created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'publisher_started':False,'Git_executed':False,'members':[{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(files)]}
p=O/'MANIFEST.fixed.json';p.write_text(json.dumps(mf,sort_keys=True,indent=2)+'\n')
print(json.dumps({'CPU_cases':len(tests),'manifest_sha256':sha(p),'members':len(files)}))
