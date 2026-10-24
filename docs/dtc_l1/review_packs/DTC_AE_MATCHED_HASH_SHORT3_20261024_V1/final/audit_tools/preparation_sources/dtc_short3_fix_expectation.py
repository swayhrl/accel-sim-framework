import pathlib,json,hashlib,shlex,copy,subprocess,shutil,importlib.util
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');F=T/'docs-worktree';D=F/'docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_SHORT3_20261024_V1'
read=lambda p:json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
req=read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json');resolved={};fixes=[]
for r in req['specs']:
 p=T/'control'/(r['cohort']+'_SPEC.json');s=read(p);assert sha(p)==r['sha256'];opts=copy.deepcopy(s['expected_options'])
 for conf in s['configs']:
  assert sha(conf['path'])==conf['sha256'];tokens=shlex.split(P(conf['path']).read_text(),comments=True);key=None;vals=[]
  for token in tokens+['-__END__']:
   if token.startswith('-') and len(token)>1 and (token[1].isalpha() or token[1]=='_'):
    if key is not None:opts[key]=[v for item in vals for v in item.split()]
    key=token;vals=[]
   else:vals.append(token)
 opts['-trace']=[s['native_simulator_argv'][s['native_simulator_argv'].index('-trace')+1]]
 diff={k:{'declared_metadata':s['expected_options'].get(k),'resolved_from_frozen_config_and_argv':opts.get(k)} for k in opts if opts[k]!=s['expected_options'].get(k)}
 assert set(diff)=={'-trace','-gpgpu_dram_timing_opt'} and len(opts)==270
 resolved[r['cohort']]={'original_spec_sha256':r['sha256'],'options':opts,'metadata_corrections':diff}
 fixes.append({'cohort':r['cohort'],'corrections':diff})
p=T/'control/RESOLVED_EFFECTIVE_OPTIONS_R2.json'
with p.open('x') as f:json.dump(resolved,f,indent=2);f.write('\n')
code=(T/'tools/short3_strict.py').read_text()
code=code.replace("def population(raw,s,d,m):\n", "def population(raw,s,d,m):\n s=dict(s);s['expected_options']=resolved_options(s)\n")
code=code.replace("effective_options=s['expected_options']","effective_options=resolved_options(s)")
code+='''
def resolved_options(s):
 if not s.get('cohort','').startswith('E2-AEF3-'):return s['expected_options']
 p=T/'control/RESOLVED_EFFECTIVE_OPTIONS_R2.json'
 need(sha(p)==RESOLVED_OPTIONS_SHA256,'published expectation resolver changed')
 row=read(p)[s['cohort']]
 need(sha(T/'control'/(s['cohort']+'_SPEC.json'))==row['original_spec_sha256'],'original runtime spec changed')
 return row['options']
'''
code+='\nRESOLVED_OPTIONS_SHA256='+repr(sha(p))+'\n'
with (T/'tools/short3_strict_r2.py').open('x') as f:f.write(code)
sp=importlib.util.spec_from_file_location('resolved_strict',T/'tools/short3_strict_r2.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
actual=m.terminal('E2-AEF3-NN-DM');assert actual['performance_accepted'] and actual['cycles']==6132
proof={'schema':'DTC_SHORT3_EXPECTATION_METADATA_CORRECTION_R2','status':'PASS_EXISTING_COMPLETE_OUTPUT_REVALIDATED_ZERO_NEW_MODELS','cause':'Original generated expected_options incorrectly retained GEMM -trace and line-split a quoted multiline DRAM timing string. Actual simulator argv/config byte sequences were correct and unchanged.','changed_runtime_files':[],'changed_original_specs':[],'model_retries':0,'budget':12,'consumed':1,'never_started':11,'resolver_sha256':sha(p),'strict_r2_sha256':sha(T/'tools/short3_strict_r2.py'),'corrections':fixes,'existing_NN_DM_independent_strict':{k:v for k,v in actual.items() if k not in ['metrics','traffic','effective_options']},'prior_controller_state':read(T/'control/CONTROLLER_STATE.json')}
with (T/'control/EXPECTATION_METADATA_CORRECTION_R2.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
for f in [p,T/'control/EXPECTATION_METADATA_CORRECTION_R2.json']:shutil.copyfile(f,D/'control'/f.name)
shutil.copyfile(T/'tools/short3_strict_r2.py',D/'tools/short3_strict_r2.py')
print(json.dumps({'status':proof['status'],'NN_DM_cycles':actual['cycles'],'kernel_count':actual['kernel_count'],'resource_decisions':actual['resource_decisions']}))
