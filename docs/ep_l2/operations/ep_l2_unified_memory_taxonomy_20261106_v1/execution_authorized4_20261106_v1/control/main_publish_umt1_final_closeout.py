"""UMT1 Main rolling scientific publisher; no model starts, no source or Native mutations."""
from pathlib import Path
import json,hashlib,subprocess,fcntl,datetime,importlib.util,base64
C=Path(__file__).resolve().parent;A=C.parent;U=A.parent;J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
REG=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
REPO='repos/swayhrl/accel-sim-framework';BASE='838faaab158aaa70c70dac7ec1c5817cb16890b3'
BRANCH='hrl/ep-l2-umt1-pressure-exact4-20261106-v1'
PREFIX='docs/ep_l2/operations/ep_l2_unified_memory_taxonomy_20261106_v1/execution_authorized4_20261106_v1'
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def exact(r):
 assert sha(r['path'])==r['sha256'],'evidence drift '+r['path'];return read(r['path'])
def write(p,d):Path(p).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
def clean(d):
 if isinstance(d,dict):return {k:clean(v)for k,v in d.items()if not any(z in k.lower()for z in ['token','nonce','secret'])}
 if isinstance(d,list):return [clean(v)for v in d]
 return d
def report():
 manifest=read(C/'EXACT_EXECUTION_MANIFEST.json');reg=read(REG);points=[];counts={'accepted':0,'technical_failure':0,'pending':0}
 sp=importlib.util.spec_from_file_location('umt1_closed_mechanism_collector',C/'closed_counter_summary_umt1.py');collector=importlib.util.module_from_spec(sp);sp.loader.exec_module(collector)
 for p in manifest['points']:
  group=manifest['groups'][p['group']];q=reg['registered_future_requests'][group['request_id']];r=q['consumed'].get(p['cohort'],{});s=exact(p['spec_ref'])
  item={'cohort':p['cohort'],'group':p['group'],'mode':s['mode'],'state':r.get('state','NOT_STARTED'),'consumed':bool(r),'uuid':r.get('uuid'),'cycles':None,'spec_ref':p['spec_ref'],'Source5':s['source_identity'],'input_identity_sha256':s['input_identity_sha256'],'geometry':s['geometry'],'limits':s['limits'],'independent_release':True,'expected_complete_application':{k:s[k]for k in ['command_count','expected_kernel_launches','expected_CTA','expected_instructions']}}
  for key in ['accepted_point_ref','done_ref','archive_receipt_ref','validation_ref']:item[key]=r.get(key)
  if r.get('done_ref'):
   d=exact(r['done_ref']);item.update(elapsed_seconds=d.get('elapsed_seconds'),stop_reason=d.get('stop_reason'),launcher_wait_returncode=d.get('launcher_wait_returncode'))
  if r.get('output'):
   identity=Path(r['output'])/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
   if identity.exists():item['actual_model_identity_ref']=ref(identity)
  if r.get('state')=='CLOSED_ACCEPTED':
   pt=exact(r['accepted_point_ref']);ar=exact(r['archive_receipt_ref']);rs=ar['native_restores']
   assert pt['cohort']==p['cohort']and pt['uuid']==r['uuid']==ar['uuid']and pt['spec_ref']['sha256']==p['spec_ref']['sha256']
   assert pt['source_identity']==s['source_identity']and pt['input_identity_sha256']==s['input_identity_sha256']and pt['hardware_drained']is True
   assert ar['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS'and len(rs)==2 and len({x['target']for x in rs})==2
   assert all(x['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS'and x['archive_sha256']==ar['archive_ref']['sha256']for x in rs)
   item.update(cycles=pt['cycles'],kernel_count=pt['kernel_count'],CTA=pt['CTA'],instructions=pt['instructions'],hardware_drained=True,archive_two_restores=True)
   try:
    cm=collector.collect(p['cohort'],s,r,C);item['closed_counter_summary_ref']=ref(C/'CLOSED_COUNTERS'/(p['cohort']+'.json'))
    item['pressure_activation']=cm['activation'];item['normal_line_pressure']=cm['normal_line_pressure']
    assert cm['activation'].get('policy')==int(s['expected_effective_options']['-gpgpu_ep_l2_ro_pressure_epoch'])
    item['mechanisms']={k:{key:value for key,value in vv.items()if key!='last_per_slice'}for k,vv in cm['groups'].items()}
    item['RO_head_waits']={k:{kk:vv for kk,vv in v.items()if kk!='last_per_slice'}for k,v in cm['RO_head_waits'].items()}
   except Exception as err:item['counter_gap']=repr(err)
   counts['accepted']+=1
  elif r.get('state')=='CLOSED_UNACCEPTED':counts['technical_failure']+=1
  else:counts['pending']+=1
  points.append(item)
 comparisons={}
 for g in manifest['groups']:
  aa=next(p for p in points if p['group']==g and p['mode']=='F_BASELINE');bb=next(p for p in points if p['group']==g and p['mode']=='F_PRESSURE_EPOCH')
  if aa['cycles']is None or bb['cycles']is None:comparisons[g]={'status':'UNKNOWN_UNTIL_BOTH_SAME_SOURCE_POINTS_ACCEPTED'};continue
  assert aa['Source5']==bb['Source5']and aa['input_identity_sha256']==bb['input_identity_sha256']
  comparisons[g]={'status':'SAME_SOURCE_SAME_INPUT_FULL283_POLICY_ONLY_COMPARISON','F_BASELINE_cycles':aa['cycles'],'F_PRESSURE_EPOCH_cycles':bb['cycles'],'saved_cycles':aa['cycles']-bb['cycles'],'reduction_percent':100*(aa['cycles']-bb['cycles'])/aa['cycles'],'pressure_activation':bb.get('pressure_activation',{'status':'UNKNOWN'}),'interpretation':'NO_ACTIVATION is no proof of active-pressure RO efficacy; activation itself is not proof of performance benefit; joint trigger incidence not exported.'}
 result={'schema':'EP_MAIN_UMT1_EXACT4_ROLLING_SCIENTIFIC_RESULTS_V1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'counts':counts,'points':points,'comparisons':comparisons,'budgets':{g:{k:reg['registered_future_requests'][x['request_id']].get(k)for k in ['budget','remaining','state']}for g,x in manifest['groups'].items()},'authorized_starts':4,'no_retry':True,'no_refund':True,'Source_KEEP':True,'released_source_bytes':0,'old_Source78_context_not_matched_reference':True,'physical_PPA':'NOT_PROVEN','application_NI':'NOT_MEASURED','numeric_output':'UNKNOWN','not_global_project_model_limit':True}
 write(C/'PERFORMANCE_CURRENT.json',result)
 lines=['# UMT1 pressure-policy exact4 rolling scientific results','','Only CLOSED_ACCEPTED points with full application/drain, true164 SHA archive and two independent Native restores have accepted cycles. Other cells remain UNKNOWN. Source812 / ELFa606 /850MHz / L100 /G32x8 /FRFCFS128 /full283; only pressure_epoch0/1 differs.','','| Group | Mode | State | Accepted cycles | Activation |','|---|---|---|---:|---|']
 for p in points:lines.append('| '+p['group']+' | '+p['mode']+' | '+p['state']+' | '+str(p['cycles']if p['cycles']is not None else'UNKNOWN')+' | '+p.get('pressure_activation',{}).get('status','UNKNOWN')+' |')
 lines+=['','Counts: '+json.dumps(counts),'','## Matched comparisons','']
 for k,v in comparisons.items():lines.append('- '+k+': '+json.dumps(v))
 lines+=['','## Mechanism observations','']
 for p in points:
  if p['cycles']is not None:
   lines+=['- '+p['cohort']+': activation='+json.dumps(p.get('pressure_activation'))+'; ordinaryLine='+json.dumps(p.get('normal_line_pressure'))+'; productionCounters='+json.dumps(p.get('mechanisms'))+'; ROheadWaits='+json.dumps(p.get('RO_head_waits'))]
   if p.get('counter_gap'):lines+=['  Counter gap retained: '+p['counter_gap']]
 lines+=['','Full final64 per-slice counter records and active slice IDs are in CLOSED_COUNTERS. Line peak, actual block events, candidate+pressure coincidence, policy activation and complete-application performance are separate. Head waiting sums overlap and are not critical-path cycles; issued lower bytes are not completed DRAM bandwidth. Old Source78 results remain context only. Positive/negative/zero results and technical failures remain. No retry/refund. ApplicationNI/numerical-output/PPA limitations remain.','']
 (C/'PERFORMANCE_CURRENT.md').write_text('\n'.join(lines))
 return result
def api(method,path,body=None,missing=False):
 args=['/usr/local/bin/gh','api','-X',method,path]
 if body is not None:write(C/'PUBLICATION_API_REQUEST.json',body);args+=['--input',str(C/'PUBLICATION_API_REQUEST.json')]
 p=subprocess.run(args,capture_output=True,timeout=180)
 if p.returncode:
  if missing and b'404'in p.stderr:return None
  raise ValueError('GitHub API '+p.stderr.decode(errors='replace')[-500:])
 return json.loads(p.stdout)
def main():
 with (J/'execution_performance_first_20261103_v1/control/MAIN_GIT_PUBLICATION.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  current=report();expected=C/'PUBLICATION_EXPECTED_HEAD.json';base=read(expected)['head']if expected.exists()else BASE
  branch=api('GET',REPO+'/git/ref/heads/'+BRANCH,missing=True)
  if branch is None:
   assert base==BASE;branch=api('POST',REPO+'/git/refs',{'ref':'refs/heads/'+BRANCH,'sha':BASE})
  assert branch['object']['sha']==base,'remote moved, never force'
  files={}
  allowed=['USER_AUTHORIZATION.json','USER_AUTHORIZATION_SCOPE.txt','EXACT_EXECUTION_MANIFEST.json','EXACT4_ACTIVATION_PAYLOAD.json','MAIN_FORMAL_NATIVE_INSTALLATION_RECEIPT.json','MAIN_INDEPENDENT_HOST_ENGINEERING_REVIEW.json','MAIN_ENGINEERING_REVIEW_CONV.json','MAIN_ENGINEERING_REVIEW_SCAN.json','MAIN_EXECUTOR_ACTIVATION.json','MAIN_REAL_PREPARE_EXACT4.json','MAIN_REAL_PREPARE_EXACT4_V2.json','MAIN_PRECONSUME_ROUTE_SCHEMA_FIX.json','ROOT_LAUNCH_INTENT.json','ROOT_LAUNCH_ACK.json','EXECUTOR_STARTED.json','EXECUTOR_FINISHED.json','PERFORMANCE_CURRENT.json','PERFORMANCE_CURRENT.md','FINAL_SCOPE_CLOSURE.json','MAIN_COUNTER_COLLECTOR_DELTA_CHECK.json','main_activate_exact4.py','closed_counter_summary_umt1.py','main_publish_umt1_progress.py','main_metadata_watch_umt1.py','METADATA_WATCH_STARTED.json','METADATA_WATCH_FINISHED.json','ACTIVATION_TRUE164_ARCHIVE_RECEIPT.json','UMT1_FINAL_SCIENTIFIC_RESULTS_AND_CLOSEOUT.md','FINAL_REQUIREMENT_COMPLETION_AUDIT.json','main_final_requirement_audit_umt1.py','DUPLICATE_COUNTER_SEMANTICS_REVIEW.json','TAXONOMY_VALIDATION_FEEDBACK.json','FINAL_CLOSEOUT_TRUE164_RECEIPT.json','FINAL_SMALL_EVIDENCE_MANIFEST.json','main_publish_umt1_final_closeout.py']
  for name in allowed:
   p=C/name
   if p.exists():files['control/'+name]=p
  for p in C.glob('CLOSED_COUNTERS/*.json'):files['control/CLOSED_COUNTERS/'+p.name]=p
  for p in (C/'closed_scan_insert_review_20261107_v1').iterdir():
   if p.is_file()and p.suffix in ['.json','.py','.sh']:files['control/closed_scan_insert_review_20261107_v1/'+p.name]=p
  for g,z in read(C/'EXACT_EXECUTION_MANIFEST.json')['groups'].items():
   root=Path(z['data_root']);rt=Path(z['runtime_root'])
   for name in ['USER_AUTHORIZATION.json','USER_REQUEST.txt',z['route_file']]:files['formal/'+g+'/'+name]=root/'control'/name
   route=read(root/'control'/z['route_file']);rr=Path(route['shared_route_contract_ref']['path']);files['formal/'+g+'/'+rr.name]=rr
   for p in root.glob('cases/*/control/FROZEN_SPEC.json'):files['formal/'+g+'/'+p.parts[-3]+'/FROZEN_SPEC.json']=p
   for name in ['ep_perf_native_wv_modes_draft.py','ep_perf_common_v2.py','runtime_monitor_schema_v4_strict.py','native_route_guard_v3.py','mode_contract.py','mode_aware_terminal.py','ep_perf_archive.py','ep_perf_postprocess.py']:
    files['runtime/'+g+'/'+name]=rt/name
   for name in ['SOURCE812_NATIVE_RUNTIME_CLOSURE.json','RUNTIME_FULL43_CONTRACT.json','HOST_QUALIFICATION.json','TRACE_CHILD_HOST_DEPENDENCIES.json','INPUT_ELIGIBILITY.json','RO_QUALIFICATION.json']:
    files['engineering/'+g+'/'+name]=root.parent/'documents'/name
  for name in ['finite_main_exact4_candidate.py','resource_scope_umt1.py','resources_conv_umt1.py','resources_scan_umt1.py','DELIVERY_MANIFEST.json','READONLY_INITIAL_RESOURCE_SNAPSHOT.json','RESOURCE_IMMUTABLE_DEPENDENCIES.json']:
   files['engineering_dispatch/'+name]=A/'engineering_dispatch'/name
  for p in current['points']:
   for key in ['accepted_point_ref','archive_receipt_ref','done_ref']:
    if p.get(key):files['results/'+p['cohort']+'/'+key+'.json']=Path(p[key]['path'])
  entries=[];manifest=[]
  for name,p in sorted(files.items()):
   original=p.read_bytes();b=(json.dumps(clean(json.loads(original)),sort_keys=True,separators=(',',':'))+'\n').encode()if p.suffix=='.json'else original
   assert len(b)<2*(1<<20)
   entries.append({'path':PREFIX+'/'+name,'mode':'100644','type':'blob','content':b.decode()})
   manifest.append({'file':name,'original_ref':ref(p),'export_sha256':hashlib.sha256(b).hexdigest(),'export_bytes':len(b),'raw_preserved':b==original})
  note='# UMT1 authorized Conv2 + Scan2 execution\n\nFour independent starts were explicitly approved after reviewing838faa. This is a finite new scope, not an EP project lifetime cap. Exact Sources/inputs/283 maps, limits, Native43/22+5 qualification and dynamic resources are frozen before launch. Conv12h,Scan72h; no model retry/refund. Short and long points release independently.\n\nSee [rolling accepted results](control/PERFORMANCE_CURRENT.md), [full structured results](control/PERFORMANCE_CURRENT.json), [immutable execution manifest](control/EXACT_EXECUTION_MANIFEST.json), [user scope](control/USER_AUTHORIZATION.json) and [original taxonomy](../README.md). These review copies do not relocate Native execution authority. Source KEEP; old V3?V5 results and failures remain.\n'
  note+='\nFinal: all4 accepted, both budgets closed, eight independent Native full restores. See [final scientific report](control/UMT1_FINAL_SCIENTIFIC_RESULTS_AND_CLOSEOUT.md), [independent complete requirement audit](control/FINAL_REQUIREMENT_COMPLETION_AUDIT.json), [reviewed closed Scan route incident](control/closed_scan_insert_review_20261107_v1/MAIN_INSERT_ONLY_REVIEW.json) and [true164 final report evidence](control/FINAL_CLOSEOUT_TRUE164_RECEIPT.json). No model rerun or refund.\n'
  entries.append({'path':PREFIX+'/README.md','mode':'100644','type':'blob','content':note})
  entries.append({'path':PREFIX+'/REVIEW_EXPORT_MANIFEST.json','mode':'100644','type':'blob','content':json.dumps({'files':manifest,'recursive_secret_redaction':True,'review_only':True},sort_keys=True,indent=2)+'\n'})
  assert sum(len(e['content'].encode())for e in entries)<12*(1<<20)
  tree=api('GET',REPO+'/git/commits/'+base)['tree']['sha']
  for i in range(0,len(entries),30):tree=api('POST',REPO+'/git/trees',{'base_tree':tree,'tree':entries[i:i+30]})['sha']
  co=api('POST',REPO+'/git/commits',{'message':'UMT1 exact4: '+str(current['counts']['accepted'])+' accepted, '+str(current['counts']['technical_failure'])+' failures; independent pressure-policy execution','tree':tree,'parents':[base]})
  assert api('GET',REPO+'/git/ref/heads/'+BRANCH)['object']['sha']==base
  api('PATCH',REPO+'/git/refs/heads/'+BRANCH,{'sha':co['sha'],'force':False})
  assert api('GET',REPO+'/git/ref/heads/'+BRANCH)['object']['sha']==co['sha']
  subtree=tree
  for part in PREFIX.split('/'):
   d=api('GET',REPO+'/git/trees/'+subtree);subtree=next(x['sha']for x in d['tree']if x['path']==part and x['type']=='tree')
  d=api('GET',REPO+'/git/trees/'+subtree+'?recursive=1');assert not d.get('truncated');by={x['path']:x['sha']for x in d['tree']if x['type']=='blob'}
  for e in entries:
   b=e['content'].encode();assert by[e['path'][len(PREFIX)+1:]]==hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
  receipt={'status':'REMOTE_EXACT_HEAD_AND_ALL_EXPORTED_GIT_BLOBS_VERIFIED','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':co['sha'],'parent':base,'branch':BRANCH,'prefix':PREFIX,'files':len(entries),'counts':current['counts']}
  write(C/'REMOTE_FINAL_CLOSEOUT_PUBLICATION_RECEIPT.json',receipt);write(expected,{'head':co['sha']})
  print(json.dumps(receipt))
if __name__=='__main__':main()
