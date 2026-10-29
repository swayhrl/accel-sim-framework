"""Private CPU controls. All approval-shaped fixtures are synthetic test data.
Never imports a dispatcher, invokes a model, edits a live registry or grants NI.
"""
import pathlib,sys,uuid,importlib.util,json,copy,hashlib,os,datetime,traceback,types
P=pathlib.Path;B=P(__file__).resolve().parent;H=B/'host_candidate';J=B.parents[2];OLD=J/'research/observation_guided_20261029_v1/round2/agent_b';SBOX=B/'sandbox_controls'/str(uuid.uuid4());SBOX.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(H))
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(n,v):
 p=SBOX/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');return dict(path=str(p),sha256=sha(p))
def ref(p):return dict(path=str(p),sha256=sha(p))
mc=load('mcv2',H/'mode_contract.py');parser=load('parserv2',H/'mode_aware_terminal.py');eng=load('engv2',H/'ep_perf_native_wv_modes_draft.py');import ep_perf_common_v2 as common
# All authority/control writes are relocated BEFORE any function is called.
common.ROOT=SBOX;common.NATIVE=SBOX/'native';common.REG=common.NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';common.EPOCH=common.NATIVE/'control/CURRENT_SCIENCE_EPOCH.json'
eng.ROOT=SBOX;eng.NATIVE=common.NATIVE;eng.LEDGER=common.NATIVE/'control/qualification_ledger';eng.LEDGER.mkdir(parents=True,exist_ok=True)
(common.REG.parent/'request_history').mkdir(parents=True,exist_ok=True)
results=[]
def check(label,fn,reject=False,contains=None):
 try:
  val=fn();ok=not reject;err=None
 except Exception as ex:
  val=None;err=type(ex).__name__+':'+str(ex);tb=traceback.format_exc();ok=reject and (contains is None or contains in err)
 results.append(dict(label=label,PASS=ok,expected='REJECT'if reject else'PASS',error=err));
 if not ok:
  print(tb);raise AssertionError(results[-1])
 return val
q=read(OLD/'EXACT_SPEC_AND_BUDGET_MANIFEST.json');proposal=next(x for x in q['proposals']if x['program']=='fastWalshTransform');s=read(proposal['draft_ref']['path']);s.update(schema='EP_FULL_PERF_EXACT_SPEC_V1',cohort='EP_PERF_SANDBOX_W_ONLY_V2',science_request_id=common.GOAL)
elig=read(s['eligibility_ref']['path']);elig['modes_qualified']=list(set(elig['modes_qualified'])|{'W_ONLY'});elig['TEST_ONLY_SYNTHETIC_APPROVAL']=True;s['eligibility_ref']=put('TEST_ONLY_ELIGIBILITY.json',elig)
s['host_engine_ref']=ref(H/'ep_perf_native_wv_modes_draft.py');s['host_common_ref']=ref(H/'ep_perf_common_v2.py');s['mode_contract_ref']=ref(H/'mode_contract.py');s['validation_module_ref']=ref(H/'mode_aware_terminal.py');s['pinned_files']={} # runtime map pins controlled independently below
accepted_s=read(s['original_accepted_S_spec_ref']['path']);live=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');oldpop=live['registered_future_requests'][common.FRONTEND_GOAL];oldrow=oldpop['consumed'][accepted_s['cohort']];pt=read(oldrow['accepted_point_ref']['path'])
anchor=dict(schema='EP_MAIN_EXACT_EXISTING_S_REFERENCE_QUALIFICATION_V1',status='EXACT_EXISTING_S_HARDWARE_INPUT_OBSERVERS_QUALIFIED_FOR_MATCHED_REFERENCE',approved_by='EP-MAIN',TEST_ONLY_SYNTHETIC_APPROVAL=True,spec_ref=pt['spec_ref'],point_ref=oldrow['accepted_point_ref'],current_closed_state='CLOSED_ACCEPTED',currently_accepted_population=True,source_identity=s['source_identity'],input_identity_sha256=s['input_identity_sha256'],expected_effective_options_sha256=mc.digest_value(accepted_s['expected_effective_options']),registry_population_request_id=common.FRONTEND_GOAL)
s['matched_S_anchor_qualification_ref']=put('TEST_ONLY_ANCHOR.json',anchor)
cpu=dict(schema='EP_MAIN_SOURCE78_FORMAL_MODE_CPU_QUALIFICATION_V1',status='EXACT_SOURCE78_FORMAL_MODE_CPU_PASS_NOT_APPLICATION_ACCEPTANCE',approved_by='EP-MAIN',TEST_ONLY_SYNTHETIC_APPROVAL=True,mode='W_ONLY',source_identity=s['source_identity'],geometry=s['geometry'],formal_flags=mc.flags('W_ONLY'),application_permission=False,completed_controls=['constructor32x8','partition_WAD128','a1_versions_reorder'],evidence_refs={'actual_cpu':ref(OLD/'CPU_ACTUAL_EXECUTION_FINAL.json'),'actual32':ref(OLD/'CPU_32X8_REQUESTS_EXECUTION_FINAL.json')},actual_exact3_result_ref=ref(OLD/'CPU_ACTUAL_EXECUTION_FINAL.json'))
s['mode_cpu_qualification_ref']=put('TEST_ONLY_MAIN_MODE_CPU.json',cpu)
hostq=dict(schema='EP_MAIN_SOURCE78_WV_MODES_HOST_QUALIFICATION_V1',status='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',TEST_ONLY_SYNTHETIC_APPROVAL=True,source_identity=s['source_identity'],modes_qualified=['S','W_ONLY','WV_ZERO_RO'],modules=[s[k]for k in ['host_engine_ref','validation_module_ref','mode_contract_ref']]);s['host_qualification_ref']=put('TEST_ONLY_HOSTQ.json',hostq)
check('parser_whole_dependency_pins',parser.verify)
check('full_static_positive_W_ONLY_synthetic_approvals',lambda:mc.validate_static(s))
for label,mut,msg in [
 ('wrong_CPU_source',lambda x:x['source_identity'].update(core_source_commit='other'),'unknown Source5'),
 ('missing_CPU',lambda x:x.update(mode_cpu_qualification_ref=None),None),
 ('missing_HostQ',lambda x:x.update(host_qualification_ref=None),None),
 ('missing_anchor',lambda x:x.update(matched_S_anchor_qualification_ref=None),None),
 ('wrong_mode_contract_pin',lambda x:x['mode_contract_ref'].update(sha256='0'*64),'mode contract self'),
 ('heavy_observer_ON',lambda x:x['observer_env'].update(EP_L2_EVENT_TIMELINE='1'),'fourheavyOFF'),
 ('S_COUNTER_WRONG',lambda x:x['expected_effective_options'].update({'-gpgpu_ep_l2_ms_observer':'0'}),'undeclaredbackground'),
 ('RO_cert_on_W',lambda x:x.update(ro_qualification_ref={'path':'forbidden'}),'must not inherit')]:
 x=copy.deepcopy(s);mut(x);check('full_static_reject_'+label,lambda x=x:mc.validate_static(x),True,msg)
# Real package instantiated unchanged numeric body (not a full application parser PASS).
_,numeric=check('parser_numeric_factory_unchanged',parser.numeric_math)
check('numeric_body_preserved',lambda:mc.need(numeric['numeric_body_sha256']=='7cc347a6c62974eedf9e1e39b007c2716fa886d26057f005c938c820b48e1817','numeric body'))
# Exercise the actual outer wrapper up to mode binding, preserving parser boundary.
check('full_parser_reject_missing_native_mode_binding',lambda:parser.validate_case(SBOX/'NO_RAW_OPENED',s,{},'unused','unused'),True,'NativeQ mode')
# Scoped synthetic native registry; old accepted row is read-only fixture, foreign/history protected.
user_ref=put('control/USER_REQUEST.txt',{'TEST_ONLY':'no application authorized'})
put('control/USER_AUTHORIZATION.json',dict(goal=common.GOAL,user_request_ref=user_ref,TEST_ONLY_SYNTHETIC_APPROVAL=True))
sp=SBOX/'cases'/s['cohort']/'control/FROZEN_SPEC.json';sp.parent.mkdir(parents=True,exist_ok=True);sp.write_text(json.dumps(s,sort_keys=True,indent=2)+'\n')
def registry():return dict(old_source_history={'old57':'KEEP'},qualification_history=['KEEP'],registered_future_requests={common.FRONTEND_GOAL:dict(budget=227,remaining=0,consumed={accepted_s['cohort']:copy.deepcopy(oldrow)}),common.GOAL:dict(budget=1,remaining=1,admitted_specs={s['cohort']:sha(sp)},consumed={},authorization_ref=ref(SBOX/'control/USER_AUTHORIZATION.json'),runtime_versions={s['host_engine_ref']['sha256']:dict(engine_ref=s['host_engine_ref'],common_ref=s['host_common_ref'])}),'FOREIGN':dict(budget=7,remaining=7,consumed={})},new_scientific_budget_remaining=8)
def install(reg=None):
 common.put(common.REG,reg or registry());common.put(common.EPOCH,dict(epoch=2,state='NATIVE_SCIENCE_ACTIVE',holder=os.uname().nodename,native_registry_sha256=common.sha(common.REG),new_budget_remaining=8))
install();check('native_exact_spec_new_request_positive',lambda:eng.spec_for(s['cohort']))
x=registry();x['registered_future_requests'][common.GOAL]['admitted_specs'][s['cohort']]='0'*64;install(x);check('native_registered_SHA_drift',lambda:eng.spec_for(s['cohort']),True,'unregistered or changed');install()
x=registry();x['registered_future_requests'][common.GOAL]['remaining']=0;install(x);check('native_budget_arithmetic_reject',lambda:eng.spec_for(s['cohort']),True,'arithmetic');install()
x=registry();x['registered_future_requests'][common.FRONTEND_GOAL]['consumed'][accepted_s['cohort']]['state']='UNACCEPTED';install(x);check('native_old_anchor_closed_population_reject',lambda:eng.spec_for(s['cohort']),True,'anchor current');install()
check('native_prepare_sole_entry_reject',lambda:eng.prepare(s['cohort']),True,'sole entry')
# A fake native prefix/suffix is confined to sandbox; fresh_input is actual mount+small commandlist+member metadata, no trace body hashing.
(eng.NATIVE/'bin').mkdir(parents=True,exist_ok=True);prior=eng.NATIVE/'prior';prior.write_bytes(b'PRIVATE_PEER_SUFFIX\n');prelude='PRIVATE_EP_PREFIX\n';(eng.NATIVE/'bin/native').write_bytes(prelude.encode()+prior.read_bytes())
put('control/NATIVE_ENTRY_ROUTE.json',dict(goal=common.GOAL,status='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE',prior_entry_ref=ref(prior),own_prelude=prelude))
os.environ['EP_FULL_PERF_NATIVE_ENTRY']='1'
check('native_prepare_real_inputs_metadata_no_body_scan',lambda:eng.prepare(s['cohort']))
(eng.NATIVE/'bin/native').write_bytes(prelude.encode()+b'WRONG_SUFFIX\n');check('native_prepare_peer_suffix_drift_reject',lambda:eng.prepare(s['cohort']),True,'peer suffix');(eng.NATIVE/'bin/native').write_bytes(prelude.encode()+prior.read_bytes())
# Actual verify_actual function, simulated producer maps/argv. Does not claim observed model PID.
si=dict(s,host_cpu=min(os.sched_getaffinity(0)));args=['CPU_ONLY_NOT_A_MODEL'];env={'TEST':'1'};info=dict(cmdline=[a.encode()for a in args],environment={k.encode():v.encode()for k,v in env.items()},affinity=[si['host_cpu']],nice=10,boot_id=s['native_boot_id'],mnt_namespace=s['native_mount_namespace'],maps='1-2 r-xp 0 00:00 0 '+s['binary_path']+'\n',limits='Max address space '+str(s['limits']['AS_bytes'])+' '+str(s['limits']['AS_bytes']))
check('native_argv_env_map_limit_positive_synthetic',lambda:eng.verify_actual(None,info,si,args,env))
for label,fn,msg in [('argv',lambda x:x.update(cmdline=[b'wrong']),'argv/environment'),('env',lambda x:x.update(environment={}), 'argv/environment'),('affinity',lambda x:x.update(affinity=[]),'CPU/nice'),('map',lambda x:x.update(maps='unknown'),'ELF not mapped'),('AS',lambda x:x.update(limits='Max address space 0 0'),'AS limit')]:
 x=copy.deepcopy(info);fn(x);check('native_actual_reject_'+label,lambda x=x:eng.verify_actual(None,x,si,args,env),True,msg)
# Registry transaction actual code: old owner rows and peers immutable. No official row writes.
install();before=common.sha(common.REG)
check('scoped_transaction_peer_reject',lambda:common.transaction('TEST_ONLY',lambda r:r['registered_future_requests']['FOREIGN'].update(remaining=0)),True,'foreign registry')
check('peer_reject_no_write',lambda:mc.need(common.sha(common.REG)==before,'bad write'))
check('scoped_transaction_old_history_reject',lambda:common.transaction('TEST_ONLY',lambda r:r['old_source_history'].update(old57='BAD')),True,'old history')
# No Popen call here. A controlled throw at fork boundary in actual run_native proves consume-first and no-refund while creating zero children.
put('control/dispatch_bindings/'+s['cohort']+'.json',dict(cohort=s['cohort'],spec_sha256=sha(sp),host_cpu=si['host_cpu']))
put('control/DISPATCH_CLAIMS.json',dict(claims={s['cohort']:dict(state='CLAIMED',spec_sha256=sha(sp),host_cpu=si['host_cpu'],estimated_peak_RAM_bytes=0,remaining_write_bytes=0)}))
original_gate=eng.resource_gate;eng.resource_gate=lambda *a:{'TEST_ONLY_RESOURCE_GATE_STUB':True};oldpop_fn=eng.subprocess.Popen;fork_seen=[]
def NO_FORK(*a,**kw):
 if a[0][0]in['findmnt','git']:return oldpop_fn(*a,**kw)
 r,e=common.authority();row=r['registered_future_requests'][common.GOAL]['consumed'][s['cohort']];assert row['state']=='CONSUMED_BEFORE_FORK';assert r['registered_future_requests'][common.GOAL]['remaining']==0;assert (eng.LEDGER/(s['cohort']+'.INTENT.json')).exists();fork_seen.append(True);raise RuntimeError('TEST_SENTINEL_NO_CHILD_FORKED')
eng.subprocess.Popen=NO_FORK
before_peers=copy.deepcopy(common.read(common.REG)['registered_future_requests']);done=check('run_native_consume_before_mockfork',lambda:eng.run_native(s['cohort']))
eng.subprocess.Popen=oldpop_fn;eng.resource_gate=original_gate
check('mockfork_seen_exactly_once',lambda:mc.need(fork_seen==[True],'fork boundary not reached'))
check('native_mockfork_no_refund',lambda:mc.need(common.read(common.REG)['registered_future_requests'][common.GOAL]['remaining']==0 and done['new_attempt_consumed']==1 and 'TEST_SENTINEL_NO_CHILD_FORKED'in done['stop_reason'],'no-refund wrong'))
check('native_mockfork_peers_preserved',lambda:mc.need(all(common.read(common.REG)['registered_future_requests'][k]==v for k,v in before_peers.items()if k!=common.GOAL),'peer mutation'))
check('native_same_spec_retry_rejected',lambda:eng.run_native(s['cohort']),True)
out=dict(schema='EP_W_ONLY_V2_ACTUAL_HOST_NATIVE_SANDBOX_CONTROLS',status='PASS_CONTROLS_NOT_MAIN_SIGNOFF_OR_APP_NI',controls=results,count=len(results),all_pass=all(x['PASS']for x in results),sandbox_root=str(SBOX),scope='actual mode static wrapper, parser preconditions/numeric factory, native spec/prepare/argv/maps verification, actual consume-before-throw transaction',full_parser_application_validation='NOT_EXECUTED',model_or_launcher_children=0,fork_boundary='INTERCEPTED_RAISED_NO_CHILD',resource_gate='STUB_ONLY_NOT_FRESH_ADMISSION_PROOF',synthetic_approval_records='TEST_ONLY_NEVER_CANDIDATE_AUTHORITY',official_registry_writes=0,production_mutations=0,Trace_body_reads=0,raw_body_scans=0,numeric=numeric,candidate_modules={p.name:ref(p)for p in H.glob('*.py')},utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(B/'HOST_NATIVE_V2_ACTUAL_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status=out['status'],count=len(results),model_starts=0)))
