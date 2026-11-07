"""Main exact closed-Scan insert-only Native review. No model start or shared Native write."""
from pathlib import Path
import json,hashlib,re,datetime,fcntl,os,copy,argparse
C=Path(__file__).resolve().parent.parent;OUT=Path(__file__).resolve().parent
N=Path('/root/data/ep_l2_dtc_l1_native_v2');REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';EPOCH=N/'control/CURRENT_SCIENCE_EPOCH.json';NATIVE=N/'bin/native'
FOREIGN=Path('/root/data/dtc_controlled_oracle_20261106_v1/initial8')
HEADER=b'#!/bin/sh\nset -eu\n'
PATTERN=re.compile(r'E2-DTCORACLE-I8-[0-9a-f]{16}-DH-(OFF_MATCHED|M_DATAREAD|L2_DATAREAD|L1_DATAREADY)-V1')
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def exact(r):
 assert sha(r['path'])==r['sha256'],'ref drift '+r['path'];return read(r['path'])
def put(p,d):
 p=Path(p);t=p.with_name('.'+p.name+'.tmp');t.write_text(json.dumps(d,sort_keys=True,indent=2)+'\n');os.replace(t,p)
def pre(p):
 p=Path(p);d=OUT/'preimages'/sha(p);d.mkdir(parents=True,exist_ok=True);f=d/p.name
 if not f.exists():f.write_bytes(p.read_bytes())
def validate_route(current,baseline,block,auth,foreign_q,own):
 assert baseline.startswith(HEADER)
 assert current==HEADER+block+baseline[len(HEADER):],'not exact one insert preserving every old byte'
 text=block.decode();lines=text.splitlines()
 assert len(lines)==9 and lines[0]=='# DTC_ORACLE_INITIAL8_V1_ROUTE; exact conditional authorized rows only.'
 assert lines[1:3]==['if [ "$#" -ge 3 ]; then',' case "$1:$3" in']
 assert lines[3].startswith('  ')and lines[3].endswith(')')
 tokens=lines[3][2:-1].split('|');assert len(tokens)%2==0
 cohorts=[]
 for i in range(0,len(tokens),2):
  assert tokens[i].startswith('experiment:');co=tokens[i].split(':',1)[1]
  assert PATTERN.fullmatch(co)and tokens[i+1]=='result:'+co
  cohorts.append(co)
 assert len(cohorts)==len(set(cohorts))==32
 assert set(cohorts).isdisjoint(own)
 handler=str(FOREIGN/'tools/oracle_frontend.py')
 expected=('# DTC_ORACLE_INITIAL8_V1_ROUTE; exact conditional authorized rows only.\n'
 'if [ "$#" -ge 3 ]; then\n case "$1:$3" in\n  '+'|'.join(v+':'+co for co in cohorts for v in ['experiment','result'])+')\n'
 '   export DTC_CONTROLLED_ORACLE_NATIVE_ENTRY=1\n'
 '   exec /usr/bin/python3 -B '+handler+' "$@"\n   ;;\n esac\nfi\n').encode()
 assert block==expected,'grammar/handler/env/shell command changed'
 assert auth['explicit_user_approval']is True and auth['ready_for_registration']is True
 assert set(auth['budgets'])==set(cohorts)==set(foreign_q['admitted_specs'])
 assert all(v==1 for v in auth['budgets'].values())and foreign_q['budget']==32
 assert auth['authority_commit']==foreign_q['approved_contract_commit']==foreign_q['authority_commit']
 assert auth['approval_request_sha256']==foreign_q['spec_request_sha256']
 return cohorts
def review():
 m=read(C/'EXACT_EXECUTION_MANIFEST.json');own={p['cohort']for p in m['points']}
 z=m['groups']['SCAN'];root=Path(z['data_root']);rp=root/'control'/z['route_file'];route=read(rp);contract=exact(route['shared_route_contract_ref'])
 baseline=Path(contract['installed_baseline_ref']['path']).read_bytes();assert hashlib.sha256(baseline).hexdigest()==contract['installed_baseline_ref']['sha256']
 current=NATIVE.read_bytes();block=(FOREIGN/'control/NATIVE_ROUTE_BLOCK.sh').read_bytes();auth=read(FOREIGN/'control/SCIENCE_AUTHORIZATION.json')
 reg=read(REG);fq=reg['registered_future_requests']['DTC_ORACLE_INITIAL8_20261106_V1']
 cohorts=validate_route(current,baseline,block,auth,fq,own)
 qa=0
 for bcur,bb,ba in [(current+b'\n:',block,auth),(current,block.replace(b'oracle_frontend.py',b'other.py'),auth),(current.replace(b'EP-MAIN authorized UMT1',b'EP-MAIN altered UMT1'),block,auth),(current,block.replace(b'E2-DTCORACLE-I8-',b'EP_PERF_'),auth),(current,block.replace(b'OFF_MATCHED-V1',b'OFF_MATCHED-*'),auth)]:
  try:validate_route(bcur,baseline,bb,ba,fq,own)
  except AssertionError:qa+=1
 assert qa==5
 OUT.mkdir(exist_ok=True);snap=OUT/'REVIEWED_CURRENT_NATIVE_EXACT_SNAPSHOT.sh'
 if snap.exists():assert snap.read_bytes()==current
 else:snap.write_bytes(current)
 original=OUT/'ORIGINAL_INSTALLED_NATIVE_BASELINE.sh'
 if original.exists():assert original.read_bytes()==baseline
 else:original.write_bytes(baseline)
 (OUT/'FOREIGN_INSERTED_BLOCK_ONLY.sh').write_bytes(block)
 points=[];q=reg['registered_future_requests'][z['request_id']]
 assert q['remaining']==0 and len(q['consumed'])==2
 for p in m['points']:
  if p['group']!='SCAN':continue
  r=q['consumed'][p['cohort']];assert r['state']=='NATURAL_COMPLETE_PENDING_VALIDATION'
  s=exact(p['spec_ref']);d=exact(r['done_ref'])
  assert d['spec_ref']==p['spec_ref']and d['source_identity']==s['source_identity']
  assert d['launcher_wait_returncode']==0 and d['stop_reason']is None and d['new_attempt_consumed']==1
  assert d['syscall_proof']['status']=='CLOSED_LOCAL_SYSCALL_INPUT_NETWORK_PROOF_PASS'
  pm=exact(d['closed_artifact_refs']['NATIVE_SIMULATOR_PID_AND_MAPS.json'])
  ps=Path('/proc/%d/stat'%pm['pid'])
  if ps.exists():assert int(ps.read_text().rsplit(')',1)[1].split()[19])!=pm['start_ticks'],'original generation still live'
  for rr in list(d['closed_artifact_refs'].values())+[d['raw_compressed_ref']]:assert sha(rr['path'])==rr['sha256']
  assert sha(Path(r['output'])/'FROZEN_SPEC.json')==p['spec_ref']['sha256']
  for path,h in s['pinned_files'].items():assert sha(path)==h
  assert sha(s['binary_path'])==s['source_identity']['binary_sha256']
  points.append({'cohort':p['cohort'],'uuid':r['uuid'],'spec_ref':p['spec_ref'],'done_ref':r['done_ref'],'raw_ref':d['raw_compressed_ref'],'model_generation_nonlive':True,'elapsed_seconds':d['elapsed_seconds']})
 result={'schema':'EP_MAIN_UMT1_CLOSED_SCAN_EXACT_INSERT_REVIEW_V1','status':'EXACT_ONE_AUTHORIZED_FINITE_FOREIGN_INSERTION_OLD_NATIVE_SUFFIX_PRESERVED','approved_by':'EP-MAIN','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'POSTRUN_CLOSED_SCAN_METADATA_ONLY','new_model_authority':False,'shared_Native_modified':False,'original_launch_baseline_ref':ref(original),'reviewed_current_snapshot_ref':ref(snap),'foreign_inserted_block_ref':ref(OUT/'FOREIGN_INSERTED_BLOCK_ONLY.sh'),'foreign_authorization_ref':ref(FOREIGN/'control/SCIENCE_AUTHORIZATION.json'),'foreign_frontend_ref':ref(FOREIGN/'tools/oracle_frontend.py'),'foreign_cohorts':cohorts,'foreign_request':'DTC_ORACLE_INITIAL8_20261106_V1','reviewed_scan_results':points,'negative_grammar_checks':qa,'consumer_numeric_monitor_Source_Spec_raw_unchanged':True,'future_unknown_route_mutation':'FAIL_CLOSED_EXACT_SNAPSHOT_ONLY'}
 put(OUT/'MAIN_INSERT_ONLY_REVIEW.json',result);return result,rp,contract
def apply():
 result,rp,contract=review();request=read(C/'EXACT_EXECUTION_MANIFEST.json')['groups']['SCAN']['request_id'];locks=[]
 try:
  for n in ['REGISTRY_UPDATE.lock','NATIVE_ROUTE_UPDATE.lock']:
   f=(N/'control/science_authority'/n).open('a+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  assert NATIVE.read_bytes()==Path(result['reviewed_current_snapshot_ref']['path']).read_bytes()
  reg=read(REG);epoch=read(EPOCH);assert sha(REG)==epoch['native_registry_sha256'];before=copy.deepcopy(reg)
  route=read(rp);cp=Path(route['shared_route_contract_ref']['path']);original_contract=read(cp)
  assert original_contract==contract
  for p in [rp,cp,REG,EPOCH]:pre(p)
  contract['original_launch_installed_baseline_ref']=contract['installed_baseline_ref']
  contract['installed_baseline_ref']=result['reviewed_current_snapshot_ref']
  contract['Main_closed_result_insert_only_review_ref']=ref(OUT/'MAIN_INSERT_ONLY_REVIEW.json')
  contract['postrun_only_no_new_model_authority']=True
  put(cp,contract)
  route['shared_route_contract_ref']=ref(cp)
  route['original_launch_global_shared_native_ref']=route['global_shared_native_ref']
  route['global_shared_native_ref']={'path':str(NATIVE),'sha256':result['reviewed_current_snapshot_ref']['sha256']}
  route['Main_postrun_insert_only_review_ref']=ref(OUT/'MAIN_INSERT_ONLY_REVIEW.json');put(rp,route)
  q=reg['registered_future_requests'][request];assert q['remaining']==0
  q['native_qualification_ref']=ref(rp);q['Main_closed_result_insert_only_review_ref']=ref(OUT/'MAIN_INSERT_ONLY_REVIEW.json')
  assert q['consumed']==before['registered_future_requests'][request]['consumed']and q['admitted_specs']==before['registered_future_requests'][request]['admitted_specs']
  assert all(reg['registered_future_requests'][k]==v for k,v in before['registered_future_requests'].items()if k!=request)
  for p in [REG,EPOCH]:
   dst=N/'control/science_authority/request_history'/(p.stem+'.'+sha(p)+'.json')
   if not dst.exists():dst.write_bytes(p.read_bytes())
  put(REG,reg);epoch['native_registry_sha256']=sha(REG);epoch['request_revision']={'operation':'EP_MAIN_UMT1_CLOSED_SCAN_EXACT_REVIEWED_INSERT_ONLY_ROUTE_RESEAL_NO_START','request_id':request,'review_ref':ref(OUT/'MAIN_INSERT_ONLY_REVIEW.json'),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};put(EPOCH,epoch)
  assert sha(NATIVE)==result['reviewed_current_snapshot_ref']['sha256']
  receipt={'status':'CLOSED_SCAN_OWN_ROUTE_RESEALED_TO_EXACT_MAIN_REVIEWED_CURRENT_BYTES','review_ref':ref(OUT/'MAIN_INSERT_ONLY_REVIEW.json'),'route_ref':ref(rp),'consumed_rows_and_specs_unchanged':True,'all_other_registry_rows_unchanged':True,'shared_Native_bytes_unchanged':True,'new_scientific_starts':0,'retries':0,'refunds':0}
  put(OUT/'MAIN_APPLY_RECEIPT.json',receipt);print(json.dumps(receipt))
 finally:
  for f in locks[::-1]:f.close()
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');args=ap.parse_args()
 if args.apply:apply()
 else:r,_,_=review();print(json.dumps({'status':r['status'],'scans':len(r['reviewed_scan_results']),'negative_checks':r['negative_grammar_checks'],'new_scientific_starts':0}))
