import pathlib,importlib.util,ast,copy,hashlib,json,tempfile,subprocess,types,datetime
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');D=P(tempfile.mkdtemp(prefix='OBSERVER_CPU_',dir=R/'ops'));src=R/'ops/observer_exit_race_v1.py';sp=importlib.util.spec_from_file_location('qualified_observer_overlay',src);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);base=T/'tools/sweep_native_cap1m.py';original=base.read_text();code,counts=m.transformed(original);checks=[]
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
assert counts['children']==counts['child_info']==counts['faults']==1;checks.append('exact_three_process_observation_sites_transformed')
transformed=ast.parse(code).body[0];prior=next(n for n in ast.parse(original).body if isinstance(n,ast.FunctionDef) and n.name=='run_native')
class Reverse(ast.NodeTransformer):
 def visit_Try(self,node):
  if len(node.body)==1 and len(node.handlers)==1 and any(isinstance(n,ast.Name) and n.id=='_observer_race_note' for n in ast.walk(node.handlers[0])):return self.visit(node.body[0])
  return self.generic_visit(node)
 def visit_Call(self,node):
  if isinstance(node.func,ast.Name) and node.func.id=='_observer_race_children':return ast.parse('childfile.read_text().split() if childfile.exists() else []',mode='eval').body
  return self.generic_visit(node)
 def visit_ExceptHandler(self,node):
  if isinstance(node.type,ast.Tuple) and any(isinstance(n,ast.Name) and n.id=='ProcessLookupError' for n in node.type.elts):
   kept=[n for n in node.type.elts if not(isinstance(n,ast.Name) and n.id=='ProcessLookupError')];node.type=kept[0] if len(kept)==1 else ast.Tuple(elts=kept,ctx=ast.Load())
  return self.generic_visit(node)
assert ast.dump(Reverse().visit(copy.deepcopy(transformed)),include_attributes=False)==ast.dump(prior,include_attributes=False);checks.append('reverse_transform_proves_all_other_native_code_AST_exact_including_policy_capture_actual_wait_and_limits')
assert m.transformed(original)[0]==code;checks.append('deterministic_source_generation')
missing=D/'does_not_exist';assert m.children(missing)==[];checks.append('vanished_parent_children_file_is_empty_observation_not_a_stale_PID_snapshot')
genuine=P('/proc/self/task')/str(__import__('os').getpid())/'children';assert isinstance(m.children(genuine),list);checks.append('normal_children_observation_retained')
oldP=m.P
def denied(*a):return types.SimpleNamespace(read_text=lambda:(_ for _ in ()).throw(PermissionError('denied')))
m.P=denied
try:
 try:m.children('x')
 except PermissionError:pass
 else:raise AssertionError('permission denied was masked')
finally:m.P=oldP
checks.append('permission_and_other_errors_not_swallowed')
tries=[n for n in ast.walk(ast.parse(code)) if isinstance(n,ast.Try) and any(isinstance(x,ast.Name) and x.id=='_observer_race_note' for h in n.handlers for x in ast.walk(h))];assert len(tries)==2
header='''def observe_fixture(p,out,observations,child_info):
 for turn in range(2):
  PLACEHOLDER
 return p.wait()
'''
fn=ast.parse(header).body[0];fn.body[0].body=copy.deepcopy(tries)+[ast.Pass()];mod=ast.Module(body=[fn],type_ignores=[]);ast.fix_missing_locations(mod);namespace={'P':P,'_observer_race_note':m.note};exec(compile(mod,'CPU_FIXTURE_EXACT_TRANSFORMED_PROC_BLOCKS','exec'),namespace);observe=namespace['observe_fixture'];runs=[]
for mode in ['identity_missing','stat_missing','permission_not_masked']:
 with (D/(mode+'.stdout')).open('wb') as stdout:
  child=subprocess.Popen(['/usr/bin/python3','-B','-c','print("complete_cpu_fixture_output")'],stdout=stdout,stderr=subprocess.STDOUT);rc=child.wait(timeout=3);assert rc==0
 obs=[{'pid':child.pid,'start_ticks':0}]
 def read_identity(pid):
  if mode=='permission_not_masked':raise PermissionError('unexpected access error')
  if mode=='stat_missing':return {'pid':pid}
  return {'pid':pid,'start_ticks':int((P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19])}
 if mode=='permission_not_masked':
  try:observe(child,D,obs,read_identity)
  except PermissionError:pass
  else:raise AssertionError('non-race error masked')
 else:assert observe(child,D,obs,read_identity)==0
 assert (D/(mode+'.stdout')).read_bytes()==b'complete_cpu_fixture_output\n';runs.append({'case':mode,'actual_wait_returncode':rc,'complete_output_preserved':True})
checks.append('real_child_exit_between_poll_and_identity_or_stat_read_closes_with_actual_wait_and_complete_pipe')
checks.append('unexpected_identity_access_error_still_fails_closed')
# Demonstrate the unguarded old observation actually raises on the same exited PID.
try:(P('/proc')/str(child.pid)/'stat').read_text()
except FileNotFoundError:pass
else:raise AssertionError('fixture PID unexpectedly persisted')
checks.append('original_missing_proc_exception_reproduced_without_using_any_simulator')
events=[json.loads(l) for l in (D/'OBSERVER_PROC_EXIT_RACE_EVENTS.jsonl').read_text().splitlines()];assert len(events)==4 and all(e['actual_launcher_poll_returncode']==0 and e['action'].startswith('No stale identity') for e in events);checks.append('recovery_events_preserve_actual_poll_result_and_explicit_last_observed_identity')
native=types.ModuleType('CPU_install_fixture_native');native.__file__=str(base);native.exclusive=lambda p,o:o;native.__dict__.update({'P':P});m.install(native);assert native._OBSERVER_PROC_RACE_BINDING['base_native_source_sha256']==sha(base);assert native.exclusive(D/'X.INTENT.json',{'x':1})['observer_exit_race_binding']['adapter_sha256']==sha(src);checks.append('new_attempt_INTENT_launch_PID_adapter_binding_is_explicit')
try:m.install(native)
except AssertionError:pass
else:raise AssertionError('duplicate install accepted')
checks.append('duplicate_install_rejected')
report={'status':'PASS','schema':'OBSERVER_EXIT_RACE_CPU_QUALIFICATION_V1','adapter_sha256':sha(src),'base_native_sha256':sha(base),'generated_source_sha256':hashlib.sha256(code.encode()).hexdigest(),'driver_sha256':sha(__file__),'checks':checks,'check_count':len(checks),'real_CPU_fixture_cases':runs,'fixture_directory':str(D),'scientific_simulator_starts':0,'scientific_processes_attached':0,'historical_receipts_fabricated':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};out=R/'ops/OBSERVER_EXIT_RACE_CPU_QUALIFICATION_V1.json';out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'fixture':str(D),'adapter_sha256':sha(src)}))
