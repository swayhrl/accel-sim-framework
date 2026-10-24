"""Zero-model option expectation qualification against frozen real GEMM echoes."""
import pathlib,json,hashlib,copy,importlib.util
T=pathlib.Path('/root/data/dtc_main_short3_20261024_v1');A=pathlib.Path('/root/data/dtc_main_20261023_v1/ae_fair_v1')
def read(p):return json.loads(pathlib.Path(p).read_bytes())
sp=importlib.util.spec_from_file_location('fixed_expectations',T/'tools/short3_strict_r2.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
rows=[]
for row in read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['specs']:
 s=read(T/'control'/(row['cohort']+'_SPEC.json'));orig='E2-AEFAIR-'+s['cell'];out=pathlib.Path(read(A/'control/qualification_ledger'/(orig+'.INTENT.json'))['output']);gold=read(out/'AEFAIR_STRICT.json')
 expected=copy.deepcopy(gold['effective_options']);expected['-trace']=[s['native_simulator_argv'][s['native_simulator_argv'].index('-trace')+1]]
 actual=m.resolved_options(s);assert actual==expected and len(actual)==270
 old=read(A/'control'/(orig+'_SPEC.json'));assert [r['sha256'] for r in s['configs']]==[r['sha256'] for r in old['configs']]
 rows.append({'cohort':row['cohort'],'status':'ALL270_MATCH_REAL_FROZEN_GEMM_ECHO_WITH_ONLY_EXACT_INPUT_TRACE_REBOUND','old_GEMM_uuid':gold['uuid'],'old_GEMM_strict_sha256':hashlib.sha256((out/'AEFAIR_STRICT.json').read_bytes()).hexdigest(),'all4_config_SHA_same':True,'new_model_starts':0})
x={'schema':'DTC_SHORT3_RESOLVER_GOLDEN_CONFIG_JOIN_V1','status':'PASS_ALL12_ZERO_MODEL_STARTS','rows':rows,'scope':'Proves correct expected option normalization for exact same configuration byte sequences, with -trace derived from the new frozen argv. No simulator run or historical performance reuse.'}
with (T/'control/RESOLVER_GOLDEN_CONFIG_JOIN.json').open('x') as f:json.dump(x,f,indent=2);f.write('\n')
print(x['status'],len(rows))
