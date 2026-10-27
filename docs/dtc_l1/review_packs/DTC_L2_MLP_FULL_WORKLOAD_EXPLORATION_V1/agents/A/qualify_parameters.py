"""Local mutation invariants + remote isolated real option-parser CPU fixture."""
import base64,hashlib,importlib.util,json,pathlib,subprocess
from l2_config_generator import *
ROOT=pathlib.Path(__file__).parent
REMOTE='/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/A'
ev=json.loads((ROOT/'SOURCE_EVIDENCE.json').read_text());checks=[];cases=[]
def check(name,value):
    assert value,name
    checks.append(name)
extensions={'E1536':{'entries':1536},'M32':{'merge':32},'Q256':{'miss_queue':256},'F512':{'frfcfs':512}}
profiles={**PROFILES,**stage2_templates(),**extensions}
for cell,s in ev['p0_specs'].items():
    for label,profile in profiles.items():
        texts,manifest=generate(s['config_texts'],profile)
        expected=normalize(profile);before=effective_options(s['config_texts']);after=effective_options(texts)
        check(cell+'/'+label+'/non_target',all(before[k]==after[k] for k in before if k not in (L2,FR)))
        check(cell+'/'+label+'/P0_byte_identity',label!='P0' or texts==s['config_texts'])
        check(cell+'/'+label+'/bank_data_unchanged',manifest['logical_resource_cost']['l2_data_bytes']==10485760)
        parsed=[]
        relevant={L2,FR,*FIXED,'-dram_seperate_write_queue_enable'}
        for t in texts:
            parsed.append('\n'.join(line for line in t.splitlines() if line.split('#',1)[0].strip().split(' ',1)[0] in relevant)+'\n')
        cases.append({'cell':cell,'label':label,'texts':parsed,'expected':expected,'transform':manifest})
bad=[{'entries':0},{'entries':True},{'merge':3},{'miss_queue':-1},{'frfcfs':0},{'entries':2147483647},{'other':1},'UNKNOWN']
for i,p in enumerate(bad):
    try:normalize(p)
    except (ValueError,TypeError):check('reject_invalid_'+str(i),True)
    else:raise AssertionError('Accepted invalid profile '+str(p))
for cell,s in ev['p0_specs'].items():
    badbase=list(s['config_texts']);badbase[0]+='\n-gpgpu_clock_domains 1410.0:1410.0:1410.0:1700.0\n'
    try:generate(badbase,'E384')
    except ValueError:check(cell+'/reject_PS_base',True)
    else:raise AssertionError('Accepted changed clock')
bundle={p.name:base64.b64encode(p.read_bytes()).decode() for p in ROOT.iterdir() if p.is_file() and p.suffix in ('.py','.cc','.json') and p.name!='QUALIFICATION.json'}
payload={'root':REMOTE,'files':bundle,'cases':cases,'source_option_parser_sha256':ev['sources']['src/option_parser.cc']['sha256']}
remote=r'''
import base64,hashlib,json,pathlib,subprocess,tempfile
P=PAYLOAD
root=pathlib.Path(P['root']);root.mkdir(parents=True,exist_ok=True)
for n,b in P['files'].items():(root/n).write_bytes(base64.b64decode(b))
C=pathlib.Path('/root/data/dtc_failure_repair_20261025_v1/core')
assert hashlib.sha256((C/'src/option_parser.cc').read_bytes()).hexdigest()==P['source_option_parser_sha256']
exe=root/'cpu_fixture';compile=subprocess.run(['g++','-std=c++11','-O2','-I'+str(C/'src'),str(root/'option_parser_fixture.cc'),str(C/'src/option_parser.cc'),'-o',str(exe)],capture_output=True,text=True)
assert compile.returncode==0,compile.stderr
results=[]
for case in P['cases']:
 d=root/'cpu_cases'/(case['cell']+'_'+case['label']);d.mkdir(parents=True,exist_ok=True)
 paths=[]
 for i,t in enumerate(case['texts']):
  p=d/('config-'+str(i)+'.config');p.write_text(t);paths.append(str(p))
 r=subprocess.run([str(exe),*paths],capture_output=True,text=True,timeout=10)
 assert r.returncode==0,(case['label'],r.stdout,r.stderr)
 actual=json.loads(r.stdout.strip().splitlines()[-1]);expected=case['expected']
 assert all(actual[k]==v for k,v in expected.items()),(actual,expected)
 result={k:case[k] for k in ['cell','label','expected']};result.update(actual=actual,returncode=r.returncode);results.append(result)
 (d/'TRANSFORM.json').write_text(json.dumps(case['transform'],indent=2))
out={'status':'PASS','cpu_fixture_cases':len(results),'model_launches':0,'model_cycles':0,'fixture_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'compile_stderr':compile.stderr,'linked_core_source':str(C/'src/option_parser.cc'),'linked_core_source_sha256':P['source_option_parser_sha256'],'cases':results,'limitations':['Actual Core option_parser.cc exercised; cache_config sscanf format/order and fixed invariants independently mirrored, not full cache object construction.','No simulator executable, GPU trace, cycle engine, or model resource lease invoked.','CPU parsing success does not prove performance, memory boundedness, or workload liveness; actual scientific qualifications remain required.']}
(root/'CPU_FIXTURE_RESULTS.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
'''.replace('PAYLOAD',repr(payload),1)
r=subprocess.run(['ssh','hrl-174-new','python3','-'],input=remote.encode(),capture_output=True,timeout=120)
assert r.returncode==0,r.stderr.decode()
cpu=json.loads(r.stdout);out={'status':'PASS','local_invariant_checks':len(checks),'check_names':checks,'cpu':cpu,'model_launches':0}
(ROOT/'QUALIFICATION.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'status':out['status'],'local_invariants':len(checks),'real_core_option_parser_cases':cpu['cpu_fixture_cases'],'model_launches':0}))
