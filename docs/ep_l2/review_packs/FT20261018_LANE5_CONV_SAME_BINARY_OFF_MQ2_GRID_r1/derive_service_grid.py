"""Derive one same-binary service grid solely from current accepted immutable rows."""
import argparse,csv,hashlib,json,subprocess,sys,datetime
from pathlib import Path
ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1')
sys.path.insert(0,str(ROOT/'util/ep_l2/ft_lane5'))
from acceptance import load_current_authority,current_manifest
BINARY='f0af8515057e315af708a0e3c2fde4a3098b0c0fb3f7014471d8d8c9426f1f30'
CORE='84359d4ba492acb639a2092fa271e9169038bf7d';FRAMEWORK='197741be9be9b8e390a557d639503b416d8e95f0'
PROFILES=['B16_OFF','S64','U_OFF']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--workload',required=True,choices=['convolutionSeparable','FWT_7_21']);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--include-rg1',action='store_true');a=ap.parse_args()
 out=a.out.resolve();assert out.is_relative_to(ROOT/'docs/ep_l2/review_packs');assert not out.exists(),'Never overwrite old grid revision'
 state=load_current_authority();m=current_manifest(state);conditions=['SERVICE_OFF','SERVICE_MQ2']+(['SERVICE_RG1'] if a.include_rg1 else [])
 rows=[r for r in m['rows'] if r.get('workload')==a.workload and r.get('binary_sha256')==BINARY and r.get('profile') in PROFILES and r.get('regime') in conditions and r.get('scientific_acceptance')=='CURRENT_ACCEPTED']
 index={}
 base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 for r in rows:
  key=(r['profile'],r['regime']);assert key not in index,'Duplicate current endpoint';assert r['core_source_commit']==CORE and r['framework_source_commit']==FRAMEWORK
  p=ROOT/r['independent_review']['path'];assert sha(p)==r['independent_review']['sha256'];assert p.read_bytes()==subprocess.check_output(['git','show',base+':'+str(p.relative_to(ROOT))],cwd=ROOT)
  comp=p.parent/'COMPARISON.json';assert comp.read_bytes()==subprocess.check_output(['git','show',base+':'+str(comp.relative_to(ROOT))],cwd=ROOT);c=json.loads(comp.read_text());assert c['cycles']==r['observed_cycles'] and c['instructions']==r['instructions']
  index[key]={**r,'comparison_asset':{'path':str(comp.relative_to(ROOT)),'sha256':sha(comp)},'service_totals':c['service_totals']}
 assert set(index)=={(p,c) for p in PROFILES for c in conditions},'Grid incomplete; wait, do not infer missing endpoints'
 rows=[index[(p,c)] for c in conditions for p in PROFILES];assert len({r['trace_content_sha256'] for r in rows})==1;assert len({r['instructions'] for r in rows})==1
 mode_effects=[]
 for c in conditions:
  b,s,u=[index[(p,c)]['observed_cycles'] for p in PROFILES]
  mode_effects.append({'condition':c,'B16_cycles':b,'S64_cycles':s,'Unified_cycles':u,'B16_over_Unified':b/u,'S64_over_Unified':s/u,'B16_over_S64':b/s,'Unified_cycles_saved_vs_B16':b-u,'Unified_fraction_cycles_saved_vs_B16':(b-u)/b,'Unified_cycles_saved_vs_S64':s-u,'Unified_fraction_cycles_saved_vs_S64':(s-u)/s})
 within=[]
 for c in conditions[1:]:
  for p in PROFILES:
   off=index[(p,'SERVICE_OFF')]['observed_cycles'];on=index[(p,c)]['observed_cycles'];within.append({'profile':p,'condition':c,'OFF_cycles':off,'ON_cycles':on,'OFF_over_ON':off/on,'absolute_cycles_saved':off-on,'fraction_cycles_saved':(off-on)/off})
 comparison={'status':'COMPLETE_CURRENT_ACCEPTED_SAME_BINARY_GRID','workload':a.workload,'conditions':conditions,'mode_comparisons':mode_effects,'within_mode_OFF_ON':within,'geomean':None,'limits':['Exploratory complete Conv/FWT service sensitivity, never overwrite original five-workloadH0 mean1.0016002037656606','All performance ratios use this exact new binary and workload only; no cross-binary anchors','Enabled-only wait counters and overlapping bank-cycle sums are not applicationcycles saved','MQ2 inputs contain LDG.E.SYS excluded by current conservative classifier; zero observed effects do not test eligible ordinary-LDG bypass','No combinedMQ2+RG1, no negative result removal']}
 receipt={'status':comparison['status'],'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_publication_before_grid':base,'current_V2_binding':state['binding'],'core_source':CORE,'framework_source':FRAMEWORK,'binary_sha256':BINARY,'workload':a.workload,'conditions':conditions,'profiles':PROFILES,'accepted_endpoint_count':len(rows),'trace_content_sha256':rows[0]['trace_content_sha256'],'native_instructions_each':rows[0]['instructions'],'new_starts':0,'new_scientific_acceptances':0,'new_budget_or_deadline':False,'scope':'Derived from immutable remote-published currentaccepted endpoint reviews; all originalraw, failedattempts and oldH0 remain untouched. Individual endpoint handoffs precede this grid.'}
 out.mkdir();put(out/'ROWS.json',rows);put(out/'COMPARISON.json',comparison);put(out/'RECEIPT.json',receipt)
 with (out/'CYCLES.csv').open('w',newline='') as f:
  names=['workload','profile','regime','observed_cycles','instructions','run_key','runtime_config_sha256','trace_content_sha256','binary_sha256'];writer=csv.DictWriter(f,fieldnames=names,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
 (out/'derive_service_grid.py').write_bytes(Path(__file__).read_bytes());(out/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(out.iterdir()) if p.name!='SHA256SUMS'))
 print(json.dumps({'pack':str(out.relative_to(ROOT)),'accepted':len(rows),'mode_comparisons':mode_effects,'OFF_ON':within},sort_keys=True))
if __name__=='__main__':main()
