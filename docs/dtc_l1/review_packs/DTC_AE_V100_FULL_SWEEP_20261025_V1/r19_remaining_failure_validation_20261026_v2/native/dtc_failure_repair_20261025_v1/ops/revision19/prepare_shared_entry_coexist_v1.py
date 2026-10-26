import pathlib,json,hashlib,os,subprocess,tempfile,shutil,datetime,importlib.util
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/revision19';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');L=F/'validation_late_failure_v1';X=F/'validation_remaining_failure_v1';N=P('/root/data/ep_l2_dtc_l1_native_v2');entry=N/'bin/native';hist=D/'aborted_shared_entry_activation_v1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
assert not(L/'control/CONTROLLER_START_R19.json').exists();hist.mkdir(exist_ok=True);assert not list(hist.iterdir());q=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');assert 'DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1'not in q['registered_future_requests']
assert all(q['registered_future_requests'][k]['orchestrator_sha256']=='b7c302aff28712729efc4c06d5744e8cd184c115a069b2536c52b2cba45e6b31'for k in['DTC_AE_V100_FULL_SWEEP_20261025_V1','DTC_AE_LAVAMEM_REPAIR_20261026_V2','DTC_AE_LATE_FAILURE_REPAIR_20261026_V1'])
before=entry.read_bytes();old=read(F/'ops/R19_ZERO_MODEL_QUALIFICATION_V1.json');assert sha(entry)=='dc7c232b944691379aaa42417abd7d622114abc148ecb6fdf72aebf6ecbf3f66';assert str(F/'ops/revision18/frontend_v1.py').encode()not in before
route='''# Exact DTC continuation prefixes; EP and other routes below are preserved.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-AEV100-*|experiment:E2-AEREPAIR-LAVAMEM2-*|experiment:E2-AEREPAIR-LATE4-*|experiment:E2-AEREPAIR-REMAIN4-*|result:E2-AEREPAIR-REMAIN4-*)
   exec /usr/bin/python3 -B /root/data/dtc_failure_repair_20261025_v1/ops/revision18/frontend_v1.py "$@"
   ;;
 esac
fi
'''.encode();anchor=b'#!/bin/sh\nset -eu\n';assert before.startswith(anchor);after=anchor+route+before[len(anchor):];assert after.replace(route,b'',1)==before and after.count(str(F/'ops/revision18/frontend_v1.py').encode())==1
candidate=D/'NATIVE_SHARED_ENTRY_COEXIST_CANDIDATE_V1.sh';candidate.write_bytes(after);subprocess.run(['/bin/sh','-n',str(candidate)],check=True)
checks=[]
with tempfile.TemporaryDirectory(prefix='R19_SHARED_ROUTE_CPU_',dir=D)as td:
 root=P(td);stub=root/'route_stub.py';stub.write_text('import sys,json;print(json.dumps(sys.argv[1:]))\n')
 # Shell dispatch is real. Absolute external commands are replaced only in this
 # isolated CPU copy so no actual native frontend/model can be invoked.
 text=after.decode().replace('exec /usr/bin/python3 -B '+str(F/'ops/revision18/frontend_v1.py'),'exec /usr/bin/python3 '+str(stub)+' DTC').replace('exec /usr/bin/python3 -B /root/data/ep_memory_path_sensitivity_20261026_v1/tools/e2_fresh_input_dispatch.py','exec /usr/bin/python3 '+str(stub)+' EP').replace('exec /bin/sh /root/data/ep_memory_path_sensitivity_20261026_v1/tools/prior_to_e2_entry.sh','exec /usr/bin/python3 '+str(stub)+' FALLBACK');cpu=root/'entry.sh';cpu.write_text(text)
 for argv,label in[(['experiment','prepare','E2-AEV100-X','--project','DTC_L1'],'DTC'),(['experiment','run-native','E2-AEREPAIR-LAVAMEM2-X'],'DTC'),(['experiment','inspect','E2-AEREPAIR-LATE4-X'],'DTC'),(['experiment','run-native','E2-AEREPAIR-REMAIN4-X'],'DTC'),(['result','archive','E2-AEREPAIR-REMAIN4-X'],'DTC'),(['experiment','prepare','EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1'],'EP'),(['result','archive','EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1'],'EP'),(['experiment','prepare','EP_NATIVE_VECTOR_DRAM935_SENSITIVITY_20261026_V1'],'FALLBACK'),(['status'],'FALLBACK'),(['experiment','prepare','OTHER'],'FALLBACK')]:
  got=json.loads(subprocess.check_output(['/bin/sh',str(cpu),*argv],text=True));assert got==[label,*argv];checks.append(dict(argv=argv,route=label,status='PASS'))
 assert before==after.replace(route,b'',1);checks.append(dict(name='old shared EP wrapper bytes reconstruct exactly; DTC prefix unique; sh syntax valid',status='PASS'))
put(D/'SHARED_ENTRY_COEXIST_CPU_QUALIFICATION_V1.json',dict(status='PASS',check_count=len(checks),checks=checks,source_before_sha256=sha(entry),candidate_sha256=sha(candidate),driver_sha256=sha(__file__),real_frontend_or_model_starts=0,EP_or_delegated_source_writes=0))
preserve=[F/'ops/R19_ZERO_MODEL_QUALIFICATION_V1.json',F/'ops/R19_PUBLICATION_READBACK_V1.json',L/'control/CONTROLLER_LAUNCH_R19.json',L/'control/PARENT_TRANSFER_R19_PREIMAGE.json',L/'logs/CONTROLLER_R19.stdout.log',X/'control/OLD_LIVE_RUNTIME_CORRECTION_PREFLIGHT_R19.json',L/'control/OLD_REPAIR_REQUEST_BEFORE_R19.json']
preserve += [r/'control/REQUEST_BEFORE_R19.json'for r in[T,F/'validation_lava_memory_v2',L,X]]
records=[]
for p in preserve:
 assert p.exists(),p;rel=str(p.relative_to(F))if p.is_relative_to(F)else'original/'+p.name;dst=hist/rel;dst.parent.mkdir(parents=True,exist_ok=True);digest=sha(p);p.rename(dst);assert sha(dst)==digest;records.append(dict(original_path=str(p),preserved_path=str(dst),sha256=digest))
(hist/'native_entry_before.bytes').write_bytes(before);temp=entry.with_name('.native.DTC_COEXIST_writing');temp.write_bytes(after);temp.chmod(entry.stat().st_mode&0o777);assert entry.read_bytes()==before,'concurrent shared entry update; preserve other lane and do not apply';temp.replace(entry);assert sha(entry)==sha(candidate)
put(D/'SHARED_ENTRY_COEXIST_APPLY_RECEIPT_V1.json',dict(status='DTC_R18_PREFIX_ADDED_WITH_EXACT_SHARED_EP_BYTES_PRESERVED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),native_entry_before_sha256=hashlib.sha256(before).hexdigest(),native_entry_after_sha256=sha(entry),CPU_qualification_sha256=sha(D/'SHARED_ENTRY_COEXIST_CPU_QUALIFICATION_V1.json'),preserved_aborted_zero_activation_files=records,new_request_registered=False,scientific_model_starts=0,old_q_budget_or_spent_writes=0,old_R18_parent_remains_departed=True))
print(json.dumps(dict(status='PASS',checks=len(checks),entry_sha256=sha(entry),preserved_zero_activation_files=len(records))))
