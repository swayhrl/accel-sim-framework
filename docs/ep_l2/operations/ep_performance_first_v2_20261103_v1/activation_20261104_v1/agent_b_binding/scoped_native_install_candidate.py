# Main scoped-native installation CANDIDATE. Default emit only.
from pathlib import Path
import argparse,hashlib,json,os,shlex,uuid
P=Path(__file__).resolve().parent
R=P/'qualified_runtime'
NATIVE=Path('/root/data/ep_l2_dtc_l1_native_v2')
DATA=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_cc_cam_highclock_20261104_v1/highclock')
GOAL='EP_L2_CC_CAM_REPAIRED_VECTOR4M_850_1275_1700_V1'
COHORTS=tuple(sorted('EP_PERF_CC_CAM_VECTOR4M_'+m+'_'+str(f)+'_V1'for m in ['S','F']for f in [850,1275,1700]))
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def ref(p):p=Path(p);return dict(path=str(p),sha256=sha_bytes(p.read_bytes()))
def need(v,m):
 if not v:raise ValueError(m)
def render(prior,frontend):
 first=prior.splitlines(keepends=True)[0];need(first.startswith(b'#!')and first.endswith(b'\n'),'preserve prior interpreter')
 pre=first.decode()+'''# Main exact-six CC-CAM route; current global native is the full suffix.
if [ "$#" -ge 3 ] && [ "$1" = experiment ]; then
  case "$3" in
    '''+'|'.join(COHORTS)+''')
      if [ "$#" -ne 5 ] || [ "$4" != --project ] || [ "$5" != EP_L2 ]; then
        printf '%s\\n' 'CC_CAM_NATIVE_HOLD exact5/project required' >&2; exit 2
      fi
      case "$2" in prepare|inspect|run-native|accept) ;;
        *) printf '%s\\n' 'CC_CAM_NATIVE_HOLD unsupported operation' >&2; exit 2;;
      esac
      export EP_FULL_PERF_NATIVE_ENTRY=1
      exec /usr/bin/python3 -B '''+shlex.quote(str(frontend))+''' "$@"
      ;;
  esac
fi
printf '%s\\n' 'CC_CAM_NATIVE_HOLD outside exact scoped request' >&2
exit 2
'''
 return pre.encode()+prior,pre

def emit():
 prior=NATIVE/'bin/native';front=R/'ep_perf_frontend.py';prior_bytes=prior.read_bytes();payload,prelude=render(prior_bytes,front)
 out=P/'native_install_candidate';out.mkdir(exist_ok=True);snapshot=out/('GLOBAL_NATIVE_PRIOR_'+sha_bytes(prior_bytes)+'.bytes')
 if not snapshot.exists():snapshot.write_bytes(prior_bytes)
 need(snapshot.read_bytes()==prior_bytes,'immutable prior snapshot drift')
 candidate=out/'scoped_native_candidate';candidate.write_bytes(payload);os.chmod(candidate,0o755)
 plan=dict(schema='EP_MAIN_CC_CAM_SCOPED_NATIVE_INSTALL_CANDIDATE_V1',status='CANDIDATE_EMITTED_NOT_INSTALLED',goal=GOAL,data_ROOT=str(DATA),entry_target=str(DATA.parent/'bin/native'),global_native_ref=ref(prior),prior_entry_ref=ref(snapshot),candidate_ref=ref(candidate),entry_ref=dict(path=str(DATA.parent/'bin/native'),sha256=sha_bytes(payload)),frontend_ref=ref(front),own_prelude=prelude,cohorts=list(COHORTS),global_native_change_permitted=False,scientific_starts=0)
 (out/'NATIVE_INSTALL_PLAN.json').write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n');return plan

def apply_plan(plan,expected_data_ROOT=DATA,expected_global_native=NATIVE/'bin/native'):
 # Main only. CPU tests explicitly pass private roots; CLI never overrides them.
 expected_data_ROOT=Path(expected_data_ROOT);expected_global_native=Path(expected_global_native)
 need(plan['goal']==GOAL and plan['cohorts']==list(COHORTS),'exact scope only')
 need(Path(plan['data_ROOT'])==expected_data_ROOT and Path(plan['entry_target'])==expected_data_ROOT.parent/'bin/native','target scope mismatch')
 need(Path(plan['global_native_ref']['path'])==expected_global_native and ref(expected_global_native)==plan['global_native_ref'],'global native changed; rederive, never overwrite')
 prior=Path(plan['prior_entry_ref']['path']).read_bytes();payload=Path(plan['candidate_ref']['path']).read_bytes()
 need(sha_bytes(prior)==plan['prior_entry_ref']['sha256']and prior==expected_global_native.read_bytes(),'prior snapshot mismatch')
 need(sha_bytes(payload)==plan['candidate_ref']['sha256']==plan['entry_ref']['sha256']and payload.endswith(prior)and payload.startswith(plan['own_prelude'].encode()),'candidate suffix/prefix/identity')
 need(ref(plan['frontend_ref']['path'])==plan['frontend_ref'],'frontend changed')
 target=Path(plan['entry_target']);target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():need(target.read_bytes()==payload,'existing scoped native differs; no overwrite')
 else:
  tmp=target.with_name('.native.'+str(uuid.uuid4()));tmp.write_bytes(payload);os.chmod(tmp,0o755);os.replace(tmp,target)
 need(ref(target)==plan['entry_ref']and expected_global_native.read_bytes()==prior,'closed entry/global verification')
 route=dict(goal=GOAL,status='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE',entry_ref=plan['entry_ref'],prior_entry_ref=plan['prior_entry_ref'],own_prelude=plan['own_prelude'],global_native_ref=plan['global_native_ref'],frontend_ref=plan['frontend_ref'],global_native_unchanged=True,scientific_starts=0)
 p=expected_data_ROOT/'control/NATIVE_ENTRY_ROUTE.json';p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():need(json.loads(p.read_text())==route,'existing route differs')
 else:p.write_text(json.dumps(route,indent=2,sort_keys=True)+'\n')
 return dict(status='SCOPED_ENTRY_INSTALLED_GLOBAL_NATIVE_UNCHANGED_NO_SCIENCE',route_ref=ref(p),entry_ref=ref(target))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');a=parser.parse_args()
 if not a.apply:print(json.dumps(emit()))
 else:
  p=P/'native_install_candidate/NATIVE_INSTALL_PLAN.json';print(json.dumps(apply_plan(json.loads(p.read_text()))))
