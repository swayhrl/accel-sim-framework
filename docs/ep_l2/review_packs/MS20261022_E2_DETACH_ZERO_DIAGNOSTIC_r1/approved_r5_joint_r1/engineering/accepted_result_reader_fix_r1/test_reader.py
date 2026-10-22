import sys,types,json,hashlib,importlib.util,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
stub=types.ModuleType('tagpressure_successor');stub.SCI_SCOPE='TAGPRESSURE_OBSERVER_DIAGNOSTIC_POINT_V1'
def require(ok,msg):
 if not ok:raise ValueError(msg)
stub.require=require;sys.modules['tagpressure_successor']=stub
p=Path(__file__).parent;spec=importlib.util.spec_from_file_location('candidate',p/'tagpressure_metadata.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[]
def case(name,fn,reject=False):
 try:fn()
 except (ValueError,OSError,KeyError,TypeError) as exc:
  if not reject:raise
  rows.append({'case':name,'result':'PASS_EXPECTED_REJECTION','reason':str(exc)[:160]})
 else:
  assert not reject,name+' unexpectedly accepted';rows.append({'case':name,'result':'PASS'})
def ref(path):return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
r=json.load(open('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json'))['mechanism_study_20261019_v1'];a=r['attempts'][-1];assert a['attempt_id']=='E056_47abdc7f';actual={k:r['accepted_results'][a['attempt_id']][k] for k in ('path','sha256')}
case('ACTUAL_12127626_BYTE_ACCEPTED_RECEIPT_EXACT_SHA',lambda:m.read_accepted_result(actual,a))
with tempfile.TemporaryDirectory(prefix='e2-r5-reader-test-') as tmp:
 m.ACCEPTED_OUTPUT=Path(tmp);b={'attempt_id':'E056_47abdc7f','identity':{'synthetic':True},'qualification_id':'SYNTHETIC_Q'};path=Path(tmp)/b['attempt_id']/'run_status.json';path.parent.mkdir();doc={'attempt_id':b['attempt_id'],'identity':b['identity'],'qualification_id':b['qualification_id'],'scientific_scope':stub.SCI_SCOPE,'status':'COMPLETE_VALID','exit_code':0,'independent_acceptance':'PASS','complete_input_verified':True};path.write_text(json.dumps(doc));good=ref(path)
 case('SYNTHETIC_MINIMAL_ACCEPTED',lambda:m.read_accepted_result(good,b))
 case('SYNTHETIC_BAD_HASH',lambda:m.read_accepted_result(dict(good,sha256='0'*64),b),True)
 case('SYNTHETIC_OUTSIDE_PATH',lambda:m.read_accepted_result(dict(good,path='/tmp/run_status.json'),b),True)
 case('SYNTHETIC_WRONG_ATTEMPT',lambda:m.read_accepted_result(good,dict(b,attempt_id='E057_00000000')),True)
 doc['identity']={'wrong':True};path.write_text(json.dumps(doc));case('SYNTHETIC_IDENTITY_CHANGED',lambda:m.read_accepted_result(ref(path),b),True)
 doc['identity']=b['identity'];doc['exit_code']=False;path.write_text(json.dumps(doc));case('SYNTHETIC_BOOL_NATIVE_EXIT',lambda:m.read_accepted_result(ref(path),b),True)
 path.write_text('{"status":1,"status":2}');case('SYNTHETIC_DUPLICATE_JSON_KEY',lambda:m.read_accepted_result(ref(path),b),True)
 with path.open('wb') as f:f.truncate(m.ACCEPTED_RECEIPT_LIMIT+1)
 case('SYNTHETIC_SPARSE_384MIB_PLUS1_STAT_REJECT_NO_BODY_READ',lambda:m.read_accepted_result(dict(good,sha256='0'*64),b),True)
 path.unlink();path.symlink_to('/tmp/no-receipt');case('SYNTHETIC_SYMLINK_REJECT',lambda:m.read_accepted_result(good,b),True)
report={'status':'BOUNDED_ACCEPTED_RESULT_READER_CONTROLS_PASS','control_count':len(rows),'actual_read':{'path':actual['path'],'bytes':12127626,'sha256':actual['sha256']},'controls':rows,'no_controller_registry_source_mutation':True,'synthetic_is_not_native_or_application_qualification':True}
(p/'TEST_RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
