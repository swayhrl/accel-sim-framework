"""Additive source-bound native scopes; never substitute a legacy proof for ordinary input."""
import json,hashlib
from pathlib import Path
PIN='1740009d1579b2402b32076f4f65f27619396c01'
def require(ok,why):
 if not ok:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def find_anchor(R,w,mode,git):
 path='docs/ep_l2/review_packs/FT20261017_LANE6_R18_FIVE_PAIR_EN_V6_r1/PAPER_CURRENT_FIVE_PAIR_INTAKE.json'
 raw=(R/path).read_bytes();require(raw==git('show',PIN+':'+path),'Frozen H0 manifest changed')
 found=[]
 for item in json.loads(raw)['intakes']:
  p=item['intake_directory']+'/SAD_NATIVE_INTAKE.json';b=(R/p).read_bytes();require(b==git('show',PIN+':'+p),'Frozen H0 packet changed')
  for run in json.loads(b)['packet']['runs']:
   if run['workload']==w and run['mode']==mode:found.append((run,p))
 require(len(found)==1,'No exact accepted H0 workload/mode anchor');return found[0]
def scope_kind(adapter,q,w):
 require(adapter.get('workload',w)==w,'Adapter workload mismatch')
 require(adapter['experiment_id']=='EPL2_DOWNSTREAM_HEADROOM_R19' and adapter['regime'] in ('Q4','D4','D2','L25'),'Wrong experiment/condition')
 if w in ('convolutionSeparable','FWT_7_21'):
  require(q['atomic_input_auditor_sha256']=='187cd19145d48e89fc63129faa45ccdc7d207d50272527ffdebbe01ac18694e4','Legacy path needs exact qualified native auditor')
  return 'SOURCE_BOUND_LEGACY_NATIVE_R17'
 require(w in ('sad','vectorAdd_4M'),'Unqualified workload')
 require(adapter['regime']=='D4','Ordinary extension currently qualified only for D4')
 require(q['release_name']=='R19_D4_B16_U_WB16_ORDINARY_NONLEGACY_ROBUSTNESS_SCOPE_r1','Ordinary scope requires its own qualified certificate')
 require(w in q['selected_robustness_workloads'] and q['atomic_input_auditor_sha256']=='6ad289048168c83b1354ac73c63e9c9444fec75ac8963b3e99e4f0a8896962b8','Wrong ordinary input qualification')
 require('input_adapter_revision' not in q,'Legacy adapter is not ordinary qualification')
 return 'SOURCE_BOUND_ORDINARY_NATIVE_Q1'
def bind_scope(R,a,q,run,base,anchor_path,git):
 w=run['workload'];kind=scope_kind(a,q,w);ident=run['identity'];audit=run['original_result']['audit'];spec=run['original_spec']
 require(base['workload']==w and base['mode']==run['mode'],'H0 anchor workload/mode mismatch')
 for key in ('core_source_commit','framework_source_commit','binary_sha256','trace_content_sha256','workload','epoch_range','termination_contract'):
  require(base['identity'][key]==ident[key],'H0/condition identity mismatch: '+key)
 require(base['original_result']['audit']['traces']==audit['traces'],'Condition must retain exact accepted H0 full trace bodies')
 out={'workload':w,'mode':run['mode'],'kind':kind,'H0_anchor':anchor_path,'H0_anchor_sha256':sha((R/anchor_path).read_bytes()),'trace_content_sha256':ident['trace_content_sha256'],'qualification_publication':a['qualification_publication'],'qualification_path':a['qualification_path']}
 if kind=='SOURCE_BOUND_LEGACY_NATIVE_R17':
  p='docs/ep_l2/review_packs/FT20261017_LANE5_R17_NATIVE_BYTE_SEMANTIC_PROOF_r1/NATIVE_LEGACY_BYTE_SEMANTIC_PROOF_R17_r1.json';raw=git('show',run['_current_pub']+':'+p) if '_current_pub' in run else git('show',a['_current_pub']+':'+p)
  require(sha(raw)=='9b62884190b8f6bd77d3b3bf873d0e3e60ce718db9e7c51a9797ec99bd46dce2','Legacy byte proof changed');proof=json.loads(raw)
  require(proof['status']=='PASS_FULL_NATIVE_BYTE_AND_ZERO_MASK_SEMANTIC_PROOF','Legacy proof not PASS');items=[v for v in proof['workloads'] if v['workload']==w];require(len(items)==1,'Legacy proof workload mismatch')
  require(all(ident[k]==v for k,v in proof['source_identity'].items()),'Legacy proof source mismatch');require(sorted([{k:f[k] for k in ('name','bytes','sha256')} for f in items[0]['files']],key=lambda z:z['name'])==[z for z in audit['traces'] if z['name']!=spec['entry_trace_name']],'Legacy proof content mismatch');out['legacy_proof_sha256']=sha(raw)
 else:
  ref=spec['atomic_input_scope'];raw=Path(ref['path']).read_bytes();proof=json.loads(raw);require(sha(raw)==ref['sha256']==run['original_result']['audit']['atomic_input_scope']['sha256'],'Ordinary per-spec proof identity mismatch')
  require(proof['tool_sha256']==q['atomic_input_auditor_sha256'] and proof['trace_content_manifest']==audit['traces'],'Ordinary complete-body auditor/manifest mismatch');out.update(ordinary_proof_path=ref['path'],ordinary_proof_sha256=sha(raw),legacy_proof_used=False)
 return out
