"""Main-only private materializer. Default check never writes, installs, consumes or starts."""
from pathlib import Path
import argparse,ast,copy,hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
SOURCE5=json.loads((HERE.parent/'SOURCE5_CANDIDATE.json').read_bytes())['Source5']
def need(x,m):
 if not x:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def ref(p):return dict(path=str(p),sha256=sha(p))
def exact(r):need(isinstance(r,dict)and sha(r['path'])==r['sha256'],'immutable ref mismatch');return read(r['path'])
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--materialize',action='store_true');ap.add_argument('--contract-ref-file',type=Path);ap.add_argument('--cpu-review-ref-file',type=Path);args=ap.parse_args()
 build=read(HERE/'PRIVATE_GRAPH_BUILD.json')
 if not args.contract_ref_file or not args.cpu_review_ref_file:
  need(not args.materialize,'Main contract/review exact refs required before materialize')
  print(json.dumps(dict(status='CHECK_ONLY_MAIN_ENGINEERING_MARKERS_PENDING',writes=0,Source5=SOURCE5,scientific_permission=False)));return 0
 cr=read(args.contract_ref_file);qr=read(args.cpu_review_ref_file);contract=exact(cr);review=exact(qr)
 need(contract['Source5']==review['Source5']==SOURCE5,'Main review Source5 mismatch')
 need(contract['schema']=='EP_V5_ONE_SOURCE283_CONSUMER_CONTRACT_V1'and contract['scope']=='EXACT_ONE_SOURCE283_ONLY'and contract['review_status']=='MAIN_REVIEWED_EXACT_SOURCE283'and contract['option_count']==283,'Main exact283 contract not approved')
 need(review['approved_by']=='EP-MAIN'and review['review_boundary']=='EXACT_SOURCE283_CONSTRUCTOR_AND_FEATURE_CONTRACT_ONLY'and review['application_model_started']is False,'Main CPU-only review absent')
 need(contract['production_CPU_review_ref']==qr,'Main contract/review exact ref mismatch')
 need(set(review['closed_profiles'])==set(contract['expected_283_maps_by_profile'])=={'S','WV_OFF','WV_ON'},'exact3 profile population')
 need(contract['declared_feature_options']==['-gpgpu_ep_l2_tvd_cold_filter'],'feature whitelist')
 for k in review['closed_profiles']:
  need(exact(contract['expected_283_maps_by_profile'][k])==exact(review['actual_constructed_283_map_refs'][k]),'actual283 map mismatch')
 receipt=exact(review['actual_constructor_receipt_ref']);need(receipt['Source5']==SOURCE5,'constructor Source5')
 need(all(r['returncode']==0 and r['expected_options']==r['actual_options']==283 and not r['mismatches']and r['constructor_pass']for r in receipt['runs']),'constructor proof incomplete')
 manifest=read(HERE/'HOST_PRIVATE_CANDIDATE_MANIFEST.json')
 for r in manifest['files']:need(sha(r['path'])==r['sha256'],'private candidate changed after review')
 if not args.materialize:
  print(json.dumps(dict(status='CHECK_PASS_APPROVED_ENGINEERING_NO_WRITES',writes=0,Source5=SOURCE5,contract_ref=cr,review_ref=qr,scientific_permission=False)));return 0
 # Output only to a new bounded owned descendant. Never edits the reviewed candidate.
 key=hashlib.sha256((cr['sha256']+qr['sha256']).encode()).hexdigest()[:20]
 out=HERE/'main_materialized'/key
 need(not out.exists(),'exact materialization already exists; inspect existing output, do not rerun')
 out.parent.mkdir(exist_ok=True);tmp=Path(tempfile.mkdtemp(prefix='stage_',dir=out.parent))
 def local(p):
  p=Path(p)
  return tmp/p.relative_to(out)if p.is_relative_to(out)else p
 def digest(p):return sha(local(p))
 def rr(p):return dict(path=str(p),sha256=digest(p))
 try:
  shutil.copytree(HERE/'runtime',tmp/'runtime',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  shutil.copytree(HERE/'execution',tmp/'execution',ignore=shutil.ignore_patterns('__pycache__','*.pyc','CPU_*.lock','*.lock'))
  for n in ['resources_a_v5.py','FOUR_FOREIGN_EXACT_MAPPING_PINS.json']:shutil.copy2(HERE/n,tmp/n)
  for p in tmp.rglob('*'):
   if p.is_file():
    try:p.write_text(p.read_text().replace(str(HERE),str(out)))
    except UnicodeDecodeError:pass
  R=out/'runtime';Q=out/'execution/control'
  # Fix acyclic owned JSON path refs after relocation; all external refs stay exact.
  def fix(v):
   if isinstance(v,list):return [fix(x)for x in v]
   if not isinstance(v,dict):return v
   w={k:fix(x)for k,x in v.items()}
   if set(w)>={'path','sha256'}and isinstance(w['path'],str)and Path(w['path']).is_relative_to(out)and local(w['path']).is_file():
    w['sha256']=digest(w['path'])
    if 'bytes'in w:w['bytes']=local(w['path']).stat().st_size
   return w
  for turn in range(8):
   changed=False
   for p in sorted(tmp.rglob('*.json')):
    if '/cases/'in str(p)or p.name.startswith('HOST_QUALIFICATION'):continue
    d=read(p);z=fix(d)
    if z!=d:dump(p,z);changed=True
   if not changed:break
  # modecontract binds relocated family table, while preserving code/math.
  p=local(R/'mode_contract.py');s=p.read_text();s=s.replace(next(l for l in s.splitlines()if l.startswith('FAMILY_SCOPE_SHA=')),'FAMILY_SCOPE_SHA='+repr(digest(R/'FAMILY_SCOPE.json')));p.write_text(s)
  # Repair metadata pins to preserved local numeric dependencies.
  p=local(R/'mode_aware_terminal.py');s=p.read_text();t=ast.parse(s);n=next(n for n in t.body if isinstance(n,ast.Assign)and any(isinstance(a,ast.Name)and a.id=='PINS'for a in n.targets));pins=ast.literal_eval(n.value);pins={k:digest(R/k)for k in pins};lines=s.splitlines();lines[n.lineno-1]='PINS='+repr(pins);p.write_text('\n'.join(lines)+'\n')
  # Wrapper resource source locator is new, underlying code uses HERE and is unchanged.
  p=local(R/'resources_request2.py');s=p.read_text();s=s.replace(next(l for l in s.splitlines()if l.startswith('P=pathlib.Path;PATH=')),'P=pathlib.Path;PATH=P('+repr(str(out/'resources_a_v5.py'))+');SHA='+repr(digest(out/'resources_a_v5.py')));p.write_text(s)
  # Approved objects remain immutable Main-authored external bytes.
  p=local(R/'ep_perf_native_wv_modes_draft.py');s=p.read_text();t=ast.parse(s);repl={}
  for n in t.body:
   if isinstance(n,ast.Assign):
    names=[x.id for x in n.targets if isinstance(x,ast.Name)]
    if '_SCHEMA_REFS'in names:repl[n.lineno]=repr(dict(contract_ref=cr,closure_ref=rr(Q/'SOURCE_NATIVE22_CLOSURE.json'),extra_dependencies_ref=rr(Q/'SOURCE_HOST5_CLOSURE.json')))
    if '_SCHEMA_MODULE'in names:repl[n.lineno]=repr(rr(R/'runtime_monitor_schema_v5_exact283_candidate.py'))
    if 'NATIVE_ROUTE_GUARD_REF'in names:repl[n.lineno]=repr(rr(R/'native_route_guard_v3.py'))
    if 'MODE_CONTRACT_SHA'in names:repl[n.lineno]=repr(digest(R/'mode_contract.py'))
    if 'NEW_VALIDATOR_SHA'in names:repl[n.lineno]=repr(digest(R/'mode_aware_terminal.py'))
  lines=s.splitlines()
  for k,v in repl.items():lines[k-1]=lines[k-1].split('=',1)[0]+'='+v
  p.write_text('\n'.join(lines)+'\n')
  # Final HostQ is built before Specs: no cyclic hash pin.
  modules=[rr(out/p.relative_to(tmp))for p in sorted((tmp/'runtime').rglob('*'))if p.is_file()]
  host=read(local(Q/'HOST_QUALIFICATION_CANDIDATE.json'));host.update(approved_by='EP-MAIN',Main_engineering_contract_ref=cr,Main_CPU_review_ref=qr,modules=modules);dump(local(Q/'HOST_QUALIFICATION_CANDIDATE.json'),host)
  refs=[]
  for p in sorted((tmp/'execution/cases').glob('*/control/FROZEN_SPEC.json')):
   s=fix(read(p))
   overrides=dict(host_engine_ref=R/'ep_perf_native_wv_modes_draft.py',host_common_ref=R/'ep_perf_common_v2.py',mode_contract_ref=R/'mode_contract.py',validation_module_ref=R/'mode_aware_terminal.py',postprocess_module_ref=R/'ep_perf_postprocess.py',archive_module_ref=R/'ep_perf_archive.py',native_entry_ref=R/'native_request3',native_route_guard_ref=R/'native_route_guard_v3.py',resource_module_ref=R/'resources_request2.py',source_qualification_ref=Q/'SOURCE_CPU_EVIDENCE_REBIND.json',mode_cpu_qualification_ref=Q/'MODE_CPU_EVIDENCE_REBIND.json',eligibility_ref=Q/'INPUT_MODE_REBIND_CANDIDATE.json',host_qualification_ref=Q/'HOST_QUALIFICATION_CANDIDATE.json',Main_scientific_launch_authorization=Q/'USER_AUTHORIZATION.json')
   s.update({k:rr(v)for k,v in overrides.items()});s['runtime_contract_requirement_ref']=cr
   native=read(local(Q/'SOURCE_NATIVE22_CLOSURE.json'));extra=read(local(Q/'SOURCE_HOST5_CLOSURE.json'))
   pins=dict(native['pinned_files']);pins.update({d['path']:d['sha256']for d in extra['dependencies']});pins.update({d['path']:d['sha256']for d in modules})
   for r in [cr,qr,rr(out/'resources_a_v5.py'),rr(Q/'HOST_QUALIFICATION_CANDIDATE.json')]:pins[r['path']]=r['sha256']
   s['pinned_files']=pins;s['qualification_status']='MAIN_ENGINEERING_REVIEWED_PRIVATE_FRESH_SCOPE_REQUIRED';dump(p,s);refs.append(rr(out/p.relative_to(tmp)))
  for p in (tmp/'runtime').rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
  dump(tmp/'MATERIALIZATION_RECEIPT.json',dict(status='PRIVATE_GRAPH_MATERIALIZED_PENDING_READONLY_PREPARE',Source5=SOURCE5,contract_ref=cr,review_ref=qr,prospective_spec_refs=refs,scientific_permission=False,Native_writes=0,starts=0))
  os.rename(tmp,out)
 except Exception:
  # No deletion of evidence: failed temp candidate retained for diagnosis.
  raise
 # Only read-only prepare, which MUST stop at absent fresh scientific scope.
 rows=[]
 for r in refs:
  cohort=read(r['path'])['cohort'];cmd=[sys.executable,'-B',str(out/'runtime/native_request3'),'experiment','prepare',cohort,'--project','EP_L2']
  result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
  expected='MISSING_FRESH_EXACT_REQUEST3_SCIENTIFIC_AUTHORIZATION'in result.stderr
  rows.append(dict(cohort=cohort,returncode=result.returncode,expected_fresh_scope_HOLD=expected,stdout=result.stdout,stderr=result.stderr))
  need(result.returncode==2 and expected,'materialized prepare unexpected HOLD or pass; retain graph, Main diagnose')
 receipt=read(out/'MATERIALIZATION_RECEIPT.json');receipt.update(status='MAIN_PRIVATE_ENGINEERING_PASS_FRESH_SCIENCE_SCOPE_ONLY',actual_prepare_checks=rows)
 dump(out/'MATERIALIZATION_RECEIPT.json',receipt)
 print(json.dumps(dict(status=receipt['status'],output=str(out),receipt_ref=ref(out/'MATERIALIZATION_RECEIPT.json'),scientific_permission=False,starts=0)))
 return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as exc:print(json.dumps(dict(status='HOLD_PRIVATE_NO_SCIENCE',reason=str(exc),scientific_permission=False)),file=sys.stderr);raise SystemExit(2)
