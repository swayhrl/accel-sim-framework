import json,os,sys
from ep_perf_common_v2 import *
COHORTS=['EP_PERF_PFV5_A_FWT_G32W8_S_V1', 'EP_PERF_PFV5_A_FWT_G32W8_WV_OFF_V1', 'EP_PERF_PFV5_A_FWT_G32W8_WV_ON_V1']
def main(args):
 need(os.environ.get('EP_FULL_PERF_NATIVE_ENTRY')=='1','sole entry required')
 need(len(args)==5 and args[0]=='experiment' and args[3:]==['--project','EP_L2'],'exact Native EP command')
 need(args[1]in['prepare','inspect','run-native','accept'],'operation')
 case=args[2];need(case in COHORTS,'outside exact independent request2 scope')
 s=read(ROOT/'cases'/case/'control/FROZEN_SPEC.json');engine=module(s['host_engine_ref'],'frontend_preclaim_schema');engine.engineering_spec_for(case);engine.fresh_science_authorization(s)
 registry,_=authority();q=registry['registered_future_requests'].get(GOAL);need(q is not None,'fresh Main request not registered')
 p=ROOT/'cases'/case/'control/FROZEN_SPEC.json';need(case in q['admitted_specs']and sha(p)==q['admitted_specs'][case],'spec not exactly registered')
 s=read(p);item=s['host_engine_ref'];need(P(item['path']).is_relative_to(P(__file__).resolve().parent)and sha(item['path'])==item['sha256'],'engine location/pin')
 if args[1]=='accept':return module(s['postprocess_module_ref'],'midtag_exact_postprocess').postprocess(case)
 return module(item,'midtag_exact_engine').main(args)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:])))
 except Exception as e:print(json.dumps(dict(status='HOLD',reason=str(e),automatic_retry=False)),file=sys.stderr);sys.exit(2)
