"""Default plan only; --check is strictly read-only engineering qualification."""
from pathlib import Path
import sys,json,argparse,importlib.util
D=Path(__file__).resolve().parent
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
 request=json.loads((D/'3MM_EXACT_REQUEST_V5.json').read_bytes())
 if not a.check:
  print(json.dumps(dict(status='PLAN_ONLY_NO_ACTORS',request_id=request['request_id'],requested=3,approved=0,registered=0,consumed=0,entry='--check performs read-only source/schema/mode/resource wiring checks only; no activation or model flags exist')));return 0
 sys.path.insert(0,str(D/'three_mm/runtime'));import ep_perf_native_wv_modes_draft as e
 rows=[]
 for ref in request['prospective_spec_refs']:
  s=e.read(ref['path']);e.need(e.sha(ref['path'])==ref['sha256'],'prospective Spec drift');e.engineering_spec_for(s['cohort'])
  try:e.fresh_science_authorization(s)
  except Exception as exc:e.need(str(exc)=='MISSING_FRESH_EXACT_REQUEST3_SCIENTIFIC_AUTHORIZATION','unexpected science hold')
  else:raise ValueError('preparation unexpectedly has science authorization')
  rows.append(dict(cohort=s['cohort'],status='ENGINEERING_PASS_UNAPPROVED',limits=s['limits']))
 r=e.module(e.read(request['prospective_spec_refs'][0]['path'])['resource_module_ref'],'d_current_resource')
 snap=r.snapshot();e.need(not snap['current_scope_registered'],'unexpected A2 budget registered')
 try:r.admit(snap,5*(1<<30),64*(1<<20),dict(max_global_EP_models=10))
 except Exception as exc:e.need(str(exc)=='V5_A2_REQUEST_NOT_REGISTERED','unexpected admit rejection')
 else:raise ValueError('unregistered admission passed')
 result=dict(status='PASS_CURRENT_ENGINEERING_ONLY'if not snap['foreign_metadata_errors']else'HOLD_CURRENT_FOREIGN_RESOURCE_MAPPING',points=rows,current_foreign_metadata_errors=snap['foreign_metadata_errors'],new_budget_or_starts=0,shared_Native_or_registry_writes=False)
 print(json.dumps(result,sort_keys=True));return 0 if not snap['foreign_metadata_errors']else 2
if __name__=='__main__':sys.exit(main())
