#!/usr/bin/env python3
"""Read accepted native points only; produce bounded six-cell analysis."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,subprocess,importlib.util
P=pathlib.Path;J=P('/root/data/ep_l2_matched_baseline_t_dram_latency_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def main():
 reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
 cases=read(J/'agent_a/joint_attribution/PARTIAL_ACCEPTED_THREE_INPUTS_V1.json')['cases'][:1]
 for tag in ['S_L0','S_L1','FMT_L0','FMT_L1','F_L1']:
  c='EP_MATCH_D_'+tag+'_20261027_V1';r=reg['registered_future_requests'][c];assert r['state']=='CLOSED'and r['consumed']==1 and r['remaining']==r['reserved_write_bytes']==0
  point=P(r['accepted_point_path']);d=read(point);assert sha(point)==r['accepted_point_sha256']and d['hardware_drained']
  spec=J/'cases'/c/'control/FROZEN_SPEC.json';raw=point.parent/'raw.log'
  assert sha(raw)==d['raw_sha256']and sha(spec)==d['native_spec_sha256']
  cases.append({'label':'MATCHED_'+tag,'mode':d['mode'],'raw_path':str(raw),'raw_sha256':sha(raw),'spec_path':str(spec),'spec_sha256':sha(spec),'accepted_point_path':str(point),'accepted_point_sha256':sha(point)})
 out=J/'analysis/FINAL_SIX_ACCEPTED';assert not out.exists();manifest=J/'analysis/FINAL_SIX_INPUTS.json';assert not manifest.exists();manifest.write_text(json.dumps({'cases':cases},indent=2)+'\n')
 tool=J/'agent_a/joint_attribution/joint_attribution_v4.py';assert sha(tool)=='46e3f4605f3bbc2b91ecb2aca752de6c15c3409e0996266e981cf38e1e4bfd28'
 subprocess.run(['/usr/bin/python3','-B',str(tool),'--inputs',str(manifest),'--output-dir',str(out)],check=True)
 receipt={'status':'SIX_ACCEPTED_POINTS_OFFLINE_ANALYZED_NOT_NEW_RUN_AUTHORITY','inputs':{'path':str(manifest),'sha256':sha(manifest)},'analyzer_sha256':sha(tool),'outputs':{str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size}for p in out.iterdir()if p.is_file()},'new_application_starts':0,'native_rows':{c:r for c,r in reg['registered_future_requests'].items()if c.startswith('EP_MATCH_D_')}}
 (J/'analysis/FINAL_ANALYSIS_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':receipt['status'],'case_count':len(cases),'result_sha256':sha(out/'JOINT_ATTRIBUTION.json')}))
if __name__=='__main__':main()
