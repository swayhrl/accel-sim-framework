import pathlib,json,importlib.util,hashlib,copy,difflib,ast
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');GIB=1024**3
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
guard=load('floor5_guard',T/'tools/short3_storage_guard_floor5.py');native=load('floor5_native',T/'tools/short3_native_floor5_v3.py');adapter=load('floor5_outbox_adapter',T/'tools/short3_result_floor5_v3.py');base=load('floor5_outbox',T/'tools/short3_result_base_floor5_v3.py');tests=[]
assert guard.NativeDTCGuard is guard.original.NativeDTCGuard
for free,expected in [(5*GIB-1,False),(5*GIB,False),(5*GIB+1,True),(6*GIB,True),(7*GIB,True)]:
 fake={'status':'RESOURCE_HOLD','first':{'disk_free_bytes':free},'second':{'disk_free_bytes':free},'checks':{'first_native_disk_floor_plus_monitor':False,'second_native_disk_floor_plus_monitor':False,'RAM':True,'original_10s_pair':True}}
 x=guard.rebind_admission(fake);assert (x['status']=='PASS')==expected;tests.append({'test':'target_admission_exclusive_floor_'+str(free),'pass':True})
fake['checks']['RAM']=False;assert guard.rebind_admission(fake)['status']=='RESOURCE_HOLD';tests.append({'test':'non_disk_failed_admission_preserved','pass':True})
req=json.loads((T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json').read_text())
for row in req['specs']:native.check_input(native.spec_for(row['cohort']))
resources=native.resources(native.spec_for('E2-AEF3-MRIQ-CM'));assert resources['required_free_bytes']==6*GIB+sum(p['reserved_write_bytes'] for p in resources['peer_reservations']) and resources['physical_disk_pass'] and resources['physical_RAM_pass'];tests.append({'test':'5GiB_safety_plus_exact1GiB_own_write_reserve_no_double_count','pass':True})
reg={'registered_future_requests':{adapter.REQUEST:{'reserved_write_bytes':GIB},'peer':{'state':'RUNNING','reserved_write_bytes':123}}};basis=adapter.peer_basis(reg);assert basis['registered_peer_bytes']==basis['other_outstanding_write_reservations_bytes']==123 and basis['unregistered_headroom_bytes']==0 and basis['disk_floor_bytes_preserved']==5*GIB
tests.append({'test':'registered_foreign_reservation_preserved_unknown_cushion_in_floor','pass':True})
for bad in [None,-1,'123',1.5]:
 reg['registered_future_requests']['peer']['reserved_write_bytes']=bad
 try:adapter.peer_basis(reg)
 except RuntimeError:tests.append({'test':'reject_unknown_or_invalid_foreign_'+str(bad),'pass':True})
 else:raise AssertionError('invalid foreign reserve accepted')
gate=base.gate(16*1024**2,other_reservation=0);assert gate['local_safety_floor_bytes']==5*GIB;tests.append({'test':'actual_genuine164_mount_RAM_and_local_floor_gate','pass':True})
admission=guard.native_admission(T/'DTC/run');assert admission['status']=='PASS' and all(admission['checks'].values());tests.append({'test':'actual_original10s_pair_all_non_disk_BA_checks_preserved','pass':True})
old=json.loads((T/'control/QUALIFICATION_R2.json').read_text())
for name,h in old['tool_sha256'].items():assert sha(T/'tools'/name)==h
tests.append({'test':'all_previous_qualified_tool_bytes_unchanged','pass':True})
newfiles=['short3_native_floor5_v3.py','short3_storage_guard_floor5.py','short3_result_base_floor5_v3.py','short3_result_floor5_v3.py','short3_frontend_floor5_v3.py']
for name in newfiles:ast.parse((T/'tools'/name).read_bytes())
diff=''.join(difflib.unified_diff((T/'tools/short3_native.py').read_text().splitlines(True),(T/'tools/short3_native_floor5_v3.py').read_text().splitlines(True),fromfile='original_derived_native',tofile='user_floor5_derived_native'))
(T/'control/STORAGE_NATIVE_OPERATIONAL_DIFF_V3.patch').write_text(diff)
out={'schema':'DTC_SHORT3_USER_5GiB_STORAGE_QUALIFICATION_V3','status':'PASS_ZERO_NEW_MODEL_STARTS','tests':tests,'resources':resources,'actual_target_admission':admission,'actual_copyonly_gate':gate,'source_SHA256':{name:sha(T/'tools'/name) for name in newfiles},'original_native_source_sha256':sha(T/'tools/short3_native.py'),'original_spec_request_sha256':sha(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),'original_science_authorization_sha256':sha(T/'control/SCIENCE_AUTHORIZATION.json'),'source_native_diff_sha256':sha(T/'control/STORAGE_NATIVE_OPERATIONAL_DIFF_V3.patch'),'same_scientific_budget':12,'same_simulator_configs_inputs_source_toolchain':True,'same_exact_BA_runtime_decision_class':True,'model_starts':0,'source_deletions':0,'scope':'Operational disk admission/guard floor and outbox reservation accounting only;all original sources/specs/receipts preserved.'}
with (T/'control/STORAGE_FLOOR5_QUALIFICATION_V3.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'status':out['status'],'tests':len(tests),'required_free_bytes':resources['required_free_bytes'],'local_safety_floor_bytes':5*GIB,'actual_free_bytes':resources['native_free_bytes']},indent=2))
