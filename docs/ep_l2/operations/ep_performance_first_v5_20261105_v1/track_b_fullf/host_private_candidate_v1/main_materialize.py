#!/usr/bin/env python3
"""Main-only private materializer. Default check writes nothing; never science."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys,os
H=Path(__file__).parent.resolve();R=H/'runtime';E=H/'execution';D=H/'documents';C=H/'prospective_specs'
sys.path.insert(0,str(R))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def need(v,m):
 if not v:raise ValueError(m)
def read(p):return json.loads(Path(p).read_bytes())
def exact(r):need(sha(r['path'])==r['sha256'],'immutable ref drift');return read(r['path'])
def engine():
 sp=importlib.util.spec_from_file_location('b1_materializer_engine',R/'ep_perf_native_wv_modes_draft.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def validate_main_review(p):
 q=read(p);t=read(D/'MAIN_REVIEW_TEMPLATE_NOT_SIGNED.json')
 need(q.get('schema')==t['schema']and q.get('status')=='MAIN_REVIEWED_EXACT_SOURCE283','Main exact Source283 review marker')
 need(q.get('approved_by')=='EP-MAIN'and q.get('cpu_reviewed_by')=='EP-MAIN'and q.get('independent_review_pass')is True,'Main independent CPU/source review required')
 for k in ['source_identity','request_id','consumer_graph_ref','contract_ref','mode_contract_ref','option_tables','materializer_ref']:need(q.get(k)==t[k],'Main review exact binding '+k)
 need(q.get('science_authorization')is False,'engineering review is not science authorization')
 graph=exact(q['consumer_graph_ref'])
 for r in graph['runtime']+graph['engineering_documents']:need(sha(r['path'])==r['sha256'],'Main-reviewed graph drift')
 return q
def main(argv=None):
 a=argparse.ArgumentParser();a.add_argument('--materialize',action='store_true');a.add_argument('--main-review');n=a.parse_args(argv)
 m=engine();specs=[read(p)for p in sorted(C.glob('*.json'))]
 need(len(specs)==2,'exact two candidates')
 for s in specs:m.engineering_static(s)
 m.module(specs[0]['mode_contract_ref'],'materializer_pair').validate_fair_pair(*specs)
 if not n.materialize:return dict(status='READ_ONLY_ENGINEERING_CHECK_PASS_MAIN_REVIEW_REQUIRED',points=2,writes=0,models=0,science_authorization=False)
 need(n.main_review,'explicit Main review path required')
 review=validate_main_review(Path(n.main_review).resolve())
 reg,_=m.authority();need(m.GOAL not in reg['registered_future_requests'],'registered scope Specs must never be overwritten')
 outputs=[]
 for s in specs:
  s=dict(s,Main_engineering_binding_ref=ref(Path(n.main_review).resolve()),science_authorization=False)
  m.engineering_static(s);m.module(s['mode_contract_ref'],'main_signed_mode').validate_static(s)
  p=E/'cases'/s['cohort']/'control/FROZEN_SPEC.json'
  need(p.is_relative_to(H)and not p.exists(),'private exclusive materialization only')
  outputs.append((p,s))
 # Preflight all outputs before the first write. No overwrite/shared mutation.
 for p,s in outputs:
  p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb')as f:f.write((json.dumps(s,sort_keys=True,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
 payload=dict(status='MAIN_REVIEWED_PRIVATE_ENGINEERING_MATERIALIZED_NOT_SCIENCE',request_id=m.GOAL,source_identity=review['source_identity'],Main_review_ref=ref(Path(n.main_review).resolve()),spec_refs=[ref(p)for p,s in outputs],native_entry_ref=specs[0]['native_entry_ref'],native_route_guard_ref=specs[0]['native_route_guard_ref'],owned_runtime_graph_ref=review['consumer_graph_ref'],exact_cohorts=sorted(x['cohort']for x in specs),science_authorization=False,registered_budget=0,models=0,shared_native_installed=False)
 path=E/'control/MAIN_ENGINEERING_INSTALL_PAYLOAD.json'
 need(not path.exists(),'payload exists; no silent re-materialize')
 with path.open('xb')as f:f.write((json.dumps(payload,sort_keys=True,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
 return dict(status=payload['status'],spec_refs=payload['spec_refs'],science_authorization=False,registered_budget=0,models=0)
if __name__=='__main__':
 try:print(json.dumps(main()))
 except Exception as e:print(json.dumps(dict(status='HOLD',reason=str(e),models=0,science_authorization=False)),file=sys.stderr);sys.exit(2)
