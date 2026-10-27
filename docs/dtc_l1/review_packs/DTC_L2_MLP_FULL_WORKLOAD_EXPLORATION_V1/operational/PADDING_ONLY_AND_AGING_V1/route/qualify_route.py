"""Actual POSIX shell routing with every execution target replaced by a CPU sink.
The production bin/experiment wrapper is NEVER executed.
"""
import datetime,hashlib,importlib.util,json,os,pathlib,shlex,subprocess,tempfile
from build_route import build,DEFAULT
P=pathlib.Path;HERE=P(__file__).resolve().parent;checks=[];cases=[]
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def check(ok,label):assert ok,label;checks.append(label)
old=(HERE/'native.original.sh').read_bytes();candidate,manifest=build(old)
check(candidate==(HERE/'native.candidate.sh').read_bytes(),'candidate exactly reproduced by builder')
check(candidate[manifest['prefix_bytes']:]==old,'entire4212-byte original native body preserved verbatim')
production=P('/root/data/ep_l2_dtc_l1_native_v2/bin/native');before=sha(production)
check(before==manifest['old_entry_sha256'],'production entry still matches qualified source snapshot')
fixture=P(tempfile.mkdtemp(prefix='CPU_ROUTE_',dir=HERE));sink=fixture/'sink.py';active=fixture/'ACTIVE.json'
sink.write_text('''import json,pathlib,sys,os
target=sys.argv[2];args=sys.argv[3:]
if target=='''+repr(DEFAULT)+''':
 p=pathlib.Path('''+repr(str(active))+''')
 if not p.exists() or json.loads(p.read_text()).get('status')!='ACTIVE_FUTURE_ONLY':
  print(json.dumps({'status':'HOLD','reason':'CPU_FIXTURE_NO_ACTIVE_METADATA','scientific_starts':0}),file=sys.stderr);sys.exit(2)
print(json.dumps({'target':target,'argv':args,'env':{k:os.environ.get(k)for k in ['EP_MULTIWORKLOAD_NATIVE_ENTRY','EP_MATCHED_SCOPE_ACCEPT_ENTRY','EP_MATCHED_NATIVE_ENTRY','EP_TAG_CAPACITY_NATIVE_ENTRY']},'CPU_SINK_ONLY':True,'model_starts':0}))
''')
def instrument(content):
 lines=[];n=0
 for line in content.decode().splitlines(keepends=True):
  body=line.strip()
  if body.startswith('exec '):
   words=shlex.split(body)
   if words[:3]==['exec','/usr/bin/python3','-B']and words[-1]=='$@':target=words[3]
   elif words[:2]==['exec','/bin/sh']and words[-1]=='$@':target=words[2]
   else:raise AssertionError('Uninstrumented execution target '+line)
   indent=line[:len(line)-len(line.lstrip())]
   line=indent+'exec /usr/bin/python3 '+shlex.quote(str(sink))+' --target '+shlex.quote(target)+' "$@"\n';n+=1
  lines.append(line)
 return ''.join(lines),n
oldtext,on=instrument(old);newtext,nn=instrument(candidate);check(nn==on+1,'all legacy execution targets plus exactly one opt-in target instrumented')
oldpath=fixture/'native.old.instrumented.sh';newpath=fixture/'native.new.instrumented.sh';oldpath.write_text(oldtext);newpath.write_text(newtext);os.chmod(oldpath,0o755);os.chmod(newpath,0o755)
wrapper=fixture/'experiment';wrapper.write_text('#!/bin/sh\nset -eu\nexec '+shlex.quote(str(newpath))+' experiment "$@"\n');os.chmod(wrapper,0o755)
check('/root/data/ep_l2_dtc_l1_native_v2/bin/native'not in wrapper.read_text(),'independent fixture experiment wrapper never jumps to production native')
for label,text in [('candidate',candidate),('original',old),('instrumented-new',newtext.encode()),('instrumented-old',oldtext.encode()),('fixture-wrapper',wrapper.read_bytes())]:
 result=subprocess.run(['/bin/sh','-n'],input=text,capture_output=True);check(result.returncode==0,'sh -n '+label)
def run(path,args):return subprocess.run([str(path),*args],capture_output=True,text=True,timeout=10)
def record(label,result):cases.append({'case':label,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
cohort='E2-DTCL2MLP-16f4c42373e4961e-DH-E384-V1';flag='--padding-only-admission-v1'
legacy=[[],['experiment','prepare',cohort,'--project','DTC_L1'],['experiment','run-native',cohort,'--project','DTC_L1'],['result','archive',cohort],['experiment','prepare','E2-DTCHASH18-eededb785179fc04-DH-P0-V1','--project','DTC_L1'],['result','archive','E2-DTCHASH18-eededb785179fc04-DH-P0-V1'],['experiment','run-native','EP_MULTI_FWT_S_ET1_20261027_V1','--project','EP_L2'],['result','accept-final-scopes','EP_MATCH_D_S_L0_20261027_V1'],['experiment','inspect','EP_TAGFLOW_VECTOR_A_S64_W16_T1_20261027_V1'],['experiment','prepare','UNKNOWN_COHORT'],['experiment','inspect','UNKNOWN $(touch NEVER_EXECUTED) literal space']]
for n,args in enumerate(legacy):
 a=run(oldpath,args);b=run(newpath,args);record('legacy-'+str(n),b);check((a.returncode,a.stdout,a.stderr)==(b.returncode,b.stdout,b.stderr),'no-optin exact legacy argv/env/result '+str(n))
active.write_text(json.dumps({'status':'ACTIVE_FUTURE_ONLY'}))
for op in ['prepare','inspect','run-native']:
 args=['experiment',op,cohort,'--project','DTC_L1',flag];r=run(newpath,args);record('optin-'+op,r);v=json.loads(r.stdout);check(r.returncode==0 and v['target']==DEFAULT and v['argv']==args,'correct optin '+op+' forwards exact argv only to fixture private frontend')
r=run(wrapper,['prepare',cohort,flag,'--project','DTC_L1']);record('fixture-experiment-wrapper',r);check(r.returncode==0 and json.loads(r.stdout)['argv']==['experiment','prepare',cohort,flag,'--project','DTC_L1'],'actual isolated experiment wrapper preserves argument order')
negatives=[['result','archive',cohort,flag],['project','prepare',cohort,'--project','DTC_L1',flag],['experiment','prepare','EP_MULTI_FWT_S_ET1_20261027_V1','--project','DTC_L1',flag],['experiment','register',cohort,'--project','DTC_L1',flag],['experiment','prepare',cohort,'--project','EP_L2',flag],['experiment','prepare',cohort,flag],['experiment','prepare',cohort,'--project','DTC_L1',flag,flag],['experiment','prepare',cohort,'--project','DTC_L1','--project','DTC_L1',flag],['experiment','prepare',cohort,'--project','DTC_L1',flag,'--unknown'],['experiment','prepare',cohort,'--project','DTC_L1','--padding-only-admission-v2'],['experiment','prepare',cohort,'--project','DTC_L1',flag+'=true'],['experiment',flag]]
for n,args in enumerate(negatives):
 r=run(newpath,args);record('invalid-optin-'+str(n),r);check(r.returncode==2 and not r.stdout and json.loads(r.stderr)['status']=='HOLD','wrong context/duplicate/unknown flag fails closed '+str(n))
active.unlink();args=['experiment','prepare',cohort,'--project','DTC_L1',flag];r=run(newpath,args);record('no-active-metadata-stub',r);check(r.returncode==2 and json.loads(r.stderr)['reason']=='CPU_FIXTURE_NO_ACTIVE_METADATA','routing to private gate grants no authority when fixture ACTIVE missing')
active.write_text(json.dumps({'status':'PENDING'}));r=run(newpath,args);record('inactive-metadata-stub',r);check(r.returncode==2,'inactive fixture metadata HOLD')
# A real accepted terminal control is read-only; entry SHA is absent from its
# binding/identity checks. This does not pretend the candidate was installed.
strictpath=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/tools/l2_strict.py');s=importlib.util.spec_from_file_location('route_original_strict_readonly',strictpath);st=importlib.util.module_from_spec(s);s.loader.exec_module(st);v=st.terminal(cohort)
check(v['status']=='L2_MLP_NATIVE_TRACE_PERFORMANCE_QUALIFIED'and v['performance_accepted']is True,'real accepted gaussian DH-E384 strict control remains valid without production entry edits')
check(sha(production)==before,'production native entry bytes unchanged throughout fixture checks')
out={'status':'PASS','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':len(checks),'check_labels':checks,'cases':cases,'model_starts':0,'signals':0,'production_changes':False,'candidate_manifest':manifest,'production_source_sha256_before_after':before,'fixture_root':str(fixture),'strict_control':{'cohort':cohort,'cycles':v['cycles'],'strict_source_sha256':sha(strictpath)},'qualification_layers':{'real_shell_argv_routing':'QUALIFIED_WITH_ALL_EXEC_TARGETS_REPLACED_BY_CPU_SINK','metadata_stub':'ONLY_FIXTURE_HOLD_NOT_CENTRAL_REGISTRY_QUALIFICATION','actual_B_private_frontend':'NOT_CLAIMED_BY_THIS_ROUTE_QUALIFICATION','production_entry_installation':'NOT_PERFORMED'},'code_sha256':{p.name:sha(p)for p in [HERE/'build_route.py',HERE/'qualify_route.py']}}
(HERE/'CPU_ROUTE_QUALIFICATION.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['cases','check_labels']}))
