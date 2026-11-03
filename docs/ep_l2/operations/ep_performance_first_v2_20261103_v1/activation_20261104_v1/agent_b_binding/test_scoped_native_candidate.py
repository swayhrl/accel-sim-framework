# CPU shell-routing/private installation test. Never calls real native/model.
from pathlib import Path
import copy,json,os,subprocess,uuid
import scoped_native_install_candidate as native
P=Path(__file__).resolve().parent;T=P/'private_native_CPU';T.mkdir(exist_ok=True)
prior=T/'global_native_fixture';prior.write_bytes(b'#!/bin/sh\nprintf "FOREIGN_FALLBACK:%s\\n" "$*"\n');os.chmod(prior,0o755)
front=T/'frontend_fixture.py';front.write_text('import json,os,sys\nprint(json.dumps(dict(TEST_ONLY=True,argv=sys.argv[1:],flag=os.environ.get("EP_FULL_PERF_NATIVE_ENTRY"))))\n')
payload,pre=native.render(prior.read_bytes(),front);script=T/'scoped_native_fixture';script.write_bytes(payload);os.chmod(script,0o755)
rows=[]
def check(name,fn,reject=False):
 try:r=fn();ok=not reject;error=None
 except Exception as ex:r=None;error=repr(ex);ok=reject
 rows.append(dict(label=name,PASS=ok,error=error));assert ok,rows[-1];return r
check('POSIX_syntax',lambda:native.need(subprocess.run(['/bin/sh','-n',str(script)]).returncode==0,'bad shell'))
for case in native.COHORTS:
 r=subprocess.run([str(script),'experiment','prepare',case,'--project','EP_L2'],capture_output=True,text=True);out=json.loads(r.stdout);check('route_'+case,lambda r=r,out=out,case=case:native.need(r.returncode==0 and out['flag']=='1'and out['argv']==['experiment','prepare',case,'--project','EP_L2'],'wrong own route'))
case=native.COHORTS[0]
for op in ['inspect','run-native','accept']:
 r=subprocess.run([str(script),'experiment',op,case,'--project','EP_L2'],capture_output=True,text=True);out=json.loads(r.stdout);check('CPU_fixture_only_'+op,lambda r=r,out=out,op=op:native.need(r.returncode==0 and out['argv'][1]==op,'operation routing'))
for args in [['experiment','badop',case,'--project','EP_L2'],['experiment','prepare',case,'--project','DTC'],['experiment','prepare',case],['experiment','prepare',case,'--project','EP_L2','EXTRA']]:
 r=subprocess.run([str(script),*args],capture_output=True,text=True);check('reject_bad_own_'+str(len(rows)),lambda r=r:native.need(r.returncode==2 and 'CC_CAM_NATIVE_HOLD'in r.stderr,'invalid own must not fallback'))
r=subprocess.run([str(script),'experiment','inspect','DTC_FOREIGN_EXACT_CASE','--project','DTC'],capture_output=True,text=True);check('outside_scope_fail_closed_prior_unreachable',lambda:native.need(r.returncode==2 and 'outside exact scoped request'in r.stderr and 'FOREIGN_FALLBACK'not in r.stdout,'scoped foreign route must reject'))
for foreign in ['EP_PERF_VECTOR4M_F_REF_V1','EP_PERF_UNREGISTERED_UNKNOWN_V1','DTC_HISTORICAL_CASE']:
 r=subprocess.run([str(script),'experiment','run-native',foreign,'--project','EP_L2'],capture_output=True,text=True);check('reject_outside_'+foreign,lambda r=r:native.need(r.returncode==2 and 'FOREIGN_FALLBACK'not in r.stdout,'outside case reached prior router'))
check('current_global_suffix_bytes_exact',lambda:native.need(payload.endswith(prior.read_bytes())and payload.startswith(pre.encode()),'suffix drift'))
data=T/'exec/highclock';snap=T/'snapshot.bytes';snap.write_bytes(prior.read_bytes());candidate=T/'candidate.bytes';candidate.write_bytes(payload)
plan=dict(goal=native.GOAL,data_ROOT=str(data),entry_target=str(data.parent/'bin/native'),global_native_ref=native.ref(prior),prior_entry_ref=native.ref(snap),candidate_ref=native.ref(candidate),entry_ref=dict(path=str(data.parent/'bin/native'),sha256=native.sha_bytes(payload)),frontend_ref=native.ref(front),own_prelude=pre,cohorts=list(native.COHORTS))
# Unique CPU run target lets reruns preserve previous evidence rather than reset.
data=T/('exec_'+str(uuid.uuid4()))/'highclock';plan.update(data_ROOT=str(data),entry_target=str(data.parent/'bin/native'));plan['entry_ref']['path']=plan['entry_target']
check('private_install_only',lambda:native.apply_plan(plan,data,prior));check('private_install_idempotent',lambda:native.apply_plan(plan,data,prior));check('global_fixture_unchanged',lambda:native.need(native.ref(prior)==plan['global_native_ref'],'global changed'))
bad=copy.deepcopy(plan);bad['entry_target']=str(T/'outside/native');check('wrong_target_rejected',lambda:native.apply_plan(bad,data,prior),True)
bad=copy.deepcopy(plan);bad['candidate_ref']['sha256']='0'*64;check('tampered_candidate_rejected',lambda:native.apply_plan(bad,data,prior),True)
bad=copy.deepcopy(plan);bad['global_native_ref']['sha256']='0'*64;check('stale_prior_rejected',lambda:native.apply_plan(bad,data,prior),True)
bad=copy.deepcopy(plan);bad['cohorts'].append('EXTRA');check('extra_cohort_rejected',lambda:native.apply_plan(bad,data,prior),True)
result=dict(schema='EP_CC_CAM_SCOPED_NATIVE_CANDIDATE_PRIVATE_CPU_CONTROLS_V1',status='PASS_PRIVATE_FIXTURE_ONLY_NO_REAL_NATIVE_INSTALLATION',total=len(rows),passed=sum(x['PASS']for x in rows),controls=rows,actual_Native_installs=0,real_registry_writes=0,real_model_starts=0,private_python_frontend_fixture_only=True)
(P/'SCOPED_NATIVE_CPU_CONTROLS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(status=result['status'],passed=result['passed'],total=result['total'])))
