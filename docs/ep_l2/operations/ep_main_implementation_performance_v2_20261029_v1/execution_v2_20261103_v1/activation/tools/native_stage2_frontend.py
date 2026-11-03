"""Main exact eight-cohort sole-entry adapter. One group per fresh process."""
import os,sys,json,importlib.util,pathlib
E=pathlib.Path(__file__).resolve().parents[1]
W=('EP_PERF_V2_PROPOSED_GEMM_140F6ED3_W_ONLY','EP_PERF_V2_PROPOSED_FASTWALSHTRANSFORM_FC3A9062_W_ONLY')
T=tuple('EP_PERF_T3_CONV16X8_'+arm+'_'+profile+'_V1' for arm in ('A_F_MINUS_T','B_LEGACY_F','C_CORRECTED_F') for profile in ('OFF','ON'))
def main(a):
 assert os.environ.get('EP_FULL_PERF_NATIVE_ENTRY')=='1','native sole-entry required'
 assert len(a)==5 and a[0]=='experiment' and a[1] in ('prepare','inspect','run-native','accept') and a[3:]==['--project','EP_L2'],'exact native command'
 c=a[2];assert c in W+T,'outside user-authorized exact eight cohorts'
 r=E/('runtime_w' if c in W else 'runtime_t');sys.path.insert(0,str(r))
 if c in W:
  from ep_perf_frontend import main as f
  return f(a)
 from ep_perf_common_v2 import authority,sha,read,ROOT,GOAL,module,P
 reg,_=authority();q=reg['registered_future_requests'][GOAL];p=ROOT/'cases'/c/'control/FROZEN_SPEC.json'
 assert sha(p)==q['admitted_specs'][c],'registered spec drift'
 s=read(p);v=s['host_engine_ref'];assert P(v['path']).is_relative_to(r) and sha(v['path'])==v['sha256'],'runtime location/content drift'
 if a[1]=='accept':return module(s['postprocess_module_ref'],'exact_postprocess').postprocess(c)
 return module(v,'exact_engine').main(a)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:])))
 except Exception as e:
  print(json.dumps(dict(status='HOLD',reason=str(e),automatic_retry=False)),file=sys.stderr);sys.exit(2)
