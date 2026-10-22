import sys,importlib.util,json,copy,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
p=Path(__file__).parent;sp=importlib.util.spec_from_file_location('candidate',p/'remaining_metadata_closure_driver.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
rows=[]
def case(name,fn,reject=False):
 try:fn()
 except (ValueError,KeyError,FileNotFoundError) as exc:
  if not reject:raise
  rows.append({'case':name,'result':'PASS_EXPECTED_REJECTION','reason':str(exc)})
 else:assert not reject,name;rows.append({'case':name,'result':'PASS'})
def fixture(w='dwt2d'):
 cid='V8_TAGPRESSURE_'+w+'_F';identity={'workload':w,'synthetic':True};source={'SYNTHETIC_SOURCE':True};a={'attempt_id':'SYNTHETIC_E057','condition_id':cid,'state':'COMPLETE_VALID','actual_start':True,'identity':identity,'qualification_id':'SYNTHETIC_Q','diagnostic_spec_sha256':'SYNTHETIC_SPEC'};ar={'path':'SYNTHETIC_OUTPUT/run_status.json','sha256':'SYNTHETIC_SHA'};item={'attempts':[{}]*55+[a],'accepted_results':{a['attempt_id']:ar},'tagpressure_observer_successor_batch':{'metadata_closures':{}}};manifest={'baseline_actual_starts':55,'maximum_new_actual_starts':4,'pairs':[],'source_identity':source,'conditions':{cid:{'identity':identity,'qualification':{'sha256':'SYNTHETIC_Q'},'spec_sha256':'SYNTHETIC_SPEC'}}};point={'workload':w,'condition_id':cid,'attempt_id':a['attempt_id'],'status':'CURRENT_ACCEPTED_DIAGNOSTIC_POINT','endpoint_status':'COMPLETE_VALID','pair':False,'scientific_scope':'TAGPRESSURE_OBSERVER_DIAGNOSTIC_POINT_V1','identity':identity,'qualification_id':'SYNTHETIC_Q','source_identity':source,'actual_terminal_receipt':ar};return point,item,manifest
for w in m.REMAINING_WORKLOADS:case('SYNTHETIC_EXACT_'+w,lambda w=w:m.validate_target(*fixture(w)))
for name,mutation in [('RUNNING',lambda p,i,f:i['attempts'][-1].update(state='RUNNING')),('SOURCE_CHANGE',lambda p,i,f:p.update(source_identity={})),('Q_CHANGE',lambda p,i,f:p.update(qualification_id='wrong')),('SPEC_CHANGE',lambda p,i,f:i['attempts'][-1].update(diagnostic_spec_sha256='wrong')),('PAIR',lambda p,i,f:p.update(pair=True)),('ROOT_CLOSED',lambda p,i,f:i['tagpressure_observer_successor_batch']['metadata_closures'].update({p['condition_id']:{}})),('POINTER_CHANGE',lambda p,i,f:p.update(actual_terminal_receipt={})),('DUPLICATE_ATTEMPT',lambda p,i,f:i['attempts'].append(copy.deepcopy(i['attempts'][-1])))]:
 x=fixture();mutation(*x);case('SYNTHETIC_REJECT_'+name,lambda x=x:m.validate_target(*x),True)
case('SYNTHETIC_CFD_ALREADY_COMPLETE_OUT_OF_SCOPE',lambda:m.validate_target(*fixture('cfd_097k')),True)
with tempfile.TemporaryDirectory(prefix='e2-metadata-inventory-') as tmp:
 old=m.E;m.E=Path(tmp);d=m.E/'results/dwt2d';d.mkdir(parents=True);names=['CURRENT_ACCEPTED_POINT.json','INDEPENDENT_TERMINAL_AND_CAUSE_REVIEW.json','REPORT.md','EXTRA_CAUSE.json'];verified=set()
 for name in names:(d/name).write_text('SYNTHETIC');verified.add(str((d/name).relative_to(m.E)))
 case('SYNTHETIC_COMPLETE_INVENTORY',lambda:m.result_inventory(d,verified))
 case('SYNTHETIC_CHANGEDPATHS_ONLY_OMITS_UNCHANGED_POINT',lambda:m.result_inventory(d,verified-{str((d/names[0]).relative_to(m.E))}),True)
 case('SYNTHETIC_EXTRA_CAUSE_NOT_ACCOUNTED',lambda:m.result_inventory(d,verified-{str((d/names[3]).relative_to(m.E))}),True)
 (d/'nested').mkdir();case('SYNTHETIC_NESTED_UNINVENTORIED',lambda:m.result_inventory(d,verified),True);(d/'nested').rmdir();(d/'alias').symlink_to(d);case('SYNTHETIC_SYMLINK_DIRECTORY',lambda:m.result_inventory(d,verified),True);m.E=old
(p/'TEST_RESULT.json').write_text(json.dumps({'schema':'E2_R5_REMAINING_METADATA_DRIVER_SYNTHETIC_CONTROLS_V1','status':'PASS','count':len(rows),'controls':rows,'synthetic_only':True,'no_actual_snapshots_or_central_writes':True},indent=2)+'\n');print(len(rows),'PASS')
