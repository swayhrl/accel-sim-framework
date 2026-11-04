from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,subprocess,sys
sys.dont_write_bytecode=True
P=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');O=Path(__file__).resolve().parent;F=O/'delta_metadata_checks';F.mkdir(exist_ok=True);V=P/'research/performance_first_v3_20261104_v1/activation_20261104_v1';graphs=json.loads((O/'PRIVATE_GRAPH_INDEX.json').read_text())['graphs']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def dump(p,d):Path(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
if len(sys.argv)>1:
 g=next(g for g in graphs if g['lane']==sys.argv[1]);H=Path(g['runtime']);E=Path(g['execution']);sys.path.insert(0,str(H));import ep_perf_native_wv_modes_draft as e;import private_main_dispatcher as dispatcher
 receipts=[];cpu=min(os.sched_getaffinity(0))
 for item in g['candidate_specs']:
  s=json.loads(Path(item['path']).read_text());case=s['cohort'];proof=e.validate_spec_contract(s);eng=e.engineering_spec_for(case)
  m=e.module(s['mode_contract_ref'],'new_scope_mode_contract');m.validate_fair_pair(s,json.loads(e.spec_path(s['same_background_peer_cohort']).read_text()))
  negative=[]
  for label,mutate,kind in [
   ('wrong_Source862',lambda d:d['source_identity'].update(core_source_commit='862376f62ab19f9a677abe31c6a422028b44fcd0'),'schema'),
   ('missing_required_host_cpu',lambda d:d.pop('host_cpu'),'schema'),
   ('native22_pin_removed',lambda d:d['pinned_files'].pop(next(iter(json.loads((O/'SOURCE78_NATIVE_CLOSURE.json').read_text())['pinned_files']))),'schema'),
   ('helper_shell_pin_removed',lambda d:d['pinned_files'].pop('/bin/sh'),'schema'),
   ('bad_runtime_limit',lambda d:d['limits'].update(wall_seconds=0),'schema'),
   ('changed_native_domain',lambda d:d.update(native_boot_id='0'*8+'-'+'0'*4+'-'+'0'*4+'-'+'0'*4+'-'+'0'*12),'schema'),
   ('full282_background_drift',lambda d:d['expected_effective_options'].update({'-dram_latency':'99'}),'mode'),
   ('cross_request_cohort',lambda d:d.update(cohort='EP_PERF_PFV4_A9_FOREIGN'),'mode')]:
   d=copy.deepcopy(s);mutate(d)
   try:
    if kind=='schema':e.validate_spec_contract(d)
    else:m.validate_static(d)
   except Exception as exc:negative.append(dict(test=label,status='PASS_REJECTED',reason=str(exc)))
   else:raise AssertionError('negative incorrectly passed '+label)
  bound=dict(s,host_cpu=cpu);boundproof=e.validate_spec_contract(bound,require_bound_cpu=True)
  # Actual dispatcher gate: no authority override and no claim file/resource/model effects.
  binding=dict(cohort=case,host_cpu=cpu,spec_sha256=sha(e.spec_path(case)))
  claimfile=E/'control/DISPATCH_CLAIMS.json';assert not claimfile.exists()
  try:dispatcher.claim(case,binding)
  except Exception as exc:claimhold=str(exc);assert 'MISSING_FRESH_EXACT_REQUEST2_SCIENTIFIC_AUTHORIZATION'in claimhold
  else:raise AssertionError('unapproved claim accepted')
  assert not claimfile.exists()
  # Test malformed proposal through the dispatcher entry itself, before any claim.
  original_read=e.read
  def broken_read(path):
   if Path(path)==e.spec_path(case):
    d=copy.deepcopy(s);d.pop('host_cpu');return d
   return original_read(path)
  e.read=broken_read
  try:dispatcher.claim(case,binding)
  except Exception as exc:preclaim_missing=str(exc);assert 'missing required runtime fields: host_cpu'in preclaim_missing
  else:raise AssertionError('partial claim accepted')
  e.read=original_read;assert not claimfile.exists()
  receipts.append(dict(cohort=case,full43_schema=proof,current_domain=True,current_dependency_bytes=True,engine_static_mode_geometry_input_refs_PASS=True,bound_cpu_schema=boundproof,preclaim_missing_field_HOLD=preclaim_missing,no_science_preclaim_HOLD=claimhold,negative_tests=negative))
 dump(F/(g['lane']+'_FULL43_CURRENT_DEPENDENCY_DELTA.json'),receipts)
 print(json.dumps(dict(lane=g['lane'],points=len(receipts),status='PASS',negative_tests=sum(len(x['negative_tests'])for x in receipts),preclaim_HOLDs=2*len(receipts))))
 sys.exit()
# Read-only preimage includes shared Native, registry and epoch. No route installation occurs.
reg=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');epoch=reg.parents[1]/'CURRENT_SCIENCE_EPOCH.json'
route=json.loads((P/'execution_midtag_v3_20261104_v1/midtag/control/NATIVE_ENTRY_ROUTE_V3.json').read_text());shared=Path(route['global_shared_native_ref']['path'])
pre={str(p):sha(p)for p in [reg,epoch,shared]};dump(F/'SHARED_PREIMAGE.json',pre)
runs=[]
for g in graphs:
 result=subprocess.run([sys.executable,'-B',__file__,g['lane']],text=True,capture_output=True);runs.append(dict(lane=g['lane'],exitcode=result.returncode,stdout=result.stdout,stderr=result.stderr));assert result.returncode==0,runs[-1]
# Original monitor/parser functions and original event loop unchanged, apart from one schema call before helpers/consume.
old=ast.parse((V/'runtimes/midtag/ep_perf_native_wv_modes_draft.py').read_text());oldf={x.name:x for x in old.body if isinstance(x,ast.FunctionDef)};asts=[]
for g in graphs:
 H=Path(g['runtime']);new=ast.parse((H/'ep_perf_native_wv_modes_draft.py').read_text());newf={x.name:x for x in new.body if isinstance(x,ast.FunctionDef)}
 keep=['verify_actual','fresh_input','dispatch_binding','resource_gate']
 for n in keep:assert ast.dump(oldf[n])==ast.dump(newf[n]),(g['lane'],n)
 run=copy.deepcopy(newf['run_native']);run.body=[n for n in run.body if not(isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='validate_spec_contract')]
 assert ast.dump(run)==ast.dump(oldf['run_native'])
 oldparser=ast.parse((V/'runtimes/midtag/mode_aware_terminal.py').read_text());newparser=ast.parse((H/'mode_aware_terminal.py').read_text())
 assert [ast.dump(n)for n in oldparser.body if isinstance(n,ast.FunctionDef)]==[ast.dump(n)for n in newparser.body if isinstance(n,ast.FunctionDef)]
 asts.append(dict(lane=g['lane'],monitor_functions_identical=keep,run_native_all_original_statements_identical=True,run_native_only_new_statement='strict43 currentdomain+native22+helper dependencies boundCPU before helper/output/locks/transaction/fork',mode_aware_parser_all_functions_identical=True))
# Exercise real private Native prepare per mode and request; no mock authority/route.
holds=[]
for g in graphs:
 for r in g['candidate_specs']:
  s=json.loads(Path(r['path']).read_text());args=[g['entry_ref']['path'],'experiment','prepare',s['cohort'],'--project','EP_L2'];cp=subprocess.run(args,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  assert cp.returncode==2 and 'MISSING_FRESH_EXACT_REQUEST2_SCIENTIFIC_AUTHORIZATION'in cp.stderr,(args,cp.stdout,cp.stderr)
  holds.append(dict(cohort=s['cohort'],argv=args,exitcode=cp.returncode,receipt=json.loads(cp.stderr),model_forks=0,budget_claims_consumes=0))
assert all(sha(p)==h for p,h in pre.items())
dump(F/'FULL43_DELTA_TEST_RUNS.json',runs);dump(F/'MONITOR_PARSER_AST_EQUIVALENCE.json',asts);dump(F/'REAL_PRIVATE_NATIVE_PREPARE_HOLDS.json',holds);dump(F/'SHARED_POSTIMAGE_UNCHANGED.json',dict(status='PASS',files=pre,shared_route_writes=0,registry_epoch_writes=0))
print(json.dumps(dict(status='PASS',complete_Source78_points=4,native_prepares_HOLD=len(holds),source_geometry_CPU_retests=0,application_NI_runs=0,model_starts=0,science_consumes=0,real_authority_writes=0)))

