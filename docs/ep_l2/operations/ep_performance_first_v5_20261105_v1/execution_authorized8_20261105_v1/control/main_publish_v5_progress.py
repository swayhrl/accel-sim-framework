"""Main finite V5 metadata publisher. Read results; never launches or changes science."""
from pathlib import Path
import json,hashlib,subprocess,fcntl,datetime,sys,os
C=Path(__file__).resolve().parent;V=C.parent.parent;J=V.parent.parent
REG=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
BRANCH='hrl/ep-l2-performance-first-v5-20261105-v1';BASE='a7318d0fe51bbd00b94da095bd925c60a06f0750'
REPO='repos/swayhrl/accel-sim-framework'
PREFIX='docs/ep_l2/operations/ep_performance_first_v5_20261105_v1/execution_authorized8_20261105_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def ref(p):return dict(path=str(p),sha256=sha(p))
def write(p,o):
 p=Path(p);t=p.with_name('.'+p.name+'.tmp')
 t.write_text(json.dumps(o,sort_keys=True,indent=2)+'\n');os.replace(t,p)
def exact(r):
 assert sha(r['path'])==r['sha256'],'evidence drift '+r['path'];return read(r['path'])
def clean(v):
 if isinstance(v,dict):return{k:clean(x)for k,x in v.items()if not any(w in k.lower()for w in ['token','nonce','secret'])}
 if isinstance(v,list):return[clean(x)for x in v]
 return v
def api(method,path,body=None):
 args=['/usr/local/bin/gh','api','-X',method,path]
 if body is not None:write(C/'PUBLICATION_API_REQUEST.json',body);args+=['--input',str(C/'PUBLICATION_API_REQUEST.json')]
 p=subprocess.run(args,capture_output=True,timeout=180)
 if p.returncode:raise ValueError('GitHub API '+method+' '+p.stderr.decode(errors='replace')[-800:])
 return json.loads(p.stdout)
def report():
 m=read(C/'EXACT_EXECUTION_MANIFEST.json');reg=read(REG);rows=[];cycles={};counts={'accepted':0,'technical_failure':0,'pending':0}
 for p in m['points']:
  g=m['groups'][p['group']];s=exact(p['spec_ref']);q=reg['registered_future_requests'][g['request_id']];r=q['consumed'].get(p['cohort'],{});state=r.get('state','NOT_STARTED')
  item=dict(cohort=p['cohort'],group=p['group'],mode=s['mode'],source_identity=s['source_identity'],state=state,consumed=bool(r),uuid=r.get('uuid'),cycles=None,spec_ref=p['spec_ref'],host_limits=s['limits'],independent_release=True)
  for k in ['done_ref','accepted_point_ref','archive_receipt_ref','validation_ref']:item[k]=r.get(k)
  if r.get('done_ref'):
   d=exact(r['done_ref']);item['elapsed_seconds']=d.get('elapsed_seconds');item['stop_reason']=d.get('stop_reason');item['launcher_wait_returncode']=d.get('launcher_wait_returncode')
  if state=='CLOSED_ACCEPTED':
   a=exact(r['accepted_point_ref']);ar=exact(r['archive_receipt_ref']);rest=ar['native_restores']
   assert a['cohort']==p['cohort']and a['uuid']==r['uuid']==ar['uuid']and a['spec_ref']['sha256']==p['spec_ref']['sha256']and a['hardware_drained']is True
   assert a['source_identity']==s['source_identity']and a['input_identity_sha256']==s['input_identity_sha256']
   assert ar['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS'and len(rest)==2 and len({x['target']for x in rest})==2
   assert all(x['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS'and x['archive_sha256']==ar['archive_ref']['sha256']for x in rest)
   item.update(cycles=a['cycles'],instructions=a['instructions'],CTA=a['CTA'],kernel_count=a['kernel_count'],hardware_drained=True,archive_two_restores=True)
   cycles[p['cohort']]=a['cycles'];counts['accepted']+=1
  elif state=='CLOSED_UNACCEPTED':counts['technical_failure']+=1
  else:counts['pending']+=1
  rows.append(item)
 def compare(a,b):
  if a not in cycles or b not in cycles:return dict(status='UNKNOWN_UNTIL_BOTH_EXACT_CELLS_ACCEPTED')
  x,y=cycles[a],cycles[b];return dict(reference_cycles=x,candidate_cycles=y,saved_cycles=x-y,reduction_percent=100*(x-y)/x)
 comparisons={
 'B_same_newSource_F_pressure_vs_Fbaseline':compare('EP_PERF_PFV5_B1_VECTOR4M_F_BASELINE_1700_V1','EP_PERF_PFV5_B1_VECTOR4M_F_PRESSURE_EPOCH_1700_V1'),
 'A_cold_ON_vs_OFF':compare('EP_PERF_PFV5_A_FWT_G32W8_WV_OFF_V1','EP_PERF_PFV5_A_FWT_G32W8_WV_ON_V1'),
 'A_WV_OFF_vs_S':compare('EP_PERF_PFV5_A_FWT_G32W8_S_V1','EP_PERF_PFV5_A_FWT_G32W8_WV_OFF_V1'),
 'A_WV_ON_vs_S':compare('EP_PERF_PFV5_A_FWT_G32W8_S_V1','EP_PERF_PFV5_A_FWT_G32W8_WV_ON_V1'),
 'D_G64_WV_vs_S':compare('EP_PERF_PFV4_A2_3MM_S_G64W8_V1','EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_G64W8_V1'),
 'D_WV_G64_vs_REF32':compare('EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_REF32W8_V1','EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_G64W8_V1')}
 d='EP_PERF_PFV4_A2_3MM_S_G64W8_V1'
 comparisons['D_S_G64_vs_accepted_S_REF32']=dict(reference_cycles=1696618,candidate_cycles=cycles[d],saved_cycles=1696618-cycles[d],reduction_percent=100*(1696618-cycles[d])/1696618)if d in cycles else dict(status='UNKNOWN_UNTIL_EXACT_G64_S_ACCEPTED')
 out=dict(schema='EP_MAIN_PFV5_ROLLING_EXACT8_RESULTS_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),counts=counts,points=rows,comparisons=comparisons,budgets={g:{k:reg['registered_future_requests'][z['request_id']].get(k)for k in ['budget','remaining','state']}for g,z in m['groups'].items()},all_eight_independently_released=True,complete_scientific_scope=8,automatic_model_retry=False,refund=False,C_models_authorized=0,application_NI='NOT_MEASURED',physical_PPA='NOT_PROVEN',numeric_output='UNKNOWN',Source_KEEP=True)
 write(C/'PERFORMANCE_CURRENT.json',out)
 lines=['# EP-L2 V5 exact8 rolling results','','Only CLOSED_ACCEPTED cells with full true164 archive and two distinct Native restores have published accepted cycles. Missing cells are UNKNOWN. All eight cells release independently.','','| Group | Cohort | State | Accepted cycles |','|---|---|---|---:|']
 for r in rows:lines+=['| '+r['group']+' | '+r['cohort']+' | '+r['state']+' | '+str(r['cycles']if r['cycles']is not None else'UNKNOWN')+' |']
 lines+=['','Counts: '+json.dumps(counts), '','## Matched comparisons','']
 for k,v in comparisons.items():lines+=['- '+k+': '+json.dumps(v)]
 lines+=['','A cold filter is lifetime never-installed proof, not general empty-directory detection. B retains full query port and cycle costs. C remains partial production engineering with no science starts. 1700MHz is service diagnostic, not GPU calibration.','']
 (C/'PERFORMANCE_CURRENT.md').write_text('\n'.join(lines))
 return out
def main():
 with (J/'execution_performance_first_20261103_v1/control/MAIN_GIT_PUBLICATION.lock').open('a+b')as l:
  fcntl.flock(l,fcntl.LOCK_EX)
  current=report();basefile=C/'PUBLICATION_EXPECTED_HEAD.json';base=read(basefile)['head']if basefile.exists()else BASE
  assert api('GET',REPO+'/git/ref/heads/'+BRANCH)['object']['sha']==base,'no force on moved branch'
  files={}
  allowed=['USER_REQUEST_SCOPE_TRANSCRIPTION.txt','USER_AUTHORIZATION.json','A_USER_AUTHORIZATION.json','B_USER_AUTHORIZATION.json','D_USER_AUTHORIZATION.json','A_MAIN_HOST_DELTA_APPROVAL.json','B_MAIN_HOST_DELTA_APPROVAL.json','D_MAIN_HOST_DELTA_APPROVAL.json','EXACT_EXECUTION_MANIFEST.json','MAIN_FORMAL_NATIVE_INSTALLATION_RECEIPT.json','MAIN_FINAL_SPEC_ACTIVATION_DIFFERENCES.json','ROOT_LAUNCH_ACK.json','MAIN_DISPATCHER_STARTUP_REVIEW.json','PERFORMANCE_CURRENT.json','PERFORMANCE_CURRENT.md','EXECUTOR_STARTED.json','EXECUTOR_FINISHED.json','MAIN_EXECUTOR_ACTIVATION.json','MAIN_REAL_PREPARE_AFTER_INSTALL.json','FINAL_SCOPE_CLOSURE.json','main_activate_exact8.py','main_publish_v5_progress.py','main_metadata_watch_v5.py']
  for name in allowed:
   p=C/name
   if p.exists():files['control/'+name]=p
  m=read(C/'EXACT_EXECUTION_MANIFEST.json')
  for g,z in m['groups'].items():
   root=Path(z['data_root']);rt=Path(z['runtime_root'])
   for name in ['USER_AUTHORIZATION.json',z['route_file']]:
    p=root/'control'/name;files['formal/'+g+'/'+name]=p
   for p in root.glob('cases/*/control/FROZEN_SPEC.json'):files['formal/'+g+'/'+p.parts[-3]+'/FROZEN_SPEC.json']=p
   for name in ['ep_perf_native_wv_modes_draft.py','ep_perf_frontend.py','native_route_guard_v3.py']:
    p=rt/name;files['runtime_delta/'+g+'/'+name]=p
  for eroot in [V/'activation_20261105_v1/engineering_a',V/'activation_20261105_v1/engineering_b',V/'activation_20261105_v1/engineering_d']:
   for p in eroot.glob('*'):
    if p.is_file()and p.suffix in ['.py','.json','.md']and p.stat().st_size<1024*1024 and p.name not in ['SAVED_SOURCE.json']:
     files['engineering/'+eroot.name+'/'+p.name]=p
  entries=[];manifest=[]
  for name,p in sorted(files.items()):
   raw=p.read_bytes();out=(json.dumps(clean(json.loads(raw)),sort_keys=True,indent=2)+'\n').encode()if p.suffix=='.json'else raw
   entries.append(dict(path=PREFIX+'/'+name,mode='100644',type='blob',content=out.decode('utf-8')))
   manifest.append(dict(path=name,original_ref=ref(p),export_sha256=hashlib.sha256(out).hexdigest(),bytes=len(out),raw_preserved=out==raw))
  note='# EP-L2 V5 authorized exact8 execution\n\nUser authorized A3+B2+D3 as three independent fresh scientific scopes after reviewing a7318d0. All eight release independently under current Source/Host/Native/resource gates and EP cap10. No baseline/reference completion gate. B hard wall2h, A8h, D72h; previous900s/3600s/12h14h are soft references only. No model retry or refund. C engineering only. Old V3/V4 records remain unchanged.\n\nSee [rolling accepted performance](control/PERFORMANCE_CURRENT.md), [exact immutable execution manifest](control/EXACT_EXECUTION_MANIFEST.json), and [parent engineering request](../V5_ARCHITECTURE_CANDIDATE_AND_EXPERIMENT_REQUEST.md). This snapshot is review-only, not relocated execution authority. Source KEEP.\n'
  entries.append(dict(path=PREFIX+'/README.md',mode='100644',type='blob',content=note))
  entries.append(dict(path=PREFIX+'/REVIEW_EXPORT_MANIFEST.json',mode='100644',type='blob',content=json.dumps(dict(schema='V5_EXACT8_PROGRESS_REVIEW_EXPORT_V1',files=manifest,review_only=True,redaction='recursive JSON token/nonce/secret keys omitted; original vs export SHA explicit'),sort_keys=True,indent=2)+'\n'))
  assert sum(len(x['content'].encode())for x in entries)<8*(1<<20),'bounded metadata export'
  bc=api('GET',REPO+'/git/commits/'+base)
  tree=bc['tree']['sha']
  for i in range(0,len(entries),40):tree=api('POST',REPO+'/git/trees',dict(base_tree=tree,tree=entries[i:i+40]))['sha']
  commit=api('POST',REPO+'/git/commits',dict(message='EP V5 exact8 progress: '+str(current['counts']['accepted'])+' accepted, '+str(current['counts']['technical_failure'])+' technical failures',tree=tree,parents=[base]))
  assert api('GET',REPO+'/git/ref/heads/'+BRANCH)['object']['sha']==base,'concurrent publisher moved head'
  api('PATCH',REPO+'/git/refs/heads/'+BRANCH,dict(sha=commit['sha'],force=False))
  assert api('GET',REPO+'/git/ref/heads/'+BRANCH)['object']['sha']==commit['sha']
  subtree=tree
  for part in PREFIX.split('/'):
   obj=api('GET',REPO+'/git/trees/'+subtree);subtree=next(x['sha']for x in obj['tree']if x['path']==part and x['type']=='tree')
  out=api('GET',REPO+'/git/trees/'+subtree+'?recursive=1');assert not out.get('truncated');by={x['path']:x['sha']for x in out['tree']if x['type']=='blob'}
  for e in entries:
   b=e['content'].encode();path=e['path'][len(PREFIX)+1:];assert by[path]==hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'remote blob mismatch'
  receipt=dict(status='EXACT_REMOTE_HEAD_AND_EVERY_EXPORTED_BLOB_VERIFIED',head=commit['sha'],parent=base,files=len(entries),counts=current['counts'],utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prefix=PREFIX)
  write(C/'REMOTE_PROGRESS_PUBLICATION_RECEIPT.json',receipt);write(basefile,dict(head=commit['sha']));print(json.dumps(receipt))
if __name__=='__main__':main()
