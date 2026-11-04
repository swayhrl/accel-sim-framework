from pathlib import Path
import sys,json,hashlib,types,ast,copy
sys.dont_write_bytecode=True
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');O=A/'agents/A_remaining28_runtime_source_draft_v1';checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(n,b):assert b,n;checks.append(dict(name=n,PASS=True))
def load(p):m=types.ModuleType('CPU_ONLY_'+p.stem);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
mods={}
for p in O.glob('perf28_*.py'):
 ast.parse(p.read_text(),filename=str(p))
 if p.name!='perf28_guard.py':mods[p.stem]=load(p)
check('all_runtime_and_forward_modules_parse',len(mods)>=10)
cap=mods['perf28_capacity_strict'];fields=json.loads((A/'agents/A_remaining28_owner_resource_v1/REMAINING28_RESOURCE_SPEC_FIELDS.json').read_text());specs=[]
for row in fields['points']:
 s=copy.deepcopy(row);s['expected_options']=s.pop('expected_effective_options');s.update(request='DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1',host_cpu=None,core_commit='9eedb3131937748f0492fa83aad37d3691118d70',framework_commit='02775fd795cde5aae1480d81cee6eb481d0a08f4');specs.append(s);shape=cap.validate_spec(s);assert shape['physical_lines_per_SM']in[640,768,1024]
check('all28_exact_configs_validate',len(specs)==28)
legacy=cap.LEGACY_PATH.read_text();check('ag6_source_pin_fixed',sha(cap.LEGACY_PATH)==cap.LEGACY_SHA256)
for variant in cap.VARIANTS:
 s=next(x for x in specs if x['profile']==variant);code,binding=cap.transformed_source(s);module,binding2=cap.load_for(s);check(variant+'_single_anchor_roundtrip',binding==binding2 and binding['replacement_count']==1 and binding['all_other_parser_source_bytes_unchanged'])
 shape=cap.validate_spec(s);replacement='0 <= value("oo_physical_allocated") <= '+str(shape['physical_lines_per_SM'])+' * 64, "physical_'+str(shape['physical_lines_per_SM'])+'_per_SM_capacity"';check(variant+'_all_other_parser_bytes_exact',code.replace(replacement,cap.ANCHOR,1)==legacy)
 bound=shape['capacity_bound'];expression=replacement.split(', "physical_')[0]
 for val,expected in [(-1,False),(0,True),(bound,True),(bound+1,False)]:assert eval(expression,{'__builtins__':{}},{'value':lambda key,v=val:v})is expected
 check(variant+'_bound_edges',True)
 check(variant+'_population_API_retained',all(callable(getattr(module,n))for n in ['parse_full','pipeline_contract','echo']))
 if shape['physical_lines_per_SM']==640:check(variant+'_legacy_parser_bytes_identical',hashlib.sha256(code.encode()).hexdigest()==cap.LEGACY_SHA256)
parent=load(Path('/root/data/dtc_perf_first_parallel_exploration_20261104_v1/tools/perf4_capacity_strict.py'));s=next(x for x in specs if x['profile']=='PHYS768_TAG64x8');_,b1=parent.load_for(s);_,b2=cap.load_for(s);check('phys768_legacy_transform_matches_qualified_first4',b1['transformed_source_sha256']==b2['transformed_source_sha256'])
for name,key,val in [('SM32','-gpgpu_n_clusters',['32']),('DRAM1700','-gpgpu_clock_domains',['1410.0:1410.0:1410.0:1700.0']),('logical1024','-gpgpu_dtc_l1_logical_ways',['16']),('allocation8','-gpgpu_dtc_l1_allocation_width',['8']),('MSHR384','-gpgpu_cache:dl2',['S:128:128:16,L:B:m:L:L,A:384:4,32:0,32']),('coupled_PIB','-gpgpu_dtc_l1_oo_pib_entries',['192']),('wrong_physical','-gpgpu_dtc_l1_physical_lines',['1024']),('Tagbank8','-gpgpu_dtc_l1_tag_banks',['8'])]:
 bad=copy.deepcopy(s);bad['expected_options'][key]=val
 try:cap.validate_spec(bad);ok=False
 except AssertionError:ok=True
 check('reject_'+name,ok)
bad=copy.deepcopy(s);bad['profile']=bad['structure_variant']='TAG64x16_PHYS640'
try:cap.validate_spec(bad);ok=False
except AssertionError:ok=True
check('reject_structural_Tag_HOLD_profile',ok)
# Synthetic private native identity metadata; never actual registration or native calls.
F=O/'fixtures/native_CPU_ONLY';(F/'control/specs').mkdir(parents=True,exist_ok=True);(F/'tools').mkdir(exist_ok=True)
def put(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,sort_keys=True)+'\n')
for name in ['perf28_capacity_strict.py','perf28_resources.py','perf28_guard.py','perf28_guard_policy.py']:
 src=O/name if(O/name).exists()else A/'agents/A_remaining28_owner_resource_v1'/name;(F/'tools'/name).write_bytes(src.read_bytes())
plan=dict(source_pins=[]);put(F/'control/EXECUTION_PLAN.json',plan);put(F/'control/MATRIX.json',dict(points=[dict(cohort=x['cohort'])for x in specs]));put(F/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',dict(input_digests=list({x['input_digest']for x in specs})));put(F/'control/BUILD_PROFILE.json',dict(core_commit=specs[0]['core_commit'],framework_commit=specs[0]['framework_commit']));put(F/'control/PROJECT_AUTHORITY.fixed.json',json.loads((A/'control/PROJECT_AUTHORITY.fixed.json').read_text()))
q=dict(request='DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1',budget=28,remaining=28,consumed={},admitted_specs={},engine_sha256=sha(O/'perf28_native.py'),execution_plan_sha256=sha(F/'control/EXECUTION_PLAN.json'),spec_request_sha256=sha(F/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),model_automatic_retries=0,runtime_release_evidence={'CPU_ONLY_SYNTHETIC_PROOF':True})
for s in specs:
 p=F/'control/specs'/(s['cohort']+'.json');put(p,s);(F/'control'/(s['cohort']+'_SPEC.json')).write_bytes(p.read_bytes());q['admitted_specs'][s['cohort']]=sha(p)
n=mods['perf28_native'];n.R=F;reg=dict(registered_future_requests={n.REQ:q});n.authority=lambda:(reg,{'epoch':2});original_load=n.load
receipt_mock=types.SimpleNamespace(verify=lambda plan,reg,release=None:dict(q['runtime_release_evidence']))
n.load=lambda name,path:receipt_mock if Path(path).name=='perf28_terminal_gate_receipt.py'else original_load(name,path)
check('native_registered_exact28_CPU_fixture',n.registered()[2]is q)
for s in specs:assert n.canonical(s['cohort'])['profile']==s['profile']
check('canonical_all28_full_token_variant_contract',True)
old=q['budget'];q['budget']=4
try:n.registered();ok=False
except AssertionError:ok=True
q['budget']=old;check('native_rejects_budget4',ok)
# A persisted HOLD is denied before parent lease/device/input/launcher checks.
import os
held=specs[0]['cohort'];q.update(state='RUNNING',admission_holds={held:{'state':'UNUSED_FAMILY_HOLD','uuid':None,'cycles':None}});n.authority=lambda:(reg,{'epoch':2,'state':'NATIVE_SCIENCE_ACTIVE','holder':os.uname().nodename});oldenv=os.environ.get('DTC_PERFFIRST_REMAINING28_NATIVE_ENTRY');os.environ['DTC_PERFFIRST_REMAINING28_NATIVE_ENTRY']='1'
try:n.prepare(held);ok=False
except AssertionError as err:ok=str(err)=='FAMILY_ADMISSION_HOLD_NO_START'
if oldenv is None:os.environ.pop('DTC_PERFFIRST_REMAINING28_NATIVE_ENTRY')
else:os.environ['DTC_PERFFIRST_REMAINING28_NATIVE_ENTRY']=oldenv
q['admission_holds']={};check('native_prepare_persisted_HOLD_early_reject',ok)
# Registry-locked held-consume guard precedes the old mutator's INTENT side effect.
probe={'registered_future_requests':{n.REQ:{'state':'RUNNING','consumed':{},'admission_holds':{held:{}}}}};called=[]
try:n.guard_model_mutation(probe,held,lambda current:called.append(True));ok=False
except AssertionError as err:ok=str(err)=='FAMILY_ADMISSION_HOLD_NO_CONSUME'and called==[]
check('atomic_HOLD_rejects_before_INTENT_mutator',ok)
probe['registered_future_requests'][n.REQ]['consumed'][held]={'uuid':'CPU_HEALTHY_ALREADY_CONSUMED'};probe['registered_future_requests'][n.REQ]['state']='STOP_UNACCEPTED';n.guard_model_mutation(probe,held,lambda current:called.append(True));check('atomic_guard_allows_already_consumed_completion_not_termination',called==[True])
# Pure binding reads proof via verifier mock and retains origin commit/authorization hashes.
binding=n.binding();check('binding_carries_runtime_release_evidence',binding['runtime_release_evidence']==q['runtime_release_evidence']);check('binding_keeps_commit_vs_authorizationSHA_distinct',binding['approved_contract_commit']=='1098420304d5c60db9cba6ac5d4db0bacbc0e8a7'and binding['gate_amendment_authorization_sha256']=='119217415136f6bae824ed25ecb5d0776fcd67eeff9dcae7fde6b5a0ce73f894')
# Missing real C receipt must not be interpreted as metadata/full closure PASS.
receipt=mods['perf28_terminal_gate_receipt'];contract=json.loads((A/'C_first4_terminal_gate_preparation_v1/CONTRACT.json').read_text())
try:receipt.verify(dict(first4_terminal_gate=contract),{});ok=False
except(FileNotFoundError,KeyError,AssertionError):ok=True
check('actual_missing_C_full_closure_receipt_HOLD',ok)
# Policy is byte-identical to qualified first4; guard schema/receiver pins are namespaced only.
check('guard_policy_behavior_bytes_unchanged',sha(O/'perf28_guard_policy.py')==sha(Path('/root/data/dtc_perf_first_parallel_exploration_20261104_v1/tools/perf4_guard_policy.py')))
check('runtime_guard_schema_new28',"DTC_PERFFIRST_REMAINING28_ADMISSION_PRESSURE_ONLY_RUNTIME_V1"in(O/'perf28_guard.py').read_text())
check('strict_requires_full_270echo_original_population',"old.population(raw,s,domain,legacy)"in(O/'perf28_strict.py').read_text())
check('strict_has_no_768_only_restriction',"s['structure_variant']=='PHYS768_TAG64x8'"not in(O/'perf28_strict.py').read_text())
check('registered_and_binding_no_recursive_each_other', 'binding()'not in ast.get_source_segment((O/'perf28_native.py').read_text(),next(x for x in ast.parse((O/'perf28_native.py').read_text()).body if isinstance(x,ast.FunctionDef)and x.name=='registered')))
result=dict(schema='PERFFIRST_REMAINING28_RUNTIME_DRAFT_CPU_QUALIFICATION_V1',status='PASS_CPU_DRAFT_NOT_INSTALLED',tests=checks,n=len(checks),runtime_modules_n=8,forward_modules=['terminal_gate_receipt','parent_addon','ops'],actual_registrations=0,actual_models=0,services=0,R3_or_R28_writes=0,synthetic_native_fixture_not_science=True,actual_C_terminal_gate_not_yet_claimed=True,source_pins=[dict(path=str(p),sha256=sha(p))for p in sorted(O.glob('perf28_*.py'))]);(O/'CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print('RUNTIME_CPU',len(checks),'PASS')
