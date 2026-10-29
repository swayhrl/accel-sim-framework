import pathlib,importlib.util,json,copy,hashlib,traceback,datetime
P=pathlib.Path;B=P(__file__).resolve().parent;R=B.parents[1];J=R.parents[1];H=J/'agent_c/wv_mode_host_candidate_v1'
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
old=load('old_host_contract',H/'mode_contract.py');m=load('new_host_contract',B/'host_candidate/mode_contract.py');plan=json.loads((R/'main/NEXT_MINIMAL_SCIENTIFIC_PLAN.json').read_bytes());q=plan['proposed_points'][0];S=json.loads(P(q['input_spec_ref']['path']).read_bytes());results=[]
def check(label,fn,reject=False):
 try:fn();ok=not reject;err=None
 except Exception as e:ok=reject;err=repr(e)
 results.append(dict(label=label,PASS=ok,expected='REJECT' if reject else 'PASS',error=err));assert ok,results[-1]
check('original_draft_rejects_actual_five_key_S_env',lambda:old.check_background(S),True)
for mode in m.MODES:
 s=copy.deepcopy(S);s['mode']=mode;s['T']=bool(m.MODES[mode][3]);s['M']=bool(m.MODES[mode][4]);s['expected_effective_options'].update(m.flags(mode))
 check(mode+'_actual282_background',lambda s=s:m.check_background(s))
 check(mode+'_history_profile',lambda s=s,mode=mode: (_ for _ in ()).throw(AssertionError()) if m.history_for(s)['profile']!=m.MODES[mode][5] else None)
# Background rejection with each resource/source/observer discrepancy retained.
W=copy.deepcopy(S);W.update(mode='W_ONLY',T=False,M=False);W['expected_effective_options'].update(m.flags('W_ONLY'))
mutations=[('Source92',lambda s:s['source_identity'].update(core_source_commit='92_NOT_ACCEPTED')),('geometry16set',lambda s:s['geometry'].update(sets=16)),('heavyON',lambda s:s['observer_env'].update(EP_L2_EVENT_TIMELINE='1')),('WIREOFF',lambda s:s['observer_env'].update(EPL2_LIFE_WIRE='OFF')),('unknownENV',lambda s:s['observer_env'].update(FAKE='0')),('missingWIRE',lambda s:s['observer_env'].pop('EPL2_LIFE_WIRE')),('modeTYPO',lambda s:s.update(mode='W')),('T_ON_in_W',lambda s:s.update(T=True)),('M_ON_in_W',lambda s:s.update(M=True)),('bankP2',lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_bank_ops':'2'})),('MSHR64',lambda s:s['expected_effective_options'].update({'-gpgpu_cache:dl2':'S:32:128:8,L:B:m:L:P,A:64:1,128:0,32'})),('fixedquota',lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_tvd_fixed_entries':'64'})),('statOFF',lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_ms_observer':'0'})),('unknown282key',lambda s:s['expected_effective_options'].update({'-fake':'0'})),('traceMismatch',lambda s:s['expected_effective_options'].update({'-trace':'fake'})),('wrongFT',lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_ft_mode':'1'}))]
for label,mutate in mutations:
 s=copy.deepcopy(W);mutate(s);check(label,lambda s=s:m.check_background(s),True)
for mode in ['S','W_ONLY','WV_ZERO_RO']:
 s=copy.deepcopy(W);s['mode']=mode;s['ro_qualification_ref']=None;check(mode+'_RO_NOT_APPLICABLE',lambda s=s:m.validate_ro(s))
 s['ro_qualification_ref']={'path':'forbidden'};check(mode+'_ROauthorityRejected',lambda s=s:m.validate_ro(s),True)
for mode in ['F','F_MINUS_T']:
 s=copy.deepcopy(W);s['mode']=mode;s['ro_qualification_ref']=None;check(mode+'_missingCertRejected',lambda s=s:m.validate_ro(s),True)
check('W_missingCPUqualificationRejected',lambda:m.validate_mode_cpu(W),True)
check('W_missingNewHostQRejected',lambda:m.validate_hostq(W),True)
# Explicit older CPU HOLD supplied as supposed qualification must be rejected, never upgraded.
r=J/'agent_c/wv_ro_t_mode_parameter_audit_v1/exact3_cpu_runs/f79b10ea-4950-4e4c-895b-16ca2b2a65e9/RESULT.json';s=copy.deepcopy(W);s['mode_cpu_qualification_ref']={'path':str(r),'sha256':hashlib.sha256(r.read_bytes()).hexdigest()};check('oldActualCPUHOLDRejected',lambda:m.validate_mode_cpu(s),True)
x=dict(schema='EP_ROUND2_WV_HOST_CONTRACT_CONTROLS_V1',status='PURE_MODE_CONTRACT_CONTROLS_PASS_NOT_FULL_HOST_OR_NATIVE_QUALIFICATION',controls=results,count=len(results),fullwrapper_controls=0,native_controls=0,model_starts=0,scientific_acceptance_granted=False,production_Source_changed=False,old_draft_unchanged=True,candidate_sha256=hashlib.sha256((B/'host_candidate/mode_contract.py').read_bytes()).hexdigest(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(B/'HOST_CONTRACT_ACTUAL_CONTROLS.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(dict(count=len(results),status=x['status'])))
